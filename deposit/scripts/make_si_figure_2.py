"""Supplementary Figure 2 — Row-normalized confusion matrices for both readers.

Two side-by-side 8x8 matrices on the F1 test split (n = 840). Each row is the
true motif, each column the predicted motif, and the matrix is row-normalized
so cells read as conditional probabilities. Raw counts are annotated inside
the cells. The Shannon entropy of the predicted-label distribution is shown
beneath each matrix as a single number, quantifying vocabulary collapse.
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import figure_style as fs

fs.apply_style()


def confusion(df: pd.DataFrame, pred_col: str) -> tuple[np.ndarray, np.ndarray]:
    """Return (row-normalized matrix, raw counts) over fs.MOTIFS."""
    counts = np.zeros((len(fs.MOTIFS), len(fs.MOTIFS)), dtype=int)
    motif_to_idx = {m: i for i, m in enumerate(fs.MOTIFS)}
    for true, pred in zip(df["true_regime"], df[pred_col]):
        if true in motif_to_idx and pred in motif_to_idx:
            counts[motif_to_idx[true], motif_to_idx[pred]] += 1
    row_sums = counts.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    normalised = counts / row_sums
    return normalised, counts


def predicted_label_entropy(counts: np.ndarray) -> float:
    """Shannon entropy of the marginal distribution over predicted labels (bits)."""
    col_sums = counts.sum(axis=0).astype(float)
    total = col_sums.sum()
    if total == 0:
        return 0.0
    p = col_sums / total
    nonzero = p[p > 0]
    return float(-np.sum(nonzero * np.log2(nonzero)))


CM_LABEL: dict[str, str] = {
    "single_direct": "Single direct",
    "chain_relay": "Chain relay",
    "independent_corroboration": "Indep. corroboration",
    "dependent_repetition": "Dep. repetition",
    "common_source_laundering": "CS laundering",
    "clustered_reinforcement": "Clust. reinforcement",
    "centralized_synthesis": "Cent. synthesis",
    "compound": "Compound",
}


def draw_matrix(ax, mat: np.ndarray, counts: np.ndarray, title: str) -> None:
    n = len(fs.MOTIFS)
    im = ax.imshow(mat, cmap="viridis", vmin=0.0, vmax=1.0, aspect="equal")

    # Diagonal outlines: red so they read on both ends of viridis.
    for i in range(n):
        rect = plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False,
                             edgecolor="#E63946", linewidth=1.0)
        ax.add_patch(rect)

    # Cell-count annotations.
    for i in range(n):
        for j in range(n):
            c = counts[i, j]
            if c == 0:
                continue
            colour = "white" if mat[i, j] < 0.55 else "black"
            ax.text(j, i, str(c), ha="center", va="center",
                    fontsize=5.5, color=colour)

    labels = [CM_LABEL[m] for m in fs.MOTIFS]
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(labels, rotation=35, ha="right",
                       rotation_mode="anchor", fontsize=6)
    ax.set_yticklabels(labels, fontsize=6)
    ax.set_xlabel("Predicted motif")
    ax.set_ylabel("True motif")
    ax.set_title(title, fontsize=8, pad=4, loc="left")

    # Hide the default spines for a cleaner heatmap.
    for s in ax.spines.values():
        s.set_visible(False)

    return im


def main() -> None:
    recv = fs.load_receiver("F1")
    comp = fs.load_comparator("F1")
    recv_t = recv[recv["world_id"].isin(fs.TEST_WORLDS)]
    comp_t = comp[comp["world_id"].isin(fs.TEST_WORLDS)]

    ca_norm, ca_counts = confusion(recv_t, "predicted_regime")
    fa_norm, fa_counts = confusion(comp_t, "predicted_regime_comparator")

    ca_entropy = predicted_label_entropy(ca_counts)
    fa_entropy = predicted_label_entropy(fa_counts)
    max_entropy = math.log2(len(fs.MOTIFS))

    fig = plt.figure(figsize=(fs.WIDTH_DOUBLE_IN, 4.6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.0, 0.04], wspace=0.7,
                          top=0.88, bottom=0.28, left=0.10, right=0.93)
    ax_ca = fig.add_subplot(gs[0, 0])
    ax_fa = fig.add_subplot(gs[0, 1])
    cbar_ax = fig.add_subplot(gs[0, 2])

    draw_matrix(ax_ca, ca_norm, ca_counts,
                f"{fs.READER_LABEL['content_attentive']} (qwen2.5:7b)")
    im = draw_matrix(ax_fa, fa_norm, fa_counts,
                     f"{fs.READER_LABEL['form_aligned']} (14-feature)")

    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label("Conditional probability (row-normalized)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)

    # Entropy annotations below each matrix.
    fig.text(0.27, 0.18,
             f"Predicted-label entropy: {ca_entropy:.2f} bits "
             f"(maximum at 8 classes = {max_entropy:.2f} bits)",
             fontsize=6.5, ha="center", color="#333333")
    fig.text(0.70, 0.18,
             f"Predicted-label entropy: {fa_entropy:.2f} bits "
             f"(maximum at 8 classes = {max_entropy:.2f} bits)",
             fontsize=6.5, ha="center", color="#333333")

    fs.panel_letter(ax_ca, "a", x=-0.22)
    fs.panel_letter(ax_fa, "b", x=-0.22)

    fs.save_figure(fig, "Supplementary_Figure_2", supplementary=True)


if __name__ == "__main__":
    main()
