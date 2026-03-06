#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Model Switchboard — First-Time Setup Wizard
# Guides new users through provider detection and redundancy config
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SWITCHBOARD="$SKILL_DIR/scripts/switchboard.sh"
REDUNDANCY="$SKILL_DIR/scripts/redundancy.py"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║         🔀 MODEL SWITCHBOARD — SETUP WIZARD            ║${NC}"
echo -e "${CYAN}${BOLD}║                                                          ║${NC}"
echo -e "${CYAN}${BOLD}║   Safe AI model configuration for OpenClaw               ║${NC}"
echo -e "${CYAN}${BOLD}║   Never crash your gateway again.                        ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check Prerequisites ───────────────────────────────
echo -e "${BOLD}Step 1: Checking prerequisites...${NC}"
echo ""

prereqs_ok=true

# Python 3
if command -v python3 &>/dev/null; then
    py_ver=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "  ${GREEN}✅${NC} Python $py_ver"
else
    echo -e "  ${RED}❌${NC} Python 3 not found — required for validation engine"
    echo -e "     Install: ${DIM}https://python.org/downloads${NC}"
    prereqs_ok=false
fi

# OpenClaw
if command -v openclaw &>/dev/null; then
    echo -e "  ${GREEN}✅${NC} OpenClaw CLI found"
else
    echo -e "  ${YELLOW}⚠️${NC}  OpenClaw CLI not in PATH"
    echo -e "     Install: ${DIM}npm install -g openclaw${NC}"
    echo -e "     ${DIM}(Switchboard can still validate and backup without CLI)${NC}"
fi

# Config file
if [ -f "$HOME/.openclaw/openclaw.json" ]; then
    echo -e "  ${GREEN}✅${NC} Config found: ~/.openclaw/openclaw.json"
else
    echo -e "  ${YELLOW}⚠️${NC}  No config file found"
    echo -e "     Run: ${DIM}openclaw onboard${NC} to create one"
fi

echo ""

if [ "$prereqs_ok" = false ]; then
    echo -e "${RED}Fix prerequisites above before continuing.${NC}"
    exit 1
fi

# ── Step 2: Detect Providers ──────────────────────────────────
echo -e "${BOLD}Step 2: Detecting available AI providers...${NC}"
echo ""

provider_json=$(python3 "$REDUNDANCY" providers 2>/dev/null || echo "{}")
provider_count=$(echo "$provider_json" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

if [ "$provider_count" -eq "0" ]; then
    echo -e "  ${RED}❌${NC} No providers detected!"
    echo ""
    echo -e "  ${BOLD}To use Model Switchboard, configure at least one AI provider:${NC}"
    echo ""
    echo -e "  ${CYAN}Anthropic (Claude):${NC}"
    echo "    export ANTHROPIC_API_KEY=sk-ant-..."
    echo "    ${DIM}or: openclaw models auth paste-token --provider anthropic${NC}"
    echo ""
    echo -e "  ${CYAN}OpenAI (GPT):${NC}"
    echo "    export OPENAI_API_KEY=sk-..."
    echo ""
    echo -e "  ${CYAN}Google (Gemini):${NC}"
    echo "    export GEMINI_API_KEY=AI..."
    echo ""
    echo -e "  ${CYAN}OpenRouter (hundreds of models):${NC}"
    echo "    export OPENROUTER_API_KEY=sk-or-..."
    echo ""
    echo -e "  ${DIM}After setting keys, run this setup again.${NC}"
    exit 1
fi

echo "$provider_json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for pid, p in data.items():
    count = len(p.get('models', []))
    print(f'  \033[32m✅\033[0m {p[\"displayName\"]:<25} {count} models  (via {p[\"authVia\"]})')
" 2>/dev/null

echo ""
echo -e "  ${BOLD}$provider_count provider(s) detected${NC}"
echo ""

# ── Step 3: Redundancy Assessment ─────────────────────────────
echo -e "${BOLD}Step 3: Assessing redundancy...${NC}"

python3 "$REDUNDANCY" report 3 2>/dev/null

# ── Step 4: Recommendations ───────────────────────────────────
echo ""
echo -e "${BOLD}Step 4: Recommendations${NC}"
echo ""

if [ "$provider_count" -lt 2 ]; then
    echo -e "  ${YELLOW}⚠️${NC}  You have only $provider_count provider. For true redundancy, add at least 2 more:"
    echo ""
    echo -e "  ${DIM}Recommended free/cheap options:${NC}"
    echo "    • OpenRouter — OPENROUTER_API_KEY (access to hundreds of models, many free)"
    echo "    • Google Gemini — GEMINI_API_KEY (generous free tier)"
    echo "    • Groq — GROQ_API_KEY (very fast, free tier available)"
    echo ""
elif [ "$provider_count" -lt 3 ]; then
    echo -e "  ${YELLOW}⚠️${NC}  You have $provider_count providers. Adding 1 more would give full 3-deep provider diversity."
    echo ""
else
    echo -e "  ${GREEN}✅${NC} You have $provider_count providers — excellent redundancy potential!"
    echo ""
fi

# ── Step 5: Ready to Deploy ───────────────────────────────────
echo -e "${BOLD}Step 5: Ready to deploy${NC}"
echo ""
echo -e "  To apply optimal redundant configuration:"
echo -e "    ${CYAN}./scripts/switchboard.sh redundancy-apply${NC}"
echo ""
echo -e "  To preview first (no changes):"
echo -e "    ${CYAN}./scripts/switchboard.sh redundancy-deploy${NC}"
echo ""
echo -e "  To see all commands:"
echo -e "    ${CYAN}./scripts/switchboard.sh help${NC}"
echo ""
echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}Model Switchboard is ready. Your gateway will never crash from bad model config again.${NC}"
echo ""
