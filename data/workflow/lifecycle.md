# Workflow Lifecycle

## Creating

### 1. Define Requirements

Ask:
- "What triggers this?" — cron, webhook, manual
- "What's the input?" — API, file, event payload
- "What's the output?" — notification, file, API call
- "What if it fails?" — retry, alert, skip
- "Does it need state?" — cursor, seen set, checkpoint

### 2. Check Existing Components

```bash
# Search connections
ls workflows/components/connections/

# Search nodes
ls workflows/components/nodes/

# Search similar workflows
grep -i "keyword" workflows/index.md
```

### 3. Create Workflow Folder

```bash
WORKFLOW="my-workflow"
mkdir -p "workflows/flows/$WORKFLOW"/{state,data,logs}
touch "workflows/flows/$WORKFLOW"/{flow.md,config.yaml,run.sh,CHANGELOG.md}
chmod +x "workflows/flows/$WORKFLOW/run.sh"
```

### 4. Write config.yaml

Non-secret parameters:
```yaml
threshold: 0.05
max_items: 100
recipients:
  - team@example.com

environments:
  test:
    recipients:
      - test@localhost
```

### 5. Write flow.md

See `structure.md` for format. Include:
- Trigger with timezone (if cron)
- Each node with input/output schemas
- Error handling per node
- Dependencies (if any)

### 6. Write run.sh

```bash
#!/bin/bash
set -euo pipefail

# === Configuration ===
WORKFLOW_NAME="my-workflow"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Dry-run mode
DRY_RUN="${DRY_RUN:-false}"
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
fi

# === Logging ===
RUN_ID=$(uuidgen | cut -c1-8)
LOGFILE="logs/$(date +%Y-%m-%d-%H-%M-%S).jsonl"
mkdir -p logs data state

log() {
  local node=$1 status=$2
  shift 2
  local extra=""
  [ $# -gt 0 ] && extra=",$*"
  echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"run_id\":\"$RUN_ID\",\"node\":\"$node\",\"status\":\"$status\"$extra}" >> "$LOGFILE"
}

# === Lock ===
LOCKFILE="/tmp/workflow-$WORKFLOW_NAME.lock"
exec 200>"$LOCKFILE"
flock -n 200 || { log "workflow" "skip" "\"reason\":\"already running\""; exit 0; }

# === Secrets ===
# TOKEN=$(security find-generic-password -a clawdbot -s "${WORKFLOW_NAME}_service_key" -w)

# === Config ===
THRESHOLD=$(yq '.threshold' config.yaml)
MAX_ITEMS=$(yq '.max_items' config.yaml)

# === Node 1: Fetch ===
log "fetch" "start"
if [ "$DRY_RUN" = "true" ]; then
  log "fetch" "dry-run" "\"would\":\"GET https://api.example.com/items\""
  echo '[]' > data/01-fetch.json
else
  curl -s "https://api.example.com/items?limit=$MAX_ITEMS" > data/01-fetch.json
fi
log "fetch" "ok" "\"count\":$(jq length data/01-fetch.json)"

# === Node 2: Filter ===
log "filter" "start"
jq "[.[] | select(.value > $THRESHOLD)]" data/01-fetch.json > data/02-filter.json
COUNT=$(jq length data/02-filter.json)
if [ "$COUNT" -eq 0 ]; then
  log "filter" "skip" "\"reason\":\"no items above threshold\""
  exit 0
fi
log "filter" "ok" "\"count\":$COUNT"

# === Node 3: Notify ===
log "notify" "start"
MESSAGE="Found $COUNT items above threshold"
if [ "$DRY_RUN" = "true" ]; then
  log "notify" "dry-run" "\"would_send\":\"$MESSAGE\""
else
  curl -X POST "https://api.pushover.net/1/messages.json" \
    -d "token=$PUSHOVER_TOKEN" \
    -d "user=$PUSHOVER_USER" \
    -d "message=$MESSAGE"
fi
log "notify" "ok"

log "workflow" "complete"
```

### 7. Initialize CHANGELOG.md

```markdown
# Changelog

## v1.0 (YYYY-MM-DD)
- Initial version
- Fetches items, filters by threshold, notifies
```

### 8. Register in index.md

Add entry under Active section.

### 9. Schedule (if cron)

```bash
# Edit crontab
crontab -e

# Add entry
0 8 * * * cd /path/to/workflows/flows/my-workflow && ./run.sh >> /dev/null 2>&1
```

Or use OpenClaw cron:
```
cron action=add job={...}
```

## Testing

### Dry-Run

```bash
cd workflows/flows/my-workflow
./run.sh --dry-run

# Or via environment
DRY_RUN=true ./run.sh
```

### With Test Config

```bash
# Use test environment from config.yaml
ENV=test ./run.sh --dry-run
```

### Verify Logs

```bash
cat logs/*.jsonl | jq -s 'group_by(.run_id) | .[] | {run: .[0].run_id, nodes: [.[].node], status: .[-1].status}'
```

## Updating

### 1. Increment Version

Update flow.md: `**Version:** 1.1`

### 2. Update CHANGELOG.md

```markdown
## v1.1 (YYYY-MM-DD)
- Changed: filter threshold logic
- Fixed: retry on network timeout
```

### 3. Test

```bash
./run.sh --dry-run
```

### 4. Update Component Usage

If you added/removed connections or nodes, update their "Workflows Using This" lists.

## Versioning / Rollback

### Keep Previous Versions

```bash
# Before major changes
cp run.sh "versions/run.sh.v$(yq '.version' flow.md)"
```

### Rollback

```bash
# Restore previous version
cp versions/run.sh.v1.0 run.sh

# Update CHANGELOG
echo "## v1.2 (YYYY-MM-DD)" >> CHANGELOG.md
echo "- Rolled back to v1.0 due to {reason}" >> CHANGELOG.md
```

## Archiving

### 1. Update index.md

Move from Active to Archived:
```markdown
## Archived

### old-workflow
**Archived:** 2024-02-01
**Reason:** Replaced by new-workflow
```

### 2. Remove Schedule

```bash
# Remove from crontab
crontab -l | grep -v "old-workflow" | crontab -
```

### 3. Update Component References

Remove from "Workflows Using This" in all connection and node files.

### 4. Keep Files

Don't delete — may need for reference or restore.

## Debugging

### Check Recent Logs

```bash
tail -100 workflows/flows/{name}/logs/*.jsonl | jq .
```

### Find Errors

```bash
grep '"status":"error"' workflows/flows/{name}/logs/*.jsonl | jq .
```

### Manual Run

```bash
cd workflows/flows/{name}
./run.sh
echo "Exit code: $?"
```

### Check State

```bash
cat workflows/flows/{name}/state/*.json | jq .
```

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Script doesn't run | Missing shebang or +x | `chmod +x run.sh` |
| Auth fails | Token expired | Refresh OAuth, update secret |
| Lock held | Previous run crashed | `rm /tmp/workflow-*.lock` |
| Wrong data | Stale state | Clear state/, re-run |
| No logs | Cron redirect wrong | Check crontab syntax |
