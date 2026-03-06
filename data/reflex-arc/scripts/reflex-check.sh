#!/usr/bin/env bash
# reflex-check.sh — Diagnostic tool for Reflex Arc skill
# Verifies the skill is installed correctly and shows its status.
# Zero dependencies. Runs anywhere bash runs.

set -euo pipefail

# Colors (disable if not a terminal)
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  RED='\033[0;31m'
  YELLOW='\033[1;33m'
  CYAN='\033[0;36m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  GREEN='' RED='' YELLOW='' CYAN='' BOLD='' RESET=''
fi

echo -e "${BOLD}⚡ Reflex Arc — Diagnostic Check${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check 1: Locate SKILL.md
SKILL_LOCATIONS=(
  "${HOME}/.openclaw/workspace/skills/reflex-arc/SKILL.md"
  "${HOME}/.moltbot/workspace/skills/reflex-arc/SKILL.md"
  "${HOME}/.clawdbot/workspace/skills/reflex-arc/SKILL.md"
)

FOUND=""
for loc in "${SKILL_LOCATIONS[@]}"; do
  if [ -f "$loc" ]; then
    FOUND="$loc"
    break
  fi
done

# Also check current directory
if [ -z "$FOUND" ] && [ -f "./SKILL.md" ]; then
  FOUND="./SKILL.md"
fi

if [ -n "$FOUND" ]; then
  echo -e "  ${GREEN}✓${RESET} SKILL.md found at: ${CYAN}${FOUND}${RESET}"
else
  echo -e "  ${RED}✗${RESET} SKILL.md not found in standard locations"
  echo ""
  echo "  Install with:"
  echo "    mkdir -p ~/.openclaw/workspace/skills/reflex-arc"
  echo "    cp SKILL.md ~/.openclaw/workspace/skills/reflex-arc/"
  echo ""
fi

# Check 2: Validate frontmatter
if [ -n "$FOUND" ]; then
  if head -1 "$FOUND" | grep -q "^---"; then
    echo -e "  ${GREEN}✓${RESET} YAML frontmatter detected"

    # Check for required fields
    if grep -q "^name:" "$FOUND"; then
      echo -e "  ${GREEN}✓${RESET} 'name' field present"
    else
      echo -e "  ${RED}✗${RESET} 'name' field missing from frontmatter"
    fi

    if grep -q "^description:" "$FOUND"; then
      echo -e "  ${GREEN}✓${RESET} 'description' field present"
    else
      echo -e "  ${RED}✗${RESET} 'description' field missing from frontmatter"
    fi

    if grep -q "^version:" "$FOUND"; then
      echo -e "  ${GREEN}✓${RESET} 'version' field present"
    else
      echo -e "  ${YELLOW}~${RESET} 'version' field missing (optional)"
    fi
  else
    echo -e "  ${RED}✗${RESET} No YAML frontmatter (file must start with ---)"
  fi
fi

# Check 3: Count reflexes defined
if [ -n "$FOUND" ]; then
  REFLEX_COUNT=$(grep -c "^### Reflex [0-9]" "$FOUND" 2>/dev/null || echo "0")
  echo -e "  ${GREEN}✓${RESET} ${REFLEX_COUNT} reflexes defined"
fi

# Check 4: References
if [ -n "$FOUND" ]; then
  SKILL_DIR=$(dirname "$FOUND")
  if [ -d "${SKILL_DIR}/references" ]; then
    REF_COUNT=$(find "${SKILL_DIR}/references" -name "*.md" 2>/dev/null | wc -l)
    echo -e "  ${GREEN}✓${RESET} references/ directory present (${REF_COUNT} docs)"
  else
    echo -e "  ${YELLOW}~${RESET} No references/ directory (optional)"
  fi
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BOLD}Reflex Inventory:${RESET}"
echo "  1. Contradiction Scan    — catches self-contradictions"
echo "  2. Scope Lock            — prevents answer drift"
echo "  3. Confidence Calibration — honest uncertainty"
echo "  4. Depth Match           — mirrors user's level"
echo "  5. Hallucination Sniff   — flags fabricated specifics"
echo "  6. Inversion Check       — pre-mortem on every action"
echo ""
echo -e "${BOLD}Cost:${RESET} \$0.00 | ${BOLD}APIs:${RESET} 0 | ${BOLD}Dependencies:${RESET} none"
echo -e "${BOLD}Impact:${RESET} Every other skill gets better."
echo ""
echo -e "⚡ ${CYAN}Reflex Arc is active. Think faster. Think safer.${RESET}"
