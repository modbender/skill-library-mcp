#!/usr/bin/env bash
# meeting-autopilot.sh — Main orchestrator for Meeting Autopilot
# Usage:
#   bash meeting-autopilot.sh <transcript_file> [--title "Weekly Standup"]
#   cat transcript.vtt | bash meeting-autopilot.sh - --title "Q4 Planning"
#   bash meeting-autopilot.sh --help
#
# Orchestrates: parse → extract → generate → save history

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# ── Parse arguments ───────────────────────────────────────
INPUT=""
MEETING_TITLE=""
FORMAT="auto"
OUTPUT_DIR=""
SKIP_HISTORY=false

show_help() {
  cat << EOF

  ✈️  ${BOLD}Meeting Autopilot${RESET} v${VERSION}
  Turn meeting transcripts into operational outputs.

  ${BOLD}USAGE${RESET}
    meeting-autopilot <transcript_file> [options]
    cat transcript.vtt | meeting-autopilot - [options]

  ${BOLD}OPTIONS${RESET}
    --title, -t     Meeting title (default: derived from filename)
    --format, -f    Force format: vtt, srt, txt (default: auto-detect)
    --output, -o    Output directory for report files
    --no-history    Don't save to cross-meeting history
    --help, -h      Show this help

  ${BOLD}SUPPORTED FORMATS${RESET}
    VTT   WebVTT (from Zoom, Google Meet, Microsoft Teams)
    SRT   SubRip (from Otter.ai, video editors)
    TXT   Plain text (speaker labels optional)

  ${BOLD}EXAMPLES${RESET}
    meeting-autopilot meeting.vtt --title "Sprint Planning"
    meeting-autopilot transcript.txt -t "Board Meeting" -o ./reports
    pbpaste | meeting-autopilot - -t "Quick Sync"

  ${BOLD}REQUIREMENTS${RESET}
    • bash, jq, python3, curl
    • ANTHROPIC_API_KEY or OPENAI_API_KEY

  $BRAND_FOOTER

EOF
  exit 0
}

while [ $# -gt 0 ]; do
  case "$1" in
    --help|-h)
      show_help
      ;;
    --title|-t)
      MEETING_TITLE="$2"
      shift 2
      ;;
    --format|-f)
      FORMAT="$2"
      shift 2
      ;;
    --output|-o)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --no-history)
      SKIP_HISTORY=true
      shift
      ;;
    -*)
      die "Unknown option: $1" "Run meeting-autopilot --help for usage."
      ;;
    *)
      if [ -z "$INPUT" ]; then
        INPUT="$1"
      else
        die "Unexpected argument: $1" "Only one input file is supported."
      fi
      shift
      ;;
  esac
done

# Default input is stdin
INPUT="${INPUT:--}"

# ── Validate prerequisites ────────────────────────────────
require_jq
require_cmd python3 "Install Python 3: apt install python3 / brew install python3"
require_cmd curl "Install curl: apt install curl / brew install curl"

if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${OPENAI_API_KEY:-}" ]; then
  die "No LLM API key found." \
    "Set ANTHROPIC_API_KEY or OPENAI_API_KEY. Meeting Autopilot needs an LLM to extract items from your transcript."
fi

# ── Create workspace ──────────────────────────────────────
WORKDIR="$(make_workdir)"
trap 'rm -rf "$WORKDIR"' EXIT

# ── Read input ────────────────────────────────────────────
if [ "$INPUT" = "-" ]; then
  log_info "Reading transcript from stdin..."
  TRANSCRIPT_CONTENT="$(cat)"
  if [ -z "$MEETING_TITLE" ]; then
    MEETING_TITLE="Meeting $(date '+%Y-%m-%d %H:%M')"
  fi
else
  [ -f "$INPUT" ] || die "File not found: $INPUT" "Check the path and try again."
  log_info "Reading transcript from: $INPUT"
  TRANSCRIPT_CONTENT="$(cat "$INPUT")"
  if [ -z "$MEETING_TITLE" ]; then
    # Derive title from filename
    MEETING_TITLE="$(basename "$INPUT" | sed 's/\.[^.]*$//' | tr '_-' '  ')"
  fi
fi

validate_transcript "$TRANSCRIPT_CONTENT"

# ── Detect format ─────────────────────────────────────────
if [ "$FORMAT" = "auto" ]; then
  FORMAT="$(detect_format "$TRANSCRIPT_CONTENT")"
fi
log_info "Format: $FORMAT | Title: $MEETING_TITLE"

WORD_COUNT=$(word_count "$TRANSCRIPT_CONTENT")
log_info "Transcript: $WORD_COUNT words"

# ── Step 1: Parse transcript ──────────────────────────────
echo "" >&2
log_step "Step 1/3: Parsing transcript ($FORMAT)..."

printf '%s' "$TRANSCRIPT_CONTENT" > "$WORKDIR/raw_transcript.txt"
bash "$SCRIPT_DIR/parse-transcript.sh" "$WORKDIR/raw_transcript.txt" "$FORMAT" \
  > "$WORKDIR/parsed.jsonl"

SEGMENT_COUNT=$(wc -l < "$WORKDIR/parsed.jsonl" | tr -d ' ')
log_ok "Parsed $SEGMENT_COUNT segments"

if [ "$SEGMENT_COUNT" -eq 0 ]; then
  die "No segments parsed from transcript." \
    "The transcript may be in an unsupported format. Try --format txt to force plain text parsing."
fi

# ── Step 2: Extract and classify items ────────────────────
log_step "Step 2/3: Extracting items via LLM (this may take 10-30s)..."

bash "$SCRIPT_DIR/extract-items.sh" "$WORKDIR/parsed.jsonl" "$MEETING_TITLE" \
  > "$WORKDIR/extracted.json"

ITEM_COUNT=$(jq '.summary.total' "$WORKDIR/extracted.json")
log_ok "Extracted $ITEM_COUNT items"

# Show breakdown
jq -r '"  ✅ " + (.summary.decisions | tostring) + " decisions, 📋 " + (.summary.action_items | tostring) + " action items, ❓ " + (.summary.open_questions | tostring) + " questions"' \
  "$WORKDIR/extracted.json" >&2

# ── Step 3: Generate operational outputs ──────────────────
log_step "Step 3/3: Generating operational outputs (emails, tickets)..."

bash "$SCRIPT_DIR/generate-outputs.sh" "$WORKDIR/extracted.json" "$MEETING_TITLE" \
  > "$WORKDIR/report.md"

log_ok "Report generated"

# ── Save to history ───────────────────────────────────────
if [ "$SKIP_HISTORY" != true ]; then
  ensure_history_dir
  HISTORY_SLUG="$(timestamp_slug)_$(echo "$MEETING_TITLE" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g' | head -c 50)"
  HISTORY_FILE="$HISTORY_DIR/${HISTORY_SLUG}.json"

  # Build history entry with safe JSON construction
  jq -n \
    --arg title "$MEETING_TITLE" \
    --arg date "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg format "$FORMAT" \
    --argjson word_count "$WORD_COUNT" \
    --argjson segment_count "$SEGMENT_COUNT" \
    --slurpfile extracted "$WORKDIR/extracted.json" \
    '{
      meeting_title: $title,
      date: $date,
      format: $format,
      word_count: $word_count,
      segment_count: $segment_count,
      items: $extracted[0].items,
      summary: $extracted[0].summary
    }' > "$HISTORY_FILE"

  log_ok "Saved to history: $HISTORY_FILE"
fi

# ── Save report if output dir specified ───────────────────
if [ -n "$OUTPUT_DIR" ]; then
  mkdir -p "$OUTPUT_DIR"
  REPORT_FILE="$OUTPUT_DIR/$(echo "$MEETING_TITLE" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g').md"
  cp "$WORKDIR/report.md" "$REPORT_FILE"
  log_ok "Report saved: $REPORT_FILE"
fi

# ── Output report to stdout ───────────────────────────────
echo "" >&2
log_ok "Done! Report follows:" >&2
echo "───────────────────────────────────────" >&2
echo "" >&2

cat "$WORKDIR/report.md"
