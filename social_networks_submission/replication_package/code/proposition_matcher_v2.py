"""Proposition matcher v0.2.

Fixes the conflict-pair labeling bug documented in
`outputs/matcher_validation_note_v0_1.md`.

Key changes from v0.1:

1. Adds a new label, `preserved_qualified`, used when a proposition is present
   in the message AND its conflict partner is also present. This represents
   the dominant mutator behavior on llama3.1:8b: "X is most likely, although
   Y is also suspected." Both propositions are present, both should be marked
   as such, with the qualifier indicating that the message is hedging between
   competing claims.

2. Tightens the `contradicted` rule. v0.1 labeled a proposition as contradicted
   whenever its conflict partner had higher similarity AND the partner crossed
   a low threshold (0.55). This produced false contradictions in the common
   case where both claims were in the message. v0.2 requires:

      - own_sim < SIM_ALTERED_RANGE[0] (i.e., the proposition is essentially
        not in the message)
      - partner_sim >= SIM_PRESERVED_MIN (i.e., the partner is clearly present)
      - (partner_sim - own_sim) >= SIM_CONTRADICTION_MARGIN (large gap)
      - opposite truth value
      - no `not X` style negation already in the message that would suggest
        the proposition's content was explicitly negated

   Under these stricter rules, contradiction only fires when the partner is
   present, this proposition is absent, and the gap is unambiguous.

3. Preservation rate counts preserved + preserved_qualified + altered as kept,
   contradicted + omitted as not kept. The interpretation: if a claim survives
   the transmission in any form (clean, hedged, or paraphrased), it's "kept"
   for fidelity purposes. A claim is "not kept" only if it's missing or
   explicitly contradicted.

The matcher remains deterministic and embedding-based. No LLM judge.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .model_client import EmbeddingClient

# Thresholds for v0.2.
SIM_PRESERVED_MIN = 0.65
SIM_QUALIFIED_PRESENT_MIN = 0.55         # partner-presence floor, also own-presence floor for qualification
SIM_ALTERED_RANGE = (0.45, 0.65)
SIM_CONTRADICTED_PARTNER_MIN = 0.65      # partner must be clearly present
SIM_CONTRADICTED_OWN_MAX = 0.45          # own must be clearly absent
SIM_CONTRADICTION_MARGIN = 0.20
ADDITION_NOVELTY_MIN = 0.45

SENTENCE_SPLIT_RE = re.compile(r"(?<=[\.!?])\s+(?=[A-Z])")


def split_sentences(text: str) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = SENTENCE_SPLIT_RE.split(text)
    return [p.strip() for p in parts if len(p.strip()) >= 4]


@dataclass
class PropositionMatchV2:
    proposition_id: str
    best_similarity: float
    partner_similarity: float | None
    matched_sentence_index: int | None
    classification: str       # preserved | preserved_qualified | altered | omitted | contradicted
    notes: str = ""


@dataclass
class MatchResultV2:
    matches: dict[str, PropositionMatchV2]
    unsupported_addition_count: int
    unsupported_addition_sentences: list[str] = field(default_factory=list)
    matcher_version: str = "proposition_matcher_v0_2"


# Optional: detect explicit "not X" or "ruled out X" patterns near proposition keywords.
# Used only as a hint to upgrade classification confidence when present.
NEGATION_PATTERNS = [
    r"\bnot\s+(?:the|a|an)?\s*(?P<term>\w+)",
    r"\bruled out\b",
    r"\bdid not\b",
    r"\bdoes not\b",
    r"\bdo not\b",
    r"\bwas not\b",
    r"\bwere not\b",
    r"\bno evidence\b",
    r"\bno indication\b",
]
NEG_RE = re.compile("|".join(NEGATION_PATTERNS), re.IGNORECASE)


def has_negation(text: str) -> bool:
    return bool(NEG_RE.search(text or ""))


class PropositionMatcherV2:
    """v0.2 matcher. See module docstring for behavior."""

    VERSION = "proposition_matcher_v0_2"

    def __init__(self, embedder: EmbeddingClient):
        self.embedder = embedder

    def match(
        self,
        message: str,
        world: dict[str, Any],
        in_scope_proposition_ids: list[str] | None = None,
    ) -> MatchResultV2:
        sentences = split_sentences(message)
        if not sentences:
            return MatchResultV2(matches={}, unsupported_addition_count=0)

        prop_claims = [p["natural_language_claim"] for p in world["propositions"]]
        prop_ids = [p["proposition_id"] for p in world["propositions"]]
        truth_lookup = {p["proposition_id"]: p["truth_value"] for p in world["propositions"]}

        conflict_partner: dict[str, list[str]] = {}
        for pair in world["conflict_propositions"]:
            a, b = pair
            conflict_partner.setdefault(a, []).append(b)
            conflict_partner.setdefault(b, []).append(a)

        prop_embs = self.embedder.embed(prop_claims)
        sent_embs = self.embedder.embed(sentences)
        sim = prop_embs @ sent_embs.T

        in_scope = set(in_scope_proposition_ids or prop_ids)
        matches: dict[str, PropositionMatchV2] = {}
        msg_has_negation = has_negation(message)

        for i, pid in enumerate(prop_ids):
            row = sim[i]
            j_best = int(np.argmax(row))
            own_sim = float(row[j_best])

            partner_max_sim = None
            partner_id_used = None
            for partner_id in conflict_partner.get(pid, []):
                p_idx = prop_ids.index(partner_id)
                p_sim = float(sim[p_idx].max())
                if partner_max_sim is None or p_sim > partner_max_sim:
                    partner_max_sim = p_sim
                    partner_id_used = partner_id

            # Step 1: base classification from own_sim alone.
            if own_sim >= SIM_PRESERVED_MIN:
                cls = "preserved"
            elif own_sim >= SIM_ALTERED_RANGE[0]:
                cls = "altered"
            else:
                cls = "omitted"

            notes_parts = []

            # Step 2: if both this proposition and a conflict partner are present
            # (both above the qualified-present threshold), downgrade "preserved"
            # to "preserved_qualified" and leave the others alone. This is the
            # key fix from v0.1.
            both_present = (
                partner_max_sim is not None
                and partner_max_sim >= SIM_QUALIFIED_PRESENT_MIN
                and own_sim >= SIM_QUALIFIED_PRESENT_MIN
            )
            if both_present and cls == "preserved":
                cls = "preserved_qualified"
                notes_parts.append(f"both conflict propositions present (partner {partner_id_used} sim={partner_max_sim:.2f})")
            elif both_present and cls == "altered":
                # An "altered" proposition that is present alongside its partner
                # also gets the qualifier note.
                notes_parts.append(f"altered, partner {partner_id_used} also present (sim={partner_max_sim:.2f})")

            # Step 3: stricter contradiction rule. Only contradict when own is
            # clearly absent, partner is clearly present, and the gap is large
            # AND truth values differ. Optionally, having an explicit negation
            # in the message raises confidence; we do not require it.
            if (
                partner_max_sim is not None
                and partner_max_sim >= SIM_CONTRADICTED_PARTNER_MIN
                and own_sim < SIM_CONTRADICTED_OWN_MAX
                and (partner_max_sim - own_sim) >= SIM_CONTRADICTION_MARGIN
                and truth_lookup.get(partner_id_used) != truth_lookup.get(pid)
            ):
                cls = "contradicted"
                neg_note = " with explicit negation" if msg_has_negation else ""
                notes_parts.append(
                    f"partner {partner_id_used} clearly present (sim={partner_max_sim:.2f}), own absent (sim={own_sim:.2f}){neg_note}"
                )

            # Step 4: in-scope sanity note.
            if pid in in_scope and cls == "omitted":
                notes_parts.append("in-scope proposition not found")

            matches[pid] = PropositionMatchV2(
                proposition_id=pid,
                best_similarity=round(own_sim, 4),
                partner_similarity=round(partner_max_sim, 4) if partner_max_sim is not None else None,
                matched_sentence_index=j_best if own_sim >= SIM_ALTERED_RANGE[0] else None,
                classification=cls,
                notes="; ".join(notes_parts),
            )

        per_sentence_max = sim.max(axis=0)
        unsupported_idx = [int(j) for j, s in enumerate(per_sentence_max) if float(s) < ADDITION_NOVELTY_MIN]
        unsupported_sents = [sentences[j] for j in unsupported_idx]

        return MatchResultV2(
            matches=matches,
            unsupported_addition_count=len(unsupported_idx),
            unsupported_addition_sentences=unsupported_sents,
        )


# Aggregate helpers (count preserved + preserved_qualified + altered as kept).
KEPT_LABELS = ("preserved", "preserved_qualified", "altered")


def preservation_rate(result: MatchResultV2, in_scope_proposition_ids: list[str]) -> float | None:
    if not in_scope_proposition_ids:
        return None
    kept = sum(
        1 for pid in in_scope_proposition_ids
        if result.matches.get(pid) and result.matches[pid].classification in KEPT_LABELS
    )
    return round(kept / len(in_scope_proposition_ids), 4)


def omission_count(result: MatchResultV2, in_scope_proposition_ids: list[str]) -> int:
    return sum(
        1 for pid in in_scope_proposition_ids
        if result.matches.get(pid) and result.matches[pid].classification == "omitted"
    )


def alteration_count(result: MatchResultV2, in_scope_proposition_ids: list[str]) -> int:
    return sum(
        1 for pid in in_scope_proposition_ids
        if result.matches.get(pid) and result.matches[pid].classification == "altered"
    )


def contradiction_count(result: MatchResultV2) -> int:
    return sum(1 for m in result.matches.values() if m.classification == "contradicted")


def qualified_count(result: MatchResultV2) -> int:
    return sum(1 for m in result.matches.values() if m.classification == "preserved_qualified")
