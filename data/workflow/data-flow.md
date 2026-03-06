# Data Flow Between Nodes

## Core Pattern

Each node reads input, processes, writes output. Next node reads that output.

```
Trigger → data/00-trigger.json
Node 1  → data/01-fetch.json
Node 2  → data/02-filter.json
Node 3  → data/03-transform.json
...
```

## In run.sh

```bash
#!/bin/bash
set -euo pipefail

RUN_ID=$(uuidgen | cut -c1-8)
log() { echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"run_id\":\"$RUN_ID\",\"node\":\"$1\",\"status\":\"$2\"${3:+,$3}}"; }

mkdir -p data logs
LOGFILE="logs/$(date +%Y-%m-%d-%H-%M-%S).jsonl"

# Node 1: Fetch
log "fetch" "start" >> "$LOGFILE"
curl -s "https://api.example.com/items" > data/01-fetch.json
log "fetch" "ok" "\"count\":$(jq length data/01-fetch.json)" >> "$LOGFILE"

# Node 2: Filter (reads 01, writes 02)
log "filter" "start" >> "$LOGFILE"
jq '[.[] | select(.important == true)]' data/01-fetch.json > data/02-filter.json
COUNT=$(jq length data/02-filter.json)
if [ "$COUNT" -eq 0 ]; then
  log "filter" "skip" "\"reason\":\"empty result\"" >> "$LOGFILE"
  exit 0  # Or continue based on flow.md "On empty"
fi
log "filter" "ok" "\"count\":$COUNT" >> "$LOGFILE"

# Node 3: Transform (reads 02, writes 03)
log "transform" "start" >> "$LOGFILE"
jq '[.[] | {id, title, url}]' data/02-filter.json > data/03-transform.json
log "transform" "ok" >> "$LOGFILE"
```

## Type Contracts

Define input/output schemas in flow.md to ensure compatibility:

```markdown
### 1. Fetch Emails
- **Input schema:** `{ since: ISO8601 }` (from trigger or state)
- **Output schema:** `{ emails: [{ id: string, from: string, subject: string, body: string }] }`

### 2. Filter Important
- **Input schema:** `{ emails: array }` (matches previous output)
- **Output schema:** `{ emails: array }` (same structure, filtered)
```

## Accessing Previous Steps

To access data from a non-adjacent step:

```bash
# Node 4 needs data from Node 1 AND Node 3
ORIGINAL_COUNT=$(jq length data/01-fetch.json)
FILTERED=$(cat data/03-transform.json)
```

## Parallel Branches

When workflow has parallel steps, use prefixes:

```
data/03a-twitter.json   # Branch A
data/03b-linkedin.json  # Branch B
data/04-merge.json      # After join
```

In script:
```bash
# Parallel execution
twitter_post &
PID_TW=$!
linkedin_post &
PID_LI=$!

wait $PID_TW $PID_LI
```

## Large Data Handling

For datasets that don't fit in memory:

```bash
# Stream processing with jq
jq -c '.[]' data/01-fetch.json | while read -r item; do
  process_item "$item"
done > data/02-processed.json
```

For very large files, consider pagination:
```bash
CURSOR=""
while true; do
  RESPONSE=$(curl "https://api.example.com/items?cursor=$CURSOR")
  echo "$RESPONSE" | jq '.items[]' >> data/01-fetch.json
  CURSOR=$(echo "$RESPONSE" | jq -r '.next_cursor // empty')
  [ -z "$CURSOR" ] && break
done
```

## Data Cleanup

After successful run, optionally clean intermediate files:

```bash
# Keep only final output
cleanup() {
  rm -f data/0[1-9]-*.json  # Remove intermediate
  # Keep data/final.json
}
trap cleanup EXIT
```

Or rotate old data:
```bash
# Keep last 7 days of data
find data/ -name "*.json" -mtime +7 -delete
```
