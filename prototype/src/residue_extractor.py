"""Residue extractor v0.1.

Computes per-message features used to diagnose chain-relay and centralized-synthesis
residues. All features must be deterministic given the message text, world state,
and loaded dictionaries. The extractor never calls an LLM; all features are
rule-based, dictionary-based, or embedding-based.

Versioning:
    Bump extractor_version when the feature set or method changes.
    The harness re-extracts on all prior raw traces on version bumps rather than
    overwriting old features.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import numpy as np

from .model_client import EmbeddingClient
from .proposition_matcher import (
    MatchResult,
    PropositionMatcher,
    alteration_count,
    contradiction_count,
    omission_count,
    preservation_rate,
    split_sentences,
)


EXTRACTOR_VERSION = "residue_extractor_v0_1"


# ----------------------------------------------------------------------
# Dictionary loading and word-bounded matching
# ----------------------------------------------------------------------

class Dictionary:
    def __init__(self, path: str):
        with open(path) as f:
            data = json.load(f)
        self.dictionary_id = data["dictionary_id"]
        self.entries = sorted(data["entries"], key=len, reverse=True)  # longer first
        # Build a single regex with word boundaries. Multi-word entries are matched
        # as phrases (whitespace flexible). Single-word entries with word bounds.
        escaped = [re.escape(e) for e in self.entries]
        # Allow whitespace between words to be one or more whitespace chars.
        escaped = [e.replace(r"\ ", r"\s+") for e in escaped]
        pattern = r"\b(?:" + "|".join(escaped) + r")\b"
        self._re = re.compile(pattern, flags=re.IGNORECASE)

    def count(self, text: str) -> int:
        return len(self._re.findall(text or ""))


# ----------------------------------------------------------------------
# Surface features
# ----------------------------------------------------------------------

NUMERIC_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
NAMED_ENTITY_RE = re.compile(r"\b[A-Z][A-Za-z0-9-]+(?:\s+[A-Z0-9][A-Za-z0-9-]+)*\b")
TIME_RE = re.compile(r"\b[0-2]?\d:[0-5]\d\b")
LOCATION_RE = re.compile(r"\b(?:site|bay|line|plant|building|warehouse|gate|tower|room|yard|reactor|unit|corridor|basement|dock)[_\s]?[A-Z0-9]+\b", flags=re.IGNORECASE)
TOKEN_RE = re.compile(r"\b[\w'-]+\b")
SENTENCE_END_RE = re.compile(r"[.!?]+(?:\s|$)")


def token_count(text: str) -> int:
    return len(TOKEN_RE.findall(text or ""))


def sentence_count(text: str) -> int:
    if not text:
        return 0
    parts = split_sentences(text)
    return len(parts)


def type_token_ratio(text: str) -> float | None:
    tokens = [t.lower() for t in TOKEN_RE.findall(text or "")]
    if not tokens:
        return None
    return round(len(set(tokens)) / len(tokens), 4)


def mean_sentence_length(text: str) -> float | None:
    sents = split_sentences(text)
    if not sents:
        return None
    lens = [len(TOKEN_RE.findall(s)) for s in sents]
    return round(sum(lens) / len(lens), 2)


def mean_word_length(text: str) -> float | None:
    tokens = TOKEN_RE.findall(text or "")
    if not tokens:
        return None
    return round(sum(len(t) for t in tokens) / len(tokens), 3)


def punctuation_density(text: str) -> float | None:
    if not text:
        return None
    punct = sum(1 for c in text if c in ".,;:!?-()\"'")
    return round(punct / max(len(text), 1), 4)


# ----------------------------------------------------------------------
# Feature container
# ----------------------------------------------------------------------

@dataclass
class FeatureRow:
    feature_name: str
    feature_value: Any
    extractor_name: str
    extractor_version: str
    extracted_at: str
    message_id: str
    run_id: str
    null_reason: str | None = None


def _row(name: str, value: Any, message_id: str, run_id: str, null_reason: str | None = None) -> FeatureRow:
    return FeatureRow(
        feature_name=name,
        feature_value=value,
        extractor_name="residue_extractor",
        extractor_version=EXTRACTOR_VERSION,
        extracted_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        message_id=message_id,
        run_id=run_id,
        null_reason=null_reason,
    )


# ----------------------------------------------------------------------
# Main extractor
# ----------------------------------------------------------------------

class ResidueExtractor:
    def __init__(
        self,
        embedder: EmbeddingClient,
        hedges: Dictionary,
        uncertainty: Dictionary,
        evidentials: Dictionary,
        source_markers: Dictionary,
    ):
        self.embedder = embedder
        self.hedges = hedges
        self.uncertainty = uncertainty
        self.evidentials = evidentials
        self.source_markers = source_markers
        self.matcher = PropositionMatcher(embedder)

    def extract(
        self,
        *,
        run_id: str,
        message_id: str,
        message_text: str,
        world: dict[str, Any],
        parent_text: str | None,
        original_text: str | None,
        in_scope_proposition_ids: list[str] | None,
    ) -> tuple[list[FeatureRow], dict[str, Any]]:
        """Return a list of FeatureRows plus a small aux-info dict (e.g. match details).

        The aux dict carries per-proposition match classifications that the
        audit export uses but the analysis tables flatten.
        """
        rows: list[FeatureRow] = []
        aux: dict[str, Any] = {}

        if message_text is None or message_text.strip() == "":
            rows.append(_row("token_count", 0, message_id, run_id, "empty_message"))
            return rows, aux

        # Surface features
        rows.append(_row("token_count", token_count(message_text), message_id, run_id))
        rows.append(_row("sentence_count", sentence_count(message_text), message_id, run_id))
        rows.append(_row("type_token_ratio", type_token_ratio(message_text), message_id, run_id))
        rows.append(_row("mean_sentence_length", mean_sentence_length(message_text), message_id, run_id))
        rows.append(_row("mean_word_length", mean_word_length(message_text), message_id, run_id))
        rows.append(_row("punctuation_density", punctuation_density(message_text), message_id, run_id))

        rows.append(_row("numeric_token_count", len(NUMERIC_RE.findall(message_text)), message_id, run_id))
        rows.append(_row("named_entity_count", len(NAMED_ENTITY_RE.findall(message_text)), message_id, run_id))
        rows.append(_row("temporal_marker_count", len(TIME_RE.findall(message_text)), message_id, run_id))
        rows.append(_row("location_marker_count", len(LOCATION_RE.findall(message_text)), message_id, run_id))

        # Dictionary features
        rows.append(_row("hedge_count", self.hedges.count(message_text), message_id, run_id))
        rows.append(_row("uncertainty_marker_count", self.uncertainty.count(message_text), message_id, run_id))
        rows.append(_row("evidential_marker_count", self.evidentials.count(message_text), message_id, run_id))
        rows.append(_row("source_marker_count", self.source_markers.count(message_text), message_id, run_id))

        # Compression
        if parent_text:
            parent_tok = max(token_count(parent_text), 1)
            rows.append(_row("compression_ratio_from_parent", round(token_count(message_text) / parent_tok, 4), message_id, run_id))
        else:
            rows.append(_row("compression_ratio_from_parent", None, message_id, run_id, "no_parent_text"))

        if original_text:
            orig_tok = max(token_count(original_text), 1)
            rows.append(_row("compression_ratio_from_original", round(token_count(message_text) / orig_tok, 4), message_id, run_id))
        else:
            rows.append(_row("compression_ratio_from_original", None, message_id, run_id, "no_original_text"))

        # Embedding-based drift
        try:
            msg_emb = self.embedder.embed([message_text])[0]
            if parent_text:
                par_emb = self.embedder.embed([parent_text])[0]
                drift_p = 1.0 - float(np.dot(msg_emb, par_emb))
                rows.append(_row("semantic_drift_from_parent", round(drift_p, 4), message_id, run_id))
            else:
                rows.append(_row("semantic_drift_from_parent", None, message_id, run_id, "no_parent_text"))
            if original_text:
                orig_emb = self.embedder.embed([original_text])[0]
                drift_o = 1.0 - float(np.dot(msg_emb, orig_emb))
                rows.append(_row("semantic_drift_from_original", round(drift_o, 4), message_id, run_id))
            else:
                rows.append(_row("semantic_drift_from_original", None, message_id, run_id, "no_original_text"))
        except Exception as e:
            rows.append(_row("semantic_drift_from_parent", None, message_id, run_id, f"embed_error:{type(e).__name__}"))
            rows.append(_row("semantic_drift_from_original", None, message_id, run_id, f"embed_error:{type(e).__name__}"))

        # Proposition-based features
        if world is not None:
            match_result = self.matcher.match(message_text, world, in_scope_proposition_ids)
            in_scope = in_scope_proposition_ids or [p["proposition_id"] for p in world["propositions"]]

            rows.append(_row("proposition_preservation_rate", preservation_rate(match_result, in_scope), message_id, run_id))
            rows.append(_row("proposition_omission_count", omission_count(match_result, in_scope), message_id, run_id))
            rows.append(_row("proposition_alteration_count", alteration_count(match_result, in_scope), message_id, run_id))
            rows.append(_row("proposition_contradiction_count", contradiction_count(match_result), message_id, run_id))
            rows.append(_row("unsupported_addition_count", match_result.unsupported_addition_count, message_id, run_id))

            # Uncertainty preservation rate: of propositions in scope whose
            # uncertainty < 0.8, how many remained classified preserved?
            uncertain_props = [p for p in world["propositions"] if p["proposition_id"] in in_scope and p["uncertainty"] < 0.8]
            if uncertain_props:
                kept = sum(
                    1 for p in uncertain_props
                    if match_result.matches.get(p["proposition_id"]) and match_result.matches[p["proposition_id"]].classification in ("preserved", "altered")
                )
                rows.append(_row("uncertainty_proposition_preservation_rate", round(kept / len(uncertain_props), 4), message_id, run_id))
            else:
                rows.append(_row("uncertainty_proposition_preservation_rate", None, message_id, run_id, "no_uncertain_propositions_in_scope"))

            # Evidence-marker proposition preservation: propositions whose evidence_type
            # is in {report, log_record} and were in scope.
            evid_props = [p for p in world["propositions"] if p["proposition_id"] in in_scope and p["evidence_type"] in ("report", "log_record")]
            if evid_props:
                kept = sum(
                    1 for p in evid_props
                    if match_result.matches.get(p["proposition_id"]) and match_result.matches[p["proposition_id"]].classification in ("preserved", "altered")
                )
                rows.append(_row("evidential_proposition_preservation_rate", round(kept / len(evid_props), 4), message_id, run_id))
            else:
                rows.append(_row("evidential_proposition_preservation_rate", None, message_id, run_id, "no_evidential_propositions_in_scope"))

            # Conflict resolution: for each conflict pair where both members are in_scope,
            # check if both are preserved (preserved-conflict) or only one (repaired-conflict).
            conflict_preserved = 0
            conflict_repaired = 0
            for pair in world["conflict_propositions"]:
                a, b = pair
                in_scope_a = a in in_scope
                in_scope_b = b in in_scope
                if not (in_scope_a or in_scope_b):
                    continue
                a_cls = match_result.matches.get(a, None)
                b_cls = match_result.matches.get(b, None)
                a_kept = a_cls is not None and a_cls.classification in ("preserved", "altered")
                b_kept = b_cls is not None and b_cls.classification in ("preserved", "altered")
                if in_scope_a and in_scope_b:
                    if a_kept and b_kept:
                        conflict_preserved += 1
                    elif a_kept or b_kept:
                        conflict_repaired += 1
                elif in_scope_a and a_kept:
                    # only one side was in scope; treat as not-a-conflict-test
                    pass
                elif in_scope_b and b_kept:
                    pass
            rows.append(_row("conflict_pairs_preserved", conflict_preserved, message_id, run_id))
            rows.append(_row("conflict_pairs_repaired", conflict_repaired, message_id, run_id))

            aux["match_result"] = {
                "matches": {pid: asdict(m) for pid, m in match_result.matches.items()},
                "unsupported_addition_count": match_result.unsupported_addition_count,
                "unsupported_addition_sentences": match_result.unsupported_addition_sentences,
            }

        return rows, aux


def feature_rows_to_dicts(rows: list[FeatureRow]) -> list[dict[str, Any]]:
    return [asdict(r) for r in rows]
