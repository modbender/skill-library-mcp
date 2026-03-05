---
name: water-coach
description: "Hydration tracking and coaching skill. Use when user wants to track water intake, get reminders to drink water, log body metrics, or get analytics on hydration habits."
compatibility: "Requires python3, openclaw cron feature, heartbeat feature"
metadata: {"clawdbot":{"emoji":"💧"} 
  author: oristides
---

# 💧 Water Coach



## First-time Setup 

Follow the first setup here [references/setup.md](references/setup.md)

---

## 🤖 How Other Agents Should Interact

### First-time Setup Check
```bash
water setup
```

| is_setup | What to do |
|----------|-------------|
| **false** | Ask: weight OR desired goal. Also ask: "What times do you want water reminders?" (let user configure their schedule). Then use `water set_body_weight 80` or `water set_goal 3000`. Don't assume hardcoded times! |
| **true** | Skip setup. Just log water or show status. |

### ❌ Don't Ask
- Reminder schedules after first setup (user already configured)

### ✅ Do Ask  
- "How much water did you drink?"
- Only weight/goal (first time)

---

## CLI Structure

```bash
water_coach.py <namespace> <command> [options]
```

Namespaces: `water` | `body` | `analytics`

---

## Data Format 

### CSV Format
```
logged_at,drank_at,date,slot,ml_drank,goal_at_time,message_id
```

| Column | Description |
|--------|-------------|
| logged_at | When user told you (NOW) |
| drank_at | When user actually drank (user can specify past time) |
| date | Derived from drank_at |
| slot | morning/lunch/afternoon/evening/manual |
| ml_drank | Amount in ml |
| goal_at_time | Goal at that moment |
| message_id | Audit trail - link to conversation |

**Key Rules:**
- **drank_at is MANDATORY** - always required
- If user doesn't specify drank_at → assume drank_at = logged_at
- **Cumulative is calculated at query time** (not stored)
- Use drank_at to determine which day counts

Details at  [references/log_format.md](references/log_format.md)

### Audit Trail

Every water log entry captures:
- **message_id**: Links to the conversation message where user requested the log
- **Auto-capture**: CLI automatically gets message_id from session transcript
- **Proof**: Use `water audit <message_id>` to get entry + conversation context

```bash
# Check proof of a water entry
water audit msg_123
# Returns: entry data + surrounding messages for context
```

> ⚠️ **Privacy Notice**: The audit feature can read your conversation transcripts, but **only when you explicitly run `water audit <message_id>`**. This is off by default (`audit_auto_capture: false`).
>
> ```bash
> # Edit water_config.json and set:
> "audit_auto_capture": true
> ```
>
> **How it works:**
> - Water log **always** saves the `message_id` (regardless of this setting) ✅
> - When you run `water audit <message_id>`:
>   - If `false`: Shows entry data only (message_id saved, but no context read)
>   - If `true`: Also reads transcript to show conversation context ("User said: I drank 500ml")
>
> **Why disable it?** If you discuss sensitive topics and don't need proof of intake, leave it off.

---

## Daily Commands

```bash
# Water
water status                                      # Current progress (calculated from drank_at)
water log 500                                    # Log intake (drank_at = now)
water log 500 --drank-at=2026-02-18T18:00:00Z  # Log with past time
water log 500 --drank-at=2026-02-18T18:00:00Z --message-id=msg_123
water dynamic                                    # Check if extra notification needed
water threshold                                  # Get expected % for current hour
water set_body_weight 80                        # Update weight + logs to body_metrics
water set_body_weight 80 --update-goal          # + update goal
water audit <message_id>                        # Get entry + conversation context

# Body
body log --weight=80 --height=1.75 --body-fat=18
body latest          # Get latest metrics
body history 30     # Get history

# Analytics
analytics week       # Weekly briefing (Sunday 8pm)
analytics month     # Monthly briefing (2nd day 8pm)
```

---

## Rules (MUST FOLLOW)

1. **ALWAYS use CLI** - never calculate manually
2. **LLM interprets first** - "eu tomei 2 copos" → 500ml → water log 500
3. **Threshold from CLI** - run `water threshold`, don't hardcode
4. **GOAL is USER'S CHOICE** - weight × 35 is just a DEFAULT suggestion:
   - At setup: Ask weight → suggest goal → **CONFIRM with user**
   - On weight update: Ask "Want to update your goal to the new suggested amount?"
   - User can set any goal (doctor's orders, preference, etc.)

---

## Config Tree

```
water-coach/
├── SKILL.md              ← You are here
├── scripts/
│   ├── water_coach.py   ← Unified CLI
│   └── water.py         ← Core functions
├── data/                 ← DO NOT USE - keep skill code separate from user data
└── references/
    ├── setup.md
    ├── dynamic.md
    └── log_format.md
```

### ⚠️ IMPORTANT: Data Location
**User data is stored in the AGENT WORKSPACE, NOT in the skill folder!**

| Data | Location |
|------|----------|
| water_log.csv | `<agent-workspace>/memory/data/water_log.csv` |
| water_config.json | `<agent-workspace>/memory/data/water_config.json` |
| body_metrics.csv | `<agent-workspace>/memory/data/body_metrics.csv |

Example path: `/home/oriel/.openclaw/workspace/memory/data/`

**Why?** Keeps user data separate from skill code — makes backups, migrations, and skill updates easier.

---

## Notifications Schedule

| Type | When | Command |
|------|------|---------|
| User Configured | Per user's schedule | water status |
| Default Suggestion | 9am, 12pm, 3pm, 6pm, 9pm | water status |
| Dynamic | Every ~30 min (heartbeat) | water dynamic |
| Weekly | Sunday 8pm | analytics week |
| Monthly | 2nd day 8pm | analytics month |

### Notification Rules (MUST FOLLOW)
- **USER CONFIGURES THEIR SCHEDULE** — Agent should ask user: "What times do you want water reminders?" and respect that
- **NO "no log" skip logic** — Always send notifications when scheduled, don't skip because user hasn't logged water
- **Notifications STIMULATE logging** — That's the point! Don't assume user will log on their own

---

## Quick Reference

| Task | Command |
|------|---------|
| Check progress | `water_coach.py water status` |
| Log water | `water_coach.py water log 500` |
| Need extra? | `water_coach.py water dynamic` |
| Body metrics | `water_coach.py body log --weight=80` |
| Weekly report | `water_coach.py analytics week` |
| Monthly report | `water_coach.py analytics month` |

## Dynamic Scheduling details
→ [references/dynamic.md](references/dynamic.md)

### ⚠️ Bug Fix (Feb 2026)
The `water dynamic` command had a bug where the hourly notification counter wouldn't reset when the hour changed. This is now fixed:
- The script now checks if the current hour differs from `last_extra_hour` and resets the counter accordingly
- This ensures notifications work correctly after hour boundaries (e.g., 4PM)

### ⚠️ Bug Fix (Feb 2026) - Analytics
The `analyticsPM → 5 week` and `analytics month` commands had a bug:
- Was looking for non-existent `cumulative_ml` column in CSV
- Fixed to sum `ml_drank` per day instead

### ✅ How to Build Good Weekly/Monthly Reports

**Use these functions (don't reinvent):**

| Report | Script | Function |
|--------|--------|----------|
| Weekly | `water_coach.py analytics week` | `analytics_week()` in `water_coach.py` |
| Monthly | `water_coach.py analytics month` | `analytics_month()` in `water_coach.py` |

These call `get_week_stats()` and `get_month_stats()` in `water.py`.

**When updating analytics functions, follow these rules:**

**1. Include ALL days, even with 0ml**
```python
# In get_week_stats() / get_month_stats()
# Include every day in the range, not just days with data
for i in range(days):
    d = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
    ml = by_date.get(d, {}).get("ml", 0)  # Default to 0, not skip
```

**2. Calculate true average**
```python
# Average = total_ml / ALL days (including zeros), not just tracked days
avg_ml = total_ml / days  # e.g., 15440ml / 7 days = 2205ml/day
```

**3. Show all days in table format**
```python
| Dia | ML | % | Status |
| Sab 22 | 2250ml | 67.7% | ⚠️ |
| Seg 17 | 0ml | 0.0% | ❌ |
```

This gives users an accurate picture of their habits!



## Tests

```bash
python3 -m pytest skills/water-coach/scripts/test/test_water.py -v
```

## Example

```
User: "eu tomei 2 copos"
Agent: (LLM interprets: 2 copos ≈ 500ml)
Agent: exec("water_coach.py water log 500")
→ Python logs to CSV
```



Agent Evaluations → [evaluation/AGENT.md](evaluation/AGENT.md)

