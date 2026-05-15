"""Build the markdown audit export from a JSONL trace.

Two modes:
    unblinded   shows condition and ordering
    blinded     randomizes display order and assigns opaque audit IDs
                with the mapping stored in a separate JSON file.
"""
from __future__ import annotations

import json
import os
import random
import secrets
from typing import Any


def _audit_id() -> str:
    return secrets.token_hex(3).upper()  # short readable ID like "A1F0B7"


def select_lineages(trace: list[dict[str, Any]], n: int, seed: int = 0) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rng.shuffle(trace)
    return trace[: min(n, len(trace))]


def render_lineage(run: dict[str, Any], blinded: bool, world_lookup: dict[str, dict[str, Any]] | None) -> str:
    out = []
    aid = _audit_id()
    out.append(f"## Audit item {aid}")
    out.append("")
    if not blinded:
        out.append(f"- run_id: `{run['run_id']}`")
        out.append(f"- condition: `{run['condition']}`")
        out.append(f"- run_stage: `{run.get('run_stage', '?')}`")
        out.append(f"- world_id: `{run['world_id']}`")
    else:
        out.append("- (condition and stage hidden in blinded mode)")
    out.append("")

    if world_lookup and not blinded:
        w = world_lookup.get(run["world_id"])
        if w:
            out.append("### World state")
            out.append("```json")
            out.append(json.dumps({k: v for k, v in w.items() if k != "propositions"}, indent=2))
            out.append("```")
            out.append("")
            out.append("Propositions:")
            for p in w["propositions"]:
                out.append(f"- ({p['proposition_id']}, T={str(p['truth_value']).lower()}, u={p['uncertainty']}, ev={p['evidence_type']}, c={p['centrality']}) {p['natural_language_claim']}")
            out.append("")

    out.append("### Message lineage")
    out.append("")
    for m in run["messages"]:
        src_tag = "source" if m.get("is_source_message") else "transformed"
        head = f"**[{m['role']} | {src_tag}] hop={m.get('hop_index')}**"
        if not blinded:
            head += f" (id=`{m['message_id']}`, parent={m.get('parent_message_ids', [])}, prompt=`{m.get('prompt_variant')}`)"
        out.append(head)
        out.append("")
        out.append("> " + m["text"].replace("\n", "\n> "))
        out.append("")

    if not blinded:
        out.append("### Automated feature summary")
        out.append("")
        # Group features by message
        feats_by_msg: dict[str, dict[str, Any]] = {}
        for fx in run.get("feature_extractions", []):
            feats_by_msg.setdefault(fx["message_id"], {})[fx["feature_name"]] = fx["feature_value"]
        for m in run["messages"]:
            f = feats_by_msg.get(m["message_id"], {})
            if not f:
                continue
            out.append(f"**[{m['role']}] hop={m.get('hop_index')}** (`{m['message_id']}`)")
            for k in sorted(f.keys()):
                out.append(f"- {k}: {f[k]}")
            out.append("")

        if run.get("aux"):
            out.append("### Per-proposition matches")
            for mid, aux in run["aux"].items():
                mr = aux.get("match_result", {})
                for pid, match in (mr.get("matches") or {}).items():
                    out.append(f"- `{mid}` -> `{pid}`: {match['classification']} (sim={match['best_similarity']}){' ['+match['notes']+']' if match.get('notes') else ''}")
            out.append("")

    if run.get("errors"):
        out.append("### Errors")
        for e in run["errors"]:
            out.append(f"- {e}")
        out.append("")

    out.append("### Human notes")
    out.append("")
    out.append("(blank)")
    out.append("")
    out.append("---")
    out.append("")
    return aid, "\n".join(out)


def build_audit(trace_path: str, audit_path: str, *, mode: str, sample_size: int, worlds_path: str | None = None, seed: int = 0) -> dict[str, str]:
    trace = []
    with open(trace_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            trace.append(json.loads(line))

    world_lookup = None
    if worlds_path and os.path.exists(worlds_path):
        world_lookup = {}
        with open(worlds_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                w = json.loads(line)
                world_lookup[w["world_id"]] = w

    selected = select_lineages(trace, sample_size, seed=seed)
    blinded = mode in ("blinded", "both")
    unblinded = mode in ("unblinded", "both")

    parts = []
    mapping = {}
    if unblinded:
        parts.append(f"# Audit export (unblinded mode)\n\nSample size: {len(selected)}\n")
        for run in selected:
            aid, rendered = render_lineage(run, blinded=False, world_lookup=world_lookup)
            mapping[aid] = {"run_id": run["run_id"], "condition": run["condition"], "world_id": run["world_id"], "mode": "unblinded"}
            parts.append(rendered)

    if blinded:
        # Re-shuffle and re-render in blinded mode with separate IDs.
        rng = random.Random(seed + 1)
        b_runs = list(selected)
        rng.shuffle(b_runs)
        parts.append(f"\n\n# Audit export (blinded mode)\n\nSample size: {len(b_runs)}\n")
        for run in b_runs:
            aid, rendered = render_lineage(run, blinded=True, world_lookup=world_lookup)
            mapping[aid] = {"run_id": run["run_id"], "condition": run["condition"], "world_id": run["world_id"], "mode": "blinded"}
            parts.append(rendered)

    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    with open(audit_path, "w") as f:
        f.write("\n".join(parts))

    mapping_path = audit_path.replace(".md", ".mapping.json")
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=2)

    return {"audit_path": audit_path, "mapping_path": mapping_path, "n": len(mapping)}
