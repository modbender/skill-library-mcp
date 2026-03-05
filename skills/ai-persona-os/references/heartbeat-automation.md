# Heartbeat Automation Guide

> **⚠️ OPT-IN ONLY:** Nothing in this guide runs automatically when the skill is installed.
> Heartbeat configuration and cron jobs described here are **manual setup steps** that the
> user must explicitly choose to perform. The core skill works fully without any cron jobs.
> All cron jobs run in **isolated sessions** — they read/write only local workspace files
> and make **no network calls, no API requests, and require no credentials**.

**Purpose:** Configure heartbeats and cron jobs for reliable, enforced protocol execution.  
**Added in:** v1.3.0

---

## How It Works

AI Persona OS splits operations into two layers:

| Layer | Mechanism | Frequency | Cost | Purpose |
|-------|-----------|-----------|------|---------|
| **Pulse** | HEARTBEAT.md | Every 30min | Low (~93 tokens) | Context guard + memory health |
| **Briefing** | Cron job (isolated) | 1-2x daily | Medium | Full 4-step protocol + channel scan |

**Why two layers?** Heartbeats run full agent turns. If HEARTBEAT.md is 170 lines, you burn tokens 48 times/day reading documentation the agent already knows. Keep the heartbeat tiny; move heavy ops to cron.

---

## Layer 1: Heartbeat (Every 30 Minutes)

### What HEARTBEAT.md Does

The workspace HEARTBEAT.md file is your agent's 30-minute pulse. It should be:
- Under 20 lines
- Imperative (commands, not documentation)
- Focused on context protection and memory health

The template in `assets/HEARTBEAT-template.md` is ready to use as-is. Copy it to your workspace:

```bash
cp assets/HEARTBEAT-template.md ~/workspace/HEARTBEAT.md
```

### Output Format

The agent uses traffic light indicators for instant readability:

**All clear (suppressed — user never sees this):**
```
HEARTBEAT_OK
```

**Checkpoint written:**
```
🫀 Feb 5, 2:30 PM PT | anthropic/claude-haiku-4-5 | AI Persona OS v1.3.3

🟢 Context: 31% — Healthy
🟡 Memory: Stale — last checkpoint 47m ago
🟢 Workspace: Clean
🟢 Tasks: None pending

→ Checkpoint written to memory/2026-02-05.md
  Captured: 2 decisions, 1 action item
```

**Context emergency:**
```
🚨 HEARTBEAT — Feb 5, 2:30 PM PT

🔴 Context: 84% — EMERGENCY
🔴 Memory: At risk — last checkpoint 2h ago
🟢 Workspace: Clean
🟡 Tasks: 1 blocked — PR review overdue

→ Emergency checkpoint written
  Flushed: 3 decisions, 2 action items, 1 blocker
  ⚠️ Recommend starting a fresh session
```

**Maintenance needed:**
```
🫀 HEARTBEAT — Feb 5, 2:30 PM PT

🟢 Context: 22% — Healthy
🟡 Memory: MEMORY.md at 3.8KB (limit 4KB)
🟡 Workspace: 4 logs older than 90 days
🟢 Tasks: None pending

→ Maintenance needed
  MEMORY.md approaching limit — pruning recommended
  4 session logs ready to archive
  Say "clean up" to run both
```

**Overdue items surfaced:**
```
🫀 HEARTBEAT — Feb 5, 8:00 AM PT

🟢 Context: 12% — Healthy
🟢 Memory: Synced — checkpoint 8m ago
🟢 Workspace: Clean
🟡 Tasks: 3 uncompleted from yesterday

→ Carried over from Feb 4:
  ☐ Review Q1 budget proposal
  ☐ Reply to Sarah re: onboarding
  ☐ Update WORKFLOWS.md with new deploy process
```

### Indicator Reference

| Indicator | Context | Memory | Workspace | Tasks |
|-----------|---------|--------|-----------|-------|
| 🟢 | <50% | Checkpoint <30m old | All files OK | 0 pending |
| 🟡 | 50-69% | Checkpoint 30-60m old | Minor issues | 1-3 items |
| 🔴 | ≥70% | Checkpoint >60m old | Files inaccessible | Blocked items |

### Custom Heartbeat Prompt (RECOMMENDED)

Override the default OpenClaw heartbeat prompt. This is **strongly recommended** — without it, agents may revert to old formats or ignore the template structure.

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "ackMaxChars": 20,
        "prompt": "Read HEARTBEAT.md and execute every instruction. On the first line show: 🫀 [current date/time] | [your model name] | AI Persona OS v[VERSION from workspace VERSION.md file]. Then report using 🟢🟡🔴 indicators — one per line with a blank line between each: Context, Memory, Workspace, Tasks. If you took action, state what with → prefix. Only reply HEARTBEAT_OK if all 🟢 and no action taken. Do NOT use Step 0/1/2/3/4 format. Do NOT use markdown tables. Do NOT use headers."
      }
    }
  }
}
```

This replaces the default prompt ("Read HEARTBEAT.md if it exists...") with one that:
- Shows model name and OS version on the first line (instant visibility)
- Explicitly requires 🟢🟡🔴 indicators
- Forces line breaks between indicators (blank line between each)
- Blocks the old Step format that v1.2.0 agents may have learned
- Blocks markdown tables (garbled on WhatsApp/Telegram)
- Suppresses HEARTBEAT_OK via ackMaxChars (your phone stays silent when all green)

---

## Layer 2: Daily Briefing (Cron Job)

For the full 4-step Session Management protocol (context → load state → system status → priority scan → assessment), use an isolated cron job that runs 1-2x daily.

### Morning Briefing

```bash
openclaw cron add \
  --name "ai-persona-morning-briefing" \
  --cron "0 8 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Run the AI Persona OS daily protocol:

Step 1: Load previous context — Read memory/$(date +%Y-%m-%d).md and yesterday's log. Summarize key state.

Step 2: System status — Run health-check.sh if available. Check MEMORY.md size, workspace structure, stale logs.

Step 3: Priority scan — Check channels in priority order (P1 critical → P4 background). Surface anything requiring attention.

Step 4: Assessment — System health summary, blocking issues, time-sensitive items, recommended first action.

Format as a daily briefing with 🟢🟡🔴 indicators for each section." \
  --announce
```

### End-of-Day Checkpoint

```bash
openclaw cron add \
  --name "ai-persona-eod-checkpoint" \
  --cron "0 18 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "End-of-day checkpoint:

1. Write a full checkpoint to memory/$(date +%Y-%m-%d).md with all decisions, action items, and open threads from today.

2. Review MEMORY.md — promote any repeated learnings from today's log. Prune anything stale.

3. Check .learnings/ — any pending items that should be promoted after 3+ repetitions?

4. Brief summary: what was accomplished, what carries over to tomorrow." \
  --announce
```

### Weekly Review

```bash
openclaw cron add \
  --name "ai-persona-weekly-review" \
  --cron "0 9 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --model opus \
  --message "Weekly review protocol:

1. Scan memory/ for the past 7 days. Summarize key themes, decisions, and outcomes.

2. Review .learnings/LEARNINGS.md — promote items with 3+ repetitions to MEMORY.md or AGENTS.md.

3. Archive logs older than 90 days to memory/archive/.

4. Check MEMORY.md size — prune if >3.5KB.

5. Review WORKFLOWS.md — any new patterns worth documenting?

Deliver a weekly summary with wins, issues, and focus areas for the coming week." \
  --announce
```

---

## Configuration Examples

### Minimal Setup (Heartbeat Only)

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last"
      }
    }
  }
}
```

Just uses HEARTBEAT.md as-is. Good starting point.

### Recommended Setup (Heartbeat + Cron)

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "ackMaxChars": 20,
        "prompt": "Read HEARTBEAT.md and execute every instruction. On the first line show: 🫀 [current date/time] | [your model name] | AI Persona OS v[VERSION from workspace VERSION.md file]. Then report using 🟢🟡🔴 indicators — one per line with a blank line between each: Context, Memory, Workspace, Tasks. If you took action, state what with → prefix. Only reply HEARTBEAT_OK if all 🟢 and no action taken. Do NOT use Step 0/1/2/3/4 format. Do NOT use markdown tables. Do NOT use headers.",
        "activeHours": {
          "start": "07:00",
          "end": "23:00"
        }
      }
    }
  }
}
```

Plus the cron jobs from Layer 2 above.

### Cost-Conscious Setup

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "1h",
        "target": "last",
        "activeHours": {
          "start": "08:00",
          "end": "20:00"
        }
      }
    }
  }
}
```

Hourly heartbeats during work hours only. Use a single daily cron job for the briefing.

---

## Migrating from v1.2.x

If you're upgrading from v1.2.0 or v1.2.1:

### Automatic Migration (v1.3.1+)

The new HEARTBEAT.md template includes a migration check at the top. If the agent detects it's running an old template (>30 lines), it will update from the current skill template. This happens automatically on the first heartbeat after upgrade.

### Manual Migration

If auto-migration doesn't trigger, tell your agent:

> "Read the file at your ai-persona-os skill folder: assets/HEARTBEAT-template.md. Now replace your workspace HEARTBEAT.md with that content exactly. Do not add anything."

### Critical: Add the Heartbeat Prompt Override

**This step prevents agents from reverting to the old Step 0/1/2/3/4 format.** Agents that ran v1.2.0 for a while have the old format in their learned behavior. Even with a new HEARTBEAT.md, they may ignore it and produce the old verbose output. The prompt override forces the new format at the OpenClaw level.

Tell your agent:

> "Update your openclaw.json heartbeat to: `{ "every": "30m", "target": "last", "ackMaxChars": 20, "prompt": "Read HEARTBEAT.md and execute every instruction. On the first line show: 🫀 [current date/time] | [your model name] | AI Persona OS v[VERSION from workspace VERSION.md file]. Then report using 🟢🟡🔴 indicators — one per line with a blank line between each: Context, Memory, Workspace, Tasks. If you took action, state what with → prefix. Only reply HEARTBEAT_OK if all 🟢 and no action taken. Do NOT use Step 0/1/2/3/4 format. Do NOT use markdown tables. Do NOT use headers." }`"

### Shared Channel Fix

If your agent responds in Discord/Slack channels when not mentioned, tell it:

> "List ALL Discord guilds in your config. Set requireMention: true for EVERY guild. Show me the full list when done."

This enforces Rule 5 (Selective Engagement) at the gateway level.

### What's Preserved

Your existing memory files, SOUL.md, USER.md, AGENTS.md, WORKFLOWS.md, and all workspace content are untouched. This only changes how heartbeats execute and how the agent behaves in shared channels.

---

## Troubleshooting

**Agent still uses Step 0/1/2/3/4 format:**
- Add the custom heartbeat.prompt override (see RECOMMENDED section above)
- The old format is learned behavior — the prompt override forces the new format at the OpenClaw level
- If it persists, clear the agent's session history: start a fresh session

**Heartbeat indicators render on one line (no line breaks):**
- Discord and some chat platforms collapse single newlines
- The v1.3.1 template instructs blank lines between indicators
- If still compressed: add the heartbeat prompt override which explicitly requests "blank line between each"

**Agent still replies HEARTBEAT_OK without checking:**
- Verify HEARTBEAT.md is in the workspace root (not in assets/)
- Add the custom heartbeat.prompt override — it forces structured output
- Check that HEARTBEAT.md isn't empty (OpenClaw skips empty files)

**HEARTBEAT_OK is showing up in chat (not being suppressed):**
- Check `ackMaxChars` in your heartbeat config — the response must be shorter than this value
- Verify the agent is replying with just `HEARTBEAT_OK` and no extra text
- Default ackMaxChars should cover `HEARTBEAT_OK` (12 chars) — if it's set very low, increase it

**Agent responds in Discord when not mentioned:**
- Set `requireMention: true` for ALL Discord guilds in your gateway config
- This is a gateway-level setting, not a skill setting
- Tell the agent: "List ALL Discord guilds in your config. Set requireMention: true for EVERY guild."

**Heartbeat messages are too noisy:**
- Increase interval: `"every": "1h"`
- Add activeHours to limit to work hours
- The 🟢-all-clear case already suppresses delivery

**Heartbeats not firing:**
- Run `openclaw heartbeat last` to check status
- Run `./scripts/config-validator.sh` to audit all required settings at once (NEW v1.3.2)
- Verify `agents.defaults.heartbeat.every` isn't "0m"
- Check that `every` and `target` exist in your heartbeat config — without them, heartbeats don't auto-fire
- Check activeHours timezone

**MEMORY.md too large (burning tokens):**
- v1.3.2 heartbeat auto-prunes MEMORY.md when it exceeds 4KB
- If auto-pruning hasn't triggered: manually tell your agent to prune
- Facts older than 30 days should be archived to memory/archive/
- MEMORY.md should stay under 4KB — it's read every session start

**Don't know what config settings are missing:**
- Run `./scripts/config-validator.sh` (NEW v1.3.2)
- Checks: heartbeat (every, target, ackMaxChars, prompt), Discord (requireMention per guild), workspace files (SOUL.md, USER.md, MEMORY.md size, HEARTBEAT.md template version), VERSION.md file, ESCALATION.md
- Reports 🟢 all clear / 🟡 warnings / 🔴 critical issues

**Agent's config file is clawdbot-mac.json or clawdbot.json (not openclaw.json):**
- Older installs may use the pre-rename config file
- All heartbeat and guild settings work the same regardless of filename
- Tell the agent to check its actual config file name: "What config file are you using?"

---

*Part of AI Persona OS by Jeff J Hunter — https://os.aipersonamethod.com*
