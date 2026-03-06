---
name: Job Execution Monitor
description: Monitor scheduled jobs (cron) and alert when they fail or miss their schedule.
---

# Job Execution Monitor

Monitor scheduled jobs (cron) and alert when they fail or miss their schedule.

## Install / Update (ClawHub)

Install:
```bash
clawhub install job-execution-monitor
```

Update:
```bash
clawhub update job-execution-monitor
```

---

## When to Use
Use when the user asks to:
- "monitor cron jobs"
- "alert on job failures"
- "check if jobs ran"
- "job healthcheck"
- "task surveillance"
- "why didn't my scheduled job run?"

## What It Does

**Heartbeat-based monitoring:**
- Agent checks jobs during periodic heartbeat polls (~every 60min)
- Uses cheapest LLM (Gemini Flash or Haiku) to minimize cost
- Only sends alerts when problems detected
- Tracks alert state to avoid spam

**Cost:** ~100k tokens/day (~48 checks × 2k tokens)

## How It Works

1. **Configuration:** Jobs to monitor are listed in `job-execution-monitor.json`
2. **Heartbeat check:** Agent wakes every 15-30min, checks jobs every ~4th wake
3. **Detection:** Compares last run time vs. expected schedule + tolerance
4. **Alert:** Wake event with context (expected schedule vs last run) → you decide next action
5. **Recovery:** Clears alert when job runs successfully again

## Disable / Uninstall

### If installed via systemd *user* timer
```bash
systemctl --user stop openclaw-job-execution-monitor.timer
systemctl --user disable openclaw-job-execution-monitor.timer
systemctl --user daemon-reload

# Optional: remove unit files
rm -f ~/.config/systemd/user/openclaw-job-execution-monitor.service \
      ~/.config/systemd/user/openclaw-job-execution-monitor.timer
```

### If installed via cron
```bash
crontab -l | sed '/job-execution-monitor\/scripts\/healthcheck\.sh/d' | crontab -
```

### Optional cleanup (config/state/log)
```bash
rm -f ~/.openclaw/workspace/job-execution-monitor.json
rm -f ~/.openclaw/workspace/.job-execution-monitor-state.json
rm -f ~/.openclaw/workspace/job-execution-monitor.log
```

---

## Configuration

**File:** `~/.openclaw/workspace/job-execution-monitor.json`

```json
{
  "checkIntervalMin": 60,
  "jobs": {
    "Daily 21:00 journaling (projects + accomplishments + next day plan)": {
      "schedule": "0 22 * * *",
      "tolerance": 600,
      "critical": true,
      "expectedMinLength": 200,
      "errorPatterns": ["error", "failed", "Pong", "token overflow"]
    }
  }
}
```

**Fields:**
- `schedule`: cron expression for expected run time
- `tolerance`: grace period in seconds (default 600 = 10min)
- `critical`: if true, alerts immediately (future: could escalate)
- `expectedMinLength`: minimum response length (phase 2)
- `errorPatterns`: text patterns that indicate failure (phase 2)

## State Tracking

**File:** `~/.openclaw/workspace/.job-execution-monitor-state.json`

```json
{
  "lastCheck": 1771025000,
  "alerts": {
    "daily-wrap-up_missed": 1771024500
  }
}
```

- `lastCheck`: unix timestamp of last check
- `alerts`: map of alert_key → timestamp (prevents spam)

## Instructions (for Agent)

In `HEARTBEAT.md`:

```markdown
## Job Execution Monitor (every ~60min, rotate)

Check cron jobs for missed schedules. Only alert if problem found.

**Instructions:**
1. Load `job-execution-monitor.json` config
2. Call `cron list` 
3. For each job in config:
   - Extract `state.lastRunAtMs` and `state.lastStatus`
   - Parse schedule (e.g., "0 22 * * *" = 22:00 daily)
   - If last run > (expected time + tolerance): **ALERT**
   - If last run recent: **SILENT**
4. On alert: send wake event with job name, expected time, last run time
5. On recovery (was alerting before, now OK): send recovery wake event

**State tracking:** `~/.openclaw/workspace/.job-execution-monitor-state.json`
- Track which jobs already alerted (don't spam)
- Clear alert flag when job recovers

**Rotate check:** Only run every ~4th heartbeat (once/hour if heartbeat is 15min)
```

## Examples

**Scenario 1: Job missed**
```
🔴 Job Execution Monitor: "daily-wrap-up" missed schedule
Expected: 22:00 ±10min
Last run: 5h 32m ago
Checking logs...
```

**Scenario 2: Job recovered**
```
✅ Job Execution Monitor: "daily-wrap-up" recovered
Last run: 22:02 (2min ago)
```

**Scenario 3: All OK**
```
(silent - no wake event, no alert)
```

## Cost Analysis

**Per check (~2k tokens):**
- Load config: ~200 tokens
- Call cron list: ~500 tokens
- Parse + compare: ~500 tokens
- Decision + response: ~800 tokens

**Daily (~48 checks):**
- 48 × 2k = **~100k tokens/day**
- Using Gemini Flash: **~$0.01/day** ✅

**Compared to alternatives:**
- Bash script every 10min: 0 tokens, but complex + fragile
- Cron job every 10min: 144 × 2k = ~300k tokens/day
- Heartbeat every 60min: **~100k tokens/day** ← chosen ✅

## Files

- `SKILL.md` - This documentation
- `README.md` - Quick start
- `config/job-execution-monitor.example.json` - Config template
- `scripts/patterns.json` - Error patterns (phase 2)
- `~/workspace/job-execution-monitor.json` - User config
- `~/workspace/.job-execution-monitor-state.json` - Alert state

## Philosophy

**Smart monitoring, minimal cost.**

- Check frequency: ~1/hour (good enough for daily jobs)
- Use cheapest LLM: Gemini Flash or Haiku
- Only wake main session when real problems occur
- State tracking prevents alert spam
- Agent-based = leverages existing tools, no auth/API hassles

---

**Phase 1 complete.** ✅  
**Phase 2 (pattern matching):** Coming soon.  
**Phase 3 (structured validation):** Future.
