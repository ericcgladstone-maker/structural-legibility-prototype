#!/usr/bin/env python3
"""
Substantive analysis of the B-prime primary run.

Computes the headline questions:
1. Does the receiver classify regime above chance (1/8 = 12.5%)?
2. Does the receiver's accuracy posterior align with ground-truth accuracy?
3. Does receiver origin recovery improve with trace level (the recoverability curve)?
4. Does the receiver detect false corroboration (R3/R4/R5 vs R2)?
5. Does the receiver beat chance on origin attribution at CS-M (chance ~3%)?
6. How does receiver performance vary with validity coefficient (adversarial trace)?
7. How does chain-hop-count interact with origin recovery?

Plus confusion matrices, per-cell tables, and ground-truth accuracy via residue extractor.
"""
import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

PROTO_ROOT = Path(__file__).resolve().parent.parent

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


def load_records(experiment_id: str):
    outdir = PROTO_ROOT / "outputs"
    streams = {}
    for name in ["lineage", "trace_packets", "receiver", "ground_truth"]:
        path = outdir / f"{experiment_id}.{name}.jsonl"
        with path.open() as f:
            streams[name] = [json.loads(l) for l in f if l.strip()]
    return streams


def join_by_trial_id(streams):
    """Return a list of dicts, each combining lineage + trace_packet + receiver + ground_truth for one trial."""
    by_id = defaultdict(dict)
    for name in ("lineage", "trace_packets", "receiver", "ground_truth"):
        for rec in streams[name]:
            tid = rec.get("trial_id")
            if tid:
                by_id[tid][name] = rec
    # Filter to trials present in all 4 streams
    return [v for v in by_id.values() if len(v) == 4]


def brier_score(predicted: float, actual: float) -> float:
    """Brier for a single binary prediction: squared error of predicted prob vs actual {0,1}."""
    return (predicted - actual) ** 2


def parse_cell_axes(trial_id: str):
    """Extract (regime_code, hop_count, trace_level, validity_label) from cell-id portion of trial_id."""
    # Trial-id pattern: bp__R<reg><h<n>>?__L<level>__v<vvv>__CSm__F1__W<world>__rep<n>
    parts = trial_id.split("__")
    reg = next((p for p in parts if p.startswith("R")), "?")
    hops = None
    if "h" in reg and len(reg) > 2:
        # R7h3 → hops = 3
        try:
            hops = int(reg.split("h")[1])
        except ValueError:
            hops = None
    trace = next((p for p in parts if p.startswith("L")), "?")
    val = next((p for p in parts if p.startswith("v") and p[1:].isdigit()), "?")
    return reg, hops, trace, val


def analyze_regime_classification(trials):
    """Top-1 receiver regime prediction vs ground truth, overall and per cell."""
    correct = 0
    total = 0
    cm = defaultdict(lambda: defaultdict(int))  # true_regime → predicted_regime → count
    by_cell = defaultdict(lambda: {"correct": 0, "total": 0})
    by_trace_level = defaultdict(lambda: {"correct": 0, "total": 0})

    for t in trials:
        rec = t["receiver"]
        gt = t["ground_truth"]
        if rec.get("invalid"):
            continue
        parsed = rec.get("parsed", {})
        posterior = parsed.get("regime", {}).get("posterior", {})
        if not posterior:
            continue
        # Top-1 predicted regime
        predicted = max(posterior.items(), key=lambda x: x[1])[0]
        true_reg = gt.get("true_regime")
        if true_reg is None:
            continue
        total += 1
        cm[true_reg][predicted] += 1
        if predicted == true_reg:
            correct += 1
            by_cell[t["lineage"]["condition"]]["correct"] += 1
            by_trace_level[parse_cell_axes(t["lineage"]["trial_id"])[2]]["correct"] += 1
        by_cell[t["lineage"]["condition"]]["total"] += 1
        by_trace_level[parse_cell_axes(t["lineage"]["trial_id"])[2]]["total"] += 1

    return {
        "overall_top1_accuracy": correct / total if total else 0,
        "total_trials_scored": total,
        "chance_baseline": 1 / 8,
        "confusion_matrix": dict((k, dict(v)) for k, v in cm.items()),
        "by_trace_level": dict(by_trace_level),
    }


def analyze_origin_recovery(trials):
    """c@1 on origin posterior, per trace level and per regime.

    c@1 = (correct_top1 + deferrals × correct_top1_rate_on_answered) / total
    Receiver may defer via assigning high mass to 'unknown_deferred'.
    """
    by_trace_level = defaultdict(lambda: {"correct": 0, "deferred": 0, "wrong": 0, "outside_correct": 0})
    by_regime = defaultdict(lambda: {"correct": 0, "deferred": 0, "wrong": 0, "outside_correct": 0})

    for t in trials:
        rec = t["receiver"]
        gt = t["ground_truth"]
        if rec.get("invalid"):
            continue
        parsed = rec.get("parsed", {})
        posterior = parsed.get("origin", {}).get("posterior", {})
        if not posterior:
            continue
        true_id = gt.get("true_source_persona_id")
        in_set = gt.get("true_source_in_candidate_set", True)
        # Top-1 predicted
        predicted = max(posterior.items(), key=lambda x: x[1])[0]
        trace = parse_cell_axes(t["lineage"]["trial_id"])[2]
        regime = gt.get("true_regime")

        if predicted == "unknown_deferred":
            by_trace_level[trace]["deferred"] += 1
            by_regime[regime]["deferred"] += 1
        elif predicted == "outside_set":
            if not in_set:
                by_trace_level[trace]["outside_correct"] += 1
                by_regime[regime]["outside_correct"] += 1
            else:
                by_trace_level[trace]["wrong"] += 1
                by_regime[regime]["wrong"] += 1
        else:
            if in_set and predicted == true_id:
                by_trace_level[trace]["correct"] += 1
                by_regime[regime]["correct"] += 1
            else:
                by_trace_level[trace]["wrong"] += 1
                by_regime[regime]["wrong"] += 1

    def compute_c_at_1(bucket):
        total = sum(bucket.values())
        if total == 0:
            return None
        answered = bucket["correct"] + bucket["wrong"] + bucket["outside_correct"]
        n_correct = bucket["correct"] + bucket["outside_correct"]
        n_deferred = bucket["deferred"]
        if answered == 0:
            # All deferred — c@1 reduces to 0
            return 0.0
        # c@1 = (n_correct + n_deferred * (n_correct / answered)) / total
        return (n_correct + n_deferred * (n_correct / answered)) / total

    return {
        "chance_baseline_cs_m": 1 / 32,  # 30 candidates + outside + unknown
        "by_trace_level": {
            k: {**v, "c@1": compute_c_at_1(v), "total": sum(v.values())}
            for k, v in by_trace_level.items()
        },
        "by_regime": {
            k: {**v, "c@1": compute_c_at_1(v), "total": sum(v.values())}
            for k, v in by_regime.items()
        },
    }


def analyze_accuracy_posterior(trials):
    """Distribution of receiver's accuracy posterior + Brier against world-state-derived ground truth."""
    # Ground-truth accuracy isn't computed yet (would need residue_extractor on terminals).
    # For now, report mean/median accuracy probability + variance per cell.
    by_trace_level = defaultdict(list)
    by_regime = defaultdict(list)
    by_validity = defaultdict(list)

    for t in trials:
        rec = t["receiver"]
        gt = t["ground_truth"]
        if rec.get("invalid"):
            continue
        parsed = rec.get("parsed", {})
        prob = parsed.get("accuracy", {}).get("probability")
        if not isinstance(prob, (int, float)):
            continue
        trace = parse_cell_axes(t["lineage"]["trial_id"])[2]
        validity = parse_cell_axes(t["lineage"]["trial_id"])[3]
        regime = gt.get("true_regime")
        by_trace_level[trace].append(prob)
        by_regime[regime].append(prob)
        by_validity[validity].append(prob)

    def stats(values):
        if not values:
            return None
        return {
            "n": len(values),
            "mean": round(statistics.mean(values), 4),
            "median": round(statistics.median(values), 4),
            "stdev": round(statistics.stdev(values), 4) if len(values) > 1 else None,
        }

    return {
        "by_trace_level": {k: stats(v) for k, v in by_trace_level.items()},
        "by_regime": {k: stats(v) for k, v in by_regime.items()},
        "by_validity": {k: stats(v) for k, v in by_validity.items()},
    }


def analyze_independence_judgment(trials):
    """Receiver's independence judgment vs ground-truth label, for corroboration-family regimes."""
    # Ground-truth label: True for independent_corroboration (R2); False for R3/R4/R5; None for others
    correct_class = 0
    n_classified = 0
    by_regime = defaultdict(lambda: {"correct": 0, "wrong": 0, "null": 0, "n": 0})
    threshold = 0.5

    for t in trials:
        rec = t["receiver"]
        gt = t["ground_truth"]
        if rec.get("invalid"):
            continue
        true_indep = gt.get("true_independence_label")
        if true_indep is None:
            continue
        parsed = rec.get("parsed", {})
        p_indep = parsed.get("independence_judgment", {}).get("probability_independent")
        regime = gt.get("true_regime")
        by_regime[regime]["n"] += 1
        if p_indep is None:
            by_regime[regime]["null"] += 1
            continue
        predicted = p_indep >= threshold
        n_classified += 1
        if predicted == true_indep:
            correct_class += 1
            by_regime[regime]["correct"] += 1
        else:
            by_regime[regime]["wrong"] += 1

    return {
        "overall_accuracy": correct_class / n_classified if n_classified else 0,
        "n_classified": n_classified,
        "chance_baseline": 0.5,
        "by_regime": dict(by_regime),
    }


def analyze_validity_effect(trials):
    """How does adversarial validity affect regime classification accuracy and origin c@1?"""
    by_val = defaultdict(lambda: {"regime_correct": 0, "regime_total": 0, "origin_correct": 0, "origin_total": 0})
    for t in trials:
        rec = t["receiver"]
        gt = t["ground_truth"]
        if rec.get("invalid"):
            continue
        parsed = rec.get("parsed", {})
        val = parse_cell_axes(t["lineage"]["trial_id"])[3]
        # Regime
        reg_posterior = parsed.get("regime", {}).get("posterior", {})
        if reg_posterior:
            predicted_reg = max(reg_posterior.items(), key=lambda x: x[1])[0]
            true_reg = gt.get("true_regime")
            by_val[val]["regime_total"] += 1
            if predicted_reg == true_reg:
                by_val[val]["regime_correct"] += 1
        # Origin
        ori_posterior = parsed.get("origin", {}).get("posterior", {})
        if ori_posterior:
            predicted_ori = max(ori_posterior.items(), key=lambda x: x[1])[0]
            true_id = gt.get("true_source_persona_id")
            in_set = gt.get("true_source_in_candidate_set", True)
            by_val[val]["origin_total"] += 1
            if in_set and predicted_ori == true_id:
                by_val[val]["origin_correct"] += 1
            elif (not in_set) and predicted_ori == "outside_set":
                by_val[val]["origin_correct"] += 1

    return {
        val: {
            "regime_top1_acc": d["regime_correct"] / d["regime_total"] if d["regime_total"] else 0,
            "origin_top1_acc": d["origin_correct"] / d["origin_total"] if d["origin_total"] else 0,
            "regime_n": d["regime_total"],
            "origin_n": d["origin_total"],
        }
        for val, d in sorted(by_val.items())
    }


def analyze_hop_count_effect(trials):
    """Chain-regime: receiver performance at hop=1, 3, 5."""
    by_hops = defaultdict(lambda: {"regime_correct": 0, "regime_total": 0, "origin_correct": 0, "origin_total": 0})
    for t in trials:
        rec = t["receiver"]
        gt = t["ground_truth"]
        if rec.get("invalid"):
            continue
        if gt.get("true_regime") != "chain_relay":
            continue
        hops = gt.get("hop_count")
        if hops is None:
            continue
        parsed = rec.get("parsed", {})
        reg_posterior = parsed.get("regime", {}).get("posterior", {})
        ori_posterior = parsed.get("origin", {}).get("posterior", {})
        if reg_posterior:
            predicted_reg = max(reg_posterior.items(), key=lambda x: x[1])[0]
            by_hops[hops]["regime_total"] += 1
            if predicted_reg == "chain_relay":
                by_hops[hops]["regime_correct"] += 1
        if ori_posterior:
            predicted_ori = max(ori_posterior.items(), key=lambda x: x[1])[0]
            true_id = gt.get("true_source_persona_id")
            in_set = gt.get("true_source_in_candidate_set", True)
            by_hops[hops]["origin_total"] += 1
            if in_set and predicted_ori == true_id:
                by_hops[hops]["origin_correct"] += 1
            elif (not in_set) and predicted_ori == "outside_set":
                by_hops[hops]["origin_correct"] += 1

    return {
        h: {
            "regime_top1_acc": d["regime_correct"] / d["regime_total"] if d["regime_total"] else 0,
            "origin_top1_acc": d["origin_correct"] / d["origin_total"] if d["origin_total"] else 0,
            "n": d["regime_total"],
        }
        for h, d in sorted(by_hops.items())
    }


def render_report(analyses, experiment_id) -> str:
    lines = [f"# Substantive Analysis — {experiment_id}", ""]

    # Headline numbers
    reg = analyses["regime_classification"]
    ori_tl = analyses["origin_recovery"]["by_trace_level"]
    indep = analyses["independence_judgment"]

    lines.append("## Headline numbers")
    lines.append("")
    lines.append(f"- **Regime classification (top-1)**: {reg['overall_top1_accuracy']:.1%} accurate "
                 f"({reg['total_trials_scored']} trials). **Chance = {reg['chance_baseline']:.1%}**.")
    if reg["overall_top1_accuracy"] > 2 * reg["chance_baseline"]:
        lines.append("    → Receiver is meaningfully above chance on regime classification.")
    else:
        lines.append("    → Receiver is near chance on regime classification.")
    overall_origin = sum(d.get("correct", 0) + d.get("outside_correct", 0) for d in ori_tl.values()) / sum(d.get("total", 0) for d in ori_tl.values())
    lines.append(f"- **Origin recovery (top-1 correct)**: {overall_origin:.1%} across all trace levels. **Chance at CS-M ≈ 3.1%**.")
    lines.append(f"- **Independence judgment (corroboration regimes)**: {indep['overall_accuracy']:.1%} accurate "
                 f"({indep['n_classified']} trials with applicable ground truth). **Chance = 50%**.")
    lines.append("")

    # Recoverability curve: regime classification by trace level
    lines.append("## Recoverability: regime classification by trace level")
    lines.append("")
    lines.append("| Trace level | Regime top-1 accuracy | n |")
    lines.append("|---|---|---|")
    for L, d in sorted(reg["by_trace_level"].items()):
        if d["total"]:
            acc = d["correct"] / d["total"]
            lines.append(f"| {L} | {acc:.1%} | {d['total']} |")
    lines.append("")

    # Origin recovery by trace level
    lines.append("## Origin recovery (c@1) by trace level")
    lines.append("")
    lines.append("| Trace level | c@1 | correct | wrong | deferred | outside_correct | n |")
    lines.append("|---|---|---|---|---|---|---|")
    for L, d in sorted(ori_tl.items()):
        c_at_1 = d.get("c@1") or 0
        lines.append(f"| {L} | {c_at_1:.1%} | {d['correct']} | {d['wrong']} | {d['deferred']} | {d['outside_correct']} | {d['total']} |")
    lines.append("")

    # Origin recovery by regime
    lines.append("## Origin recovery (c@1) by regime")
    lines.append("")
    ori_reg = analyses["origin_recovery"]["by_regime"]
    lines.append("| Regime | c@1 | correct | wrong | deferred | outside_correct | n |")
    lines.append("|---|---|---|---|---|---|---|")
    for reg_name, d in sorted(ori_reg.items()):
        c_at_1 = d.get("c@1") or 0
        lines.append(f"| {reg_name} | {c_at_1:.1%} | {d['correct']} | {d['wrong']} | {d['deferred']} | {d['outside_correct']} | {d['total']} |")
    lines.append("")

    # Confusion matrix (regime classification)
    lines.append("## Regime confusion matrix (true × predicted)")
    lines.append("")
    cm = reg["confusion_matrix"]
    all_regimes = sorted(set(list(cm.keys()) + [p for v in cm.values() for p in v.keys()]))
    header = "| true \\ pred | " + " | ".join(r[:10] for r in all_regimes) + " |"
    lines.append(header)
    lines.append("|---" * (len(all_regimes) + 1) + "|")
    for true_reg in all_regimes:
        row = [true_reg[:15]]
        for pred_reg in all_regimes:
            count = cm.get(true_reg, {}).get(pred_reg, 0)
            row.append(str(count))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Validity-coefficient effect
    lines.append("## Validity-coefficient effect")
    lines.append("")
    ve = analyses["validity_effect"]
    lines.append("| Validity | Regime top-1 acc | Origin top-1 acc | n |")
    lines.append("|---|---|---|---|")
    for val, d in sorted(ve.items()):
        lines.append(f"| {val} | {d['regime_top1_acc']:.1%} | {d['origin_top1_acc']:.1%} | {d['regime_n']} |")
    lines.append("")

    # Hop-count effect (chain regime only)
    lines.append("## Chain hop-count effect")
    lines.append("")
    hc = analyses["hop_count_effect"]
    lines.append("| Hops | Regime → chain_relay acc | Origin top-1 acc | n |")
    lines.append("|---|---|---|---|")
    for h, d in sorted(hc.items()):
        lines.append(f"| {h} | {d['regime_top1_acc']:.1%} | {d['origin_top1_acc']:.1%} | {d['n']} |")
    lines.append("")

    # Accuracy posterior summary
    lines.append("## Accuracy posterior summary (descriptive)")
    lines.append("")
    ap = analyses["accuracy_posterior"]
    lines.append("By trace level:")
    for L, s in sorted(ap["by_trace_level"].items()):
        if s:
            lines.append(f"- {L}: mean={s['mean']}, median={s['median']}, stdev={s['stdev']}, n={s['n']}")
    lines.append("")
    lines.append("By validity coefficient:")
    for v, s in sorted(ap["by_validity"].items()):
        if s:
            lines.append(f"- {v}: mean={s['mean']}, median={s['median']}, stdev={s['stdev']}, n={s['n']}")
    lines.append("")
    lines.append("By true regime:")
    for r, s in sorted(ap["by_regime"].items()):
        if s:
            lines.append(f"- {r}: mean={s['mean']}, median={s['median']}, stdev={s['stdev']}, n={s['n']}")
    lines.append("")

    # Independence judgment per regime
    lines.append("## Independence judgment by regime")
    lines.append("")
    lines.append("| Regime | True indep label | Correct | Wrong | Null | n |")
    lines.append("|---|---|---|---|---|---|")
    truth_per_regime = {
        "independent_corroboration": True,
        "dependent_repetition": False,
        "common_source_laundering": False,
        "clustered_reinforcement": False,
    }
    for reg, d in sorted(indep["by_regime"].items()):
        gt = truth_per_regime.get(reg, "—")
        lines.append(f"| {reg} | {gt} | {d['correct']} | {d['wrong']} | {d['null']} | {d['n']} |")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-id", default="machine_tracing_bprime_v0_1")
    parser.add_argument("--report-path", default=None)
    args = parser.parse_args()

    streams = load_records(args.experiment_id)
    trials = join_by_trial_id(streams)
    print(f"Loaded {len(trials)} trials across all 4 streams.")

    analyses = {
        "regime_classification": analyze_regime_classification(trials),
        "origin_recovery": analyze_origin_recovery(trials),
        "accuracy_posterior": analyze_accuracy_posterior(trials),
        "independence_judgment": analyze_independence_judgment(trials),
        "validity_effect": analyze_validity_effect(trials),
        "hop_count_effect": analyze_hop_count_effect(trials),
    }

    report = render_report(analyses, args.experiment_id)
    report_path = Path(args.report_path) if args.report_path else PROTO_ROOT / "outputs" / f"{args.experiment_id}.substantive_report.md"
    with report_path.open("w") as f:
        f.write(report)
    json_path = report_path.with_suffix(".substantive.json")
    with json_path.open("w") as f:
        json.dump(analyses, f, indent=2, default=str)

    print(report)
    print(f"\nReport: {report_path}")
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
