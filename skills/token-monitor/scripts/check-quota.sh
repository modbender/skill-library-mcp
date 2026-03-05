#!/bin/bash
# Quota Monitor - Warns when model quota drops below threshold
# Usage: check-quota.sh [--threshold 20] [--state-file /path/to/state.json]

set -euo pipefail

# Defaults
THRESHOLD=${QUOTA_THRESHOLD:-20}
STATE_FILE="${QUOTA_STATE_FILE:-$HOME/.openclaw/workspace/skills/token-monitor/.token-state.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    --state-file)
      STATE_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Get current model status
STATUS_OUTPUT=$(openclaw models status 2>&1 || true)

# Parse usage lines (e.g., "openai-codex usage: 5h 100% left · Day 0% left")
# Extract provider and all quota segments
LOW_QUOTAS=()
CURRENT_QUOTAS=()

while IFS= read -r line; do
  # Extract provider name (e.g., "openai-codex", "github-copilot")
  # Allow leading whitespace/dashes from formatted output
  if [[ $line =~ ^[[:space:]-]*([a-z-]+)\ usage:\ (.+)$ ]]; then
    provider="${BASH_REMATCH[1]}"
    usage_data="${BASH_REMATCH[2]}"
    
    # Parse all "X% left" segments
    while [[ $usage_data =~ ([^·]+)\ ([0-9]+)%\ left ]]; do
      quota_name="${BASH_REMATCH[1]}"
      quota_pct="${BASH_REMATCH[2]}"
      
      # Clean quota name (remove leading/trailing whitespace)
      quota_name=$(echo "$quota_name" | xargs)
      
      # Track current quota
      CURRENT_QUOTAS+=("${provider}:${quota_name}=${quota_pct}")
      
      # Check if below threshold
      if [[ $quota_pct -lt $THRESHOLD ]]; then
        LOW_QUOTAS+=("${provider} ${quota_name}: ${quota_pct}% left")
      fi
      
      # Remove matched portion for next iteration
      usage_data="${usage_data#*${BASH_REMATCH[0]}}"
    done
  fi
done <<< "$STATUS_OUTPUT"

# Load previous state
PREVIOUS_WARNINGS=()
if [[ -f "$STATE_FILE" ]]; then
  # Read previous warnings (one per line)
  while IFS= read -r warned_quota; do
    PREVIOUS_WARNINGS+=("$warned_quota")
  done < <(jq -r '.warned[]? // empty' "$STATE_FILE" 2>/dev/null || echo "")
fi

# Determine new warnings (low quotas that weren't previously warned)
NEW_WARNINGS=()
for low_quota in "${LOW_QUOTAS[@]}"; do
  already_warned=false
  for prev in "${PREVIOUS_WARNINGS[@]}"; do
    if [[ "$low_quota" == "$prev" ]]; then
      already_warned=true
      break
    fi
  done
  
  if [[ "$already_warned" == "false" ]]; then
    NEW_WARNINGS+=("$low_quota")
  fi
done

# Determine recoveries (previously warned quotas now above threshold)
RECOVERIES=()
for prev in "${PREVIOUS_WARNINGS[@]}"; do
  still_low=false
  for low_quota in "${LOW_QUOTAS[@]}"; do
    if [[ "$low_quota" == "$prev" ]]; then
      still_low=true
      break
    fi
  done
  
  if [[ "$still_low" == "false" ]]; then
    RECOVERIES+=("$prev")
  fi
done

# Send wake events for new warnings
if [[ ${#NEW_WARNINGS[@]} -gt 0 ]]; then
  MESSAGE="⚠️ Model Quota Alert (<${THRESHOLD}%):\n"
  for warning in "${NEW_WARNINGS[@]}"; do
    MESSAGE="${MESSAGE}\n• ${warning}"
  done
  
  # Output alert (caller decides how to notify)
  echo -e "$MESSAGE"
fi

# Send wake events for recoveries
if [[ ${#RECOVERIES[@]} -gt 0 ]]; then
  MESSAGE="✅ Quota Recovered (>=${THRESHOLD}%):\n"
  for recovery in "${RECOVERIES[@]}"; do
    MESSAGE="${MESSAGE}\n• ${recovery}"
  done
  
  # Output recovery (caller decides how to notify)
  echo -e "$MESSAGE"
fi

# Update state file
mkdir -p "$(dirname "$STATE_FILE")"
jq -n \
  --argjson warned "$(printf '%s\n' "${LOW_QUOTAS[@]}" | jq -R . | jq -s .)" \
  --argjson current "$(printf '%s\n' "${CURRENT_QUOTAS[@]}" | jq -R . | jq -s .)" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    warned: $warned,
    current: $current,
    lastCheck: $timestamp,
    threshold: '$THRESHOLD'
  }' > "$STATE_FILE"

# Exit with success if no new warnings, failure if warnings exist (for monitoring)
if [[ ${#NEW_WARNINGS[@]} -gt 0 ]]; then
  exit 1
else
  exit 0
fi
