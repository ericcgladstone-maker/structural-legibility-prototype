# Nature Communications submission — reproducibility deposit

Anonymized for double-blind peer review.

This folder is the data-and-code reproducibility deposit for the manuscript *Message residue preserves traces of hidden communication structure*, prepared for submission to *Nature Communications*. The manuscript text, its rendered figures, its tables, and its Supplementary Information document live in the journal submission and are not duplicated here. This deposit lets a third party regenerate the reported figures and the paired-bootstrap and predicted-label-entropy values from the underlying experimental data.

## Contents

### `data/` — raw experimental data

Twenty fixed event records, four primary-run JSON Lines streams, and the matching cross-reader-family slice. About 130 MB total. Each `*.jsonl` file is one record per line.

| File | Records | Description |
|---|---:|---|
| `worlds_v0_2.jsonl` | 20 | Structured event records that anchor every cell. Each carries a core observed event, competing causal hypotheses with their supporting evidence, peripheral operational details, and a built-in conflict pair with proposition truth values, uncertainty levels, and evidence types. The worlds are synthetic structured records, not empirical events. |
| `machine_tracing_bprime_v0_1.lineage.jsonl` | 4,200 | Production-graph instantiation records for the primary run: message sequences, persona assignments, hop structure, and the underlying language-model calls. One record per trial. |
| `machine_tracing_bprime_v0_1.trace_packets.jsonl` | 4,200 | Trace packets as presented to the reader at trace levels L1, L3, L5, and L6, with the validity coefficient applied. |
| `machine_tracing_bprime_v0_1.receiver.jsonl` | 4,200 | Content-attentive reader (qwen2.5:7b) outputs: parsed JSON with the accuracy posterior, the regime posterior over the eight motifs, the origin posterior over candidate sources, and the independence judgment, plus raw model output and the validator's `invalid` flag. |
| `machine_tracing_bprime_v0_1.ground_truth.jsonl` | 4,200 | Ground-truth labels per trial: true regime, true source persona, in-set flag, hop count, validity coefficient, and candidate-set size. |
| `machine_tracing_bprime_v0_1.terminal_features.jsonl` | 4,200 | The 14 surface features extracted per terminal message, plus the proposition-matched preservation rate `true_accuracy_score`. |
| `machine_tracing_bprime_v0_1.comparator_predictions.jsonl` | 840 | Form-aligned classifier predictions on the test split (worlds W017 to W020). |
| `machine_tracing_bprime_v0_1.redaction_results.jsonl` | 152 | Before-and-after receiver predictions from the explicit-cue redaction experiment. |
| `machine_tracing_bprime_v0_1__F2.lineage.jsonl` | 460 | Cross-family slice (llama3.1:8b reader): lineage records. |
| `machine_tracing_bprime_v0_1__F2.trace_packets.jsonl` | 460 | Cross-family slice: trace packets. |
| `machine_tracing_bprime_v0_1__F2.receiver.jsonl` | 460 | Cross-family slice: reader outputs. |
| `machine_tracing_bprime_v0_1__F2.ground_truth.jsonl` | 460 | Cross-family slice: ground-truth labels. |
| `machine_tracing_bprime_v0_1__F2.terminal_features.jsonl` | 460 | Cross-family slice: terminal-message features. |
| `machine_tracing_bprime_v0_1__F2.comparator_predictions.jsonl` | 92 | Cross-family slice: comparator predictions on its test split. |

### `scripts/` — analysis and figure-generation code

- `figure_style.py` — shared style module: color palettes, font configuration, Wilson 95% CI helper, JSONL data loaders, motif vocabulary, and output-path helpers used by every figure script.
- `make_figure_1.py` through `make_figure_4.py` — generate the four main figures (inverse problem and residue classes; eight production motifs; motif recoverability and reader-instrument alignment; alignment diagnostics).
- `make_si_figure_1.py` through `make_si_figure_3.py` — generate the three supplementary figures (aggregate reader-family comparison; row-normalized confusion matrices with predicted-label Shannon entropy; fidelity posterior versus source-content preservation).
- `bootstrap_and_entropy.py` — paired bootstrap 95% confidence intervals for the form-aligned-versus-content-attentive accuracy gap and for the full-versus-length-only accuracy gap, plus predicted-label entropy values for both reader families.

## How to run

The figure and bootstrap scripts read the JSONL streams from `data/` via the loaders in `figure_style.py`. With the deposit unpacked, each script can be executed independently from this `scripts/` folder. The figure scripts produce vector PDF and 600-dpi PNG outputs. The bootstrap script writes a single Markdown summary with paired-bootstrap intervals and entropy values, and prints a one-line summary to standard output.

The sibling `prototype/` folder of this repository contains the upstream experimental apparatus that generates the data streams above (regime instantiators, trace-packet assembly, residue extractor, proposition matcher, receiver dispatcher, and the experiment orchestrator). The deposit here is sufficient for reproducing the reported analyses and figures from the existing data without re-running the upstream apparatus.

Because language-model decoding is stochastic, the reproducibility standard for the upstream generation step is distributional, the same statistical patterns over multiple runs, rather than exact byte-equivalence of specific outputs. The analyses on the deposited data are deterministic.

## Software

Python 3.9 or later, with `numpy`, `pandas`, `matplotlib`, and `scikit-learn`. Re-running the upstream experimental pipeline additionally requires the language-model dependencies described in `prototype/README.md`.

## License

Code released under the MIT License upon publication. Data released under CC-BY-4.0.
