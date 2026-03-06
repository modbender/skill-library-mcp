#!/usr/bin/env bash
# AgentBench metrics library — shared functions for metrics read/write
#
# Provides path helpers, event logging, and summary computation.
# Sourced by hooks/metrics-collector.sh and the orchestrator command.

# Determine the metrics directory for the current run
# Uses AGENTBENCH_RUN_ID env var if set, otherwise "unknown"
agentbench_metrics_dir() {
  local run_id="${AGENTBENCH_RUN_ID:-unknown}"
  echo "/tmp/agentbench-${run_id}"
}

# Return the path to the JSONL event log
agentbench_metrics_file() {
  echo "$(agentbench_metrics_dir)/events.jsonl"
}

# Return the path to the computed summary JSON
agentbench_summary_file() {
  echo "$(agentbench_metrics_dir)/summary.json"
}

# Append a metrics event (JSON line) to the JSONL log
# Creates the metrics directory if it does not exist.
# Usage: append_event '{"event":"PostToolUse","tool":"Bash","ts":1234567890}'
append_event() {
  local json_line="$1"
  local metrics_file
  metrics_file="$(agentbench_metrics_file)"
  mkdir -p "$(dirname "$metrics_file")"
  echo "$json_line" >> "$metrics_file"
}

# Read all events from the JSONL log (stdout)
# Outputs nothing if the file does not exist.
# Usage: read_events | jq ...
read_events() {
  local metrics_file
  metrics_file="$(agentbench_metrics_file)"
  if [[ -f "$metrics_file" ]]; then
    cat "$metrics_file"
  fi
}

# Compute aggregate summary from the JSONL event log
# Writes summary.json alongside the events file.
# Requires jq; falls back to a minimal error summary if jq is missing.
compute_summary() {
  local metrics_file summary_file
  metrics_file="$(agentbench_metrics_file)"
  summary_file="$(agentbench_summary_file)"

  # Guard: no metrics file
  if [[ ! -f "$metrics_file" ]]; then
    echo '{"error":"no metrics file found"}' > "$summary_file"
    return 1
  fi

  # Guard: empty metrics file
  if [[ ! -s "$metrics_file" ]]; then
    echo '{"error":"metrics file is empty"}' > "$summary_file"
    return 1
  fi

  # Guard: jq not available
  if ! command -v jq &>/dev/null; then
    echo '{"error":"jq is not installed — cannot compute summary"}' > "$summary_file"
    return 1
  fi

  # Use jq to compute all aggregates in a single slurp pass
  jq -s '
    # Extract key events by type
    (map(select(.event == "UserPromptSubmit")) | first // null) as $start |
    (map(select(.event == "Stop"))             | last  // null) as $stop  |
    (map(select(.event == "PreToolUse"))       | first // null) as $first_tool |

    # Timing calculations (milliseconds)
    (if $start and $stop
     then (($stop.ts // 0) - ($start.ts // 0))
     else null end) as $total_ms |

    (if $start and $first_tool
     then (($first_tool.ts // 0) - ($start.ts // 0))
     else null end) as $planning_ms |

    (if $first_tool and $stop
     then (($stop.ts // 0) - ($first_tool.ts // 0))
     else null end) as $execution_ms |

    # Planning ratio (rounded to 3 decimal places)
    (if $planning_ms and $total_ms and $total_ms > 0
     then (($planning_ms / $total_ms) * 1000 | round / 1000)
     else null end) as $planning_ratio |

    # Tool call counts
    [.[] | select(.event == "PostToolUse")] as $tool_calls |
    ($tool_calls | length) as $tool_count |
    ($tool_calls
     | group_by(.tool)
     | map({(.[0].tool // "unknown"): length})
     | add // {}) as $by_type |

    # Error count
    ([.[] | select(.event == "PostToolUseFailure")] | length) as $errors |

    # Subagent count
    ([.[] | select(.event == "SubagentStart")] | length) as $subagents |

    # Compaction count
    ([.[] | select(.event == "PreCompact")] | length) as $compactions |

    {
      total_time_ms:      $total_ms,
      planning_time_ms:   $planning_ms,
      execution_time_ms:  $execution_ms,
      planning_ratio:     $planning_ratio,
      tool_calls_total:   $tool_count,
      tool_calls_by_type: $by_type,
      errors:             $errors,
      subagents_spawned:  $subagents,
      compactions:        $compactions
    }
  ' "$metrics_file" > "$summary_file"
}
