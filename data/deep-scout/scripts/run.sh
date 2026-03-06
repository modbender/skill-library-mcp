#!/usr/bin/env bash
# =============================================================================
# deep-scout/scripts/run.sh
# Main orchestrator for the Deep Scout multi-stage intelligence pipeline.
#
# Usage:
#   ./run.sh "your research query" [OPTIONS]
#
# Options:
#   --depth N          Number of URLs to fully fetch (1–10, default: 5)
#   --freshness STR    pd|pw|pm|py (default: pw)
#   --country CODE     2-letter country code (default: US)
#   --language CODE    2-letter language code (default: en)
#   --search-count N   Number of search results to collect before filtering (default: 8)
#   --min-score N      Minimum filter score 0–10 (default: 4)
#   --style STR        report|comparison|bullets|timeline (default: report)
#   --output FILE      Write report to this file instead of stdout
#   --no-browser       Disable browser fallback
#   --no-firecrawl     Disable Firecrawl fallback
#   --dimensions STR   Comparison dimensions (for --style comparison), comma-separated
#
# This script is designed to be called by the OpenClaw agent loop.
# It emits structured JSON state to deep-scout-state.json for resumability.
# =============================================================================

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
QUERY=""
DEPTH=5
FRESHNESS="pw"
COUNTRY="US"
LANGUAGE="en"
SEARCH_COUNT=8
MIN_SCORE=4
STYLE="report"
OUTPUT_FILE=""
BROWSER_FALLBACK=true
FIRECRAWL_FALLBACK=true
DIMENSIONS="auto"
MAX_CHARS=8000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
STATE_FILE="${SKILL_DIR}/deep-scout-state.json"
TODAY=$(date '+%Y-%m-%d')

# ── Arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --depth)        DEPTH="$2";        shift 2 ;;
    --freshness)    FRESHNESS="$2";    shift 2 ;;
    --country)      COUNTRY="$2";      shift 2 ;;
    --language)     LANGUAGE="$2";     shift 2 ;;
    --search-count) SEARCH_COUNT="$2"; shift 2 ;;
    --min-score)    MIN_SCORE="$2";    shift 2 ;;
    --style)        STYLE="$2";        shift 2 ;;
    --output)       OUTPUT_FILE="$2";  shift 2 ;;
    --dimensions)   DIMENSIONS="$2";   shift 2 ;;
    --no-browser)   BROWSER_FALLBACK=false; shift ;;
    --no-firecrawl) FIRECRAWL_FALLBACK=false; shift ;;
    -*)             echo "Unknown option: $1" >&2; exit 1 ;;
    *)              QUERY="$1";        shift ;;
  esac
done

if [[ -z "$QUERY" ]]; then
  echo '{"error": "Query is required. Usage: run.sh \"your query\" [OPTIONS]"}' >&2
  exit 1
fi

# ── Security: sanitize query to mitigate prompt injection ─────────────────────
sanitize_query() {
  local q="$1"
  # Truncate to 500 chars max
  q="${q:0:500}"
  # Strip common prompt injection patterns (case-insensitive via python)
  q=$(echo "$q" | python3 -c "
import re, sys
q = sys.stdin.read().strip()
# Remove role/system injection attempts
q = re.sub(r'(?i)(ignore\s+(all\s+)?previous|forget\s+(all\s+)?instructions|you\s+are\s+now|system\s*:|<\|im_start\|>|<\|im_end\|>|\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>)', '', q)
# Remove markdown/HTML attempts to inject blocks
q = re.sub(r'```[\s\S]*?```', '', q)
# Collapse whitespace
q = re.sub(r'\s+', ' ', q).strip()
print(q)
" 2>/dev/null || echo "$q")
  echo "$q"
}

QUERY=$(sanitize_query "$QUERY")

if [[ -z "$QUERY" ]]; then
  echo '{"error": "Query was empty after sanitization."}' >&2
  exit 1
fi

# ── Security: restrict --output to working directory ──────────────────────────
if [[ -n "$OUTPUT_FILE" ]]; then
  # Resolve to absolute path and ensure it stays under the skill dir or cwd
  RESOLVED_OUTPUT="$(cd "$(dirname "$OUTPUT_FILE")" 2>/dev/null && pwd)/$(basename "$OUTPUT_FILE")" 2>/dev/null || RESOLVED_OUTPUT=""
  ALLOWED_BASE_1="$(pwd)"
  ALLOWED_BASE_2="$SKILL_DIR"
  if [[ -z "$RESOLVED_OUTPUT" ]] || { [[ "$RESOLVED_OUTPUT" != "$ALLOWED_BASE_1"/* ]] && [[ "$RESOLVED_OUTPUT" != "$ALLOWED_BASE_2"/* ]]; }; then
    echo '{"error": "--output path must be under the current working directory or skill directory. Arbitrary paths are not allowed."}' >&2
    exit 1
  fi
  OUTPUT_FILE="$RESOLVED_OUTPUT"
fi

# ── Logging ───────────────────────────────────────────────────────────────────
log() { echo "[deep-scout] $*" >&2; }
log_json() { echo "$1" | python3 -m json.tool >&2 2>/dev/null || echo "$1" >&2; }

# ── State helpers ─────────────────────────────────────────────────────────────
init_state() {
  cat > "$STATE_FILE" <<EOF
{
  "query": $(echo "$QUERY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))"),
  "config": {
    "depth": $DEPTH,
    "freshness": "$FRESHNESS",
    "country": "$COUNTRY",
    "language": "$LANGUAGE",
    "search_count": $SEARCH_COUNT,
    "min_score": $MIN_SCORE,
    "style": "$STYLE",
    "max_chars": $MAX_CHARS
  },
  "stage": "init",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "search_results": [],
  "filtered_urls": [],
  "fetched_content": {},
  "report": null,
  "done": false
}
EOF
}

update_state() {
  local key="$1"
  local value="$2"
  # Use python3 to safely update JSON state (value passed via env to avoid injection)
  DS_KEY="$key" DS_VALUE="$value" python3 -c "
import json, os
state_file = os.environ.get('DS_STATE_FILE', '$STATE_FILE')
with open(state_file, 'r') as f:
    state = json.load(f)
keys = os.environ['DS_KEY'].split('.')
d = state
for k in keys[:-1]:
    d = d[k]
d[keys[-1]] = json.loads(os.environ['DS_VALUE'])
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null || true
}

# ── Stage 1: SEARCH ───────────────────────────────────────────────────────────
stage1_search() {
  log "Stage 1: Searching for: $QUERY"
  log "  params: count=$SEARCH_COUNT country=$COUNTRY freshness=$FRESHNESS lang=$LANGUAGE"

  # Emit the search parameters as structured JSON for the agent to execute
  # The agent calling this script will intercept this and run web_search
  cat <<EOF
DEEP_SCOUT_ACTION::web_search
{
  "query": $(echo "$QUERY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))"),
  "count": $SEARCH_COUNT,
  "country": "$COUNTRY",
  "search_lang": "$LANGUAGE",
  "freshness": "$FRESHNESS"
}
EOF
}

# ── Stage 2: FILTER ───────────────────────────────────────────────────────────
stage2_filter() {
  local results_json="$1"
  log "Stage 2: Filtering and scoring results"

  local prompt_file="$SKILL_DIR/prompts/filter.txt"
  local prompt
  prompt=$(cat "$prompt_file")

  # Template substitution
  prompt="${prompt//\{\{query\}\}/$QUERY}"
  prompt="${prompt//\{\{freshness\}\}/$FRESHNESS}"
  prompt="${prompt//\{\{min_score\}\}/$MIN_SCORE}"
  prompt="${prompt//\{\{results_json\}\}/$results_json}"

  cat <<EOF
DEEP_SCOUT_ACTION::llm_filter
{
  "prompt": $(echo "$prompt" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))"),
  "min_score": $MIN_SCORE,
  "depth": $DEPTH
}
EOF
}

# ── Stage 3: FETCH ────────────────────────────────────────────────────────────
stage3_fetch() {
  local url="$1"
  log "Stage 3: Fetching $url"

  cat <<EOF
DEEP_SCOUT_ACTION::fetch_tiered
{
  "url": $(echo "$url" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))"),
  "query": $(echo "$QUERY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))"),
  "max_chars": $MAX_CHARS,
  "browser_fallback": $BROWSER_FALLBACK,
  "firecrawl_fallback": $FIRECRAWL_FALLBACK,
  "browser_prompt_file": "$SKILL_DIR/prompts/browser-extract.txt"
}
EOF
}

# ── Stage 4: SYNTHESIZE ───────────────────────────────────────────────────────
stage4_synthesize() {
  local fetched_json="$1"
  log "Stage 4: Synthesizing report (style=$STYLE)"

  if [[ "$STYLE" == "comparison" ]]; then
    local prompt_file="$SKILL_DIR/prompts/synthesize-comparison.txt"
  else
    local prompt_file="$SKILL_DIR/prompts/synthesize-report.txt"
  fi

  local prompt
  prompt=$(cat "$prompt_file")

  # Build fetched_content_blocks from JSON
  local blocks
  blocks=$(echo "$fetched_json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
blocks = []
for i, (url, content) in enumerate(data.items(), 1):
    blocks.append(f'[Source {i}] ({url})\n{content}\n')
print('\n---\n'.join(blocks))
" 2>/dev/null || echo "$fetched_json")

  local source_count
  source_count=$(echo "$fetched_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo "?")

  prompt="${prompt//\{\{query\}\}/$QUERY}"
  prompt="${prompt//\{\{today\}\}/$TODAY}"
  prompt="${prompt//\{\{language\}\}/$LANGUAGE}"
  prompt="${prompt//\{\{source_count\}\}/$source_count}"
  prompt="${prompt//\{\{dimensions_or_auto\}\}/$DIMENSIONS}"
  prompt="${prompt//\{\{fetched_content_blocks\}\}/$blocks}"

  cat <<EOF
DEEP_SCOUT_ACTION::llm_synthesize
{
  "prompt": $(echo "$prompt" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))"),
  "style": "$STYLE",
  "output_file": $(echo "$OUTPUT_FILE" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))")
}
EOF
}

# ── MAIN ─────────────────────────────────────────────────────────────────────
main() {
  log "Deep Scout v0.1.0 — Starting pipeline"
  log "Query: $QUERY"

  init_state

  # Emit pipeline config for agent visibility
  cat <<EOF
DEEP_SCOUT_PIPELINE_START
{
  "query": $(echo "$QUERY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))"),
  "depth": $DEPTH,
  "freshness": "$FRESHNESS",
  "country": "$COUNTRY",
  "language": "$LANGUAGE",
  "search_count": $SEARCH_COUNT,
  "min_score": $MIN_SCORE,
  "style": "$STYLE",
  "browser_fallback": $BROWSER_FALLBACK,
  "firecrawl_fallback": $FIRECRAWL_FALLBACK,
  "state_file": "$STATE_FILE",
  "today": "$TODAY"
}

EOF

  # Stage 1: emit search action
  stage1_search

  echo ""
  echo "# AGENT INSTRUCTIONS FOR DEEP SCOUT PIPELINE"
  echo "# The above DEEP_SCOUT_ACTION blocks define the pipeline steps."
  echo "# Execute them in order:"
  echo "#   1. Run web_search with the params above"
  echo "#   2. Pass results to llm_filter (score and select top URLs)"
  echo "#   3. For each filtered URL, run fetch_tiered (web_fetch → firecrawl → browser)"
  echo "#   4. Pass all fetched content to llm_synthesize"
  echo "#   5. Output the final report"
  echo ""
  echo "# See $SKILL_DIR/SKILL.md for full agent loop instructions."
}

main "$@"
