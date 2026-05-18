#!/usr/bin/env python3
"""
Side-by-side correct/incorrect cross-tabs for the LLM receiver vs the
structure-blind comparator. Computed on the same 840 test trials used in
the comparator evaluation.

Breakouts:
  1. By true regime (structure).
  2. By trace level.
  3. By chain hop count (R7 only).
  4. Confusion matrices (LLM and Comparator) side by side.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

REGIME_KEYS = [
    "single_direct",
    "chain_relay",
    "independent_corroboration",
    "dependent_repetition",
    "common_source_laundering",
    "clustered_reinforcement",
    "centralized_synthesis",
    "compound",
]

TEST_WORLDS = {"W017", "W018", "W019", "W020"}


def load_jsonl(path: Path):
    with path.open() as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    out = ROOT / "outputs"
    eid = "machine_tracing_bprime_v0_1"
    receiver = {r["trial_id"]: r for r in load_jsonl(out / f"{eid}.receiver.jsonl") if r.get("trial_id")}
    gt = {g["trial_id"]: g for g in load_jsonl(out / f"{eid}.ground_truth.jsonl") if g.get("trial_id")}
    comp = {c["trial_id"]: c for c in load_jsonl(out / f"{eid}.comparator_predictions.jsonl") if c.get("trial_id")}

    # Restrict to test worlds (the slice on which the comparator was evaluated)
    test_tids = [tid for tid, g in gt.items() if g.get("world_id") in TEST_WORLDS]
    test_tids = [tid for tid in test_tids if tid in receiver and tid in comp]
    print(f"Test trials: {len(test_tids)}\n")

    def top1(posterior):
        if not posterior:
            return None
        return max(posterior.items(), key=lambda x: x[1])[0]

    def parse_axes(tid):
        parts = tid.split("__")
        trace = next((p for p in parts if p.startswith("L")), "?")
        val = next((p for p in parts if p.startswith("v") and p[1:].isdigit()), "?")
        return trace, val

    # ------------------------------------------------------------------
    # Table 1: by true regime
    # ------------------------------------------------------------------
    by_regime = defaultdict(lambda: {"n": 0, "llm_right": 0, "comp_right": 0})
    for tid in test_tids:
        true_reg = gt[tid].get("true_regime")
        llm_pred = top1(receiver[tid].get("parsed", {}).get("regime", {}).get("posterior", {}))
        comp_pred = top1(comp[tid].get("regime", {}).get("posterior", {}))
        d = by_regime[true_reg]
        d["n"] += 1
        if llm_pred == true_reg:
            d["llm_right"] += 1
        if comp_pred == true_reg:
            d["comp_right"] += 1

    print("=" * 90)
    print("Table 1 — Regime classification: correct vs incorrect, by true regime")
    print("=" * 90)
    print(f"{'Regime':<28} {'n':>5} {'LLM ✓':>8} {'LLM ✗':>8} {'LLM %':>8} {'Comp ✓':>8} {'Comp ✗':>8} {'Comp %':>8}")
    print("-" * 90)
    total_n = 0
    total_llm = 0
    total_comp = 0
    for reg in REGIME_KEYS:
        d = by_regime.get(reg, {"n": 0, "llm_right": 0, "comp_right": 0})
        n = d["n"]
        if n == 0:
            continue
        llm_r = d["llm_right"]
        llm_w = n - llm_r
        comp_r = d["comp_right"]
        comp_w = n - comp_r
        total_n += n
        total_llm += llm_r
        total_comp += comp_r
        print(f"{reg:<28} {n:>5} {llm_r:>8} {llm_w:>8} {llm_r/n*100:>7.1f}% {comp_r:>8} {comp_w:>8} {comp_r/n*100:>7.1f}%")
    print("-" * 90)
    print(f"{'TOTAL':<28} {total_n:>5} {total_llm:>8} {total_n-total_llm:>8} {total_llm/total_n*100:>7.1f}% {total_comp:>8} {total_n-total_comp:>8} {total_comp/total_n*100:>7.1f}%")
    print(f"\nChance baseline on 8-way classification: 12.5%")
    print()

    # ------------------------------------------------------------------
    # Table 2: by trace level
    # ------------------------------------------------------------------
    by_trace = defaultdict(lambda: {"n": 0, "llm_right": 0, "comp_right": 0})
    for tid in test_tids:
        true_reg = gt[tid].get("true_regime")
        llm_pred = top1(receiver[tid].get("parsed", {}).get("regime", {}).get("posterior", {}))
        comp_pred = top1(comp[tid].get("regime", {}).get("posterior", {}))
        trace, _ = parse_axes(tid)
        d = by_trace[trace]
        d["n"] += 1
        if llm_pred == true_reg:
            d["llm_right"] += 1
        if comp_pred == true_reg:
            d["comp_right"] += 1

    print("=" * 76)
    print("Table 2 — Regime classification: correct vs incorrect, by trace level")
    print("=" * 76)
    print(f"{'Trace level':<14} {'n':>5} {'LLM ✓':>8} {'LLM ✗':>8} {'LLM %':>8} {'Comp ✓':>8} {'Comp ✗':>8} {'Comp %':>8}")
    print("-" * 76)
    for trace in sorted(by_trace.keys()):
        d = by_trace[trace]
        n = d["n"]
        llm_r = d["llm_right"]
        comp_r = d["comp_right"]
        print(f"{trace:<14} {n:>5} {llm_r:>8} {n-llm_r:>8} {llm_r/n*100:>7.1f}% {comp_r:>8} {n-comp_r:>8} {comp_r/n*100:>7.1f}%")
    print()

    # ------------------------------------------------------------------
    # Table 3: by chain hop count (R7 only)
    # ------------------------------------------------------------------
    by_hops = defaultdict(lambda: {"n": 0, "llm_right": 0, "comp_right": 0})
    for tid in test_tids:
        if gt[tid].get("true_regime") != "chain_relay":
            continue
        hops = gt[tid].get("hop_count")
        if hops is None:
            continue
        llm_pred = top1(receiver[tid].get("parsed", {}).get("regime", {}).get("posterior", {}))
        comp_pred = top1(comp[tid].get("regime", {}).get("posterior", {}))
        d = by_hops[hops]
        d["n"] += 1
        if llm_pred == "chain_relay":
            d["llm_right"] += 1
        if comp_pred == "chain_relay":
            d["comp_right"] += 1

    print("=" * 76)
    print("Table 3 — chain_relay only: identification by hop count (1, 3, 5)")
    print("=" * 76)
    print(f"{'Hops':<6} {'n':>5} {'LLM ✓':>8} {'LLM ✗':>8} {'LLM %':>8} {'Comp ✓':>8} {'Comp ✗':>8} {'Comp %':>8}")
    print("-" * 76)
    for h in sorted(by_hops.keys()):
        d = by_hops[h]
        n = d["n"]
        llm_r = d["llm_right"]
        comp_r = d["comp_right"]
        print(f"{h:<6} {n:>5} {llm_r:>8} {n-llm_r:>8} {llm_r/n*100:>7.1f}% {comp_r:>8} {n-comp_r:>8} {comp_r/n*100:>7.1f}%")
    print()

    # ------------------------------------------------------------------
    # Tables 4 & 5: confusion matrices side by side
    # ------------------------------------------------------------------
    llm_cm = defaultdict(lambda: defaultdict(int))
    comp_cm = defaultdict(lambda: defaultdict(int))
    for tid in test_tids:
        true_reg = gt[tid].get("true_regime")
        llm_pred = top1(receiver[tid].get("parsed", {}).get("regime", {}).get("posterior", {}))
        comp_pred = top1(comp[tid].get("regime", {}).get("posterior", {}))
        if llm_pred:
            llm_cm[true_reg][llm_pred] += 1
        if comp_pred:
            comp_cm[true_reg][comp_pred] += 1

    short = {
        "single_direct": "single",
        "chain_relay": "chain",
        "independent_corroboration": "indep",
        "dependent_repetition": "dep_rep",
        "common_source_laundering": "launder",
        "clustered_reinforcement": "cluster",
        "centralized_synthesis": "synth",
        "compound": "cmpd",
    }

    def print_cm(title, cm):
        print(f"\n{title}")
        label = "true/pred"
        header = f"{label:<14}" + "".join(f"{short[r]:>9}" for r in REGIME_KEYS)
        print(header)
        print("-" * len(header))
        for tr in REGIME_KEYS:
            row = f"{short[tr]:<14}"
            for pr in REGIME_KEYS:
                v = cm.get(tr, {}).get(pr, 0)
                cell = str(v) if v else "."
                row += f"{cell:>9}"
            print(row)

    print("=" * 90)
    print("Confusion matrices — test trials only (n=840)")
    print("=" * 90)
    print_cm("LLM receiver — rows are true regime, columns are predicted regime", llm_cm)
    print_cm("Structure-blind comparator — rows are true regime, columns are predicted regime", comp_cm)


if __name__ == "__main__":
    main()
