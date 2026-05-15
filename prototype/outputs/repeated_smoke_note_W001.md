# Repeated Smoke Validation Note (W001 × 5 reps)

*Compiled 2026-05-13. Source: `chain_hub_proto_v0_1_smoke.trace.jsonl`, 20 runs, 5 reps × 4 conditions × 1 world, Ollama `llama3.1:8b`, total cost $0.00.*

This is a matcher and extractor stability check, not a substantive test of structural legibility. The N is 1 world. Patterns reported here are only about whether the pipeline behaves coherently across repeated stochastic mutator outputs.

## 1. Causal-flip detection: working as intended

Across all 15 chain terminal-or-intermediate messages (5 reps × 3 hops), the matcher labels p3 (true: cooling-system cause) as **contradicted** and p4 (false: sensor-fault cause) as **preserved**. 15 out of 15, every hop. Zero misses, zero swaps.

```
chain_3hop hop=1   p3 contradicted 5/5   p4 preserved 5/5
chain_3hop hop=2   p3 contradicted 5/5   p4 preserved 5/5
chain_3hop hop=3   p3 contradicted 5/5   p4 preserved 5/5
```

The matcher's conflict-partner logic is doing exactly the work it should. When the terminal message asserts the *false* alternative more strongly than the true cause, the matcher labels the true cause as contradicted (not as preserved-but-altered, not as omitted). The label transitions cleanly with the conflict partner's similarity exceeding the contradicted threshold.

Two substantive notes that follow but should be flagged separately:

- The flip happens at hop 1 already. The chain mutator under llama3.1:8b reliably promotes the alternative cause to "most likely" at the first hop, then preserves that flipped framing through subsequent hops. There is no progressive drift toward p4. The flip is essentially complete at hop 1.
- The hub condition is more variable. Of 5 hub runs: p3 was labeled **altered** in 3 and **contradicted** in 2; p4 was labeled **preserved** in 2, **altered** in 1, **contradicted** in 2. The hub synthesizer sometimes preserves both causal hypotheses, sometimes picks one, sometimes phrases the integration vaguely enough that neither matches strongly. Across the 5 reps, `conflict_pairs_preserved` was 1 out of 5 (with the other 4 classified as repaired). This is the dissociation P8 predicts in miniature.

Both findings are tentative on N=1 world. They serve only to confirm the matcher is producing differentiated labels for differentiated outputs.

## 2. Feature stability across repetitions

| feature | chain hop 1 | chain hop 2 | chain hop 3 | hub | 1-shot summary | 1-shot synthesis |
|---|---|---|---|---|---|---|
| `proposition_preservation_rate` (mean / sd) | 0.85 / 0.06 | 0.85 / 0.06 | 0.85 / 0.06 | 0.875 / 0.09 | 0.875 / 0.00 | 0.80 / 0.11 |
| `semantic_drift_from_original` | 0.031 / 0.014 | 0.053 / 0.022 | 0.048 / 0.011 | 0.091 / 0.027 | 0.035 / 0.014 | 0.076 / 0.013 |
| `uncertainty_marker_count` | 0.8 / 0.84 | 0.8 / 0.45 | 0.2 / 0.45 | 0.8 / 0.84 | 0.6 / 0.55 | 0.0 / 0.00 |
| `evidential_marker_count` | 0.4 / 0.55 | 0.6 / 0.89 | 0.4 / 0.55 | 1.0 / 0.71 | 0.8 / 0.45 | 1.0 / 1.00 |
| `source_marker_count` | 0.2 / 0.45 | 0.4 / 0.55 | 0.4 / 0.55 | 0.6 / 0.55 | 0.4 / 0.55 | 0.6 / 0.55 |
| `hedge_count` | 2.2 / 1.10 | 2.4 / 0.55 | 2.6 / 1.14 | 3.8 / 0.84 | 1.4 / 0.55 | 3.8 / 0.84 |
| `token_count` | 115.2 / 13.5 | 124.8 / 10.6 | 114.0 / 23.1 | 153.8 / 23.3 | 101.8 / 4.5 | 132.8 / 11.1 |

Directional read:

- `proposition_preservation_rate` is **flat across chain hops** at 0.85 with sd 0.06. The matcher is stable. The theory-relevant interpretation (chain should show monotonic loss) is *not* supported here. This is the most interesting early signal, but it is on one world.
- `semantic_drift_from_original` is roughly monotonic at hop 1 to 2 (0.031 → 0.053) and dips slightly at hop 3 (0.048). The directional trend is consistent with the prediction across repetitions, but the magnitudes are small.
- `uncertainty_marker_count` drops from 0.8 at hops 1 and 2 to 0.2 at hop 3 in chain. Suggestive of cumulative uncertainty loss, but high variance.
- `hedge_count` is *higher* in hub and one-shot synthesis (3.8 each) than in chain (~2.3) or one-shot summary (1.4). This is a content-coherent pattern: synthesizing across heterogeneous inputs invites hedging language.
- `evidential_marker_count` and `source_marker_count` are noisy. Variance across the 5 reps is substantial relative to means. The dictionary lookup is matching the locked entries, but conditions are not strongly differentiated on this metric at N=5.

## 3. Baseline length-matching is plausible

Target lengths were computed from stage-1 medians: chain median 111 tokens (→ one-shot summary target), hub median 146 tokens (→ one-shot synthesis target). Measured baselines:

- one-shot summary: 101.8 tokens (sd 4.5). 92% of target. Tight.
- one-shot synthesis: 132.8 tokens (sd 11.1). 91% of target. Acceptable.

Both baselines are slightly under target. The mutator interprets the `approximately {target_length} words` instruction conservatively. This is fine for prototype use as length-matched baselines, but if precise matching matters for any downstream comparison the prompt could be tightened (e.g. "approximately N words, no fewer than M").

## 4. Trace field completeness: 100%

```
runs missing run_stage:                  0/20
messages missing is_source_message:      0
non-source msgs missing parents:         0
calls missing input_tokens:              0
calls missing usd_cost:                  0
calls missing logprobs.available field:  0
messages missing prompt_variant:         0
runs missing feature_extractions:        0
```

Every required field is populated across all 20 runs. The trace assertion catches malformed messages on write (verified during static validation with a deliberately-bad run).

The two-stage plan is recorded correctly:
- stage1_structural: 10 runs (5 chain + 5 hub)
- stage2_baseline: 10 runs (5 one-shot summary + 5 one-shot synthesis)

`run_order_index` documents the queue position from the shuffled task list. Stage-1 and stage-2 are interleaved at the queue level but executed in two passes (stage-1 first to compute median targets, stage-2 second using those targets). This is by design and is the right pragmatic choice. Inside each stage the conditions remain interleaved.

## 5. Audit export readability

The audit export wrote 16 lineages (8 unblinded + 8 blinded) with randomized opaque IDs. Each lineage shows:
- world state JSON (in unblinded only)
- proposition list with (truth, uncertainty, evidence_type, centrality) tags
- message lineage with `[role | source]` or `[role | transformed]` tags
- per-message automated feature summary
- per-proposition match classification with similarity scores
- blank "Human notes" section

Spot-checked: the chain lineage from rep 1 (audit ID `54BE74`) is readable end-to-end. A future human coder can confirm or reject any automated classification with the full source-observation, intermediate-message, and similarity context visible on one screen.

## 6. Skeptical-feature behavior (internal control)

The skeptical features were included to detect the case where "structural" effects are mostly stylistic surface artifacts. Across the 5 reps:

| skeptical feature | chain | hub | 1-shot summary | 1-shot synthesis |
|---|---|---|---|---|
| `type_token_ratio` | 0.755 | 0.690 | 0.771 | 0.736 |
| `mean_sentence_length` | 20.4 | 22.5 | 17.6 | 20.6 |
| `mean_word_length` | 5.44 | 5.41 | 5.45 | 5.57 |
| `punctuation_density` | 0.017 | 0.014 | 0.017 | 0.019 |

Type-token ratio separates hub (0.690) from one-shot summary (0.771). Mean sentence length separates one-shot summary (17.6) from the others (~20-22). These differences are real and should be expected: synthesis tasks produce longer, more vocabulary-dense outputs than short summaries. The prediction for the full pilot is that residue features must beat a structure-blind baseline using *these* features. This smoke does not test that yet (N is too small), but the differences are large enough that the structure-blind baseline will not be trivial to beat.

## Verdict: ready to scale

The matcher and extractor are coherent across repeated stochastic outputs on W001. The causal-flip detection is reliable. Feature distributions are stable enough across reps to support eventual aggregate analysis. Trace fields are complete. Baselines are plausibly length-matched. Audit export is readable.

Two substantive observations to bookmark for the full-pilot analysis, both contingent on much larger N:

1. **Chain may not show monotonic propositional loss** under this model. The flat 0.85 preservation rate at every hop in W001 is striking. If it reproduces across worlds, it suggests either that (a) llama3.1:8b is a near-faithful relayer for propositional content even when it inverts causal stance, or (b) the proposition matcher's similarity threshold is too generous and is absorbing alterations as preservations. Worth examining in the full run with hand-coded validation on a sample.
2. **Hub conflict-preservation rate of 1/5** is intriguing but unstable at N=5. The full pilot will tell whether this is roughly 20% across worlds (P8 dissociation prediction) or essentially zero.

No fixes required before scaling. Run the full 20-world prototype with `--fresh`.
