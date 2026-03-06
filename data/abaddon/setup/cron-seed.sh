#!/bin/bash
# abaddon/setup/cron-seed.sh
# Adds the Abaddon nightly red team cron to ~/.openclaw/cron/jobs.json
# Safe to run multiple times — checks for duplicates before adding.

set -euo pipefail

JOBS_FILE="${OPENCLAW_DIR:-$HOME/.openclaw}/cron/jobs.json"
TG_GROUP="${ABADDON_TG_GROUP:-}"   # e.g. -1003772049875
TG_THREAD="${ABADDON_TG_THREAD:-}" # e.g. 64 (Security topic)

if [ ! -f "$JOBS_FILE" ]; then
  echo "❌ jobs.json not found at $JOBS_FILE"
  echo "   Is OpenClaw installed and initialized?"
  exit 1
fi

# Check for existing Abaddon job
if python3 -c "
import json, sys
with open('$JOBS_FILE') as f:
    d = json.load(f)
jobs = d.get('jobs', [])
names = [j.get('name','') for j in jobs]
if any('Abaddon' in n for n in names):
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null; then
  echo "⏭️  Abaddon cron already exists in jobs.json — skipping"
  exit 0
fi

# Build delivery config
if [ -n "$TG_GROUP" ] && [ -n "$TG_THREAD" ]; then
  DELIVERY="{\"mode\": \"announce\", \"channel\": \"telegram\", \"to\": \"${TG_GROUP}:topic:${TG_THREAD}\"}"
else
  DELIVERY="{\"mode\": \"announce\"}"
  echo "ℹ️  No TG_GROUP/TG_THREAD set — Abaddon will announce to default channel."
  echo "   Re-run with: ABADDON_TG_GROUP=-1003772049875 ABADDON_TG_THREAD=64 bash setup/cron-seed.sh"
fi

python3 - <<PYEOF
import json, uuid, time

jobs_file = "$JOBS_FILE"
delivery = $DELIVERY

with open(jobs_file) as f:
    d = json.load(f)

new_job = {
    "id": str(uuid.uuid4()),
    "agentId": "main",
    "name": "Gideon — Abaddon Nightly Red Team",
    "enabled": True,
    "createdAtMs": int(time.time() * 1000),
    "updatedAtMs": int(time.time() * 1000),
    "schedule": {
        "kind": "cron",
        "expr": "45 3 * * *",
        "tz": "America/Chicago"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "payload": {
        "kind": "agentTurn",
        "message": "RED TEAM SCAN — ABADDON MODE. Read agents/observer/AGENT_PROMPT.md for the full protocol under ## Red Team Mode (Abaddon). Run the complete adversarial scan. Assign a letter grade A-F. CRITICAL findings: send immediate Telegram alert. Save technical report to memory/audits/abaddon-YYYY-MM-DD.md. Post summary with grade to Telegram Security topic.",
        "model": "anthropic/claude-sonnet-4-6",
        "timeoutSeconds": 600
    },
    "delivery": delivery
}

if "jobs" not in d:
    d["jobs"] = []

d["jobs"].append(new_job)

with open(jobs_file, "w") as f:
    json.dump(d, f, indent=2)

print(f"✅ Abaddon cron added: {new_job['id']}")
print(f"   Schedule: 3:45 AM CST daily")
print(f"   Delivery: {json.dumps(delivery)}")
PYEOF
