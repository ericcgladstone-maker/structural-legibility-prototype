# Replication package

Anonymized for double-blind peer review.

This package contains the source code, prompts, and configuration files used to produce the results in the accompanying manuscript. The raw data (4,200 generated trials plus a 460-trial cross-reader-family robustness slice, totaling ~140 MB across four JSONL streams) is hosted separately and described in `data_manifest/`.

## Folder layout

```
replication_package/
├── README.md             this file
├── code/                 Python source files (apparatus + analyses)
├── prompts/              receiver prompt template (the one given to the LLM at each trial)
├── configs/              experiment configuration files (primary + F2 robustness slice)
└── data_manifest/        description of data files and instructions to obtain them
```

## What is and is not here

**Included:**
- Apparatus source: receiver dispatcher, candidate-set construction, regime instantiators, trace-packet assembly, end-to-end orchestrator, residue extractor, proposition matcher, structure-blind comparator.
- Analysis scripts: substantive analysis, comparator evaluation, regime cross-tabs, length-effect analysis, redaction experiment runner and analyzer.
- Receiver prompt (text format, exactly as presented to the content-attentive reader).
- Experiment configs (YAML).
- Data manifest describing the four JSONL streams.

**Not included (size or anonymization reasons):**
- Generated data JSONL files (~140 MB) — see `data_manifest/` for the hosted location and DOI when available.
- Hand-drawn vector figure source files (figures rendered to PDF/PNG are included alongside the manuscript).

## Reproduction

The apparatus is built under a reproducibility-for-human-coding discipline (Section 5 of the manuscript). All stimuli, prompts, candidate sets, and ground-truth labels are human-readable text or JSON; human coders unfamiliar with the project can be substituted at any experimental cell without redesign of the apparatus.

### Software requirements

- Python 3.9+
- `numpy`, `scikit-learn`, `sentence-transformers`, `yaml`, `jsonschema`, `httpx`
- Local Ollama inference (or equivalent) for the producer and reader language models:
  - `llama3.1:8b` (producer; cross-reader-family robustness reader)
  - `qwen2.5:7b` (primary reader)

### Re-running the experiment end-to-end (estimated cost: $0; estimated wall-clock: ~52 hours on a recent MacBook)

```
# 1. Pull the language models locally
ollama pull llama3.1:8b
ollama pull qwen2.5:7b

# 2. Run the primary experiment
python3 -m code.run_experiment_paper1 configs/machine_tracing_bprime_v0_1.yaml --fresh

# 3. Run the F2 cross-reader-family robustness slice
python3 -m code.run_experiment_paper1 configs/machine_tracing_bprime_v0_1__F2.yaml --fresh
```

### Re-analyzing the existing data without re-running the experiment

```
# Substantive analysis report (per-cell summaries, recoverability curves, etc.)
python3 code/analyze_machine_tracing_bprime.py --experiment-id machine_tracing_bprime_v0_1

# Comparator evaluation + Brier-on-accuracy analysis
python3 code/extract_terminal_features_paper1.py --experiment-id machine_tracing_bprime_v0_1
python3 code/evaluate_comparator_paper1.py --experiment-id machine_tracing_bprime_v0_1

# Per-regime cross-tabs (LLM vs comparator side-by-side)
python3 code/regime_crosstab_paper1.py

# Length-effect analysis
python3 code/length_effect_analysis.py

# Redaction experiment
python3 code/redaction_experiment.py
python3 code/analyze_redaction_results.py
```

## Reproducibility notes

The language-model components are stochastic in decoding. The reproducibility policy is *distributional reproduction*: the same statistical patterns will recur over multiple runs, but exact byte-equivalence of specific text outputs is not guaranteed by current local-inference engines for these models. All reported quantitative results in the manuscript are computed from one run of the experiment (the 4,200-trial primary plus 460-trial robustness slice). Re-running with the same configuration and seeds will produce statistically equivalent results.

## License

Code is released under the MIT License upon publication. Data is released under CC-BY-4.0.
