#!/usr/bin/env python3
"""Build the markdown audit export from a trace.

Usage:
    cd prototype
    python -m scripts.build_audit --trace outputs/chain_hub_proto_v0_1.trace.jsonl --mode both --n 6
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
sys.path.insert(0, ROOT)

from src.audit_export import build_audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", required=True)
    ap.add_argument("--audit", default=None)
    ap.add_argument("--mode", choices=["blinded", "unblinded", "both"], default="both")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--worlds", default=os.path.join(ROOT, "worlds", "worlds_v0_1.jsonl"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    trace_path = args.trace
    if not os.path.isabs(trace_path):
        trace_path = os.path.join(ROOT, trace_path)
    base = os.path.splitext(os.path.basename(trace_path))[0].replace(".trace", "")
    audit_path = args.audit or os.path.join(ROOT, "outputs", f"{base}.audit.md")
    result = build_audit(
        trace_path,
        audit_path,
        mode=args.mode,
        sample_size=args.n,
        worlds_path=args.worlds,
        seed=args.seed,
    )
    print(result)


if __name__ == "__main__":
    main()
