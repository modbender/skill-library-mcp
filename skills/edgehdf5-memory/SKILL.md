---
name: edgehdf5-memory
description: "HDF5-backed persistent cognitive memory for AI agents. Use when: (1) saving conversation exchanges to long-term memory, (2) searching/recalling past conversations by semantic similarity, (3) managing agent memory files — stats, export, snapshot, WAL flush, (4) generating AGENTS.md summaries from memory. Requires the `edgehdf5` CLI binary (install via `cargo install edgehdf5-cli`)."
---

# EdgeHDF5 Memory

Persistent HDF5-backed memory with vector search, BM25 hybrid retrieval, Hebbian learning, and temporal decay.

## Setup

```bash
# Install the CLI (one-time)
cargo install edgehdf5-cli
# Or from source:
cargo install --path crates/edgehdf5-cli
```

Set `EDGEHDF5_PATH` env var or pass `--path <file.h5>` to every command.

## Commands

All output is JSON for easy parsing.

### Create a memory file

```bash
edgehdf5 --path agent.h5 create --agent-id myagent --dim 384 --wal
```

### Save an entry

Pass JSON via `--json` or stdin:

```bash
edgehdf5 --path agent.h5 save --json '{"chunk":"User asked about weather","embedding":[0.1,0.2,...],"source_channel":"discord","timestamp":1700000000.0,"session_id":"s1","tags":"weather"}'
```

Embedding must match the dimension specified at creation.

### Search memory

```bash
edgehdf5 --path agent.h5 search --embedding '[0.1,0.2,...]' --query 'weather forecast' -k 5
```

Optional: `--vector-weight 0.7 --keyword-weight 0.3` (defaults).

### Recall a specific entry

```bash
edgehdf5 --path agent.h5 recall 42
```

### Stats

```bash
edgehdf5 --path agent.h5 stats
```

Returns: count, active entries, WAL pending, config details.

### Flush WAL

```bash
edgehdf5 --path agent.h5 flush-wal
```

### Generate AGENTS.md

```bash
edgehdf5 --path agent.h5 agents-md
# Or write to file:
edgehdf5 --path agent.h5 agents-md --output AGENTS.md
```

### Export all entries

```bash
edgehdf5 --path agent.h5 export
```

Outputs one JSON object per line (JSONL).

### Snapshot

```bash
edgehdf5 --path agent.h5 snapshot backup.h5
```

## Workflow: Saving Conversations

1. After each exchange, construct a `MemoryEntry` JSON with the conversation chunk and its embedding vector
2. Pipe to `edgehdf5 save`
3. The WAL (if enabled) ensures low-latency writes — flush periodically with `flush-wal`

## Workflow: Recalling Context

1. Embed the current query using your embedding model
2. Run `edgehdf5 search --embedding '[...]' --query 'user text' -k 10`
3. Use returned chunks as context for the response

## Notes

- Embeddings must be generated externally (e.g., via an embedding API or local model)
- The `.h5` file is a standard HDF5 file readable by any HDF5 library
- WAL files are stored alongside the `.h5` file as `<name>.h5.wal`
