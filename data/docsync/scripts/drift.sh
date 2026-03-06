#!/usr/bin/env bash
# DocSync — Drift Detection Module
# Compares code symbols against existing documentation to find staleness

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/analyze.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ─── Doc file discovery ────────────────────────────────────────────────────

find_doc_for_source() {
  local source_file="$1"
  local dir basename name

  dir=$(dirname "$source_file")
  basename=$(basename "$source_file")
  name="${basename%.*}"

  # Check common doc locations
  local candidates=(
    "$dir/$name.md"
    "$dir/README.md"
    "$dir/docs/$name.md"
    "docs/$dir/$name.md"
    "docs/api/$name.md"
    "docs/${name}.md"
  )

  for candidate in "${candidates[@]}"; do
    if [[ -f "$candidate" ]]; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

# Check if a symbol name is mentioned in a doc file
symbol_documented() {
  local symbol_name="$1"
  local doc_file="$2"

  grep -qiP "(^#+.*\b${symbol_name}\b|\`${symbol_name}\`|\b${symbol_name}\s*\(|### ${symbol_name}|## ${symbol_name})" "$doc_file" 2>/dev/null
}

# ─── Drift detection ───────────────────────────────────────────────────────

# Returns drift entries: SEVERITY\tSYMBOL\tTYPE\tFILE\tDOC_FILE\tREASON
detect_drift_for_file() {
  local source_file="$1"
  local doc_file

  if ! doc_file=$(find_doc_for_source "$source_file"); then
    # No doc file at all — everything is undocumented
    while IFS=$'\t' read -r type name lineno filepath; do
      echo -e "warning\t$name\t$type\t$source_file\t(none)\tNo documentation file found"
    done < <(parse_symbols "$source_file")
    return
  fi

  local doc_mtime source_mtime
  doc_mtime=$(stat -c %Y "$doc_file" 2>/dev/null || stat -f %m "$doc_file" 2>/dev/null || echo "0")
  source_mtime=$(stat -c %Y "$source_file" 2>/dev/null || stat -f %m "$source_file" 2>/dev/null || echo "0")

  while IFS=$'\t' read -r type name lineno filepath; do
    if ! symbol_documented "$name" "$doc_file"; then
      echo -e "critical\t$name\t$type\t$source_file\t$doc_file\tSymbol not documented"
    elif [[ "$source_mtime" -gt "$doc_mtime" ]]; then
      echo -e "warning\t$name\t$type\t$source_file\t$doc_file\tSource newer than docs (possible drift)"
    else
      echo -e "info\t$name\t$type\t$source_file\t$doc_file\tDocumented and up-to-date"
    fi
  done < <(parse_symbols "$source_file")
}

# ─── Drift report ──────────────────────────────────────────────────────────

generate_drift_report() {
  local target="$1"
  local critical=0 warnings=0 ok=0 total=0
  local report_file
  report_file=$(mktemp)

  echo -e "${BOLD}━━━ DocSync Drift Report ━━━${NC}"
  echo ""

  if [[ -f "$target" ]]; then
    detect_drift_for_file "$target" > "$report_file"
  elif [[ -d "$target" ]]; then
    analyze_directory "$target" | cut -f4 | sort -u | while IFS= read -r file; do
      detect_drift_for_file "$file"
    done > "$report_file"
  fi

  # Count severities
  critical=$(grep -c "^critical" "$report_file" 2>/dev/null || echo "0")
  warnings=$(grep -c "^warning" "$report_file" 2>/dev/null || echo "0")
  ok=$(grep -c "^info" "$report_file" 2>/dev/null || echo "0")
  total=$((critical + warnings + ok))

  # Print critical issues
  if [[ "$critical" -gt 0 ]]; then
    echo -e "${RED}${BOLD}CRITICAL ($critical)${NC} — Undocumented symbols"
    grep "^critical" "$report_file" | while IFS=$'\t' read -r sev name type file doc reason; do
      echo -e "  ${RED}✗${NC} ${BOLD}$name${NC} ${DIM}($type in $file)${NC}"
    done
    echo ""
  fi

  # Print warnings
  if [[ "$warnings" -gt 0 ]]; then
    echo -e "${YELLOW}${BOLD}WARNING ($warnings)${NC} — Possibly stale docs"
    grep "^warning" "$report_file" | while IFS=$'\t' read -r sev name type file doc reason; do
      echo -e "  ${YELLOW}⚠${NC} ${BOLD}$name${NC} ${DIM}($type in $file → $doc)${NC}"
    done
    echo ""
  fi

  # Print summary
  if [[ "$ok" -gt 0 ]]; then
    echo -e "${GREEN}${BOLD}UP TO DATE ($ok)${NC} — Documented symbols"
    echo ""
  fi

  # Summary bar
  echo -e "${BOLD}Summary:${NC} $total symbols analyzed"
  echo -e "  ${GREEN}✓ $ok documented${NC}  ${YELLOW}⚠ $warnings possibly stale${NC}  ${RED}✗ $critical undocumented${NC}"

  if [[ "$critical" -gt 0 ]]; then
    echo ""
    echo -e "${CYAN}Run ${BOLD}docsync auto-fix${NC}${CYAN} to regenerate stale docs automatically.${NC}"
  fi

  rm -f "$report_file"

  # Return exit code based on severity
  if [[ "$critical" -gt 0 ]]; then
    return 2
  elif [[ "$warnings" -gt 0 ]]; then
    return 1
  fi
  return 0
}

# ─── Commands ───────────────────────────────────────────────────────────────

do_drift() {
  local target="${1:-.}"
  generate_drift_report "$target"
}

do_auto_fix() {
  local target="${1:-.}"
  local stale_files

  echo -e "${BLUE}[DocSync]${NC} Scanning for files needing doc updates..."

  stale_files=$(mktemp)

  if [[ -f "$target" ]]; then
    detect_drift_for_file "$target" | grep -P "^(critical|warning)" | cut -f4 | sort -u > "$stale_files"
  elif [[ -d "$target" ]]; then
    analyze_directory "$target" | cut -f4 | sort -u | while IFS= read -r file; do
      detect_drift_for_file "$file"
    done | grep -P "^(critical|warning)" | cut -f4 | sort -u > "$stale_files"
  fi

  local count
  count=$(wc -l < "$stale_files" | tr -d ' ')

  if [[ "$count" -eq 0 ]]; then
    echo -e "${GREEN}[DocSync]${NC} All documentation is up to date!"
    rm -f "$stale_files"
    return 0
  fi

  echo -e "${BLUE}[DocSync]${NC} Found ${BOLD}$count${NC} files with stale or missing docs"
  echo ""

  while IFS= read -r file; do
    echo -e "${BLUE}[DocSync]${NC} Regenerating docs for ${BOLD}$file${NC}"
    do_generate "$file"
  done < "$stale_files"

  rm -f "$stale_files"
  echo ""
  echo -e "${GREEN}[DocSync]${NC} Auto-fix complete. Run ${BOLD}docsync drift${NC} to verify."
}

# ─── Git hook drift check ──────────────────────────────────────────────────

# Called by lefthook pre-commit hook
hook_drift_check() {
  local staged_files
  staged_files=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)

  if [[ -z "$staged_files" ]]; then
    return 0
  fi

  local has_drift=false
  local drift_output
  drift_output=$(mktemp)

  while IFS= read -r file; do
    if is_source_file "$file" && [[ -f "$file" ]]; then
      local file_drift
      file_drift=$(detect_drift_for_file "$file" | grep "^critical" || true)
      if [[ -n "$file_drift" ]]; then
        echo "$file_drift" >> "$drift_output"
        has_drift=true
      fi
    fi
  done <<< "$staged_files"

  if [[ "$has_drift" == "true" ]]; then
    echo ""
    echo -e "${RED}${BOLD}━━━ DocSync: Documentation Drift Detected ━━━${NC}"
    echo ""
    echo -e "${RED}The following symbols are undocumented:${NC}"
    while IFS=$'\t' read -r sev name type file doc reason; do
      echo -e "  ${RED}✗${NC} ${BOLD}$name${NC} ${DIM}($type in $file)${NC}"
    done < "$drift_output"
    echo ""
    echo -e "Run ${CYAN}${BOLD}docsync auto-fix${NC} to generate missing docs,"
    echo -e "or commit with ${CYAN}--no-verify${NC} to skip this check."
    echo ""
    rm -f "$drift_output"
    return 1
  fi

  rm -f "$drift_output"
  echo -e "${GREEN}[DocSync]${NC} Documentation is in sync with staged changes."
  return 0
}
