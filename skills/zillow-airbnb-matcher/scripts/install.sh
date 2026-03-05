#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Zillow × Airbnb Matcher — OpenClaw Skill Installer
# Run this once to set up the skill on your OpenClaw instance
#
# Usage:
#   bash scripts/install.sh
#   bash scripts/install.sh --rapidapi-key YOUR_KEY_HERE
#
# What it does:
#   1. Checks Node.js is installed (requires v16+)
#   2. Installs npm dependencies
#   3. Sets up your RapidAPI key
#   4. Runs the demo to confirm everything works
# ─────────────────────────────────────────────────────────────────────────────

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$SKILL_DIR/.env"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}   🏠 Zillow × Airbnb Matcher — Skill Installer      ${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# ─── Step 1: Check Node.js ────────────────────────────────────────────────────

echo -e "${YELLOW}Step 1: Checking Node.js...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed.${NC}"
    echo "   Install it from: https://nodejs.org (choose 'LTS' version)"
    exit 1
fi

NODE_VERSION=$(node -e "process.stdout.write(process.version.slice(1).split('.')[0])")
if [ "$NODE_VERSION" -lt 16 ]; then
    echo -e "${RED}❌ Node.js v$NODE_VERSION found, but v16+ is required.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version) found${NC}"

# ─── Step 2: Install dependencies ────────────────────────────────────────────

echo ""
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"

cd "$SKILL_DIR"
npm install --silent 2>&1 | tail -5

echo -e "${GREEN}✅ Dependencies installed${NC}"

# ─── Step 3: RapidAPI Key setup ──────────────────────────────────────────────

echo ""
echo -e "${YELLOW}Step 3: RapidAPI key setup...${NC}"

# Parse --rapidapi-key argument
RAPIDAPI_KEY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --rapidapi-key) RAPIDAPI_KEY="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Check for existing key
EXISTING_KEY=""
if [ -f "$ENV_FILE" ]; then
    EXISTING_KEY=$(grep "^RAPIDAPI_KEY=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"')
fi

if [ -n "$RAPIDAPI_KEY" ]; then
    if [ -f "$ENV_FILE" ]; then
        if grep -q "^RAPIDAPI_KEY=" "$ENV_FILE"; then
            sed -i "s/^RAPIDAPI_KEY=.*/RAPIDAPI_KEY=$RAPIDAPI_KEY/" "$ENV_FILE"
        else
            echo "RAPIDAPI_KEY=$RAPIDAPI_KEY" >> "$ENV_FILE"
        fi
    else
        echo "RAPIDAPI_KEY=$RAPIDAPI_KEY" > "$ENV_FILE"
    fi
    echo -e "${GREEN}✅ RapidAPI key saved to .env${NC}"
elif [ -n "$EXISTING_KEY" ]; then
    echo -e "${GREEN}✅ RapidAPI key found in existing .env${NC}"
else
    echo -e "${YELLOW}ℹ️  No RapidAPI key provided.${NC}"
    echo ""
    echo "   To get your FREE key (takes 2 minutes):"
    echo "   1. Go to https://rapidapi.com → Sign up (free, no credit card)"
    echo "   2. Subscribe to these 2 APIs (both have free tiers):"
    echo "      - Airbnb: https://rapidapi.com/3b-data-3b-data-default/api/airbnb13"
    echo "      - Zillow: https://rapidapi.com/apimaker/api/zillow-com1"
    echo "   3. Copy your API key from any API page (top right)"
    echo "   4. Run again: bash scripts/install.sh --rapidapi-key YOUR_KEY"
    echo ""
    echo "   Demo mode works without a key!"
fi

# ─── Step 4: Run demo test ────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}Step 4: Running demo test...${NC}"
echo ""

node "$SKILL_DIR/scripts/search.js" --demo

echo ""
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}  ✅ Installation complete!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo "Chat commands (send to your bot):"
echo "  \"search airbnb 78704\"          → Live search Austin TX"
echo "  \"check properties 33139\"       → Miami Beach"
echo "  \"search airbnb Nashville TN\"   → Search by city"
echo "  \"airbnb demo\"                  → Demo (no API needed)"
echo ""
echo "CLI commands:"
echo "  node scripts/search.js --demo"
echo "  node scripts/search.js --zip 78704"
echo "  node scripts/search.js --zip 78704 --max-price 800000"
echo ""
