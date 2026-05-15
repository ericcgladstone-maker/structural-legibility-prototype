#!/usr/bin/env python3
"""Run the full chain-hub prototype across all 20 worlds.

Usage:
    cd prototype
    python -m scripts.run_prototype                    # uses config default (1 rep)
    python -m scripts.run_prototype --reps 3           # 3 reps per condition per world
    python -m scripts.run_prototype --fresh            # delete prior trace before running
    python -m scripts.run_prototype --allow-invalid-model-calls   # skip preflight

Provider overrides via env vars (see smoke_test.py).
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
sys.path.insert(0, ROOT)

from src.run_experiment import PreflightError, run_experiment


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=None, help="Replications per condition per world")
    ap.add_argument("--config", default=os.path.join(ROOT, "configs", "chain_hub_proto_v0_1.yaml"))
    ap.add_argument("--fresh", action="store_true", help="Delete prior trace before running")
    ap.add_argument("--allow-invalid-model-calls", action="store_true",
                    help="Skip provider preflight; record API errors in the trace")
    args = ap.parse_args()
    try:
        summary = run_experiment(
            args.config,
            n_per_condition=args.reps,
            verbose=True,
            fresh=args.fresh,
            allow_invalid_model_calls=args.allow_invalid_model_calls,
        )
    except PreflightError as e:
        print(f"[preflight failure] {e}", file=sys.stderr)
        print("Pass --allow-invalid-model-calls to bypass the preflight check.", file=sys.stderr)
        sys.exit(2)
    print("\nSummary:", summary)


if __name__ == "__main__":
    main()
