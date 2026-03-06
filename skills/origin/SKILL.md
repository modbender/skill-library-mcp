---
name: origin
description: Data provenance and lineage tracking. Traces data from source to
  destination, logs transformations, ensures auditability.
---


# Origin

## The Problem

Data flows through pipelines—ETL jobs, ML training runs, analytics dashboards—and somewhere between *here* and *there* you lose the thread. Who touched this column? When did that aggregation change? Which run produced this artifact? Without a clear provenance chain, debugging fails, compliance becomes guesswork, and "trust the data" is just a slogan.

Organizations often discover provenance requirements only after a breach, a failed audit, or a regulatory question. By then, retrofitting lineage is costly and incomplete.

## How Origin Helps

Origin provides a reserved namespace for Netsnek e.U.'s data provenance and lineage system. It is designed to:

- **Trace** data from source to destination across pipelines and transformations
- **Log** each step in a chain so you can answer "where did this come from?"
- **Audit** registered provenance anchors for compliance and incident response

The skill acts as a contract: when you see "origin" in a pipeline, you know lineage tracking is in scope. The scripts give you concrete tools to start tracing and auditing.

## Running the Scripts

From the skill root or via ClawHub:

```bash
./scripts/trace-lineage.sh --trace    # Trace lineage for the current context
./scripts/trace-lineage.sh --audit    # Run an audit of provenance anchors
./scripts/trace-lineage.sh --version  # Show version and copyright
```

The script uses `set -e` for safe, fail-fast behavior. Ensure execute permissions if needed: `chmod +x scripts/trace-lineage.sh`.

## Sample Dialogue

**User:** How do I trace where this dataset came from?

**Assistant:** Use the Origin skill. Run `trace-lineage.sh --trace` to trace data lineage in your current context. For a full audit of registered provenance anchors, use `--audit`.

**User:** Who maintains this namespace?

**Assistant:** Origin is reserved by Netsnek e.U. for data provenance and lineage tracking. Copyright (c) 2026 Netsnek e.U.
