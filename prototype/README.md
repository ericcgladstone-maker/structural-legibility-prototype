# Structural Legibility Prototype (v0.1)

A small, auditable research harness for testing whether communication structures leave detectable and discriminative residues in transmitted messages. This is not an app, dashboard, or production system. It is the smallest transparent system that can answer:

> Do chain relay and centralized synthesis produce residue profiles that are detectable, discriminative, and not reducible to one-shot summarization, length, topic, or generic style?

The theoretical spine is `structure → transformation → residue → recoverability`. The first prototype tests the most fragile arrow, `transformation → residue`. Receiver-inference, human raters, broad model-family comparison, adversarial conditions, and a full factorial design are all deliberately deferred.

## Repository layout

```
prototype/
├── README.md
├── requirements.txt
├── residue_mapping_table.md         specification of structurally diagnostic residues
├── world_state_template.md          specification of the world-state slots
├── schemas/
│   └── world_schema_v0_1.json       JSON Schema for worlds
├── worlds/
│   └── worlds_v0_1.jsonl            20 hand-crafted operational-event worlds
├── dictionaries/                    locked dictionaries (versioned)
│   ├── hedges_v0_1.json
│   ├── uncertainty_markers_v0_1.json
│   ├── evidential_markers_v0_1.json
│   └── source_markers_v0_1.json
├── prompts/                         versioned prompt templates
│   ├── source_prompt_v0_1.txt
│   ├── relay_a_v0_1.txt
│   ├── relay_b_v0_1.txt
│   ├── relay_c_v0_1.txt
│   ├── synthesis_a_v0_1.txt
│   ├── synthesis_b_v0_1.txt
│   ├── synthesis_c_v0_1.txt
│   ├── summary_baseline_v0_1.txt
│   └── synthesis_baseline_v0_1.txt
├── configs/
│   ├── chain_hub_proto_v0_1.yaml    experiment config (the versioned design artifact)
│   └── pricing_table_v0_1.json
├── src/                             harness code
│   ├── model_client.py              dispatch to Ollama / Anthropic / OpenAI + local embeddings
│   ├── world_loader.py              load + validate worlds
│   ├── proposition_matcher.py       embedding-based proposition matching
│   ├── residue_extractor.py         per-message feature extraction (v0.1)
│   ├── trace_writer.py              append-only JSONL trace writer with assertions
│   ├── run_experiment.py            main harness: config -> trace
│   ├── etl.py                       JSONL -> Parquet -> DuckDB
│   └── audit_export.py              markdown audit export (blinded and unblinded)
├── scripts/
│   ├── smoke_test.py                1 world, 1 rep, all conditions
│   ├── run_prototype.py             full 20-world prototype
│   ├── build_etl.py                 standalone ETL run
│   └── build_audit.py               standalone audit export
└── outputs/                         created on first run
    ├── chain_hub_proto_v0_1.trace.jsonl
    ├── parquet_chain_hub_proto_v0_1/
    │   ├── runs.parquet
    │   ├── messages.parquet
    │   ├── calls.parquet
    │   ├── features.parquet
    │   └── aux_matches.parquet
    ├── chain_hub_proto_v0_1.duckdb
    ├── chain_hub_proto_v0_1.audit.md
    └── chain_hub_proto_v0_1.audit.mapping.json
```

## What the prototype does

Per world, it runs four conditions in interleaved order:

- `chain_3hop` — source generates a chain original report. Three relay nodes pass it on in sequence, each seeing only the prior message. Three relay-prompt variants cycle across hops.
- `hub_3input_synthesis` — three source nodes each render a partial report of the same world from a different subset of propositions (with partial overlap and one structured causal conflict). A synthesizer integrates all three into a single terminal message. Three synthesis-prompt variants cycle across runs.
- `one_shot_summary_length_matched` — single LLM call: source generates the chain original, then a separate LLM call summarizes it to a length matched to the median chain terminal.
- `one_shot_synthesis_length_matched` — single LLM call: source generates the three hub inputs, then a separate LLM call integrates them with a baseline synthesis prompt to a length matched to the median hub terminal.

Every LLM call is stateless. Conditions are interleaved by a seeded shuffle to prevent batch effects. All intermediate messages, prompts, raw outputs, model metadata, token counts, costs, and (where available) logprobs are stored.

Per-message residue features are extracted at the end of each run (see `src/residue_extractor.py` and `residue_mapping_table.md`).

## Setup

Python 3.11 or newer.

```bash
cd prototype
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Local model (cheapest, recommended for first runs)

Install Ollama (https://ollama.com) and pull a small model:

```bash
ollama pull llama3.1:8b
ollama serve
```

Default config uses `ollama_local` with `llama3.1:8b` at `http://localhost:11434/api/chat`. Override the URL with `OLLAMA_URL` env var if needed.

### API model alternatives

For Anthropic:

```bash
export ANTHROPIC_API_KEY=...
export MUTATOR_PROVIDER=anthropic
export MUTATOR_MODEL=claude-haiku-4-5
export SOURCE_PROVIDER=anthropic
export SOURCE_MODEL=claude-haiku-4-5
```

For OpenAI:

```bash
export OPENAI_API_KEY=...
export MUTATOR_PROVIDER=openai
export MUTATOR_MODEL=gpt-4o-mini
export SOURCE_PROVIDER=openai
export SOURCE_MODEL=gpt-4o-mini
```

The smoke test honors these env vars and writes a temporary override config. The prototype runner (`run_prototype.py`) uses the YAML config directly; edit the `models:` section to switch providers permanently.

## Running

### Smoke test (1 world, 1 rep per condition, ~4 lineages)

```bash
cd prototype
python -m scripts.smoke_test
```

Expected behavior: 4 runs, all valid, total cost near $0 on Ollama or ~$0.01–0.05 on Haiku/gpt-4o-mini. Trace written to `outputs/smoke_test.trace.jsonl`.

### Full prototype (20 worlds, 1 rep per condition default)

```bash
cd prototype
python -m scripts.run_prototype
# or, with more replications:
python -m scripts.run_prototype --reps 3
```

Expected output: 80 runs (20 worlds × 4 conditions × 1 rep) at default. Cost depends on provider: roughly free on Ollama, ~$1–5 on Haiku, ~$5–15 on GPT-4o-mini.

### After a run, build the analysis layer

```bash
python -m scripts.build_etl --trace outputs/chain_hub_proto_v0_1.trace.jsonl
python -m scripts.build_audit --trace outputs/chain_hub_proto_v0_1.trace.jsonl --mode both --n 6
```

Then query DuckDB directly:

```bash
duckdb outputs/chain_hub_proto_v0_1.duckdb
> SELECT condition, AVG(feature_value)
  FROM features
  WHERE feature_name = 'semantic_drift_from_original'
  GROUP BY condition;
> SELECT * FROM features_wide LIMIT 5;
```

## What to inspect first

1. **Open the audit export** (`outputs/*.audit.md`). Read 5 to 10 lineages by hand. The viewer is intentionally rendered first so you spot extractor bugs and prompt misalignments before trusting aggregates.

2. **Check the smoke test invariants.** All four runs should have `invalid: false`. Every message should have non-empty text. Every call should have a non-zero cost (unless on Ollama) or recorded token counts.

3. **Look at the per-message feature summary** in the audit. Are the residue features sensible? Is `proposition_preservation_rate` close to 1.0 for the source message and degrading by chain hop? Is `source_marker_count` reasonable?

4. **Compare chain terminal vs. one-shot summary** for the same world. Does the chain terminal show more drift, more compression, or more uncertainty loss than the one-shot? This is the key diagnostic comparison.

## Failure modes and what they mean

| Symptom | Likely cause | Diagnostic |
|---|---|---|
| All chain runs marked invalid | Local model not running, or API key missing | Check provider/model and `OLLAMA_URL` |
| `semantic_drift_from_original` is ~0 for all chain hops | Mutators are too faithful (near-verbatim relay) | Inspect prompts; consider increasing temperature or rephrasing relay prompts |
| Within-condition variance > across-condition variance | Stochastic decoding noise dominates | Increase replications, or lower temperature |
| Chain terminal features match one-shot summary features | Chain residue is not structurally entailed (failure case for the theory) | Inspect lineages by hand to verify mutators are actually relaying |
| `proposition_preservation_rate` is unreliable | Embedding threshold is wrong for this domain | Hand-code 10 lineages, recalibrate `SIM_PRESERVED_MIN` in `proposition_matcher.py` |
| `unsupported_addition_count` is high in all conditions | Source generator is hallucinating beyond the proposition list | Lower temperature on `source_generator`, or tighten the source prompt |
| Skeptical features (type-token ratio, mean sentence length) discriminate regimes as well as target features | Structural effects are mostly stylistic; theory is in trouble | Pre-registered failure mode; investigate before scaling |

## Precommitted thresholds

The config carries pre-registered targets for the key tests, copied here for visibility. Compare these against post-run results rather than retrofitting thresholds to the data.

- chain hop slope for `proposition_preservation_rate`: |Spearman ρ| ≥ 0.5
- chain hop slope for `uncertainty_marker_count`: |Spearman ρ| ≥ 0.4
- chain hop slope for `semantic_drift_from_original`: ρ ≥ 0.5
- hub conflict-repair fraction (conflict NOT preserved in terminal): ≥ 0.5
- hub source-marker loss (terminal < min(inputs)): ≥ 0.5
- residue classifier vs. structure-blind baseline: balanced-accuracy delta ≥ 0.15
- skeptical features alone classifier: balanced-accuracy delta ≤ 0.05

## What this prototype does NOT do

- No receiver-inference experiment yet (P5-P8 of the structural-legibility propositions remain untested).
- No human-rater workflow (but every lineage is exportable for later human coding).
- No adversarial-mimicry baseline (worth adding once basic residue signal is confirmed).
- No model-family separation in default config (architecture supports it; default uses one cheap mutator family for cost reasons).
- No multi-prompt-phrasing test of effect robustness across phrasings (variants cycle but the harness does not yet contrast a run with the same world under prompt variant A vs. C explicitly). This is a near-term extension.
- No emotional-salience moderator, no political content, no real-world events.
- No publication-ready analysis. The prototype produces queryable data for the analysis pass.

## Versioning policy

Every component carries a `_v0_1` suffix. Versioning is by component, not by experiment-wide schema. When bumping a component:

1. Bump the suffix on the relevant file(s).
2. Update the `component_versions:` block in the config.
3. Re-extract all features on any prior raw traces if the extractor changed. Never overwrite old features.
4. Keep old versions on disk. New runs cite new versions in their trace.

## License and authorship

Research artifact accompanying a manuscript under anonymized peer review. License and authorship details will be added upon publication.
