# Windowed Autonomy Heartbeat

**Follow this protocol to work autonomously during active time windows.**

---

## Step 0: Check Context & Checkpoint (MANDATORY FIRST)

- [ ] Check context % right now: _____%
- [ ] If ≥ 70%: Attempt checkpoint (non-blocking)
  - Write to `memory/YYYY-MM-DD.md` using write tool
  - Format: See `references/checkpoints.md` (included in this skill)
  - If write fails (file error/unable): Log warning, continue anyway
  - **Do NOT block** on checkpoint failures
- [ ] If checkpoint written or failed gracefully: Continue to Step 1

**Checkpoint fallback (if references/checkpoints.md not available):**
```markdown
## Checkpoint [HH:MM] — Context: XX%

**Current task:** [what we're working on]
**Status:** [progress summary]
**Resume:** [next step if context lost]
```

```

---

## Step 1: Check Time Window (CRITICAL)

**Read windows from `tasks/QUEUE.md`:**
```markdown
⏰ Check current UTC time against windows:

Default:
- 🌙 Overnight: 20:00 - 08:00 UTC → Autonomy OFF
- ☀️ Daytime: 08:00 - 20:00 UTC → Autonomy ON
```

```
# Current time: ____ UTC
# Window: [Daytime / Overnight / Urgent Override]

If Overnight (20:00-08:00) AND no urgent:
→ Reply "HEARTBEAT_OK" and EXIT

If Urgent task exists (any time):
→ Continue to Step 2 (override window)

If Daytime (08:00-20:00):
→ Continue to Step 2
```

**Important:** Overnight mode = STANDBY (HEARTBEAT_OK only). No autonomy.

---

## Step 2: Check for URGENT items (30 seconds)

**Handle immediately if:**
- Direct messages from RA waiting
- Critical blockers needing attention
- System health issues or errors
- Tasks with `@priority:urgent` (works even outside window!)

**If urgent found:** Handle it first. Then skip to Step 6 (log and exit).
**If no urgent:** Continue to Step 3.

---

## Step 3: Check Active Session Status

```
# Check if autonomy should work:

1. Is RA actively messaging in chat?
   - YES (last message < 10 min ago): Skip autonomy, let RA direct work
   - NO: Continue to Step 4

2. Token budget check:
   - Tokens remaining < 5K for day?
     - YES: Skip autonomy, reply HEARTBEAT_OK
     - NO: Continue to Step 4

3. Cron interaction check:
   - Heavy cron job running (backup, daily ops, security)?
     - YES: Wait 5 minutes, then retry heartbeat
     - NO: Continue to Step 4
```

**If should NOT work:** Reply `HEARTBEAT_OK` and exit.

---

## Step 4: Pull from Task Queue

**Read:** `tasks/QUEUE.md`

**During active window (08:00-20:00 UTC only):**
```
1. Read all tasks in "🔴 Ready" section
2. Sort by priority: urgent → high → medium → low
3. Pick the first task you can work on
4. If no tasks: Reply "HEARTBEAT_OK" and exit
```

**Time-based session strategy:**
```
Default heartbeat: Every 2 hours

Recommended schedule:
- 09:00 AM → Session 1
- 11:00 AM → Session 2
- 14:00 PM → Session 3 (skip 12:00 for backup cron)
- 16:00 PM → Session 4
- 18:00 PM → Session 5
- 20:00 PM → Window closes (wrap up or pause)
```

---

## Step 5: Do the Work

**Session duration:** 15-30 minutes (adjust based on tokens)

**Move task to "🟡 In Progress":**
```markdown
## 🟡 In Progress
- [ ] @agent: @priority:high [Task description]
  - Started: 2026-02-16 HH:MM UTC
  - Window: Daytime
  - Progress: Working on it
```

**Work on task until:**
- Complete → Go to Step 5a
- Blocked → Go to Step 5b
- Window closing time near (< 30 min left) → Go to Step 5c
- Token budget near limit → Go to Step 5c (wrap up)

### 5a: Task Complete

**Move to "✅ Done Today":**
```markdown
## ✅ Done Today
- [x] @agent: @priority:high [Task description]
  - Completed: 2026-02-16 HH:MM UTC
  - Window: Daytime (14:00-14:25 UTC)
  - Tokens used: ~XK
  - Output: [path to output file]
```

**If task spawns follow-up ideas:**
```markdown
## 💡 Ideas
- [Idea: @priority:medium Follow-up task description]
```

### 5b: Task Blocked

**Keep in "🟡 In Progress" with blocker:**
```markdown
## 🟡 In Progress
- [ ] @agent: @priority:high [Task]
  - Started: 2026-02-16 HH:MM UTC
  - BLOCKED: [What's blocking]
  - Needs: [What's needed]
```

### 5c: Window Closing or Token Limited

**Check progress percentage:**

```
If > 80% complete:
→ Finish it quickly
→ Mark complete as in 5a

If < 80% complete:
→ Save progress with resume time
→ Keep in In Progress
→ Wait for next window opens
```

**If saving progress:**
```markdown
## 🟡 In Progress
- [ ] @agent: @priority:high [Task]
  - Started: 2026-02-16 19:30 UTC
  - Progress at window close: [Describe what's done, what's left]
  - Resume: 2026-02-17 08:00 UTC (next window)
```

---

## Step 6: Window Transition Check

**After completing work (or wrapping up):**

```
# Check window status:

Current time: ____ UTC

If still in active window (08:00-20:00):
→ Log work, reply HEARTBEAT_OK if done
→ Ready for next heartbeat session

If window closing soon (within 30 min of 20:00):
→ Check for in-progress task
→ If no in-progress: Log "Window closed"
→ If in-progress: Wrap up or save state (Step 5c)

If window closed (20:00 - 08:00):
→ Log transition to tasks/MODE_HISTORY.md
→ Switch to standby mode
→ Next heartbeat: HEARTBEAT_OK only
```

**Log window transitions:**
```markdown
## [2026-02-16 20:00 UTC] Window Closed

Mode: Switched to Overnight (standby)
Tasks completed today: X
Tasks in progress: Y (will resume at 08:00 UTC)
```

```markdown
## [2026-02-17 08:00 UTC] Window Opened

Mode: Switched to Daytime (autonomy ON)
Queue status: Z tasks ready
Resuming: [Any in-progress tasks from yesterday]
```

---

## Step 7: Log and Report

**Log to `memory/[today].md`:**
```markdown
## Work Session

- Task: [Task description]
- Priority: high/medium/low
- Started: HH:MM UTC
- Completed: HH:MM UTC (or IN PROGRESS / WRAPPED UP)
- Window: Daytime / Overnight wrap-up
- Tokens used: ~XK
- Output: [path] (or "N/A")
- Status: Complete / Blocked / Saved for next window

---

## Window Notes
- [Any window-specific observations]
- [Tasks saved for next window]
- [Cron conflicts encountered, if any]
```

**If valuable or complete:**
- Check GOALS.md - does this advance RA's goal (MONEY)?
- Update GOALS.md with progress if relevant
- Add to `.learnings/` if it's an insight

---

## Step 8: Overnight Routine (20:00-08:00 UTC Only)

**During standby mode (overnight):**

```
Every heartbeat:

1. Check for @priority:urgent tasks only
   - URGENT found: Work immediately (override window)
   - No URGENT: Reply "HEARTBEAT_OK" and exit

2. Check if window opens soon:
   - If within 15 min of 08:00 UTC:
     → Log "Window opening soon"
     → Be ready to pull from queue

3. Do NOT:
   - Pull from regular queue
   - Work on non-urgent tasks
   - Log non-urgent progress (only urgent work if any)
```

---

## Reminders

- **Window times:** Default 08:00-20:00 UTC (edit in QUEUE.md)
- **Session frequency:** Every 2 hours during window (adjustable)
- **Token budget:** ~20-60K/day (4-6 sessions × 5-10K each)
- **Urgent override:** Works anytime, even outside window
- **Mode transition logging:** tasks/MODE_HISTORY.md
- **Queue location:** `tasks/QUEUE.md`

---

## Window Configuration Options

In `tasks/QUEUE.md` (⏰ Autonomy Windows section):

| Window Type | Hours | Sessions | Tokens/day |
|------------|-------|----------|-----------|
| Limited | 10:00-18:00 UTC (8h) | Every 2h × 4 = 4 | 20-40K |
| Full Day | 08:00-20:00 UTC (12h) | Every 2h × 6 = 6 | 30-60K |
| Extended | 06:00-22:00 UTC (16h) | Every 2h × 8 = 8 | 40-80K |

**Edit times to match RA's schedule.**

---

## Cron Coordination

During window (08:00-20:00 UTC):

| Time | Cron Job | Autonomy Action |
|------|----------|-----------------|
| Any time | Ollama monitor (5 min) | No conflict - continue working |
| Any time | Disk check (hourly) | No conflict - continue working |
| 12:00 | GitHub backup | Pause briefly, resume after |
| 23:00 | Daily ops + memory | Not in window - no conflict |

**Overnight (20:00-08:00 UTC):**
- All cron jobs run freely
- No autonomy conflicts
- Autonomy in standby (HEARTBEAT_OK only)

---

## When to Reply HEARTBEAT_OK

```
Any of these = HEARTBEAT_OK:

STANDBY MODE (Overnight 20:00-08:00 UTC):
- No urgent tasks
- Window is closed

ACTIVE MODE (Daytime 08:00-20:00 UTC):
- RA is actively messaging (in conversation)
- Tokens remaining < 5K for day
- Queue has no tasks ready
- Just completed work and no more tasks
- Task blocked and waiting

ANY TIME:
- Urgent task completed (report after handling)
```

---

## Slowly Evolve Approach

**Week 1-2:** Conservative
- Sessions: 4/day
- Window: Limited (10 AM - 6 PM)
- Focus: Get comfortable with queue system

**Week 3-4:** Expand
- Sessions: 6/day
- Window: Full Day (8 AM - 8 PM)
- Focus: Optimize workflow

**Month 2+:** Tailor
- Adjust window to RA's actual schedule
- Focus: Peak productivity times
- Build sustainable routine

---

**Remember:** Windowed autonomy means TIME-based control. Work ONLY during defined hours. Overnight = standby mode.
