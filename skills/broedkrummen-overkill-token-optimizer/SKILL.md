# Overkill Token Optimizer

Token optimization for OpenClaw agents. Reduces token usage through CLI compression, session management, and memory optimization.

## Prerequisites

**Required:** `oktk` CLI must be installed manually:

```bash
npm install -g oktk
```

Or see: https://github.com/satnamra/oktk

## Features

- **Token stats** - View session token usage
- **Session indexing** - Index old sessions for search
- **Hybrid search** - Semantic + keyword search
- **CLI compression** - Compress command outputs (requires oktk)

## CLI Commands

```bash
# Show token usage statistics
token-optimizer stats

# Check optimization level
token-optimizer check

# Index sessions for search
token-optimizer index

# Search sessions (use --hybrid for semantic+keyword)
token-optimizer search "query" --hybrid

# Compress command output (requires oktk)
token-optimizer compress git status
```

## Configuration

Set custom oktk path:
```bash
export OKTK_BIN=/path/to/oktk
```

## Storage

- Session index: `~/.openclaw/workspace-memory-builder/.session_index/`

---

*Overkill Token Optimizer v1.0.3*
