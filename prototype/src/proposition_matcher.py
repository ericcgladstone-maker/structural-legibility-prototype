"""Match world propositions against rendered messages.

Returns a per-proposition classification:
    preserved        : present in the message with content matching the claim
    altered          : present but with substantively different content
    omitted          : absent from the message
    contradicted     : message asserts the negation or an incompatible claim

Also detects:
    unsupported_additions : claims in the message not derivable from any world proposition

Approach:
    - Split message into sentences.
    - For each proposition, compute embedding similarity to each sentence.
    - For sentences with high similarity, also check token-level overlap.
    - Classify based on similarity thresholds and the proposition's truth_value
      plus an auxiliary contradiction probe using its conflict partner if any.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .model_client import EmbeddingClient


# Tunable thresholds; lock for the prototype.
SIM_PRESERVED_MIN = 0.65
SIM_CONTRADICTED_MIN = 0.55  # high similarity to the *conflict partner* claim
SIM_ALTERED_RANGE = (0.45, 0.65)
ADDITION_NOVELTY_MIN = 0.45  # max similarity to any world prop below which a sentence is "unsupported"


SENTENCE_SPLIT_RE = re.compile(r"(?<=[\.!?])\s+(?=[A-Z])")


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    # Conservative: split on sentence-ending punctuation followed by a capital.
    parts = SENTENCE_SPLIT_RE.split(text)
    # Drop trivially short fragments.
    return [p.strip() for p in parts if len(p.strip()) >= 4]


@dataclass
class PropositionMatch:
    proposition_id: str
    best_similarity: float
    matched_sentence_index: int | None
    classification: str           # preserved | altered | omitted | contradicted
    notes: str = ""


@dataclass
class MatchResult:
    matches: dict[str, PropositionMatch]
    unsupported_addition_count: int
    unsupported_addition_sentences: list[str] = field(default_factory=list)
    extractor_version: str = "proposition_matcher_v0_1"


class PropositionMatcher:
    def __init__(self, embedder: EmbeddingClient):
        self.embedder = embedder

    def match(
        self,
        message: str,
        world: dict[str, Any],
        in_scope_proposition_ids: list[str] | None = None,
    ) -> MatchResult:
        """Match the world's propositions against the message.

        `in_scope_proposition_ids` indicates the propositions the source intended
        to convey. Out-of-scope propositions are still measurable but only as
        confirmation that no unsupported drift introduced them.
        """
        sentences = split_sentences(message)
        if not sentences:
            return MatchResult(matches={}, unsupported_addition_count=0)

        prop_claims = [p["natural_language_claim"] for p in world["propositions"]]
        prop_ids = [p["proposition_id"] for p in world["propositions"]]
        truth_lookup = {p["proposition_id"]: p["truth_value"] for p in world["propositions"]}

        conflict_partner = {}
        for pair in world["conflict_propositions"]:
            a, b = pair
            conflict_partner.setdefault(a, []).append(b)
            conflict_partner.setdefault(b, []).append(a)

        # Embed everything once.
        prop_embs = self.embedder.embed(prop_claims)
        sent_embs = self.embedder.embed(sentences)

        # sim[i, j] = similarity between proposition i and sentence j.
        import numpy as np
        sim = prop_embs @ sent_embs.T  # both normalized

        in_scope = set(in_scope_proposition_ids or prop_ids)
        matches: dict[str, PropositionMatch] = {}

        for i, pid in enumerate(prop_ids):
            row = sim[i]
            j_best = int(np.argmax(row))
            best_sim = float(row[j_best])

            classification = "omitted"
            notes = ""

            if best_sim >= SIM_PRESERVED_MIN:
                classification = "preserved"
            elif SIM_ALTERED_RANGE[0] <= best_sim < SIM_ALTERED_RANGE[1]:
                classification = "altered"

            # Contradiction: if a conflicting partner is *more* similar than this prop,
            # and the partner has opposite truth_value, classify as contradicted.
            for partner_id in conflict_partner.get(pid, []):
                partner_idx = prop_ids.index(partner_id)
                partner_sim = float(sim[partner_idx].max())
                if (
                    partner_sim >= SIM_CONTRADICTED_MIN
                    and partner_sim > best_sim
                    and truth_lookup.get(partner_id) != truth_lookup.get(pid)
                ):
                    classification = "contradicted"
                    notes = f"conflicting partner {partner_id} matched more strongly (sim={partner_sim:.2f})"
                    break

            # If the proposition was in_scope and absent, mark as omission explicitly.
            if pid in in_scope and classification == "omitted":
                notes = notes or "in-scope proposition not found"

            matches[pid] = PropositionMatch(
                proposition_id=pid,
                best_similarity=round(best_sim, 4),
                matched_sentence_index=j_best if best_sim >= SIM_ALTERED_RANGE[0] else None,
                classification=classification,
                notes=notes,
            )

        # Unsupported additions: sentences whose maximum similarity to any world
        # proposition is below ADDITION_NOVELTY_MIN.
        per_sentence_max = sim.max(axis=0)  # for each sentence, max over props
        unsupported_idx = [int(j) for j, s in enumerate(per_sentence_max) if float(s) < ADDITION_NOVELTY_MIN]
        unsupported_sents = [sentences[j] for j in unsupported_idx]

        return MatchResult(
            matches=matches,
            unsupported_addition_count=len(unsupported_idx),
            unsupported_addition_sentences=unsupported_sents,
        )


def preservation_rate(result: MatchResult, in_scope_proposition_ids: list[str]) -> float | None:
    if not in_scope_proposition_ids:
        return None
    preserved = sum(
        1 for pid in in_scope_proposition_ids
        if result.matches.get(pid) and result.matches[pid].classification in ("preserved", "altered")
    )
    return round(preserved / len(in_scope_proposition_ids), 4)


def omission_count(result: MatchResult, in_scope_proposition_ids: list[str]) -> int:
    return sum(
        1 for pid in in_scope_proposition_ids
        if result.matches.get(pid) and result.matches[pid].classification == "omitted"
    )


def alteration_count(result: MatchResult, in_scope_proposition_ids: list[str]) -> int:
    return sum(
        1 for pid in in_scope_proposition_ids
        if result.matches.get(pid) and result.matches[pid].classification == "altered"
    )


def contradiction_count(result: MatchResult) -> int:
    return sum(1 for m in result.matches.values() if m.classification == "contradicted")
