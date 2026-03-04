#!/usr/bin/env bash
# Loopuman CLI — Route tasks to verified human workers
# https://loopuman.com | https://www.8004scan.io/agents/celo/17

set -euo pipefail

# --- Config ---
CONFIG_FILE="${LOOPUMAN_CONFIG:-$HOME/.openclaw/skills/loopuman/config.json}"
if [[ ! -f "$CONFIG_FILE" ]]; then
  CONFIG_FILE="$HOME/.clawdbot/skills/loopuman/config.json"
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: Config file not found. Create one at ~/.openclaw/skills/loopuman/config.json"
  echo ""
  echo "mkdir -p ~/.openclaw/skills/loopuman"
  echo 'cat > ~/.openclaw/skills/loopuman/config.json << EOF'
  echo '{ "apiKey": "YOUR_API_KEY", "apiUrl": "https://api.loopuman.com" }'
  echo 'EOF'
  exit 1
fi

API_KEY=$(jq -r '.apiKey' "$CONFIG_FILE")
API_URL=$(jq -r '.apiUrl // "https://api.loopuman.com"' "$CONFIG_FILE")

if [[ "$API_KEY" == "null" || "$API_KEY" == "YOUR_API_KEY" ]]; then
  echo "Error: Invalid API key. Get one with:"
  echo "curl -X POST https://api.loopuman.com/api/v1/register -H 'Content-Type: application/json' -d '{\"email\":\"you@example.com\",\"company_name\":\"Your Name\"}'"
  exit 1
fi

# --- Helpers ---
api() {
  local method="$1" endpoint="$2"
  shift 2
  curl -sf -X "$method" \
    -H "x-api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    "$API_URL$endpoint" "$@"
}

usage() {
  cat <<EOF
Loopuman CLI — Route tasks to verified human workers

USAGE:
  loopuman.sh <command> [options]

COMMANDS:
  create    Create a new human task
  status    Check task status + get submissions
  wait      Poll until task completes
  list      List your tasks
  cancel    Cancel a task (refund if no workers)
  help      Show this help

EXAMPLES:
  loopuman.sh create --title "Verify address" \\
    --description "Is 123 Main St real? Reply YES/NO" \\
    --category other --budget 30 --estimated-seconds 120

  loopuman.sh status --task-id abc123
  loopuman.sh wait --task-id abc123 --interval 30 --timeout 600
  loopuman.sh list
  loopuman.sh cancel --task-id abc123
EOF
}

# --- Commands ---
cmd_create() {
  local title="" description="" category="other" budget=100 estimated_seconds=120 max_workers=1 webhook_url="" priority="normal"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --title) title="$2"; shift 2 ;;
      --description) description="$2"; shift 2 ;;
      --category) category="$2"; shift 2 ;;
      --budget) budget="$2"; shift 2 ;;
      --estimated-seconds) estimated_seconds="$2"; shift 2 ;;
      --max-workers) max_workers="$2"; shift 2 ;;
      --webhook) webhook_url="$2"; shift 2 ;;
      --priority) priority="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; exit 1 ;;
    esac
  done

  if [[ -z "$title" ]]; then
    echo "Error: --title is required"; exit 1
  fi
  [[ -z "$description" ]] && description="$title"

  local payload
  payload=$(jq -n \
    --arg title "$title" \
    --arg description "$description" \
    --arg category "$category" \
    --argjson budget_vae "$budget" \
    --argjson estimated_seconds "$estimated_seconds" \
    --argjson max_workers "$max_workers" \
    --arg priority "$priority" \
    --arg webhook_url "$webhook_url" \
    '{
      title: $title,
      description: $description,
      category: $category,
      budget_vae: $budget_vae,
      estimated_seconds: $estimated_seconds,
      max_workers: $max_workers,
      priority: $priority
    } + (if $webhook_url != "" then {webhook_url: $webhook_url} else {} end)')

  local response
  response=$(api POST "/api/v1/tasks" -d "$payload")

  if echo "$response" | jq -e '.task_id' > /dev/null 2>&1; then
    echo "$response" | jq '{task_id: .task_id, status: .status, budget_vae: .budget_vae, budget_usd: .budget_usd}'
  else
    echo "Error creating task:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    exit 1
  fi
}

cmd_status() {
  local task_id=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --task-id) task_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; exit 1 ;;
    esac
  done
  [[ -z "$task_id" ]] && { echo "Error: --task-id is required"; exit 1; }

  api GET "/api/v1/tasks/$task_id" | jq '.'
}

cmd_wait() {
  local task_id="" interval=30 timeout=600
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --task-id) task_id="$2"; shift 2 ;;
      --interval) interval="$2"; shift 2 ;;
      --timeout) timeout="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; exit 1 ;;
    esac
  done
  [[ -z "$task_id" ]] && { echo "Error: --task-id is required"; exit 1; }

  local elapsed=0
  echo "Waiting for task $task_id (polling every ${interval}s, timeout ${timeout}s)..."

  while [[ $elapsed -lt $timeout ]]; do
    local response
    response=$(api GET "/api/v1/tasks/$task_id" 2>/dev/null || echo '{"status":"error"}')
    local status approved
    status=$(echo "$response" | jq -r '.status // "unknown"')
    approved=$(echo "$response" | jq -r '.progress.approved // 0')

    if [[ "$approved" -gt 0 ]]; then
      echo "✅ Task has approved submissions!"
      echo "$response" | jq '{task_id: .task_id, status: .status, submissions: .submissions}'
      return 0
    fi

    case "$status" in
      expired|cancelled)
        echo "Task $status."
        echo "$response" | jq '{task_id: .task_id, status: .status, progress: .progress}'
        return 1
        ;;
      *)
        echo "  [$elapsed/${timeout}s] Status: $status — approved: $approved"
        ;;
    esac

    sleep "$interval"
    elapsed=$((elapsed + interval))
  done

  echo "Timeout after ${timeout}s. Check later: loopuman.sh status --task-id $task_id"
  return 1
}

cmd_list() {
  api GET "/api/v1/tasks" | jq '.'
}

cmd_cancel() {
  local task_id=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --task-id) task_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; exit 1 ;;
    esac
  done
  [[ -z "$task_id" ]] && { echo "Error: --task-id is required"; exit 1; }

  api DELETE "/api/v1/tasks/$task_id" | jq '.'
}

# --- Main ---
case "${1:-help}" in
  create)  shift; cmd_create "$@" ;;
  status)  shift; cmd_status "$@" ;;
  wait)    shift; cmd_wait "$@" ;;
  list)    shift; cmd_list ;;
  cancel)  shift; cmd_cancel "$@" ;;
  help|--help|-h) usage ;;
  *) echo "Unknown command: $1"; usage; exit 1 ;;
esac
