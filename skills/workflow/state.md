# State Management

## When to Use State

Use `state/` when workflow needs to:
- Remember where it left off (cursor)
- Avoid reprocessing items (seen set)
- Resume after failure (checkpoint)
- Accumulate data across runs (accumulator)

## State Files

```
flows/{workflow}/state/
├── cursor.json      # Position marker
├── seen.json        # Processed item IDs
├── checkpoint.json  # Multi-step progress
└── accumulator.json # Data being collected
```

## cursor.json

Track position in a stream:

```json
{
  "last_id": "email_abc123",
  "last_timestamp": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:05:00Z"
}
```

Usage:
```bash
# Read cursor
LAST_ID=$(jq -r '.last_id // ""' state/cursor.json 2>/dev/null || echo "")

# Fetch only new items
if [ -n "$LAST_ID" ]; then
  curl "https://api.example.com/items?after=$LAST_ID" > data/01-fetch.json
else
  curl "https://api.example.com/items" > data/01-fetch.json
fi

# Update cursor
NEW_LAST=$(jq -r '.[-1].id' data/01-fetch.json)
echo "{\"last_id\":\"$NEW_LAST\",\"updated_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > state/cursor.json
```

## seen.json

Deduplicate across runs:

```json
{
  "seen": ["id1", "id2", "id3"],
  "updated_at": "2024-01-15T08:05:00Z"
}
```

Usage:
```bash
# Load seen set
SEEN=$(jq -r '.seen[]' state/seen.json 2>/dev/null | sort | uniq)

# Filter out already processed
jq --slurpfile seen <(echo "$SEEN" | jq -R -s 'split("\n") | map(select(. != ""))') \
   '[.[] | select(.id as $id | $seen[0] | index($id) | not)]' \
   data/01-fetch.json > data/02-new.json

# Update seen (keep last 1000)
jq -r '.[].id' data/02-new.json >> state/seen.tmp
tail -1000 state/seen.tmp | jq -R -s '{seen: split("\n") | map(select(. != "")), updated_at: now | todate}' > state/seen.json
rm state/seen.tmp
```

## checkpoint.json

Resume multi-step workflows after failure:

```json
{
  "completed_nodes": ["fetch", "filter", "transform"],
  "current_node": "notify",
  "partial_data": {
    "items_processed": 45,
    "items_total": 100
  },
  "started_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:03:00Z"
}
```

Usage:
```bash
# Check if resuming
LAST_NODE=$(jq -r '.current_node // ""' state/checkpoint.json 2>/dev/null || echo "")

run_node() {
  NODE=$1
  # Skip if already completed
  if jq -e ".completed_nodes | index(\"$NODE\")" state/checkpoint.json >/dev/null 2>&1; then
    log "$NODE" "skip" "\"reason\":\"already completed\""
    return 0
  fi
  
  # Mark as current
  jq ".current_node = \"$NODE\"" state/checkpoint.json > state/checkpoint.tmp && mv state/checkpoint.tmp state/checkpoint.json
  
  # Run the actual node logic
  $NODE
  
  # Mark as completed
  jq ".completed_nodes += [\"$NODE\"]" state/checkpoint.json > state/checkpoint.tmp && mv state/checkpoint.tmp state/checkpoint.json
}

# Execute with checkpointing
run_node "fetch"
run_node "filter"
run_node "transform"
run_node "notify"

# Clear checkpoint on success
rm -f state/checkpoint.json
```

## accumulator.json

Collect data over multiple runs (e.g., weekly summary):

```json
{
  "period": "2024-W03",
  "items": [
    {"date": "2024-01-15", "count": 10},
    {"date": "2024-01-16", "count": 15}
  ],
  "total": 25
}
```

Usage:
```bash
# Add today's data
TODAY=$(date +%Y-%m-%d)
TODAY_COUNT=$(jq length data/02-processed.json)

jq --arg date "$TODAY" --argjson count "$TODAY_COUNT" \
   '.items += [{"date": $date, "count": $count}] | .total += $count' \
   state/accumulator.json > state/accumulator.tmp && mv state/accumulator.tmp state/accumulator.json

# Check if period complete (e.g., end of week)
if [ "$(date +%u)" = "7" ]; then
  # Generate weekly report
  generate_report state/accumulator.json
  # Reset accumulator
  echo '{"period":"'$(date +%Y-W%V)'","items":[],"total":0}' > state/accumulator.json
fi
```

## State Corruption Recovery

If state becomes corrupted:

```bash
# Reset and re-scan
reset_state() {
  rm -rf state/*
  echo '{}' > state/cursor.json
  echo '{"seen":[]}' > state/seen.json
  log "state" "reset" "\"reason\":\"manual recovery\""
}
```

Document recovery procedure in flow.md:
```markdown
## Recovery
If state corrupted: `rm -rf state/*` and re-run. 
Will reprocess all items (idempotent operations safe).
```

## State Hygiene

Add cleanup to workflow:

```bash
# Prune seen.json to last 30 days worth of IDs
prune_seen() {
  CUTOFF=$(date -d "30 days ago" +%Y-%m-%d)
  # Implementation depends on whether seen.json tracks timestamps per ID
}

# Rotate old checkpoints
find state/ -name "checkpoint-*.json" -mtime +7 -delete
```
