---
name: surreal-sync
description: "Data migration and synchronization to SurrealDB from MongoDB, PostgreSQL, MySQL, Neo4j, Kafka, and JSONL. Full and incremental CDC sync. Part of the surreal-skills collection."
license: MIT
metadata:
  version: "1.0.4"
  author: "24601"
  parent_skill: "surrealdb"
  snapshot_date: "2026-02-19"
  upstream:
    repo: "surrealdb/surreal-sync"
    release: "v0.3.4"
    sha: "8166b2b041b1"
---

# Surreal-Sync -- Data Migration and Synchronization

Surreal-Sync is a CLI tool for migrating data from various database sources to
SurrealDB with full and incremental synchronization via Change Data Capture (CDC).

## Supported Sources

| Source | Full Sync | Incremental CDC | Method |
|--------|-----------|----------------|--------|
| MongoDB | Yes | Yes | Change streams |
| MySQL | Yes | Yes | Trigger-based CDC + sequence checkpoints |
| PostgreSQL (triggers) | Yes | Yes | Trigger-based CDC + sequence checkpoints |
| PostgreSQL (wal2json) | Yes | Yes | Logical replication with wal2json plugin |
| Neo4j | Yes | Yes | Timestamp-based tracking |
| JSONL Files | Yes | N/A | Batch import from JSON Lines |
| Apache Kafka | Yes | Yes | Consumer subscriptions with deduplication |

## Quick Start

```bash
# Install surreal-sync (Rust binary)
cargo install surreal-sync

# Full sync from PostgreSQL (trigger-based)
surreal-sync from postgres trigger-full \
  --connection-string "postgresql://user:pass@localhost/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace prod \
  --to-database main

# Incremental CDC from PostgreSQL (wal2json)
surreal-sync from postgres wal2json \
  --connection-string "postgresql://user:pass@localhost/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace prod \
  --to-database main

# Full sync from MongoDB
surreal-sync from mongo full \
  --connection-string "mongodb://localhost:27017/mydb" \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace prod \
  --to-database main

# Batch import from JSONL
surreal-sync from jsonl import \
  --file data.jsonl \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace prod \
  --to-database main

# Consume from Kafka
surreal-sync from kafka consume \
  --bootstrap-servers "localhost:9092" \
  --topic my-events \
  --surreal-endpoint "http://localhost:8000" \
  --surreal-username root \
  --surreal-password root \
  --to-namespace prod \
  --to-database main
```

## CLI Pattern

```
surreal-sync from <SOURCE> <COMMAND> \
  --connection-string [CONNECTION STRING] \
  --surreal-endpoint [SURREAL ENDPOINT] \
  --surreal-username [SURREAL USERNAME] \
  --surreal-password [SURREAL PASSWORD] \
  --to-namespace <NS> \
  --to-database <DB>
```

## Key Features

- Automatic schema inference and SurrealDB table creation
- Record ID mapping from source primary keys
- Relationship extraction and graph edge creation
- Configurable batch sizes and parallelism
- Resumable sync with checkpoint tracking
- Deduplication for Kafka consumers

## Full Documentation

See the main skill's rule file for complete guidance:
- **[rules/surreal-sync.md](../../rules/surreal-sync.md)** -- source configuration, schema mapping, CDC setup, conflict resolution, and production deployment
- **[surrealdb/surreal-sync](https://github.com/surrealdb/surreal-sync)** -- upstream repository
