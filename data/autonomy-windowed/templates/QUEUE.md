# Task Queue

*Last updated: [timestamp]*
*Autonomy mode: Windowed (time-based)*
*Current window: [Daytime/Overnight]*

---

## ⏰ Autonomy Windows

- 🌙 Overnight: **20:00 - 08:00 UTC** → Autonomy OFF (standby)
- ☀️ Daytime: **08:00 - 20:00 UTC** → Autonomy ON (work from queue)

*Edit these times to match RA's schedule*

---

## 🔴 Ready (can be picked up during active window)

[Tasks waiting to be worked on]

- [ ] @priority:high [Task description]
- [ ] @priority:medium [Task description]
- [ ] @priority:low [Task description]

---

## 🟡 In Progress

[Tasks currently being worked on]

- [ ] @agent: @priority:high [Task description]
  - Started: 2026-02-16 HH:MM UTC
  - Progress: [Current progress note]
  - [Optional] Resume: 2026-02-17 08:00 UTC (if paused at window close)

---

## 🔵 Blocked

[Tasks waiting for something]

- [ ] @priority:medium [Task description] (needs: [what's blocking])

---

## ✅ Done Today

[Tasks completed today - clear daily or archive]

- [x] @agent: @priority:high [Task description]
  - Completed: 2026-02-16 HH:MM UTC
  - Window: Daytime/Overnight
  - Output: [path to output file or notes]

---

## 💡 Ideas

[Candidate tasks for future work - promote to Ready when ready]

- [Idea: @priority:medium [Task idea description]]
- [Idea: @priority:low [Another idea]]

---

## Priority Levels

| Priority | When to use | Selection order |
|----------|-------------|-----------------|
| `urgent` | Deadline < 6h, emergency | FIRST (even outside window) |
| `high` | Deadline 24h, important | First in window |
| `medium` | Normal importance | Second in window |
| `low` | Nice to have, no deadline | Last in window |

---

## Window Configuration

### Default Windows

| Window | Hours | Sessions |
|--------|-------|----------|
| Full Day | 8 AM - 8 PM (12h) | Every 2h × 6 = 6 sessions |
| Extended | 6 AM - 10 PM (16h) | Every 2h × 8 = 8 sessions |
| Limited | 10 AM - 6 PM (8h) | Every 2-3h × 4 = 4 sessions |

**To change windows:** Edit the "Autonomy Windows" section above

### Token Budget

| Window | Sessions | Tokens per session | Total per day |
|--------|----------|-------------------|---------------|
| Full Day | 6 | 5-10K | 30-60K |
| Extended | 8 | 5-10K | 40-80K |
| Limited | 4 | 5-10K | 20-40K |

---

## Urgent Task Override

**Definition:** Tasks that cannot wait for window to open

**Add to queue:**
```markdown
## 🔴 Ready
- [ ] @priority:urgent URGENT: [task description]
```

**Behavior:**
- Works **immediately**, even outside window
- Overrides normal window schedule
- Complete urgent task, then check window status

---

## Connecting to GOALS.md

Every task should link to RA's long-term goal: **MONEY**

**Add goal references:**
```markdown
- [ ] @priority:high Competitor pricing analysis (GOAL: pricing strategy)
- [ ] @priority:medium Write sales email template (GOAL: improve conversion)
- [ ] @priority:low Research alternatives (GOAL: cost optimization)
```

**After completion:** Update GOALS.md with progress notes

---

## Daily Routine

### Window Opens (08:00 UTC)

1. Check queue for 🔴 Ready tasks
2. Pick highest priority task
3. Work 15-30 minutes
4. Update queue (move to 🟡 In Progress or ✅ Done Today)
5. Log to `memory/[today].md`

### During Window (09:00 - 20:00 UTC)

**Every 2 hours:**
1. Heartbeat triggers
2. Check queue (🔴 Ready)
3. Pick next highest priority task
4. Work on it
5. Update queue after completion
6. Log progress

**Cron interactions:**
- Light cron (Ollama, disk check): No conflict, work continues
- Heavy cron (backup, daily ops): Pause work, resume after cron completes

### Window Closes (20:00 UTC)

1. Check if task in progress:
   - **If > 80% complete:** Finish it
   - **If < 80% complete:** Save progress, keep in 🟡 In Progress, note resume time

2. Update queue state:
```markdown
## 🟡 In Progress
- [ ] @agent: @priority:high [Task]
  - Started: 2026-02-16 19:30 UTC
  - Progress at window close: [describe progress]
  - Resume: 2026-02-17 08:00 UTC
```

3. Log to `tasks/MODE_HISTORY.md`:
```markdown
## [2026-02-16 20:00 UTC] Window Closed
Mode: Overnight (standby)
Tasks completed today: 4
Tasks in progress: 1 (will resume tomorrow)
```

### Overnight (20:00 - 08:00 UTC)

**Every heartbeat:**
1. Check for `@priority:urgent` tasks only
2. No urgent → Reply "HEARTBEAT_OK"
3. Cron jobs run freely (no autonomy conflicts)

---

## Task Output Format

```markdown
## Task: [Title]

**Completed during:** Daytime window (14:00-14:25 UTC)
**Duration:** 25 minutes
**Tokens:** 7K

### Work Done
[Describe what was accomplished]

### Output
[Attach output file or content]

### Next Steps
[What to do next - add to Ideas if task spawns follow-up]
```

---

## Learnings Integration

After completing tasks, add to `.learnings/`:

```markdown
## [LRN-20260216-001] task-completion
Task: [Task description]

Completed during: Daytime window (14:00-14:25 UTC)
Tokens used: 7K

Key findings: [summarize]
```

```markdown
## [ERR-20260216-001] task-issue
Error: [Problem description]

Fix: [Document the fix]
```

---

## Evolving Over Time ("Slowly Evolve")

This mode allows The agent to gradually take on more work:

### Week 1-2: Conservative
- Sessions: 4/day, Limited window (10 AM - 6 PM)
- Focus on getting comfortable with queue system
- Monitor performance and token usage
- Adjust schedule based on RA's feedback

### Week 3-4: Expand
- Sessions: 6/day, Full Day window (8 AM - 8 PM)
- Add more task varieties to queue
- Optimize based on what RA finds valuable

### Month 2+: Optimize
- Tailor windows to RA's actual schedule
- Focus on peak productivity times
- Build sustainable routine

---

## Coordination With Cron

| Time | Cron Job | Autonomy Status |
|------|----------|-----------------|
| 00:00 | GitHub backup | OFF (overnight) |
| 03:00 | Temp cleanup | OFF (overnight) |
| 08:00 | Window opens | ON ✅ |
| 09:00 | Work on queue | Autonomy |
| 12:00 | GitHub backup | ON (pause briefly) |
| 14:00 | Work on queue | Autonomy |
| 17:00 | Work on queue | Autonomy |
| 20:00 | Window closes | OFF ❌ |
| 23:00 | Daily ops + memory | OFF (overnight) |

---

*Daytime window = autonomous work from queue*
*Overnight = standby mode, cron jobs run freely*
*Urgent tasks work immediately even outside window*
