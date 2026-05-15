"""Append-only JSONL trace writer with assertion guards.

Each run is a single JSON line. The harness must call assert_run_valid() before
write_run() so missing data crashes early in pilot mode.
"""
from __future__ import annotations

import json
import os
from typing import Any


class TraceAssertionError(AssertionError):
    pass


def assert_run_valid(run: dict[str, Any]) -> None:
    required = [
        "run_id", "experiment_id", "config_hash", "component_versions",
        "created_at", "run_order_index", "world_id", "condition",
        "run_stage", "messages", "calls", "feature_extractions", "errors", "invalid",
    ]
    for k in required:
        if k not in run:
            raise TraceAssertionError(f"trace missing required key: {k}")

    if not isinstance(run["messages"], list):
        raise TraceAssertionError("trace 'messages' must be a list")
    for m in run["messages"]:
        if not m.get("message_id"):
            raise TraceAssertionError("message missing message_id")
        if "is_source_message" not in m:
            raise TraceAssertionError(f"message {m['message_id']} missing is_source_message flag")
        is_source = bool(m["is_source_message"])
        parents = m.get("parent_message_ids") or []
        if is_source and parents:
            raise TraceAssertionError(f"source message {m['message_id']} has parent_message_ids; source messages must be parentless")
        if (not is_source) and (not parents):
            raise TraceAssertionError(f"non-source message {m['message_id']} missing parent_message_ids")
        if not isinstance(m.get("text"), str):
            raise TraceAssertionError(f"message {m['message_id']} missing text or text is not a string")
        # Allow empty text only if invalid=true and a structured error explains why.
        if m["text"].strip() == "" and not run.get("invalid"):
            raise TraceAssertionError(f"message {m['message_id']} has empty text on valid run")

    for c in run.get("calls", []):
        if "model_metadata" not in c:
            raise TraceAssertionError("call missing model_metadata")
        if "raw_output" not in c:
            raise TraceAssertionError("call missing raw_output")


class TraceWriter:
    def __init__(self, path: str):
        self.path = path
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        # Open in append mode; create empty file if missing.
        if not os.path.exists(path):
            with open(path, "w"):
                pass

    def write_run(self, run: dict[str, Any]) -> None:
        assert_run_valid(run)
        with open(self.path, "a") as f:
            f.write(json.dumps(run, default=str) + "\n")
