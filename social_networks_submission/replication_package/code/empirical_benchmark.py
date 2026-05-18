"""
Empirical-benchmark comparator for the receiver-task evaluation.

Implements the spec in `specs/empirical_benchmark_comparator_v0_1.md`:
- Structure-blind L1 comparator: only sees the intercepted message (no trace packet, no candidate-specific context).
- Wraps existing residue_extractor_v2.py features.
- Produces calibrated probabilistic predictions on the same output scale as the receiver.
- Logistic regression default; isotonic regression post-hoc calibration.
- The fourth-tier reference in the four-tier evaluation structure.

Outputs match the receiver's seven-output JSON format:
- DV1 accuracy posterior: LR on residue features against world-state-derived accuracy ground truth.
- DV3 regime posterior: multinomial LR on residue features against regime ground truth.
- DV5 origin posterior: UNIFORM baseline (chance) — L1 comparator has no candidate-specific info; honesty about Pinto-Thiran-Vetterli single-observer identifiability bound.
- DV7 independence judgment: binary LR if signal exists; 0.5 default otherwise.
- DV2/DV4/DV6 confidence outputs: derived from predicted-posterior entropy.

Literature anchors:
- Tetlock (2005) empirical-benchmark practice from forecasting evaluation.
- Niculescu-Mizil and Caruana (2005) + Naeini et al. (2015) for isotonic-regression post-hoc calibration.
- Gneiting and Raftery (2007) strictly proper scoring rules as calibration target.
- Pinto-Thiran-Vetterli (2012) single-observer identifiability bound — justifies the uniform-origin baseline at L1.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


REGIME_LABELS = [
    "single_direct",
    "chain_relay",
    "independent_corroboration",
    "dependent_repetition",
    "common_source_laundering",
    "clustered_reinforcement",
    "centralized_synthesis",
    "compound",
]

DEFAULT_FEATURE_KEYS = [
    "proposition_preservation_rate",
    "proposition_contradiction_count",
    "preserved_qualified_count",
    "proposition_alteration_count",
    "semantic_drift_from_original",
    "hedge_count",
    "evidential_marker_count",
    "source_marker_count",
    "uncertainty_marker_count",
    "unsupported_addition_count",
    "terminal_token_count",
    "terminal_sentence_count",
    "mean_sentence_length",
    "lexical_density",
    "compression_ratio",
]

PROBABILITY_BIN_LABELS = [
    ("almost no chance", 0.025),
    ("very unlikely", 0.125),
    ("unlikely", 0.325),
    ("roughly even chance", 0.500),
    ("likely", 0.675),
    ("very likely", 0.875),
    ("almost certain", 0.975),
]


@dataclass
class TrainingExample:
    """One terminal message with extracted features and ground-truth labels."""
    trace_packet_id: str
    world_id: str
    cell_id: str
    features: dict[str, float]
    true_accuracy_score: float  # 0.0 to 1.0
    true_regime: str  # one of REGIME_LABELS
    true_independence_label: bool | None  # None if not applicable


@dataclass
class ComparatorModels:
    """Trained models for the L1 comparator."""
    accuracy_model: Any = None  # sklearn pipeline producing P(accurate)
    regime_model: Any = None  # sklearn pipeline producing posterior over 8 regimes
    independence_model: Any | None = None  # sklearn pipeline producing P(independent), or None
    feature_keys: list[str] = field(default_factory=lambda: list(DEFAULT_FEATURE_KEYS))
    seed: int = 0


def _features_to_vector(features: dict[str, float], feature_keys: list[str]) -> list[float]:
    """Extract feature values in fixed order. Missing features get 0.0 (caller should ensure feature presence)."""
    return [float(features.get(k, 0.0)) for k in feature_keys]


def _probability_bin(p: float) -> str:
    """Map a probability to its GJP-style bin label per receiver prompt conventions."""
    for label, threshold in PROBABILITY_BIN_LABELS:
        if p <= threshold + 0.025:
            return label
    return PROBABILITY_BIN_LABELS[-1][0]


def _entropy_to_confidence(p_distribution: list[float]) -> str:
    """Map a distribution's entropy to a discrete confidence label."""
    entropy = -sum(p * math.log2(p + 1e-12) for p in p_distribution if p > 0)
    max_entropy = math.log2(len(p_distribution))
    normalized = entropy / max_entropy if max_entropy > 0 else 0.0
    # Low entropy -> high confidence; high entropy -> low confidence
    if normalized < 0.33:
        return "high"
    elif normalized < 0.67:
        return "moderate"
    else:
        return "low"


def train_comparator(
    training_examples: list[TrainingExample],
    *,
    feature_keys: list[str] | None = None,
    seed: int = 42,
    calibration_method: str = "isotonic",
) -> ComparatorModels:
    """
    Train the empirical-benchmark comparator on a set of training examples.

    Each training example must have features (from residue_extractor_v2) and
    ground-truth labels for accuracy, regime, and (optionally) independence.

    Calibration: 5-fold cross-validated isotonic regression by default
    (Niculescu-Mizil and Caruana 2005). Use calibration_method="sigmoid" for
    Platt scaling instead.
    """
    if not SKLEARN_AVAILABLE:
        raise RuntimeError("scikit-learn is required. Install with: pip install scikit-learn")

    feature_keys = feature_keys or list(DEFAULT_FEATURE_KEYS)
    X = np.array([_features_to_vector(ex.features, feature_keys) for ex in training_examples])

    # Accuracy: binarize ground truth at 0.7 threshold (the cutoff is a design choice;
    # could also do ordinal regression for continuous accuracy. Binary is simpler and
    # matches the DV1 "P(accurate)" framing.)
    y_accuracy = np.array([1 if ex.true_accuracy_score >= 0.7 else 0 for ex in training_examples])
    accuracy_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, random_state=seed)),
    ])
    accuracy_calibrated = CalibratedClassifierCV(accuracy_pipeline, method=calibration_method, cv=5)
    accuracy_calibrated.fit(X, y_accuracy)

    # Regime: multinomial LR over the 8 regime labels.
    y_regime = np.array([ex.true_regime for ex in training_examples])
    regime_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, multi_class="multinomial", random_state=seed)),
    ])
    regime_calibrated = CalibratedClassifierCV(regime_pipeline, method=calibration_method, cv=5)
    regime_calibrated.fit(X, y_regime)

    # Independence: binary LR over the subset with non-null independence labels.
    independence_model = None
    indep_examples = [ex for ex in training_examples if ex.true_independence_label is not None]
    if len(indep_examples) >= 20:  # need enough data to train + calibrate
        X_indep = np.array([_features_to_vector(ex.features, feature_keys) for ex in indep_examples])
        y_indep = np.array([1 if ex.true_independence_label else 0 for ex in indep_examples])
        indep_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(max_iter=1000, random_state=seed)),
        ])
        independence_model = CalibratedClassifierCV(indep_pipeline, method=calibration_method, cv=5)
        independence_model.fit(X_indep, y_indep)

    return ComparatorModels(
        accuracy_model=accuracy_calibrated,
        regime_model=regime_calibrated,
        independence_model=independence_model,
        feature_keys=feature_keys,
        seed=seed,
    )


def predict_receiver_format(
    models: ComparatorModels,
    features: dict[str, float],
    candidate_ids: list[str],
    *,
    is_corroboration_family: bool = False,
) -> dict:
    """
    Produce a prediction in the receiver's seven-output JSON format.

    Parameters
    ----------
    models : trained ComparatorModels.
    features : feature dict for the terminal message (from residue_extractor_v2).
    candidate_ids : list of candidate persona IDs for this trial (used to build the uniform-baseline origin posterior).
    is_corroboration_family : whether the regime is in {independent_corroboration, dependent_repetition, common_source_laundering, clustered_reinforcement}. If False and the regime is single-direct/chain-relay/centralized-synthesis, the independence judgment is null.
    """
    if not SKLEARN_AVAILABLE:
        raise RuntimeError("scikit-learn is required.")

    X = np.array([_features_to_vector(features, models.feature_keys)])

    # Accuracy posterior: probability of being accurate per the classifier
    accuracy_prob = float(models.accuracy_model.predict_proba(X)[0][1])
    accuracy_confidence = _entropy_to_confidence([accuracy_prob, 1.0 - accuracy_prob])

    # Regime posterior: multinomial probabilities. sklearn's classes_ may be in any
    # alphabetical order; align to REGIME_LABELS for stable output.
    regime_proba_raw = models.regime_model.predict_proba(X)[0]
    regime_classes = list(models.regime_model.classes_)
    regime_posterior = {label: 0.0 for label in REGIME_LABELS}
    for cls, p in zip(regime_classes, regime_proba_raw):
        regime_posterior[cls] = float(p)
    # Renormalize in case some regimes were not in training data
    s = sum(regime_posterior.values())
    if s > 0:
        regime_posterior = {k: v / s for k, v in regime_posterior.items()}
    regime_confidence = _entropy_to_confidence(list(regime_posterior.values()))

    # Origin posterior: UNIFORM baseline (honesty about Pinto-Thiran-Vetterli identifiability).
    # L1 comparator has no candidate-specific information to use.
    n_buckets = len(candidate_ids) + 2  # +outside_set, +unknown_deferred
    uniform_weight = 1.0 / n_buckets
    origin_posterior = {cid: uniform_weight for cid in candidate_ids}
    origin_posterior["outside_set"] = uniform_weight
    origin_posterior["unknown_deferred"] = uniform_weight
    origin_confidence = "low"  # honest representation of no information

    # Independence judgment: trained model if applicable; otherwise 0.5 default or null
    if is_corroboration_family:
        if models.independence_model is not None:
            indep_prob = float(models.independence_model.predict_proba(X)[0][1])
            indep_confidence = _entropy_to_confidence([indep_prob, 1.0 - indep_prob])
        else:
            indep_prob = 0.5
            indep_confidence = "low"
        independence_block = {
            "probability_independent": indep_prob,
            "confidence_in_judgment": indep_confidence,
            "reasoning": "L1 comparator (structure-blind LR on residue features) prediction.",
        }
    else:
        independence_block = {
            "probability_independent": None,
            "confidence_in_judgment": None,
            "reasoning": "N/A — single-source regime",
        }

    return {
        "predictor_kind": "comparator_v0_1",
        "accuracy": {
            "probability": accuracy_prob,
            "probability_bin": _probability_bin(accuracy_prob),
            "confidence_in_judgment": accuracy_confidence,
            "reasoning": "L1 comparator: logistic regression on residue features against world-state-derived accuracy ground truth.",
        },
        "regime": {
            "posterior": regime_posterior,
            "confidence_in_judgment": regime_confidence,
            "reasoning": "L1 comparator: multinomial LR on residue features against regime ground truth.",
        },
        "origin": {
            "posterior": origin_posterior,
            "confidence_in_judgment": origin_confidence,
            "reasoning": "L1 comparator has no candidate-specific information; reports uniform baseline (Pinto-Thiran-Vetterli single-observer identifiability honesty).",
        },
        "independence_judgment": independence_block,
    }


def save_models(models: ComparatorModels, path: Path | str) -> None:
    """Persist trained models to disk via pickle (for offline reuse)."""
    import pickle
    with Path(path).open("wb") as f:
        pickle.dump(models, f)


def load_models(path: Path | str) -> ComparatorModels:
    """Load trained models from disk."""
    import pickle
    with Path(path).open("rb") as f:
        return pickle.load(f)


def _main_demo() -> None:
    """
    Demonstration: build a stub comparator that produces uniform baselines
    everywhere (no trained models). Useful as a sanity check before real
    training data exists.
    """
    print("empirical_benchmark.py — module loaded.")
    if not SKLEARN_AVAILABLE:
        print("sklearn not available — install with: pip install scikit-learn")
        print("Module loads but training/prediction require sklearn.")
        return

    print(f"sklearn available. Feature keys: {DEFAULT_FEATURE_KEYS}")
    print(f"Regime labels: {REGIME_LABELS}")
    print(f"Probability bins: {[bin_[0] for bin_ in PROBABILITY_BIN_LABELS]}")
    print()
    print("To use:")
    print("  1. After receiver runs produce a feature parquet (via residue_extractor_v2 on terminal messages),")
    print("     construct TrainingExample objects from the held-out training subset (80/20 world-level split).")
    print("  2. Call train_comparator(training_examples) to fit LR + isotonic calibration.")
    print("  3. At evaluation time, call predict_receiver_format(models, features, candidate_ids) per terminal.")
    print("  4. Comparator predictions are stored alongside receiver predictions with predictor_kind='comparator_v0_1'.")
    print("  5. Per-cell Brier/ECE/AUROC comparison at analysis time.")


if __name__ == "__main__":
    _main_demo()
