"""Figure 3 — Recoverability by motif and reader-instrument alignment.

Panel a: 2D alignment scatter, content-attentive accuracy (x) vs form-aligned
accuracy (y), one labelled point per motif with Wilson 95% CI crosses, diagonal
reference. Motif colours.

Panel b: Paired bars per motif, sorted by form-aligned accuracy. Reader-pair
colours (form-aligned vs content-attentive), Wilson 95% CI whiskers, exact
percentages annotated, chance baseline.

Boundary cases (compound, common-source laundering) are annotated directly on
Panel a, replacing a separate annotation strip.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import figure_style as fs

fs.apply_style()


def collect_results():
    recv = fs.load_receiver("F1")
    comp = fs.load_comparator("F1")
    recv_test = recv[recv["world_id"].isin(fs.TEST_WORLDS)]
    comp_test = comp[comp["world_id"].isin(fs.TEST_WORLDS)]
    llm = fs.per_motif_accuracy(recv_test, pred_col="predicted_regime")
    fa = fs.per_motif_accuracy(comp_test, pred_col="predicted_regime_comparator")
    return llm, fa


# Label placement per motif for the scatter (offset from the data point, in
# axes-data units, with anchor description).  Kept centralised so we can iterate.
SCATTER_LABEL: dict[str, str] = {
    "single_direct": "Single direct",
    "chain_relay": "Chain relay",
    "independent_corroboration": "Independent corroboration",
    "dependent_repetition": "Dependent repetition",
    "common_source_laundering": "Common-source laundering",
    "clustered_reinforcement": "Clustered reinforcement",
    "centralized_synthesis": "Centralized synthesis",
    "compound": "Compound",
}

# Manual offsets to keep the five low-x motifs vertically spaced near the y-axis.
SCATTER_LABEL_OFFSET: dict[str, tuple[float, float, str, str]] = {
    # dx, dy, horizontalalignment, verticalalignment relative to the point
    "single_direct": (-4.0, 0.0, "right", "center"),
    "chain_relay": (4.5, -4.5, "left", "top"),
    "independent_corroboration": (4.5, -3.5, "left", "top"),
    "dependent_repetition": (5.0, -3.5, "left", "top"),
    "common_source_laundering": (5.0, 0.0, "left", "center"),
    "clustered_reinforcement": (5.0, 8.0, "left", "bottom"),
    "centralized_synthesis": (5.0, -8.0, "left", "top"),
    "compound": (5.0, -1.5, "left", "top"),
}


def panel_scatter(ax, llm, fa) -> None:
    # Reference diagonal.
    ax.plot([0, 100], [0, 100], color="#BBBBBB", linestyle=(0, (3, 2)),
            linewidth=0.7, zorder=0)

    # Region annotations: very faint, smaller, italic.
    ax.text(3, 97, "form-aligned advantage", color="#BBBBBB", fontsize=5.5,
            ha="left", va="top", style="italic")
    ax.text(97, 3, "semantic-aligned advantage", color="#BBBBBB", fontsize=5.5,
            ha="right", va="bottom", style="italic")

    # Plot each motif.
    for motif in fs.MOTIFS:
        x = llm[motif].accuracy * 100
        y = fa[motif].accuracy * 100
        x_lo = llm[motif].ci_lo * 100
        x_hi = llm[motif].ci_hi * 100
        y_lo = fa[motif].ci_lo * 100
        y_hi = fa[motif].ci_hi * 100
        colour = fs.MOTIF_COLOR[motif]
        # CI cross (horizontal + vertical).
        ax.plot([x_lo, x_hi], [y, y], color=colour, linewidth=0.8, alpha=0.8, zorder=1)
        ax.plot([x, x], [y_lo, y_hi], color=colour, linewidth=0.8, alpha=0.8, zorder=1)
        # Point: motif colour with dark stroke.
        ax.scatter([x], [y], s=48, color=colour, edgecolor="black",
                   linewidth=0.7, zorder=3)
        # Label: black for legibility against any motif colour.
        dx, dy, ha, va = SCATTER_LABEL_OFFSET[motif]
        ax.text(x + dx, y + dy, SCATTER_LABEL[motif],
                color="#1a1a1a", fontsize=6.5, ha=ha, va=va, zorder=4)

    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect("equal")
    ax.set_xlabel("Content-attentive reader accuracy (%)")
    ax.set_ylabel("Form-aligned classifier accuracy (%)")
    ax.set_xticks(np.arange(0, 101, 20))
    ax.set_yticks(np.arange(0, 101, 20))
    ax.grid(False)


def panel_bars(ax, llm, fa) -> None:
    # Sort motifs by form-aligned accuracy, descending; failure case (compound) at the right.
    order = sorted(fs.MOTIFS, key=lambda m: -fa[m].accuracy)

    x_centres = np.arange(len(order))
    intra = 0.34
    fa_xs = x_centres - intra / 2
    llm_xs = x_centres + intra / 2

    fa_vals = np.array([fa[m].accuracy for m in order])
    llm_vals = np.array([llm[m].accuracy for m in order])
    fa_lo = np.array([fa[m].ci_lo for m in order])
    fa_hi = np.array([fa[m].ci_hi for m in order])
    llm_lo = np.array([llm[m].ci_lo for m in order])
    llm_hi = np.array([llm[m].ci_hi for m in order])

    fa_colour = fs.READER_COLOR["form_aligned"]
    ca_colour = fs.READER_COLOR["content_attentive"]

    ax.bar(fa_xs, fa_vals, width=intra * 0.9,
           color=fa_colour, edgecolor=fa_colour, linewidth=0.6,
           label=fs.READER_LABEL["form_aligned"])
    ax.bar(llm_xs, llm_vals, width=intra * 0.9,
           color=ca_colour, edgecolor=ca_colour, linewidth=0.6,
           label=fs.READER_LABEL["content_attentive"])
    ax.errorbar(fa_xs, fa_vals, yerr=[fa_vals - fa_lo, fa_hi - fa_vals],
                fmt="none", ecolor="black", elinewidth=0.5, capsize=1.5)
    ax.errorbar(llm_xs, llm_vals, yerr=[llm_vals - llm_lo, llm_hi - llm_vals],
                fmt="none", ecolor="black", elinewidth=0.5, capsize=1.5)

    # Above-bar percentages. Skip the label on zero-height bars to keep the
    # baseline uncluttered. Substantive zero results remain in the caption.
    for x, v in zip(fa_xs, fa_vals):
        if v < 0.005:
            continue
        ax.text(x, v + 0.025, f"{v * 100:.0f}", ha="center", va="bottom",
                fontsize=5.5, color=fa_colour)
    for x, v in zip(llm_xs, llm_vals):
        if v < 0.005:
            continue
        ax.text(x, v + 0.025, f"{v * 100:.0f}", ha="center", va="bottom",
                fontsize=5.5, color=ca_colour)

    # Chance baseline.
    ax.axhline(fs.CHANCE_BASELINE, color=fs.CHANCE_COLOR, linestyle=(0, (3, 2)),
               linewidth=0.6, zorder=0)
    ax.text(len(order) - 0.5, fs.CHANCE_BASELINE + 0.012, "Chance",
            fontsize=5.5, color=fs.CHANCE_COLOR, ha="right", va="bottom")

    # Small coloured motif ticks under x-axis (the visual link to Panel a colours).
    for x, m in zip(x_centres, order):
        ax.plot([x], [-0.035], marker="s", markersize=4.5,
                markeredgecolor="black", markeredgewidth=0.4,
                color=fs.MOTIF_COLOR[m], clip_on=False, zorder=5)

    # Even-shorter bar-axis labels for the print-size width. Abbreviations are
    # defined in the manuscript's Figure 3 caption.
    bar_label = {
        "single_direct": "Single",
        "chain_relay": "Chain",
        "independent_corroboration": "Indep. corrob.",
        "dependent_repetition": "Dep. rep.",
        "common_source_laundering": "CS launder",
        "clustered_reinforcement": "Cluster",
        "centralized_synthesis": "Cent. synth.",
        "compound": "Compound",
    }
    ax.set_xticks(x_centres)
    ax.set_xticklabels([bar_label[m] for m in order],
                       fontsize=6, rotation=32, ha="right",
                       rotation_mode="anchor")
    ax.set_ylim(0, 1.10)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_yticklabels([f"{int(t * 100)}%" for t in np.arange(0, 1.01, 0.2)])
    ax.set_ylabel("Top-1 accuracy on eight-way task")
    # Legend below the panel rather than upper-right (which collided with the
    # 95% single-direct content-attentive bar).
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.35),
              frameon=False, fontsize=6.5, ncol=2,
              handlelength=1.4, handleheight=1.0, borderpad=0.3,
              columnspacing=1.4)


def main() -> None:
    llm, fa = collect_results()

    fig = plt.figure(figsize=(fs.WIDTH_DOUBLE_IN, 3.7))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.6], wspace=0.32,
                          top=0.95, bottom=0.22, left=0.07, right=0.985)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    panel_scatter(ax_a, llm, fa)
    panel_bars(ax_b, llm, fa)
    fs.panel_letter(ax_a, "a", x=-0.18)
    fs.panel_letter(ax_b, "b", x=-0.08)

    fs.save_figure(fig, "Figure_3")


if __name__ == "__main__":
    main()
