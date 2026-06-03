# Nature Communications submission — replication materials

Anonymized for double-blind peer review.

This folder contains rendered figures and analysis scripts for the manuscript *Message residue preserves traces of hidden communication structure*, prepared for submission to *Nature Communications*. The manuscript file itself is not included here. The earlier Social Networks submission materials for the same project are in the sibling `social_networks_submission/` folder of this repository, and the underlying apparatus is in the `prototype/` folder.

## Contents

- `03_figures/main/` — four rendered main figures (vector PDF + 600-dpi PNG):
  - `Figure_1` — inverse problem and residue classes (two-row schematic, residue card, scope).
  - `Figure_2` — eight production motifs as directed graphs (2x4 grid, natural-language labels, node-type legend).
  - `Figure_3` — motif recoverability and reader-instrument alignment. Panel a is the alignment scatter of form-aligned classifier accuracy versus content-attentive reader accuracy, one labeled motif per point, with Wilson 95% CI crosses. Panel b is the paired bars per motif, sorted by form-aligned accuracy.
  - `Figure_4` — alignment diagnostics. Panel a, full 14-feature versus length-only classifier. Panel b, F1 versus F2 cross-reader-family comparison. Panel c, trace observability sweep across L1, L3, L5, L6.
- `03_figures/scripts/` — figure-generating Python scripts:
  - `figure_style.py` is the shared style module (palettes, fonts, Wilson 95% CI helper, JSONL data loaders).
  - `make_figure_1.py` through `make_figure_4.py` build the four main figures.
  - `make_si_figure_1.py` through `make_si_figure_3.py` build the three supplementary figures.
- `05_supplementary_information/figures/` — three supplementary figures (PDF + PNG):
  - `Supplementary_Figure_1` — aggregate motif-class recovery by reader type and family.
  - `Supplementary_Figure_2` — row-normalized confusion matrices for both readers on the F1 primary test trials (n = 840), with raw cell counts annotated, the diagonal outlined, and predicted-label Shannon entropy reported beneath each panel.
  - `Supplementary_Figure_3` — fidelity-posterior versus source-content preservation scatter across n = 4,197 post-validation primary trials, Pearson r = +0.029.
- `05_supplementary_information/bootstrap_and_entropy.md` — paired bootstrap 95% confidence intervals for two accuracy gaps and predicted-label entropy values for both reader families.
- `05_supplementary_information/scripts/bootstrap_and_entropy.py` — script that reproduces the bootstrap intervals and entropy values reported in the above document.

## What is NOT here

- The manuscript markdown, title page, cover letter, and submission-portal-specific files are not included. Those are handled through the journal's submission system.
- The raw JSONL data files (~140 MB total) are described in the sibling `social_networks_submission/replication_package/data_manifest/README.md` and are hosted separately by size. The figure and bootstrap scripts assume those files are available at `prototype/outputs/` in the original project layout.

## Reproducibility

The figure scripts and the bootstrap script read per-trial data from JSON Lines streams (lineage, trace packets, receiver outputs with the validator's invalid flag preserved per trial, ground-truth labels, terminal-feature extractions, and the trained classifier's per-trial test-split predictions). With those streams in place at the expected path, every reported number in the four main figures, in the three supplementary figures, and in `bootstrap_and_entropy.md` is reproducible by running the corresponding script.

Because language-model decoding is stochastic, the reproducibility standard for the upstream generation step is distributional, the same statistical patterns over multiple runs, rather than exact byte-equivalence of specific outputs.

## License

Code released under the MIT License upon publication. Data released under CC-BY-4.0.
