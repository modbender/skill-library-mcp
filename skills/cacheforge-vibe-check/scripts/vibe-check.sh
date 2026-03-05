#!/usr/bin/env bash
# vibe-check.sh — Main entry point for the Vibe Check skill
# Audits code for "vibe coding sins" — patterns that indicate AI-generated
# code was accepted without proper review. Produces a scored report card.
#
# Usage:
#   ./vibe-check.sh FILE                    Analyze a single file
#   ./vibe-check.sh DIRECTORY               Scan directory recursively
#   ./vibe-check.sh --diff [HEAD~N]         Analyze git diff changes
#   ./vibe-check.sh --staged                Analyze staged changes
#   ./vibe-check.sh --fix FILE|DIRECTORY    Include fix suggestions
#
# Environment:
#   ANTHROPIC_API_KEY or OPENAI_API_KEY — for LLM-powered analysis
#   VIBE_CHECK_BATCH_SIZE — files per LLM call (default: 3)

set -euo pipefail
source "$(dirname "$0")/common.sh"

# ─── Argument parsing ────────────────────────────────────────────────
TARGET=""
DIFF_MODE="false"
DIFF_REF="HEAD~1"
STAGED_MODE="false"
BRANCH=""
FIX_MODE="false"
OUTPUT_FILE=""
MAX_FILES_ARG="$MAX_FILES"

show_help() {
  cat <<'EOF'

  🎭 Vibe Check v0.1.0 — Audit Code for Vibe Coding Sins
  ═══════════════════════════════════════════════════════

  USAGE:
    vibe-check FILE                 Analyze a single Python/JS/TS file
    vibe-check DIRECTORY            Scan directory recursively
    vibe-check --diff [HEAD~N]      Analyze files changed in git diff
    vibe-check --staged             Analyze git staged changes
    vibe-check --fix FILE|DIR       Include suggested fixes (unified diff)

  OPTIONS:
    --diff [REF]       Analyze changed files since REF (default: HEAD~1)
    --staged           Analyze staged changes only
    --branch BRANCH    Compare against branch
    --fix              Generate fix suggestions for each finding
    --output FILE      Write report to file instead of stdout
    --max-files N      Max files to analyze (default: 50)
    --help             Show this help

  EXAMPLES:
    vibe-check src/                        # Scan entire src directory
    vibe-check app.py                      # Check a single file
    vibe-check --diff HEAD~5              # Check last 5 commits
    vibe-check --fix src/utils/           # With fix suggestions
    vibe-check --diff --fix --output report.md

  LANGUAGES (v1):
    Python (.py), TypeScript (.ts, .tsx), JavaScript (.js, .jsx, .mjs, .cjs)

  ENVIRONMENT:
    ANTHROPIC_API_KEY   For LLM-powered analysis (recommended)
    OPENAI_API_KEY      Alternative LLM provider
    (Falls back to heuristic analysis if neither is set)

  SCORING:
    A (90-100)  Pristine       B (80-89)  Clean
    C (70-79)   Decent         D (60-69)  Needs Work
    F (<60)     Heavy Vibe Coding

EOF
}

require_option_value() {
  local flag="$1"
  local value="${2:-}"
  if [[ -z "$value" || "$value" =~ ^-- ]]; then
    err "Missing value for ${flag}"
    exit 1
  fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      show_help
      exit 0
      ;;
    --diff)
      DIFF_MODE="true"
      shift
      # Check if next arg looks like a ref (not a flag)
      if [[ $# -gt 0 && ! "$1" =~ ^-- ]]; then
        DIFF_REF="$1"
        shift
      fi
      ;;
    --staged)
      DIFF_MODE="true"
      STAGED_MODE="true"
      shift
      ;;
    --branch)
      DIFF_MODE="true"
      require_option_value "--branch" "${2:-}"
      BRANCH="$2"
      shift 2
      ;;
    --fix)
      FIX_MODE="true"
      shift
      ;;
    --output|-o)
      require_option_value "--output" "${2:-}"
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --max-files)
      require_option_value "--max-files" "${2:-}"
      if [[ ! "$2" =~ ^[1-9][0-9]*$ ]]; then
        err "--max-files must be a positive integer, got: $2"
        exit 1
      fi
      MAX_FILES_ARG="$2"
      shift 2
      ;;
    -*)
      warn "Unknown option: $1"
      shift
      ;;
    *)
      TARGET="$1"
      shift
      ;;
  esac
done

# ─── Validate inputs ─────────────────────────────────────────────────
if [ "$DIFF_MODE" = "false" ] && [ -z "$TARGET" ]; then
  err "No target specified. Provide a file, directory, or use --diff."
  echo "" >&2
  show_help >&2
  exit 1
fi

# ─── Discover files to analyze ───────────────────────────────────────
FILES_LIST=$(mktemp)
trap "rm -f '$FILES_LIST'" EXIT

if [ "$DIFF_MODE" = "true" ]; then
  # Git diff mode
  DIFF_ARGS=()
  if [ "$STAGED_MODE" = "true" ]; then
    DIFF_ARGS+=("--staged")
  elif [ -n "$BRANCH" ]; then
    DIFF_ARGS+=("--branch" "$BRANCH")
  else
    DIFF_ARGS+=("$DIFF_REF")
  fi
  
  bash "${SCRIPTS_DIR}/git-diff.sh" "${DIFF_ARGS[@]}" > "$FILES_LIST" 2>/dev/null || {
    err "Failed to get git diff files. Are you in a git repository?"
    exit 1
  }
  
  # Use target as display path or fallback to git root
  if [ -z "$TARGET" ]; then
    TARGET=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
  fi
else
  # File or directory mode
  discover_files "$TARGET" "$MAX_FILES_ARG" > "$FILES_LIST" 2>/dev/null || {
    err "Failed to discover files in: $TARGET"
    exit 1
  }
fi

FILE_COUNT=$(wc -l < "$FILES_LIST" | tr -d ' ')

if [ "$FILE_COUNT" -eq 0 ]; then
  err "No supported files found (Python, TypeScript, JavaScript)."
  info "Supported extensions: .py, .ts, .tsx, .js, .jsx, .mjs, .cjs"
  exit 1
fi

info "Found ${FILE_COUNT} file(s) to analyze"

# ─── Run analysis ────────────────────────────────────────────────────
ANALYSIS_FILE=$(mktemp)
trap "rm -f '$FILES_LIST' '$ANALYSIS_FILE'" EXIT

ANALYZE_ARGS=()
if [ "$FIX_MODE" = "true" ]; then
  ANALYZE_ARGS+=("--fix")
fi

# Read files and pass to analyzer
while IFS= read -r file; do
  [ -z "$file" ] && continue
  ANALYZE_ARGS+=("$file")
done < "$FILES_LIST"

bash "${SCRIPTS_DIR}/analyze.sh" "${ANALYZE_ARGS[@]}" > "$ANALYSIS_FILE" 2>/dev/null || {
  # analyzer may have partial results — continue if we have any
  if [ ! -s "$ANALYSIS_FILE" ]; then
    err "Analysis failed and produced no results."
    exit 1
  fi
  warn "Analysis completed with some errors (partial results)"
}

RESULT_COUNT=$(wc -l < "$ANALYSIS_FILE" | tr -d ' ')
if [ "$RESULT_COUNT" -eq 0 ]; then
  err "Analysis produced no results."
  exit 1
fi

info "Analyzed ${RESULT_COUNT} file(s), generating report..."

# ─── Generate report ─────────────────────────────────────────────────
REPORT_ARGS=("$TARGET")
if [ "$FIX_MODE" = "true" ]; then
  REPORT_ARGS+=("--fix")
fi

if [ -n "$OUTPUT_FILE" ]; then
  cat "$ANALYSIS_FILE" | bash "${SCRIPTS_DIR}/report.sh" "${REPORT_ARGS[@]}" > "$OUTPUT_FILE"
  info "Report written to: $OUTPUT_FILE"
  
  # Print summary to stderr
  SCORE=$(cat "$ANALYSIS_FILE" | python3 -c "
import json, sys
results = [json.loads(l) for l in sys.stdin if l.strip()]
weights = {'error_handling':0.20,'duplication':0.15,'dead_code':0.10,'input_validation':0.15,'magic_values':0.10,'test_coverage':0.10,'naming_quality':0.10,'security':0.10}
total_lines = sum(r.get('line_count',1) for r in results)
if total_lines > 0:
    score = sum(sum(r.get('scores',{}).get(c,50)*w for c,w in weights.items()) * r.get('line_count',1) for r in results) / total_lines
else:
    score = 50
print(round(max(0,min(100,score))))
" 2>/dev/null || echo "??")
  info "🎭 Vibe Score: ${SCORE}/100"
else
  cat "$ANALYSIS_FILE" | bash "${SCRIPTS_DIR}/report.sh" "${REPORT_ARGS[@]}"
fi
