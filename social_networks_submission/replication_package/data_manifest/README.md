# Data manifest

The raw data files referenced in the manuscript and required by the analysis scripts are hosted separately due to size (~140 MB total). They will be deposited at a public repository with a citable DOI upon publication. For peer review, an anonymized download link will be provided through the journal's submission system.

## Data streams

For each of two experimental runs (primary F1 + cross-reader-family robustness slice F2), four JSONL streams are deposited:

### Primary run (F1, qwen2.5:7b as content-attentive reader)

| File | Records | Size | Description |
|---|---|---|---|
| `machine_tracing_bprime_v0_1.lineage.jsonl` | 4,200 | ~83 MB | Production-graph instantiation records: message sequences, persona assignments, hop structure, transformation calls. One record per trial. |
| `machine_tracing_bprime_v0_1.trace_packets.jsonl` | 4,200 | ~8 MB | Trace packets as presented to the reader: intercepted message text, trace-level metadata (L1–L6), validity coefficient. |
| `machine_tracing_bprime_v0_1.receiver.jsonl` | 4,200 | ~21 MB | Reader outputs: parsed JSON with seven fields (accuracy posterior, regime posterior, origin posterior, independence judgment), plus raw model output and validation metadata. |
| `machine_tracing_bprime_v0_1.ground_truth.jsonl` | 4,200 | ~3 MB | Ground-truth labels: true regime, true source persona, in-set flag, hop count, validity coefficient, candidate-set size. |

### F2 cross-reader-family robustness slice (llama3.1:8b as content-attentive reader)

| File | Records | Size | Description |
|---|---|---|---|
| `machine_tracing_bprime_v0_1__F2.lineage.jsonl` | 460 | ~9 MB | Lineage records for the F2 slice. |
| `machine_tracing_bprime_v0_1__F2.trace_packets.jsonl` | 460 | ~1 MB | Trace packets. |
| `machine_tracing_bprime_v0_1__F2.receiver.jsonl` | 460 | ~2 MB | F2 reader outputs. |
| `machine_tracing_bprime_v0_1__F2.ground_truth.jsonl` | 460 | ~0.5 MB | Ground-truth labels. |

### Derived / analysis-stage artifacts

| File | Description |
|---|---|
| `machine_tracing_bprime_v0_1.terminal_features.jsonl` | 14-feature surface-form extractions per terminal message (input to the form-aligned classifier). |
| `machine_tracing_bprime_v0_1.comparator_predictions.jsonl` | Comparator predictions on the F1 test split (n=840). |
| `machine_tracing_bprime_v0_1.redaction_results.jsonl` | Before/after receiver predictions from the redaction experiment (n=152). |

### Worlds

| File | Records | Description |
|---|---|---|
| `worlds_v0_2.jsonl` | 20 | Structured world specifications with conflict pairs, propositions, evidence-type tags. The 20 fixed worlds used across all 4,200 primary trials. |

## Trial identifier convention

Trials use a structured identifier of the form:
`bp__R{regime_code}__L{trace_level}__v{validity_x100}__CSm__F{family}__W{world_id}__rep{replicate}`

Examples:
- `bp__R1__L1__v100__CSm__F1__W001__rep0` — single_direct, content-only trace, no metadata to corrupt, F1 reader, world 1, replicate 0.
- `bp__R7h3__L6__v030__CSm__F1__W014__rep2` — chain_relay (3 hops), full analytic packet at v=0.30 corruption, F1 reader, world 14, replicate 2.

Regime codes: R1 single_direct, R2 independent_corroboration, R3 dependent_repetition, R4 common_source_laundering, R5 clustered_reinforcement, R6 centralized_synthesis, R7 chain_relay (with hop count hN), R8 compound.

## Accessing the data during review

Reviewers: an anonymized download link is provided through the journal's submission system. Please contact the editorial office if you need assistance obtaining the data files.

Upon publication, the data deposit DOI will be reported in the manuscript's data availability statement.
