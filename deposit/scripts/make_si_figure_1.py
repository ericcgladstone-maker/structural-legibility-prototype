"""Supplementary Figure 1 — Aggregate motif-class recovery by reader type and family.

Four bars in two reader-pair groups (form-aligned, content-attentive), each
with F1 (primary, qwen2.5:7b) and F2 (cross-family, llama3.1:8b) test-split
accuracies. Chance baseline shown as a horizontal dashed line at 12.5%.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import figure_style as fs

fs.apply_style()


def compute_bars():
    recv1 = fs.load_receiver("F1")
    recv2 = fs.load_receiver("F2")
    comp1 = fs.load_comparator("F1")
    comp2 = fs.load_comparator("F2")

    def acc(df, pred_col):
        sub = df[df["world_id"].isin(fs.TEST_WORLDS)]
        return fs.summarize_accuracy(sub[pred_col] == sub["true_regime"])

    return {
        "form_aligned_F1": acc(comp1, "predicted_regime_comparator"),
        "form_aligned_F2": acc(comp2, "predicted_regime_comparator"),
        "content_attentive_F1": acc(recv1, "predicted_regime"),
        "content_attentive_F2": acc(recv2, "predicted_regime"),
    }


def main() -> None:
    results = compute_bars()

    # Bar layout: two groups of two bars; form-aligned on the left, content-attentive on the right.
    group_centres = np.array([0.0, 1.7])
    intra = 0.35
    positions = [
        group_centres[0] - intra / 2, group_centres[0] + intra / 2,
        group_centres[1] - intra / 2, group_centres[1] + intra / 2,
    ]
    bar_keys = ["form_aligned_F1", "form_aligned_F2", "content_attentive_F1", "content_attentive_F2"]
    values = [results[k].accuracy for k in bar_keys]
    ci_lo = [results[k].ci_lo for k in bar_keys]
    ci_hi = [results[k].ci_hi for k in bar_keys]
    ns = [results[k].n for k in bar_keys]
    err_lower = [v - lo for v, lo in zip(values, ci_lo)]
    err_upper = [hi - v for v, hi in zip(values, ci_hi)]
    fa_colour = fs.READER_COLOR["form_aligned"]
    ca_colour = fs.READER_COLOR["content_attentive"]
    colours = [fa_colour, fa_colour, ca_colour, ca_colour]
    # F2 distinguished by lighter / hatched: use open fill (no facecolor) with edge.
    facecolours = [fa_colour, "white", ca_colour, "white"]
    hatches = [None, "////", None, "////"]
    edgecolours = colours
    family_labels = ["F1", "F2", "F1", "F2"]

    fig, ax = plt.subplots(figsize=(fs.WIDTH_SINGLE_IN, 2.1))
    bars = ax.bar(
        positions, values, width=intra * 0.9,
        color=facecolours, edgecolor=edgecolours, linewidth=0.9,
        hatch=hatches[0],  # set per-bar below
    )
    for bar, hatch in zip(bars, hatches):
        if hatch:
            bar.set_hatch(hatch)
    ax.errorbar(
        positions, values,
        yerr=[err_lower, err_upper],
        fmt="none", ecolor="black", elinewidth=0.7, capsize=2.0,
    )

    # Chance baseline.
    ax.axhline(fs.CHANCE_BASELINE, color=fs.CHANCE_COLOR, linestyle=(0, (3, 2)), linewidth=0.7, zorder=0)
    ax.text(group_centres[1] - 0.7, fs.CHANCE_BASELINE + 0.008,
            "Chance (12.5%)", fontsize=6, color=fs.CHANCE_COLOR, ha="left", va="bottom")

    # Value annotations above each bar.
    for x, v, n in zip(positions, values, ns):
        ax.text(x, v + 0.025 + max(err_upper), f"{v * 100:.1f}%",
                ha="center", va="bottom", fontsize=6.5, color="black")
        ax.text(x, -0.04, f"n={n}", ha="center", va="top", fontsize=6, color="#555555")

    # Group labels under each pair.
    ax.text(group_centres[0], -0.10, fs.READER_LABEL["form_aligned"],
            ha="center", va="top", fontsize=7.5, fontweight="bold")
    ax.text(group_centres[1], -0.10, fs.READER_LABEL["content_attentive"],
            ha="center", va="top", fontsize=7.5, fontweight="bold")

    # Family labels inside bars (small).
    for x, fam in zip(positions, family_labels):
        ax.text(x, 0.012, fam, ha="center", va="bottom", fontsize=6, color="white" if fam == "F1" else "#333333")

    ax.set_xticks([])
    ax.set_ylim(0, 0.85)
    ax.set_yticks(np.arange(0, 0.81, 0.2))
    ax.set_yticklabels([f"{int(t * 100)}%" for t in np.arange(0, 0.81, 0.2)])
    ax.set_ylabel("Top-1 accuracy on eight-way task")
    ax.set_xlim(-0.6, group_centres[1] + 0.6)

    # Subtle legend explaining F1 / F2 hatch convention.
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor="#666666", edgecolor="#666666", label="F1 (primary)"),
        plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="#666666", hatch="////", label="F2 (cross-family)"),
    ]
    ax.legend(
        handles=legend_elements, loc="upper right", frameon=False,
        fontsize=6, handlelength=1.4, handleheight=1.0,
    )

    fs.save_figure(fig, "Supplementary_Figure_1", supplementary=True)


if __name__ == "__main__":
    main()
