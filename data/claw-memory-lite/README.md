# claw-memory-lite

> Lightweight Long-Term Memory for OpenClaw — SQLite-Powered, Zero External Dependencies, Millisecond Queries

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Built%20for-OpenClaw-blue)](https://github.com/openclaw/openclaw)

## Why claw-memory-lite?

OpenClaw's native `memory/*.md` approach works great initially, but as memory files accumulate:

- ❌ Every session loads all markdown files — slow and token-heavy
- ❌ Text-based search is inefficient
- ❌ No structured indexing or categorization

**claw-memory-lite** solves this with:

- ✅ **SQLite Storage** — Query in <10ms, no external vector DB needed
- ✅ **L0/L1/L2 Hierarchy** — Inspired by OpenViking, but lightweight (~200 lines)
- ✅ **Auto-Extraction** — Cron/heartbeat-based, zero manual maintenance
- ✅ **Zero External Dependencies** — Pure Python `sqlite3` (built-in)
- ✅ **Privacy-First** — All data stays local, no API calls

## Quick Start (Recommended)

### 1. Installation

The easiest way is to add it as a standard OpenClaw Skill:

```bash
npx skills add timothysong0w0/claw-memory-lite --agent openclaw
```

### 2. Initialize Database

```bash
# Run extraction script once (creates database automatically)
python ~/.openclaw/extensions/claw-memory-lite/scripts/extract_memory.py
```

### 3. Configure Automation

Add the following to your `HEARTBEAT.md` to enable daily memory extraction:

```bash
python ~/.openclaw/extensions/claw-memory-lite/scripts/extract_memory.py
```

---

## Manual Installation (Alternative)

If you prefer to manage scripts manually:

```bash
# Clone the repository
git clone https://github.com/timothysong0w0/claw-memory-lite.git

# Copy scripts to your workspace
cp claw-memory-lite/scripts/*.py /home/node/.openclaw/workspace/scripts/
```

Usage for manual installation:
- Search: `python scripts/db_query.py [keyword]`
- Extract: `python scripts/extract_memory.py`

---

## Usage (Skill Mode)

### Search by Keyword
```bash
python ~/.openclaw/extensions/claw-memory-lite/scripts/db_query.py [SEARCH_TERM]
```

### Filter by Category
```bash
python ~/.openclaw/extensions/claw-memory-lite/scripts/db_query.py --category Skill
```

## Categories

| Category | Description |
|----------|-------------|
| `System` | Session configuration, model aliases, compatibility rules |
| `Environment` | Workspace paths, backup rules, tool policies |
| `Skill` | Skill configurations, API endpoints, known issues |
| `Project` | Project status, strategy parameters, TODOs |
| `Comm` | Channel mappings, notification rules, bot configs |
| `Security` | Access control principles, audit log locations |

## L0/L1/L2 Hierarchy

claw-memory-lite adopts a simplified 3-tier structure inspired by OpenViking:

### L0 — Abstract (One-Line Summary)

A single sentence capturing the core essence. Used for quick scanning.

### L1 — Overview (Category Index)

Categorized summaries (2-3 sentences) for decision-making during planning.

### L2 — Details (Full Content in DB)

Complete factual records stored in SQLite, queryable on demand.

## Comparison: claw-memory-lite vs OpenViking

| Feature | claw-memory-lite | OpenViking |
|---------|------------------|------------|
| **Target** | OpenClaw-specific | General Agent context |
| **Dependencies** | None (sqlite3 built-in) | Embedding + VLM models |
| **Storage** | SQLite | Vector DB + Filesystem |
| **Retrieval** | SQL + Category Filter | Vector search + Directory recursion |
| **Complexity** | Low (~200 LOC) | High (full framework) |
| **Token Optimization** | Query-on-demand (no pre-loading) | L0/L1/L2 layered loading |
| **Best For** | Conversation memory, config logs | Document/codebase management |

## Performance Benchmarks

| Operation | Time |
|-----------|------|
| Database query (keyword) | <5ms |
| Database query (category) | <2ms |
| Auto-extraction (per file) | ~50ms |
| Initial DB creation | ~100ms |

*Benchmarked on Linux x64 with 30+ memory records*

## Roadmap

- [ ] Add `--export` flag to dump DB to JSON/Markdown
- [ ] Integration with OpenClaw's native `memory_search` tool

**Contributions welcome!** Have ideas or want to help? Open an issue or submit a PR.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

For detailed acknowledgments and inspiration sources, see [CREDITS.md](CREDITS.md).

## Acknowledgments

- **鸿蒙小张** (Xiaohongshu/RedNote blogger) — Original inspiration for this project's core concept. This implementation was created with permission and based on his ideas.
- [OpenViking](https://github.com/volcengine/OpenViking) by ByteDance — Inspiration for the L0/L1/L2 hierarchy structure and context management paradigm.
- [OpenClaw](https://github.com/openclaw/openclaw) — The AI agent framework this is built for.

---

**Built with us for OpenClaw users who value speed, privacy, and simplicity.**
