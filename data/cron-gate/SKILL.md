---
name: Cron Gate
description: Every OpenClaw cron that spawns an isolated LLM session burns
  tokens — prompt loading, Weave files, tool calls — even when there's nothing
  new to process. If you run memory integration across 5 ses...
---

# Cron Gate

**Stop wasting tokens on crons with nothing to do.**

Every OpenClaw cron that spawns an isolated LLM session burns tokens — prompt loading, Weave files, tool calls — even when there's nothing new to process. If you run memory integration across 5 sessions twice a day, that's 10 LLM wake-ups. Most of them find nothing and go back to sleep, having burned ~40K tokens each.

Cron Gate is a zero-token Python gatekeeper that checks for new activity *before* triggering expensive LLM crons. No new messages? No wake-up. No tokens burned.

## How It Works

```
System crontab (free)          OpenClaw cron (expensive)
        │                              │
   gate.py runs              disabled, waiting
        │                              │
   checks sessions.json       ┌───────┘
        │                     │
   new activity? ─── yes ───► triggers cron via API
        │
       no ──► exits silently (0 tokens)
```

1. A lightweight Python script runs on system crontab (zero LLM cost)
2. It reads `sessions.json` to check `updatedAt` timestamps
3. Compares against its own state file (last time it triggered each session)
4. Only calls the OpenClaw gateway API to trigger crons for sessions with genuinely new messages
5. Idle sessions never wake up — they cost nothing until someone talks in them

## Install

### 1. Copy the gate script

```bash
cp gate.py /opt/scripts/cron-gate.py
chmod +x /opt/scripts/cron-gate.py
```

### 2. Configure your session-to-cron mapping

Edit the `SESSION_CRONS` dict in `gate.py` to map your session keys to their integration cron IDs:

```python
SESSION_CRONS = {
    "agent:main:telegram:group:-1234567890": {
        "evening": "your-evening-cron-id-here",
        "morning": "your-morning-cron-id-here",
    },
    "agent:main:discord:channel:9876543210": {
        "evening": "another-cron-id",
        "morning": None,  # skip morning for this session
    },
}
```

**Finding your session keys:** Look in `~/.openclaw/agents/main/sessions/sessions.json`

**Finding your cron IDs:** Run `/crons` in chat or check the OpenClaw dashboard

### 3. Disable the original crons

For each integration cron you're gating, disable it (but don't delete — the gate script triggers them on-demand):

```
/cron update <cron-id> enabled=false
```

Or ask your agent: "Disable all memory integration crons — they'll be triggered by the gate script now."

### 4. Add system crontab entries

```bash
# Evening integration window (adjust times to match your schedule)
5 6 * * * /usr/bin/python3 /opt/scripts/cron-gate.py evening >> /var/log/cron-gate.log 2>&1

# Morning integration window
5 18 * * * /usr/bin/python3 /opt/scripts/cron-gate.py morning >> /var/log/cron-gate.log 2>&1
```

## Usage

```bash
# Dry run — see what would trigger without actually doing it
python3 gate.py --dry-run evening

# Force a specific slot (ignore time-of-day check)
python3 gate.py morning

# Normal operation (auto-detects slot from UTC hour)
python3 gate.py
```

## Time Windows

The script auto-detects which slot to run based on UTC hour:
- **Evening:** 4-8 UTC
- **Morning:** 16-20 UTC

Override by passing `evening` or `morning` as an argument. When run from crontab with an explicit slot argument, the time window check is bypassed.

## State File

Activity timestamps are stored in `/opt/scripts/cron-gate-state.json` (configurable). This is how the gate knows what's "new" — it compares each session's `updatedAt` against the last time it triggered that cron.

To reset (re-trigger everything on next run):
```bash
rm /opt/scripts/cron-gate-state.json
```

## Token Savings

Real-world numbers from the first deployment:
- **Before:** 10 integration crons × 2/day = 20 LLM sessions, ~800K tokens/day
- **After:** Only sessions with new activity get triggered. Idle sessions = 0 tokens.
- **Typical savings:** 60-80% reduction in integration token costs
- **Gate script cost:** Zero. It's pure Python, no LLM involved.

## Beyond Memory Integration

This pattern works for any cron that might have nothing to do:
- **Email checks** — gate behind inbox message count
- **Social platform rounds** — gate behind API health check
- **Notification checks** — gate behind unread count
- **Any periodic LLM task** — if a cheap check can determine "nothing to do," gate it

The principle: **check cheap, wake expensive only when needed.**

## Requirements

- Python 3.8+
- OpenClaw with gateway API running on localhost:18789
- System crontab access (`crontab -e`)
- No additional dependencies (stdlib only)
