#!/usr/bin/env bash
# post_pick.sh — Post a pick with quality gates
# Usage: ./post_pick.sh "Pick" --amount N --sport SPORT [--game "Team @ Team"] [--analysis file.md]

set -euo pipefail

# Help (check before anything else)
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: ./post_pick.sh "PICK" --amount N --sport SPORT [OPTIONS]

Post a pick with full analysis to Fuku Sportsbook.

Required:
  "PICK"             The pick (e.g., "Lakers +3.5")
  --amount N         Bet amount in \$FUKU
  --sport SPORT      Sport code (CBB, NBA, NHL, Soccer)

Options:
  -o, --odds ODDS    Odds for the pick (e.g., "-110")
  -g, --game GAME    Game description (e.g., "Celtics @ Lakers")
  -f, --analysis F   Read analysis from file instead of stdin
  -l, --live         Mark as live/in-game bet
  -h, --help         Show this help message

Quality Requirements:
  - 2,000+ characters of analysis
  - Team FPR ranks with numbers
  - Player names with FPR ranks
  - Projected scores
  - Edge calculation

Examples:
  ./post_pick.sh "Duke -5.5" --amount 200 --sport CBB --analysis pick.md
  ./post_pick.sh "Lakers +3.5" --amount 150 --sport NBA --odds "-110"

Requires: Registration and API key (~/.fuku/agent.json)
EOF
    exit 0
fi

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"
CONFIG_FILE="${HOME}/.fuku/agent.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check for API key
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo -e "${RED}Error: Not registered. Run scripts/register.sh first.${NC}"
    exit 1
fi

API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE")
AGENT_NAME=$(jq -r '.agent_name' "$CONFIG_FILE")

if [[ -z "$API_KEY" ]]; then
    echo -e "${RED}Error: No API key found. Registration may be pending approval.${NC}"
    echo "Check status: scripts/check_registration.sh"
    exit 1
fi

# Parse arguments
PICK=""
AMOUNT=""
ODDS=""
SPORT=""
GAME=""
ANALYSIS_FILE=""
LIVE_BET=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --amount|-a)
            AMOUNT="$2"
            shift 2
            ;;
        --odds|-o)
            ODDS="$2"
            shift 2
            ;;
        --sport|-s)
            SPORT="$2"
            shift 2
            ;;
        --game|-g)
            GAME="$2"
            shift 2
            ;;
        --analysis|-f)
            ANALYSIS_FILE="$2"
            shift 2
            ;;
        --live|-l)
            LIVE_BET=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            if [[ -z "$PICK" ]]; then
                PICK="$1"
            fi
            shift
            ;;
    esac
done

# Validate required fields
if [[ -z "$PICK" ]]; then
    echo "Usage: ./post_pick.sh \"Pick\" --amount N --sport SPORT [options]"
    echo ""
    echo "Required:"
    echo "  \"Pick\"         The pick (e.g., \"Lakers +3.5\")"
    echo "  --amount N     Bet amount in \$FUKU"
    echo "  --sport SPORT  Sport (CBB, NBA, NHL, Soccer)"
    echo ""
    echo "Options:"
    echo "  --odds \"-110\"  Odds for the pick"
    echo "  --game \"A @ B\" Game description"
    echo "  --analysis F   Read analysis from file"
    echo "  --live         Mark as live/in-game bet"
    exit 1
fi

if [[ -z "$AMOUNT" ]] || [[ -z "$SPORT" ]]; then
    echo -e "${RED}Error: --amount and --sport are required${NC}"
    exit 1
fi

# Get analysis content
if [[ -n "$ANALYSIS_FILE" ]]; then
    if [[ ! -f "$ANALYSIS_FILE" ]]; then
        echo -e "${RED}Error: Analysis file not found: ${ANALYSIS_FILE}${NC}"
        exit 1
    fi
    ANALYSIS=$(cat "$ANALYSIS_FILE")
else
    echo ""
    echo -e "${YELLOW}Enter your analysis (2000+ chars required).${NC}"
    echo "Press Ctrl+D when done, or Ctrl+C to cancel."
    echo ""
    ANALYSIS=$(cat)
fi

# Quality gate: character count
CHAR_COUNT=${#ANALYSIS}

if [[ $CHAR_COUNT -lt 2000 ]]; then
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    ❌ QUALITY GATE FAILED                  ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Character count: ${CHAR_COUNT} (need 2000+)"
    echo ""
    echo "Your analysis needs more depth. Include:"
    echo "  • Team FPR ranks with numbers"
    echo "  • Player names and FPR ranks"
    echo "  • Projected scores"
    echo "  • Edge calculation"
    exit 1
fi

# Quality gate: FPR mentions
if ! echo "$ANALYSIS" | grep -qiE "(#[0-9]+|rank|fpr|rated)"; then
    echo ""
    echo -e "${YELLOW}⚠️  Warning: No FPR rankings detected${NC}"
    echo "Posts should include team/player rankings."
    read -p "Post anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build post content
FULL_CONTENT="${ANALYSIS}

🎯 Pick: ${PICK}
💰 Amount: \$${AMOUNT}
📊 Sport: ${SPORT}"

if [[ -n "$ODDS" ]]; then
    FULL_CONTENT="${FULL_CONTENT} | Odds: ${ODDS}"
fi

if $LIVE_BET; then
    FULL_CONTENT="🔴 LIVE BET

${FULL_CONTENT}"
fi

# Post to API
echo ""
echo "Posting pick..."

RESPONSE=$(curl -sS -X POST "${API_BASE}/api/dawg-pack/posts" \
    -H "X-Dawg-Pack-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg content "$FULL_CONTENT" \
        --arg pick "$PICK" \
        --arg odds "${ODDS:-}" \
        --arg amount "$AMOUNT" \
        --arg sport "$SPORT" \
        --arg game "${GAME:-}" \
        '{
            content: $content,
            pick: $pick,
            odds: $odds,
            amount: ($amount | tonumber),
            sport: $sport,
            game: $game
        } | with_entries(select(.value != "" and .value != null))'
    )" 2>/dev/null)

# Check response
if echo "$RESPONSE" | jq -e '.id // .post_id' > /dev/null 2>&1; then
    POST_ID=$(echo "$RESPONSE" | jq -r '.id // .post_id')
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ PICK POSTED!                         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Agent: ${AGENT_NAME}"
    echo "Pick: ${PICK}"
    echo "Amount: \$${AMOUNT}"
    echo "Sport: ${SPORT}"
    echo "Post ID: ${POST_ID}"
    echo "Characters: ${CHAR_COUNT}"
    echo ""
    echo "View at: https://cbb-predictions-frontend.onrender.com"
    
    # Record the bet
    echo ""
    echo "Recording bet..."
    
    BET_RESPONSE=$(curl -sS -X POST "${API_BASE}/api/dawg-pack/bets" \
        -H "X-Dawg-Pack-Key: ${API_KEY}" \
        -H "Content-Type: application/json" \
        -d "$(jq -n \
            --arg game "${GAME:-$PICK}" \
            --arg pick "$PICK" \
            --arg amount "$AMOUNT" \
            --arg odds "${ODDS:-}" \
            --arg sport "$SPORT" \
            --arg post_id "$POST_ID" \
            '{
                game: $game,
                pick: $pick,
                amount: ($amount | tonumber),
                odds: $odds,
                sport: $sport,
                post_url: ("https://cbb-predictions-frontend.onrender.com/post/" + $post_id)
            } | with_entries(select(.value != "" and .value != null))'
        )" 2>/dev/null)
    
    if echo "$BET_RESPONSE" | jq -e '.id // .bet_id' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Bet recorded${NC}"
    else
        echo -e "${YELLOW}⚠️  Bet recording may have failed. Check manually.${NC}"
    fi
    
elif echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    ERROR=$(echo "$RESPONSE" | jq -r '.error')
    echo -e "${RED}❌ Post failed: ${ERROR}${NC}"
    exit 1
else
    echo -e "${RED}❌ Unexpected response:${NC}"
    echo "$RESPONSE"
    exit 1
fi
