PhoenixClaw leverages OpenClaw's built-in cron system for automated, passive journaling. This configuration ensures nightly reflections occur without manual triggers.

### One-Time Setup
Run the following command to register the PhoenixClaw nightly reflection job. This schedules the task to run every day at 10:00 PM local time.

```bash
openclaw cron add \
  --name "PhoenixClaw nightly reflection" \
  --cron "0 22 * * *" \
  --tz "auto" \
  --session isolated \
  --message "Execute PhoenixClaw with COMPLETE 9-step Core Workflow. CRITICAL STEPS:
1. Load config
2. memory_get + Scan session logs and filter by each message timestamp for today (not file mtime)
3. Identify moments (decisions, emotions, milestones, photos) -> creates 'moments' data
4. Detect patterns
5. Execute ALL plugins at hook points (Ledger runs at post-moment-analysis)
6. Generate journal WITH all plugin sections
7-9. Update timeline, growth-map, profile

NEVER skip session log scanning - images are ONLY there. NEVER skip step 3 - plugins depend on moments data."
```

> **Memory & Session Scan**: Always scan session logs from all known directories (`~/.openclaw/sessions/`, `~/.openclaw/agents/*/sessions/`, `~/.openclaw/cron/runs/`, `~/.agent/sessions/`) alongside daily memory to capture in-progress activity. Use recursive scanning to find `.jsonl` files in nested subdirectories. If daily memory is missing or sparse, use session logs to reconstruct context, then update daily memory.

### Configuration Details
- **--name**: Unique identifier for the job. Useful for management.
- **--cron**: Standard crontab syntax. "0 22 * * *" represents 10:00 PM daily.
- **--tz auto**: Automatically detects the system's local timezone. You can also specify a specific timezone like "America/New_York".
- **--session isolated**: Ensures the job runs in a clean environment with full tool access, preventing interference from active coding sessions.
- **--message**: Keep this payload task-focused and version-agnostic. Do not hardcode skill version numbers here; treat `metadata.version` in `SKILL.md` as the source of truth.

### Verification and Monitoring
To ensure the job is correctly registered and active:

```bash
openclaw cron list
```

To view the execution history, including status codes and timestamps of previous runs:

```bash
openclaw cron history "PhoenixClaw nightly reflection"
```

### Modifying and Removing Jobs
If you need to change the schedule or the instructions, you can update the job using the same name:

```bash
openclaw cron update "PhoenixClaw nightly reflection" --cron "0 23 * * *"
```

To completely stop and delete the automated reflection job:

```bash
openclaw cron remove "PhoenixClaw nightly reflection"
```

### Post-Execution Verification

After cron runs, verify the full workflow executed:

```bash
# 1. Check target-day messages were scanned (by message timestamp)
TARGET_DAY="$(date +%Y-%m-%d)"
TARGET_TZ="${TARGET_TZ:-Asia/Shanghai}"
read START_EPOCH END_EPOCH < <(
  python3 - <<'PY' "$TARGET_DAY" "$TARGET_TZ"
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys

day, tz = sys.argv[1], sys.argv[2]
start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=ZoneInfo(tz))
end = start + timedelta(days=1)
print(int(start.timestamp()), int(end.timestamp()))
PY
)

for dir in "$HOME/.openclaw/sessions" \
           "$HOME/.openclaw/agents" \
           "$HOME/.openclaw/cron/runs" \
           "$HOME/.agent/sessions"; do
  [ -d "$dir" ] || continue
  find "$dir" -name "*.jsonl" -print0
done |
  xargs -0 jq -cr --argjson start "$START_EPOCH" --argjson end "$END_EPOCH" '
    (.timestamp // .created_at // empty) as $ts
    | ($ts | fromdateiso8601?) as $epoch
    | select($epoch != null and $epoch >= $start and $epoch < $end)
  ' | wc -l

# 2. Check images were extracted (if any existed)
ls -la ~/PhoenixClaw/Journal/assets/$(date +%Y-%m-%d)/ 2>/dev/null || echo "No assets dir"

# 3. Check Ledger plugin ran (if installed)
grep -q "财务\|Finance\|💰" ~/PhoenixClaw/Journal/daily/$(date +%Y-%m-%d).md && echo "Ledger OK" || echo "Ledger section missing"

# 4. Check journal contains callout sections
grep -c "\[!" ~/PhoenixClaw/Journal/daily/$(date +%Y-%m-%d).md
```

**Diagnostic interpretation:**
- If images are missing → session logs were not properly scanned
- If Ledger section is missing → moment identification (step 3) was skipped
- If no callouts → journal generation used minimal template

Optional JS audit (structured summary, user/noise split):

```bash
node skills/phoenixclaw/references/session-day-audit.js --day "$(date +%Y-%m-%d)" --tz "Asia/Shanghai"
```

### Troubleshooting
If journals are not appearing as expected, check the following:

1. **System Wake State**: OpenClaw cron requires the host machine to be awake. On macOS/Linux, ensure the machine isn't sleeping during the scheduled time.
2. **Path Resolution**: Ensure `openclaw` is in the system PATH available to the cron daemon.
3. **Log Inspection**: Check the internal OpenClaw logs for task-specific errors:
   ```bash
   openclaw logs --task "PhoenixClaw nightly reflection"
   ```
4. **Timezone Mismatch**: If jobs run at unexpected hours, verify the detected timezone with `openclaw cron list` and consider hardcoding the timezone if `auto` fails.
5. **Tool Access**: Ensure the `isolated` session has proper permissions to read the memory directories and write to the journal storage.
6. **Memory Search Availability**: If `memory_search` is unavailable due to a missing embeddings provider (OpenAI/Gemini/Local), journaling will still continue by scanning daily memory and session logs directly. For cross-day pattern recognition and long-term recall, consider configuring an embeddings provider.
