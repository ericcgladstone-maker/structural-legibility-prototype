"""Main experiment harness.

Usage (CLI via scripts/run_prototype.py or scripts/smoke_test.py):
    config = load_config("configs/chain_hub_proto_v0_1.yaml")
    run_experiment(config, prototype_root="prototype/", n_per_condition=1)

The harness produces:
    - a JSONL trace at outputs/<experiment_id>.trace.jsonl
    - a small console summary (passed/failed runs, total cost)

It does NOT run ETL or audit export; those are separate scripts.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
import yaml

from .model_client import EmbeddingClient, PricingTable, call_model
from .residue_extractor import Dictionary, ResidueExtractor, feature_rows_to_dicts
from .trace_writer import TraceWriter
from .world_loader import load_worlds, render_proposition_list


class PreflightError(RuntimeError):
    pass


# ----------------------------------------------------------------------
# Config loading
# ----------------------------------------------------------------------

@dataclass
class LoadedConfig:
    raw: dict[str, Any]
    prototype_root: str
    config_path: str
    config_hash: str


def load_config(config_path: str, prototype_root: str | None = None) -> LoadedConfig:
    with open(config_path) as f:
        text = f.read()
    raw = yaml.safe_load(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    root = prototype_root or os.path.dirname(os.path.dirname(os.path.abspath(config_path)))
    return LoadedConfig(raw=raw, prototype_root=root, config_path=config_path, config_hash=digest)


# ----------------------------------------------------------------------
# Prompt rendering
# ----------------------------------------------------------------------

def _read_prompt(root: str, name_with_v: str) -> str:
    path = os.path.join(root, "prompts", f"{name_with_v}.txt")
    with open(path) as f:
        return f.read()


def render_source_prompt(template: str, world: dict[str, Any], proposition_ids: list[str]) -> str:
    return template.format(
        event_type=world["event_type"],
        location_id=world["location_id"],
        time=world["time"],
        proposition_list=render_proposition_list(world, proposition_ids),
    )


def render_relay_prompt(template: str, prior_message: str) -> str:
    return template.format(prior_message=prior_message)


def render_synthesis_prompt(template: str, input_a: str, input_b: str, input_c: str) -> str:
    return template.format(input_a=input_a, input_b=input_b, input_c=input_c)


def render_summary_prompt(template: str, original_message: str, target_length: int) -> str:
    return template.format(original_message=original_message, target_length=target_length)


def render_synthesis_baseline_prompt(template: str, input_a: str, input_b: str, input_c: str, target_length: int) -> str:
    return template.format(input_a=input_a, input_b=input_b, input_c=input_c, target_length=target_length)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def cycle_variant(pool: list[str], index: int) -> str:
    return pool[index % len(pool)]


# ----------------------------------------------------------------------
# Single-run executors
# ----------------------------------------------------------------------

def _make_call_record(
    *,
    role: str,
    provider: str,
    model_name: str,
    temperature: float,
    top_p: float,
    seed: int | None,
    full_prompt: str,
    result,
    prompt_variant: str | None,
) -> dict[str, Any]:
    return {
        "role": role,
        "prompt_variant": prompt_variant,
        "full_prompt": full_prompt,
        "raw_output": result.raw_output,
        "model_metadata": {
            "provider": provider,
            "model_name": model_name,
            "temperature": temperature,
            "top_p": top_p,
            "seed_supported": result.seed_supported,
            "seed": result.seed,
            "reproducibility_policy": result.reproducibility_policy,
        },
        "usage": {
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "cached_tokens": result.cached_tokens,
            "usd_cost": result.usd_cost,
            "pricing_table_version": result.pricing_table_version,
        },
        "logprobs": {
            "available": result.logprobs_available,
            "reason": result.logprobs_reason,
            "top_logprobs": result.top_logprobs,
        },
        "latency_seconds": result.latency_seconds,
        "api_error": result.api_error,
        "extra": result.extra,
    }


def _generate_source(
    *,
    world: dict[str, Any],
    proposition_ids: list[str],
    cfg: dict[str, Any],
    pricing: PricingTable,
    root: str,
) -> tuple[str, dict[str, Any]]:
    prompt_name = cfg["component_versions"]["source_prompt"]
    template = _read_prompt(root, prompt_name)
    prompt = render_source_prompt(template, world, proposition_ids)
    src_cfg = cfg["models"]["source_generator"]
    result = call_model(
        provider=src_cfg["provider"],
        model_name=src_cfg["model_name"],
        prompt=prompt,
        temperature=src_cfg["temperature"],
        top_p=src_cfg["top_p"],
        max_output_tokens=src_cfg["max_output_tokens"],
        seed=None,
        pricing=pricing,
    )
    call = _make_call_record(
        role="source_generator",
        provider=src_cfg["provider"],
        model_name=src_cfg["model_name"],
        temperature=src_cfg["temperature"],
        top_p=src_cfg["top_p"],
        seed=None,
        full_prompt=prompt,
        result=result,
        prompt_variant=prompt_name,
    )
    return result.raw_output, call


def _run_chain(world, cfg, pricing, root, condition, run_order_index, rng) -> dict[str, Any]:
    """Execute a chain_3hop run for one world."""
    run_id = new_id("R")
    created_at = utcnow_iso()
    errors: list[dict] = []
    calls: list[dict] = []
    messages: list[dict] = []
    invalid = False

    relay_pool = condition["relay_prompt_pool"]
    selection = condition.get("relay_variant_selection", "cycle")

    # 1. Source message
    src_text, src_call = _generate_source(
        world=world,
        proposition_ids=world["chain_original_propositions"],
        cfg=cfg,
        pricing=pricing,
        root=root,
    )
    calls.append(src_call)
    if not src_text.strip() or src_call["api_error"]:
        invalid = True
        errors.append({"stage": "source_generation", "error": src_call["api_error"] or "empty_source_output"})

    src_msg_id = new_id("M")
    messages.append({
        "message_id": src_msg_id,
        "role": "source",
        "is_source_message": True,
        "parent_message_ids": [],
        "hop_index": 0,
        "text": src_text,
        "in_scope_propositions": world["chain_original_propositions"],
        "prompt_variant": cfg["component_versions"]["source_prompt"],
    })

    # 2. Relay hops
    mut_cfg = cfg["models"]["mutator"]
    prior_text = src_text
    prior_id = src_msg_id
    hops = condition["hops"]
    for hop_index in range(1, hops + 1):
        if selection == "cycle":
            variant = cycle_variant(relay_pool, hop_index - 1)
        elif selection == "random":
            variant = rng.choice(relay_pool)
        else:
            variant = relay_pool[0]
        template = _read_prompt(root, variant)
        prompt = render_relay_prompt(template, prior_text)
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
        calls.append(_make_call_record(
            role=f"relay_hop_{hop_index}",
            provider=mut_cfg["provider"],
            model_name=mut_cfg["model_name"],
            temperature=mut_cfg["temperature"],
            top_p=mut_cfg["top_p"],
            seed=None,
            full_prompt=prompt,
            result=result,
            prompt_variant=variant,
        ))
        if not result.raw_output.strip() or result.api_error:
            invalid = True
            errors.append({"stage": f"relay_hop_{hop_index}", "error": result.api_error or "empty_output"})

        msg_id = new_id("M")
        messages.append({
            "message_id": msg_id,
            "role": "relay",
            "is_source_message": False,
            "parent_message_ids": [prior_id],
            "hop_index": hop_index,
            "text": result.raw_output,
            "in_scope_propositions": world["chain_original_propositions"],
            "prompt_variant": variant,
        })
        prior_text = result.raw_output
        prior_id = msg_id

    return {
        "run_id": run_id,
        "experiment_id": cfg["experiment_id"],
        "config_hash": "filled_by_caller",
        "component_versions": cfg["component_versions"],
        "created_at": created_at,
        "run_order_index": run_order_index,
        "run_stage": "stage1_structural",
        "world_id": world["world_id"],
        "condition": condition["name"],
        "condition_type": condition["type"],
        "messages": messages,
        "calls": calls,
        "feature_extractions": [],
        "errors": errors,
        "invalid": invalid,
    }


def _run_hub(world, cfg, pricing, root, condition, run_order_index, rng) -> dict[str, Any]:
    run_id = new_id("R")
    created_at = utcnow_iso()
    errors: list[dict] = []
    calls: list[dict] = []
    messages: list[dict] = []
    invalid = False

    # 1. Three source inputs from the same world
    input_message_ids: list[str] = []
    input_texts: list[str] = []
    for label, key in (("hub_input_a", "hub_input_a_propositions"),
                       ("hub_input_b", "hub_input_b_propositions"),
                       ("hub_input_c", "hub_input_c_propositions")):
        text, call = _generate_source(
            world=world,
            proposition_ids=world[key],
            cfg=cfg,
            pricing=pricing,
            root=root,
        )
        call["role"] = f"source_generator_{label}"
        calls.append(call)
        if not text.strip() or call["api_error"]:
            invalid = True
            errors.append({"stage": f"source_generation_{label}", "error": call["api_error"] or "empty_output"})

        mid = new_id("M")
        messages.append({
            "message_id": mid,
            "role": label,
            "is_source_message": True,
            "parent_message_ids": [],
            "hop_index": 0,
            "text": text,
            "in_scope_propositions": world[key],
            "prompt_variant": cfg["component_versions"]["source_prompt"],
        })
        input_message_ids.append(mid)
        input_texts.append(text)

    # 2. Synthesis call
    syn_pool = condition["synthesis_prompt_pool"]
    selection = condition.get("synthesis_variant_selection", "cycle")
    if selection == "cycle":
        variant = cycle_variant(syn_pool, run_order_index)
    elif selection == "random":
        variant = rng.choice(syn_pool)
    else:
        variant = syn_pool[0]
    template = _read_prompt(root, variant)
    prompt = render_synthesis_prompt(template, input_texts[0], input_texts[1], input_texts[2])
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
    calls.append(_make_call_record(
        role="synthesizer",
        provider=mut_cfg["provider"],
        model_name=mut_cfg["model_name"],
        temperature=mut_cfg["temperature"],
        top_p=mut_cfg["top_p"],
        seed=None,
        full_prompt=prompt,
        result=result,
        prompt_variant=variant,
    ))
    if not result.raw_output.strip() or result.api_error:
        invalid = True
        errors.append({"stage": "synthesis", "error": result.api_error or "empty_output"})

    # The terminal message's in-scope propositions are the union of the three inputs.
    union = sorted(set(world["hub_input_a_propositions"]) | set(world["hub_input_b_propositions"]) | set(world["hub_input_c_propositions"]))

    terminal_id = new_id("M")
    messages.append({
        "message_id": terminal_id,
        "role": "synthesizer",
        "is_source_message": False,
        "parent_message_ids": input_message_ids,
        "hop_index": 1,
        "text": result.raw_output,
        "in_scope_propositions": union,
        "prompt_variant": variant,
    })

    return {
        "run_id": run_id,
        "experiment_id": cfg["experiment_id"],
        "config_hash": "filled_by_caller",
        "component_versions": cfg["component_versions"],
        "created_at": created_at,
        "run_order_index": run_order_index,
        "run_stage": "stage1_structural",
        "world_id": world["world_id"],
        "condition": condition["name"],
        "condition_type": condition["type"],
        "messages": messages,
        "calls": calls,
        "feature_extractions": [],
        "errors": errors,
        "invalid": invalid,
    }


def _run_one_shot_summary(world, cfg, pricing, root, condition, run_order_index, rng, target_length: int) -> dict[str, Any]:
    run_id = new_id("R")
    created_at = utcnow_iso()
    errors: list[dict] = []
    calls: list[dict] = []
    messages: list[dict] = []
    invalid = False

    # 1. Source generation (the chain original)
    src_text, src_call = _generate_source(
        world=world,
        proposition_ids=world["chain_original_propositions"],
        cfg=cfg,
        pricing=pricing,
        root=root,
    )
    calls.append(src_call)
    if not src_text.strip() or src_call["api_error"]:
        invalid = True
        errors.append({"stage": "source_generation", "error": src_call["api_error"] or "empty_output"})

    src_msg_id = new_id("M")
    messages.append({
        "message_id": src_msg_id,
        "role": "source",
        "is_source_message": True,
        "parent_message_ids": [],
        "hop_index": 0,
        "text": src_text,
        "in_scope_propositions": world["chain_original_propositions"],
        "prompt_variant": cfg["component_versions"]["source_prompt"],
    })

    # 2. One-shot summary
    prompt_name = condition["summary_prompt"]
    template = _read_prompt(root, prompt_name)
    prompt = render_summary_prompt(template, src_text, target_length)
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
    calls.append(_make_call_record(
        role="one_shot_summarizer",
        provider=mut_cfg["provider"],
        model_name=mut_cfg["model_name"],
        temperature=mut_cfg["temperature"],
        top_p=mut_cfg["top_p"],
        seed=None,
        full_prompt=prompt,
        result=result,
        prompt_variant=prompt_name,
    ))
    if not result.raw_output.strip() or result.api_error:
        invalid = True
        errors.append({"stage": "one_shot_summary", "error": result.api_error or "empty_output"})

    terminal_id = new_id("M")
    messages.append({
        "message_id": terminal_id,
        "role": "one_shot_summarizer",
        "is_source_message": False,
        "parent_message_ids": [src_msg_id],
        "hop_index": 1,
        "text": result.raw_output,
        "in_scope_propositions": world["chain_original_propositions"],
        "prompt_variant": prompt_name,
    })

    return {
        "run_id": run_id,
        "experiment_id": cfg["experiment_id"],
        "config_hash": "filled_by_caller",
        "component_versions": cfg["component_versions"],
        "created_at": created_at,
        "run_order_index": run_order_index,
        "run_stage": "stage2_baseline",
        "world_id": world["world_id"],
        "condition": condition["name"],
        "condition_type": condition["type"],
        "messages": messages,
        "calls": calls,
        "feature_extractions": [],
        "errors": errors,
        "invalid": invalid,
    }


def _run_one_shot_synthesis(world, cfg, pricing, root, condition, run_order_index, rng, target_length: int) -> dict[str, Any]:
    run_id = new_id("R")
    created_at = utcnow_iso()
    errors: list[dict] = []
    calls: list[dict] = []
    messages: list[dict] = []
    invalid = False

    input_message_ids: list[str] = []
    input_texts: list[str] = []
    for label, key in (("hub_input_a", "hub_input_a_propositions"),
                       ("hub_input_b", "hub_input_b_propositions"),
                       ("hub_input_c", "hub_input_c_propositions")):
        text, call = _generate_source(
            world=world,
            proposition_ids=world[key],
            cfg=cfg,
            pricing=pricing,
            root=root,
        )
        call["role"] = f"source_generator_{label}"
        calls.append(call)
        if not text.strip() or call["api_error"]:
            invalid = True
            errors.append({"stage": f"source_generation_{label}", "error": call["api_error"] or "empty_output"})

        mid = new_id("M")
        messages.append({
            "message_id": mid,
            "role": label,
            "is_source_message": True,
            "parent_message_ids": [],
            "hop_index": 0,
            "text": text,
            "in_scope_propositions": world[key],
            "prompt_variant": cfg["component_versions"]["source_prompt"],
        })
        input_message_ids.append(mid)
        input_texts.append(text)

    prompt_name = condition["synthesis_baseline_prompt"]
    template = _read_prompt(root, prompt_name)
    prompt = render_synthesis_baseline_prompt(template, input_texts[0], input_texts[1], input_texts[2], target_length)
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
    calls.append(_make_call_record(
        role="one_shot_synthesizer",
        provider=mut_cfg["provider"],
        model_name=mut_cfg["model_name"],
        temperature=mut_cfg["temperature"],
        top_p=mut_cfg["top_p"],
        seed=None,
        full_prompt=prompt,
        result=result,
        prompt_variant=prompt_name,
    ))
    if not result.raw_output.strip() or result.api_error:
        invalid = True
        errors.append({"stage": "one_shot_synthesis", "error": result.api_error or "empty_output"})

    union = sorted(set(world["hub_input_a_propositions"]) | set(world["hub_input_b_propositions"]) | set(world["hub_input_c_propositions"]))

    terminal_id = new_id("M")
    messages.append({
        "message_id": terminal_id,
        "role": "one_shot_synthesizer",
        "is_source_message": False,
        "parent_message_ids": input_message_ids,
        "hop_index": 1,
        "text": result.raw_output,
        "in_scope_propositions": union,
        "prompt_variant": prompt_name,
    })

    return {
        "run_id": run_id,
        "experiment_id": cfg["experiment_id"],
        "config_hash": "filled_by_caller",
        "component_versions": cfg["component_versions"],
        "created_at": created_at,
        "run_order_index": run_order_index,
        "run_stage": "stage2_baseline",
        "world_id": world["world_id"],
        "condition": condition["name"],
        "condition_type": condition["type"],
        "messages": messages,
        "calls": calls,
        "feature_extractions": [],
        "errors": errors,
        "invalid": invalid,
    }


# ----------------------------------------------------------------------
# Feature extraction
# ----------------------------------------------------------------------

def _attach_features(run: dict[str, Any], world: dict[str, Any], extractor: ResidueExtractor) -> None:
    msgs = run["messages"]
    msgs_by_id = {m["message_id"]: m for m in msgs}
    # The chain original / first source message in a hub is the "original"
    # for drift purposes. For chain, this is the role=source message. For hub
    # synthesis runs, the "original" reference is ambiguous; we use the first input.
    source_msg = next((m for m in msgs if m.get("role") in ("source", "hub_input_a")), None)
    original_text = source_msg["text"] if source_msg else None

    aux_per_message = {}
    for m in msgs:
        parent_ids = m.get("parent_message_ids", [])
        parent_text = msgs_by_id[parent_ids[0]]["text"] if parent_ids else None
        rows, aux = extractor.extract(
            run_id=run["run_id"],
            message_id=m["message_id"],
            message_text=m["text"],
            world=world,
            parent_text=parent_text,
            original_text=original_text,
            in_scope_proposition_ids=m.get("in_scope_propositions"),
        )
        run["feature_extractions"].extend(feature_rows_to_dicts(rows))
        if aux:
            aux_per_message[m["message_id"]] = aux
    run["aux"] = aux_per_message


# ----------------------------------------------------------------------
# Preflight checks
# ----------------------------------------------------------------------

def _preflight_ollama(model_name: str, endpoint: str | None = None) -> None:
    base = (endpoint or os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")).replace("/api/chat", "")
    try:
        r = httpx.get(f"{base}/api/tags", timeout=3.0)
        r.raise_for_status()
        j = r.json()
        names = {m.get("name") for m in j.get("models", [])}
        if model_name not in names:
            raise PreflightError(
                f"ollama_local: model '{model_name}' not found at {base}. "
                f"Available models: {sorted(n for n in names if n)}. "
                f"Run `ollama pull {model_name}` or change the config."
            )
    except httpx.HTTPError as e:
        raise PreflightError(
            f"ollama_local: endpoint {base} unreachable ({type(e).__name__}: {e}). "
            f"Start Ollama with `ollama serve` or set OLLAMA_URL."
        ) from e


def _preflight_anthropic() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise PreflightError("anthropic: ANTHROPIC_API_KEY not set in environment")


def _preflight_openai() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise PreflightError("openai: OPENAI_API_KEY not set in environment")


def preflight_check(cfg: dict[str, Any]) -> None:
    """Verify configured providers are reachable. Raise PreflightError on failure."""
    seen: set[tuple[str, str]] = set()
    for role in ("mutator", "source_generator"):
        m = cfg["models"].get(role)
        if not m:
            continue
        key = (m["provider"], m["model_name"])
        if key in seen:
            continue
        seen.add(key)
        if m["provider"] == "ollama_local":
            _preflight_ollama(m["model_name"])
        elif m["provider"] == "anthropic":
            _preflight_anthropic()
        elif m["provider"] == "openai":
            _preflight_openai()


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------

def run_experiment(
    config_path: str,
    *,
    n_per_condition: int | None = None,
    worlds_subset: list[str] | None = None,
    verbose: bool = True,
    fresh: bool = False,
    allow_invalid_model_calls: bool = False,
) -> dict[str, Any]:
    loaded = load_config(config_path)
    cfg = loaded.raw
    root = loaded.prototype_root

    # Preflight: verify providers are reachable before we touch the trace file.
    if not allow_invalid_model_calls:
        preflight_check(cfg)

    worlds_path = os.path.join(root, cfg["worlds_file"])
    schema_path = os.path.join(root, "schemas", "world_schema_v0_1.json")
    worlds = load_worlds(worlds_path, schema_path=schema_path)
    if worlds_subset:
        worlds = [w for w in worlds if w["world_id"] in worlds_subset]
    elif cfg.get("worlds_to_use") not in (None, "all"):
        keep = set(cfg["worlds_to_use"])
        worlds = [w for w in worlds if w["world_id"] in keep]
    if not worlds:
        raise RuntimeError("no worlds selected to run")

    n_reps = n_per_condition if n_per_condition is not None else cfg.get("n_replications_per_condition", 1)

    pricing_path = os.path.join(root, "configs", "pricing_table_v0_1.json")
    pricing = PricingTable(pricing_path)

    seed = int(cfg["run_ordering"]["random_seed"])
    rng = random.Random(seed)

    # Build the interleaved task list.
    tasks: list[tuple[dict[str, Any], dict[str, Any], int]] = []
    for w in worlds:
        for cond in cfg["conditions"]:
            if not cond.get("enabled", True):
                continue
            for rep in range(n_reps):
                tasks.append((w, cond, rep))
    rng.shuffle(tasks)
    if verbose:
        print(f"[run] {len(tasks)} runs queued across {len(worlds)} worlds and {len(cfg['conditions'])} conditions")
        print("[run] two-stage plan:")
        print("[run]   stage1_structural: chain + hub conditions, interleaved across worlds")
        print("[run]   stage2_baseline:   one-shot summary + one-shot synthesis, length-matched to stage1 medians")

    # Set up extractor (loaded once).
    emb_cfg = cfg["models"]["embedding"]
    embedder = EmbeddingClient(model_name=emb_cfg["model_name"], batch_size=emb_cfg.get("batch_size", 32))
    dict_versions = cfg["component_versions"]["dictionaries"]
    extractor = ResidueExtractor(
        embedder=embedder,
        hedges=Dictionary(os.path.join(root, "dictionaries", f"{dict_versions['hedges']}.json")),
        uncertainty=Dictionary(os.path.join(root, "dictionaries", f"{dict_versions['uncertainty_markers']}.json")),
        evidentials=Dictionary(os.path.join(root, "dictionaries", f"{dict_versions['evidential_markers']}.json")),
        source_markers=Dictionary(os.path.join(root, "dictionaries", f"{dict_versions['source_markers']}.json")),
    )

    trace_path = os.path.join(root, cfg["outputs"]["trace_path"])
    if fresh and os.path.exists(trace_path):
        os.remove(trace_path)
        if verbose:
            print(f"[run] fresh=True: removed prior trace at {trace_path}")
    writer = TraceWriter(trace_path)

    # Track per-condition median terminal lengths for length-matched baselines.
    # First pass: chain + hub runs. Second pass: baselines using computed targets.
    pending_baseline_tasks: list[tuple] = []
    chain_terminal_lengths: list[int] = []
    hub_terminal_lengths: list[int] = []

    summary = {
        "total_runs": 0,
        "valid_runs": 0,
        "invalid_runs": 0,
        "total_usd_cost": 0.0,
        "by_condition": {},
    }

    # First pass: structural conditions
    for run_index, (world, cond, rep) in enumerate(tasks):
        if cond["type"] in ("one_shot_summary", "one_shot_synthesis"):
            pending_baseline_tasks.append((run_index, world, cond, rep))
            continue
        run = _dispatch_run(world, cond, cfg, pricing, root, run_index, rng)
        run["config_hash"] = loaded.config_hash
        _attach_features(run, world, extractor)
        writer.write_run(run)
        _accumulate(summary, run)
        # Track terminal length for baseline matching.
        terminals = [m for m in run["messages"] if m.get("hop_index", 0) > 0 or m.get("role") == "synthesizer"]
        if terminals:
            term_text = terminals[-1]["text"]
            if cond["type"] == "chain":
                chain_terminal_lengths.append(len(term_text.split()))
            elif cond["type"] == "hub":
                hub_terminal_lengths.append(len(term_text.split()))
        if verbose:
            print(f"[run {run_index+1}/{len(tasks)}] {cond['name']} world={world['world_id']} invalid={run['invalid']}")

    # Compute baseline length targets.
    import statistics
    chain_target = int(statistics.median(chain_terminal_lengths)) if chain_terminal_lengths else 80
    hub_target = int(statistics.median(hub_terminal_lengths)) if hub_terminal_lengths else 110

    # Second pass: baselines
    for run_index, world, cond, rep in pending_baseline_tasks:
        if cond["type"] == "one_shot_summary":
            run = _run_one_shot_summary(world, cfg, pricing, root, cond, run_index, rng, target_length=chain_target)
        else:
            run = _run_one_shot_synthesis(world, cfg, pricing, root, cond, run_index, rng, target_length=hub_target)
        run["config_hash"] = loaded.config_hash
        _attach_features(run, world, extractor)
        writer.write_run(run)
        _accumulate(summary, run)
        if verbose:
            print(f"[run {run_index+1}/{len(tasks)}] {cond['name']} world={world['world_id']} invalid={run['invalid']} (baseline target={chain_target if cond['type']=='one_shot_summary' else hub_target})")

    if verbose:
        print(f"[done] {summary['valid_runs']}/{summary['total_runs']} valid, total cost ${summary['total_usd_cost']:.4f}")
        for c, d in summary["by_condition"].items():
            print(f"  {c}: {d['valid']}/{d['total']} valid, ${d['cost']:.4f}")

    return summary


def _dispatch_run(world, cond, cfg, pricing, root, run_index, rng):
    if cond["type"] == "chain":
        return _run_chain(world, cfg, pricing, root, cond, run_index, rng)
    if cond["type"] == "hub":
        return _run_hub(world, cfg, pricing, root, cond, run_index, rng)
    raise ValueError(f"unknown condition type: {cond['type']}")


def _accumulate(summary, run):
    summary["total_runs"] += 1
    if run["invalid"]:
        summary["invalid_runs"] += 1
    else:
        summary["valid_runs"] += 1
    cost = sum((c.get("usage", {}).get("usd_cost") or 0.0) for c in run["calls"])
    summary["total_usd_cost"] += cost
    bc = summary["by_condition"].setdefault(run["condition"], {"total": 0, "valid": 0, "cost": 0.0})
    bc["total"] += 1
    if not run["invalid"]:
        bc["valid"] += 1
    bc["cost"] += cost
