"""
Regime instantiators for paper 1.

Implements the 5 new regimes added under the converged receiver-centered framing:
- R1 single_direct: 1 producer, 0 intermediaries.
- R2 independent_corroboration: 3 independent observers of the same world; intercept one.
- R3 dependent_repetition: 1 source + 3 dependent relayers (each framed as independent); intercept one.
- R4 common_source_laundering: 1 source + 3 laundering relayers (upstream identity hidden); intercept one.
- R5 clustered_reinforcement: 1 source + 3 cluster echoes; intercept one.

R6 (centralized_synthesis) and R7 (chain_relay) already exist in `run_experiment.py`
as `_run_hub` and `_run_chain`. R8 (compound) is composed of two of the above and is
implemented as an orchestration pattern (see `compose_compound_regime`).

Each instantiator returns a run dict with the standard fields plus `lineage_metadata`
suitable for downstream trace-packet assembly + ground-truth emission.

Literature anchors:
- Mesoudi-Whiten (2008) transmission-chain methodology.
- Kempe-Kleinberg-Tardos (2003) independent-cascade for R5.
- Acerbi-Stubbersfield (2023) LLM-content-bias controls.
- Park et al. (2023) generative-agent architecture.
- Schum cascaded inference for ground-truth labeling.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from .model_client import PricingTable, call_model
from .run_experiment import (
    _generate_source,
    _make_call_record,
    _read_prompt,
    new_id,
    render_relay_prompt,
    render_synthesis_prompt,
    utcnow_iso,
)


REGIME_LABELS = {
    "single_direct",
    "chain_relay",
    "independent_corroboration",
    "dependent_repetition",
    "common_source_laundering",
    "clustered_reinforcement",
    "centralized_synthesis",
    "compound",
}

# Regime-specific producer/relayer prompt pools (matching the prompts on disk).
INDEPENDENT_OBSERVER_PROMPTS = [
    "independent_observer_a_v0_1",
    "independent_observer_b_v0_1",
    "independent_observer_c_v0_1",
]
DEPENDENT_RELAYER_PROMPTS = [
    "dependent_relayer_a_v0_1",
    "dependent_relayer_b_v0_1",
    "dependent_relayer_c_v0_1",
]
LAUNDERING_RELAYER_PROMPTS = [
    "laundering_relayer_a_v0_1",
    "laundering_relayer_b_v0_1",
    "laundering_relayer_c_v0_1",
]
CLUSTER_ECHO_PROMPTS = [
    "cluster_echo_a_v0_1",
    "cluster_echo_b_v0_1",
    "cluster_echo_c_v0_1",
]


# ----------------------------------------------------------------------
# Context and helpers
# ----------------------------------------------------------------------


@dataclass
class RegimeContext:
    """Inputs and resources shared across regime instantiators."""
    world: dict
    persona_pool: list[dict]
    cfg: dict
    pricing: PricingTable
    root: str
    run_order_index: int
    rng: random.Random


def _pick_personas(
    pool: list[dict], n: int, rng: random.Random, *, category: str | None = None
) -> list[dict]:
    """
    Sample n distinct personas from the pool, optionally filtered to an
    operational_category. Falls back to broader pool if category-filtered
    pool is too small.
    """
    if category is not None:
        filtered = [p for p in pool if p["operational_category"] == category]
        if len(filtered) >= n:
            return rng.sample(filtered, n)
    if len(pool) < n:
        raise ValueError(f"Persona pool has {len(pool)} entries, need {n}")
    return rng.sample(pool, n)


def _call_mutator(
    *,
    role: str,
    prompt: str,
    prompt_variant: str,
    cfg: dict,
    pricing: PricingTable,
) -> tuple[str, dict]:
    """Call the mutator LLM with the rendered prompt; return (text, call_record)."""
    mut_cfg = cfg["models"]["mutator"]
    result = call_model(
        provider=mut_cfg["provider"],
        model_name=mut_cfg["model_name"],
        prompt=prompt,
        temperature=mut_cfg["temperature"],
        top_p=mut_cfg["top_p"],
        max_output_tokens=mut_cfg["max_output_tokens"],
        seed=None,
        pricing=pricing,
    )
    call = _make_call_record(
        role=role,
        provider=mut_cfg["provider"],
        model_name=mut_cfg["model_name"],
        temperature=mut_cfg["temperature"],
        top_p=mut_cfg["top_p"],
        seed=None,
        full_prompt=prompt,
        result=result,
        prompt_variant=prompt_variant,
    )
    return result.raw_output, call


def _build_run_dict(
    *,
    ctx: RegimeContext,
    regime: str,
    messages: list[dict],
    calls: list[dict],
    errors: list[dict],
    intercepted_message_id: str,
    true_source_persona: dict,
    hops: list[dict],
    true_independence_label: bool | None,
) -> dict:
    """Assemble the canonical run dict + lineage_metadata."""
    return {
        "run_id": new_id("R"),
        "experiment_id": ctx.cfg["experiment_id"],
        "config_hash": "filled_by_caller",
        "component_versions": ctx.cfg["component_versions"],
        "created_at": utcnow_iso(),
        "run_order_index": ctx.run_order_index,
        "run_stage": "stage1_structural",
        "world_id": ctx.world["world_id"],
        "condition": regime,
        "condition_type": regime,
        "regime": regime,
        "messages": messages,
        "calls": calls,
        "feature_extractions": [],
        "errors": errors,
        "invalid": bool(errors),
        "lineage_metadata": {
            "intercepted_message_id": intercepted_message_id,
            "true_source_persona_id": true_source_persona["persona_id"],
            "true_source_persona": true_source_persona,
            "true_regime": regime,
            "true_independence_label": true_independence_label,
            "hops": hops,
        },
    }


def _build_hop(step: int, persona: dict, transformation_type: str) -> dict:
    """Build a PROV-style hop record for trace-packet assembly."""
    return {
        "step": step,
        "agent_identifier": persona["persona_id"],
        "transformation_type": transformation_type,
        "timestamp": utcnow_iso(),
    }


# ----------------------------------------------------------------------
# R1: single_direct
# ----------------------------------------------------------------------


def run_single_direct(ctx: RegimeContext) -> dict:
    """R1: 1 producer, no intermediaries. The source output is the terminal."""
    producer = _pick_personas(ctx.persona_pool, 1, ctx.rng)[0]

    src_text, src_call = _generate_source(
        world=ctx.world,
        proposition_ids=ctx.world["chain_original_propositions"],
        cfg=ctx.cfg,
        pricing=ctx.pricing,
        root=ctx.root,
    )
    src_call["role"] = f"source_producer_{producer['persona_id']}"

    errors: list[dict] = []
    if not src_text.strip() or src_call.get("api_error"):
        errors.append({"stage": "source_generation", "error": src_call.get("api_error") or "empty_output"})

    msg_id = new_id("M")
    msg = {
        "message_id": msg_id,
        "role": "source",
        "is_source_message": True,
        "parent_message_ids": [],
        "hop_index": 0,
        "text": src_text,
        "in_scope_propositions": ctx.world["chain_original_propositions"],
        "prompt_variant": ctx.cfg["component_versions"]["source_prompt"],
        "persona_id": producer["persona_id"],
    }

    return _build_run_dict(
        ctx=ctx,
        regime="single_direct",
        messages=[msg],
        calls=[src_call],
        errors=errors,
        intercepted_message_id=msg_id,
        true_source_persona=producer,
        hops=[_build_hop(0, producer, "direct")],
        true_independence_label=None,
    )


# ----------------------------------------------------------------------
# R2: independent_corroboration
# ----------------------------------------------------------------------


def run_independent_corroboration(ctx: RegimeContext) -> dict:
    """R2: 3 independent observers produce reports of the same world; intercept one."""
    observers = _pick_personas(ctx.persona_pool, 3, ctx.rng)

    messages: list[dict] = []
    calls: list[dict] = []
    errors: list[dict] = []

    for i, (observer, prompt_name) in enumerate(zip(observers, INDEPENDENT_OBSERVER_PROMPTS)):
        template = _read_prompt(ctx.root, prompt_name)
        world_details = _render_world_details(ctx.world)
        prompt = template.replace("{WORLD_DETAILS}", world_details)
        text, call = _call_mutator(
            role=f"independent_observer_{i}_{observer['persona_id']}",
            prompt=prompt,
            prompt_variant=prompt_name,
            cfg=ctx.cfg,
            pricing=ctx.pricing,
        )
        if not text.strip() or call.get("api_error"):
            errors.append({
                "stage": f"independent_observer_{i}",
                "error": call.get("api_error") or "empty_output",
            })

        mid = new_id("M")
        messages.append({
            "message_id": mid,
            "role": "independent_observer",
            "is_source_message": True,
            "parent_message_ids": [],
            "hop_index": 0,
            "text": text,
            "in_scope_propositions": ctx.world["chain_original_propositions"],
            "prompt_variant": prompt_name,
            "persona_id": observer["persona_id"],
        })
        calls.append(call)

    # Intercept a random one (deterministic given seed via the rng)
    intercepted_idx = ctx.rng.randint(0, len(messages) - 1)
    intercepted_msg = messages[intercepted_idx]
    intercepted_persona = observers[intercepted_idx]

    return _build_run_dict(
        ctx=ctx,
        regime="independent_corroboration",
        messages=messages,
        calls=calls,
        errors=errors,
        intercepted_message_id=intercepted_msg["message_id"],
        true_source_persona=intercepted_persona,
        hops=[_build_hop(0, intercepted_persona, "direct")],
        true_independence_label=True,
    )


# ----------------------------------------------------------------------
# R3: dependent_repetition
# ----------------------------------------------------------------------


def run_dependent_repetition(ctx: RegimeContext) -> dict:
    """R3: 1 upstream source + 3 dependent relayers each producing a derivative; intercept one relayer's output."""
    upstream, relayer_a, relayer_b, relayer_c = _pick_personas(ctx.persona_pool, 4, ctx.rng)
    relayers = [relayer_a, relayer_b, relayer_c]

    messages: list[dict] = []
    calls: list[dict] = []
    errors: list[dict] = []

    # 1. Upstream source produces M₀
    src_text, src_call = _generate_source(
        world=ctx.world,
        proposition_ids=ctx.world["chain_original_propositions"],
        cfg=ctx.cfg,
        pricing=ctx.pricing,
        root=ctx.root,
    )
    src_call["role"] = f"upstream_source_{upstream['persona_id']}"
    if not src_text.strip() or src_call.get("api_error"):
        errors.append({"stage": "upstream_source", "error": src_call.get("api_error") or "empty_output"})

    src_msg_id = new_id("M")
    messages.append({
        "message_id": src_msg_id,
        "role": "upstream_source",
        "is_source_message": True,
        "parent_message_ids": [],
        "hop_index": 0,
        "text": src_text,
        "in_scope_propositions": ctx.world["chain_original_propositions"],
        "prompt_variant": ctx.cfg["component_versions"]["source_prompt"],
        "persona_id": upstream["persona_id"],
    })
    calls.append(src_call)

    # 2. Three dependent relayers each produce a derivative
    relayer_msg_ids: list[str] = []
    for i, (relayer, prompt_name) in enumerate(zip(relayers, DEPENDENT_RELAYER_PROMPTS)):
        template = _read_prompt(ctx.root, prompt_name)
        prompt = template.replace("{INCOMING_MESSAGE}", src_text)
        text, call = _call_mutator(
            role=f"dependent_relayer_{i}_{relayer['persona_id']}",
            prompt=prompt,
            prompt_variant=prompt_name,
            cfg=ctx.cfg,
            pricing=ctx.pricing,
        )
        if not text.strip() or call.get("api_error"):
            errors.append({"stage": f"dependent_relayer_{i}", "error": call.get("api_error") or "empty_output"})

        mid = new_id("M")
        messages.append({
            "message_id": mid,
            "role": "dependent_relayer",
            "is_source_message": False,
            "parent_message_ids": [src_msg_id],
            "hop_index": 1,
            "text": text,
            "in_scope_propositions": ctx.world["chain_original_propositions"],
            "prompt_variant": prompt_name,
            "persona_id": relayer["persona_id"],
        })
        calls.append(call)
        relayer_msg_ids.append(mid)

    # 3. Intercept a random relayer's output
    intercepted_idx = ctx.rng.randint(0, len(relayer_msg_ids) - 1)
    intercepted_relayer = relayers[intercepted_idx]

    hops = [
        _build_hop(0, upstream, "source"),
        _build_hop(1, intercepted_relayer, "relay"),
    ]

    return _build_run_dict(
        ctx=ctx,
        regime="dependent_repetition",
        messages=messages,
        calls=calls,
        errors=errors,
        intercepted_message_id=relayer_msg_ids[intercepted_idx],
        true_source_persona=upstream,  # the upstream is the true originator
        hops=hops,
        true_independence_label=False,
    )


# ----------------------------------------------------------------------
# R4: common_source_laundering
# ----------------------------------------------------------------------


def run_common_source_laundering(ctx: RegimeContext) -> dict:
    """R4: like R3, but the upstream identity is concealed in the trace metadata.

    Topology is the same as R3; the difference is in:
    - The relayer prompts (laundering_relayer instead of dependent_relayer; explicit anti-attribution).
    - The trace-metadata hop[0] agent_identifier is recorded as 'hidden_upstream' rather than the real persona ID.
      (Trace-packet assembly + validity coefficient interact with this; under high validity the
       hidden_upstream sentinel still appears, modeling the laundering. Under low validity, false attributions
       could be injected — that's a v0.2 extension.)
    """
    upstream, relayer_a, relayer_b, relayer_c = _pick_personas(ctx.persona_pool, 4, ctx.rng)
    relayers = [relayer_a, relayer_b, relayer_c]

    messages: list[dict] = []
    calls: list[dict] = []
    errors: list[dict] = []

    src_text, src_call = _generate_source(
        world=ctx.world,
        proposition_ids=ctx.world["chain_original_propositions"],
        cfg=ctx.cfg,
        pricing=ctx.pricing,
        root=ctx.root,
    )
    src_call["role"] = f"laundering_upstream_{upstream['persona_id']}"
    if not src_text.strip() or src_call.get("api_error"):
        errors.append({"stage": "laundering_upstream", "error": src_call.get("api_error") or "empty_output"})

    src_msg_id = new_id("M")
    messages.append({
        "message_id": src_msg_id,
        "role": "laundering_upstream",
        "is_source_message": True,
        "parent_message_ids": [],
        "hop_index": 0,
        "text": src_text,
        "in_scope_propositions": ctx.world["chain_original_propositions"],
        "prompt_variant": ctx.cfg["component_versions"]["source_prompt"],
        "persona_id": upstream["persona_id"],
    })
    calls.append(src_call)

    relayer_msg_ids: list[str] = []
    for i, (relayer, prompt_name) in enumerate(zip(relayers, LAUNDERING_RELAYER_PROMPTS)):
        template = _read_prompt(ctx.root, prompt_name)
        prompt = template.replace("{INCOMING_MESSAGE}", src_text)
        text, call = _call_mutator(
            role=f"laundering_relayer_{i}_{relayer['persona_id']}",
            prompt=prompt,
            prompt_variant=prompt_name,
            cfg=ctx.cfg,
            pricing=ctx.pricing,
        )
        if not text.strip() or call.get("api_error"):
            errors.append({"stage": f"laundering_relayer_{i}", "error": call.get("api_error") or "empty_output"})

        mid = new_id("M")
        messages.append({
            "message_id": mid,
            "role": "laundering_relayer",
            "is_source_message": False,
            "parent_message_ids": [src_msg_id],
            "hop_index": 1,
            "text": text,
            "in_scope_propositions": ctx.world["chain_original_propositions"],
            "prompt_variant": prompt_name,
            "persona_id": relayer["persona_id"],
        })
        calls.append(call)
        relayer_msg_ids.append(mid)

    intercepted_idx = ctx.rng.randint(0, len(relayer_msg_ids) - 1)
    intercepted_relayer = relayers[intercepted_idx]

    # Trace-metadata hops: hop[0] is recorded as "hidden_upstream" — the upstream identity is concealed
    # in the path metadata the receiver eventually sees.
    hops = [
        {
            "step": 0,
            "agent_identifier": "hidden_upstream",
            "transformation_type": "source",
            "timestamp": utcnow_iso(),
        },
        _build_hop(1, intercepted_relayer, "relay"),
    ]

    return _build_run_dict(
        ctx=ctx,
        regime="common_source_laundering",
        messages=messages,
        calls=calls,
        errors=errors,
        intercepted_message_id=relayer_msg_ids[intercepted_idx],
        true_source_persona=upstream,  # the actual originator (concealed from receiver)
        hops=hops,
        true_independence_label=False,
    )


# ----------------------------------------------------------------------
# R5: clustered_reinforcement
# ----------------------------------------------------------------------


def run_clustered_reinforcement(ctx: RegimeContext) -> dict:
    """R5: source + 3 cluster echoes within a community. Intercept one.

    Topology: simple cluster (source produces M₀ → 3 cluster members each echo).
    More elaborate cluster topology (e.g., echo chain within cluster) is a v0.2 extension.
    """
    # Pick personas from the same operational category to model a community
    community_personas = _pick_personas(
        ctx.persona_pool, 4, ctx.rng,
        category=ctx.rng.choice(list({p["operational_category"] for p in ctx.persona_pool})),
    )
    source = community_personas[0]
    echos = community_personas[1:]

    messages: list[dict] = []
    calls: list[dict] = []
    errors: list[dict] = []

    src_text, src_call = _generate_source(
        world=ctx.world,
        proposition_ids=ctx.world["chain_original_propositions"],
        cfg=ctx.cfg,
        pricing=ctx.pricing,
        root=ctx.root,
    )
    src_call["role"] = f"cluster_source_{source['persona_id']}"
    if not src_text.strip() or src_call.get("api_error"):
        errors.append({"stage": "cluster_source", "error": src_call.get("api_error") or "empty_output"})

    src_msg_id = new_id("M")
    messages.append({
        "message_id": src_msg_id,
        "role": "cluster_source",
        "is_source_message": True,
        "parent_message_ids": [],
        "hop_index": 0,
        "text": src_text,
        "in_scope_propositions": ctx.world["chain_original_propositions"],
        "prompt_variant": ctx.cfg["component_versions"]["source_prompt"],
        "persona_id": source["persona_id"],
    })
    calls.append(src_call)

    echo_msg_ids: list[str] = []
    for i, (echo, prompt_name) in enumerate(zip(echos, CLUSTER_ECHO_PROMPTS)):
        template = _read_prompt(ctx.root, prompt_name)
        prompt = template.replace("{INCOMING_MESSAGE}", src_text)
        text, call = _call_mutator(
            role=f"cluster_echo_{i}_{echo['persona_id']}",
            prompt=prompt,
            prompt_variant=prompt_name,
            cfg=ctx.cfg,
            pricing=ctx.pricing,
        )
        if not text.strip() or call.get("api_error"):
            errors.append({"stage": f"cluster_echo_{i}", "error": call.get("api_error") or "empty_output"})

        mid = new_id("M")
        messages.append({
            "message_id": mid,
            "role": "cluster_echo",
            "is_source_message": False,
            "parent_message_ids": [src_msg_id],
            "hop_index": 1,
            "text": text,
            "in_scope_propositions": ctx.world["chain_original_propositions"],
            "prompt_variant": prompt_name,
            "persona_id": echo["persona_id"],
        })
        calls.append(call)
        echo_msg_ids.append(mid)

    intercepted_idx = ctx.rng.randint(0, len(echo_msg_ids) - 1)
    intercepted_echo = echos[intercepted_idx]

    hops = [
        _build_hop(0, source, "source"),
        _build_hop(1, intercepted_echo, "echo"),
    ]

    return _build_run_dict(
        ctx=ctx,
        regime="clustered_reinforcement",
        messages=messages,
        calls=calls,
        errors=errors,
        intercepted_message_id=echo_msg_ids[intercepted_idx],
        true_source_persona=source,
        hops=hops,
        true_independence_label=False,
    )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _render_world_details(world: dict) -> str:
    """Render the world's slot fields as a text block for producer prompts that take {WORLD_DETAILS}."""
    return (
        f"Event type: {world['event_type']}\n"
        f"Location: {world['location_id']}\n"
        f"Time: {world['time']}\n"
        f"Observed core event: {world['observed_core_event']}\n"
        f"Primary causal hypothesis: {world['primary_causal_hypothesis']}\n"
        f"Evidence for primary cause: {world['evidence_for_primary_cause']}\n"
        f"Alternative causal hypothesis: {world['alternative_causal_hypothesis']}\n"
        f"Evidence for alternative cause: {world['evidence_for_alternative_cause']}\n"
        f"Consequence: {world['consequence']}\n"
        f"Mitigation: {world['mitigation']}\n"
        f"Uncertainty fields: {', '.join(world['uncertainty_fields'])}\n"
        f"Peripheral operational detail: {world['peripheral_operational_detail']}\n"
    )


# ----------------------------------------------------------------------
# Dispatch
# ----------------------------------------------------------------------


REGIME_DISPATCH = {
    "single_direct": run_single_direct,
    "independent_corroboration": run_independent_corroboration,
    "dependent_repetition": run_dependent_repetition,
    "common_source_laundering": run_common_source_laundering,
    "clustered_reinforcement": run_clustered_reinforcement,
    # R6 centralized_synthesis: handled by run_experiment._run_hub
    # R7 chain_relay: handled by run_experiment._run_chain
    # R8 compound: composed via compose_compound_regime (orchestration pattern)
}


def run_regime(regime: str, ctx: RegimeContext) -> dict:
    """Dispatch to the appropriate regime instantiator. Raises ValueError for unknown regime."""
    if regime not in REGIME_DISPATCH:
        raise ValueError(
            f"Unknown regime: {regime}. Known: {sorted(REGIME_DISPATCH)}. "
            f"R6/R7 are handled by run_experiment._run_hub/_run_chain; R8 via compose_compound_regime."
        )
    return REGIME_DISPATCH[regime](ctx)


# ----------------------------------------------------------------------
# Sanity check helper
# ----------------------------------------------------------------------


def sanity_check_run(run: dict) -> list[str]:
    """Verify a regime-instantiator output is well-formed. Returns list of issues."""
    issues: list[str] = []
    for k in ("run_id", "regime", "world_id", "messages", "calls", "lineage_metadata"):
        if k not in run:
            issues.append(f"missing top-level key: {k}")
    if "regime" in run and run["regime"] not in REGIME_LABELS:
        issues.append(f"unknown regime label: {run['regime']}")
    lm = run.get("lineage_metadata", {})
    for k in ("intercepted_message_id", "true_source_persona_id", "true_regime", "hops"):
        if k not in lm:
            issues.append(f"lineage_metadata missing: {k}")
    intercepted_id = lm.get("intercepted_message_id")
    if intercepted_id and not any(m.get("message_id") == intercepted_id for m in run.get("messages", [])):
        issues.append(f"intercepted_message_id {intercepted_id} not in messages")
    return issues
