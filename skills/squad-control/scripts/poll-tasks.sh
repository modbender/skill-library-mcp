#!/bin/bash
# Poll Squad Control for pending tasks
# Called by the agent's cron job
# Requires: SC_API_URL and SC_API_KEY environment variables

set -euo pipefail

SC_API_URL="${SC_API_URL:?SC_API_URL not set}"
SC_API_KEY="${SC_API_KEY:?SC_API_KEY not set}"

# Poll for pending tasks
response=$(curl -sfL "${SC_API_URL}/api/tasks/pending" \
  -H "x-api-key: ${SC_API_KEY}" 2>/dev/null) || {
  echo "ERROR: Failed to reach Squad Control API at ${SC_API_URL}"
  exit 1
}

# Extract workspace context (repo URL + GitHub token for private repos)
repo_url=$(echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('workspace', {}).get('repoUrl', ''))
" 2>/dev/null || echo "")

github_token=$(echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('workspace', {}).get('githubToken', ''))
" 2>/dev/null || echo "")

task_count=$(echo "$response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len(d.get('tasks', [])))
" 2>/dev/null || echo "0")

# Export context for the agent to use
export REPO_URL="$repo_url"
export GITHUB_TOKEN="$github_token"

# Also check for review tasks (tasks with status=review that need Hawk)
review_response=$(curl -sfL "${SC_API_URL}/api/tasks/list?status=review" \
  -H "x-api-key: ${SC_API_KEY}" 2>/dev/null) || review_response=""

review_count=$(echo "$review_response" | python3 -c "
import json, sys
d = json.load(sys.stdin)
# Only tasks with a PR deliverable and not already picked up
def has_pr(deliverables):
    return any(d.get('type') == 'pr' or '/pull/' in (d.get('url') or '') for d in deliverables)
tasks = [t for t in d.get('tasks', [])
         if has_pr(t.get('deliverables', []))
         and not t.get('pickedUpAt')]
print(len(tasks))
" 2>/dev/null || echo "0")

# Check for stuck "working" tasks — has PR deliverable but hasn't transitioned
# (sub-agent completed work but never called set-review)
working_response=$(curl -sfL "${SC_API_URL}/api/tasks/list?status=working" \
  -H "x-api-key: ${SC_API_KEY}" 2>/dev/null) || working_response=""

stuck_json=$(echo "$working_response" | python3 -c "
import json, sys, time
d = json.load(sys.stdin)
now_ms = time.time() * 1000
threshold_ms = 30 * 60 * 1000  # 30 minutes
def has_pr(deliverables):
    return any(d.get('type') == 'pr' or '/pull/' in (d.get('url') or '') for d in deliverables)
stuck = [t for t in d.get('tasks', [])
         if has_pr(t.get('deliverables', []))
         and (not t.get('pickedUpAt') or (t.get('startedAt') and now_ms - t['startedAt'] > threshold_ms))]
print(json.dumps({'tasks': stuck}))
" 2>/dev/null || echo '{"tasks":[]}')

stuck_count=$(echo "$stuck_json" | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('tasks', [])))" 2>/dev/null || echo "0")

if [ "$task_count" -eq 0 ] && [ "$review_count" -eq 0 ] && [ "$stuck_count" -eq 0 ]; then
  echo "HEARTBEAT_OK"
  exit 0
fi

# Output pending tasks (if any)
if [ "$task_count" -gt 0 ]; then
  echo "PENDING_TASKS:"
  echo "$response"
fi

# Output review tasks (if any)
if [ "$review_count" -gt 0 ]; then
  echo "REVIEW_TASKS:"
  echo "$review_response"
fi

# Output stuck tasks for auto-rescue (if any) — only filtered tasks, not all working
if [ "$stuck_count" -gt 0 ]; then
  echo "STUCK_TASKS:"
  echo "$stuck_json"
fi
