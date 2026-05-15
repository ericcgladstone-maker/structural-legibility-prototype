#!/usr/bin/env python3
"""Run ETL: JSONL trace -> Parquet -> DuckDB.

Usage:
    cd prototype
    python -m scripts.build_etl --trace outputs/chain_hub_proto_v0_1.trace.jsonl
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
sys.path.insert(0, ROOT)

from src.etl import run_etl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", required=True, help="Path to trace JSONL")
    ap.add_argument("--parquet_dir", default=None, help="Directory to write Parquet files (default: outputs/parquet_<expt>)")
    ap.add_argument("--duckdb", default=None, help="Path to write DuckDB file (default: outputs/<expt>.duckdb)")
    args = ap.parse_args()

    trace_path = args.trace
    if not os.path.isabs(trace_path):
        trace_path = os.path.join(ROOT, trace_path)
    base = os.path.splitext(os.path.basename(trace_path))[0].replace(".trace", "")
    parquet_dir = args.parquet_dir or os.path.join(ROOT, "outputs", f"parquet_{base}")
    duckdb_path = args.duckdb or os.path.join(ROOT, "outputs", f"{base}.duckdb")

    paths = run_etl(trace_path, parquet_dir, duckdb_path)
    print("Parquet written:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
    print(f"DuckDB: {duckdb_path}")


if __name__ == "__main__":
    main()
