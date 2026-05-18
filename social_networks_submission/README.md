# Social Networks submission — replication materials

This folder contains the anonymized replication package and rendered figures for the manuscript *Inferring Communication Topology from Message Residue*, submitted to *Social Networks*.

## Contents

- `replication_package/` — source code, prompts, configuration files, and a data manifest describing the four JSONL streams (~140 MB) used in the analyses. See `replication_package/README.md` for reproducibility instructions and `replication_package/data_manifest/README.md` for data-file descriptions.
- `figures/` — six rendered figures (PDF and PNG, 300 dpi) as referenced by the manuscript:
  - `figure_1` — Inverse topology inference design (conceptual schematic)
  - `figure_2` — Eight production graph motifs (directed graphs)
  - `figure_3` — Topology recovery by reader type
  - `figure_4` — Recoverability by graph motif
  - `figure_5` — Confusion matrices for both readers
  - `figure_6` — Trace observability + accuracy-posterior decoupling

## What is NOT here

- The manuscript itself, title page, and submission-portal-specific files (highlights, declarations) are not included. Those go through the journal's submission system.
- The raw JSONL data files (~140 MB total) are described in the `data_manifest/` but are hosted separately due to size.

## License

Code released under the MIT License upon publication. Data released under CC-BY-4.0.
