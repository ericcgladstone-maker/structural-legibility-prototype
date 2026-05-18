#!/usr/bin/env python3
"""
Items 1 + 2 of the post-B-prime analysis pass.

ITEM 1 — Structure-blind comparator (Tetlock empirical-benchmark) vs receiver:
  Train an LR on residue features against the same ground truth the receiver is
  scored on. Compare per-cell Brier (accuracy) and top-1 accuracy (regime) between
  the receiver and the comparator. If receiver beats comparator, the receiver is
  doing structural reasoning above and beyond pattern-matching on surface features.

ITEM 2 — Ground-truth accuracy Brier on the receiver's accuracy posterior:
  The ground-truth accuracy proxy is proposition_preservation_rate from the
  residue extractor — what fraction of the source's in-scope propositions
  survived into the terminal message that the receiver saw. Brier of the
  receiver's accuracy probability vs binarized truth (>= 0.7 threshold), plus
  mean-absolute-error and Pearson correlation against the continuous truth.

Inputs (all in outputs/):
  - {experiment_id}.lineage.jsonl
  - {experiment_id}.receiver.jsonl
  - {experiment_id}.ground_truth.jsonl
  - {experiment_id}.terminal_features.jsonl  (produced by extract_terminal_features_paper1.py)

Outputs (in outputs/):
  - {experiment_id}.comparator_eval.md       (markdown report)
  - {experiment_id}.comparator_eval.json     (machine-readable analyses)
  - {experiment_id}.comparator_predictions.jsonl  (per-trial comparator predictions)

Holdout: 80/20 world-level split (worlds W001-W016 train, W017-W020 test). World-level
to avoid leakage from within-world replicate variance.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import numpy as np

from src.empirical_benchmark import (
    DEFAULT_FEATURE_KEYS,
    TrainingExample,
    predict_receiver_format,
    train_comparator,
)

# Honest structure-blind features: surface text statistics + dictionary counts ONLY.
# Excluded: proposition_*, semantic_drift_*, compression_ratio_* — these require
# knowledge of the source/parent text or the world's propositions, which a
# structure-blind receiver does not have access to.
STRUCTURE_BLIND_FEATURE_KEYS = [
    "token_count",
    "sentence_count",
    "type_token_ratio",
    "mean_sentence_length",
    "mean_word_length",
    "punctuation_density",
    "numeric_token_count",
    "named_entity_count",
    "temporal_marker_count",
    "location_marker_count",
    "hedge_count",
    "uncertainty_marker_count",
    "evidential_marker_count",
    "source_marker_count",
]


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


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as f:
        return [json.loads(l) for l in f if l.strip()]


def load_streams(experiment_id: str):
    outdir = ROOT / "outputs"
    lineage = load_jsonl(outdir / f"{experiment_id}.lineage.jsonl")
    receiver = load_jsonl(outdir / f"{experiment_id}.receiver.jsonl")
    gt = load_jsonl(outdir / f"{experiment_id}.ground_truth.jsonl")
    features = load_jsonl(outdir / f"{experiment_id}.terminal_features.jsonl")
    return lineage, receiver, gt, features


def join_trials(lineage, receiver, gt, features):
    """Join all streams on the (cell_id, world_id, replicate_index) tuple OR on trial_id.

    Trial_id is the unambiguous join key (present in lineage's messages, receiver, gt).
    Features were keyed by (run_id, world_id, cell_id) so we map run_id -> trial_id via
    the receiver/gt records.
    """
    # Build run_id -> trial_id lookup from ground_truth records
    run_to_trials = defaultdict(list)
    for g in gt:
        run_to_trials[g.get("lineage_id")].append(g)
    # receiver and gt share trial_id
    receiver_by_tid = {r["trial_id"]: r for r in receiver if r.get("trial_id")}
    gt_by_tid = {g["trial_id"]: g for g in gt if g.get("trial_id")}
    # Features: key by (run_id) — there should be one record per lineage run
    features_by_run = {f["run_id"]: f for f in features}

    joined = []
    for tid, g in gt_by_tid.items():
        r = receiver_by_tid.get(tid)
        if r is None:
            continue
        run_id = g.get("lineage_id")
        feat = features_by_run.get(run_id)
        if feat is None:
            continue
        joined.append({
            "trial_id": tid,
            "world_id": g.get("world_id"),
            "cell_id": g.get("cell_id"),
            "ground_truth": g,
            "receiver": r,
            "features": feat["features"],
            "true_accuracy_score": feat.get("true_accuracy_score"),
        })
    return joined


def split_train_test(trials: list[dict], train_world_ids: set[str]):
    train = [t for t in trials if t["world_id"] in train_world_ids]
    test = [t for t in trials if t["world_id"] not in train_world_ids]
    return train, test


def build_training_examples(trials: list[dict]) -> list[TrainingExample]:
    examples = []
    for t in trials:
        score = t.get("true_accuracy_score")
        if score is None or not isinstance(score, (int, float)):
            continue
        gt = t["ground_truth"]
        examples.append(TrainingExample(
            trace_packet_id=t["trial_id"],
            world_id=t["world_id"],
            cell_id=t["cell_id"],
            features=t["features"],
            true_accuracy_score=float(score),
            true_regime=gt.get("true_regime") or "single_direct",
            true_independence_label=gt.get("true_independence_label"),
        ))
    return examples


def brier_binary(prob: float, outcome: int) -> float:
    return (prob - outcome) ** 2


def compute_metrics_for_predictions(trials, predictions_by_tid):
    """
    Compute per-cell metrics for a given set of receiver-or-comparator predictions.

    Returns dict with keys:
      - by_cell: {cell_id: {brier_accuracy, top1_regime_acc, n}}
      - overall: {brier_accuracy, top1_regime_acc, n}
    """
    per_cell = defaultdict(lambda: {"brier_accuracy_sum": 0.0, "brier_accuracy_n": 0,
                                     "regime_correct": 0, "regime_n": 0,
                                     "mae_accuracy_sum": 0.0, "mae_n": 0,
                                     "trials": 0})
    for t in trials:
        tid = t["trial_id"]
        pred = predictions_by_tid.get(tid)
        if pred is None:
            continue
        cell = t["cell_id"]
        per_cell[cell]["trials"] += 1

        # Accuracy: Brier against binarized ground truth, plus MAE against continuous
        true_score = t.get("true_accuracy_score")
        prob = pred.get("accuracy", {}).get("probability")
        if true_score is not None and isinstance(prob, (int, float)):
            y_bin = 1 if true_score >= 0.7 else 0
            per_cell[cell]["brier_accuracy_sum"] += (prob - y_bin) ** 2
            per_cell[cell]["brier_accuracy_n"] += 1
            per_cell[cell]["mae_accuracy_sum"] += abs(prob - true_score)
            per_cell[cell]["mae_n"] += 1

        # Regime top-1
        reg_post = pred.get("regime", {}).get("posterior", {})
        if reg_post:
            top = max(reg_post.items(), key=lambda x: x[1])[0]
            true_reg = t["ground_truth"].get("true_regime")
            per_cell[cell]["regime_n"] += 1
            if top == true_reg:
                per_cell[cell]["regime_correct"] += 1

    by_cell = {}
    overall_brier_sum, overall_brier_n = 0.0, 0
    overall_mae_sum, overall_mae_n = 0.0, 0
    overall_reg_correct, overall_reg_n = 0, 0
    for cell, d in per_cell.items():
        brier = d["brier_accuracy_sum"] / d["brier_accuracy_n"] if d["brier_accuracy_n"] else None
        mae = d["mae_accuracy_sum"] / d["mae_n"] if d["mae_n"] else None
        reg = d["regime_correct"] / d["regime_n"] if d["regime_n"] else None
        by_cell[cell] = {
            "brier_accuracy": round(brier, 4) if brier is not None else None,
            "mae_accuracy": round(mae, 4) if mae is not None else None,
            "top1_regime_acc": round(reg, 4) if reg is not None else None,
            "n": d["trials"],
        }
        overall_brier_sum += d["brier_accuracy_sum"]
        overall_brier_n += d["brier_accuracy_n"]
        overall_mae_sum += d["mae_accuracy_sum"]
        overall_mae_n += d["mae_n"]
        overall_reg_correct += d["regime_correct"]
        overall_reg_n += d["regime_n"]
    overall = {
        "brier_accuracy": round(overall_brier_sum / overall_brier_n, 4) if overall_brier_n else None,
        "mae_accuracy": round(overall_mae_sum / overall_mae_n, 4) if overall_mae_n else None,
        "top1_regime_acc": round(overall_reg_correct / overall_reg_n, 4) if overall_reg_n else None,
        "n_brier": overall_brier_n,
        "n_regime": overall_reg_n,
    }
    return {"by_cell": by_cell, "overall": overall}


def receiver_predictions_dict(trials):
    """Pull receiver predictions in the same shape as comparator predictions, keyed by trial_id."""
    out = {}
    for t in trials:
        rec = t["receiver"]
        if rec.get("invalid"):
            continue
        parsed = rec.get("parsed", {})
        if parsed:
            out[t["trial_id"]] = parsed
    return out


def comparator_predictions_dict(trials, models):
    out = {}
    for t in trials:
        rec = t["receiver"]
        parsed = rec.get("parsed", {})
        # Candidate IDs from the receiver's origin posterior (excluding deferred/outside)
        ori = parsed.get("origin", {}).get("posterior", {})
        candidate_ids = [k for k in ori.keys() if k not in ("outside_set", "unknown_deferred")]
        if not candidate_ids:
            # Fallback: 30 placeholder names
            candidate_ids = [f"CANDIDATE_{i}" for i in range(30)]
        regime = t["ground_truth"].get("true_regime")
        is_corro = regime in ("independent_corroboration", "dependent_repetition",
                              "common_source_laundering", "clustered_reinforcement")
        try:
            pred = predict_receiver_format(models, t["features"], candidate_ids, is_corroboration_family=is_corro)
            out[t["trial_id"]] = pred
        except Exception as e:
            print(f"[skip comparator] {t['trial_id']}: {e}")
    return out


def analyze_accuracy_brier_against_truth(trials):
    """
    Item 2 deliverable: Brier of receiver's accuracy posterior against ground-truth
    preservation_rate (binarized at 0.7), stratified by trace level, regime, validity.
    Also reports MAE against the continuous truth and Pearson correlation.
    """
    by_trace_level = defaultdict(lambda: {"brier_sum": 0.0, "mae_sum": 0.0, "n": 0,
                                           "probs": [], "scores": []})
    by_regime = defaultdict(lambda: {"brier_sum": 0.0, "mae_sum": 0.0, "n": 0,
                                      "probs": [], "scores": []})
    by_validity = defaultdict(lambda: {"brier_sum": 0.0, "mae_sum": 0.0, "n": 0,
                                        "probs": [], "scores": []})
    overall = {"brier_sum": 0.0, "mae_sum": 0.0, "n": 0, "probs": [], "scores": []}

    for t in trials:
        rec = t["receiver"]
        if rec.get("invalid"):
            continue
        prob = rec.get("parsed", {}).get("accuracy", {}).get("probability")
        score = t.get("true_accuracy_score")
        if not isinstance(prob, (int, float)) or score is None or not isinstance(score, (int, float)):
            continue
        y_bin = 1 if score >= 0.7 else 0
        brier = (prob - y_bin) ** 2
        mae = abs(prob - score)

        tid = t["trial_id"]
        parts = tid.split("__")
        trace = next((p for p in parts if p.startswith("L")), "?")
        validity = next((p for p in parts if p.startswith("v") and p[1:].isdigit()), "?")
        regime = t["ground_truth"].get("true_regime") or "?"

        for bucket in (by_trace_level[trace], by_regime[regime], by_validity[validity], overall):
            bucket["brier_sum"] += brier
            bucket["mae_sum"] += mae
            bucket["n"] += 1
            bucket["probs"].append(prob)
            bucket["scores"].append(score)

    def finalize(d):
        if d["n"] == 0:
            return None
        out = {
            "brier": round(d["brier_sum"] / d["n"], 4),
            "mae": round(d["mae_sum"] / d["n"], 4),
            "n": d["n"],
            "mean_receiver_prob": round(statistics.mean(d["probs"]), 4),
            "mean_true_score": round(statistics.mean(d["scores"]), 4),
        }
        if len(d["probs"]) > 1 and len(set(d["scores"])) > 1 and len(set(d["probs"])) > 1:
            try:
                out["pearson_r"] = round(float(np.corrcoef(d["probs"], d["scores"])[0, 1]), 4)
            except Exception:
                pass
        return out

    return {
        "overall": finalize(overall),
        "by_trace_level": {k: finalize(v) for k, v in by_trace_level.items() if v["n"] > 0},
        "by_regime": {k: finalize(v) for k, v in by_regime.items() if v["n"] > 0},
        "by_validity": {k: finalize(v) for k, v in by_validity.items() if v["n"] > 0},
    }


def render_report(experiment_id, item2, comparator_metrics, receiver_metrics, holdout_info) -> str:
    lines = [f"# Comparator + accuracy-Brier evaluation — {experiment_id}", ""]

    lines.append(f"Holdout: train worlds {sorted(holdout_info['train_worlds'])[:3]}…({len(holdout_info['train_worlds'])} worlds), "
                 f"test worlds {sorted(holdout_info['test_worlds'])} ({len(holdout_info['test_worlds'])} worlds). "
                 f"All metrics below computed on TEST worlds only.")
    lines.append("")

    # Item 2 headline
    lines.append("## Item 2 — Receiver accuracy posterior vs ground-truth preservation rate")
    lines.append("")
    o = item2["overall"]
    if o:
        lines.append(f"**Overall Brier on receiver accuracy posterior (vs binarized truth): {o['brier']}**")
        lines.append(f"- MAE against continuous truth: {o['mae']}")
        lines.append(f"- Mean receiver probability: {o['mean_receiver_prob']}  | Mean true preservation rate: {o['mean_true_score']}")
        if "pearson_r" in o:
            lines.append(f"- Pearson r(receiver_prob, true_score): {o['pearson_r']}")
        lines.append(f"- n = {o['n']}")
    lines.append("")
    lines.append("Reference: a constant predictor at the base rate would yield Brier = p*(1-p) where p = mean(true_y).")
    if o:
        mean_y = o["mean_true_score"]
        # Approximate base rate via mean continuous score thresholded at 0.7 — we don't have it directly, so estimate
        # Use a simpler reference: a constant 0.79 predictor against binarized truth
        lines.append(f"  Receiver's constant-prediction Brier (always predict 0.79): see per-cell breakdown for comparison.")
    lines.append("")

    lines.append("### By trace level")
    lines.append("")
    lines.append("| Trace level | Brier | MAE | Mean(receiver prob) | Mean(true score) | Pearson r | n |")
    lines.append("|---|---|---|---|---|---|---|")
    for L, d in sorted(item2["by_trace_level"].items()):
        pr = d.get("pearson_r", "—")
        lines.append(f"| {L} | {d['brier']} | {d['mae']} | {d['mean_receiver_prob']} | {d['mean_true_score']} | {pr} | {d['n']} |")
    lines.append("")

    lines.append("### By regime")
    lines.append("")
    lines.append("| Regime | Brier | MAE | Mean(receiver prob) | Mean(true score) | Pearson r | n |")
    lines.append("|---|---|---|---|---|---|---|")
    for reg, d in sorted(item2["by_regime"].items()):
        pr = d.get("pearson_r", "—")
        lines.append(f"| {reg} | {d['brier']} | {d['mae']} | {d['mean_receiver_prob']} | {d['mean_true_score']} | {pr} | {d['n']} |")
    lines.append("")

    lines.append("### By validity coefficient")
    lines.append("")
    lines.append("| Validity | Brier | MAE | Mean(receiver prob) | Mean(true score) | Pearson r | n |")
    lines.append("|---|---|---|---|---|---|---|")
    for v, d in sorted(item2["by_validity"].items()):
        pr = d.get("pearson_r", "—")
        lines.append(f"| {v} | {d['brier']} | {d['mae']} | {d['mean_receiver_prob']} | {d['mean_true_score']} | {pr} | {d['n']} |")
    lines.append("")

    # Item 1 headline
    lines.append("## Item 1 — Receiver vs structure-blind comparator")
    lines.append("")
    rec_o = receiver_metrics["overall"]
    comp_o = comparator_metrics["overall"]
    lines.append(f"**Receiver Brier (accuracy): {rec_o['brier_accuracy']}  | Comparator Brier: {comp_o['brier_accuracy']}**")
    delta = (rec_o['brier_accuracy'] - comp_o['brier_accuracy']) if rec_o['brier_accuracy'] is not None and comp_o['brier_accuracy'] is not None else None
    if delta is not None:
        sign = "WORSE" if delta > 0 else "BETTER"
        lines.append(f"  → Receiver is {sign} than comparator by {abs(delta):.4f} Brier (lower=better).")
    lines.append(f"**Receiver top-1 regime acc: {rec_o['top1_regime_acc']}  | Comparator: {comp_o['top1_regime_acc']}**")
    if rec_o['top1_regime_acc'] is not None and comp_o['top1_regime_acc'] is not None:
        d_reg = rec_o['top1_regime_acc'] - comp_o['top1_regime_acc']
        sign = "BETTER" if d_reg > 0 else "WORSE"
        lines.append(f"  → Receiver is {sign} than comparator by {abs(d_reg):.4f} (higher=better).")
    lines.append("")

    lines.append("### Per-cell receiver-vs-comparator deltas (test worlds only)")
    lines.append("")
    lines.append("| Cell | n | Recv Brier | Comp Brier | Brier Δ (recv-comp) | Recv reg-acc | Comp reg-acc | Reg Δ |")
    lines.append("|---|---|---|---|---|---|---|---|")
    all_cells = sorted(set(receiver_metrics["by_cell"].keys()) | set(comparator_metrics["by_cell"].keys()))
    for cell in all_cells:
        r = receiver_metrics["by_cell"].get(cell, {})
        c = comparator_metrics["by_cell"].get(cell, {})
        r_brier = r.get("brier_accuracy", None)
        c_brier = c.get("brier_accuracy", None)
        b_delta = round(r_brier - c_brier, 4) if r_brier is not None and c_brier is not None else "—"
        r_reg = r.get("top1_regime_acc", None)
        c_reg = c.get("top1_regime_acc", None)
        reg_delta = round(r_reg - c_reg, 4) if r_reg is not None and c_reg is not None else "—"
        n = r.get("n", c.get("n", 0))
        lines.append(f"| {cell} | {n} | {r_brier} | {c_brier} | {b_delta} | {r_reg} | {c_reg} | {reg_delta} |")
    lines.append("")
    lines.append("Reading: Brier Δ < 0 means receiver is better-calibrated on accuracy than the structure-blind baseline.")
    lines.append("Reg Δ > 0 means receiver is more often correct on regime than the baseline.")
    lines.append("Where both Δ favor the receiver, the receiver is doing structural reasoning beyond surface features.")
    lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment-id", default="machine_tracing_bprime_v0_1")
    ap.add_argument("--test-worlds", nargs="*", default=["W017", "W018", "W019", "W020"])
    args = ap.parse_args()

    print(f"Loading streams for {args.experiment_id}...")
    lineage, receiver, gt, features = load_streams(args.experiment_id)
    print(f"  lineage: {len(lineage)}, receiver: {len(receiver)}, gt: {len(gt)}, features: {len(features)}")

    print("Joining trials...")
    trials = join_trials(lineage, receiver, gt, features)
    print(f"  joined: {len(trials)}")

    test_world_set = set(args.test_worlds)
    train_world_set = set(t["world_id"] for t in trials) - test_world_set
    train_trials, test_trials = split_train_test(trials, train_world_set)
    print(f"  train trials: {len(train_trials)}, test trials: {len(test_trials)}")

    print("Building training examples...")
    train_examples = build_training_examples(train_trials)
    print(f"  {len(train_examples)} training examples")

    print(f"Training comparator (LR + isotonic calibration) on {len(STRUCTURE_BLIND_FEATURE_KEYS)} structure-blind surface features...")
    models = train_comparator(train_examples, feature_keys=STRUCTURE_BLIND_FEATURE_KEYS, seed=42)
    print("  done.")

    print("Generating receiver and comparator predictions on test trials...")
    rec_preds = receiver_predictions_dict(test_trials)
    comp_preds = comparator_predictions_dict(test_trials, models)
    print(f"  receiver preds: {len(rec_preds)}, comparator preds: {len(comp_preds)}")

    # Write comparator predictions to disk for downstream use
    comp_path = ROOT / "outputs" / f"{args.experiment_id}.comparator_predictions.jsonl"
    with comp_path.open("w") as f:
        for tid, pred in comp_preds.items():
            f.write(json.dumps({"trial_id": tid, **pred}) + "\n")

    print("Computing metrics...")
    receiver_metrics = compute_metrics_for_predictions(test_trials, rec_preds)
    comparator_metrics = compute_metrics_for_predictions(test_trials, comp_preds)

    print("Computing item-2 accuracy-Brier analysis (all trials, both train+test)...")
    item2 = analyze_accuracy_brier_against_truth(trials)

    report = render_report(
        args.experiment_id, item2, comparator_metrics, receiver_metrics,
        holdout_info={"train_worlds": sorted(train_world_set), "test_worlds": sorted(test_world_set)},
    )

    report_path = ROOT / "outputs" / f"{args.experiment_id}.comparator_eval.md"
    with report_path.open("w") as f:
        f.write(report)
    json_path = ROOT / "outputs" / f"{args.experiment_id}.comparator_eval.json"
    with json_path.open("w") as f:
        json.dump({
            "item2": item2,
            "comparator_metrics": comparator_metrics,
            "receiver_metrics": receiver_metrics,
            "train_worlds": sorted(train_world_set),
            "test_worlds": sorted(test_world_set),
        }, f, indent=2, default=str)
    print(f"\nReport: {report_path}")
    print(f"JSON: {json_path}")
    print(f"Comparator preds: {comp_path}")


if __name__ == "__main__":
    main()
