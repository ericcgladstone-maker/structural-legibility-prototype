"""
Trace-packet assembly and rendering.

Builds trace packets at each trace level (L1-L6) from lineage data + cell spec,
and renders the JSON packet as the natural-language text the receiver consumes.

Per:
- `schemas/trace_packet_schema_v0_1.json` for the JSON structure.
- `prompts/trace_packet_render_v0_1.md` for the deterministic JSON-to-text rendering rule.

Validity-coefficient operationalization: Steffens cost-of-forgery. At validity v < 1.0,
some fraction of trace fields are flagged as forged/contaminated. The forging procedure
is deterministic given the seed.

Literature anchors:
- W3C PROV (Moreau-Missier 2013) for L4 path metadata.
- Admiralty Code (NATO STANAG / Joseph-Corkill 2011) for L3 source-reliability + information-credibility.
- HUMINT report format for L5 collection context.
- ICD-203 finished-product structure for L6 analytic packet.
- Steffens (2020) cost-of-forgery for validity-coefficient operationalization.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ADMIRALTY_RELIABILITY_DESCRIPTIONS = {
    "A": "completely reliable",
    "B": "usually reliable",
    "C": "fairly reliable",
    "D": "not usually reliable",
    "E": "unreliable",
    "F": "cannot be judged",
}

ADMIRALTY_CREDIBILITY_DESCRIPTIONS = {
    "1": "confirmed by other independent sources",
    "2": "probably true",
    "3": "possibly true",
    "4": "doubtful",
    "5": "improbable",
    "6": "cannot be judged",
}


@dataclass
class LineageData:
    """Lineage produced by a regime instantiator. The trace packet is assembled from this."""
    lineage_id: str
    regime: str  # one of the 8 regimes
    intercepted_message: str  # the terminal Mᵢ
    hops: list[dict] = field(default_factory=list)  # ordered list of agent transitions; step 0 = source
    interception_method: str = "open-source web monitoring"  # default
    interception_channel: str = "operational reporting channel"
    interception_timestamp: str | None = None  # ISO timestamp
    proximate_sender_persona: dict | None = None  # the persona at the immediate upstream hop


def build_trace_packet(
    *,
    lineage: LineageData,
    trace_packet_id: str,
    trace_level: int,
    validity_coefficient: float | None,
    seed: int,
    persona_pool: dict[str, dict] | None = None,
) -> dict:
    """
    Build a trace packet at the specified trace level with the specified validity coefficient.

    Parameters
    ----------
    lineage : LineageData object describing the production lineage.
    trace_packet_id : unique identifier for this packet.
    trace_level : 1-6.
    validity_coefficient : 0.0-1.0; None at L1 (no trace to be invalid about).
    seed : RNG seed for deterministic forging.
    persona_pool : optional dict[persona_id -> persona dict] used to look up Admiralty ratings.
    """
    if trace_level not in (1, 2, 3, 4, 5, 6):
        raise ValueError(f"trace_level must be 1-6, got {trace_level}")

    packet: dict[str, Any] = {
        "trace_packet_id": trace_packet_id,
        "lineage_id": lineage.lineage_id,
        "trace_level": trace_level,
        "validity_coefficient": validity_coefficient,
        "intercepted_message": lineage.intercepted_message,
    }

    rng = random.Random(seed)

    if trace_level >= 2:
        packet["source_label"] = _build_source_label(lineage, rng, validity_coefficient or 1.0)

    if trace_level >= 3:
        packet["admiralty_rating"] = _build_admiralty_rating(lineage, rng, validity_coefficient or 1.0, persona_pool)

    if trace_level >= 4:
        packet["path_metadata"] = _build_path_metadata(lineage, rng, validity_coefficient or 1.0)

    if trace_level >= 5:
        packet["collection_context"] = _build_collection_context(lineage)

    if trace_level >= 6:
        packet["analytic_packet"] = _build_analytic_packet(lineage, rng)

    return packet


def _build_source_label(lineage: LineageData, rng: random.Random, validity: float) -> dict:
    """L2: proximate sender label. Forging: at low validity, label may be forged (incorrect sender)."""
    if lineage.proximate_sender_persona is None:
        return {"label": "unknown", "label_type": "anonymous"}
    if rng.random() < (1.0 - validity):
        # Forged label: use a different persona's ID
        return {
            "label": "forged_unknown",
            "label_type": "anonymous",
        }
    return {
        "label": lineage.proximate_sender_persona["persona_id"],
        "label_type": "named" if "OFFICER" in lineage.proximate_sender_persona["persona_id"] else "pseudonymous",
    }


def _build_admiralty_rating(
    lineage: LineageData, rng: random.Random, validity: float, persona_pool: dict[str, dict] | None
) -> dict:
    """L3: Admiralty Code A-F × 1-6 rating on the proximate sender."""
    # Source reliability: use persona's baseline rating if available; otherwise default
    if (
        persona_pool is not None
        and lineage.proximate_sender_persona is not None
        and lineage.proximate_sender_persona["persona_id"] in persona_pool
    ):
        baseline = persona_pool[lineage.proximate_sender_persona["persona_id"]]["baseline_admiralty_reliability"]
    else:
        baseline = "C"  # fairly reliable, default

    if rng.random() < (1.0 - validity):
        # Forged rating: shift one notch in random direction
        levels = ["A", "B", "C", "D", "E", "F"]
        idx = levels.index(baseline)
        shift = rng.choice([-1, 1])
        new_idx = max(0, min(len(levels) - 1, idx + shift))
        source_reliability = levels[new_idx]
    else:
        source_reliability = baseline

    # Information credibility: assign based on regime characteristics
    # (Default 3 = "possibly true". At low validity, may be inflated to 1-2.)
    info_credibility = "3"
    if rng.random() < (1.0 - validity):
        # Forged credibility: inflated to 1 or 2
        info_credibility = rng.choice(["1", "2"])

    return {
        "source_reliability": source_reliability,
        "information_credibility": info_credibility,
    }


def _build_path_metadata(lineage: LineageData, rng: random.Random, validity: float) -> dict:
    """L4: PROV-style path metadata. At low validity, some hops are flagged as forged."""
    hops_with_authenticity = []
    for hop in lineage.hops:
        is_authentic = rng.random() < validity
        annotated_hop = {
            "step": hop["step"],
            "agent_identifier": hop["agent_identifier"] if is_authentic else f"forged_{hop['agent_identifier']}",
            "transformation_type": hop.get("transformation_type", "unknown"),
            "timestamp": hop.get("timestamp"),
            "field_known_to_be_authentic": is_authentic,
        }
        hops_with_authenticity.append(annotated_hop)
    return {"hops": hops_with_authenticity}


def _build_collection_context(lineage: LineageData) -> dict:
    """L5: HUMINT-style collection context."""
    return {
        "interception_method": lineage.interception_method,
        "interception_channel": lineage.interception_channel,
        "interception_timestamp": lineage.interception_timestamp,
        "collection_source_descriptor": None,
    }


def _build_analytic_packet(lineage: LineageData, rng: random.Random) -> dict:
    """L6: ICD-203-style analytic packet. v0.1 generates a minimal default; production work would have analyst input."""
    return {
        "key_judgments": [f"Intercepted message attributed to regime: {lineage.regime}"],
        "supporting_evidence": ["Hop metadata indicates relay through identified intermediaries."],
        "alternative_hypotheses": ["The intercepted message may have been produced by an alternative regime."],
        "analytic_confidence": "moderate",
        "dissenting_views": [],
    }


# ----------------------------------------------------------------------
# Rendering (JSON -> natural language)
# ----------------------------------------------------------------------


def render_trace_packet(packet: dict) -> str:
    """
    Render a trace packet as natural-language text for the receiver prompt.

    Follows `prompts/trace_packet_render_v0_1.md`. Deterministic: same JSON -> same text.
    """
    parts: list[str] = []
    trace_level = packet["trace_level"]

    if trace_level == 1:
        parts.append("(No trace context available beyond the intercepted message itself.)")
        return "\n".join(parts)

    if trace_level >= 2 and packet.get("source_label"):
        sl = packet["source_label"]
        parts.append(f"Proximate sender: {sl['label']}")
        parts.append(f"Sender identifier type: {sl['label_type']}")

    if trace_level >= 3 and packet.get("admiralty_rating"):
        ar = packet["admiralty_rating"]
        rel_letter = ar["source_reliability"]
        cred_num = ar["information_credibility"]
        parts.append(
            f"Source reliability (Admiralty): {rel_letter} — {ADMIRALTY_RELIABILITY_DESCRIPTIONS.get(rel_letter, 'unspecified')}"
        )
        parts.append(
            f"Information credibility (Admiralty): {cred_num} — {ADMIRALTY_CREDIBILITY_DESCRIPTIONS.get(cred_num, 'unspecified')}"
        )

    if trace_level >= 4 and packet.get("path_metadata"):
        parts.append("Path metadata (transmission chain from origin to interception):")
        for hop in packet["path_metadata"]["hops"]:
            step = hop["step"]
            agent = hop["agent_identifier"]
            tform = hop["transformation_type"]
            ts = hop.get("timestamp")
            authentic = hop.get("field_known_to_be_authentic", True)
            timestamp_clause = f" at {ts}" if ts else ""
            authenticity_clause = "" if authentic else " [authenticity uncertain]"
            label = "source" if step == 0 else "intercepted here" if step == len(packet["path_metadata"]["hops"]) - 1 else f"step {step}"
            parts.append(f"  Step {step} ({label}): {agent} — {tform}{timestamp_clause}{authenticity_clause}")

    if trace_level >= 5 and packet.get("collection_context"):
        cc = packet["collection_context"]
        parts.append("Collection context:")
        parts.append(f"  Method: {cc.get('interception_method', 'unspecified')}")
        parts.append(f"  Channel: {cc.get('interception_channel', 'unspecified')}")
        parts.append(f"  Time of interception: {cc.get('interception_timestamp') or 'unspecified'}")
        parts.append(f"  Collection source: {cc.get('collection_source_descriptor') or 'unspecified'}")

    if trace_level >= 6 and packet.get("analytic_packet"):
        ap = packet["analytic_packet"]
        parts.append("Prior analyst assessment:")
        parts.append("  Key judgments:")
        for kj in ap.get("key_judgments", []):
            parts.append(f"    - {kj}")
        parts.append("  Supporting evidence:")
        for ev in ap.get("supporting_evidence", []):
            parts.append(f"    - {ev}")
        parts.append("  Alternative hypotheses considered:")
        for alt in ap.get("alternative_hypotheses", []):
            parts.append(f"    - {alt}")
        parts.append(f"  Analyst confidence: {ap.get('analytic_confidence', 'unspecified')}")
        dv = ap.get("dissenting_views") or []
        if dv:
            parts.append("  Dissenting views:")
            for d in dv:
                parts.append(f"    - {d}")
        else:
            parts.append("  Dissenting views: None recorded.")

    # Validity-coefficient annotation
    v = packet.get("validity_coefficient")
    if v is not None:
        parts.append(
            f"\nTrace-validity note: The trace fields above are reported as observed by the receiver. "
            f"Some fields may be partially or wholly forged or contaminated. "
            f"Validity coefficient: {v:.2f} (1.00 = trace fully reliable; 0.00 = trace fields entirely contaminated)."
        )

    return "\n".join(parts)


def _main_demo() -> None:
    """Demonstration: build and render trace packets at each L level."""
    lineage = LineageData(
        lineage_id="demo_lineage_1",
        regime="chain_relay",
        intercepted_message="The cooling system at Site B malfunctioned at 09:40. Maintenance has confirmed.",
        hops=[
            {"step": 0, "agent_identifier": "OPS-OFFICER-ALPHA-1", "transformation_type": "relay", "timestamp": "2026-05-14T09:45:00Z"},
            {"step": 1, "agent_identifier": "OPS-OFFICER-BRAVO-1", "transformation_type": "relay", "timestamp": "2026-05-14T09:50:00Z"},
            {"step": 2, "agent_identifier": "REGIONAL-COORD-HUB-1", "transformation_type": "relay", "timestamp": "2026-05-14T10:05:00Z"},
        ],
        interception_method="open-source operational monitoring",
        interception_channel="standard reporting channel",
        interception_timestamp="2026-05-14T10:15:00Z",
        proximate_sender_persona={"persona_id": "REGIONAL-COORD-HUB-1"},
    )

    for level in (1, 3, 5, 6):
        packet = build_trace_packet(
            lineage=lineage,
            trace_packet_id=f"demo_tp_L{level}",
            trace_level=level,
            validity_coefficient=0.95 if level > 1 else None,
            seed=42,
        )
        print(f"\n=== L{level} packet ===")
        rendered = render_trace_packet(packet)
        print(rendered)


if __name__ == "__main__":
    _main_demo()
