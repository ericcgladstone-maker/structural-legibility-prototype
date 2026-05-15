# github/ — Export folder

Copied materials prepared for GitHub upload. **Not the canonical source.**

## What this is

A staging area for a clean GitHub presentation of the structural-legibility / communication-accuracy prototype. Files here are copies. Originals remain in the parent project folder.

## Refresh model

- Treat this folder as **derived**. Do not edit files here as the primary copy.
- When the parent project changes, refresh by re-copying from the canonical source, not by editing the export in place.
- Future re-exports may overwrite anything added directly here.
- A future CoMSES deposit may pull from the same staging.

## What was copied

- `prototype/` — the complete prototype tree, including:
  - `src/` — pipeline modules (`etl.py`, `model_client.py`, `proposition_matcher.py`, `residue_extractor.py`, `run_experiment.py`, `trace_writer.py`, `world_loader.py`, `audit_export.py`).
  - `scripts/` — runner scripts (`run_prototype.py`, `build_etl.py`, `build_audit.py`, `smoke_test.py`).
  - `configs/`, `dictionaries/`, `prompts/`, `schemas/`, `worlds/` — declarative config artifacts.
  - `outputs/` — smoke-run audit trail and parquet outputs (small enough to keep; useful as worked example).
  - `README.md`, `requirements.txt`, `world_state_template.md`, `residue_mapping_table.md`.
- `docs/literature_review.md`, `docs/structural_legibility_lit_review.md`, `docs/structural_legibility_lit_review_memo.md` — supporting theoretical material.

## What was deliberately excluded

- `prototype/.venv/` (~834 MB) — local Python virtual environment; **must never be in version control**. Removed after rsync inadvertently picked it up.
- `prototype/.pytest_cache/` — pytest cache directory.
- All `__pycache__/` and `*.pyc` files.

## Uncertain inclusion decisions

- **`prototype/outputs/`** — kept because the smoke run is small (~4 MB) and demonstrates expected pipeline behavior. If a clean clone-and-run experience is preferred, move outputs into a `samples/` subfolder or strip them entirely before upload.
- **`prototype/outputs/full_run.log`** — review for any API keys, account names, or sensitive paths before pushing public.
- **`docs/` literature review files** — these are full prose reviews, possibly with verbatim quotes from cited works. Confirm no fair-use issues before making public.

## Outstanding items before upload

- Add a `LICENSE` (MIT or Apache-2.0 recommended for code-heavy repos).
- Add a `CITATION.cff` once authorship/citation form is finalized.
- Scan `prototype/outputs/` and any prompt files for API keys / model IDs / project secrets.
- Confirm prompt files are OK to publish (they may encode proprietary methodology).
- Consider whether `world_state_template.md` and `worlds/worlds_v0_1.jsonl` need redaction.
