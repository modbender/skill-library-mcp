#!/usr/bin/env bash
# Wrapper for Cursor CLI headless (agent -p). Supports prompt from stdin/file,
# output format, and optional stream progress. Requires: agent (Cursor CLI).
# For --stream progress display, jq is required.

set -euo pipefail

PROMPT=""
PROMPT_FILE=""
DIR=""
OUTPUT_FORMAT="text"
MODEL=""
MODE=""
FORCE=true
STREAM=true

usage() {
  cat <<'EOF'
Usage: run-task.sh -p "prompt" | -f prompt-file [options]

Prompt (exactly one):
  -p "prompt"       Inline prompt
  -f prompt-file    Read prompt from file

Options:
  -d dir            Working directory (default: cwd)
  -o format         Output format: text, json, stream-json (default: stream-json when streaming)
  -m model          Model name
  --mode mode       Mode: agent, plan, ask
  --force           Allow file modifications (default)
  --no-force        Do not modify files; agent only proposes changes
  --stream          Use stream-json with progress display (default; requires jq)
  --no-stream       Plain output only (text or json per -o); no progress display

Examples:
  ./scripts/run-task.sh -f task.txt
  ./scripts/run-task.sh -p "Refactor utils.js" -d /path/to/project --no-stream -o json
  ./scripts/run-task.sh -f review.txt --no-stream -o text
EOF
  exit 1
}

# Check agent is available
if ! command -v agent &>/dev/null; then
  echo "Error: 'agent' (Cursor CLI) not found on PATH. Install: curl https://cursor.com/install -fsS | bash" >&2
  exit 1
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p)
      [[ -n "$PROMPT_FILE" ]] && { echo "Error: use -p or -f, not both" >&2; usage; }
      PROMPT="${2:?Error: -p requires a prompt string}"
      shift 2
      ;;
    -f)
      [[ -n "$PROMPT" ]] && { echo "Error: use -p or -f, not both" >&2; usage; }
      PROMPT_FILE="${2:?Error: -f requires a file path}"
      shift 2
      ;;
    -d)
      DIR="${2:?Error: -d requires a directory}"
      shift 2
      ;;
    -o)
      OUTPUT_FORMAT="${2:?Error: -o requires format (text|json|stream-json)}"
      shift 2
      ;;
    -m)
      MODEL="${2:?Error: -m requires model name}"
      shift 2
      ;;
    --mode)
      MODE="${2:?Error: --mode requires agent|plan|ask}"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --no-force)
      FORCE=false
      shift
      ;;
    --stream)
      STREAM=true
      shift
      ;;
    --no-stream)
      STREAM=false
      shift
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Error: unknown option $1" >&2
      usage
      ;;
  esac
done

# Require exactly one of -p or -f
if [[ -z "$PROMPT" && -z "$PROMPT_FILE" ]]; then
  echo "Error: provide -p \"prompt\" or -f prompt-file" >&2
  usage
fi
if [[ -n "$PROMPT" && -n "$PROMPT_FILE" ]]; then
  echo "Error: use -p or -f, not both" >&2
  usage
fi

# Resolve prompt
if [[ -n "$PROMPT_FILE" ]]; then
  if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: prompt file not found: $PROMPT_FILE" >&2
    exit 1
  fi
  PROMPT=$(cat "$PROMPT_FILE")
fi

# --stream implies stream-json and requires jq for progress
if [[ "$STREAM" == true ]]; then
  OUTPUT_FORMAT="stream-json"
  if ! command -v jq &>/dev/null; then
    echo "Warning: --stream progress display requires jq; output will be raw NDJSON" >&2
  fi
fi

# Build agent command (array for safe quoting)
CMD=(agent -p)
[[ "$FORCE" == true ]] && CMD+=(--force)
CMD+=(--output-format "$OUTPUT_FORMAT")
[[ -n "$MODEL" ]] && CMD+=(-m "$MODEL")
[[ -n "$MODE" ]] && CMD+=(--mode "$MODE")
[[ "$STREAM" == true ]] && CMD+=(--stream-partial-output)

# Run from directory if set
run_agent() {
  if [[ -n "$DIR" ]]; then
    if [[ ! -d "$DIR" ]]; then
      echo "Error: directory not found: $DIR" >&2
      exit 1
    fi
    cd "$DIR" && "${CMD[@]}" "$PROMPT"
  else
    "${CMD[@]}" "$PROMPT"
  fi
}

# Progress parser for stream-json + --stream (uses jq)
stream_progress() {
  local have_jq=false
  command -v jq &>/dev/null && have_jq=true

  if [[ "$have_jq" != true ]]; then
    cat
    return
  fi

  local accumulated_text="" tool_count=0 start_time
  start_time=$(date +%s)

  while IFS= read -r line; do
    echo "$line"
    type=$(echo "$line" | jq -r '.type // empty')
    subtype=$(echo "$line" | jq -r '.subtype // empty')

    case "$type" in
      system)
        if [[ "$subtype" == "init" ]]; then
          model=$(echo "$line" | jq -r '.model // "unknown"')
          echo "Using model: $model" >&2
        fi
        ;;
      assistant)
        content=$(echo "$line" | jq -r '.message.content[0].text // empty')
        accumulated_text="$accumulated_text$content"
        printf "\rGenerating: %d chars" ${#accumulated_text} >&2
        ;;
      tool_call)
        if [[ "$subtype" == "started" ]]; then
          tool_count=$((tool_count + 1))
          if echo "$line" | jq -e '.tool_call.writeToolCall' >/dev/null 2>&1; then
            path=$(echo "$line" | jq -r '.tool_call.writeToolCall.args.path // "unknown"')
            echo -e "\nTool #$tool_count: Writing $path" >&2
          elif echo "$line" | jq -e '.tool_call.readToolCall' >/dev/null 2>&1; then
            path=$(echo "$line" | jq -r '.tool_call.readToolCall.args.path // "unknown"')
            echo -e "\nTool #$tool_count: Reading $path" >&2
          fi
        elif [[ "$subtype" == "completed" ]]; then
          if echo "$line" | jq -e '.tool_call.writeToolCall.result.success' >/dev/null 2>&1; then
            lines=$(echo "$line" | jq -r '.tool_call.writeToolCall.result.success.linesCreated // 0')
            size=$(echo "$line" | jq -r '.tool_call.writeToolCall.result.success.fileSize // 0')
            echo "   Created $lines lines ($size bytes)" >&2
          elif echo "$line" | jq -e '.tool_call.readToolCall.result.success' >/dev/null 2>&1; then
            lines=$(echo "$line" | jq -r '.tool_call.readToolCall.result.success.totalLines // 0')
            echo "   Read $lines lines" >&2
          fi
        fi
        ;;
      result)
        duration=$(echo "$line" | jq -r '.duration_ms // 0')
        end_time=$(date +%s)
        total_time=$((end_time - start_time))
        echo -e "\nCompleted in ${duration}ms (${total_time}s total)" >&2
        echo "Tools: $tool_count, chars: ${#accumulated_text}" >&2
        ;;
    esac
  done
}

# Execute and exit with agent's status
if [[ "$OUTPUT_FORMAT" == "stream-json" && "$STREAM" == true ]]; then
  run_agent | stream_progress
  exit "${PIPESTATUS[0]}"
else
  run_agent
  exit $?
fi
