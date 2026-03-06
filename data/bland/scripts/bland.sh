#!/usr/bin/env bash
# Bland AI Voice Calling CLI
# Usage: bland <command> [options]

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ── Config ──────────────────────────────────────────────────────────────────
API_BASE="https://api.bland.ai/v1"
DEFAULT_VOICE="josh"
DEFAULT_MODEL="base"

# Load API key from environment or .env file
if [[ -z "${BLAND_API_KEY:-}" ]]; then
  ENV_FILE="${BASH_SOURCE[0]%/*}/../../../.env"
  if [[ -f "$ENV_FILE" ]]; then
    BLAND_API_KEY=$(grep '^BLAND_API_KEY=' "$ENV_FILE" | cut -d= -f2-)
  fi
  # Also try /root/clawd/.env directly
  if [[ -z "${BLAND_API_KEY:-}" ]] && [[ -f /root/clawd/.env ]]; then
    BLAND_API_KEY=$(grep '^BLAND_API_KEY=' /root/clawd/.env | cut -d= -f2-)
  fi
fi

if [[ -z "${BLAND_API_KEY:-}" ]]; then
  echo -e "${RED}Error: BLAND_API_KEY not set. Add it to /root/clawd/.env${NC}" >&2
  exit 1
fi

# ── Helpers ─────────────────────────────────────────────────────────────────

err() { echo -e "${RED}Error: $*${NC}" >&2; exit 1; }
ok()  { echo -e "${GREEN}✓${NC} $*"; }
info() { echo -e "${CYAN}$*${NC}"; }
dim()  { echo -e "${DIM}$*${NC}"; }

api_get() {
  local endpoint="$1"
  curl -sS -f "${API_BASE}${endpoint}" \
    -H "authorization: ${BLAND_API_KEY}" \
    -H "Content-Type: application/json" 2>/dev/null || {
    err "API request failed: GET ${endpoint}"
  }
}

api_post() {
  local endpoint="$1"
  local data="${2:-{\}}"
  curl -sS -f "${API_BASE}${endpoint}" \
    -X POST \
    -H "authorization: ${BLAND_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$data" 2>/dev/null || {
    err "API request failed: POST ${endpoint}"
  }
}

usage() {
  cat <<EOF
${BOLD}Bland AI Voice Calling CLI${NC}

${BOLD}Usage:${NC} bland <command> [options]

${BOLD}Commands:${NC}
  call <phone>              Place an outbound AI call
  call-status <call_id>     Get call details/status
  calls [--limit N]         List recent calls
  stop <call_id>            Stop an active call
  stop-all                  Stop all active calls
  recording <call_id>       Get call recording URL
  transcript <call_id>      Get call transcript
  voices                    List available voices
  numbers                   List owned inbound numbers
  buy-number                Purchase an inbound number
  setup-inbound <phone>     Configure inbound call agent
  balance                   Check account balance
  analyze <call_id>         Analyze a call with AI

${BOLD}Call Options:${NC}
  --task "prompt"           Instructions for the AI agent
  --voice "josh"            Voice name (default: josh)
  --first-sentence "Hi"     Opening sentence
  --from "+1234567890"      Outbound caller ID
  --wait-for-greeting       Wait for other party to speak first
  --wait                    Poll until call completes
  --model "base"            Model to use (default: base)

${BOLD}Examples:${NC}
  bland call +14155551234 --task "Ask about their hours"
  bland call +14155551234 --task "Make a reservation" --wait
  bland transcript abc-123-def
  bland analyze abc-123 --goal "Did they confirm?"
EOF
}

# ── Commands ────────────────────────────────────────────────────────────────

cmd_call() {
  local phone="" task="" voice="$DEFAULT_VOICE" model="$DEFAULT_MODEL"
  local first_sentence="" from_number="" wait_for_greeting="false" wait_mode="false"

  # First positional arg is phone number
  if [[ $# -gt 0 && "$1" != --* ]]; then
    phone="$1"; shift
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --task)            task="$2"; shift 2 ;;
      --voice)           voice="$2"; shift 2 ;;
      --first-sentence)  first_sentence="$2"; shift 2 ;;
      --from)            from_number="$2"; shift 2 ;;
      --wait-for-greeting) wait_for_greeting="true"; shift ;;
      --wait)            wait_mode="true"; shift ;;
      --model)           model="$2"; shift 2 ;;
      *)                 err "Unknown option: $1" ;;
    esac
  done

  [[ -z "$phone" ]] && err "Phone number required. Usage: bland call <phone> --task \"prompt\""

  # Build JSON body
  local body
  body=$(jq -n \
    --arg phone "$phone" \
    --arg task "$task" \
    --arg voice "$voice" \
    --arg model "$model" \
    --arg first_sentence "$first_sentence" \
    --arg from "$from_number" \
    --argjson wait_for_greeting "$wait_for_greeting" \
    '{
      phone_number: $phone,
      voice: $voice,
      model: $model,
      wait_for_greeting: $wait_for_greeting
    }
    + (if $task != "" then {task: $task} else {} end)
    + (if $first_sentence != "" then {first_sentence: $first_sentence} else {} end)
    + (if $from != "" then {from: $from} else {} end)
    ')

  info "Calling ${phone}..."
  local response
  response=$(api_post "/calls" "$body")

  local call_id status
  call_id=$(echo "$response" | jq -r '.call_id // .id // "unknown"')
  status=$(echo "$response" | jq -r '.status // "initiated"')

  if [[ "$call_id" == "null" || "$call_id" == "unknown" ]]; then
    echo -e "${RED}Call failed:${NC}"
    echo "$response" | jq .
    exit 1
  fi

  ok "Call initiated"
  echo -e "  ${BOLD}Call ID:${NC}  $call_id"
  echo -e "  ${BOLD}Status:${NC}  $status"
  echo -e "  ${BOLD}Phone:${NC}   $phone"
  echo -e "  ${BOLD}Voice:${NC}   $voice"

  if [[ "$wait_mode" == "true" ]]; then
    echo ""
    info "Waiting for call to complete..."
    _poll_call "$call_id"
  fi
}

_poll_call() {
  local call_id="$1"
  local max_attempts=120  # 10 minutes max (5s intervals)
  local attempt=0

  while [[ $attempt -lt $max_attempts ]]; do
    sleep 5
    attempt=$((attempt + 1))

    local response
    response=$(api_get "/calls/${call_id}" 2>/dev/null) || continue

    local status
    status=$(echo "$response" | jq -r '.status // "unknown"')

    case "$status" in
      completed|ended|failed|error|no-answer|voicemail)
        echo ""
        ok "Call ${status}"
        _format_call_details "$response"
        return 0
        ;;
      *)
        printf "\r  ${DIM}Status: %-15s (${attempt}/${max_attempts})${NC}" "$status"
        ;;
    esac
  done

  echo ""
  echo -e "${YELLOW}Timed out waiting for call to complete. Check with: bland call-status ${call_id}${NC}"
}

cmd_call_status() {
  local call_id="${1:-}"
  [[ -z "$call_id" ]] && err "Call ID required. Usage: bland call-status <call_id>"

  local response
  response=$(api_get "/calls/${call_id}")
  _format_call_details "$response"
}

_format_call_details() {
  local data="$1"

  local status duration price phone_number created_at
  status=$(echo "$data" | jq -r '.status // "unknown"')
  duration=$(echo "$data" | jq -r '.call_length // .duration // "n/a"')
  price=$(echo "$data" | jq -r '.price // .cost // "n/a"')
  phone_number=$(echo "$data" | jq -r '.to // .phone_number // "n/a"')
  created_at=$(echo "$data" | jq -r '.created_at // "n/a"')

  local status_color="$CYAN"
  case "$status" in
    completed|ended) status_color="$GREEN" ;;
    failed|error)    status_color="$RED" ;;
    active|ringing)  status_color="$YELLOW" ;;
  esac

  echo -e "${BOLD}Call Details${NC}"
  echo -e "  ${BOLD}Status:${NC}    ${status_color}${status}${NC}"
  echo -e "  ${BOLD}Phone:${NC}     ${phone_number}"
  echo -e "  ${BOLD}Duration:${NC}  ${duration}"
  echo -e "  ${BOLD}Cost:${NC}      ${price}"
  echo -e "  ${BOLD}Created:${NC}   ${created_at}"

  # Show transcript if available
  local has_transcript
  has_transcript=$(echo "$data" | jq 'has("concatenated_transcript") or has("transcripts")')
  if [[ "$has_transcript" == "true" ]]; then
    echo ""
    echo -e "${BOLD}Transcript:${NC}"
    # Try concatenated_transcript first
    local concat
    concat=$(echo "$data" | jq -r '.concatenated_transcript // empty')
    if [[ -n "$concat" && "$concat" != "null" ]]; then
      echo "$concat" | sed 's/^/  /'
    else
      # Fall back to transcripts array
      echo "$data" | jq -r '.transcripts[]? | "  \(.user // .role // "?"): \(.text // .content // "")"' 2>/dev/null || true
    fi
  fi
}

cmd_calls() {
  local limit=10
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      *)       err "Unknown option: $1" ;;
    esac
  done

  local response
  response=$(api_get "/calls")

  echo -e "${BOLD}Recent Calls${NC}"
  echo ""

  echo "$response" | jq -r --argjson limit "$limit" '
    (.calls // .)[:$limit][] |
    "\(.call_id // .id)  \(.status // "?")  \(.to // .phone_number // "?")  \(.created_at // "?")"
  ' 2>/dev/null | while IFS= read -r line; do
    if echo "$line" | grep -qi "completed\|ended"; then
      echo -e "  ${GREEN}${line}${NC}"
    elif echo "$line" | grep -qi "failed\|error"; then
      echo -e "  ${RED}${line}${NC}"
    elif echo "$line" | grep -qi "active\|ringing"; then
      echo -e "  ${YELLOW}${line}${NC}"
    else
      echo "  ${line}"
    fi
  done
}

cmd_stop() {
  local call_id="${1:-}"
  [[ -z "$call_id" ]] && err "Call ID required. Usage: bland stop <call_id>"

  local response
  response=$(api_post "/calls/${call_id}/stop")
  ok "Call ${call_id} stopped"
  echo "$response" | jq -r '.status // .message // empty' 2>/dev/null || true
}

cmd_stop_all() {
  local response
  response=$(api_post "/calls/active/stop")
  ok "All active calls stopped"
  echo "$response" | jq . 2>/dev/null || true
}

cmd_recording() {
  local call_id="${1:-}"
  [[ -z "$call_id" ]] && err "Call ID required. Usage: bland recording <call_id>"

  local response
  response=$(api_get "/calls/${call_id}/recording")

  local url
  url=$(echo "$response" | jq -r '.url // .recording_url // empty')
  if [[ -n "$url" && "$url" != "null" ]]; then
    ok "Recording URL:"
    echo "  $url"
  else
    echo "$response" | jq .
  fi
}

cmd_transcript() {
  local call_id="${1:-}"
  [[ -z "$call_id" ]] && err "Call ID required. Usage: bland transcript <call_id>"

  # Try corrected transcript first
  local corrected
  corrected=$(api_get "/calls/${call_id}/correct" 2>/dev/null) || true

  if [[ -n "$corrected" ]] && echo "$corrected" | jq -e '.corrected_transcript // .aligned // empty' &>/dev/null; then
    echo -e "${BOLD}Corrected Transcript:${NC}"
    echo "$corrected" | jq -r '
      (.corrected_transcript // .aligned // [])[] |
      "  \(.user // .role // "?"): \(.text // .content // "")"
    ' 2>/dev/null
    return
  fi

  # Fall back to call details transcript
  local response
  response=$(api_get "/calls/${call_id}")

  echo -e "${BOLD}Transcript:${NC}"

  local concat
  concat=$(echo "$response" | jq -r '.concatenated_transcript // empty')
  if [[ -n "$concat" && "$concat" != "null" ]]; then
    echo "$concat" | sed 's/^/  /'
  else
    echo "$response" | jq -r '.transcripts[]? | "  \(.user // .role // "?"): \(.text // .content // "")"' 2>/dev/null || {
      echo -e "  ${DIM}No transcript available yet${NC}"
    }
  fi
}

cmd_voices() {
  local response
  response=$(api_get "/voices")

  echo -e "${BOLD}Available Voices${NC}"
  echo ""

  echo "$response" | jq -r '
    (if type == "array" then . else (.voices // []) end)[] |
    "  \(.name // .id // "?")  \(.description // "")"
  ' 2>/dev/null || {
    # Fallback: just print the raw response nicely
    echo "$response" | jq .
  }
}

cmd_numbers() {
  local response
  response=$(api_get "/inbound")

  echo -e "${BOLD}Owned Numbers${NC}"
  echo ""

  echo "$response" | jq -r '
    (if type == "array" then . else (.inbound_numbers // .numbers // []) end)[] |
    "  \(.phone_number // .number // "?")  \(.name // .label // "")"
  ' 2>/dev/null || {
    echo "$response" | jq .
  }
}

cmd_buy_number() {
  local area_code=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --area-code) area_code="$2"; shift 2 ;;
      *)           err "Unknown option: $1" ;;
    esac
  done

  local body="{}"
  if [[ -n "$area_code" ]]; then
    body=$(jq -n --arg ac "$area_code" '{area_code: $ac}')
  fi

  local response
  response=$(api_post "/inbound/purchase" "$body")

  local number
  number=$(echo "$response" | jq -r '.phone_number // .number // empty')
  if [[ -n "$number" && "$number" != "null" ]]; then
    ok "Purchased number: ${BOLD}${number}${NC}"
  else
    echo "$response" | jq .
  fi
}

cmd_setup_inbound() {
  local phone="" task="" voice="$DEFAULT_VOICE"

  if [[ $# -gt 0 && "$1" != --* ]]; then
    phone="$1"; shift
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --task)  task="$2"; shift 2 ;;
      --voice) voice="$2"; shift 2 ;;
      *)       err "Unknown option: $1" ;;
    esac
  done

  [[ -z "$phone" ]] && err "Phone number required. Usage: bland setup-inbound <phone> --task \"prompt\""
  [[ -z "$task" ]] && err "--task is required for inbound setup"

  local body
  body=$(jq -n \
    --arg task "$task" \
    --arg voice "$voice" \
    '{prompt: $task, voice: $voice}')

  # URL-encode the phone number (handle the +)
  local encoded_phone
  encoded_phone=$(echo "$phone" | sed 's/+/%2B/g')

  local response
  response=$(api_post "/inbound/${encoded_phone}/update" "$body")

  ok "Inbound agent configured for ${phone}"
  echo -e "  ${BOLD}Voice:${NC}  $voice"
  echo -e "  ${BOLD}Task:${NC}   $task"
}

cmd_balance() {
  local response
  response=$(api_get "/me")

  echo -e "${BOLD}Account Balance${NC}"

  local balance
  balance=$(echo "$response" | jq -r '.billing.current_balance // .current_balance // .balance // .credits // empty')
  if [[ -n "$balance" && "$balance" != "null" ]]; then
    echo -e "  ${GREEN}\$${balance}${NC}"
  else
    echo "$response" | jq .
  fi

  local total_calls
  total_calls=$(echo "$response" | jq -r '.total_calls // empty')
  if [[ -n "$total_calls" && "$total_calls" != "null" ]]; then
    echo -e "  ${DIM}Total calls: ${total_calls}${NC}"
  fi
}

cmd_analyze() {
  local call_id="" goal="" questions='[]'

  if [[ $# -gt 0 && "$1" != --* ]]; then
    call_id="$1"; shift
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --goal)      goal="$2"; shift 2 ;;
      --questions) questions="$2"; shift 2 ;;
      *)           err "Unknown option: $1" ;;
    esac
  done

  [[ -z "$call_id" ]] && err "Call ID required. Usage: bland analyze <call_id> --goal \"question\""
  [[ -z "$goal" ]] && err "--goal is required for analysis"

  local body
  body=$(jq -n \
    --arg goal "$goal" \
    --argjson questions "$questions" \
    '{goal: $goal, questions: $questions}')

  local response
  response=$(api_post "/calls/${call_id}/analyze" "$body")

  echo -e "${BOLD}Call Analysis${NC}"
  echo ""
  echo "$response" | jq -r '
    if type == "object" then
      to_entries[] | "  \(.key): \(.value)"
    else
      .
    end
  ' 2>/dev/null || echo "$response" | jq .
}

# ── Main ────────────────────────────────────────────────────────────────────

command="${1:-}"
shift || true

case "$command" in
  call)           cmd_call "$@" ;;
  call-status)    cmd_call_status "$@" ;;
  calls)          cmd_calls "$@" ;;
  stop)           cmd_stop "$@" ;;
  stop-all)       cmd_stop_all ;;
  recording)      cmd_recording "$@" ;;
  transcript)     cmd_transcript "$@" ;;
  voices)         cmd_voices "$@" ;;
  numbers)        cmd_numbers "$@" ;;
  buy-number)     cmd_buy_number "$@" ;;
  setup-inbound)  cmd_setup_inbound "$@" ;;
  balance)        cmd_balance "$@" ;;
  analyze)        cmd_analyze "$@" ;;
  help|--help|-h) usage ;;
  "")             usage ;;
  *)              err "Unknown command: $command. Run 'bland help' for usage." ;;
esac
