---
name: autonomy-windowed
version: 1.0.0
description: Time-windowed autonomous task queue. Autonomy works only during specific time windows (e.g., 8 AM - 8 PM UTC), while cron jobs run overnight. Separates concerns by time - day = autonomy, night = maintenance. Use when you want predictable work schedule, controlled token budget, and clear temporal separation between autonomous work and scheduled maintenance.
metadata:
  openclaw:
    emoji: "⏰"
    category: productivity
---

# Windowed Autonomy

Transform your agent from reactive to autonomous worker during **specific time windows**.

---

## Concept

The agent works autonomously **only during defined time windows**. Outside windows, the agent only replies `HEARTBEAT_OK`. Cron jobs run overnight when autonomy is disabled.

```
🌙 Overnight (10 PM - 8 AM UTC):  Autonomy OFF
☀️ Daytime (8 AM - 10 PM UTC):   Autonomy ON
```

**Clear separation:** Day = work on queue, Night = cron maintenance

---

## How It Works

### 1. Time Windows

Define active windows in `tasks/QUEUE.md`:

```markdown
## ⏰ Autonomy Windows

- 🌙 Overnight: 20:00 - 08:00 UTC → Autonomy OFF
- ☀️ Daytime: 08:00 - 20:00 UTC → Autonomy ON
```

### 2. Heartbeat Flow

**During Active Window:**
```
Heartbeat → Check urgent → No → Read QUEUE → Pick task → Work 15-30 min → Update QUEUE → Log
```

**Outside Active Window:**
```
Heartbeat → Check urgent → No → Reply "HEARTBEAT_OK" → Sleep
```

**Urgent Override:**
```
Heartbeat → Check urgent → YES → Work immediately (even outside window)
```

### 3. Window Transitions

**Window Opens (8:00 AM):**
- Autonomous mode enabled
- Start pulling from queue
- Log to `tasks/MODE_HISTORY.md`: "Window opened"

**Window Closes (8:00 PM):**
- Autonomous mode disabled
- Wrap up current task if in progress
- Log transition: "Window closed"
- Switch to standby mode (HEARTBEAT_OK only)

---

## Schedule Examples

| Time | Activity | Mode |
|------|----------|------|
| 00:00 | GitHub backup (cron) | Overnight (no autonomy) |
| 02:00 | Heartbeat check | Standby (HEARTBEAT_OK) |
| 03:00 | Temp cleanup (cron) | Overnight (no autonomy) |
| 08:00 | Window opens | ✅ Autonomy ON |
| 09:00 | Work on task | Autonomy |
| 12:00 | GitHub backup (cron) | Autonomy (pause for backup) |
| 14:00 | Work on task | Autonomy |
| 20:00 | Window closes | ❌ Autonomy OFF |
| 23:00 | Daily ops + memory (cron) | Overnights (no autonomy) |

---

## Queue Structure

```markdown
# Task Queue

## ⏰ Autonomy Windows
- 🌙 Overnight: 20:00 - 08:00 UTC → Autonomy OFF
- ☀️ Daytime: 08:00 - 20:00 UTC → Autonomy ON

---

## 🔴 Ready (can be picked up during windows)
- [ ] @priority:high [Task description]
- [ ] @priority:medium [Task description]

## 🟡 In Progress
- [ ] @agent: @priority:high [Task description]
  - Started: 2026-02-16 14:00 UTC

## 🔵 Blocked
- [ ] @priority:medium [Task] (needs: [what's blocking])

## ✅ Done Today
- [x] @agent: @priority:high [Task]
  - Completed: 2026-02-16 14:25 UTC

## 💡 Ideas
- [Idea for future work]
```

---

## Priority System

Priority affects task selection order during windows:

| Priority | When to use | Selection |
|----------|-------------|-----------|
| `@priority:urgent` | Time-sensitive, deadline < 6h | Pick FIRST, even outside window |
| `@priority:high` | Important, deadline 24h | Pick first in window |
| `@priority:medium` | Normal importance | Pick second in window |
| `@priority:low` | Nice to have | Pick last in window |

---

## Window Types

### Full Day Window (Default)

**Active:** 8 AM - 8 PM UTC (12 hours)

**Use when:**
- youris available during these hours
- Tasks are not time-sensitive
- Want predictable work schedule

**Heartbeat frequency:** Every 2 hours (6 sessions/day)

### Extended Window

**Active:** 6 AM - 10 PM UTC (16 hours)

**Use when:**
- Want more work hours
- yourhas varied schedule

**Heartbeat frequency:** Every 2 hours (8 sessions/day)

### Limited Window

**Active:** 10 AM - 6 PM UTC (8 hours)

**Use when:**
- Want controlled token budget
- yourhas focused availability

**Heartbeat frequency:** Every 2-3 hours (3-4 sessions/day)

---

## Token Budget

**Recommended:** 4-6 sessions/day, ~5-10K tokens each = 20-60K/day

**Session strategy:**

| Window Type | Sessions/day | Tokens | Schedule |
|------------|--------------|--------|----------|
| Full Day (12h) | 6 | 30-60K | Every 2 hours |
| Extended (16h) | 8 | 40-80K | Every 2 hours |
| Limited (8h) | 4 | 20-40K | Every 2-3 hours |

**When to stop:**
- Window closes (time-based)
- Tokens remaining < 5K
- Queue empty
- youris actively messaging (human priority)

---

## Urgent Tasks Override

**Definition:** Tasks that cannot wait for window to open

**Add to queue with `@priority:urgent`:**
```markdown
## 🔴 Ready
- [ ] @priority:urgent Emergency: [task description]
```

**Behavior:**
- Autonomy works **immediately**, even if outside window
- Override all other considerations
- Complete urgent task, then check window status

---

## Wrapping Up When Window Closes

**If in middle of task when window closes:**

1. Check task progress:
   - If > 80% complete → Finish it
   - If < 80% complete → Save progress, move to In Progress, stop

2. Save state:
```markdown
## 🟡 In Progress
- [ ] @agent: @priority:high [Task description]
  - Started: 2026-02-16 19:30 UTC
  - Progress at window close: Completed X section, need to do Y
  - Resume: 2026-02-17 08:00 UTC (next window)
```

3. Log to `tasks/MODE_HISTORY.md`:
```markdown
## [2026-02-16 20:00 UTC] Window Closed
Status: Task in progress (60% complete)
Action: Saved state, will resume in next window
```

---

## Mode History Tracking

File: `tasks/MODE_HISTORY.md`

```markdown
# Window Mode Transitions

## [2026-02-16 08:00 UTC] Window Opened
Mode: Daytime window
Queue state: 3 tasks ready
Expected sessions: 6

## [2026-02-16 20:00 UTC] Window Closed
Mode: Overnight (standby)
Sessions completed: 5
Tasks completed: 4
Tasks remaining: 1 (in progress, resume tomorrow)

## [2026-02-17 08:00 UTC] Window Opened
Mode: Daytime window
Resumed task in progress
```

---

## Coordinating With Cron

**Daytime (Autonomy ON):**
- Light cron runs fine (Ollama monitor, disk check) - no conflict
- Heavy cron (backup) - autonomy pauses during execution

**Overnight (Autonomy OFF):**
- All cron jobs run freely
- No autonomy conflicts

**Cron schedule:**

| Time | Cron Job | Autonomy Mode |
|------|----------|---------------|
| Every 5 min | Ollama monitor | Any (low impact) |
| Every hour | Disk check | Any (low impact) |
| 00:00 | GitHub backup | OFF (overnight) |
| 03:00 | Temp cleanup | OFF (overnight) |
| 08:00 | Window opens | ON |
| 12:00 | GitHub backup | ON (pause during) |
| 14:00 | Daily ops + memory (Sun) | ON (pause during) |
| 20:00 | Window closes | OFF (overnight) |
| 23:00 | Daily ops + memory | OFF (overnight) |

---

## GOALS.md Integration

Link queue tasks to RA's long-term goal: **MONEY**

**Add goal references:**
```markdown
- [ ] @priority:high Competitor pricing analysis (GOAL: monetization strategy)
- [ ] @priority:medium Write sales email template (GOAL: improve conversion)
```

**Work toward goals during windows:**
- Research tasks during early window (fresh energy)
- Writing tasks during mid window (flow state)
- Review tasks during late window (wind down)

---

## .learnings/ Integration

After completing tasks, add findings to `.learnings/`:

```markdown
## [LRN-20260216-001] task-completion
Task: [Task description]

Completed during: Daytime window (14:00-14:25 UTC)
Tokens used: 8K

Key findings: [summarize]
```

---

## Daily Routine

### Window Opens (8:00 AM)

1. Check queue for tasks in 🔴 Ready
2. Pick highest priority task
3. Work 15-30 minutes
4. Update queue (In Progress or Done)

### During Window (9 AM - 8 PM)

1. Every 2 hours: heartbeat, check queue
2. Work on next highest priority task
3. Update queue after completion
4. Log progress to memory/[today].md

### Window Closes (8:00 PM)

1. Check if task in progress
2. If yes: Save progress or finish if close
3. Move to Done Today or keep in In Progress
4. Log transition `tasks/MODE_HISTORY.md`
5. Switch to standby (HEARTBEAT_OK only)

### Overnight (8 PM - 8 AM)

1. Every heartbeat: Check urgent only
2. If no urgent: Reply HEARTBEAT_OK
3. Cron jobs run freely
4. No autonomous work

---

## Task Output Format

```markdown
## Task: [Title]

**Completed during:** [Window type] [Time range]
**Duration:** X minutes
**Tokens:** YK

### Work Done
[Describe what was accomplished]

### Output
[Attach output file or content]

### Next Steps
[What to do next - add to Ideas if task spawns follow-up]
```

---

## Evolving Over Time

**The "slowly evolve" approach:**

This mode allows The agent to **gradually take on more work**:

**Week 1-2:**
- Conservative: 4 sessions/day, limited window
- Monitor performance, adjust schedule

**Week 3-4:**
- Expand: 6 sessions/day, extended window if needed
- Add more task types to queue

**Month 2:**
- Optimize: Tailor window to RA's actual schedule and peak productivity times
- Adjust based on what yourfinds valuable

**Key:** Start small, expand based on feedback and results.

---

## When to Use This Skill

Use this skill when:
- You want **predictable work schedule**
- You want autonomy to work during **specific hours**
- Tasks are **not time-sensitive** (can wait for window)
- You want **clear temporal separation** between autonomy and maintenance
- You're okay with "slowly evolving" - start small, expand over time

---

## When NOT to Use This Skill

Do not use this skill when:
- You want **24/7 autonomous work** → Use `autonomy-type-based` for type-based filtering
- Tasks are **highly time-sensitive** → Use urgency override or different approach
- You want **task-based separation** rather than time-based → Use `autonomy-type-based`
- youris awake during **non-standard hours** → Adjust windows to match schedule

---

## Quick Reference

**Default window:** 8 AM - 8 PM UTC (adjustable)
**Session frequency:** Every 2-3 hours during window
**Priority order:** `urgent` (override) → `high` → `medium` → `low`
**Queue location:** `tasks/QUEUE.md`

---

*See templates/QUEUE.md for full template structure*
