#!/usr/bin/env bash
# extract-items.sh — Multi-pass LLM extraction from parsed transcript
# Usage: bash extract-items.sh <parsed_jsonl_file> [meeting_title]
# Input:  JSONL file from parse-transcript.sh
# Output: JSON to stdout with extracted + classified items
#
# Pass 1: Extract raw items with speaker attribution
# Pass 2: Classify each item (decision, action_item, open_question, parking_lot, key_point)
#
# Requires: ANTHROPIC_API_KEY or OPENAI_API_KEY env var

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_jq

PARSED_FILE="${1:--}"
MEETING_TITLE="${2:-Untitled Meeting}"

# Read parsed segments
if [ "$PARSED_FILE" = "-" ]; then
  SEGMENTS="$(cat)"
else
  [ -f "$PARSED_FILE" ] || die "Parsed JSONL file not found: $PARSED_FILE"
  SEGMENTS="$(cat "$PARSED_FILE")"
fi

[ -z "$SEGMENTS" ] && die "No parsed segments to extract from." \
  "Run parse-transcript.sh first to generate JSONL segments."

SEGMENT_COUNT=$(echo "$SEGMENTS" | wc -l | tr -d ' ')
log_info "Processing $SEGMENT_COUNT transcript segments"

# ── Build consolidated transcript for LLM ─────────────────
# Convert JSONL into a readable transcript block
TRANSCRIPT_TEXT=$(echo "$SEGMENTS" | python3 -c '
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        seg = json.loads(line)
        ts = seg.get("timestamp", "")
        spk = seg.get("speaker", "")
        txt = seg.get("text", "")
        prefix = ""
        if ts:
            prefix += f"[{ts}] "
        if spk:
            prefix += f"{spk}: "
        print(f"{prefix}{txt}")
    except json.JSONDecodeError:
        continue
')

# ── Determine API to use ──────────────────────────────────
EXTRACTION_PROMPT_FILE="$SCRIPT_DIR/../templates/extraction-prompt.md"
CLASSIFICATION_PROMPT_FILE="$SCRIPT_DIR/../templates/classification-prompt.md"

[ -f "$EXTRACTION_PROMPT_FILE" ] || die "Template not found: extraction-prompt.md"
[ -f "$CLASSIFICATION_PROMPT_FILE" ] || die "Template not found: classification-prompt.md"

EXTRACTION_PROMPT="$(cat "$EXTRACTION_PROMPT_FILE")"
CLASSIFICATION_PROMPT="$(cat "$CLASSIFICATION_PROMPT_FILE")"

# ── LLM Call Helper ───────────────────────────────────────
# Calls the LLM via Anthropic or OpenAI API
# Arguments: $1 = system prompt, stdin = user message
# Output: LLM response text to stdout
call_llm() {
  local system_prompt="$1"
  local user_message
  user_message="$(cat)"

  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    # Anthropic Claude API
    local anthropic_base
    anthropic_base="${ANTHROPIC_API_URL:-https://api.anthropic.com}"
    validate_http_url "$anthropic_base" "ANTHROPIC_API_URL"

    local request_body
    request_body=$(jq -n \
      --arg model "${ANTHROPIC_MODEL:-claude-sonnet-4-20250514}" \
      --arg system "$system_prompt" \
      --arg user "$user_message" \
      '{
        model: $model,
        max_tokens: 8192,
        system: $system,
        messages: [{role: "user", content: $user}]
      }')

    local response
    response=$(printf '%s' "$request_body" | curl -sS \
      "${anthropic_base%/}/v1/messages" \
      -H "Content-Type: application/json" \
      -H "x-api-key: ${ANTHROPIC_API_KEY}" \
      -H "anthropic-version: 2023-06-01" \
      -d @- 2>/dev/null)

    # Extract text content
    printf '%s' "$response" | jq -r '.content[0].text // empty' 2>/dev/null
    return

  elif [ -n "${OPENAI_API_KEY:-}" ]; then
    # OpenAI API
    local openai_base
    openai_base="${OPENAI_API_URL:-https://api.openai.com}"
    validate_http_url "$openai_base" "OPENAI_API_URL"

    local request_body
    request_body=$(jq -n \
      --arg model "${OPENAI_MODEL:-gpt-4o}" \
      --arg system "$system_prompt" \
      --arg user "$user_message" \
      '{
        model: $model,
        max_tokens: 8192,
        messages: [
          {role: "system", content: $system},
          {role: "user", content: $user}
        ]
      }')

    local response
    response=$(printf '%s' "$request_body" | curl -sS \
      "${openai_base%/}/v1/chat/completions" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer ${OPENAI_API_KEY}" \
      -d @- 2>/dev/null)

    printf '%s' "$response" | jq -r '.choices[0].message.content // empty' 2>/dev/null
    return
  fi

  die "No LLM API key found." \
    "Set ANTHROPIC_API_KEY or OPENAI_API_KEY. Meeting Autopilot uses an LLM to extract items from your transcript."
}

# ── Extract JSON from LLM response ───────────────────────
# LLM might wrap JSON in ```json ... ``` blocks
extract_json() {
  python3 -c '
import sys, re, json

text = sys.stdin.read().strip()

# Try to find JSON in code blocks first
code_block = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
if code_block:
    text = code_block.group(1).strip()

# Try to find JSON array or object
json_match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
if json_match:
    candidate = json_match.group(1)
    try:
        parsed = json.loads(candidate)
        print(json.dumps(parsed, ensure_ascii=False))
        sys.exit(0)
    except json.JSONDecodeError:
        pass

# Last resort: try the whole thing
try:
    parsed = json.loads(text)
    print(json.dumps(parsed, ensure_ascii=False))
except json.JSONDecodeError:
    print("[]", file=sys.stderr)
    sys.exit(1)
'
}

# ── PASS 1 + 2: Extract and classify items ───────────────
log_step "Pass 1+2: Extracting and classifying items from transcript..."

# Combine extraction and classification into a single pass for efficiency
# (the prompts are designed to handle both)
COMBINED_PROMPT="$EXTRACTION_PROMPT

---

$CLASSIFICATION_PROMPT"

EXTRACTION_RESULT=$(printf '%s' "Meeting Title: $MEETING_TITLE

TRANSCRIPT:
$TRANSCRIPT_TEXT" | call_llm "$COMBINED_PROMPT")

if [ -z "$EXTRACTION_RESULT" ]; then
  die "LLM returned empty response during extraction." \
    "Check your API key and network connection. The transcript may also be too long for the context window."
fi

# Parse the JSON from LLM response
ITEMS_JSON=$(printf '%s' "$EXTRACTION_RESULT" | extract_json)

if [ -z "$ITEMS_JSON" ] || [ "$ITEMS_JSON" = "[]" ]; then
  log_warn "No items extracted from transcript. The meeting may not have had actionable content."
  ITEMS_JSON="[]"
fi

# ── Build output JSON ────────────────────────────────────
EXTRACT_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

jq -n \
  --arg title "$MEETING_TITLE" \
  --arg extract_time "$EXTRACT_TIME" \
  --argjson segment_count "$SEGMENT_COUNT" \
  --argjson items "$ITEMS_JSON" \
  '{
    meeting_title: $title,
    extract_time: $extract_time,
    segment_count: $segment_count,
    items: $items,
    summary: {
      total: ($items | length),
      decisions: ([$items[] | select(.type == "decision")] | length),
      action_items: ([$items[] | select(.type == "action_item")] | length),
      open_questions: ([$items[] | select(.type == "open_question")] | length),
      parking_lot: ([$items[] | select(.type == "parking_lot")] | length),
      key_points: ([$items[] | select(.type == "key_point")] | length)
    }
  }'

log_ok "Extracted $(echo "$ITEMS_JSON" | jq 'length') items from transcript"
