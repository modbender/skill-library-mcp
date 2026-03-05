---
name: openclaw-universal-memory
description: Connector-agnostic Postgres + pgvector memory ingestion and retrieval with incremental cursor history.
---

# OpenClaw Universal Memory

This skill provides a generic memory layer for heterogeneous data:
- canonical entity/chunk schema,
- connector-style ingestion with cursors,
- searchable memory in Postgres.

## Use Cases

- Normalize records from multiple systems into one schema.
- Keep incremental sync history (`cursor` per connector/account).
- Build RAG-ready chunk storage in pgvector.

## Prerequisites

- Postgres with `vector` extension.
- Local package installed: `pip install -e .`.
- Python dependency for DB I/O:
  - `pip install "psycopg[binary]>=3.2"`
- DSN provided via environment variable (`DATABASE_DSN` by default).

## Security Boundaries

- Do not pass raw passwords/tokens in command-line arguments.
- Prefer OS secret store or process environment injection for DSN.
- This skill only reads/writes your configured Postgres database; it does not call external APIs directly.
- Use least-privilege DB credentials (`SELECT/INSERT/UPDATE/DELETE` on `um_*` tables only).
- Review and trust any custom connector before running it.

## Responsible Use Caveat

- Use this only for accounts/data you legitimately control or are authorized to process.
- You are responsible for privacy, retention, and regulatory compliance.
- This project is provided under Apache 2.0 without operational warranty.
- This implementation is mostly AI-generated code with experienced engineer oversight; validate before production use.

## Commands

Store DB credentials once (recommended):

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action configure-dsn
```

Initialize schema:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action init-schema \
  --dsn-env DATABASE_DSN
```

Ingest JSON/NDJSON:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action ingest-json \
  --dsn-env DATABASE_DSN \
  --source gmail \
  --account marcos@athanasoulis.net \
  --entity-type email \
  --input /path/to/records.ndjson
```

Ingest from built-in connectors:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action ingest-connector \
  --connector google \
  --account you@example.com \
  --dsn-env DATABASE_DSN \
  --limit 300
```

Validate connector auth/config before ingest:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action validate-connector \
  --connector google \
  --account you@example.com \
  --dsn-env DATABASE_DSN \
  --limit 1
```

Search:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action search \
  --dsn-env DATABASE_DSN \
  --query "Deryk" \
  --limit 20
```

Recent ingest history:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action events \
  --dsn-env DATABASE_DSN \
  --limit 20
```

Doctor check:

```bash
python skills/openclaw-universal-memory/scripts/run_memory.py \
  --action doctor
```

Scheduling reference:
- `docs/SCHEDULING.md` (cron examples, 15-minute default, connector toggles)

## Connector Contract (for custom adapters)

A connector returns normalized records + next cursor:

- `external_id`
- `entity_type`
- `title`
- `body_text`
- `raw_json`
- `meta_json`
- `next_cursor`

This keeps ingestion generic and supports arbitrary source systems.

Starter connector templates:
- `src/openclaw_memory/connectors/templates.py`

Step-by-step setup guide (Gmail/Slack/Asana/iMessage):
- `docs/CONNECTOR_SETUP_WALKTHROUGH.md`


## Community

We welcome connector contributions via PR.
See `docs/CONNECTOR_CONTRIBUTING.md` for required contract, tests, and setup instructions.
