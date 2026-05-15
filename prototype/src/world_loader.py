"""Load and validate worlds from JSONL."""
from __future__ import annotations

import json
import os
from typing import Any

import jsonschema


def load_worlds(path: str, schema_path: str | None = None) -> list[dict[str, Any]]:
    worlds: list[dict[str, Any]] = []
    with open(path) as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                w = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"World JSONL parse error at line {i}: {e}")
            worlds.append(w)

    if schema_path and os.path.exists(schema_path):
        with open(schema_path) as f:
            schema = json.load(f)
        for w in worlds:
            jsonschema.validate(instance=w, schema=schema)

    # Cross-field assertions.
    seen_ids = set()
    for w in worlds:
        wid = w["world_id"]
        if wid in seen_ids:
            raise ValueError(f"Duplicate world_id: {wid}")
        seen_ids.add(wid)
        prop_ids = {p["proposition_id"] for p in w["propositions"]}
        for key in ("chain_original_propositions", "hub_input_a_propositions", "hub_input_b_propositions", "hub_input_c_propositions"):
            for pid in w[key]:
                if pid not in prop_ids:
                    raise ValueError(f"{wid}: {key} references undefined proposition {pid}")
        for pair in w["conflict_propositions"]:
            for pid in pair:
                if pid not in prop_ids:
                    raise ValueError(f"{wid}: conflict pair references undefined proposition {pid}")
    return worlds


def proposition_text(world: dict[str, Any], proposition_id: str) -> str:
    for p in world["propositions"]:
        if p["proposition_id"] == proposition_id:
            return p["natural_language_claim"]
    raise KeyError(f"{world['world_id']}: proposition {proposition_id} not found")


def render_proposition_list(world: dict[str, Any], proposition_ids: list[str]) -> str:
    lines = []
    for pid in proposition_ids:
        for p in world["propositions"]:
            if p["proposition_id"] == pid:
                lines.append(f"- ({p['proposition_id']}) {p['natural_language_claim']}")
                break
    return "\n".join(lines)
