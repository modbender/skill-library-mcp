#!/usr/bin/env bash
# ClawAudit Skill Scanner
# Scans installed OpenClaw skills for malicious patterns
#
# Usage:
#   bash scan-skills.sh                    # Scan all skills
#   bash scan-skills.sh --skill <name>     # Scan specific skill
#   bash scan-skills.sh --json             # Output as JSON

set -euo pipefail

# --- Colors & Formatting ---
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

# --- Config ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERNS_FILE="${SCRIPT_DIR}/../references/malicious-patterns.json"
RULES_FILE="${SCRIPT_DIR}/../references/scan-rules.json"

# Skill directories to scan (in precedence order)
SKILL_DIRS=(
  "${HOME}/.openclaw/workspace/skills"
  "${HOME}/.npm-global/lib/node_modules/openclaw/skills"
  "${HOME}/.openclaw/skills"
  "${HOME}/openclaw/skills"
  "${HOME}/.clawdbot/skills"
)

# Also check workspace skills if OPENCLAW_WORKSPACE is set
if [ -n "${OPENCLAW_WORKSPACE:-}" ]; then
  SKILL_DIRS=("${OPENCLAW_WORKSPACE}/skills" "${SKILL_DIRS[@]}")
fi

# --- Arguments ---
SCAN_SINGLE=""
OUTPUT_JSON=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --skill) SCAN_SINGLE="$2"; shift 2 ;;
    --json) OUTPUT_JSON=true; shift ;;
    --help) echo "Usage: scan-skills.sh [--skill <name>] [--json]"; exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- Find skills directory ---
ACTIVE_SKILL_DIR=""
for dir in "${SKILL_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    ACTIVE_SKILL_DIR="$dir"
    break
  fi
done

if [ -z "$ACTIVE_SKILL_DIR" ]; then
  if ! $OUTPUT_JSON; then
    echo -e "${RED}✗ No skills directory found.${NC}" >&2
    echo "  Checked: ${SKILL_DIRS[*]}" >&2
  fi
  exit 1
fi

# --- Load Scan Rules from JSON ---
# Patterns are stored externally to keep this script clean of threat pattern strings.
if [ ! -f "$RULES_FILE" ]; then
  echo -e "${RED}✗ Scan rules file not found: ${RULES_FILE}${NC}" >&2
  exit 1
fi
if ! command -v jq &>/dev/null; then
  echo -e "${RED}✗ jq is required but not installed. Run: sudo apt install jq${NC}" >&2
  exit 1
fi

# Load all rules into parallel bash arrays.
# Output 5 lines per rule (code, severity, label, pattern, record-sep "---"),
# then read them in groups of 5 — avoids @tsv backslash double-escaping.
RULE_CODES=()
RULE_SEVERITIES=()
RULE_LABELS=()
RULE_PATTERNS=()

while IFS= read -r code && IFS= read -r severity && IFS= read -r label && IFS= read -r pattern && IFS= read -r _sep; do
  RULE_CODES+=("$code")
  RULE_SEVERITIES+=("$severity")
  RULE_LABELS+=("$label")
  RULE_PATTERNS+=("$pattern")
done < <(jq -r '.rules[] | .code, .severity, .label, (.patterns | join("|")), "---"' "$RULES_FILE")

# --- Scanner ---
FINDINGS=()
TOTAL_CRITICAL=0
TOTAL_WARNINGS=0
TOTAL_INFO=0
SKILLS_SCANNED=0

scan_skill() {
  local skill_dir="$1"
  local skill_name
  skill_name=$(basename "$skill_dir")

  # Skip if scanning a specific skill and this isn't it
  if [ -n "$SCAN_SINGLE" ] && [ "$skill_name" != "$SCAN_SINGLE" ]; then
    return
  fi

  # Auto-skip the directory ClawAudit itself is installed in —
  # it intentionally contains threat patterns (the scanner patterns themselves)
  local this_script_dir
  this_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local this_skill_dir
  this_skill_dir="$(dirname "$this_script_dir")"
  if [ "$(realpath "$skill_dir" 2>/dev/null || echo "$skill_dir")" = "$(realpath "$this_skill_dir" 2>/dev/null || echo "$this_skill_dir")" ]; then
    if ! $OUTPUT_JSON; then
      echo -e "\n${GRAY}━━━ Skipping (self): ${skill_name}${NC}"
    fi
    return
  fi

  # Also skip skills explicitly marked as trusted (first-party security tools)
  if [ -f "${skill_dir}/.claw-audit-trusted" ]; then
    if ! $OUTPUT_JSON; then
      echo -e "\n${GRAY}━━━ Skipping (trusted): ${skill_name}${NC}"
    fi
    return
  fi

  SKILLS_SCANNED=$((SKILLS_SCANNED + 1))
  local skill_findings=0

  if ! $OUTPUT_JSON; then
    echo -e "\n${BLUE}━━━ Scanning: ${BOLD}${skill_name}${NC} ${GRAY}(${skill_dir})${NC}"
  fi

  # Collect all text files in the skill directory (exclude references/ — pattern database, not code)
  local files
  files=$(find "$skill_dir" -type f \
    -not -path "*/references/*" \
    \( -name "*.md" -o -name "*.sh" -o -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" -o -name "*.cfg" \) \
    2>/dev/null || true)

  if [ -z "$files" ]; then
    if ! $OUTPUT_JSON; then
      echo -e "  ${GRAY}No scannable files found${NC}"
    fi
    return
  fi

  # Check all patterns (loaded from scan-rules.json)
  for i in "${!RULE_CODES[@]}"; do
    local code="${RULE_CODES[$i]}"
    local severity="${RULE_SEVERITIES[$i]}"
    local label="${RULE_LABELS[$i]}"
    local pattern="${RULE_PATTERNS[$i]}"

    while IFS= read -r file; do
      local matches
      matches=$(grep -nEi "$pattern" "$file" 2>/dev/null || true)
      if [ -n "$matches" ]; then
        local rel_file="${file#$skill_dir/}"
        skill_findings=$((skill_findings + 1))

        if [ "$severity" = "critical" ]; then
          TOTAL_CRITICAL=$((TOTAL_CRITICAL + 1))
          if ! $OUTPUT_JSON; then
            echo -e "  ${RED}🔴 ${code} ${label}${NC}"
            echo "$matches" | head -3 | while IFS= read -r line; do
              echo -e "     ${GRAY}${rel_file}:${line}${NC}"
            done
          fi
        else
          TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
          if ! $OUTPUT_JSON; then
            echo -e "  ${YELLOW}🟡 ${code} ${label}${NC}"
            echo "$matches" | head -2 | while IFS= read -r line; do
              echo -e "     ${GRAY}${rel_file}:${line}${NC}"
            done
          fi
        fi

        local safe_skill safe_label safe_file
        safe_skill="${skill_name//\"/\\\"}"
        safe_label="${label//\"/\\\"}"
        safe_file="${rel_file//\"/\\\"}"
        FINDINGS+=("{\"skill\":\"${safe_skill}\",\"severity\":\"${severity}\",\"code\":\"${code}\",\"label\":\"${safe_label}\",\"file\":\"${safe_file}\"}")
      fi
    done <<< "$files"
  done

  # Summary per skill
  if ! $OUTPUT_JSON; then
    if [ $skill_findings -eq 0 ]; then
      echo -e "  ${GREEN}✓ No issues found${NC}"
    fi
  fi
}

# --- Main ---
if ! $OUTPUT_JSON; then
  echo -e "${BOLD}🛡️  ClawAudit Skill Scanner${NC}"
  echo -e "${GRAY}Scanning skills in: ${ACTIVE_SKILL_DIR}${NC}"
fi

# Iterate over skill directories
if [ -n "$SCAN_SINGLE" ]; then
  skill_path="${ACTIVE_SKILL_DIR}/${SCAN_SINGLE}"
  if [ -d "$skill_path" ]; then
    scan_skill "$skill_path"
  else
    echo -e "${RED}✗ Skill '${SCAN_SINGLE}' not found in ${ACTIVE_SKILL_DIR}${NC}"
    exit 1
  fi
else
  for skill_dir in "${ACTIVE_SKILL_DIR}"/*/; do
    [ -d "$skill_dir" ] && scan_skill "$skill_dir"
  done
fi

# --- Output ---
if $OUTPUT_JSON; then
  echo "{"
  echo "  \"skills_scanned\": ${SKILLS_SCANNED},"
  echo "  \"critical\": ${TOTAL_CRITICAL},"
  echo "  \"warnings\": ${TOTAL_WARNINGS},"
  echo "  \"findings\": [$(IFS=,; echo "${FINDINGS[*]:-}")]"
  echo "}"
else
  echo ""
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}📊 Scan Summary${NC}"
  echo -e "   Skills scanned:  ${SKILLS_SCANNED}"
  echo -e "   Critical:        ${RED}${TOTAL_CRITICAL}${NC}"
  echo -e "   Warnings:        ${YELLOW}${TOTAL_WARNINGS}${NC}"

  if [ $TOTAL_CRITICAL -gt 0 ]; then
    echo ""
    echo -e "   ${RED}⚠️  Critical issues found! Review findings above.${NC}"
    echo -e "   ${GRAY}Run 'node scripts/audit-config.mjs' for config checks.${NC}"
  elif [ $TOTAL_WARNINGS -gt 0 ]; then
    echo ""
    echo -e "   ${YELLOW}⚡ Some warnings found. Review recommended.${NC}"
  else
    echo ""
    echo -e "   ${GREEN}✅ All skills look clean!${NC}"
  fi
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi
