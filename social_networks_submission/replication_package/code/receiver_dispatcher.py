"""
Receiver dispatcher.

Given a trace packet, a candidate set, and a receiver model configuration:
1. Renders the receiver prompt (substituting trace-packet text and candidate-set text into the template).
2. Calls the receiver LLM (model-family separate from producer/mutator).
3. Parses the seven-output JSON response.
4. Validates the response structure.
5. Returns a structured dict alongside raw call metadata.

Per:
- `prompts/receiver_v0_1.txt` for the prompt template.
- `prompts/trace_packet_render_v0_1.md` for trace-packet rendering.
- `prompts/candidate_set_construction_v0_1.md` for candidate-set rendering.
- `schemas/ground_truth_schema_v0_1.json` for the ground-truth sidecar.

Literature anchors:
- ICD-203 likelihood + confidence-in-judgment separation.
- Tetlock-Mellers GJP probability bins.
- Tian et al. 2023 verbalized confidence elicitation.
- Heuer ACH explicit hypothesis enumeration.
- Admiralty Code two-dim source × information decomposition.
- Peñas-Rodrigo c@1 deferral option.
- RSA joint-listener framing.
- Model-family separation discipline (Geng et al. 2024 single-model fragility).
- Reproducibility-for-coding: greedy/temperature-zero decoding; self-contained natural-language prompts.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    # When imported as part of the src package (production path)
    from .candidate_set import CandidateSet, render_candidate_set
    from .model_client import PricingTable, call_model
    from .trace_packet_assembly import render_trace_packet
except ImportError:
    # When run as a standalone script for the demo. The demo only uses
    # _parse_and_validate, which doesn't require any of these imports.
    CandidateSet = None  # type: ignore
    render_candidate_set = None  # type: ignore
    PricingTable = None  # type: ignore
    call_model = None  # type: ignore
    render_trace_packet = None  # type: ignore


REGIME_KEYS = [
    "single_direct",
    "chain_relay",
    "independent_corroboration",
    "dependent_repetition",
    "common_source_laundering",
    "clustered_reinforcement",
    "centralized_synthesis",
    "compound",
]

PROBABILITY_BIN_LABELS = {
    "almost no chance",
    "very unlikely",
    "unlikely",
    "roughly even chance",
    "likely",
    "very likely",
    "almost certain",
}

CONFIDENCE_LABELS = {"low", "moderate", "high"}


@dataclass
class ReceiverResult:
    """One receiver call's parsed output plus raw call metadata."""
    parsed: dict | None  # the parsed seven-output JSON, or None if parse failed
    raw_output: str
    validation_errors: list[str]
    invalid: bool  # True if parsed is None or validation_errors is non-empty
    call_metadata: dict  # input_tokens, output_tokens, latency_seconds, etc.

    def to_dict(self) -> dict:
        return {
            "parsed": self.parsed,
            "raw_output": self.raw_output,
            "validation_errors": self.validation_errors,
            "invalid": self.invalid,
            "call_metadata": self.call_metadata,
        }


def load_receiver_prompt_template(prompt_path: Path | str) -> str:
    """Load the receiver prompt template (`prompts/receiver_v0_1.txt`)."""
    with Path(prompt_path).open() as f:
        return f.read()


def render_receiver_prompt(
    template: str,
    *,
    trace_packet: dict,
    candidate_set: CandidateSet,
    show_active_producer_flag: bool = True,
) -> str:
    """Substitute trace-packet text and candidate-set text into the receiver prompt template."""
    intercepted_message = trace_packet["intercepted_message"]
    trace_level = trace_packet["trace_level"]
    validity = trace_packet.get("validity_coefficient")
    validity_str = f"{validity:.2f}" if validity is not None else "N/A (L1)"
    context_packet_text = render_trace_packet(trace_packet)
    candidate_set_text = render_candidate_set(candidate_set, show_active_producer_flag=show_active_producer_flag)

    return (
        template.replace("{INTERCEPTED_MESSAGE}", intercepted_message)
        .replace("{TRACE_LEVEL}", str(trace_level))
        .replace("{VALIDITY_COEFFICIENT}", validity_str)
        .replace("{CONTEXT_PACKET_RENDERED}", context_packet_text)
        .replace("{CANDIDATE_SET_RENDERED}", candidate_set_text)
    )


def dispatch_receiver(
    *,
    trace_packet: dict,
    candidate_set: CandidateSet,
    receiver_prompt_template: str,
    receiver_model_config: dict,
    pricing: PricingTable | None = None,
) -> ReceiverResult:
    """
    Render the receiver prompt, call the receiver LLM, parse the JSON response, validate.

    receiver_model_config keys (from YAML):
      provider, model_name, temperature, top_p, max_output_tokens, seed_supported.

    Recommended config for paper 1: temperature=0.0 (greedy), top_p=1.0, max_output_tokens=2048.
    Receiver model family must differ from producer/mutator family (model-family separation).
    """
    prompt = render_receiver_prompt(
        receiver_prompt_template,
        trace_packet=trace_packet,
        candidate_set=candidate_set,
    )

    result = call_model(
        provider=receiver_model_config["provider"],
        model_name=receiver_model_config["model_name"],
        prompt=prompt,
        temperature=receiver_model_config.get("temperature", 0.0),
        top_p=receiver_model_config.get("top_p", 1.0),
        max_output_tokens=receiver_model_config.get("max_output_tokens", 2048),
        seed=receiver_model_config.get("seed"),
        pricing=pricing,
    )

    parsed, validation_errors = _parse_and_validate(result.raw_output, candidate_set)

    return ReceiverResult(
        parsed=parsed,
        raw_output=result.raw_output,
        validation_errors=validation_errors,
        invalid=(parsed is None or len(validation_errors) > 0),
        call_metadata={
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "usd_cost": result.usd_cost,
            "latency_seconds": result.latency_seconds,
            "api_error": result.api_error,
            "provider": receiver_model_config["provider"],
            "model_name": receiver_model_config["model_name"],
            "temperature": receiver_model_config.get("temperature", 0.0),
            "prompt_length_chars": len(prompt),
        },
    )


# ----------------------------------------------------------------------
# JSON extraction and validation
# ----------------------------------------------------------------------


def _extract_json(raw_output: str) -> dict | None:
    """
    Extract the first JSON object from the LLM's raw output.

    Robust to common LLM output artifacts: markdown code fences, leading/trailing prose.
    """
    if not raw_output:
        return None

    # Strip markdown code fences if present
    text = raw_output.strip()
    if text.startswith("```"):
        # Remove opening fence (with optional language tag) and closing fence
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fall back: find the first {...} block by brace matching
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


# Tolerance for posterior sum (LLM probabilities often round; we accept and auto-renormalize)
POSTERIOR_SUM_TOLERANCE = 0.15  # accept sums in [0.85, 1.15]; auto-renormalize


def _renormalize_posterior(posterior: dict[str, float]) -> dict[str, float]:
    """Renormalize a posterior dict to sum to 1.0. Returns a new dict."""
    s = sum(posterior.values())
    if s <= 0:
        n = len(posterior)
        return {k: 1.0 / n for k in posterior}
    return {k: v / s for k, v in posterior.items()}


def _edit_distance(a: str, b: str) -> int:
    """Simple Levenshtein edit distance."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        cur = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            cur.append(min(cur[-1] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = cur
    return prev[-1]


def _nearest_expected_key(key: str, expected: set[str], *, max_distance: int = 2) -> str | None:
    """Find the nearest expected key by edit distance, returning it if within max_distance."""
    best: tuple[int, str] | None = None
    for ek in expected:
        d = _edit_distance(key, ek)
        if d <= max_distance and (best is None or d < best[0]):
            best = (d, ek)
    return best[1] if best else None


def _parse_and_validate(raw_output: str, candidate_set: CandidateSet) -> tuple[dict | None, list[str]]:
    """Parse JSON, validate the seven-output structure, and auto-renormalize posteriors.

    Posteriors with sum within POSTERIOR_SUM_TOLERANCE of 1.0 are auto-renormalized
    in-place (LLM rounding tolerance). Outside that tolerance is a validation error.

    Returns (parsed_dict_or_None, list_of_errors).
    """
    parsed = _extract_json(raw_output)
    if parsed is None:
        return None, ["Failed to extract valid JSON from raw_output"]

    errors: list[str] = []

    # Top-level required keys
    for key in ("accuracy", "regime", "origin", "independence_judgment"):
        if key not in parsed:
            errors.append(f"Missing top-level key: {key}")

    if errors:
        return parsed, errors

    lo, hi = 1.0 - POSTERIOR_SUM_TOLERANCE, 1.0 + POSTERIOR_SUM_TOLERANCE

    # accuracy block
    acc = parsed["accuracy"]
    if not isinstance(acc.get("probability"), (int, float)):
        errors.append("accuracy.probability is not numeric")
    elif not (0.0 <= acc["probability"] <= 1.0):
        errors.append(f"accuracy.probability out of [0, 1]: {acc['probability']}")
    if acc.get("probability_bin") not in PROBABILITY_BIN_LABELS:
        errors.append(f"accuracy.probability_bin invalid: {acc.get('probability_bin')}")
    if acc.get("confidence_in_judgment") not in CONFIDENCE_LABELS:
        errors.append(f"accuracy.confidence_in_judgment invalid: {acc.get('confidence_in_judgment')}")

    # regime block
    reg = parsed["regime"]
    posterior = reg.get("posterior", {})
    missing = [k for k in REGIME_KEYS if k not in posterior]
    if missing:
        errors.append(f"regime.posterior missing keys: {missing}")
    if not missing:
        # Validate values are in [0, 1] (allow small over-1 from rounding)
        for k in REGIME_KEYS:
            v = posterior[k]
            if v < -0.01 or v > 1.01:
                errors.append(f"regime.posterior[{k}] grossly out of [0, 1]: {v}")
        # Validate sum within tolerance, then renormalize
        s = sum(posterior[k] for k in REGIME_KEYS)
        if not (lo <= s <= hi):
            errors.append(f"regime.posterior sum out of [{lo:.2f}, {hi:.2f}]: {s:.4f}")
        else:
            # Auto-renormalize
            reg["posterior"] = _renormalize_posterior({k: max(0.0, posterior[k]) for k in REGIME_KEYS})
    if reg.get("confidence_in_judgment") not in CONFIDENCE_LABELS:
        errors.append(f"regime.confidence_in_judgment invalid: {reg.get('confidence_in_judgment')}")

    # origin block — permissive: receivers may omit zero-probability candidates;
    # receivers may also typo candidate IDs. Auto-fill missing with 0; soft-match
    # unexpected keys against the candidate list by edit distance; drop unmatched.
    org = parsed["origin"]
    origin_posterior = org.get("posterior", {})
    expected_origin_keys = {c["persona_id"] for c in candidate_set.candidates} | {"outside_set", "unknown_deferred"}

    # Soft-match unexpected keys to nearest candidate ID (edit distance ≤ 2)
    extra_origin_keys = set(origin_posterior.keys()) - expected_origin_keys
    soft_matched_pairs: list[tuple[str, str]] = []
    for extra_key in list(extra_origin_keys):
        nearest = _nearest_expected_key(extra_key, expected_origin_keys, max_distance=2)
        if nearest is not None and nearest not in origin_posterior:
            # Merge the typo's probability into the nearest valid key
            origin_posterior[nearest] = origin_posterior.pop(extra_key)
            soft_matched_pairs.append((extra_key, nearest))
        else:
            # Unmatched typo: drop it (with a warning logged via a non-fatal note)
            origin_posterior.pop(extra_key, None)

    # Auto-fill any missing expected keys with 0
    for k in expected_origin_keys:
        if k not in origin_posterior:
            origin_posterior[k] = 0.0

    # Always renormalize as long as sum is positive. At CS-M (30 candidates) and higher,
    # receivers frequently produce sums grossly off from 1.0 (range observed in B-prime
    # early phase: 0.30 - 1.95) while their relative weights remain meaningful.
    # Renormalization preserves the receiver's intent; the only true error is a non-positive
    # sum (model produced no signal). Annotate large gaps from 1.0 for downstream filtering.
    s = sum(origin_posterior.values())
    if s <= 0:
        errors.append(f"origin.posterior sum non-positive: {s:.4f}")
    else:
        if not (0.85 <= s <= 1.15):
            org.setdefault("_repairs", {})["origin_sum_pre_renormalize"] = round(s, 4)
        org["posterior"] = _renormalize_posterior({k: max(0.0, v) for k, v in origin_posterior.items()})
        if soft_matched_pairs:
            org.setdefault("_repairs", {})["soft_matched_typos"] = soft_matched_pairs
    if org.get("confidence_in_judgment") not in CONFIDENCE_LABELS:
        errors.append(f"origin.confidence_in_judgment invalid: {org.get('confidence_in_judgment')}")

    # independence_judgment block
    # For single-source regimes, the receiver is instructed to set probability_independent=null,
    # confidence_in_judgment=null, reasoning="N/A — single-source regime". Some receivers may put
    # the "N/A — single-source regime" text in confidence_in_judgment instead of (or in addition
    # to) reasoning — accept that as the equivalent of null.
    indep = parsed["independence_judgment"]
    p_indep = indep.get("probability_independent")
    if p_indep is not None and not (0.0 <= p_indep <= 1.0):
        errors.append(f"independence_judgment.probability_independent out of [0, 1]: {p_indep}")
    indep_conf = indep.get("confidence_in_judgment")
    is_na_text = isinstance(indep_conf, str) and "n/a" in indep_conf.lower()
    if indep_conf is not None and indep_conf not in CONFIDENCE_LABELS and not is_na_text:
        errors.append(f"independence_judgment.confidence_in_judgment invalid: {indep_conf}")

    return parsed, errors


def receiver_output_to_record(
    receiver_result: ReceiverResult,
    *,
    trace_packet_id: str,
    candidate_set_id: str,
    receiver_family: str,
) -> dict:
    """Convert a ReceiverResult into a flat record suitable for trace storage."""
    return {
        "trace_packet_id": trace_packet_id,
        "candidate_set_id": candidate_set_id,
        "receiver_family": receiver_family,
        "predictor_kind": f"receiver_{receiver_family}",
        "parsed": receiver_result.parsed,
        "raw_output": receiver_result.raw_output,
        "invalid": receiver_result.invalid,
        "validation_errors": receiver_result.validation_errors,
        "call_metadata": receiver_result.call_metadata,
    }


def _main_demo() -> None:
    """Demonstration: validate the JSON-extraction and validation pipeline on a synthetic response."""
    # Synthetic valid response
    sample = """```json
{
  "accuracy": {
    "probability": 0.65,
    "probability_bin": "likely",
    "confidence_in_judgment": "moderate",
    "reasoning": "Demo"
  },
  "regime": {
    "posterior": {
      "single_direct": 0.05,
      "chain_relay": 0.40,
      "independent_corroboration": 0.05,
      "dependent_repetition": 0.20,
      "common_source_laundering": 0.10,
      "clustered_reinforcement": 0.05,
      "centralized_synthesis": 0.10,
      "compound": 0.05
    },
    "confidence_in_judgment": "low",
    "reasoning": "Demo"
  },
  "origin": {
    "posterior": {
      "OPS-OFFICER-ALPHA-1": 0.20,
      "OPS-OFFICER-BRAVO-1": 0.15,
      "FIELD-ANALYST-NORTH-1": 0.10,
      "outside_set": 0.30,
      "unknown_deferred": 0.25
    },
    "confidence_in_judgment": "low",
    "reasoning": "Demo"
  },
  "independence_judgment": {
    "probability_independent": 0.30,
    "confidence_in_judgment": "moderate",
    "reasoning": "Demo"
  }
}
```"""

    # Mock candidate set with the three candidates the JSON references
    from dataclasses import dataclass as dc
    candidates = [
        {"persona_id": "OPS-OFFICER-ALPHA-1", "role_descriptor": "demo"},
        {"persona_id": "OPS-OFFICER-BRAVO-1", "role_descriptor": "demo"},
        {"persona_id": "FIELD-ANALYST-NORTH-1", "role_descriptor": "demo"},
    ]

    @dc
    class MockCS:
        candidates: list
        candidate_set_id: str = "demo"

    mcs = MockCS(candidates=candidates)
    parsed, errors = _parse_and_validate(sample, mcs)
    print("Parsed JSON keys:", list(parsed.keys()) if parsed else None)
    print("Validation errors:", errors)
    if not errors:
        print("Validation PASSED on synthetic sample.")
    else:
        print("Validation FAILED.")


if __name__ == "__main__":
    _main_demo()
