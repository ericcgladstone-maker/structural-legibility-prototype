"""
Candidate-set construction for the receiver-task.

Implements the methodology in `prompts/candidate_set_construction_v0_1.md`:
- CS-S (small closed, n=5): 1 true source + 4 impostors, operational-category-matched. True source always present.
- CS-M (medium open, n=30): 1 true + 29 impostors with p=0.7; 0 true + 30 impostors with p=0.3. Stratified impostor pool.
- CS-L (large open, n=100): 1 true + 99 impostors with p=0.3; 0 true + 100 impostors with p=0.7. Looser plausibility.
- Prior: uniform (default) or structured_biased (Krackhardt CSS option; 70% uniform + 20% concentrated on active_producer + 10% reserved for outside_set/unknown_deferred).

Deterministic given (cell_id, world_id, seed) per reproducibility-for-human-coding discipline.

Literature anchors:
- Koppel-Schler-Argamon (2009) universe-definition discipline.
- Koppel-Winter (2014) impostor sampling.
- PAN open-set evaluation conventions (outside_set residual, unknown_deferred via Peñas-Rodrigo c@1).
- Krackhardt (1987) cognitive social structures for structured-biased prior.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SIZE_CLASS_CONFIG = {
    "CS-S": {"target_size": 5, "true_in_set_prob": 1.0, "category_match_required": True},
    "CS-M": {"target_size": 30, "true_in_set_prob": 0.7, "category_match_required": False},
    "CS-L": {"target_size": 100, "true_in_set_prob": 0.3, "category_match_required": False},
}


@dataclass
class CandidateSet:
    """Constructed candidate set with prior weights and ground-truth metadata."""
    candidate_set_id: str
    size_class: str  # CS-S | CS-M | CS-L
    seed: int
    prior_type: str  # uniform | structured_biased
    true_source_persona_id: str
    true_source_in_set: bool
    candidates: list[dict]  # ordered list of persona dicts
    prior_weights: dict[str, float]  # persona_id -> weight, plus "outside_set" and "unknown_deferred"

    def to_dict(self) -> dict:
        return {
            "candidate_set_id": self.candidate_set_id,
            "size_class": self.size_class,
            "seed": self.seed,
            "prior_type": self.prior_type,
            "true_source_persona_id": self.true_source_persona_id,
            "true_source_in_set": self.true_source_in_set,
            "candidates": self.candidates,
            "prior_weights": self.prior_weights,
        }


def load_persona_pool(path: Path | str) -> list[dict]:
    """Load persona pool from JSON file. Returns list of persona dicts."""
    with Path(path).open() as f:
        data = json.load(f)
    return data["personas"]


def build_candidate_set(
    persona_pool: list[dict],
    *,
    cell_id: str,
    world_id: str,
    seed: int,
    size_class: str,
    true_source_persona_id: str,
    prior_type: str = "uniform",
) -> CandidateSet:
    """
    Construct a candidate set deterministically given (cell_id, world_id, seed).

    Parameters
    ----------
    persona_pool : list of persona dicts (loaded from persona_pool_v0_1.json).
    cell_id : identifier of the experimental cell.
    world_id : identifier of the world being evaluated.
    seed : RNG seed for reproducibility.
    size_class : CS-S | CS-M | CS-L.
    true_source_persona_id : persona_id of the actual originating source.
    prior_type : "uniform" (default) or "structured_biased" (Krackhardt CSS).
    """
    if size_class not in SIZE_CLASS_CONFIG:
        raise ValueError(f"Unknown size_class: {size_class}. Must be one of {list(SIZE_CLASS_CONFIG)}.")
    if prior_type not in ("uniform", "structured_biased"):
        raise ValueError(f"Unknown prior_type: {prior_type}.")

    cfg = SIZE_CLASS_CONFIG[size_class]
    rng = random.Random(seed)

    # Locate the true source in the pool
    true_source = next((p for p in persona_pool if p["persona_id"] == true_source_persona_id), None)
    if true_source is None:
        raise ValueError(f"True source {true_source_persona_id} not found in persona pool.")

    # Decide whether the true source is in the constructed set
    if cfg["true_in_set_prob"] >= 1.0:
        true_in_set = True
    else:
        true_in_set = rng.random() < cfg["true_in_set_prob"]

    # Build impostor pool
    impostor_pool = [p for p in persona_pool if p["persona_id"] != true_source_persona_id]
    if cfg["category_match_required"]:
        impostor_pool = [p for p in impostor_pool if p["operational_category"] == true_source["operational_category"]]

    impostor_count = cfg["target_size"] - (1 if true_in_set else 0)
    if len(impostor_pool) < impostor_count:
        raise ValueError(
            f"Not enough impostors for {size_class}: pool has {len(impostor_pool)} "
            f"matching personas, need {impostor_count}. Expand the persona pool."
        )

    # Sort the impostor pool by persona_id for determinism before sampling
    impostor_pool = sorted(impostor_pool, key=lambda p: p["persona_id"])
    impostors = rng.sample(impostor_pool, impostor_count)

    # Build the candidate list and shuffle order so true source position is not predictable
    candidates = ([true_source] if true_in_set else []) + impostors
    rng.shuffle(candidates)

    # Build prior weights
    prior_weights = _build_prior_weights(candidates, prior_type)

    candidate_set_id = f"{cell_id}__{world_id}__seed{seed}"
    return CandidateSet(
        candidate_set_id=candidate_set_id,
        size_class=size_class,
        seed=seed,
        prior_type=prior_type,
        true_source_persona_id=true_source_persona_id,
        true_source_in_set=true_in_set,
        candidates=candidates,
        prior_weights=prior_weights,
    )


def _build_prior_weights(candidates: list[dict], prior_type: str) -> dict[str, float]:
    """Construct prior weights over candidates + outside_set + unknown_deferred."""
    candidate_ids = [c["persona_id"] for c in candidates]
    n = len(candidates)

    if prior_type == "uniform":
        n_buckets = n + 2  # +outside_set, +unknown_deferred
        weight = 1.0 / n_buckets
        weights = {cid: weight for cid in candidate_ids}
        weights["outside_set"] = weight
        weights["unknown_deferred"] = weight
    elif prior_type == "structured_biased":
        # 70% uniform across candidates; 20% concentrated on active_producer subset; 8% outside_set; 2% unknown_deferred
        active_ids = [c["persona_id"] for c in candidates if c.get("active_producer", False)]
        n_active = len(active_ids)
        uniform_mass = 0.70
        active_mass = 0.20
        outside_mass = 0.08
        unknown_mass = 0.02

        per_candidate_uniform = uniform_mass / n
        per_active_bonus = active_mass / n_active if n_active > 0 else 0.0
        # If no active producers, redistribute the active_mass uniformly
        if n_active == 0:
            per_candidate_uniform += active_mass / n

        weights = {}
        for cid in candidate_ids:
            weights[cid] = per_candidate_uniform
            if cid in active_ids:
                weights[cid] += per_active_bonus
        weights["outside_set"] = outside_mass
        weights["unknown_deferred"] = unknown_mass
    else:
        raise ValueError(f"Unknown prior_type: {prior_type}")

    # Verify normalization
    total = sum(weights.values())
    if not (0.999 <= total <= 1.001):
        raise RuntimeError(f"Prior weights sum to {total}, not 1.0")
    return weights


def render_candidate_set(cs: CandidateSet, show_active_producer_flag: bool = True) -> str:
    """
    Render the candidate set as natural-language text for the receiver prompt.

    Follows `prompts/trace_packet_render_v0_1.md` "Candidate-source set rendering".
    Includes `outside_set` and `unknown_deferred` as explicit options.

    The structured-biased prior is operationalized via the active-producer flag
    when `show_active_producer_flag=True` — the receiver sees which candidates
    are flagged as more-likely producers without seeing numerical prior weights.
    """
    lines = []
    lines.append("Candidate sources (assign probability to each, plus to outside_set and optionally unknown_deferred):")
    for c in cs.candidates:
        flag = ""
        if show_active_producer_flag and cs.prior_type == "structured_biased" and c.get("active_producer", False):
            flag = " [flagged as more-likely active producer]"
        line = f"  - {c['persona_id']}: {c['role_descriptor']}{flag}"
        lines.append(line)
    lines.append("  - outside_set: the true source is not in the above list (assign mass here if the trace evidence suggests so)")
    lines.append("  - unknown_deferred: the evidence is genuinely insufficient to commit to any of the above (use sparingly)")
    return "\n".join(lines)


def to_ground_truth_partial(cs: CandidateSet) -> dict:
    """
    Extract candidate-set-related fields for the ground-truth sidecar artifact
    (per `schemas/ground_truth_schema_v0_1.json`).
    """
    return {
        "candidate_set_size_class": cs.size_class,
        "candidate_set_seed": cs.seed,
        "candidate_set_size_actual": len(cs.candidates),
        "true_source_persona_id": cs.true_source_persona_id,
        "true_source_in_candidate_set": cs.true_source_in_set,
    }


def _sanity_check_candidate_set(cs: CandidateSet) -> None:
    """Run sanity checks on a constructed candidate set."""
    cfg = SIZE_CLASS_CONFIG[cs.size_class]
    n_expected = cfg["target_size"]
    assert len(cs.candidates) == n_expected, \
        f"Size mismatch for {cs.size_class}: expected {n_expected}, got {len(cs.candidates)}"
    if cs.size_class == "CS-S":
        assert cs.true_source_in_set, "CS-S must contain true source"
    # Verify all candidate ids are unique
    cids = [c["persona_id"] for c in cs.candidates]
    assert len(set(cids)) == len(cids), "Duplicate candidates in set"
    # Verify true source presence matches flag
    if cs.true_source_in_set:
        assert cs.true_source_persona_id in cids, \
            f"true_source_in_set=True but {cs.true_source_persona_id} not in candidates"
    else:
        assert cs.true_source_persona_id not in cids, \
            f"true_source_in_set=False but {cs.true_source_persona_id} is in candidates"
    # Verify prior normalization
    total = sum(cs.prior_weights.values())
    assert 0.999 <= total <= 1.001, f"Prior weights sum to {total}"
    # Verify prior keys match candidates + outside + unknown
    expected_keys = set(cids) | {"outside_set", "unknown_deferred"}
    assert set(cs.prior_weights.keys()) == expected_keys, \
        f"Prior keys mismatch: {set(cs.prior_weights.keys()) - expected_keys}"


def _main_demo() -> None:
    """Demonstration: build a candidate set for each size class and prior type."""
    base = Path(__file__).resolve().parent.parent
    pool_path = base / "dictionaries" / "persona_pool_v0_1.json"
    pool = load_persona_pool(pool_path)
    print(f"Loaded {len(pool)} personas from {pool_path.name}")

    # Pick a true source for demonstration
    true_source = pool[0]["persona_id"]
    print(f"True source: {true_source}")

    # CS-S can be demonstrated because the seed pool has 4 personas per category (matches CS-S requirement of 4 impostors with same operational_category).
    for size_class in ("CS-S",):
        for prior in ("uniform", "structured_biased"):
            try:
                cs = build_candidate_set(
                    pool,
                    cell_id="demo_cell",
                    world_id="W001",
                    seed=42,
                    size_class=size_class,
                    true_source_persona_id=true_source,
                    prior_type=prior,
                )
                _sanity_check_candidate_set(cs)
                print(f"\n--- {size_class} / {prior} ---")
                print(f"  candidate_set_id: {cs.candidate_set_id}")
                print(f"  true_source_in_set: {cs.true_source_in_set}")
                print(f"  candidates: {[c['persona_id'] for c in cs.candidates]}")
                print(f"  prior sum: {sum(cs.prior_weights.values()):.6f}")
                print(f"  prior on true source: {cs.prior_weights.get(true_source, 0):.4f}")
                print(f"  prior on outside_set: {cs.prior_weights['outside_set']:.4f}")
                print(f"  prior on unknown_deferred: {cs.prior_weights['unknown_deferred']:.4f}")
                print("\nRendered for receiver prompt:")
                print(render_candidate_set(cs))
            except Exception as e:
                print(f"\n--- {size_class} / {prior} ---")
                print(f"  FAILED: {e}")

    # CS-M and CS-L require persona pool expansion (need 30 and 100 impostors respectively).
    # Note this in the output for the user.
    print("\nNote: CS-M and CS-L demonstrations require expanding the persona pool")
    print(f"from {len(pool)} to ~150 entries. Currently the seed pool has 20 personas total.")


if __name__ == "__main__":
    _main_demo()
