#!/usr/bin/env python3
"""
Extract residue features from each trial's TERMINAL message (the message the receiver saw).

For each lineage record:
- Identify the terminal message (intercepted_message_id from lineage_metadata).
- Identify the source message (is_source_message=True) for original-text comparisons.
- Identify the terminal's parent message (parent_message_ids[0]).
- Run residue_extractor_v2.extract() against the world.
- Emit a row: trial_id + cell_id + world_id + features_wide + ground_truth_preservation_rate.

This single artifact supports:
- Item 1: comparator feature input (X for LR training).
- Item 2: ground-truth accuracy = proposition_preservation_rate (target for Brier on receiver accuracy posterior).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from src.model_client import EmbeddingClient
from src.residue_extractor import Dictionary
from src.residue_extractor_v2 import ResidueExtractorV2
from src.world_loader import load_worlds


def find_terminal_and_source(run: dict) -> tuple[dict | None, dict | None, dict | None]:
    """Return (terminal_msg, source_msg, parent_of_terminal_msg)."""
    msgs = run.get("messages", [])
    msgs_by_id = {m["message_id"]: m for m in msgs}
    lm = run.get("lineage_metadata", {})
    terminal_id = lm.get("intercepted_message_id")
    terminal = msgs_by_id.get(terminal_id) if terminal_id else None
    # Source: prefer is_source_message=True, then role='source', then first message
    source = next((m for m in msgs if m.get("is_source_message")), None)
    if source is None:
        source = next((m for m in msgs if m.get("role") in ("source", "hub_input_a")), None)
    if source is None and msgs:
        source = msgs[0]
    # Parent of terminal
    parent = None
    if terminal:
        parent_ids = terminal.get("parent_message_ids", [])
        if parent_ids:
            parent = msgs_by_id.get(parent_ids[0])
    return terminal, source, parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment-id", default="machine_tracing_bprime_v0_1")
    ap.add_argument("--worlds-file", default="worlds/worlds_v0_2.jsonl")
    ap.add_argument("--limit", type=int, default=None, help="Process only the first N trials (debug)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lineage_path = ROOT / "outputs" / f"{args.experiment_id}.lineage.jsonl"
    out_path = Path(args.out) if args.out else ROOT / "outputs" / f"{args.experiment_id}.terminal_features.jsonl"

    print(f"Loading lineage records from {lineage_path}")
    runs = []
    with lineage_path.open() as f:
        for line in f:
            if line.strip():
                runs.append(json.loads(line))
    if args.limit:
        runs = runs[: args.limit]
    print(f"Processing {len(runs)} trials")

    worlds = load_worlds(str(ROOT / args.worlds_file))
    world_lookup = {w["world_id"]: w for w in worlds}

    embedder = EmbeddingClient(model_name="all-MiniLM-L6-v2", batch_size=32)
    extractor = ResidueExtractorV2(
        embedder=embedder,
        hedges=Dictionary(str(ROOT / "dictionaries" / "hedges_v0_1.json")),
        uncertainty=Dictionary(str(ROOT / "dictionaries" / "uncertainty_markers_v0_1.json")),
        evidentials=Dictionary(str(ROOT / "dictionaries" / "evidential_markers_v0_1.json")),
        source_markers=Dictionary(str(ROOT / "dictionaries" / "source_markers_v0_1.json")),
    )

    n_done = 0
    n_skipped = 0
    t0 = time.time()
    with out_path.open("w") as out_f:
        for run in runs:
            trial_id = run.get("condition")  # cell_id; we use the unique trial_id from messages
            # The actual trial_id we want comes from elsewhere — the lineage has run_id, condition, world_id
            # Find the trial_id from the messages or from a synthesized form
            # Lineage doesn't directly carry trial_id; we synthesize from condition+world+replicate_index if needed.
            # But the ground_truth and receiver records DO have trial_id, so we'll join later by run_id.
            run_id = run.get("run_id")
            world_id = run.get("world_id")
            cell_id = run.get("condition")
            world = world_lookup.get(world_id)
            if world is None:
                n_skipped += 1
                continue
            terminal, source, parent = find_terminal_and_source(run)
            if terminal is None:
                n_skipped += 1
                continue

            # Use source's in_scope_propositions as the denominator if available
            in_scope = source.get("in_scope_propositions") if source else None
            original_text = source.get("text") if source else None
            parent_text = parent.get("text") if parent else None
            terminal_text = terminal.get("text", "")

            try:
                rows, aux = extractor.extract(
                    run_id=run_id,
                    message_id=terminal.get("message_id", ""),
                    message_text=terminal_text,
                    world=world,
                    parent_text=parent_text,
                    original_text=original_text,
                    in_scope_proposition_ids=in_scope,
                )
            except Exception as e:
                n_skipped += 1
                print(f"[skip] {trial_id} extract error: {e}")
                continue

            # Pivot to wide feature dict
            feat = {}
            for r in rows:
                try:
                    val = float(r.feature_value) if r.feature_value is not None else None
                except (TypeError, ValueError):
                    val = None
                feat[r.feature_name] = val

            record = {
                "run_id": run_id,
                "world_id": world_id,
                "cell_id": cell_id,
                "condition_type": run.get("condition_type"),
                "regime": run.get("regime"),
                "replicate_index": run.get("replicate_index"),
                "terminal_message_id": terminal.get("message_id"),
                "source_message_id": source.get("message_id") if source else None,
                "features": feat,
                # Ground-truth accuracy proxy: preservation_rate (kept / in_scope)
                "true_accuracy_score": feat.get("proposition_preservation_rate"),
            }
            out_f.write(json.dumps(record) + "\n")
            n_done += 1
            if n_done % 100 == 0:
                elapsed = time.time() - t0
                rate = n_done / elapsed if elapsed > 0 else 0
                eta_min = (len(runs) - n_done) / rate / 60 if rate > 0 else 0
                print(f"  {n_done}/{len(runs)} ({rate:.1f}/sec, ETA {eta_min:.1f} min)")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed/60:.1f} min: {n_done} extracted, {n_skipped} skipped")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
