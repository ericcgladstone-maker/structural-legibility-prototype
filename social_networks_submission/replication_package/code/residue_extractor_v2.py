"""Residue extractor v0.2.

Same surface, dictionary, embedding, and proposition features as v0.1, but
uses `PropositionMatcherV2` and reports the new `preserved_qualified` label
in proposition-level counts.

New features added:
    proposition_qualified_count      number of propositions in scope classified as preserved_qualified

Modified features:
    proposition_preservation_rate    now counts preserved + preserved_qualified + altered as kept
    proposition_contradiction_count  uses tighter v0.2 contradiction rule
    conflict_pairs_preserved         counts a pair as preserved if both members have a "kept" label
    conflict_pairs_repaired          counts a pair as repaired if exactly one is kept

Output rows are tagged `extractor_version: residue_extractor_v0_2`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import numpy as np

from .model_client import EmbeddingClient
from .proposition_matcher_v2 import (
    PropositionMatcherV2,
    MatchResultV2,
    KEPT_LABELS,
    alteration_count,
    contradiction_count,
    omission_count,
    preservation_rate,
    qualified_count,
)
from .residue_extractor import (
    Dictionary,
    FeatureRow,
    NUMERIC_RE,
    NAMED_ENTITY_RE,
    TIME_RE,
    LOCATION_RE,
    TOKEN_RE,
    token_count,
    sentence_count,
    type_token_ratio,
    mean_sentence_length,
    mean_word_length,
    punctuation_density,
)


EXTRACTOR_VERSION = "residue_extractor_v0_2"


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


class ResidueExtractorV2:
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
        self.matcher = PropositionMatcherV2(embedder)

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
        rows: list[FeatureRow] = []
        aux: dict[str, Any] = {}

        if message_text is None or message_text.strip() == "":
            rows.append(_row("token_count", 0, message_id, run_id, "empty_message"))
            return rows, aux

        # Surface
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

        # Dictionary
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

        # Drift
        try:
            msg_emb = self.embedder.embed([message_text])[0]
            if parent_text:
                par_emb = self.embedder.embed([parent_text])[0]
                rows.append(_row("semantic_drift_from_parent", round(1.0 - float(np.dot(msg_emb, par_emb)), 4), message_id, run_id))
            else:
                rows.append(_row("semantic_drift_from_parent", None, message_id, run_id, "no_parent_text"))
            if original_text:
                orig_emb = self.embedder.embed([original_text])[0]
                rows.append(_row("semantic_drift_from_original", round(1.0 - float(np.dot(msg_emb, orig_emb)), 4), message_id, run_id))
            else:
                rows.append(_row("semantic_drift_from_original", None, message_id, run_id, "no_original_text"))
        except Exception as e:
            rows.append(_row("semantic_drift_from_parent", None, message_id, run_id, f"embed_error:{type(e).__name__}"))
            rows.append(_row("semantic_drift_from_original", None, message_id, run_id, f"embed_error:{type(e).__name__}"))

        # Proposition-level with v0.2 matcher
        if world is not None:
            match_result = self.matcher.match(message_text, world, in_scope_proposition_ids)
            in_scope = in_scope_proposition_ids or [p["proposition_id"] for p in world["propositions"]]

            rows.append(_row("proposition_preservation_rate", preservation_rate(match_result, in_scope), message_id, run_id))
            rows.append(_row("proposition_omission_count", omission_count(match_result, in_scope), message_id, run_id))
            rows.append(_row("proposition_alteration_count", alteration_count(match_result, in_scope), message_id, run_id))
            rows.append(_row("proposition_contradiction_count", contradiction_count(match_result), message_id, run_id))
            rows.append(_row("proposition_qualified_count", qualified_count(match_result), message_id, run_id))
            rows.append(_row("unsupported_addition_count", match_result.unsupported_addition_count, message_id, run_id))

            # Uncertainty-prop preservation
            uncertain_props = [p for p in world["propositions"] if p["proposition_id"] in in_scope and p["uncertainty"] < 0.8]
            if uncertain_props:
                kept = sum(
                    1 for p in uncertain_props
                    if match_result.matches.get(p["proposition_id"]) and match_result.matches[p["proposition_id"]].classification in KEPT_LABELS
                )
                rows.append(_row("uncertainty_proposition_preservation_rate", round(kept / len(uncertain_props), 4), message_id, run_id))
            else:
                rows.append(_row("uncertainty_proposition_preservation_rate", None, message_id, run_id, "no_uncertain_propositions_in_scope"))

            # Evidential-prop preservation
            evid_props = [p for p in world["propositions"] if p["proposition_id"] in in_scope and p["evidence_type"] in ("report", "log_record")]
            if evid_props:
                kept = sum(
                    1 for p in evid_props
                    if match_result.matches.get(p["proposition_id"]) and match_result.matches[p["proposition_id"]].classification in KEPT_LABELS
                )
                rows.append(_row("evidential_proposition_preservation_rate", round(kept / len(evid_props), 4), message_id, run_id))
            else:
                rows.append(_row("evidential_proposition_preservation_rate", None, message_id, run_id, "no_evidential_propositions_in_scope"))

            # Conflict pairs under v0.2 logic.
            conflict_preserved = 0
            conflict_repaired = 0
            conflict_erased = 0
            for pair in world["conflict_propositions"]:
                a, b = pair
                in_scope_a = a in in_scope
                in_scope_b = b in in_scope
                if not (in_scope_a and in_scope_b):
                    continue
                a_cls = match_result.matches.get(a)
                b_cls = match_result.matches.get(b)
                a_kept = a_cls is not None and a_cls.classification in KEPT_LABELS
                b_kept = b_cls is not None and b_cls.classification in KEPT_LABELS
                if a_kept and b_kept:
                    conflict_preserved += 1
                elif a_kept or b_kept:
                    conflict_repaired += 1
                else:
                    conflict_erased += 1
            rows.append(_row("conflict_pairs_preserved", conflict_preserved, message_id, run_id))
            rows.append(_row("conflict_pairs_repaired", conflict_repaired, message_id, run_id))
            rows.append(_row("conflict_pairs_erased", conflict_erased, message_id, run_id))

            aux["match_result"] = {
                "matcher_version": match_result.matcher_version,
                "matches": {pid: asdict(m) for pid, m in match_result.matches.items()},
                "unsupported_addition_count": match_result.unsupported_addition_count,
                "unsupported_addition_sentences": match_result.unsupported_addition_sentences,
            }

        return rows, aux
