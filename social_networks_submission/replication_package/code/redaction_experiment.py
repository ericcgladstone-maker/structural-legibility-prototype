#!/usr/bin/env python3
"""
Redaction experiment for the form-vs-meaning mechanism test.

For trials from regimes that produce explicit production-process self-disclosures
("Here is my rewritten report", "Here's an echo of the source message",
"Source A's findings...", etc.), identify the cue, redact the sentence
containing it, and re-run the LLM receiver. Compare top-1 regime classification
before vs after redaction.

Logic:
- If the LLM is using the explicit cue, regime classification should shift
  (likely toward `single_direct` once the disclosure is removed).
- If the LLM is form-blind (the strong claim), redaction should not change
  classification — the LLM was relying on stylometric form, not the
  literal disclosure.

Scope: F1 (qwen2.5:7b receiver) trials where:
- True regime is dependent_repetition (R3), common_source_laundering (R4),
  clustered_reinforcement (R5), or centralized_synthesis (R6).
- Terminal message contains a detectable explicit-cue phrase.

Compute: ~160 trials × ~45 sec = ~2 hours sequential. Run in background.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import yaml

from src.candidate_set import build_candidate_set, load_persona_pool
from src.receiver_dispatcher import dispatch_receiver, load_receiver_prompt_template


# Cue patterns per regime — phrases that explicitly disclose the production process.
CUE_PATTERNS = {
    "dependent_repetition": re.compile(
        r"\b(here is my (rewrite|rewritten)|here.{0,3}s my rewrit"
        r"|i (have |.ve )?(maintained|kept|preserved) (the )?(same )?(essential|key) (information|claims|content)"
        r"|present(ed|ing) (it )?in my own words|in my own (words|framing)"
        r"|rewrit(ing|ten) (the )?report|i.{0,3}ll rewrite|i will rewrite"
        r"|maintain(ed|ing) the original|rephras(ed|ing) the source)\b",
        re.IGNORECASE,
    ),
    "clustered_reinforcement": re.compile(
        r"\b(here.{0,3}s an echo|an echo of"
        r"|within[- ]community|in[- ]group (phrasing|abbreviation|jargon)"
        r"|community jargon|shared jargon|specialist (jargon|terminology)"
        r"|note that i.{0,3}(ve )?used|using (within[- ]community|in[- ]group|community))\b",
        re.IGNORECASE,
    ),
    "centralized_synthesis": re.compile(
        r"\b(source [A-D]|both sources|all (three )?sources|multiple sources"
        r"|from the inputs|across (the )?(input|source)s|sources agree|sources differ)\b",
        re.IGNORECASE,
    ),
    "common_source_laundering": re.compile(
        r"(key findings:\s*\n\s*[*\-\d]|investigation (revealed|found):\s*\n\s*[*\-\d]"
        r"|the following (key )?(findings|points|takeaways))",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def detect_cue(text: str, regime: str) -> re.Match | None:
    pat = CUE_PATTERNS.get(regime)
    if pat is None:
        return None
    return pat.search(text)


def redact_cue(text: str, regime: str) -> tuple[str, list[str]]:
    """
    Redact sentences containing the regime's cue pattern.

    Strategy: split into paragraphs first, then within each paragraph by sentence-ending
    punctuation followed by whitespace. For each unit (sentence or paragraph chunk),
    drop it if it contains the cue. Reassemble.

    Returns (redacted_text, list_of_removed_chunks).
    """
    pat = CUE_PATTERNS.get(regime)
    if pat is None:
        return text, []

    # First: paragraph split
    paragraphs = text.split("\n\n")
    kept_paragraphs: list[str] = []
    removed: list[str] = []

    for para in paragraphs:
        # Within each paragraph: sentence-level split
        # Simple split on period+space or period+newline; preserves question marks too
        units = re.split(r"(?<=[.!?])\s+", para)
        kept_units: list[str] = []
        for unit in units:
            if pat.search(unit):
                removed.append(unit.strip())
            else:
                kept_units.append(unit)
        if kept_units:
            kept_paragraphs.append(" ".join(kept_units))

    # If after redaction the entire message is empty, fall back to deleting just the matched substring
    redacted = "\n\n".join(kept_paragraphs).strip()
    if not redacted:
        # Aggressive fallback: replace the matched phrase with empty string
        m = pat.search(text)
        if m:
            redacted = (text[: m.start()] + text[m.end():]).strip()
            removed = [m.group(0)]

    return redacted, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment-id", default="machine_tracing_bprime_v0_1")
    ap.add_argument("--config-path", default="configs/machine_tracing_bprime_v0_1.yaml")
    ap.add_argument("--limit", type=int, default=None, help="Cap number of trials processed")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cfg_path = ROOT / args.config_path
    with cfg_path.open() as f:
        cfg = yaml.safe_load(f)
    receiver_model_config = cfg["models"]["receiver"]
    persona_pool_path = ROOT / cfg["persona_pool_file"]
    persona_pool = load_persona_pool(persona_pool_path)
    receiver_prompt_template = load_receiver_prompt_template(ROOT / "prompts" / "receiver_v0_1.txt")

    # Load streams
    outdir = ROOT / "outputs"
    def jsonl(p):
        with p.open() as f:
            return [json.loads(l) for l in f if l.strip()]
    packets_by_tid = {p["trial_id"]: p for p in jsonl(outdir / f"{args.experiment_id}.trace_packets.jsonl") if p.get("trial_id")}
    receiver_by_tid = {r["trial_id"]: r for r in jsonl(outdir / f"{args.experiment_id}.receiver.jsonl") if r.get("trial_id")}
    gt_by_tid = {g["trial_id"]: g for g in jsonl(outdir / f"{args.experiment_id}.ground_truth.jsonl") if g.get("trial_id")}

    # Build cell_id → cell_spec lookup from config
    cell_specs = {c["cell_id"]: c for c in cfg["cells"]}

    # Identify candidate trials
    targets = []
    for tid, gt in gt_by_tid.items():
        regime = gt.get("true_regime")
        if regime not in CUE_PATTERNS:
            continue
        if tid not in packets_by_tid or tid not in receiver_by_tid:
            continue
        msg = packets_by_tid[tid].get("intercepted_message", "") or ""
        m = detect_cue(msg, regime)
        if m is None:
            continue
        targets.append(tid)

    print(f"Identified {len(targets)} candidate trials with detectable cues (across 4 regimes).")
    if args.limit:
        targets = targets[: args.limit]
        print(f"Processing first {len(targets)} (limit applied).")

    out_path = Path(args.out) if args.out else outdir / f"{args.experiment_id}.redaction_results.jsonl"
    # Resume support: skip trial_ids already done
    done_tids = set()
    if out_path.exists():
        with out_path.open() as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    if rec.get("trial_id"):
                        done_tids.add(rec["trial_id"])
        print(f"Resume: {len(done_tids)} trials already done in existing output file.")

    targets_to_run = [t for t in targets if t not in done_tids]
    print(f"To process: {len(targets_to_run)}")
    if not targets_to_run:
        print("Nothing to do.")
        return

    t0 = time.time()
    with out_path.open("a") as out_f:
        for i, tid in enumerate(targets_to_run, 1):
            gt = gt_by_tid[tid]
            original_packet = packets_by_tid[tid]
            original_receiver = receiver_by_tid[tid]
            cell_id = gt["cell_id"]
            cell_spec = cell_specs.get(cell_id)
            if cell_spec is None:
                print(f"[skip] no cell spec for {cell_id}")
                continue
            true_regime = gt["true_regime"]
            original_msg = original_packet["intercepted_message"]
            redacted_msg, removed_chunks = redact_cue(original_msg, true_regime)
            if redacted_msg == original_msg:
                # Cue was supposedly present but redaction made no change — skip
                continue

            # Build the redacted trace packet (clone, swap message)
            redacted_packet = dict(original_packet)
            redacted_packet["intercepted_message"] = redacted_msg

            # Rebuild candidate set deterministically from ground truth
            seed = gt["candidate_set_seed"]
            try:
                candidate_set = build_candidate_set(
                    persona_pool,
                    cell_id=cell_id,
                    world_id=gt["world_id"],
                    seed=seed,
                    size_class=cell_spec["candidate_set_size_class"],
                    true_source_persona_id=gt["true_source_persona_id"],
                    prior_type=cell_spec.get("prior_type", "uniform"),
                )
            except Exception as e:
                print(f"[skip] {tid}: candidate-set rebuild failed: {e}")
                continue

            # Dispatch receiver on redacted packet
            try:
                result = dispatch_receiver(
                    trace_packet=redacted_packet,
                    candidate_set=candidate_set,
                    receiver_prompt_template=receiver_prompt_template,
                    receiver_model_config=receiver_model_config,
                )
            except Exception as e:
                print(f"[error] {tid}: dispatch failed: {e}")
                continue

            # Compare top-1 regime
            def top1(pred):
                p = (pred or {}).get("regime", {}).get("posterior", {})
                if not p:
                    return None
                return max(p.items(), key=lambda x: x[1])[0]
            original_top1 = top1(original_receiver.get("parsed"))
            redacted_top1 = top1(result.parsed)
            original_acc = ((original_receiver.get("parsed") or {}).get("accuracy") or {}).get("probability")
            redacted_acc = ((result.parsed or {}).get("accuracy") or {}).get("probability")

            record = {
                "trial_id": tid,
                "true_regime": true_regime,
                "trace_level": original_packet.get("trace_level"),
                "original_top1_regime": original_top1,
                "redacted_top1_regime": redacted_top1,
                "regime_changed": (original_top1 != redacted_top1) if (original_top1 and redacted_top1) else None,
                "original_correct": (original_top1 == true_regime),
                "redacted_correct": (redacted_top1 == true_regime),
                "original_accuracy_prob": original_acc,
                "redacted_accuracy_prob": redacted_acc,
                "removed_chunks": removed_chunks,
                "original_message_chars": len(original_msg),
                "redacted_message_chars": len(redacted_msg),
                "redacted_invalid": result.invalid,
                "redacted_validation_errors": result.validation_errors,
                "redacted_parsed": result.parsed,
            }
            out_f.write(json.dumps(record) + "\n")
            out_f.flush()

            if i % 5 == 0 or i == 1:
                elapsed = time.time() - t0
                rate = i / elapsed if elapsed else 0
                eta = (len(targets_to_run) - i) / rate / 60 if rate else 0
                print(f"  {i}/{len(targets_to_run)} done (rate {rate:.2f}/sec, ETA {eta:.1f} min). Last: {tid} → orig={original_top1}, red={redacted_top1}")

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed/60:.1f} min")
    print(f"Output: {out_path}")


if __name__ == "__main__":
    main()
