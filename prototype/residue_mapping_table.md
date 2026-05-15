# Residue Mapping Table

*Version: v0.1. Compiled 2026-05-13. The conceptual and measurement specification for the chain-vs-centralized-synthesis prototype.*

## Purpose

A residue is an observable feature of a received message that carries information about its hidden production or transmission history. This table identifies, for each production regime in the first prototype, the transformations the regime should perform, the candidate residues those transformations produce, the non-structural confounds that could mimic those residues, and what would make each residue *structurally diagnostic* rather than merely a generic artifact of summarization, editing, or paraphrase.

A residue is structurally diagnostic only if it satisfies three conditions:

1. **Detectable.** The feature distribution differs from an appropriate baseline.
2. **Discriminative.** The feature helps classify the production regime above a structure-blind length/topic/style baseline.
3. **Structurally entailed or privileged.** The feature is not equally producible by a one-shot operation on the original message, including under an adversarial mimicry prompt instructing a single LLM to "produce what a chain of N relayers would output."

The third condition is the new requirement. It prevents the theory from mistaking summarization artifacts for structure artifacts.

## Table

| Production regime | Transformation mechanism | Candidate residue | Non-structural confound | Structurally diagnostic version | Measurable feature | Expected direction | Notes for prototype |
|---|---|---|---|---|---|---|---|
| **chain relay** | sequential relay and compression across nodes that each see only the prior message | loss of detail | one-shot summarization can also drop details | monotonic detail loss across hops, with different detail classes decaying at different rates | proposition_preservation_rate by hop, specificity_count by hop, numeric_token_count by hop, named_entity_count by hop | preservation decreases with hop count, slope significantly different from zero | log every intermediate message so hop-slope is recoverable retrospectively |
| chain relay | sequential paraphrase | semantic drift from original | one-shot paraphrase drifts too | drift accumulates stepwise rather than appearing in one jump | semantic_drift_from_original by hop, semantic_drift_from_parent by hop | drift_from_original increases monotonically, drift_from_parent roughly constant per hop | embed each intermediate, plot drift trajectory |
| chain relay | sequential hedge stripping or amplification | uncertainty loss | editors remove hedges generically | uncertainty markers decay as a function of relay distance, not abruptly | uncertainty_marker_count by hop, uncertainty_preservation_rate by hop | decay across hops, possibly nonlinear | check whether decay rate differs for hedges tied to conflict vs. unbothered claims |
| chain relay | sequential evidential stripping | evidential-marker loss | bureaucratic editing removes attribution | evidential markers decay with path length, source markers disappear at specific hops | evidential_marker_count by hop, source_marker_count by hop | decay across hops | distinguish removal of "the operator reported" vs. removal of evidence-type qualifiers |
| chain relay | accumulating compression | compression ratio | one-shot summary compresses too | compression accumulates stepwise rather than in one jump | compression_ratio_from_parent at each hop, compression_ratio_from_original at terminal | terminal compression > sum of stepwise compressions only if accumulated; one-shot summary should match the terminal compression but not the per-hop trajectory | the per-hop compression trajectory is the diagnostic signature, not the terminal value |
| chain relay | drift toward gist and schema | unsupported additions | hallucination occurs in single-shot LLM use too | additions correlate with later hops or with content domains where schema priors are strong | unsupported_addition_count by hop | low at hop 1, rising at later hops | hand-inspect additions to verify they are schema-driven rather than random |
| **centralized synthesis** | integration of partially overlapping inputs with at least one structured conflict | fluent coherence with suppressed conflict | expert summary also smooths language | terminal message integrates heterogeneous inputs from multiple sources, reconciles or erases the conflict, and suppresses provenance markers for the disagreement | contradiction_preserved_or_repaired (binary or graded), uncertainty_loss_around_conflict, cross_input_proposition_coverage, source_marker_count | conflict-repair > conflict-preservation, uncertainty markers attached to conflict drop disproportionately | the conflict is the hub design's load-bearing feature, see world template |
| centralized synthesis | aggregation across heterogeneous evidence bases | single-voice register | a competent editor can do the same | inputs from different evidence types are combined without retaining their evidence-type distinctions; single voice in terminal | evidence_type_diversity_in_terminal vs. evidence_type_diversity_across_inputs, stylistic_homogeneity | evidence-type information collapses, register homogenizes | needs evidence_type tags on world propositions to be measurable |
| centralized synthesis | selective input weighting | uneven proposition coverage | random summarization | terminal preserves propositions from some inputs disproportionately, with a pattern not predicted by proposition centrality alone | cross_input_proposition_coverage broken out by input (a, b, c) | uneven coverage with bias toward whichever input has more affirmations or more confident framing | compare against one-shot synthesis baseline to test prompt-specific vs. structural |
| centralized synthesis | provenance flattening | source-marker loss | anonymization or editorial standardization | terminal has fewer source markers than any individual input despite synthesizing them | source_marker_count in terminal vs. mean and max across inputs | terminal < min(inputs) for source markers | this is the strongest single hub residue if it appears |
| **one-shot summary baseline** | single-pass compression of the chain original | similar surface compression and detail loss | this is the regime, not a confound | terminal residue should *match the chain terminal in aggregate compression* but *lack the per-hop trajectory* | all chain-relay features applied to one-shot summary | matches chain terminal on length and compression; differs on per-hop diagnostics by construction | the comparison test: chain residue is structurally diagnostic only if it exceeds the one-shot summary on per-hop features |
| **one-shot synthesis baseline** | single-pass integration of three hub inputs under a baseline prompt | similar fluent coherence | this is the regime, not a confound | terminal should match the hub terminal on integration but reveal whether conflict-repair and source-marker loss are *prompt-driven* or *structurally privileged* | all hub-synthesis features applied to one-shot baseline | if one-shot baseline matches the hub on conflict_preserved_or_repaired and source_marker_count, hub residue is not structurally privileged | this baseline is the strongest validity test in the prototype |
| **structure-blind length/topic/style baseline** | none; a classifier trained only on length, topic indicator, and generic style features (type-token ratio, mean sentence length, lexical sophistication) | not a residue, a baseline | not applicable | structural classifiers must beat this baseline by a meaningful margin (precommitted threshold) to demonstrate that residue features carry structural information beyond surface correlates | classifier balanced accuracy and AUC for regime prediction from style-only features vs. residue features | structure-blind baseline should perform near chance on structurally diagnostic features but well on surface features | precommitted threshold for "meaningful margin": balanced-accuracy delta ≥ 0.15 vs. structure-blind baseline |
| **adversarial mimicry baseline** (optional in first prototype) | single LLM call prompted to "produce what a chain of 5 relayers would output for this message" | similar surface residue under adversarial framing | this is the regime, not a confound | tests whether chain residue can be faked by a single-shot LLM with adversarial prompting | all chain-relay features applied to adversarial mimicry output | if adversarial mimicry reproduces chain per-hop residue (e.g., simulated intermediate hops), chain residue is *not* structurally entailed | the strongest possible falsification test; include if budget permits |

## Skeptical feature set (internal control)

In addition to the structurally-relevant features above, the residue extractor should compute a *skeptical* feature set whose distributions should *not* differ across regimes if structural legibility is real. These features serve as an internal validity check.

- type_token_ratio
- mean_sentence_length
- mean_word_length
- punctuation_density
- subordinate_clause_density (approximate)
- average_syllables_per_word (approximate)

If these features discriminate regimes as well as the target residue features, the "structural" effects are mostly stylistic artifacts.

## Precommitted quantitative thresholds

Before runs are executed, the following thresholds are committed in the experiment config and treated as falsification criteria. After the prototype is run, results are compared against these thresholds, not against post-hoc inspection.

| Test | Metric | Threshold |
|---|---|---|
| chain hop slope | Spearman ρ between hop_index and proposition_preservation_rate | \|ρ\| ≥ 0.5 |
| chain hop slope | Spearman ρ between hop_index and uncertainty_marker_count | \|ρ\| ≥ 0.4 |
| chain hop slope | Spearman ρ between hop_index and semantic_drift_from_original | ρ ≥ 0.5 |
| hub conflict repair | proportion of hub runs in which the structured conflict is *not* preserved in the terminal message | ≥ 0.5 (i.e., hub erases conflict more often than not) |
| hub source-marker loss | terminal source_marker_count < min(input source_marker_counts) | ≥ 0.5 of runs |
| structural classifier vs. structure-blind baseline | balanced-accuracy delta in regime prediction | ≥ 0.15 |
| chain vs. one-shot summary, per-hop trajectory | feature trajectories statistically separable on at least one diagnostic feature (e.g., proposition_preservation_rate at intermediate hops) | yes/no, qualitative inspection |
| skeptical features | balanced-accuracy delta when classifying regime from skeptical features alone | ≤ 0.05 (i.e., skeptical features should not discriminate) |

These thresholds are not asserting that the prototype must hit them. They are pre-registered targets so post-hoc inspection cannot retroactively define a threshold the data happens to clear.

## What this table is for

This is the spec document. It tells the world-state slot template what proposition types, uncertainty fields, evidence markers, conflicts, and peripheral details the worlds must contain so that the residues listed above are *measurable*. It tells the residue extractor what features to compute. It tells the experiment config what conditions and baselines to include. The world template, schema, prompts, extractor, and config all derive from this table.

Do not modify this table after worlds and prompts are built without also re-evaluating the downstream artifacts.
