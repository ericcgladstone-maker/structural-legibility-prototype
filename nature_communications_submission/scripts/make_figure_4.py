"""Figure 4 — Alignment diagnostics, three panels.

Panel a: length-only vs full 14-feature classifier on the same test split.
        Identifies the feature channels that carry the recovery signal.

Panel b: F1 (qwen2.5:7b) vs F2 (llama3.1:8b) reader-family comparison.
        Shows the gap between residue classes survives a change of language
        model on the content-attentive side.

Panel c: trace-observability sweep (L1 -> L6) for both readers, with the
        form-aligned L1 accuracy as a dashed reference line.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import figure_style as fs

fs.apply_style()

PREEMPT_PATH = (
    fs.PROJECT_ROOT
    / "Nature Communications Submission"
    / "00_source_social_networks_submission"
    / "replication_package"
    / "paper1_preempt_analyses.json"
)


def panel_length_only(ax) -> None:
    """Panel a: full 14-feature vs length-only classifier."""
    with open(PREEMPT_PATH) as fh:
        agg = json.load(fh)["analysis_a"]

    full = agg["full_14"]["aggregate"]
    length = agg["length_only_2"]["aggregate"]

    full_ci = fs.wilson_ci(full["correct"], full["n"])
    length_ci = fs.wilson_ci(length["correct"], length["n"])

    positions = [0.0, 0.85]
    values = [full["acc"], length["acc"]]
    err_lo = [v - ci[0] for v, ci in zip(values, [full_ci, length_ci])]
    err_hi = [ci[1] - v for v, ci in zip(values, [full_ci, length_ci])]
    rb = [full["regime_balanced_mean"], length["regime_balanced_mean"]]

    fa_colour = fs.READER_COLOR["form_aligned"]
    bars = ax.bar(
        positions, values, width=0.55,
        color=fa_colour, edgecolor=fa_colour, linewidth=0.6,
    )
    bars[1].set_facecolor("white")
    bars[1].set_hatch("////")

    ax.errorbar(positions, values, yerr=[err_lo, err_hi], fmt="none",
                ecolor="black", elinewidth=0.6, capsize=2.0)

    for x, v in zip(positions, values):
        ax.text(x, v + 0.022, f"{v * 100:.1f}%", ha="center", va="bottom", fontsize=7)

    ax.set_xticks(positions)
    ax.set_xticklabels(["14-feature\nclassifier", "Length-only\n(2 features)"],
                       fontsize=7)
    ax.set_ylim(0, 0.85)
    ax.set_yticks(np.arange(0, 0.81, 0.2))
    ax.set_yticklabels([f"{int(t * 100)}%" for t in np.arange(0, 0.81, 0.2)])
    ax.set_ylabel("Pooled accuracy on test split")

    # Balanced-mean annotations positioned in the empty upper area inside each bar.
    # The 14-feature bar (solid teal) carries a white label; the length-only bar
    # (hatched white) carries a dark label for legibility against the hatching.
    for x, m, dark in zip(positions, rb, (False, True)):
        ax.text(x, 0.05, f"balanced\nmean\n{m * 100:.1f}%", ha="center", va="bottom",
                fontsize=5.5, color="#1a1a1a" if dark else "white",
                fontweight="bold" if dark else "normal",
                linespacing=1.0)

    ax.axhline(fs.CHANCE_BASELINE, color=fs.CHANCE_COLOR, linestyle=(0, (3, 2)),
               linewidth=0.6, zorder=0)

    ax.set_title("Full features exceed length-only",
                 fontsize=7.5, pad=4, color="#333333", loc="left",
                 fontweight="bold")


def panel_cross_family(ax) -> None:
    """Panel b: cross-family slice (F1 primary vs F2 cross-family) for both readers."""
    comp1 = fs.load_comparator("F1")
    comp2 = fs.load_comparator("F2")
    recv1 = fs.load_receiver("F1")
    recv2 = fs.load_receiver("F2")

    def test_acc(df, pred_col):
        sub = df[df["world_id"].isin(fs.TEST_WORLDS)]
        return fs.summarize_accuracy(sub[pred_col] == sub["true_regime"])

    fa1 = test_acc(comp1, "predicted_regime_comparator")
    fa2 = test_acc(comp2, "predicted_regime_comparator")
    ca1 = test_acc(recv1, "predicted_regime")
    ca2 = test_acc(recv2, "predicted_regime")

    group_centres = np.array([0.0, 2.2])
    intra = 0.36
    positions = [
        group_centres[0] - intra / 2, group_centres[0] + intra / 2,
        group_centres[1] - intra / 2, group_centres[1] + intra / 2,
    ]
    results = [fa1, fa2, ca1, ca2]
    fa_colour = fs.READER_COLOR["form_aligned"]
    ca_colour = fs.READER_COLOR["content_attentive"]
    edge_colours = [fa_colour, fa_colour, ca_colour, ca_colour]
    face_colours = [fa_colour, "white", ca_colour, "white"]
    hatches = [None, "////", None, "////"]
    families = ["F1", "F2", "F1", "F2"]

    bars = ax.bar(positions, [r.accuracy for r in results], width=intra * 0.9,
                  color=face_colours, edgecolor=edge_colours, linewidth=0.7)
    for bar, h in zip(bars, hatches):
        if h:
            bar.set_hatch(h)
    ax.errorbar(
        positions, [r.accuracy for r in results],
        yerr=[[r.accuracy - r.ci_lo for r in results], [r.ci_hi - r.accuracy for r in results]],
        fmt="none", ecolor="black", elinewidth=0.6, capsize=2.0,
    )

    for x, r in zip(positions, results):
        ax.text(x, r.accuracy + 0.022, f"{r.accuracy * 100:.1f}%",
                ha="center", va="bottom", fontsize=6.5)

    ax.set_xticks(positions)
    ax.set_xticklabels(families, fontsize=6.5)
    ax.text(group_centres[0], -0.13, "Form-aligned",
            ha="center", va="top", fontsize=7, fontweight="bold", transform=ax.transData)
    ax.text(group_centres[1], -0.13, "Content-attentive",
            ha="center", va="top", fontsize=7, fontweight="bold", transform=ax.transData)

    ax.set_xlim(-0.55, group_centres[1] + 0.55)
    ax.set_ylim(0, 0.85)
    ax.set_yticks(np.arange(0, 0.81, 0.2))
    ax.set_yticklabels([f"{int(t * 100)}%" for t in np.arange(0, 0.81, 0.2)])
    ax.set_ylabel("Test-split accuracy")

    ax.axhline(fs.CHANCE_BASELINE, color=fs.CHANCE_COLOR, linestyle=(0, (3, 2)),
               linewidth=0.6, zorder=0)

    ax.set_title("Gap persists across reader families",
                 fontsize=7.5, pad=4, color="#333333", loc="left",
                 fontweight="bold")


def fam_str(x, positions, families):
    idx = positions.index(x)
    return families[idx]


def panel_trace(ax) -> None:
    """Panel c: trace-observability sweep for both readers."""
    recv = fs.load_receiver("F1")
    comp = fs.load_comparator("F1")
    # Parse trace level and restrict to test split (the comparator covers test only).
    for df in (recv, comp):
        df["trace_level"] = df["trial_id"].map(lambda t: fs.parse_trial_id(t).get("trace_level"))
    recv_t = recv[recv["world_id"].isin(fs.TEST_WORLDS)]
    comp_t = comp[comp["world_id"].isin(fs.TEST_WORLDS)]

    levels = [1, 3, 5, 6]
    fa_pts, ca_pts = [], []
    for level in levels:
        sub_c = comp_t[comp_t["trace_level"] == level]
        sub_r = recv_t[recv_t["trace_level"] == level]
        fa_pts.append(fs.summarize_accuracy(sub_c["predicted_regime_comparator"] == sub_c["true_regime"]))
        ca_pts.append(fs.summarize_accuracy(sub_r["predicted_regime"] == sub_r["true_regime"]))

    xs = np.arange(len(levels))
    fa_vals = [r.accuracy for r in fa_pts]
    ca_vals = [r.accuracy for r in ca_pts]
    fa_lo = [r.ci_lo for r in fa_pts]
    fa_hi = [r.ci_hi for r in fa_pts]
    ca_lo = [r.ci_lo for r in ca_pts]
    ca_hi = [r.ci_hi for r in ca_pts]

    fa_colour = fs.READER_COLOR["form_aligned"]
    ca_colour = fs.READER_COLOR["content_attentive"]

    ax.errorbar(xs, fa_vals,
                yerr=[np.array(fa_vals) - np.array(fa_lo), np.array(fa_hi) - np.array(fa_vals)],
                fmt="o-", color=fa_colour, ecolor=fa_colour, capsize=2.5,
                linewidth=1.2, markersize=5,
                label=fs.READER_LABEL["form_aligned"])
    ax.errorbar(xs, ca_vals,
                yerr=[np.array(ca_vals) - np.array(ca_lo), np.array(ca_hi) - np.array(ca_vals)],
                fmt="s-", color=ca_colour, ecolor=ca_colour, capsize=2.5,
                linewidth=1.2, markersize=5,
                label=fs.READER_LABEL["content_attentive"])

    # Reference line at form-aligned L1.
    fa_l1 = fa_vals[0]
    ax.axhline(fa_l1, color=fa_colour, linestyle=(0, (3, 2)), linewidth=0.7, alpha=0.6)
    ax.text(0.05, fa_l1 + 0.015,
            f"Form-aligned L1 ({fa_l1 * 100:.1f}%)",
            fontsize=6, color=fa_colour, ha="left", va="bottom", style="italic")

    ax.set_xticks(xs)
    ax.set_xticklabels([f"L{level}" for level in levels])
    ax.set_xlabel("Trace observability level")
    ax.set_ylim(0, 0.85)
    ax.set_yticks(np.arange(0, 0.81, 0.2))
    ax.set_yticklabels([f"{int(t * 100)}%" for t in np.arange(0, 0.81, 0.2)])
    ax.set_ylabel("Test-split accuracy")
    ax.legend(loc="upper left", frameon=False, fontsize=6.5,
              handlelength=1.5, borderpad=0.3)

    ax.axhline(fs.CHANCE_BASELINE, color=fs.CHANCE_COLOR, linestyle=(0, (3, 2)),
               linewidth=0.6, zorder=0)

    ax.set_title("Trace helps content-attentive readers",
                 fontsize=7.5, pad=4, color="#333333", loc="left",
                 fontweight="bold")


def main() -> None:
    fig = plt.figure(figsize=(fs.WIDTH_DOUBLE_IN, 3.5))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.05, 1.1], wspace=0.55,
                          top=0.82, bottom=0.18, left=0.07, right=0.985)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])

    panel_length_only(ax_a)
    panel_cross_family(ax_b)
    panel_trace(ax_c)

    fs.panel_letter(ax_a, "a", x=-0.22)
    fs.panel_letter(ax_b, "b", x=-0.18)
    fs.panel_letter(ax_c, "c", x=-0.18)

    fs.save_figure(fig, "Figure_4")


if __name__ == "__main__":
    main()
