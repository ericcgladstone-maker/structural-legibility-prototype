#!/usr/bin/env python3
"""Smoke test: 1 world, 1 rep across all conditions.

Writes to smoke-specific output paths and defaults to fresh (deletes any prior
smoke trace before running). Use --allow-invalid-model-calls to bypass the
preflight check on the configured provider.

Run from prototype/ root:

    cd prototype
    python -m scripts.smoke_test

Default uses ollama_local with llama3.1:8b. Override via env:

    MUTATOR_PROVIDER=anthropic MUTATOR_MODEL=claude-haiku-4-5 \
      SOURCE_PROVIDER=anthropic SOURCE_MODEL=claude-haiku-4-5 \
      python -m scripts.smoke_test
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
sys.path.insert(0, ROOT)

import yaml

from src.run_experiment import PreflightError, run_experiment


SMOKE_PATHS = {
    "trace_path": "outputs/chain_hub_proto_v0_1_smoke.trace.jsonl",
    "features_path": "outputs/chain_hub_proto_v0_1_smoke.features.parquet",
    "duckdb_path": "outputs/chain_hub_proto_v0_1_smoke.duckdb",
    "audit_path": "outputs/chain_hub_proto_v0_1_smoke.audit.md",
    "report_path": "outputs/chain_hub_proto_v0_1_smoke_report.md",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="W001", help="Single world_id for the smoke test")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--allow-invalid-model-calls", action="store_true",
                    help="Skip the provider preflight check (logs API failures into the trace instead)")
    ap.add_argument("--no-fresh", action="store_true",
                    help="Append to the smoke trace instead of starting fresh (default: fresh)")
    args = ap.parse_args()

    base_config = os.path.join(ROOT, "configs", "chain_hub_proto_v0_1.yaml")
    with open(base_config) as f:
        cfg = yaml.safe_load(f)

    # Provider overrides from env.
    if os.environ.get("MUTATOR_PROVIDER"):
        cfg["models"]["mutator"]["provider"] = os.environ["MUTATOR_PROVIDER"]
    if os.environ.get("MUTATOR_MODEL"):
        cfg["models"]["mutator"]["model_name"] = os.environ["MUTATOR_MODEL"]
    if os.environ.get("SOURCE_PROVIDER"):
        cfg["models"]["source_generator"]["provider"] = os.environ["SOURCE_PROVIDER"]
    if os.environ.get("SOURCE_MODEL"):
        cfg["models"]["source_generator"]["model_name"] = os.environ["SOURCE_MODEL"]

    # Smoke output paths.
    cfg["outputs"].update(SMOKE_PATHS)

    smoke_config = os.path.join(ROOT, "configs", "_smoke_override.yaml")
    with open(smoke_config, "w") as f:
        yaml.safe_dump(cfg, f)

    try:
        summary = run_experiment(
            smoke_config,
            n_per_condition=args.reps,
            worlds_subset=[args.world],
            verbose=True,
            fresh=not args.no_fresh,
            allow_invalid_model_calls=args.allow_invalid_model_calls,
        )
    except PreflightError as e:
        print(f"[preflight failure] {e}", file=sys.stderr)
        print("Pass --allow-invalid-model-calls to write trace anyway (recorded API errors).", file=sys.stderr)
        sys.exit(2)

    print("\nSmoke summary:", summary)


if __name__ == "__main__":
    main()
