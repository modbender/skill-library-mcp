#!/bin/bash

# MiniMax Usage - Check coding plan credits remaining
# Usage: minimax-usage [--threshold <percent>]
#   --threshold: Only output when remaining % drops below this value
#                If omitted, always outputs (backward compat)

API_KEY="${MINIMAX_API_KEY}"
THRESHOLD=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# Validate threshold is a non-negative integer if provided
if [[ -n "$THRESHOLD" ]] && ! [[ "$THRESHOLD" =~ ^[0-9]+$ ]]; then
  echo "Error: --threshold must be a non-negative integer" >&2
  exit 1
fi

if [[ -z "$API_KEY" ]]; then
  echo "Error: MINIMAX_API_KEY environment variable not set" >&2
  exit 1
fi

response=$(curl -s --location 'https://www.minimax.io/v1/api/openplatform/coding_plan/remains' \
  --header "Authorization: Bearer $API_KEY" \
  --header 'Content-Type: application/json')

if [[ $? -ne 0 ]] || [[ -z "$response" ]]; then
  echo "Error: Failed to reach MiniMax API" >&2
  exit 1
fi

# Check for API-level error using JSON field
api_error=$(echo "$response" | jq -r '.error // empty')
if [[ -n "$api_error" ]]; then
  echo "API Error: $api_error" >&2
  exit 1
fi

# Extract fields from first model entry
model_count=$(echo "$response" | jq '.model_remains | length')
if [[ "$model_count" -eq 0 ]] || [[ "$model_count" == "null" ]]; then
  echo "Error: No model data in API response" >&2
  exit 1
fi

total=$(echo "$response" | jq '.model_remains[0].current_interval_total_count // 0')
remaining=$(echo "$response" | jq '.model_remains[0].current_interval_usage_count // 0')
model=$(echo "$response" | jq -r '.model_remains[0].model_name // "MiniMax"')
end_time=$(echo "$response" | jq '.model_remains[0].end_time // empty')
remains_time=$(echo "$response" | jq '.model_remains[0].remains_time // empty')

# Calculate remaining percentage
if [[ "$total" -gt 0 ]]; then
  # Use awk for floating point
  remaining_pct=$(awk "BEGIN { printf \"%.1f\", ($remaining / $total) * 100 }")
  remaining_pct_int=$(awk "BEGIN { printf \"%d\", ($remaining / $total) * 100 }")
else
  remaining_pct="0.0"
  remaining_pct_int=0
fi

# If threshold set and we're above it, exit silently
if [[ -n "$THRESHOLD" ]] && [[ "$remaining_pct_int" -ge "$THRESHOLD" ]]; then
  exit 0
fi

# Build output
if [[ -n "$THRESHOLD" ]] && [[ "$remaining_pct_int" -lt "$THRESHOLD" ]]; then
  echo "**⚠️ MiniMax Usage Alert — ${model}**"
else
  echo "**🤖 MiniMax Usage — ${model}**"
fi

remaining_fmt=$(printf "%'d" "$remaining")
total_fmt=$(printf "%'d" "$total")
echo "Remaining: **${remaining_fmt}** of ${total_fmt} requests (${remaining_pct}%)"

# Reset time (end_time is in milliseconds)
if [[ -n "$end_time" ]]; then
  end_secs=$((end_time / 1000))
  # Format in Eastern Time
  reset_str=$(TZ="America/New_York" date -r "$end_secs" "+%b %d, %Y %I:%M %p" 2>/dev/null \
    || TZ="America/New_York" date -d "@$end_secs" "+%b %d, %Y %I:%M %p" 2>/dev/null)
  if [[ -n "$reset_str" ]]; then
    echo "Resets: ${reset_str} ET"
  fi
fi

# Time remaining (remains_time is in milliseconds)
if [[ -n "$remains_time" ]]; then
  secs=$((remains_time / 1000))
  h=$((secs / 3600))
  m=$(( (secs % 3600) / 60 ))
  s=$((secs % 60))
  printf "Time left: %d:%02d:%02d\n" "$h" "$m" "$s"
fi
