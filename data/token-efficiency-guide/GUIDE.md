# How to Reduce Your Token Consumption by 80-90% Instantly

**For:** Anyone running OpenClaw on a Claude Max subscription
**Goal:** Go from burning through your weekly limit in 2 days to making it last all week

---

## How Claude Max Limits Work

- **5-hour rolling window:** Burns as you use it, resets gradually
- **7-day rolling window:** If this hits 100%, you're stuck for days
- **Multiple agents on one account share the same pool**

**Where your tokens actually go:**
Most users discover that 80%+ of their token budget is consumed by heartbeats on expensive models, bloated context windows, and cron jobs running on Opus. Fix these and you keep 80-90% of your budget for actual work.

---

## 1. Set Heartbeat Model to Haiku (~25% of total budget saved)

Heartbeats fire every few minutes just to check if anything needs attention. They almost never need intelligence. Running them on Opus is like hiring a surgeon to take your temperature.

**In your OpenClaw config (`openclaw.json`):**
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "model": "anthropic/claude-haiku-4-5"
      }
    }
  }
}
```

---

## 2. Compact Sessions and Control Context Growth (~20% of total budget saved)

Context accumulation is the single biggest token drain. Every message re-sends the full conversation history. A 50-message session means 200K+ tokens of cached context on every single interaction — even for a simple "yes."

**What to do:**
- Use `/compact` during long sessions to summarize and shrink context
- Configure automatic session resets nightly (cron job or bash script)
- After completing a big task, reset the session before starting the next one

**In AGENTS.md or your system prompt, add:**
```
After completing major tasks, proactively suggest a session reset to save tokens.
```

---

## 3. Convert Simple Cron Jobs to Bash Scripts (~15% of total budget saved)

If a cron job does pure logic (check a value, compare thresholds, send a notification), it doesn't need an LLM. Write a bash script and run it via system crontab.

**How to identify candidates:** If the job doesn't need to *understand* or *generate* text, it can be bash.

**Example:** A usage monitor that reads a JSON file, checks if a value exceeds a threshold, and sends a notification. That's an `if` statement, not intelligence.

```bash
crontab -e
# Add: */30 * * * * /path/to/your-script.sh
```

---

## 4. Set Remaining Cron Jobs to Sonnet (~10% of total budget saved)

Cron jobs run unattended. Most don't need Opus. Each cron job on Opus uses ~5x the tokens it would on Sonnet.

**For each cron job**, add a `model` field to the payload:
```json
{
  "payload": {
    "kind": "agentTurn",
    "model": "sonnet",
    "message": "..."
  }
}
```

**Rule of thumb:**
- Simple monitoring, summaries, reports → **Sonnet**
- Complex analysis, multi-step reasoning, code generation → **Opus**

---

## 5. Isolate Large Output Operations (~10% of total budget saved)

Running commands that produce huge outputs (directory listings, full configs, log dumps) in the main session permanently bloats it. All that output stays in session history and gets re-sent with every future message.

**What to do:**
- Run diagnostic/exploration commands in a sub-agent or separate session
- Always pipe output through `head -n 20`, `grep`, or `wc -l` instead of dumping full results
- Never run `find /`, `config.schema`, or full log exports in the main session

**In AGENTS.md, add:**
```
When running shell commands, always limit output. Use head, grep, tail, or wc -l. 
Never dump large outputs into the main session.
```

---

## 6. Reduce Cron Frequency (~8% of total budget saved)

Does this really need to run every 30 minutes? Every day?

| Instead of | Try | Savings |
|-----------|-----|---------|
| Every 30 min | Every 2 hours | 75% of that job |
| Daily | Every other day | 50% of that job |
| Daily | Weekly (for non-urgent) | 85% of that job |

---

## 7. Clean Up Workspace Files (~7% of total budget saved)

Every file listed under workspace injection gets sent with **EVERY SINGLE MESSAGE**. If these files total 20KB, that's ~5,000 tokens burned per interaction — before anyone says a word.

### Step-by-step:

**A. Measure current size:**
```bash
cd ~/.openclaw/workspace
total=0
for f in SOUL.md AGENTS.md TOOLS.md USER.md IDENTITY.md MEMORY.md HEARTBEAT.md; do
  if [ -f "$f" ]; then
    size=$(wc -c < "$f")
    echo "$size bytes  $f"
    total=$((total + size))
  fi
done
echo "---"
echo "$total bytes TOTAL"
```

**B. Target: under 15KB total (ideally under 10KB)**

**C. For each file over 3KB:**

1. Open the file
2. Separate *identity* (needed every message) from *reference* (looked up occasionally)
3. Move reference content to `bank/reference/FILENAME-details.md`
4. Replace in original with a pointer:
   ```
   Full details: see bank/reference/FILENAME-details.md
   ```

**D. Common bloat:**

| File | Typical bloat | Fix |
|------|--------------|-----|
| USER.md | Full biography, family tree | Keep: name, language, timezone, preferences. Move rest to `bank/reference/` |
| TOOLS.md | Detailed instructions per tool | Keep: 1-line per tool. Move examples to `bank/reference/` |
| AGENTS.md | Long workflow descriptions | Keep: core rules. Move procedures to `bank/reference/` |
| MEMORY.md | Growing list of everything | Keep: index with pointers. Actual memories in `memory/` directory |
| SOUL.md | Personality essays | Keep under 2KB. Personality doesn't need paragraphs |

**E. Verify:**
```bash
cat SOUL.md AGENTS.md TOOLS.md USER.md IDENTITY.md MEMORY.md HEARTBEAT.md 2>/dev/null | wc -c
# Should be under 15000
```

---

## 8. Enable Cache Retention (~3% of total budget saved)

Anthropic's prompt cache expires after 5 minutes of inactivity. Every "cold start" pays full price for the entire system prompt again. If you use your agent sporadically, this adds up fast.

**In your config:**
```json
{
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-opus-4-6": {
          "params": {
            "cacheRetention": "long"
          }
        }
      }
    }
  }
}
```

This tells OpenClaw to keep the prompt cache alive longer, reducing cold-start costs.

---

## 9. Coordinate Usage Between Agents (~2% of total budget saved)

If multiple agents share one subscription, avoid simultaneous heavy usage. The 5-hour window drains twice as fast with two active agents.

Agree on time blocks. One agent does heavy work in the morning, the other in the afternoon.

---

## 10. Automate Maintenance with System Cron (~5% of total budget saved)

Don't rely on the LLM to keep itself clean. Set up bash scripts on system crontab for recurring maintenance. These run without any token cost.

**Recommended nightly cron scripts:**

### a. Session Trimmer (02:00)
Archives session files larger than 5MB or older than 7 days. Prevents context bloat from accumulating silently.

```bash
#!/bin/bash
# nightly-session-trim.sh
SESSION_DIR="$HOME/.openclaw/agents/main/sessions"
ARCHIVE_DIR="$HOME/.openclaw/agents/main/sessions-archive"
mkdir -p "$ARCHIVE_DIR"

# Archive sessions > 5MB
find "$SESSION_DIR" -name "*.jsonl" -size +5M -exec mv {} "$ARCHIVE_DIR/" \;

# Archive sessions not touched in 7 days
find "$SESSION_DIR" -name "*.jsonl" -mtime +7 -exec mv {} "$ARCHIVE_DIR/" \;

# Delete archives older than 30 days
find "$ARCHIVE_DIR" -name "*.jsonl" -mtime +30 -delete
```

### b. Daily Backup (03:00)
Git push for md files + Google Drive upload for databases. See disaster recovery section.

### c. Session Reset (23:00)
Reset group and agent sessions nightly to prevent context snowball.

### d. Usage Guard (every 30 min)
Monitor subscription utilization and auto-switch to API key at 90% threshold.

**Install all four:**
```bash
crontab -e
# Add:
0 2 * * * /path/to/nightly-session-trim.sh
0 3 * * * /path/to/daily-backup.sh
0 23 * * * /path/to/reset-whatsapp-sessions.sh
*/30 * * * * /path/to/claude-usage-guard.sh
```

These scripts cost zero tokens and prevent the problems that waste tokens.

---

## Total Impact

| Step | Saves | Effort |
|------|-------|--------|
| 1. Heartbeat → Haiku | ~25% | 1 minute (config change) |
| 2. Compact sessions / control context | ~20% | 10 minutes (prompt + cron) |
| 3. Simple crons → bash | ~15% | 1-2 hours (per script) |
| 4. Cron jobs → Sonnet | ~10% | 5 minutes (per job) |
| 5. Isolate large outputs | ~10% | 10 minutes (prompt rules) |
| 6. Reduce cron frequency | ~8% | 5 minutes |
| 7. Workspace cleanup | ~7% | 30 minutes |
| 8. Cache retention | ~3% | 1 minute (config change) |
| 9. Coordinate agents | ~2% | Agreement |
| 10. Automate maintenance crons | ~5% | 1-2 hours (scripts) |
| **Combined** | **~80-90%** | **One afternoon** |

---

*Compatible with OpenClaw 2026.2+*
