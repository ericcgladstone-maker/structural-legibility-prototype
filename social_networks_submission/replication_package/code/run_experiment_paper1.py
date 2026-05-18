"""
Paper-1 experiment orchestrator.

Stage 1: lineage generation (regime instantiation).
Stage 2: trace-packet assembly + candidate-set construction + receiver dispatch + ground-truth emission.
Stage 3 (post-hoc / separate script): comparator training + per-cell evaluation.

For each (cell × world × replicate) tuple, produces:
- A lineage record (regime instantiation output).
- A trace packet at the cell's trace level + validity coefficient.
- A constructed candidate set + ground-truth sidecar.
- A receiver-prediction record.

All artifacts written to JSONL traces under reproducibility-for-human-coding discipline:
deterministic given (cell_id, world_id, seed); all stimuli + receiver prompts + outputs
archived as human-readable text/JSON.

Per:
- `comprehensive_review.md` §12 paper-1 design.
- `project_build_spec.md` factorial structure.
- `project_evaluation_framework.md` four-tier evaluation references.
- `project_receiver_task.md` seven-output spec.

Literature anchors carried forward from upstream modules.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .candidate_set import build_candidate_set, load_persona_pool, to_ground_truth_partial
from .model_client import PricingTable
from .receiver_dispatcher import (
    dispatch_receiver,
    load_receiver_prompt_template,
    receiver_output_to_record,
)
from .regime_instantiators import REGIME_DISPATCH, RegimeContext, run_regime, sanity_check_run
from .run_experiment import (
    _preflight_anthropic,
    _preflight_ollama,
    _preflight_openai,
    _run_chain,
    _run_hub,
    load_config,
    preflight_check,
)
from .trace_packet_assembly import LineageData, build_trace_packet
from .world_loader import load_worlds


# Regimes handled in regime_instantiators.py vs the existing run_experiment harness.
EXISTING_HARNESS_REGIMES = {"chain_relay", "centralized_synthesis"}
NEW_HARNESS_REGIMES = set(REGIME_DISPATCH.keys())
ALL_REGIMES = EXISTING_HARNESS_REGIMES | NEW_HARNESS_REGIMES | {"compound"}


@dataclass
class CellSpec:
    """One cell of the experimental factorial."""
    cell_id: str
    regime: str
    trace_level: int  # 1-6
    validity_coefficient: float | None
    candidate_set_size_class: str  # CS-S | CS-M | CS-L
    prior_type: str  # uniform | structured_biased
    receiver_family_label: str
    chain_hops: int | None = None  # only for chain_relay
    compound_regime_sequence: list[str] | None = None  # only for compound
    extra: dict[str, Any] | None = None  # regime-specific config overrides

    @classmethod
    def from_yaml_entry(cls, entry: dict) -> "CellSpec":
        return cls(
            cell_id=entry["cell_id"],
            regime=entry["regime"],
            trace_level=entry["trace_level"],
            validity_coefficient=entry.get("validity_coefficient"),
            candidate_set_size_class=entry["candidate_set_size_class"],
            prior_type=entry.get("prior_type", "uniform"),
            receiver_family_label=entry["receiver_family_label"],
            chain_hops=entry.get("chain_hops"),
            compound_regime_sequence=entry.get("compound_regime_sequence"),
            extra=entry.get("extra"),
        )


# ----------------------------------------------------------------------
# Lineage generation
# ----------------------------------------------------------------------


def _generate_lineage(
    cell: CellSpec,
    world: dict,
    persona_pool: list[dict],
    cfg: dict,
    pricing: PricingTable,
    root: str,
    run_order_index: int,
    rng: random.Random,
) -> dict:
    """Dispatch to the appropriate regime instantiator based on cell.regime."""
    if cell.regime in NEW_HARNESS_REGIMES:
        ctx = RegimeContext(
            world=world,
            persona_pool=persona_pool,
            cfg=cfg,
            pricing=pricing,
            root=root,
            run_order_index=run_order_index,
            rng=rng,
        )
        run = run_regime(cell.regime, ctx)
        # Override the condition field to cell_id for per-cell aggregation in analysis.
        # (regime_instantiators set condition=regime by default; orchestrator knows the cell_id.)
        run["condition"] = cell.cell_id
        run["condition_type"] = cell.regime
    elif cell.regime == "chain_relay":
        # Use existing harness's _run_chain. Wrap to add persona attribution + lineage_metadata.
        condition_stub = {
            "name": cell.cell_id,
            "type": "chain",
            "hops": cell.chain_hops or 3,
            "relay_prompt_pool": cfg.get("relay_prompt_pool", ["relay_a_v0_1", "relay_b_v0_1", "relay_c_v0_1"]),
            "relay_variant_selection": "cycle",
        }
        run = _run_chain(world, cfg, pricing, root, condition_stub, run_order_index, rng)
        run = _augment_existing_run_with_lineage_metadata(run, cell, persona_pool, rng)
    elif cell.regime == "centralized_synthesis":
        condition_stub = {
            "name": cell.cell_id,
            "type": "hub",
            "n_inputs": 3,
            "synthesis_prompt_pool": cfg.get("synthesis_prompt_pool", ["synthesis_a_v0_1", "synthesis_b_v0_1", "synthesis_c_v0_1"]),
            "synthesis_variant_selection": "cycle",
        }
        run = _run_hub(world, cfg, pricing, root, condition_stub, run_order_index, rng)
        run = _augment_existing_run_with_lineage_metadata(run, cell, persona_pool, rng)
    elif cell.regime == "compound":
        run = _generate_compound_lineage(cell, world, persona_pool, cfg, pricing, root, run_order_index, rng)
    else:
        raise ValueError(f"Unknown regime: {cell.regime}")

    issues = sanity_check_run(run) if "lineage_metadata" in run else []
    if issues:
        run.setdefault("errors", []).extend([{"stage": "sanity_check", "error": i} for i in issues])
    return run


def _augment_existing_run_with_lineage_metadata(
    run: dict,
    cell: CellSpec,
    persona_pool: list[dict],
    rng: random.Random,
) -> dict:
    """
    Add lineage_metadata to a run produced by the existing harness's _run_chain / _run_hub.

    Assigns personas pseudo-randomly per producing role and constructs the hops list.
    """
    messages = run["messages"]
    source_msg = next((m for m in messages if m.get("is_source_message")), None)
    if source_msg is None:
        return run

    # Pick personas: one for the source, one per non-source producer/relayer
    n_producers = sum(1 for m in messages if m.get("role") in ("source", "hub_input_a", "hub_input_b", "hub_input_c", "relay"))
    personas = rng.sample(persona_pool, n_producers)
    persona_iter = iter(personas)

    hops: list[dict] = []
    terminal_id: str | None = None
    true_source_persona: dict | None = None

    for m in messages:
        if m.get("role") in ("source", "hub_input_a", "hub_input_b", "hub_input_c", "relay"):
            persona = next(persona_iter)
            m["persona_id"] = persona["persona_id"]
            if m["role"] == "source":
                true_source_persona = persona
            hops.append({
                "step": m.get("hop_index", 0),
                "agent_identifier": persona["persona_id"],
                "transformation_type": "relay" if m["role"] == "relay" else "source",
                "timestamp": _utcnow_iso(),
            })
        # The terminal is the message with the highest hop_index or the synthesizer's output
        if m.get("role") in ("relay", "synthesizer", "one_shot_summarizer", "one_shot_synthesizer"):
            terminal_id = m["message_id"]

    if true_source_persona is None and personas:
        true_source_persona = personas[0]

    if true_source_persona is None:
        # Fallback if we can't determine source persona
        true_source_persona = rng.choice(persona_pool)

    run["regime"] = cell.regime
    run["lineage_metadata"] = {
        "intercepted_message_id": terminal_id or messages[-1]["message_id"],
        "true_source_persona_id": true_source_persona["persona_id"],
        "true_source_persona": true_source_persona,
        "true_regime": cell.regime,
        "true_independence_label": None,  # not applicable for chain or centralized_synthesis
        "hops": hops,
    }
    return run


def _generate_compound_lineage(
    cell: CellSpec,
    world: dict,
    persona_pool: list[dict],
    cfg: dict,
    pricing: PricingTable,
    root: str,
    run_order_index: int,
    rng: random.Random,
) -> dict:
    """
    Compose a compound regime (e.g., laundering → chain). v0.1 implementation: run the
    first regime; use its terminal as the source for the second regime; concatenate
    messages + calls; set ground-truth source to the FIRST regime's true source.
    """
    seq = cell.compound_regime_sequence or ["common_source_laundering", "chain_relay"]
    if len(seq) != 2:
        raise NotImplementedError("v0.1 compound regime composer supports exactly 2-regime sequences.")

    # Stage 1: first regime
    first_cell = CellSpec(
        cell_id=cell.cell_id + "_part1",
        regime=seq[0],
        trace_level=cell.trace_level,
        validity_coefficient=cell.validity_coefficient,
        candidate_set_size_class=cell.candidate_set_size_class,
        prior_type=cell.prior_type,
        receiver_family_label=cell.receiver_family_label,
        chain_hops=cell.chain_hops,
    )
    first_run = _generate_lineage(first_cell, world, persona_pool, cfg, pricing, root, run_order_index, rng)
    first_terminal_id = first_run["lineage_metadata"]["intercepted_message_id"]
    first_terminal_msg = next(m for m in first_run["messages"] if m["message_id"] == first_terminal_id)
    first_terminal_text = first_terminal_msg["text"]
    first_true_source = first_run["lineage_metadata"]["true_source_persona"]

    # Stage 2: second regime, fed the first regime's terminal as input
    # For v0.1 we re-use the regime function but inject the input — simplest implementation:
    # re-run with the persona_pool minus already-used personas and use a synthetic world-like
    # wrapper. For now, just append the second regime as another step and aggregate metadata.
    # A more sophisticated implementation would parameterize the regime function to take an
    # arbitrary input rather than always generating from the world. v0.2 extension.
    # v0.1 fallback: only chain_relay or dependent_repetition as the second stage make sense
    # without major refactoring.
    second_cell = CellSpec(
        cell_id=cell.cell_id + "_part2",
        regime=seq[1],
        trace_level=cell.trace_level,
        validity_coefficient=cell.validity_coefficient,
        candidate_set_size_class=cell.candidate_set_size_class,
        prior_type=cell.prior_type,
        receiver_family_label=cell.receiver_family_label,
        chain_hops=cell.chain_hops,
    )
    second_run = _generate_lineage(second_cell, world, persona_pool, cfg, pricing, root, run_order_index, rng)

    # Combine
    combined = {
        "run_id": first_run["run_id"] + "_" + second_run["run_id"],
        "experiment_id": first_run["experiment_id"],
        "config_hash": first_run["config_hash"],
        "component_versions": first_run["component_versions"],
        "created_at": first_run["created_at"],
        "run_order_index": run_order_index,
        "run_stage": "stage1_structural",
        "world_id": world["world_id"],
        "condition": cell.cell_id,
        "condition_type": "compound",
        "regime": "compound",
        "messages": first_run["messages"] + second_run["messages"],
        "calls": first_run["calls"] + second_run["calls"],
        "feature_extractions": [],
        "errors": first_run["errors"] + second_run["errors"],
        "invalid": bool(first_run["errors"] or second_run["errors"]),
        "lineage_metadata": {
            "intercepted_message_id": second_run["lineage_metadata"]["intercepted_message_id"],
            "true_source_persona_id": first_true_source["persona_id"],
            "true_source_persona": first_true_source,
            "true_regime": "compound",
            "compound_regime_sequence": seq,
            "true_independence_label": None,
            "hops": first_run["lineage_metadata"]["hops"] + second_run["lineage_metadata"]["hops"],
        },
    }
    return combined


# ----------------------------------------------------------------------
# Receiver pipeline (Stage 2)
# ----------------------------------------------------------------------


def _build_lineage_data_for_trace_packet(run: dict) -> LineageData:
    """Extract a LineageData object from a run for trace-packet assembly."""
    lm = run["lineage_metadata"]
    intercepted_id = lm["intercepted_message_id"]
    intercepted_msg = next(m for m in run["messages"] if m["message_id"] == intercepted_id)
    return LineageData(
        lineage_id=run["run_id"],
        regime=run["regime"],
        intercepted_message=intercepted_msg["text"],
        hops=lm["hops"],
        interception_method="open-source operational monitoring",
        interception_channel="standard reporting channel",
        interception_timestamp=_utcnow_iso(),
        proximate_sender_persona=lm["true_source_persona"] if lm["hops"] and len(lm["hops"]) == 1 else None,
    )


def _run_receiver_pipeline(
    *,
    run: dict,
    cell: CellSpec,
    persona_pool: list[dict],
    persona_pool_dict: dict,
    receiver_prompt_template: str,
    receiver_model_config: dict,
    pricing: PricingTable,
    seed: int,
) -> dict:
    """
    Stage 2: from a lineage run, build trace packet + candidate set, dispatch receiver,
    emit ground truth. Returns a dict with all stage-2 artifacts.
    """
    lineage = _build_lineage_data_for_trace_packet(run)
    trace_packet_id = f"{cell.cell_id}__{run['world_id']}__seed{seed}"
    trace_packet = build_trace_packet(
        lineage=lineage,
        trace_packet_id=trace_packet_id,
        trace_level=cell.trace_level,
        validity_coefficient=cell.validity_coefficient,
        seed=seed,
        persona_pool=persona_pool_dict,
    )

    candidate_set = build_candidate_set(
        persona_pool,
        cell_id=cell.cell_id,
        world_id=run["world_id"],
        seed=seed,
        size_class=cell.candidate_set_size_class,
        true_source_persona_id=run["lineage_metadata"]["true_source_persona_id"],
        prior_type=cell.prior_type,
    )

    receiver_result = dispatch_receiver(
        trace_packet=trace_packet,
        candidate_set=candidate_set,
        receiver_prompt_template=receiver_prompt_template,
        receiver_model_config=receiver_model_config,
        pricing=pricing,
    )

    receiver_record = receiver_output_to_record(
        receiver_result,
        trace_packet_id=trace_packet_id,
        candidate_set_id=candidate_set.candidate_set_id,
        receiver_family=cell.receiver_family_label,
    )

    # Build ground-truth sidecar
    lm = run["lineage_metadata"]
    ground_truth = {
        "ground_truth_id": f"gt__{trace_packet_id}",
        "trace_packet_id": trace_packet_id,
        "lineage_id": run["run_id"],
        "cell_id": cell.cell_id,
        "world_id": run["world_id"],
        "replicate_index": 0,
        "true_regime": lm["true_regime"],
        "compound_regime_sequence": lm.get("compound_regime_sequence"),
        "hop_count": cell.chain_hops if cell.regime == "chain_relay" else None,
        "true_source_persona_id": lm["true_source_persona_id"],
        "true_source_in_candidate_set": candidate_set.true_source_in_set,
        "true_accuracy_score": None,  # to be filled by residue_extractor in post-hoc analysis
        "true_independence_label": lm["true_independence_label"],
        "trace_validity_coefficient": cell.validity_coefficient,
        "candidate_set_size_class": cell.candidate_set_size_class,
        "candidate_set_seed": seed,
        "candidate_set_size_actual": len(candidate_set.candidates),
        "resolution_criteria_version": "resolution_criteria_v0_1",
    }

    return {
        "trace_packet": trace_packet,
        "candidate_set": candidate_set.to_dict(),
        "receiver_result": receiver_record,
        "ground_truth": ground_truth,
    }


# ----------------------------------------------------------------------
# Public orchestrator
# ----------------------------------------------------------------------


def run_paper1_experiment(
    config_path: str,
    *,
    worlds_subset: list[str] | None = None,
    cell_subset: list[str] | None = None,
    fresh: bool = False,
    verbose: bool = True,
    allow_invalid_model_calls: bool = False,
) -> dict:
    """
    End-to-end paper-1 experiment.

    For each (cell × world × replicate) tuple:
      1. Generate lineage (regime instantiation).
      2. Build trace packet + candidate set.
      3. Dispatch receiver.
      4. Emit ground-truth sidecar.

    Writes four parallel JSONL streams:
      - <experiment_id>.lineage.jsonl (one record per run)
      - <experiment_id>.trace_packets.jsonl
      - <experiment_id>.receiver.jsonl
      - <experiment_id>.ground_truth.jsonl
    """
    loaded = load_config(config_path)
    cfg = loaded.raw
    root = loaded.prototype_root

    if not allow_invalid_model_calls:
        # Existing harness preflight checks mutator + source_generator
        preflight_check(cfg)
        # Paper-1 additionally requires the receiver model
        receiver = cfg["models"].get("receiver")
        if receiver:
            if receiver["provider"] == "ollama_local":
                _preflight_ollama(receiver["model_name"])
            elif receiver["provider"] == "anthropic":
                _preflight_anthropic()
            elif receiver["provider"] == "openai":
                _preflight_openai()

    # Load worlds
    worlds_path = os.path.join(root, cfg["worlds_file"])
    schema_path = os.path.join(root, "schemas", "world_schema_v0_1.json")
    worlds = load_worlds(worlds_path, schema_path=schema_path)
    if worlds_subset:
        worlds = [w for w in worlds if w["world_id"] in worlds_subset]
    elif cfg.get("worlds_to_use") not in (None, "all"):
        keep = set(cfg["worlds_to_use"])
        worlds = [w for w in worlds if w["world_id"] in keep]

    # Load persona pool
    persona_pool_path = os.path.join(root, cfg.get("persona_pool_file", "dictionaries/persona_pool_v0_1.json"))
    persona_pool = load_persona_pool(persona_pool_path)
    persona_pool_dict = {p["persona_id"]: p for p in persona_pool}

    # Load receiver prompt
    receiver_prompt_path = os.path.join(root, "prompts", f"{cfg['component_versions']['receiver_prompt']}.txt")
    receiver_prompt_template = load_receiver_prompt_template(receiver_prompt_path)

    # Load cells
    all_cells = [CellSpec.from_yaml_entry(c) for c in cfg["cells"]]
    if cell_subset:
        all_cells = [c for c in all_cells if c.cell_id in cell_subset]

    # Setup pricing + rng
    pricing_path = os.path.join(root, "configs", "pricing_table_v0_1.json")
    pricing = PricingTable(pricing_path)
    base_seed = int(cfg["run_ordering"]["random_seed"])
    rng = random.Random(base_seed)

    # Build task list: cell × world × replicate
    n_reps = cfg.get("n_replications_per_condition", 1)
    tasks: list[tuple[CellSpec, dict, int]] = []
    for cell in all_cells:
        for w in worlds:
            for rep in range(n_reps):
                tasks.append((cell, w, rep))
    rng.shuffle(tasks)

    # Open output streams (append mode by default for resume support)
    lineage_path = os.path.join(root, cfg["outputs"]["lineage_path"])
    trace_packets_path = os.path.join(root, cfg["outputs"]["trace_packets_path"])
    receiver_path = os.path.join(root, cfg["outputs"]["receiver_predictions_path"])
    gt_path = os.path.join(root, cfg["outputs"]["ground_truth_path"])

    # Resume support: scan existing lineage records for completed trial_ids.
    # Lineage is written LAST per trial, so its presence => the trial fully completed.
    completed_trial_ids: set[str] = set()
    if not fresh and os.path.exists(lineage_path):
        with open(lineage_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    tid = rec.get("trial_id")
                    if tid:
                        completed_trial_ids.add(tid)
                except json.JSONDecodeError:
                    pass
        if verbose and completed_trial_ids:
            print(f"[resume] Found {len(completed_trial_ids)} completed trial_ids in {lineage_path}; will skip them.")

    out_lineage = open(lineage_path, "w" if fresh else "a")
    out_trace_packets = open(trace_packets_path, "w" if fresh else "a")
    out_receiver = open(receiver_path, "w" if fresh else "a")
    out_gt = open(gt_path, "w" if fresh else "a")

    summary = {
        "total_tasks": len(tasks),
        "skipped_resume": 0,
        "completed": 0,
        "receiver_invalid": 0,
        "lineage_invalid": 0,
    }

    try:
        for task_index, (cell, world, rep) in enumerate(tasks):
            # Deterministic per-trial identifier (resume marker)
            trial_id = f"{cell.cell_id}__{world['world_id']}__rep{rep}"
            if trial_id in completed_trial_ids:
                summary["skipped_resume"] += 1
                continue

            if verbose:
                print(f"[{task_index+1}/{len(tasks)}] cell={cell.cell_id} world={world['world_id']} rep={rep}")
            task_seed = base_seed + task_index

            # Stage 1: lineage (compute; don't write yet — lineage is last)
            task_rng = random.Random(task_seed)
            run = _generate_lineage(
                cell, world, persona_pool, cfg, pricing, root, task_index, task_rng,
            )
            run["config_hash"] = loaded.config_hash
            run["trial_id"] = trial_id
            run["replicate_index"] = rep

            if run.get("invalid"):
                # Write lineage to mark as done (so we don't retry on resume)
                out_lineage.write(json.dumps(run, ensure_ascii=False) + "\n")
                out_lineage.flush()
                summary["lineage_invalid"] += 1
                if verbose:
                    print(f"  lineage INVALID (errors: {run.get('errors')})")
                continue

            # Stage 2: receiver pipeline
            stage2 = _run_receiver_pipeline(
                run=run,
                cell=cell,
                persona_pool=persona_pool,
                persona_pool_dict=persona_pool_dict,
                receiver_prompt_template=receiver_prompt_template,
                receiver_model_config=cfg["models"]["receiver"],
                pricing=pricing,
                seed=task_seed,
            )
            # Attach trial_id to stage2 artifacts for cross-reference
            stage2["trace_packet"]["trial_id"] = trial_id
            stage2["receiver_result"]["trial_id"] = trial_id
            stage2["ground_truth"]["trial_id"] = trial_id

            # Write trace_packet, receiver, ground_truth FIRST; lineage LAST.
            # Lineage-presence implies all 4 streams written for this trial → safe resume marker.
            out_trace_packets.write(json.dumps(stage2["trace_packet"], ensure_ascii=False) + "\n")
            out_trace_packets.flush()
            out_receiver.write(json.dumps(stage2["receiver_result"], ensure_ascii=False) + "\n")
            out_receiver.flush()
            out_gt.write(json.dumps(stage2["ground_truth"], ensure_ascii=False) + "\n")
            out_gt.flush()
            out_lineage.write(json.dumps(run, ensure_ascii=False) + "\n")
            out_lineage.flush()

            if stage2["receiver_result"]["invalid"]:
                summary["receiver_invalid"] += 1
                if verbose:
                    print(f"  receiver INVALID (errors: {stage2['receiver_result']['validation_errors']})")
            summary["completed"] += 1
    finally:
        out_lineage.close()
        out_trace_packets.close()
        out_receiver.close()
        out_gt.close()

    if verbose:
        print(
            f"\n[done] {summary['completed']} newly completed; "
            f"{summary['skipped_resume']} skipped (resume); "
            f"{summary['lineage_invalid']} lineage_invalid; "
            f"{summary['receiver_invalid']} receiver_invalid; "
            f"{summary['total_tasks']} total tasks"
        )

    return summary


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the paper-1 experiment given a YAML config (e.g., configs/paper1_pilot_v0_1.yaml)."
    )
    parser.add_argument("config_path", help="Path to the experiment YAML config.")
    parser.add_argument(
        "--worlds",
        nargs="*",
        default=None,
        help="Subset of world_ids to run (e.g., W001 W002). Defaults to config's worlds_to_use.",
    )
    parser.add_argument(
        "--cells",
        nargs="*",
        default=None,
        help="Subset of cell_ids to run. Defaults to all cells in config.",
    )
    parser.add_argument("--fresh", action="store_true", help="Overwrite output files instead of appending.")
    parser.add_argument(
        "--allow-invalid-model-calls",
        action="store_true",
        help="Skip provider preflight checks (for testing without Ollama running).",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress per-trial verbose output.")
    args = parser.parse_args()

    summary = run_paper1_experiment(
        args.config_path,
        worlds_subset=args.worlds,
        cell_subset=args.cells,
        fresh=args.fresh,
        verbose=not args.quiet,
        allow_invalid_model_calls=args.allow_invalid_model_calls,
    )

    print(f"\nSummary: {json.dumps(summary, indent=2)}")


if __name__ == "__main__":
    _cli()
