"""Figure 1 — The inverse problem and message residue.

Panel a: two-row schematic.
   top row    = Forward production: World -> Production graph -> Terminal message + trace.
   bottom row = Inverse inference: Terminal message + trace -> Reader instrument
                -> Posterior over motif class.

Panel b: three residue classes (semantic, formal, trace) annotated directly on a
schematic placeholder message; two reader icons mark which channels each
instrument reads.

Panel c: scope text block (recovered vs not recovered).

Residue-class colours only.
"""

from __future__ import annotations

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

import figure_style as fs

fs.apply_style()

FORWARD_COLOUR = "#4F6D7A"
INVERSE_COLOUR = "#9C3848"


def add_box(ax, x, y, w, h, label, *, facecolor="#EEF1F4",
            edgecolor="#444444", fontsize=7, fontweight="normal"):
    box = mpatches.FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.5",
        linewidth=0.8, edgecolor=edgecolor, facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color="#1a1a1a")


def add_arrow(ax, x0, y0, x1, y1, *, color="#444444", linewidth=1.1,
              linestyle="-"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>,head_length=0.36,head_width=0.22",
                                color=color, linewidth=linewidth,
                                linestyle=linestyle))


# ---------------------------------------------------------------------------
# Panel a: two-row schematic
# ---------------------------------------------------------------------------
def panel_schematic(ax) -> None:
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()

    box_w = 17
    box_h = 12

    # Top row centres: World, Production graph, Terminal message + trace.
    top_y = 76
    top_xs = [16, 50, 84]
    top_labels = [
        "World\n$W$",
        "Production\ngraph $G$",
        "Terminal message $M$\n+ trace $T$",
    ]
    top_faces = ["#EEF1F4", "#EEF1F4", "#F8EFE4"]
    for x, label, fc in zip(top_xs, top_labels, top_faces):
        add_box(ax, x, top_y, box_w, box_h, label, facecolor=fc)
    for i in range(2):
        add_arrow(ax, top_xs[i] + box_w / 2 + 0.4, top_y,
                  top_xs[i + 1] - box_w / 2 - 0.4, top_y,
                  color=FORWARD_COLOUR)
    ax.text(2, top_y + box_h / 2 + 5,
            "Forward production",
            ha="left", va="bottom", fontsize=8, fontweight="bold",
            color=FORWARD_COLOUR)

    # Bottom row centres: M + trace, Reader, Posterior.
    bot_y = 26
    bot_xs = [16, 50, 84]
    bot_labels = [
        "Terminal message $M$\n+ trace $T$",
        "Reader\ninstrument",
        "Posterior\nover $C(G)$",
    ]
    bot_faces = ["#F8EFE4", "#EEF1F4", "#EEF1F4"]
    for x, label, fc in zip(bot_xs, bot_labels, bot_faces):
        add_box(ax, x, bot_y, box_w, box_h, label, facecolor=fc)
    for i in range(2):
        add_arrow(ax, bot_xs[i] + box_w / 2 + 0.4, bot_y,
                  bot_xs[i + 1] - box_w / 2 - 0.4, bot_y,
                  color=INVERSE_COLOUR)
    ax.text(2, bot_y + box_h / 2 + 5,
            "Inverse inference",
            ha="left", va="bottom", fontsize=8, fontweight="bold",
            color=INVERSE_COLOUR)

    # The two orange boxes are the same artifact. A small italic label between
    # the rows says so directly, without a long curved connector.
    ax.text(50, 51, "same artifact",
            ha="center", va="center", fontsize=6.5,
            color="#666666", style="italic")


# ---------------------------------------------------------------------------
# Panel b: residue classes
# ---------------------------------------------------------------------------
def panel_residue(ax) -> None:
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()

    # Message card.
    card = mpatches.FancyBboxPatch(
        (4, 14), 60, 78,
        boxstyle="round,pad=0.02,rounding_size=0.6",
        linewidth=0.8, edgecolor="#444444", facecolor="white",
    )
    ax.add_patch(card)
    ax.text(34, 88, "Terminal message", ha="center", va="top",
            fontsize=6, color="#555555", style="italic")

    # Highlight bands with inline labels at the right end of each band.
    bands = [
        (75, 8, "Semantic", "semantic",
         "Source A reports event X."),
        (54, 16, "Formal", "formal",
         "Bullet structure, hedges,\nlength, lexical variety"),
        (29, 14, "Trace", "trace",
         "Reliability: A-1\nPath: source > liaison > analyst"),
    ]
    for centre, height, label, key, body in bands:
        colour = fs.RESIDUE_COLOR[key]
        ax.add_patch(mpatches.Rectangle(
            (7, centre - height / 2), 54, height,
            facecolor=colour, alpha=0.16, linewidth=0))
        # Tag the band on its left edge.
        ax.add_patch(mpatches.Rectangle(
            (7, centre - height / 2), 1.3, height,
            facecolor=colour, alpha=0.85, linewidth=0))
        ax.text(10, centre, body,
                ha="left", va="center", fontsize=6.5, color=colour,
                fontweight="medium", linespacing=1.3)
        ax.text(62, centre, label,
                ha="left", va="center", fontsize=6.5, color=colour,
                fontweight="bold")

    # Two reader instruments, pulled closer to the residue bands.
    reader_left = 70
    reader_w = 22
    reader_x = reader_left + reader_w / 2
    ca = mpatches.FancyBboxPatch(
        (reader_left, 64), reader_w, 22,
        boxstyle="round,pad=0.02,rounding_size=0.4",
        linewidth=0.8, edgecolor=fs.READER_COLOR["content_attentive"],
        facecolor="white",
    )
    ax.add_patch(ca)
    ax.text(reader_x, 80, "Content-attentive\nreader",
            ha="center", va="center", fontsize=6.5,
            color=fs.READER_COLOR["content_attentive"], fontweight="bold")
    ax.text(reader_x, 70, "uses semantic + trace",
            ha="center", va="center", fontsize=5.5, color="#333333")

    fa = mpatches.FancyBboxPatch(
        (reader_left, 20), reader_w, 22,
        boxstyle="round,pad=0.02,rounding_size=0.4",
        linewidth=0.8, edgecolor=fs.READER_COLOR["form_aligned"],
        facecolor="white",
    )
    ax.add_patch(fa)
    ax.text(reader_x, 36, "Form-aligned\nclassifier",
            ha="center", va="center", fontsize=6.5,
            color=fs.READER_COLOR["form_aligned"], fontweight="bold")
    ax.text(reader_x, 26, "uses formal only",
            ha="center", va="center", fontsize=5.5, color="#333333")


# ---------------------------------------------------------------------------
# Panel c: scope
# ---------------------------------------------------------------------------
def panel_scope(ax) -> None:
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_axis_off()
    box = mpatches.FancyBboxPatch(
        (5, 10), 90, 80,
        boxstyle="round,pad=0.02,rounding_size=0.6",
        linewidth=0.8, edgecolor="#777777", facecolor="#FAFAFA",
    )
    ax.add_patch(box)
    ax.text(50, 80, "Scope of the inverse problem",
            ha="center", va="center", fontsize=8, fontweight="bold",
            color="#333333")
    ax.text(50, 55,
            "Recovered: the motif class $C(G)$,\n"
            "the kind of production graph that\n"
            "generated the message.",
            ha="center", va="center", fontsize=7,
            color=FORWARD_COLOUR, linespacing=1.45)
    ax.text(50, 24,
            "Not recovered: actor identities,\n"
            "the full graph $G$, the truth of $M$.",
            ha="center", va="center", fontsize=7,
            color=INVERSE_COLOUR, linespacing=1.45)


def main() -> None:
    fig = plt.figure(figsize=(fs.WIDTH_DOUBLE_IN, 4.4))
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[1.0, 1.0],
        width_ratios=[1.55, 1.0],
        wspace=0.10, hspace=0.18,
        top=0.965, bottom=0.04, left=0.025, right=0.985,
    )
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])

    panel_schematic(ax_a)
    panel_residue(ax_b)
    panel_scope(ax_c)

    fs.panel_letter(ax_a, "a", x=0.005, y=0.96)
    fs.panel_letter(ax_b, "b", x=0.005, y=0.96)
    fs.panel_letter(ax_c, "c", x=0.005, y=0.96)

    fs.save_figure(fig, "Figure_1")


if __name__ == "__main__":
    main()
