---
name: token-monitor
description: Monitor OpenClaw token/quota usage and alert when any quota drops below a threshold (default 20%). Uses `openclaw models status` and writes only a local state file to avoid duplicate alerts. **Does not handle secrets.** **Token cost:** Script itself: 0 tokens (pure bash). Heartbeat integration: ~1k-2k tokens/hour (reading HEARTBEAT.md + executing script). Alert delivery: ~500-1k tokens/alert. **Optimization:** Use system cron instead of heartbeat to reduce to ~0 tokens (except alerts).
---

# Token Monitor

Monitors OpenClaw token/quota usage and outputs alerts when any quota drops below a configurable threshold (default 20%).

## Features

- **Multi-provider support**: Monitors all configured providers (openai-codex, github-copilot, google-antigravity, etc.)
- **Multi-quota tracking**: Tracks all quota types (5h, Day, Premium, Chat, etc.)
- **Smart alerting**: Only alerts on new low-quota events (no spam)
- **Recovery notifications**: Alerts when quota recovers above threshold
- **State persistence**: Remembers previous warnings across runs

## Install / Update (ClawHub)

Install:
```bash
clawhub install token-monitor
```

Update:
```bash
clawhub update token-monitor
```

(You can also run `clawhub update --all`.)

---

## Disable / Uninstall

### If enabled via HEARTBEAT.md
Remove the Token Monitor section from `HEARTBEAT.md` (or comment it out). No further uninstall needed.

### If enabled via an OpenClaw cron job
Disable/remove the cron job:
```bash
openclaw cron list
openclaw cron remove <jobId>
```

### Optional cleanup (state)
```bash
rm -f ~/.openclaw/workspace/skills/token-monitor/.token-state.json
```

---

## Usage

### Manual Check

Run the monitoring script directly:

```bash
skills/token-monitor/scripts/check-quota.sh
```

If installed into `~/.openclaw/skills`, run:

```bash
~/.openclaw/skills/token-monitor/scripts/check-quota.sh
```

With custom threshold (default 20%):

```bash
skills/token-monitor/scripts/check-quota.sh --threshold 10
```

### Automated Monitoring (Heartbeat)

Add to `HEARTBEAT.md` for periodic checks:

```markdown
## Token Monitor (every ~60min, rotate)

Check model quotas and alert if below threshold.

**Instructions:**
1. Run `output=$(skills/token-monitor/scripts/check-quota.sh 2>&1)`
2. If output non-empty → send wake event with output text
3. If empty → all quotas OK, continue silently

**Rotate check:** Only run every ~4th heartbeat (once/hour if heartbeat is 15min)

**Example integration:**
```bash
output=$(skills/token-monitor/scripts/check-quota.sh 2>&1)
if [[ -n "$output" ]]; then
  openclaw cron wake --text "$output" --mode now
fi
```
```

### Automated Monitoring (Cron Job)

Create a dedicated cron job for precise scheduling:

```bash
openclaw cron add --schedule "*/30 * * * *" \
  --payload '{"kind":"systemEvent","text":"Run quota monitor: skills/token-monitor/scripts/check-quota.sh"}' \
  --name "Token Monitor (30min)"
```

## Output

### Low Quota Alert

```
⚠️ Model Quota Alert (<20%):
• openai-codex Day: 0% left
• github-copilot Premium: 5% left
```

### Recovery Alert

```
✅ Quota Recovered (>=20%):
• openai-codex 5h: 100% left
```

## State File

The script maintains state in:
```
~/.openclaw/workspace/skills/token-monitor/.token-state.json
```

Example state:
```json
{
  "warned": [
    "openai-codex Day: 0% left",
    "github-copilot Premium: 5% left"
  ],
  "current": [
    "openai-codex:5h=100",
    "openai-codex:Day=0",
    "github-copilot:Premium=5",
    "github-copilot:Chat=100"
  ],
  "lastCheck": "2026-02-15T09:30:00Z",
  "threshold": 20
}
```

## Configuration

### Environment Variables

- `QUOTA_THRESHOLD`: Alert threshold percentage (default: 20)
- `QUOTA_STATE_FILE`: Path to state file (default: `~/.openclaw/workspace/skills/token-monitor/.token-state.json`)

### Script Arguments

- `--threshold <pct>`: Set alert threshold (overrides `QUOTA_THRESHOLD`)
- `--state-file <path>`: Set state file location (overrides `QUOTA_STATE_FILE`)

## How It Works

1. **Parse quota data**: Runs `openclaw models status` and extracts all "X% left" values
2. **Identify low quotas**: Finds all quotas below threshold
3. **Compare with previous state**: Determines new warnings and recoveries
4. **Send alerts**: Uses `openclaw cron wake` to deliver notifications
5. **Update state**: Saves current state for next run

## Dependencies

- `openclaw` CLI (models status, cron wake)
- `jq` (JSON parsing)
- `bash` 4.0+

## Troubleshooting

**No alerts sent:**
- Check that quota is actually below threshold: `openclaw models status`
- Verify state file permissions: `cat ~/.openclaw/workspace/skills/token-monitor/.token-state.json`
- Run script manually to see output: `skills/token-monitor/scripts/check-quota.sh`

**Duplicate alerts:**
- State file may be corrupted or deleted
- Check state file for `warned` array: `jq .warned ~/.openclaw/workspace/skills/token-monitor/.token-state.json`

**Script fails:**
- Ensure `jq` is installed: `jq --version`
- Check script permissions: `ls -l skills/token-monitor/scripts/check-quota.sh`
- Run with verbose output: `bash -x skills/token-monitor/scripts/check-quota.sh`
