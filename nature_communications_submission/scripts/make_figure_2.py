"""Figure 2 — The eight production motifs as directed graphs.

A clean 2x4 grid of small panels. Each panel shows the directed call graph for
one motif, with the natural-language motif name as the title and a one-phrase
cue beneath. Muted motif colours are used for the producer nodes so the same
colour identifies the same motif across Figs 2, 3, and 4. A single node-type
legend appears below the grid.
"""

from __future__ import annotations

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

import figure_style as fs

fs.apply_style()


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------
NODE_RADIUS = 4.0  # in cell-internal coordinates (0-100)


def _muted(colour: str, factor: float = 0.55) -> tuple[float, float, float]:
    """Mix a hex colour toward white so the grid reads softly."""
    from matplotlib.colors import to_rgb
    r, g, b = to_rgb(colour)
    return tuple(c + (1.0 - c) * (1 - factor) for c in (r, g, b))


def draw_source(ax, x, y, colour):
    ax.add_patch(mpatches.Circle((x, y), NODE_RADIUS, facecolor=colour,
                                 edgecolor="black", linewidth=0.6, zorder=3))


def draw_hidden(ax, x, y):
    ax.add_patch(mpatches.Circle((x, y), NODE_RADIUS, facecolor="white",
                                 edgecolor="#9C3848", linewidth=1.2,
                                 linestyle=(0, (2, 1)), zorder=3))
    ax.text(x, y - 0.2, "H", ha="center", va="center",
            fontsize=5.5, color="#9C3848", fontweight="bold", zorder=4)


def draw_relay(ax, x, y):
    s = NODE_RADIUS * 1.6
    ax.add_patch(mpatches.Rectangle((x - s / 2, y - s / 2), s, s,
                                    facecolor="#D9D9D9", edgecolor="black",
                                    linewidth=0.6, zorder=3))


def draw_hub(ax, x, y, colour):
    s = NODE_RADIUS * 2.1
    ax.add_patch(mpatches.Rectangle((x - s / 2, y - s / 2), s, s,
                                    facecolor=colour, edgecolor="black",
                                    linewidth=0.7, zorder=3))


def draw_receiver(ax, x, y):
    tri = mpatches.Polygon(
        [(x - 3.5, y - 4), (x - 3.5, y + 4), (x + 4.5, y)],
        closed=True, facecolor="white", edgecolor="black", linewidth=0.7,
        zorder=3,
    )
    ax.add_patch(tri)


def draw_edge(ax, x0, y0, x1, y1, *, colour="#555555"):
    # Shorten the segment a bit so the arrow head lands cleanly on the target
    # rather than burying inside it.
    dx, dy = x1 - x0, y1 - y0
    length = (dx ** 2 + dy ** 2) ** 0.5
    if length == 0:
        return
    shrink = NODE_RADIUS + 1.5
    ux, uy = dx / length, dy / length
    x0s = x0 + ux * shrink
    y0s = y0 + uy * shrink
    x1s = x1 - ux * shrink
    y1s = y1 - uy * shrink
    ax.annotate("", xy=(x1s, y1s), xytext=(x0s, y0s),
                arrowprops=dict(arrowstyle="-|>,head_length=0.35,head_width=0.18",
                                color=colour, linewidth=0.9),
                zorder=2)


# ---------------------------------------------------------------------------
# Per-motif layouts
# ---------------------------------------------------------------------------
def cell_setup(ax, title, cue):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    ax.text(50, 99, title, ha="center", va="top",
            fontsize=7.5, fontweight="bold", color="#1a1a1a")
    ax.text(50, 3, cue, ha="center", va="bottom",
            fontsize=6.5, color="#555555", style="italic")


def draw_single_direct(ax, colour):
    draw_source(ax, 25, 50, colour)
    draw_receiver(ax, 80, 50)
    draw_edge(ax, 25, 50, 80, 50)


def draw_chain_relay(ax, colour):
    xs = [15, 36, 57, 78]
    y = 50
    draw_source(ax, xs[0], y, colour)
    draw_relay(ax, xs[1], y)
    draw_relay(ax, xs[2], y)
    draw_receiver(ax, xs[3], y)
    for a, b in zip(xs, xs[1:]):
        draw_edge(ax, a, y, b, y)


def draw_independent_corroboration(ax, colour):
    xs_src = [22, 22, 22]
    ys_src = [78, 50, 22]
    for x, y in zip(xs_src, ys_src):
        draw_source(ax, x, y, colour)
    draw_receiver(ax, 78, 50)
    for x, y in zip(xs_src, ys_src):
        draw_edge(ax, x, y, 78, 50)


def draw_dependent_repetition(ax, colour):
    # One upstream source -> 3 downstream relayers -> receiver
    src_x, src_y = 16, 50
    relays = [(48, 78), (48, 50), (48, 22)]
    rcvr_x, rcvr_y = 82, 50
    draw_source(ax, src_x, src_y, colour)
    for x, y in relays:
        draw_relay(ax, x, y)
    draw_receiver(ax, rcvr_x, rcvr_y)
    for x, y in relays:
        draw_edge(ax, src_x, src_y, x, y)
        draw_edge(ax, x, y, rcvr_x, rcvr_y)


def draw_common_source_laundering(ax, colour):
    # Hidden source -> 3 relayers -> receiver. The hidden source is dashed/red.
    src_x, src_y = 16, 50
    relays = [(48, 78), (48, 50), (48, 22)]
    rcvr_x, rcvr_y = 82, 50
    draw_hidden(ax, src_x, src_y)
    for x, y in relays:
        draw_relay(ax, x, y)
    draw_receiver(ax, rcvr_x, rcvr_y)
    for x, y in relays:
        draw_edge(ax, src_x, src_y, x, y, colour="#9C3848")
        draw_edge(ax, x, y, rcvr_x, rcvr_y)


def draw_clustered_reinforcement(ax, colour):
    # Four community nodes cross-connected, one edge to receiver.
    nodes = [(28, 72), (50, 80), (50, 36), (28, 28)]
    for x, y in nodes:
        draw_source(ax, x, y, colour)
    rcvr_x, rcvr_y = 82, 54
    draw_receiver(ax, rcvr_x, rcvr_y)
    # Cross-talk within the community.
    pairs = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)]
    for i, j in pairs:
        x0, y0 = nodes[i]
        x1, y1 = nodes[j]
        draw_edge(ax, x0, y0, x1, y1, colour="#888888")
    # The terminal message reaches the receiver from one community member.
    draw_edge(ax, nodes[1][0], nodes[1][1], rcvr_x, rcvr_y)


def draw_centralized_synthesis(ax, colour):
    # Three sources -> hub -> receiver.
    src = [(18, 78), (18, 50), (18, 22)]
    hub_x, hub_y = 50, 50
    for x, y in src:
        draw_source(ax, x, y, colour)
    draw_hub(ax, hub_x, hub_y, colour)
    draw_receiver(ax, 82, 50)
    for x, y in src:
        draw_edge(ax, x, y, hub_x, hub_y)
    draw_edge(ax, hub_x, hub_y, 82, 50)


def draw_compound(ax, colour):
    # Common-source laundering (stage 1) followed by chain relay (stage 2),
    # with a faint vertical divider between the two stages.
    src_x, src_y = 8, 50
    relays = [(28, 78), (28, 50), (28, 22)]
    divider_x = 47
    chain = [(58, 50), (76, 50)]
    rcvr_x, rcvr_y = 92, 50

    # Stage labels along the bottom of the panel.
    ax.text((src_x + relays[0][0]) / 2 + 2, 12, "laundering",
            ha="center", va="center", fontsize=5.5, color="#777777",
            style="italic")
    ax.text((chain[0][0] + chain[1][0]) / 2, 12, "chain",
            ha="center", va="center", fontsize=5.5, color="#777777",
            style="italic")

    # Faint vertical divider between the two stages.
    ax.plot([divider_x, divider_x], [16, 84],
            color="#cccccc", linewidth=0.7, linestyle=(0, (2, 2)), zorder=1)

    draw_hidden(ax, src_x, src_y)
    for x, y in relays:
        draw_relay(ax, x, y)
    for x, y in chain:
        draw_relay(ax, x, y)
    draw_receiver(ax, rcvr_x, rcvr_y)

    # Hidden source to relayers (red edges).
    for x, y in relays:
        draw_edge(ax, src_x, src_y, x, y, colour="#9C3848")
    # All relayers funnel into the first chain node, then linear chain to receiver.
    for x, y in relays:
        draw_edge(ax, x, y, chain[0][0], chain[0][1])
    draw_edge(ax, chain[0][0], chain[0][1], chain[1][0], chain[1][1])
    draw_edge(ax, chain[1][0], chain[1][1], rcvr_x, rcvr_y)


MOTIF_DRAWER = {
    "single_direct": draw_single_direct,
    "chain_relay": draw_chain_relay,
    "independent_corroboration": draw_independent_corroboration,
    "dependent_repetition": draw_dependent_repetition,
    "common_source_laundering": draw_common_source_laundering,
    "clustered_reinforcement": draw_clustered_reinforcement,
    "centralized_synthesis": draw_centralized_synthesis,
    "compound": draw_compound,
}


def main() -> None:
    fig = plt.figure(figsize=(fs.WIDTH_DOUBLE_IN, 4.4))
    gs = fig.add_gridspec(2, 4, wspace=0.10, hspace=0.18,
                          top=0.94, bottom=0.18, left=0.02, right=0.985)

    for idx, motif in enumerate(fs.MOTIFS):
        ax = fig.add_subplot(gs[idx // 4, idx % 4])
        cell_setup(ax, fs.MOTIF_LABEL[motif], fs.MOTIF_CUE[motif])
        colour = _muted(fs.MOTIF_COLOR[motif], factor=0.55)
        MOTIF_DRAWER[motif](ax, colour)

    # Node-type legend; motif colour is encoded by source-node fill.
    legend_handles = [
        Line2D([0], [0], marker="o", linestyle="", markersize=7.5,
               markerfacecolor="#cccccc", markeredgecolor="black",
               markeredgewidth=0.6, label="Source (motif color)"),
        Line2D([0], [0], marker="o", linestyle="", markersize=7.5,
               markerfacecolor="white", markeredgecolor="#9C3848",
               markeredgewidth=1.2, label="Hidden source"),
        Line2D([0], [0], marker="s", linestyle="", markersize=7.5,
               markerfacecolor="#D9D9D9", markeredgecolor="black",
               markeredgewidth=0.6, label="Relayer"),
        Line2D([0], [0], marker="s", linestyle="", markersize=10,
               markerfacecolor="#cccccc", markeredgecolor="black",
               markeredgewidth=0.7, label="Hub synthesizer"),
        Line2D([0], [0], marker=">", linestyle="", markersize=8,
               markerfacecolor="white", markeredgecolor="black",
               markeredgewidth=0.7, label="Receiver"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=5,
               frameon=False, fontsize=7, bbox_to_anchor=(0.5, 0.025),
               columnspacing=2.0, handletextpad=0.5)
    fig.text(0.5, 0.005,
             "Source-node color identifies motif.",
             ha="center", va="bottom", fontsize=6, color="#555555",
             style="italic")

    fs.save_figure(fig, "Figure_2")


if __name__ == "__main__":
    main()
