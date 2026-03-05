---
name: session-health-monitor
description: Context window health monitoring for OpenClaw agents — threshold warnings via Telegram, pre-compaction snapshots, and memory rotation.
allowed-tools:
  - Bash
  - Read
  - Write
version: 1.1.0
author: heinrichclawdster
---

# Session Health Monitor

Monitor your OpenClaw agent context window health, get warnings via Telegram when usage is high, save critical facts before compaction, and keep memory directories clean.

## Overview

Four capabilities for OpenClaw agent sessions:

1. **Context Threshold Warnings** — Agents append usage footer to Telegram messages and warn at configurable thresholds
2. **Compaction Detection** — Track usage drops to infer when context was compacted
3. **Pre-Compaction Snapshots** — Save key facts and decisions to daily memory files before they're lost
4. **Memory Rotation** — Archive old daily memory files to prevent clutter

## Quick Setup (OpenClaw)

### 1. Add shared skill reference

Add to your `shared/INDEX.md`:

```markdown
| Context window health, compaction detection, pre-compaction snapshots | `skill-session-health.md` |
```

### 2. Create shared skill doc

Create `shared/skill-session-health.md`:

```markdown
# Session Health Monitor

## Context Health Thresholds
| Level  | Condition                          | Action                        |
|--------|------------------------------------|-------------------------------|
| GREEN  | <50% used AND 0 compactions        | Normal operation              |
| YELLOW | >=50% used OR >=1 compaction       | Save key facts via snapshot   |
| RED    | >=75% used OR >=2 compactions      | Save facts NOW, session ending|

## Behavioral Rules
1. When context reaches YELLOW+, extract 3-5 key facts (decisions, files changed, blockers)
2. Run: `bash scripts/snapshot.sh "fact1" "fact2"`
3. Append footer to Telegram messages at YELLOW+: `X% Context Window | Nx compacted`
4. Do this BEFORE session ends or context gets compacted
5. After any detected compaction, immediately snapshot what you remember
```

### 3. Add heartbeat step

Add to your agent heartbeat/loop:

```markdown
**Context health check**: Run `session_status` → always append context % to Telegram messages
as footer: `📊 X% Context Window`. If Context >50% OR Compactions >=1, add:
"⚠️ consider /restart after current task." If Context >75% OR Compactions >=2, flag as urgent.
```

## Context Health Thresholds

| Level  | Condition                              | Action                        |
|--------|----------------------------------------|-------------------------------|
| GREEN  | <50% used AND 0 compactions            | Normal operation              |
| YELLOW | >=50% used OR >=1 compaction           | Consider saving key facts     |
| RED    | >=75% used OR >=2 compactions          | Save facts NOW, session ending|

## Telegram Message Footer

Agents append a footer to every outgoing Telegram message:

```
📊 42% Context Window                          # GREEN — no extra warning
📊 63% Context Window | 1x compacted           # YELLOW — consider restart
⚠️ 📊 81% Context Window | 2x compacted        # RED — urgent, save facts
```

This keeps the user informed about session health without requiring manual checks.

## Pre-Compaction Snapshot Protocol

**When context reaches YELLOW or above, the agent SHOULD:**

1. Extract 3-5 key facts from the current session (decisions made, files changed, blockers found)
2. Write them to `memory/YYYY-MM-DD.md` using `scripts/snapshot.sh`
3. Include any unfinished work or next steps
4. Do this BEFORE the session ends or context is compacted

**Example snapshot content:**
```markdown
## Pre-Compaction Snapshot (14:32)
- Refactored auth module to use JWT instead of sessions (files: src/auth.ts, src/middleware.ts)
- Bug found in rate limiter: counter resets on deploy, not on TTL expiry
- Next: write tests for new auth flow, fix rate limiter reset logic
- Decision: using RS256 for JWT signing (user preference)
```

**When to trigger:**
- Context hits 50%+ for the first time in a session
- After any detected compaction
- Before ending a long session
- When the agent detects it has accumulated significant context

## Scripts Reference

### context-check.sh
Standalone health check, useful in heartbeat loops.

```bash
bash scripts/context-check.sh                    # Human-readable output
bash scripts/context-check.sh --json              # Machine-readable JSON
echo '{"context_window":{"used_percentage":72}}' | bash scripts/context-check.sh
# Exit codes: 0=GREEN, 1=YELLOW, 2=RED
```

### snapshot.sh
Save facts to daily memory file.

```bash
bash scripts/snapshot.sh "Fact one" "Fact two" "Fact three"
echo -e "Fact one\nFact two" | bash scripts/snapshot.sh -
```

### rotate.sh
Archive old daily memory files.

```bash
bash scripts/rotate.sh           # Archives files older than 3 days (default)
KEEP_DAYS=7 bash scripts/rotate.sh  # Keep 7 days instead
```

## Configuration

All configuration is via environment variables with sensible defaults:

| Variable             | Default                                          | Description                            |
|----------------------|--------------------------------------------------|----------------------------------------|
| `MEMORY_DIR`         | Auto-detect (see below)                          | Where to write daily memory files      |
| `KEEP_DAYS`          | `3`                                              | Days to keep before archiving          |
| `HEALTH_GREEN_MAX`   | `50`                                             | Max % for GREEN status                 |
| `HEALTH_RED_MIN`     | `75`                                             | Min % for RED status                   |
| `COMPACTION_DROP`    | `30`                                             | % drop that indicates compaction       |

**Memory directory auto-detection order:**
1. `$MEMORY_DIR` environment variable
2. `~/.openclaw/workspace/memory` (if exists)
3. `~/.claude/memory` (fallback)

## Troubleshooting

### jq not installed
```bash
# macOS
brew install jq
# Linux
sudo apt-get install jq
```

### Reset compaction state
```bash
rm /tmp/session-health-*.json
```

### Agent not appending footer
1. Check `shared/INDEX.md` references `skill-session-health.md`
2. Check heartbeat includes the context health step
3. Verify `session_status` tool is available to the agent
