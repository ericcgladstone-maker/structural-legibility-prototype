"""Supplementary Figure 3 — Content-attentive reader confidence is decoupled
from ground-truth message preservation.

Scatter of the LLM's stated fidelity posterior (y) versus the ground-truth
proposition-preservation rate (x), across all n = 4,197 post-validation F1
trials. A faint y = x reference line marks where a calibrated reader would
sit. Marginal histograms summarise the per-axis distributions. The Pearson
correlation and the two means are annotated, reproducing the manuscript's
r = +0.029 result.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import figure_style as fs

fs.apply_style()


def collect_scatter_data() -> pd.DataFrame:
    """Join receiver fidelity posterior with terminal-features preservation."""
    recv = fs.load_receiver("F1")  # already invalid-filtered, joined to ground_truth
    feats = fs.load_terminal_features("F1")
    joined = recv.merge(
        feats[["cell_id", "world_id", "replicate_index", "true_accuracy_score"]]
            .rename(columns={"true_accuracy_score": "preservation_rate"}),
        on=["cell_id", "world_id", "replicate_index"],
        how="inner",
    )
    joined = joined.dropna(subset=["accuracy_probability", "preservation_rate"])
    return joined


def main() -> None:
    df = collect_scatter_data()
    n = len(df)
    x = df["preservation_rate"].to_numpy(dtype=float)
    y = df["accuracy_probability"].to_numpy(dtype=float)
    pearson_r = float(np.corrcoef(x, y)[0, 1])
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    print(f"n = {n}, Pearson r = {pearson_r:.4f}, mean(x) = {x_mean:.4f}, mean(y) = {y_mean:.4f}")

    ca_colour = fs.READER_COLOR["content_attentive"]

    fig = plt.figure(figsize=(fs.WIDTH_SINGLE_IN * 1.15, 3.2))
    gs = fig.add_gridspec(
        2, 2, width_ratios=[5, 1], height_ratios=[1, 5],
        wspace=0.05, hspace=0.05,
        top=0.93, bottom=0.13, left=0.16, right=0.95,
    )
    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)

    # Small uniform jitter on both axes to spread the discrete LLM probability levels.
    rng = np.random.default_rng(0)
    jitter = 0.018
    x_j = x + rng.uniform(-jitter, jitter, size=x.shape)
    y_j = y + rng.uniform(-jitter, jitter, size=y.shape)
    ax_main.scatter(x_j, y_j, s=5, color=ca_colour, alpha=0.18,
                    edgecolor="none", rasterized=True)
    # Reference y = x (perfect calibration of fidelity posterior to preservation).
    ax_main.plot([0, 1], [0, 1], linestyle=(0, (3, 2)), color="#999999",
                 linewidth=0.7)

    # Crosshair at the joint means.
    ax_main.axvline(x_mean, color="#222222", linewidth=0.5, alpha=0.55)
    ax_main.axhline(y_mean, color="#222222", linewidth=0.5, alpha=0.55)
    ax_main.scatter([x_mean], [y_mean], s=42, color="black", zorder=5,
                    marker="x", linewidths=1.3)

    ax_main.text(0.04, 0.96,
                 f"Pearson r = {pearson_r:+.3f}\nn = {n}",
                 transform=ax_main.transAxes,
                 fontsize=7, color="#222222", ha="left", va="top",
                 bbox=dict(boxstyle="round,pad=0.25",
                           facecolor="white", edgecolor="#cccccc", linewidth=0.5))
    # Mean labels placed inside the plot, anchored from the crosshair.
    ax_main.text(x_mean - 0.012, 0.03,
                 f"mean preservation = {x_mean:.2f}",
                 fontsize=6, color="#333333", ha="right", va="bottom")
    ax_main.text(0.04, y_mean - 0.015,
                 f"mean fidelity belief = {y_mean:.2f}",
                 fontsize=6, color="#333333", ha="left", va="top")

    ax_main.set_xlim(0, 1.02)
    ax_main.set_ylim(0, 1.02)
    ax_main.set_xlabel("Ground-truth message preservation rate")
    ax_main.set_ylabel("Stated fidelity posterior (LLM)")
    ax_main.set_xticks(np.arange(0, 1.01, 0.2))
    ax_main.set_yticks(np.arange(0, 1.01, 0.2))

    # Marginal histograms.
    bins = np.linspace(0, 1, 31)
    ax_top.hist(x, bins=bins, color="#666666", edgecolor="none", alpha=0.75)
    ax_top.set_yticks([])
    ax_top.spines["left"].set_visible(False)
    plt.setp(ax_top.get_xticklabels(), visible=False)
    plt.setp(ax_top.get_xticklines(), visible=False)

    ax_right.hist(y, bins=bins, orientation="horizontal",
                  color=ca_colour, edgecolor="none", alpha=0.75)
    ax_right.set_xticks([])
    ax_right.spines["bottom"].set_visible(False)
    plt.setp(ax_right.get_yticklabels(), visible=False)
    plt.setp(ax_right.get_yticklines(), visible=False)

    fig.suptitle("Fidelity posterior is decoupled from source-content preservation",
                 fontsize=8, x=0.16, y=0.985, ha="left")

    fs.save_figure(fig, "Supplementary_Figure_3", supplementary=True)


if __name__ == "__main__":
    main()
