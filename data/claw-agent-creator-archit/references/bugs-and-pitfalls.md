# Bugs and Pitfalls

Every known gotcha from building OpenClaw agents. Check before debugging from scratch.

## Critical Pitfalls

### Editing jobs.json While Gateway Runs

**Symptom**: Edits lost, corrupted, or conflicted.
**Cause**: Gateway writes state updates after every cron run — race condition.
**Fix**: `openclaw gateway stop` → edit → `openclaw gateway start`. Always.

### Copying Files Without Updating Paths

**Symptom**: Silent failures (e.g., dedup reading wrong cache).
**Cause**: Copied files contain hardcoded workspace paths.
**Fix**: After copying, grep for old paths: `grep -r "workspace/" ~/.openclaw/workspace-<new>/`

### Telegram Group Messages Silently Dropped

**Symptom**: No response. Logs: `skip: no-mention`.
**Cause**: Three configs required; missing any one fails silently.
**Fix**: Set all three layers (see telegram-routing.md).

## Config Validation Errors

| Invalid Key | Error | Use Instead |
|-------------|-------|-------------|
| `heartbeat.enabled` | Rejected on startup | `heartbeat.every: "0"` |
| `allowGroups` | Rejected on startup | List in `channels.telegram.groups` |
| `openclaw config set` with brackets | Malformed keys with escaped quotes | Edit `openclaw.json` directly |

## Telegram Group Migration

### Group ID Changes When Bot Made Admin

**Symptom**: Messages to group return `reason: "not-allowed"`. Cron notifications silently fail.
**Cause**: Telegram upgrades regular groups to supergroups (new ID) when admin actions are taken (making bot admin, enabling persistent history, setting public username). Happens once per group.
**What auto-updates**: `channels.telegram.groups` in openclaw.json (OpenClaw detects migration).
**What does NOT auto-update**: `bindings[]`, cron job prompts, external scripts.
**Fix**: Use the self-healing pattern — never hardcode group IDs. See telegram-routing.md and prompt-patterns.md for the dynamic resolution preamble.

## Cron Job Pitfalls

### No Date Anchoring

**Symptom**: Old stories reported as "today's news".
**Fix**: Start every prompt with `Today is $(date '+%A, %B %d, %Y').`

### Identical Morning/Evening Prompts

**Symptom**: Evening repeats morning stories.
**Fix**: Differentiate time context + add "Do NOT repeat" + use shared sessions (no `sessionTarget: "isolated"`).

### Source Rules Only in SOUL.md

**Symptom**: Agent uses unreliable sources despite SOUL.md.
**Cause**: SOUL.md content lost during context compaction.
**Fix**: Inline `SOURCES:` and reject lists in every prompt.

### Stale Paths After Agent Reassignment

**Symptom**: Job runs but uses wrong workspace.
**Fix**: Audit all paths in cron payloads when changing `agentId`.

## Session / Memory Pitfalls

### Isolated Sessions Break Q&A

**Fix**: Remove `sessionTarget: "isolated"` from jobs where continuity matters.

### Reusing agentDir

**Symptom**: Auth failures, session collisions.
**Fix**: Every agent needs unique `agentDir`.

## Qdrant / Mem0 Pitfalls

### Version Mismatch

**Fix**: Pin Qdrant to v1.13.6: `docker run ... qdrant/qdrant:v1.13.6`

### Vector Dimension Mismatch

**Symptom**: `expected dim: 768, got 1536`
**Fix**: Pre-create collections: `curl -X PUT .../collections/memories -d '{"vectors":{"size":768,"distance":"Cosine"}}'`
