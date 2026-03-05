#!/usr/bin/env bash
set -euo pipefail

# Job Execution Monitor healthcheck script
# Monitors OpenClaw cron jobs and emits alerts via `openclaw cron wake` if jobs are missing/late.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
CONFIG_FILE="${WORKSPACE}/job-execution-monitor.json"
STATE_FILE="${WORKSPACE}/.job-execution-monitor-state.json"

# Check dependencies
for cmd in jq date; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: $cmd not found" >&2
    exit 1
  fi
done

# Check openclaw CLI
if ! command -v openclaw &>/dev/null; then
  echo "ERROR: openclaw CLI not found" >&2
  exit 1
fi

# Load config
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "ERROR: Config not found: $CONFIG_FILE" >&2
  echo "Copy from: ${SCRIPT_DIR}/../config/job-execution-monitor.example.json" >&2
  exit 1
fi

CONFIG=$(cat "$CONFIG_FILE")
CHECK_INTERVAL=$(echo "$CONFIG" | jq -r '.checkIntervalMin // 10')

# Initialize state file
if [[ ! -f "$STATE_FILE" ]]; then
  echo '{"lastCheck": 0, "alerts": {}}' > "$STATE_FILE"
fi

STATE=$(cat "$STATE_FILE")

# Get current timestamp
NOW=$(date +%s)
LAST_CHECK=$(echo "$STATE" | jq -r '.lastCheck // 0')

# Helper: Send wake event via openclaw CLI
send_wake() {
  local text="$1"
  # Use heredoc to avoid quoting issues
  openclaw cron wake --text="$text" --mode=now 2>/dev/null || true
}

# Helper: Parse cron schedule to next expected unix timestamp
# Simplified: only handles "M H * * *" format for now
parse_cron_next() {
  local schedule="$1"
  local tolerance="${2:-600}"
  
  # Extract hour and minute (assumes "M H * * *" format)
  local minute=$(echo "$schedule" | awk '{print $1}')
  local hour=$(echo "$schedule" | awk '{print $2}')
  
  # Get today's date at specified time
  local today_run=$(date -d "today ${hour}:${minute}" +%s)
  
  # If we're past that time, check against today's run
  if (( NOW > today_run + tolerance )); then
    # Missed today, next would be tomorrow
    echo "$today_run"
  else
    echo "$today_run"
  fi
}

# Check each configured job
echo "$CONFIG" | jq -r '.jobs | keys[]' | while read -r job_name; do
  job_config=$(echo "$CONFIG" | jq -r --arg name "$job_name" '.jobs[$name]')
  
  schedule=$(echo "$job_config" | jq -r '.schedule // ""')
  tolerance=$(echo "$job_config" | jq -r '.tolerance // 600')
  
  if [[ -z "$schedule" ]]; then
    continue
  fi
  
  # Get job status from openclaw (redirects + json parsing)
  job_json=$(openclaw cron list 2>/dev/null | jq --arg name "$job_name" '.jobs[] | select(.name == $name)' 2>/dev/null || echo '{}')
  
  if [[ "$job_json" == "{}" ]]; then
    # Job not found
    alert_key="${job_name}_missing"
    already_alerted=$(echo "$STATE" | jq -r --arg k "$alert_key" '.alerts[$k] // 0')
    
    if (( already_alerted == 0 )); then
      msg="🔴 Job-Observer: Job \"$job_name\" not found in cron list"
      echo "$msg"
      send_wake "$msg"
      STATE=$(echo "$STATE" | jq --arg k "$alert_key" --arg t "$NOW" '.alerts[$k] = ($t | tonumber)')
    fi
    continue
  fi
  
  # Extract last run time (ms) and status
  last_run_ms=$(echo "$job_json" | jq -r '.state.lastRunAtMs // 0')
  last_status=$(echo "$job_json" | jq -r '.state.lastStatus // "unknown"')
  last_run=$((last_run_ms / 1000))  # Convert to seconds
  
  if (( last_run == 0 )); then
    # Never ran
    alert_key="${job_name}_never_ran"
    already_alerted=$(echo "$STATE" | jq -r --arg k "$alert_key" '.alerts[$k] // 0')
    
    if (( already_alerted == 0 )); then
      msg="🔴 Job-Observer: Job \"$job_name\" never ran"
      echo "$msg"
      send_wake "$msg"
      STATE=$(echo "$STATE" | jq --arg k "$alert_key" --arg t "$NOW" '.alerts[$k] = ($t | tonumber)')
    fi
    continue
  fi
  
  # Check if job missed its schedule
  expected_time=$(parse_cron_next "$schedule" "$tolerance")
  time_diff=$((NOW - last_run))
  expected_diff=$((NOW - expected_time))
  
  if (( expected_diff > tolerance && time_diff > tolerance )); then
    # Missed
    alert_key="${job_name}_missed"
    already_alerted=$(echo "$STATE" | jq -r --arg k "$alert_key" '.alerts[$k] // 0')
    
    if (( already_alerted == 0 )); then
      hours_ago=$((time_diff / 3600))
      mins_ago=$(( (time_diff % 3600) / 60 ))
      msg="🔴 Job-Observer: \"$job_name\" missed schedule (expected $(date -d @$expected_time '+%H:%M'), last run ${hours_ago}h ${mins_ago}m ago)"
      echo "$msg"
      send_wake "$msg"
      STATE=$(echo "$STATE" | jq --arg k "$alert_key" --arg t "$NOW" '.alerts[$k] = ($t | tonumber)')
    fi
  else
    # Job ran on time - clear any previous alerts
    alert_key="${job_name}_missed"
    was_alerted=$(echo "$STATE" | jq -r --arg k "$alert_key" '.alerts[$k] // 0')
    
    if (( was_alerted > 0 )); then
      msg="✅ Job-Observer: \"$job_name\" recovered (last run $(date -d @$last_run '+%H:%M'))"
      echo "$msg"
      send_wake "$msg"
      STATE=$(echo "$STATE" | jq --arg k "$alert_key" 'del(.alerts[$k])')
    fi
  fi
done

# Update state file
STATE=$(echo "$STATE" | jq --arg t "$NOW" '.lastCheck = ($t | tonumber)')
echo "$STATE" > "$STATE_FILE"

echo "✅ Job-Observer check complete ($(date '+%Y-%m-%d %H:%M:%S'))"
