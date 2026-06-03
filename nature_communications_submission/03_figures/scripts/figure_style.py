"""Shared style and data loaders for the Nature Communications figure set.

Every figure script imports from this module so colours, fonts, motif order,
and data-loading conventions stay consistent across Figs 1-4 and SI 1-3.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# scripts/ -> 03_figures/ -> Nature Communications Submission/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "prototype" / "outputs"
FIGURES_DIR = PROJECT_ROOT / "Nature Communications Submission" / "03_figures"
MAIN_FIGURES_DIR = FIGURES_DIR / "main"
SI_FIGURES_DIR = (
    PROJECT_ROOT / "Nature Communications Submission"
    / "05_supplementary_information" / "figures"
)

# ---------------------------------------------------------------------------
# Motif canonical order + display labels + Fig-2 cue phrases
# ---------------------------------------------------------------------------
MOTIFS: tuple[str, ...] = (
    "single_direct",
    "chain_relay",
    "independent_corroboration",
    "dependent_repetition",
    "common_source_laundering",
    "clustered_reinforcement",
    "centralized_synthesis",
    "compound",
)

MOTIF_LABEL: dict[str, str] = {
    "single_direct": "Single direct",
    "chain_relay": "Chain relay",
    "independent_corroboration": "Independent corroboration",
    "dependent_repetition": "Dependent repetition",
    "common_source_laundering": "Common-source laundering",
    "clustered_reinforcement": "Clustered reinforcement",
    "centralized_synthesis": "Centralized synthesis",
    "compound": "Compound",
}

# Short labels for tight axes (Fig 3 bars)
MOTIF_SHORT: dict[str, str] = {
    "single_direct": "Single\ndirect",
    "chain_relay": "Chain\nrelay",
    "independent_corroboration": "Independent\ncorroboration",
    "dependent_repetition": "Dependent\nrepetition",
    "common_source_laundering": "Common-source\nlaundering",
    "clustered_reinforcement": "Clustered\nreinforcement",
    "centralized_synthesis": "Centralized\nsynthesis",
    "compound": "Compound",
}

# One-phrase cues beneath each Fig-2 panel
MOTIF_CUE: dict[str, str] = {
    "single_direct": "One source",
    "chain_relay": "Path of relayers",
    "independent_corroboration": "Independent sources",
    "dependent_repetition": "One source repeated",
    "common_source_laundering": "Hidden shared ancestor",
    "clustered_reinforcement": "Community circulation",
    "centralized_synthesis": "Hub aggregation",
    "compound": "Composed motifs",
}

# ---------------------------------------------------------------------------
# Colours (semantic, color-blind safe)
# ---------------------------------------------------------------------------
# Okabe-Ito 8-color palette: one stable colour per motif, reused in Fig 2
# and Fig 3a. NOT used to encode reader identity.
MOTIF_COLOR: dict[str, str] = {
    "single_direct": "#0072B2",            # blue
    "chain_relay": "#E69F00",              # orange
    "independent_corroboration": "#009E73", # bluish green
    "dependent_repetition": "#56B4E9",     # sky blue
    "common_source_laundering": "#D55E00", # vermillion
    "clustered_reinforcement": "#CC79A7",  # reddish purple
    "centralized_synthesis": "#F0E442",    # yellow (lightened in dark contexts)
    "compound": "#4D4D4D",                  # dark grey (the "failure" motif)
}

# Reader pair: used in Fig 3b and Fig 4 where reader identity is the contrast.
# Chosen to be distinct from every motif colour.
READER_COLOR: dict[str, str] = {
    "form_aligned": "#2E5266",    # deep teal
    "content_attentive": "#A23E48",  # muted brick
}
READER_LABEL: dict[str, str] = {
    "form_aligned": "Form-aligned classifier",
    "content_attentive": "Content-attentive reader",
}

# Three residue classes: used in Fig 1 only.
RESIDUE_COLOR: dict[str, str] = {
    "semantic": "#1F77B4",  # blue
    "formal": "#2CA02C",    # green
    "trace": "#7E57C2",     # violet
}

CHANCE_BASELINE = 1.0 / 8.0  # 0.125 on the eight-way task
CHANCE_COLOR = "#888888"


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
def apply_style() -> None:
    """Set Matplotlib rcParams for Nature-style figures.

    Call once at the top of every figure script.
    """
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7,
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "legend.fontsize": 6.5,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,  # editable text in PDFs
        "ps.fonttype": 42,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
    })


# Nature Communications widths (mm); 25.4 mm per inch.
WIDTH_SINGLE_IN = 89 / 25.4
WIDTH_DOUBLE_IN = 183 / 25.4


def panel_letter(ax, letter: str, *, x: float = -0.15, y: float = 1.02) -> None:
    """Place a lowercase bold panel letter ('a', 'b', ...) at the top-left of the panel."""
    ax.text(
        x, y, letter,
        transform=ax.transAxes,
        fontsize=9, fontweight="bold",
        ha="right", va="bottom",
    )


# ---------------------------------------------------------------------------
# Wilson 95% confidence interval
# ---------------------------------------------------------------------------
def wilson_ci(successes: int, n: int, z: float = 1.95996398454) -> tuple[float, float]:
    """Wilson score 95% CI on a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def wilson_lower(successes: int, n: int) -> float:
    return wilson_ci(successes, n)[0]


def wilson_upper(successes: int, n: int) -> float:
    return wilson_ci(successes, n)[1]


# ---------------------------------------------------------------------------
# Trial-ID parsing
# ---------------------------------------------------------------------------
TRIAL_RE = re.compile(
    r"^bp__R(?P<regime_code>[0-9]+)(?:h(?P<hop>[0-9]+))?"
    r"__L(?P<trace_level>[0-9]+)"
    r"__v(?P<validity_x100>[0-9]+)"
    r"__CSm__F(?P<family>[0-9]+)"
    r"__W(?P<world>[0-9]+)"
    r"__rep(?P<rep>[0-9]+)$"
)


def parse_trial_id(trial_id: str) -> dict[str, str | int | None]:
    """Extract trace level, world, hop count, validity from a trial_id."""
    m = TRIAL_RE.match(trial_id)
    if m is None:
        return {}
    g = m.groupdict()
    return {
        "regime_code": int(g["regime_code"]),
        "hop_count": int(g["hop"]) if g["hop"] else None,
        "trace_level": int(g["trace_level"]),
        "validity": int(g["validity_x100"]) / 100.0,
        "family": int(g["family"]),
        "world": f"W{int(g['world']):03d}",
        "rep": int(g["rep"]),
    }


TEST_WORLDS = frozenset({"W017", "W018", "W019", "W020"})


# ---------------------------------------------------------------------------
# JSONL loaders
# ---------------------------------------------------------------------------
def _iter_jsonl(path: Path) -> Iterable[dict]:
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_ground_truth(family: str = "F1") -> pd.DataFrame:
    """Per-trial ground truth as a DataFrame keyed by trial_id."""
    fname = (
        "machine_tracing_bprime_v0_1.ground_truth.jsonl"
        if family == "F1"
        else "machine_tracing_bprime_v0_1__F2.ground_truth.jsonl"
    )
    rows: list[dict] = []
    for rec in _iter_jsonl(DATA_DIR / fname):
        rows.append({
            "trial_id": rec["trial_id"],
            "trace_packet_id": rec["trace_packet_id"],
            "true_regime": rec["true_regime"],
            "world_id": rec["world_id"],
            "cell_id": rec.get("cell_id"),
            "replicate_index": rec.get("replicate_index"),
            "hop_count": rec.get("hop_count"),
            "validity": rec.get("trace_validity_coefficient"),
            "true_accuracy_score": rec.get("true_accuracy_score"),
        })
    df = pd.DataFrame(rows)
    # Parse fields out of trial_id (the canonical encoding). The stand-alone
    # replicate_index field is always 0 in the deposited ground_truth records;
    # the real replicate index lives inside the trial_id.
    parsed = df["trial_id"].map(parse_trial_id)
    df["trace_level"] = parsed.map(lambda d: d.get("trace_level"))
    df["replicate_index"] = parsed.map(lambda d: d.get("rep"))
    return df


def _argmax_regime(posterior: dict[str, float]) -> str:
    return max(posterior, key=posterior.get)


def load_receiver(family: str = "F1") -> pd.DataFrame:
    """Per-trial receiver outputs joined on trace_packet_id.

    Columns: trial_id, trace_packet_id, predicted_regime, regime_posterior (dict),
    accuracy_probability, world_id, true_regime, trace_level.
    """
    fname = (
        "machine_tracing_bprime_v0_1.receiver.jsonl"
        if family == "F1"
        else "machine_tracing_bprime_v0_1__F2.receiver.jsonl"
    )
    rows: list[dict] = []
    for rec in _iter_jsonl(DATA_DIR / fname):
        if rec.get("invalid") is True:
            continue  # validator-rejected: manuscript filters these out
        parsed = rec.get("parsed") or {}
        regime_block = parsed.get("regime") or {}
        regime = regime_block.get("posterior") or {}
        if not regime:
            continue
        accuracy_block = parsed.get("accuracy") or {}
        rows.append({
            "trace_packet_id": rec["trace_packet_id"],
            "predicted_regime": _argmax_regime(regime),
            "regime_posterior": regime,
            "accuracy_probability": accuracy_block.get("probability"),
        })
    df = pd.DataFrame(rows)
    gt = load_ground_truth(family)
    # Join via trace_packet_id (receiver) -> trace_packet_id (ground_truth).
    out = gt.merge(df, on="trace_packet_id", how="inner")
    return out


def load_terminal_features(family: str = "F1") -> pd.DataFrame:
    """Per-trial terminal-message features and ground-truth preservation rate.

    Keys: cell_id, world_id, replicate_index, terminal_message_id, regime,
    true_accuracy_score (the proposition-matched preservation rate that the
    manuscript correlates against the LLM's stated fidelity posterior).
    """
    fname = (
        "machine_tracing_bprime_v0_1.terminal_features.jsonl"
        if family == "F1"
        else "machine_tracing_bprime_v0_1__F2.terminal_features.jsonl"
    )
    rows: list[dict] = []
    for rec in _iter_jsonl(DATA_DIR / fname):
        rows.append({
            "cell_id": rec.get("cell_id"),
            "world_id": rec.get("world_id"),
            "replicate_index": rec.get("replicate_index"),
            "regime": rec.get("regime"),
            "true_accuracy_score": rec.get("true_accuracy_score"),
        })
    return pd.DataFrame(rows)


def load_comparator(family: str = "F1") -> pd.DataFrame:
    """Form-aligned classifier predictions (only on the test split for F1)."""
    fname = (
        "machine_tracing_bprime_v0_1.comparator_predictions.jsonl"
        if family == "F1"
        else "machine_tracing_bprime_v0_1__F2.comparator_predictions.jsonl"
    )
    rows: list[dict] = []
    for rec in _iter_jsonl(DATA_DIR / fname):
        regime = rec.get("regime", {}).get("posterior", {})
        if not regime:
            continue
        rows.append({
            "trial_id": rec["trial_id"],
            "predicted_regime_comparator": _argmax_regime(regime),
            "regime_posterior_comparator": regime,
            "accuracy_probability_comparator": (rec.get("accuracy") or {}).get("probability"),
        })
    df = pd.DataFrame(rows)
    gt = load_ground_truth(family)
    out = gt.merge(df, on="trial_id", how="inner")
    return out


# ---------------------------------------------------------------------------
# Accuracy summarizers
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AccuracyResult:
    n: int
    correct: int
    accuracy: float
    ci_lo: float
    ci_hi: float


def summarize_accuracy(correct_mask: pd.Series) -> AccuracyResult:
    n = int(correct_mask.shape[0])
    k = int(correct_mask.sum())
    p = k / n if n > 0 else 0.0
    lo, hi = wilson_ci(k, n)
    return AccuracyResult(n=n, correct=k, accuracy=p, ci_lo=lo, ci_hi=hi)


def per_motif_accuracy(df: pd.DataFrame, *, pred_col: str, true_col: str = "true_regime") -> dict[str, AccuracyResult]:
    out: dict[str, AccuracyResult] = {}
    for motif in MOTIFS:
        sub = df[df[true_col] == motif]
        if sub.empty:
            out[motif] = AccuracyResult(n=0, correct=0, accuracy=0.0, ci_lo=0.0, ci_hi=0.0)
            continue
        correct = (sub[pred_col] == sub[true_col]).astype(int)
        out[motif] = summarize_accuracy(correct)
    return out


def regime_balanced_accuracy(per_motif: dict[str, AccuracyResult]) -> float:
    """Unweighted mean of per-motif accuracies, matching the manuscript definition."""
    accs = [r.accuracy for r in per_motif.values() if r.n > 0]
    return float(np.mean(accs)) if accs else 0.0


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def save_figure(
    fig: plt.Figure, stem: str, *,
    supplementary: bool = False,
    also_png: bool = True,
    png_dpi: int = 600,
) -> None:
    """Write a figure as <stem>.pdf (+ optional 600 dpi PNG).

    Main figures go to 03_figures/main/. Supplementary figures go to
    05_supplementary_information/figures/.
    """
    out_dir = SI_FIGURES_DIR if supplementary else MAIN_FIGURES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{stem}.pdf"
    fig.savefig(pdf_path)
    if also_png:
        fig.savefig(out_dir / f"{stem}.png", dpi=png_dpi)
    plt.close(fig)
    print(f"wrote {pdf_path.relative_to(PROJECT_ROOT)}")
