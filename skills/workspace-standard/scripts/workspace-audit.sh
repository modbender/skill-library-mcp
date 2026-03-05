#!/usr/bin/env bash
# workspace-audit.sh — Audit an OpenClaw workspace against the workspace standard.
# Usage: ./workspace-audit.sh [workspace-path]
# Defaults to current directory if no path given.

set -euo pipefail

# Help
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
  echo "Usage: workspace-audit.sh [workspace-path]"
  echo ""
  echo "Audit an OpenClaw workspace against the workspace standard."
  echo "Defaults to current directory if no path given."
  echo "Exit code = number of issues (0 = clean)."
  exit 0
fi

WORKSPACE="${1:-.}"
ISSUES=0
WARNINGS=0

# --- Defaults (overridden by .workspace-standard.yml if present) ---
MEMORY_BUDGET=100
STALE_DAYS=14
PROJ_SUBDIRS="references plans research reports"

# --- Load config ---
CONFIG="$WORKSPACE/.workspace-standard.yml"
if [ -f "$CONFIG" ]; then
  # Simple YAML parser for flat keys (no external deps)
  _cfg() { grep "^[[:space:]]*$1:" "$CONFIG" 2>/dev/null | head -1 | sed "s/.*$1:[[:space:]]*//" | tr -d '"' | tr -d "'" || true; }
  VAL=$(_cfg memory_lines); [ -n "$VAL" ] && MEMORY_BUDGET="$VAL"
  VAL=$(_cfg stale_days);   [ -n "$VAL" ] && STALE_DAYS="$VAL"

  # Parse project subdirs list
  _parse_list() {
    local in_section=false
    while IFS= read -r line; do
      if echo "$line" | grep -q "^  ${1}:"; then in_section=true; continue; fi
      if $in_section; then
        if echo "$line" | grep -q "^[[:space:]]*- "; then
          echo "$line" | sed 's/^[[:space:]]*- //'
        else
          break
        fi
      fi
    done < "$CONFIG"
  }
  PARSED=$(_parse_list "subdirs")
  [ -n "$PARSED" ] && PROJ_SUBDIRS="$PARSED"
fi

# Colors (disabled if not a terminal)
if [ -t 1 ]; then
  RED='\033[0;31m'; YEL='\033[0;33m'; GRN='\033[0;32m'; DIM='\033[0;90m'; RST='\033[0m'
else
  RED=''; YEL=''; GRN=''; DIM=''; RST=''
fi

issue()   { ISSUES=$((ISSUES + 1));   echo -e "${RED}✗${RST} $1"; }
warn()    { WARNINGS=$((WARNINGS + 1)); echo -e "${YEL}⚠${RST} $1"; }
ok()      { echo -e "${GRN}✓${RST} $1"; }
section() { echo -e "\n${DIM}── $1 ──${RST}"; }

# --- Pre-flight ---
if [ ! -f "$WORKSPACE/MEMORY.md" ]; then
  echo "Error: $WORKSPACE doesn't look like an OpenClaw workspace (no MEMORY.md)"
  exit 1
fi

echo "Auditing workspace: $(cd "$WORKSPACE" && pwd)"

# --- 1. Root files ---
section "Root Files"
for f in AGENTS.md SOUL.md USER.md MEMORY.md; do
  [ -f "$WORKSPACE/$f" ] && ok "$f exists" || issue "$f missing"
done
for f in TOOLS.md IDENTITY.md HEARTBEAT.md; do
  [ -f "$WORKSPACE/$f" ] && ok "$f exists" || warn "$f missing (optional)"
done

# --- 2. MEMORY.md budget ---
section "MEMORY.md Budget"
if [ -f "$WORKSPACE/MEMORY.md" ]; then
  LINES=$(wc -l < "$WORKSPACE/MEMORY.md")
  if [ "$LINES" -le "$MEMORY_BUDGET" ]; then
    ok "MEMORY.md: ${LINES} lines (budget: ${MEMORY_BUDGET})"
  else
    OVER=$((LINES - MEMORY_BUDGET))
    issue "MEMORY.md: ${LINES} lines — ${OVER} lines OVER budget (${MEMORY_BUDGET})"
  fi
fi

# --- 3. Directory structure ---
section "Directory Structure"
for d in memory memory/entities projects runbooks skills; do
  [ -d "$WORKSPACE/$d" ] && ok "$d/ exists" || issue "$d/ missing"
done

# Warn if flat docs/ still exists with files
if [ -d "$WORKSPACE/docs" ] && [ "$(find "$WORKSPACE/docs" -type f 2>/dev/null | wc -l)" -gt 0 ]; then
  COUNT=$(find "$WORKSPACE/docs" -type f | wc -l)
  warn "docs/ still has ${COUNT} files — consider migrating to projects/ and runbooks/"
fi

# --- 4. Project registry ---
section "Projects"
if [ -f "$WORKSPACE/projects/_index.md" ]; then
  ok "projects/_index.md exists"
else
  issue "projects/_index.md missing — no project registry"
fi

# Check each project directory for README.md and standard subdirs
PROJ_COUNT=0
for proj_dir in "$WORKSPACE"/projects/*/; do
  [ -d "$proj_dir" ] || continue
  proj_name=$(basename "$proj_dir")
  [ "$proj_name" = "_index.md" ] && continue
  PROJ_COUNT=$((PROJ_COUNT + 1))

  if [ -f "$proj_dir/README.md" ]; then
    ok "projects/${proj_name}/README.md exists"
  else
    warn "projects/${proj_name}/README.md missing"
  fi

  # Check for standard subdirs or legacy docs/
  HAS_STANDARD=false
  for sub in $PROJ_SUBDIRS; do
    [ -d "$proj_dir/$sub" ] && HAS_STANDARD=true
  done
  if $HAS_STANDARD; then
    ok "projects/${proj_name}/ has standard subdirectories"
  elif [ -d "$proj_dir/docs" ]; then
    warn "projects/${proj_name}/ uses legacy docs/ — migrate when next touched"
  else
    warn "projects/${proj_name}/ has no content directories"
  fi
done
echo -e "${DIM}   ${PROJ_COUNT} projects found${RST}"

# --- 5. Runbooks ---
section "Runbooks"
if [ -d "$WORKSPACE/runbooks" ]; then
  RB_COUNT=$(find "$WORKSPACE/runbooks" -name "*.md" -type f | wc -l)
  ok "runbooks/ contains ${RB_COUNT} files"
else
  issue "runbooks/ missing"
fi

# --- 6. Front-matter audit ---
section "Front-Matter"
FM_TOTAL=0
FM_MISSING=0
FM_STALE=0

check_frontmatter() {
  local file="$1"
  local rel_path="${file#$WORKSPACE/}"
  ((FM_TOTAL++))

  # Check for YAML front-matter
  if head -1 "$file" 2>/dev/null | grep -q "^---$"; then
    # Check for role field
    if ! head -20 "$file" | grep -q "^role:"; then
      warn "${rel_path}: front-matter missing 'role:' field"
      FM_MISSING=$((FM_MISSING + 1))
    fi

    # Check for stale updated date
    UPDATED=$(head -20 "$file" | grep "^updated:" | sed 's/updated: *//' | tr -d '"' | tr -d "'" 2>/dev/null || true)
    if [ -n "$UPDATED" ]; then
      # Compare dates (portable: works on both GNU and BSD date)
      if command -v date >/dev/null 2>&1; then
        UPDATED_TS=$(date -d "$UPDATED" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$UPDATED" +%s 2>/dev/null || echo "")
        if [ -n "$UPDATED_TS" ]; then
          NOW_TS=$(date +%s)
          AGE_DAYS=$(( (NOW_TS - UPDATED_TS) / 86400 ))
          if [ "$AGE_DAYS" -gt "$STALE_DAYS" ]; then
            STATUS=$(head -20 "$file" | grep "^status:" | sed 's/status: *//' | tr -d '"' | tr -d "'" || true)
            if [ "$STATUS" = "current" ] || [ "$STATUS" = "active" ]; then
              warn "${rel_path}: status=${STATUS} but updated ${AGE_DAYS} days ago"
              FM_STALE=$((FM_STALE + 1))
            fi
          fi
        fi
      fi
    fi
  else
    FM_MISSING=$((FM_MISSING + 1))
  fi
}

# Scan projects/ and runbooks/ for markdown files (disable errexit for grep in function)
set +e
while IFS= read -r file; do
  [ -n "$file" ] && check_frontmatter "$file"
done < <(find "$WORKSPACE/projects" "$WORKSPACE/runbooks" -name "*.md" -type f 2>/dev/null)
set -e

if [ "$FM_MISSING" -eq 0 ]; then
  ok "All ${FM_TOTAL} files have front-matter with role"
else
  issue "${FM_MISSING}/${FM_TOTAL} files missing front-matter or role field"
fi

if [ "$FM_STALE" -gt 0 ]; then
  warn "${FM_STALE} files may be stale (active/current but not updated in >${STALE_DAYS} days)"
fi

# --- 7. Daily logs ---
section "Memory"
if [ -d "$WORKSPACE/memory" ]; then
  LOG_COUNT=$(find "$WORKSPACE/memory" -maxdepth 1 -name "20??-??-??.md" -type f | wc -l)
  ok "${LOG_COUNT} daily logs found"

  # Check for today's log
  TODAY=$(date +%Y-%m-%d)
  if [ -f "$WORKSPACE/memory/${TODAY}.md" ]; then
    ok "Today's log exists (${TODAY}.md)"
  else
    warn "No log for today (${TODAY}.md)"
  fi

  # Entity files
  ENT_COUNT=$(find "$WORKSPACE/memory/entities" -name "*.md" -type f 2>/dev/null | wc -l)
  ok "${ENT_COUNT} entity files"
fi

# --- Summary ---
section "Summary"
echo ""
if [ "$ISSUES" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
  echo -e "${GRN}Workspace is clean. No issues found.${RST}"
elif [ "$ISSUES" -eq 0 ]; then
  echo -e "${YEL}${WARNINGS} warning(s), 0 issues. Workspace is functional but could be tidier.${RST}"
else
  echo -e "${RED}${ISSUES} issue(s), ${WARNINGS} warning(s). Workspace needs attention.${RST}"
fi
echo ""

exit $ISSUES
