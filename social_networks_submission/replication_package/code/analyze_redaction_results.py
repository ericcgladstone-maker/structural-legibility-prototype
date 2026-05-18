#!/usr/bin/env python3
"""
Summarize the redaction-experiment results.

Tests the form-vs-meaning mechanism: when an explicit cue is redacted from a message,
does the LLM's regime classification change?
- If yes: the LLM was using explicit cues; not purely form-blind.
- If no: the LLM was not using the cues; form-blind on this task.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    out = ROOT / "outputs" / "machine_tracing_bprime_v0_1.redaction_results.jsonl"
    with out.open() as f:
        records = [json.loads(l) for l in f if l.strip()]

    n = len(records)
    print(f"# Redaction experiment summary — n = {n} trials\n")

    # Overall
    n_changed = sum(1 for r in records if r["regime_changed"])
    n_orig_correct = sum(1 for r in records if r["original_correct"])
    n_red_correct = sum(1 for r in records if r["redacted_correct"])
    n_invalid_redacted = sum(1 for r in records if r["redacted_invalid"])
    n_acc_changed = sum(1 for r in records if r["original_accuracy_prob"] != r["redacted_accuracy_prob"])

    print("## Overall")
    print(f"- Regime top-1 changed after redaction: {n_changed} / {n} = {n_changed/n*100:.1f}%")
    print(f"- Original LLM correct on regime: {n_orig_correct} / {n} = {n_orig_correct/n*100:.1f}%")
    print(f"- Redacted LLM correct on regime: {n_red_correct} / {n} = {n_red_correct/n*100:.1f}%")
    print(f"- Accuracy posterior changed: {n_acc_changed} / {n} = {n_acc_changed/n*100:.1f}%")
    print(f"- Redacted receiver invalid: {n_invalid_redacted}\n")

    # By regime
    print("## By true regime\n")
    print(f"{'Regime':<28} {'n':>5} {'changed':>9} {'orig✓':>7} {'red✓':>7} {'orig→red':>15}")
    print("-" * 80)
    by_regime = defaultdict(list)
    for r in records:
        by_regime[r["true_regime"]].append(r)

    for reg in sorted(by_regime.keys()):
        rs = by_regime[reg]
        n_r = len(rs)
        n_changed_r = sum(1 for r in rs if r["regime_changed"])
        n_orig_correct_r = sum(1 for r in rs if r["original_correct"])
        n_red_correct_r = sum(1 for r in rs if r["redacted_correct"])
        # Net effect: did the redacted version become more or less correct?
        delta = n_red_correct_r - n_orig_correct_r
        delta_str = f"{n_orig_correct_r}→{n_red_correct_r} ({delta:+d})"
        print(f"{reg:<28} {n_r:>5} {n_changed_r:>3}/{n_r:<3}{n_changed_r/n_r*100:>4.0f}% {n_orig_correct_r:>3}/{n_r:<3} {n_red_correct_r:>3}/{n_r:<3} {delta_str:>15}")

    # By trace level
    print("\n## By trace level\n")
    print(f"{'Level':<8} {'n':>5} {'changed':>9} {'orig✓':>7} {'red✓':>7}")
    print("-" * 50)
    by_L = defaultdict(list)
    for r in records:
        L = f"L{r['trace_level']}"
        by_L[L].append(r)
    for L in sorted(by_L.keys()):
        rs = by_L[L]
        n_l = len(rs)
        n_changed_l = sum(1 for r in rs if r["regime_changed"])
        n_orig_correct_l = sum(1 for r in rs if r["original_correct"])
        n_red_correct_l = sum(1 for r in rs if r["redacted_correct"])
        print(f"{L:<8} {n_l:>5} {n_changed_l:>3}/{n_l:<3}{n_changed_l/n_l*100:>4.0f}% {n_orig_correct_l:>3}/{n_l:<3} {n_red_correct_l:>3}/{n_l:<3}")

    # Where the LLM did change, what did it change TO?
    print("\n## When the LLM's classification changed, what did it change to?\n")
    changes = defaultdict(int)  # (original_top1 → redacted_top1) → count
    for r in records:
        if r["regime_changed"]:
            changes[(r["original_top1_regime"], r["redacted_top1_regime"])] += 1
    if changes:
        for (orig, red), count in sorted(changes.items(), key=lambda x: -x[1]):
            print(f"  {orig} → {red}: {count}")
    else:
        print("  (no changes)")

    # Interpretation
    print("\n## Interpretation\n")
    pct_changed = n_changed / n * 100
    if pct_changed < 15:
        verdict = "**STRONG support for form-blindness.** Removing explicit cues did not shift the LLM's regime classification — the LLM was not using the cues."
    elif pct_changed < 35:
        verdict = "**MODERATE support for form-blindness.** The LLM was partially using cues, but most of its judgment is based on something other than the explicit disclosure."
    else:
        verdict = "**Cues mattered.** Removing explicit cues meaningfully shifted classifications. The 'form-blind' claim does NOT hold in its strong form — the LLM was using cues but apparently not effectively enough to close the gap with stylometry."
    print(verdict)
    print(f"\nForm-blindness predicted: changes are rare AND red✓ ≈ orig✓ (redaction doesn't hurt accuracy).")
    print(f"Observed: changes occurred in {pct_changed:.1f}% of trials; redaction shifted regime accuracy by {(n_red_correct - n_orig_correct):+d} cases.")


if __name__ == "__main__":
    main()
