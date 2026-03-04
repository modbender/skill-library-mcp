---
name: memory-sync
description: >
  Scrape and analyze OpenClaw JSONL session logs to reconstruct and backfill
  agent memory files. Use when: (1) Memory appears incomplete after model
  switches, (2) Verifying memory coverage, (3) Reconstructing lost memory,
  (4) Automated daily memory sync via cron/heartbeat. Supports simple
  extraction and LLM-based narrative summaries with automatic secret
  sanitization.
---

# Memory Sync

Tool for maintaining agent memory continuity across model switches with automatic secret sanitization.

## Installation

Requires Python 3.11+ and `click`:

```bash
pip install click

# Optional: for direct API summarization (only if not using OpenClaw backend)
pip install openai
```

## Quick Start

```bash
# Run directly from skill directory
python ~/.openclaw/skills/memory-sync/memory_sync.py compare

# Or create an alias for convenience
alias memory-sync="python ~/.openclaw/skills/memory-sync/memory_sync.py"

# Check for gaps
memory-sync compare

# Backfill today's memory (simple extraction - fast, no LLM)
memory-sync backfill --today

# Backfill with LLM narrative (uses OpenClaw's native model - no API key needed)
memory-sync backfill --today --summarize

# Backfill all missing
memory-sync backfill --all
```

## Commands

| Command | Description |
|---------|-------------|
| `compare` | Find gaps between session logs and memory files |
| `backfill --today` | Generate memory for current day |
| `backfill --since YYYY-MM-DD` | Backfill from date to present |
| `backfill --all` | Backfill all missing dates |
| `backfill --incremental` | Backfill only changed dates since last run |
| `extract` | Extract conversations matching criteria |
| `summarize --date YYYY-MM-DD` | Generate LLM summary for a single day |
| `transitions` | List model transitions |
| `validate` | Check memory files for consistency issues |
| `stats` | Show coverage statistics |

## Simple Extraction vs LLM Summarization

The backfill command supports two modes:

**Simple Extraction (default, without `--summarize`):**
- Fast, no LLM or API calls needed
- Extracts topics via keyword frequency analysis
- Identifies key user questions and assistant responses
- Detects decision markers from text patterns
- Produces structured output with Topics, Key Exchanges, Decisions sections
- With `--preserve`: Hand-written content is **appended** to the end of the new file
- Best for: Quick backfills, initial setup, systems without LLM access

**LLM Summarization (with `--summarize`) - Recommended:**
- Uses LLM to generate narrative summaries
- Produces coherent 2-4 paragraph prose
- Better context and insight extraction
- With `--preserve`: Existing content is **passed to the LLM** with instructions to incorporate it into the new summary, maintaining temporal order and thematic structure
- Best for: Daily automation, high-quality memory files

**Recommended for regular use:**
```bash
# Best quality: LLM summary that incorporates any existing notes
memory-sync backfill --today --summarize --preserve
```

Both modes automatically sanitize secrets before writing.

## Common Workflows

### Initial Setup

```bash
# Check what's missing
memory-sync compare

# Backfill everything (may take time)
memory-sync backfill --all
```

### Nightly Automation (Recommended)

```bash
# Best: LLM summary that incorporates any existing notes
memory-sync backfill --today --summarize --preserve

# Smart: Process only days changed since last run
memory-sync backfill --incremental --summarize --preserve

# Or use a specific backend if preferred
memory-sync backfill --today --summarize --preserve --summarize-backend anthropic
```

### Catch-Up After Gaps

```bash
# Backfill from last week to present
memory-sync backfill --since 2026-01-28 --summarize
```

### Regenerate with Preserved Content

```bash
# Keep hand-written notes when regenerating
memory-sync backfill --date 2026-02-05 --force --preserve --summarize
```

## Secret Sanitization

All content is automatically sanitized to prevent secret leakage:

- **30+ explicit patterns**: OpenAI, Anthropic, GitHub, AWS, Stripe, Discord, Slack, Notion, Google, Brave, Tavily, SerpAPI, etc.
- **Structural detection**: JWT tokens, SSH keys, database connection strings, high-entropy base64
- **Generic patterns**: API keys, tokens, passwords, environment variables
- **Defense-in-depth**: Secrets redacted at every stage (extraction, LLM processing, file writes, CLI display)

Secrets are replaced with `[REDACTED-TYPE]` placeholders.

See `SECRET_PATTERNS.md` for complete pattern list.

## Summarization Backends

The `--summarize` flag supports multiple backends via `--summarize-backend`:

| Backend | Description | API Key Required |
|---------|-------------|------------------|
| `openclaw` (default) | Uses OpenClaw's `sessions spawn` with your configured model | No |
| `anthropic` | Direct Anthropic API via openai package | `ANTHROPIC_API_KEY` |
| `openai` | Direct OpenAI API via openai package | `OPENAI_API_KEY` |

### Examples

```bash
# Default: use OpenClaw's native model (no API key needed)
memory-sync backfill --today --summarize

# Explicit backend selection
memory-sync backfill --today --summarize --summarize-backend openclaw
memory-sync backfill --today --summarize --summarize-backend anthropic
memory-sync backfill --today --summarize --summarize-backend openai

# Override model for any backend
memory-sync backfill --today --summarize --model claude-sonnet-4-20250514
memory-sync backfill --today --summarize --summarize-backend openai --model gpt-4o
```

The `openclaw` backend is recommended as it:
- Uses your existing OpenClaw configuration
- Requires no separate API keys
- Leverages whatever model you have configured in OpenClaw

## Automated Usage

### Nightly Cron (3am)

Process today with LLM summary, preserving any existing notes:

```bash
0 3 * * * cd ~/.openclaw/skills/memory-sync && python memory_sync.py backfill --today --summarize --preserve >> ~/.memory-sync/cron.log 2>&1
```

### Smart Incremental Mode

Automatically detects changes since last run:

```bash
# Initial backfill (run once, simple extraction for speed)
python memory_sync.py backfill --all

# Then set up nightly incremental with LLM summaries
0 3 * * * cd ~/.openclaw/skills/memory-sync && python memory_sync.py backfill --incremental --summarize --preserve >> ~/.memory-sync/cron.log 2>&1
```

State is tracked in `~/.memory-sync/state.json`.

## Configuration

**Default paths:**
- Session logs: `~/.openclaw/agents/main/sessions/*.jsonl`
- Memory files: `~/.openclaw/workspace/memory/`

**Override with CLI flags:**
- `--sessions-dir /path/to/sessions`
- `--memory-dir /path/to/memory`

**Environment variables (only for direct API backends):**
- `ANTHROPIC_API_KEY` - Required for `--summarize-backend anthropic`
- `OPENAI_API_KEY` - Required for `--summarize-backend openai`

The default `openclaw` backend requires no API keys - it uses your OpenClaw configuration.

```bash
# Only needed if using direct API backends
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
```

## Content Preservation

The `--preserve` flag behavior depends on whether `--summarize` is used:

**Without `--summarize` (simple extraction):**
- Hand-written content (after footer marker) is **appended verbatim** to the end of the newly generated file
- The new extraction replaces the auto-generated portion, your notes are kept at the end

**With `--summarize` (LLM mode):**
- Existing hand-written content is **passed to the LLM** as context
- The LLM is instructed to incorporate your notes into the new summary
- Result: Your insights are woven into a coherent narrative, not just appended

**Example:**
```bash
# Regenerate with LLM, incorporating existing notes into the summary
memory-sync backfill --date 2026-02-05 --force --preserve --summarize
```

Auto-generated markers:
- Header: `*Auto-generated from N session messages*`
- Footer: `*Review and edit this draft to capture what's actually important.*`

Content after the footer marker is considered hand-written and will be preserved.

## Backfill Options

**Date selection (choose one):**
- `--date YYYY-MM-DD` - Single specific date
- `--today` - Current date only (for nightly automation)
- `--since YYYY-MM-DD` - From date to present (for catch-up)
- `--all` - All missing dates (for initial setup)
- `--incremental` - Only dates changed since last run (smart automation)

**Additional flags:**
- `--dry-run` - Show what would be created without creating files
- `--force` - Overwrite existing files (required for regeneration)
- `--preserve` - Keep hand-written content when regenerating
- `--summarize` - Use LLM for narrative summaries
- `--summarize-backend BACKEND` - Backend for summarization: `openclaw` (default), `anthropic`, `openai`
- `--model MODEL` - Model override for summarization (default varies by backend)

## Performance

| Mode | Time per Day | Best For |
|------|-------------|----------|
| `--all` | 5-10 min × N days | Initial setup only |
| `--since` | 5-10 min × N days | Recovery after gaps |
| `--today` | 30-60 sec | Nightly automation |
| `--incremental` | 30-60 sec × changed days | Smart automation |
