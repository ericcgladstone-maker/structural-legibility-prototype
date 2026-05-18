#!/usr/bin/env python3
"""
Does message length affect regime classification accuracy?
Theoretical prediction: floor at low length, rise, asymptote.
Tested for both the LLM receiver and the structure-blind comparator on F1.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEST_WORLDS = {"W017", "W018", "W019", "W020"}


def main():
    out = ROOT / "outputs"
    eid = "machine_tracing_bprime_v0_1"

    def jsonl(p):
        with p.open() as f:
            return [json.loads(l) for l in f if l.strip()]

    receiver = {r["trial_id"]: r for r in jsonl(out / f"{eid}.receiver.jsonl") if r.get("trial_id")}
    gt = {g["trial_id"]: g for g in jsonl(out / f"{eid}.ground_truth.jsonl") if g.get("trial_id")}
    comp = {c["trial_id"]: c for c in jsonl(out / f"{eid}.comparator_predictions.jsonl") if c.get("trial_id")}
    features = jsonl(out / f"{eid}.terminal_features.jsonl")
    feat_by_run = {f["run_id"]: f for f in features}

    def top1(post):
        if not post:
            return None
        return max(post.items(), key=lambda x: x[1])[0]

    # Build per-trial join with token_count
    trials = []
    for tid, g in gt.items():
        if tid not in receiver:
            continue
        run_id = g.get("lineage_id")
        feat = feat_by_run.get(run_id)
        if not feat:
            continue
        token_count = (feat["features"] or {}).get("token_count")
        if token_count is None:
            continue
        true_reg = g.get("true_regime")
        llm_top1 = top1((receiver[tid].get("parsed") or {}).get("regime", {}).get("posterior", {}))
        in_test = g.get("world_id") in TEST_WORLDS
        comp_top1 = top1(comp.get(tid, {}).get("regime", {}).get("posterior", {})) if in_test else None
        trials.append({
            "trial_id": tid,
            "true_regime": true_reg,
            "token_count": int(token_count),
            "llm_top1": llm_top1,
            "comp_top1": comp_top1,
            "in_test": in_test,
        })

    print(f"Total trials: {len(trials)}")
    print(f"Test trials (with comparator preds): {sum(1 for t in trials if t['in_test'])}\n")

    # ----- Length distribution by regime -----
    print("=" * 60)
    print("Message length distribution by regime (all trials)")
    print("=" * 60)
    print(f"{'Regime':<28} {'n':>5} {'mean':>6} {'median':>7} {'min':>5} {'max':>5}")
    by_reg = defaultdict(list)
    for t in trials:
        by_reg[t["true_regime"]].append(t["token_count"])
    for reg in sorted(by_reg.keys()):
        tcs = by_reg[reg]
        tcs_sorted = sorted(tcs)
        mean = sum(tcs) / len(tcs)
        median = tcs_sorted[len(tcs) // 2]
        print(f"{reg:<28} {len(tcs):>5} {mean:>6.0f} {median:>7} {min(tcs):>5} {max(tcs):>5}")
    print()

    # ----- Length-vs-accuracy: LLM (all trials) -----
    bins = [(0, 100), (100, 150), (150, 200), (200, 250), (250, 300), (300, 400), (400, 1000)]

    def bin_label(lo, hi):
        return f"{lo}-{hi if hi < 1000 else '∞'}"

    def compute_bin_accuracy(items, pred_key, restrict_to_test=False):
        binned = defaultdict(lambda: {"n": 0, "correct": 0})
        for t in items:
            if restrict_to_test and not t["in_test"]:
                continue
            pred = t[pred_key]
            if pred is None:
                continue
            tc = t["token_count"]
            for lo, hi in bins:
                if lo <= tc < hi:
                    binned[(lo, hi)]["n"] += 1
                    if pred == t["true_regime"]:
                        binned[(lo, hi)]["correct"] += 1
                    break
        return binned

    print("=" * 60)
    print("LLM regime accuracy by message length (all 4,200 trials)")
    print("=" * 60)
    print(f"{'Token range':<14} {'n':>5} {'correct':>8} {'accuracy':>10}")
    llm_binned = compute_bin_accuracy(trials, "llm_top1", restrict_to_test=False)
    for lo, hi in bins:
        d = llm_binned[(lo, hi)]
        n = d["n"]
        if n == 0:
            continue
        acc = d["correct"] / n
        print(f"{bin_label(lo, hi):<14} {n:>5} {d['correct']:>8} {acc*100:>9.1f}%")
    print()

    print("=" * 60)
    print("Comparator regime accuracy by message length (test trials only, n=840)")
    print("=" * 60)
    print(f"{'Token range':<14} {'n':>5} {'correct':>8} {'accuracy':>10}")
    comp_binned = compute_bin_accuracy(trials, "comp_top1", restrict_to_test=True)
    for lo, hi in bins:
        d = comp_binned[(lo, hi)]
        n = d["n"]
        if n == 0:
            continue
        acc = d["correct"] / n
        print(f"{bin_label(lo, hi):<14} {n:>5} {d['correct']:>8} {acc*100:>9.1f}%")
    print()

    # ----- Within-regime length vs accuracy -----
    print("=" * 80)
    print("WITHIN-regime length effect — Comparator (test trials only)")
    print("=" * 80)
    print(f"{'Regime':<28} {'short ≤200':>13} {'mid 200-300':>14} {'long >300':>13}")
    print("-" * 80)
    for reg in sorted(by_reg.keys()):
        reg_trials = [t for t in trials if t["true_regime"] == reg and t["in_test"]]
        if not reg_trials:
            continue
        short = [t for t in reg_trials if t["token_count"] <= 200 and t["comp_top1"] is not None]
        mid = [t for t in reg_trials if 200 < t["token_count"] <= 300 and t["comp_top1"] is not None]
        long_ = [t for t in reg_trials if t["token_count"] > 300 and t["comp_top1"] is not None]
        def fmt(lst):
            if not lst:
                return "—"
            n = len(lst)
            c = sum(1 for t in lst if t["comp_top1"] == t["true_regime"])
            return f"{c}/{n} ({c/n*100:.0f}%)"
        print(f"{reg:<28} {fmt(short):>13} {fmt(mid):>14} {fmt(long_):>13}")
    print()

    print("=" * 80)
    print("WITHIN-regime length effect — LLM (all trials)")
    print("=" * 80)
    print(f"{'Regime':<28} {'short ≤200':>13} {'mid 200-300':>14} {'long >300':>13}")
    print("-" * 80)
    for reg in sorted(by_reg.keys()):
        reg_trials = [t for t in trials if t["true_regime"] == reg and t["llm_top1"] is not None]
        short = [t for t in reg_trials if t["token_count"] <= 200]
        mid = [t for t in reg_trials if 200 < t["token_count"] <= 300]
        long_ = [t for t in reg_trials if t["token_count"] > 300]
        def fmt(lst):
            if not lst:
                return "—"
            n = len(lst)
            c = sum(1 for t in lst if t["llm_top1"] == t["true_regime"])
            return f"{c}/{n} ({c/n*100:.0f}%)"
        print(f"{reg:<28} {fmt(short):>13} {fmt(mid):>14} {fmt(long_):>13}")


if __name__ == "__main__":
    main()
