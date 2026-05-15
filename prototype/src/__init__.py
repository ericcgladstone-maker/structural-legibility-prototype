"""Structural legibility prototype harness.

Modules:
    model_client       Dispatch to Ollama, Anthropic, OpenAI, or local embeddings.
    world_loader       Load and validate worlds from JSONL.
    proposition_matcher Match world propositions against rendered messages.
    residue_extractor  Compute per-message residue features.
    trace_writer       Append-only JSONL trace writer with assertion guards.
    run_experiment     Main harness: config -> trace.
    etl                JSONL trace -> Parquet feature tables -> DuckDB.
    audit_export       Markdown audit-export builder.
"""
