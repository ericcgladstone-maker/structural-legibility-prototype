# Paired bootstrap confidence intervals and prediction-label entropy

Paired bootstrap intervals over 5,000 resamples of trial-level correct or not. Predictions are matched per trial (paired). Manuscript-reported point estimates are reproduced as the column-mean values; the intervals quantify uncertainty around the paired gap.

## 1. Form-aligned classifier minus content-attentive reader on the F1 test split

- Paired n = 840
- Form-aligned accuracy: 0.6119
- Content-attentive accuracy: 0.2726
- Paired difference (form-aligned minus content-attentive): 0.3393 (95% bootstrap CI 0.2976 to 0.3821)
- The interval excludes zero, so the paired gap is reliably positive.

## 2. 14-feature classifier minus length-only baseline on the F1 test split

- Paired n = 840
- 14-feature accuracy (refit): 0.6119
- Length-only (token_count + sentence_count) accuracy (refit): 0.5214
- Paired difference (full minus length-only): 0.0905 (95% bootstrap CI 0.0607 to 0.1190)
- The interval excludes zero, confirming that features beyond message length contribute load-bearing recovery.

## 3. Predicted-label entropy

Entropy of the marginal distribution over predicted motif labels, in bits, capped at log2 8 = 3.00 bits when the eight labels are used equally.

| Slice | Reader | n | Entropy (bits) |
|---|---|---:|---:|
| F1 (qwen2.5:7b primary) | Content-attentive | 840 | 1.68 |
| F1 (qwen2.5:7b primary) | Form-aligned | 840 | 2.36 |
| F2 (llama3.1:8b cross-family) | Content-attentive | 89 | 2.23 |
| F2 (llama3.1:8b cross-family) | Form-aligned | 92 | 2.12 |

The content-attentive readers compress their predictions onto a small subset of the motif vocabulary (vocabulary collapse), while the form-aligned classifier distributes predictions across more of the eight labels. The same pattern recurs on the cross-family slice.
