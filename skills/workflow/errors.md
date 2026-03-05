# Error Handling

## Error Declaration in flow.md

Every node must specify behavior:

```markdown
### 2. Filter Important
- **On error:** retry(3) | fail | continue | alert
- **On empty:** skip | continue | fail
```

| Behavior | Meaning |
|----------|---------|
| `retry(N)` | Retry N times with exponential backoff, then fail |
| `fail` | Stop workflow, exit non-zero |
| `continue` | Log error, proceed to next node |
| `alert` | Notify, then continue or fail (specify which) |
| `skip` | Skip remaining nodes, exit success |

## Retry Pattern

```bash
retry() {
  local max_attempts=$1
  shift
  local attempt=1
  local delay=1
  
  while [ $attempt -le $max_attempts ]; do
    if "$@"; then
      return 0
    fi
    log "$NODE" "retry" "\"attempt\":$attempt,\"max\":$max_attempts,\"delay\":$delay"
    sleep $delay
    delay=$((delay * 2))  # Exponential backoff
    attempt=$((attempt + 1))
  done
  
  return 1
}

# Usage
retry 3 curl -s "https://api.example.com/items" > data/01-fetch.json \
  || { log "fetch" "error" "\"reason\":\"max retries exceeded\""; exit 1; }
```

## Partial Failure Handling

When workflow has multiple independent operations:

```bash
# Track failures
FAILURES=0

process_item() {
  if ! do_operation "$1"; then
    log "process" "error" "\"item\":\"$1\""
    FAILURES=$((FAILURES + 1))
    return 1
  fi
}

# Process all, collect failures
for item in $(jq -r '.[].id' data/01-items.json); do
  process_item "$item" || true  # Continue on failure
done

# Fail if too many errors
if [ $FAILURES -gt 5 ]; then
  log "workflow" "error" "\"reason\":\"too many failures\",\"count\":$FAILURES"
  exit 1
fi
```

## Rollback Pattern

For workflows that modify external state:

```bash
# Track what we've done
CREATED_IDS=()

create_item() {
  ID=$(curl -X POST ... | jq -r '.id')
  CREATED_IDS+=("$ID")
  echo "$ID"
}

rollback() {
  log "rollback" "start" "\"items\":${#CREATED_IDS[@]}"
  for id in "${CREATED_IDS[@]}"; do
    curl -X DELETE "https://api.example.com/items/$id" || true
  done
  log "rollback" "complete"
}

# Set trap for cleanup on failure
trap rollback ERR

# Operations that might fail
create_item "item1"
create_item "item2"
do_something_risky  # If this fails, rollback triggers

# Success - disable trap
trap - ERR
```

## Idempotency

Make operations safe to retry:

```bash
# Check before create
create_if_not_exists() {
  local id=$1
  local data=$2
  
  # Check if already exists
  if curl -s "https://api.example.com/items/$id" | jq -e '.id' >/dev/null 2>&1; then
    log "create" "skip" "\"reason\":\"already exists\",\"id\":\"$id\""
    return 0
  fi
  
  # Create
  curl -X POST -d "$data" "https://api.example.com/items"
}
```

Document idempotency in flow.md:
```markdown
## Idempotency
- **Key:** item_id
- **Check:** GET /items/{id} before POST
- **Behavior:** Skip if exists, create if new
```

## Alert on Error

```bash
alert_and_fail() {
  local message=$1
  
  # Send alert (Pushover, Slack, etc.)
  curl -X POST "https://api.pushover.net/1/messages.json" \
    -d "token=$PUSHOVER_TOKEN" \
    -d "user=$PUSHOVER_USER" \
    -d "message=Workflow failed: $message"
  
  log "alert" "sent" "\"message\":\"$message\""
  exit 1
}

# Usage
curl -s "$URL" > data/01-fetch.json \
  || alert_and_fail "Failed to fetch from $URL"
```

## Handling Empty Results

```bash
# Check for empty after fetch
if [ ! -s data/01-fetch.json ] || [ "$(jq length data/01-fetch.json)" -eq 0 ]; then
  case "$ON_EMPTY" in
    skip)
      log "fetch" "skip" "\"reason\":\"empty result\""
      exit 0
      ;;
    fail)
      log "fetch" "error" "\"reason\":\"empty result\""
      exit 1
      ;;
    continue)
      log "fetch" "warn" "\"reason\":\"empty result, continuing\""
      echo "[]" > data/01-fetch.json
      ;;
  esac
fi
```

## Lock Files (Prevent Concurrent Runs)

```bash
LOCKFILE="/tmp/workflow-${WORKFLOW_NAME}.lock"

acquire_lock() {
  exec 200>"$LOCKFILE"
  if ! flock -n 200; then
    log "workflow" "skip" "\"reason\":\"already running\""
    exit 0
  fi
}

# At start of run.sh
acquire_lock

# Lock released automatically on exit
```

## Error Logging

Always include context:

```bash
log_error() {
  local node=$1
  local error=$2
  local context=$3
  
  echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"run_id\":\"$RUN_ID\",\"node\":\"$node\",\"status\":\"error\",\"error\":\"$error\"${context:+,$context}}"
}

# Include relevant data
log_error "fetch" "HTTP 429" "\"url\":\"$URL\",\"retry_after\":60"
log_error "parse" "Invalid JSON" "\"line\":15,\"input_file\":\"data/01-fetch.json\""
```
