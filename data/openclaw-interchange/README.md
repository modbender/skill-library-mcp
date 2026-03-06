# @openclaw/interchange

[![Tests](https://img.shields.io/badge/tests-32%20passing-brightgreen)]() [![Node](https://img.shields.io/badge/node-%3E%3D18-blue)]() [![License: MIT](https://img.shields.io/badge/license-MIT-yellow)]()

> The shared .md interchange library that every OpenClaw skill builds on.

Interchange provides atomic file I/O, deterministic serialization, YAML frontmatter parsing, advisory locking, and schema validation for `.md` interchange files. It's the foundation layer — ensuring that every skill speaks the same language and every write is crash-safe.

## Features

- **Atomic writes** — tmp + fsync + rename protocol prevents partial writes
- **Deterministic serialization** — same input always produces byte-identical output
- **YAML frontmatter** — read/write structured metadata in `.md` files
- **Advisory locking** — prevent concurrent writes from multiple agents
- **Schema validation** — validate frontmatter and interchange layers
- **Content hashing & generations** — track changes with generation IDs and content hashes
- **Staleness detection** — check if interchange files need regeneration
- **DB-to-interchange reconciliation** — sync database state to `.md` files
- **Circuit breaker** — resilient I/O with automatic failure detection
- **Helpers** — slugify, table formatting, currency formatting, relative time

## Quick Start

```bash
cd skills/interchange
npm install
```

```js
import { readMd, writeMd, acquireLock, releaseLock, validateFrontmatter } from '@openclaw/interchange';

// Read a .md interchange file
const doc = readMd('path/to/file.md');
console.log(doc.frontmatter, doc.body);

// Atomic write with frontmatter
writeMd('path/to/output.md', {
  frontmatter: { type: 'report', generated: new Date().toISOString() },
  body: '## Summary\nAll systems operational.'
});

// Advisory locking
const lock = acquireLock('path/to/file.md');
try {
  // ... safe writes ...
} finally {
  releaseLock(lock);
}
```

## API Reference

| Export | Description |
|--------|-------------|
| `readMd(path)` | Parse `.md` file into `{ frontmatter, body }` |
| `writeMd(path, doc)` | Atomic write with YAML frontmatter |
| `atomicWrite(path, content)` | Raw atomic write (tmp → fsync → rename) |
| `acquireLock(path)` / `releaseLock(lock)` | Advisory file locking |
| `validateFrontmatter(data, schema)` | Validate frontmatter against a schema |
| `validateLayer(layer)` | Validate interchange layer structure |
| `nextGenerationId()` | Generate a new generation ID |
| `contentHash(content)` | SHA-256 content hash |
| `serializeFrontmatter(obj)` | Deterministic YAML serialization |
| `serializeTable(rows)` | Deterministic markdown table |
| `updateIndex(dir)` / `rebuildIndex(dir)` | Maintain interchange indexes |
| `listInterchange(dir)` | List all interchange files in a directory |
| `isStale(path, db)` | Check if a file needs regeneration |
| `reconcileDbToInterchange(db, dir)` | Sync DB state → `.md` files |
| `CircuitBreaker` | Resilient I/O wrapper |
| `slugify(str)` | URL-safe slug from string |
| `formatTable(rows)` / `formatCurrency(n)` / `relativeTime(date)` | Formatting helpers |

## Architecture

Pure JavaScript library (no database, no CLI). Exports functions that other skills import to read, write, and validate `.md` interchange files. All I/O follows the atomic write protocol to prevent corruption.

## Testing

```bash
npm test
```

32 tests covering atomic writes, deterministic serialization, frontmatter parsing, locking, schema validation, indexing, staleness detection, reconciliation, and circuit breaker behavior.

## Part of the OpenClaw Ecosystem

This is the foundation package. Every other OpenClaw skill (`orchestration`, `monitoring`, `crm`, `ecommerce`, `voice`) depends on `@openclaw/interchange` for reading and writing `.md` interchange files.

## License

MIT
