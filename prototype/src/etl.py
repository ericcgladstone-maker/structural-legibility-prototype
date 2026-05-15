"""ETL: JSONL trace -> Parquet feature tables -> DuckDB.

Produces five logical tables exposed as views in the DuckDB database:
    runs              one row per run
    messages          one row per message
    calls             one row per LLM call
    features          one row per (message_id, feature_name) (long format)
    aux_matches       one row per (message_id, proposition_id) matching detail
"""
from __future__ import annotations

import json
import os
from typing import Any

import duckdb
import pandas as pd


def load_trace(path: str) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            runs.append(json.loads(line))
    return runs


def flatten(trace: list[dict[str, Any]]) -> dict[str, pd.DataFrame]:
    run_rows = []
    msg_rows = []
    call_rows = []
    feat_rows = []
    aux_rows = []

    for run in trace:
        run_rows.append({
            "run_id": run["run_id"],
            "experiment_id": run["experiment_id"],
            "config_hash": run.get("config_hash"),
            "created_at": run["created_at"],
            "run_order_index": run["run_order_index"],
            "run_stage": run.get("run_stage"),
            "world_id": run["world_id"],
            "condition": run["condition"],
            "condition_type": run.get("condition_type"),
            "invalid": run.get("invalid", False),
            "n_errors": len(run.get("errors", [])),
        })
        for m in run["messages"]:
            msg_rows.append({
                "run_id": run["run_id"],
                "message_id": m["message_id"],
                "role": m["role"],
                "is_source_message": m.get("is_source_message"),
                "hop_index": m.get("hop_index"),
                "parent_message_ids": ",".join(m.get("parent_message_ids", [])),
                "text": m["text"],
                "in_scope_propositions": ",".join(m.get("in_scope_propositions", [])),
                "prompt_variant": m.get("prompt_variant"),
            })
        for c in run["calls"]:
            mm = c.get("model_metadata", {})
            u = c.get("usage", {})
            lp = c.get("logprobs", {})
            call_rows.append({
                "run_id": run["run_id"],
                "role": c.get("role"),
                "prompt_variant": c.get("prompt_variant"),
                "provider": mm.get("provider"),
                "model_name": mm.get("model_name"),
                "temperature": mm.get("temperature"),
                "top_p": mm.get("top_p"),
                "seed": mm.get("seed"),
                "input_tokens": u.get("input_tokens"),
                "output_tokens": u.get("output_tokens"),
                "usd_cost": u.get("usd_cost"),
                "pricing_table_version": u.get("pricing_table_version"),
                "logprobs_available": lp.get("available"),
                "latency_seconds": c.get("latency_seconds"),
                "api_error_type": (c.get("api_error") or {}).get("type") if c.get("api_error") else None,
                "api_error_message": (c.get("api_error") or {}).get("message") if c.get("api_error") else None,
            })
        for fx in run.get("feature_extractions", []):
            feat_rows.append({
                "run_id": fx["run_id"],
                "message_id": fx["message_id"],
                "feature_name": fx["feature_name"],
                "feature_value": fx["feature_value"],
                "extractor_name": fx["extractor_name"],
                "extractor_version": fx["extractor_version"],
                "extracted_at": fx["extracted_at"],
                "null_reason": fx.get("null_reason"),
            })
        for mid, aux in (run.get("aux") or {}).items():
            mr = aux.get("match_result", {})
            for pid, match in (mr.get("matches") or {}).items():
                aux_rows.append({
                    "run_id": run["run_id"],
                    "message_id": mid,
                    "proposition_id": pid,
                    "best_similarity": match.get("best_similarity"),
                    "matched_sentence_index": match.get("matched_sentence_index"),
                    "classification": match.get("classification"),
                    "notes": match.get("notes"),
                })

    return {
        "runs": pd.DataFrame(run_rows),
        "messages": pd.DataFrame(msg_rows),
        "calls": pd.DataFrame(call_rows),
        "features": pd.DataFrame(feat_rows),
        "aux_matches": pd.DataFrame(aux_rows),
    }


def _build_features_wide(features_df: pd.DataFrame) -> pd.DataFrame:
    if features_df.empty:
        return features_df
    # Coerce values to numeric where possible (long-format strings -> floats).
    f = features_df.copy()
    f["feature_value_num"] = pd.to_numeric(f["feature_value"], errors="coerce")
    wide = f.pivot_table(
        index=["run_id", "message_id"],
        columns="feature_name",
        values="feature_value_num",
        aggfunc="first",
    ).reset_index()
    wide.columns.name = None
    return wide


def write_parquet(tables: dict[str, pd.DataFrame], out_dir: str) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    if "features" in tables and not tables["features"].empty:
        tables["features_wide"] = _build_features_wide(tables["features"])
    paths = {}
    for name, df in tables.items():
        path = os.path.join(out_dir, f"{name}.parquet")
        df.to_parquet(path, index=False)
        paths[name] = path
    return paths


def build_duckdb(parquet_paths: dict[str, str], duckdb_path: str) -> None:
    if os.path.exists(duckdb_path):
        os.remove(duckdb_path)
    con = duckdb.connect(duckdb_path)
    for name, path in parquet_paths.items():
        abs_path = os.path.abspath(path).replace("'", "''")
        con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_parquet('{abs_path}')")
    con.close()


def run_etl(trace_path: str, parquet_dir: str, duckdb_path: str) -> dict[str, str]:
    trace = load_trace(trace_path)
    tables = flatten(trace)
    paths = write_parquet(tables, parquet_dir)
    build_duckdb(paths, duckdb_path)
    return paths
