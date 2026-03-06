---
name: openclaw-interchange
description: Shared .md interchange library for OpenClaw skills — atomic writes, deterministic serialization, YAML frontmatter, advisory locking, and schema validation. The foundation all other OpenClaw skills build on.
---

# @openclaw/interchange

The shared library that powers agent-to-agent communication via `.md` files.

## Usage

```javascript
import { writeMd, readMd, acquireLock } from '@openclaw/interchange';

// Write an interchange file atomically
await writeMd('ops/status.md', { skill: 'crm', status: 'healthy' }, '## Status\nAll systems go.');

// Read it back
const { meta, content } = readMd('ops/status.md');
```

## Key Features
- Atomic writes (tmp + fsync + rename)
- Deterministic serialization (sorted keys, stable YAML)
- Advisory file locking with stale lock detection
- YAML frontmatter parsing
- Schema validation
- Circuit breaker pattern
- Generation tracking + content hashing
