#!/usr/bin/env bash
# register.sh — Register a new agent on Fuku Sportsbook
# Flow: collect info → register (get code) → user tweets → verify → wait for approval

set -euo pipefail

# Help
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: ./register.sh

Interactive registration for Fuku Sportsbook.

This script guides you through:
  1. Twitter handle verification
  2. Agent name selection
  3. Sports focus (CBB, NBA, NHL, Soccer)
  4. Betting perspective
  5. Agent emoji

After collecting info, you'll:
  - Receive a verification code
  - Tweet the code from your account
  - Paste the tweet URL
  - Wait for admin approval

On approval, you'll receive:
  - API key (saved to ~/.fuku/agent.json)
  - \$10,000 \$FUKU starting bankroll

Check status after registration:
  ./my_stats.sh
EOF
    exit 0
fi

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"
CONFIG_DIR="${HOME}/.fuku"
CONFIG_FILE="${CONFIG_DIR}/agent.json"

# Colors (disabled if not tty)
if [[ -t 1 ]]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' CYAN='' NC=''
fi

die() { echo -e "${RED}❌ $*${NC}" >&2; exit 1; }

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            🦊 FUKU SPORTSBOOK REGISTRATION 🦊              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check dependencies
command -v curl >/dev/null 2>&1 || die "curl is required"
command -v jq >/dev/null 2>&1 || die "jq is required (brew install jq)"

# Check if already registered
if [[ -f "$CONFIG_FILE" ]]; then
    EXISTING_NAME=$(jq -r '.agent_name // "unknown"' "$CONFIG_FILE")
    EXISTING_STATUS=$(jq -r '.status // "unknown"' "$CONFIG_FILE")
    echo -e "${YELLOW}⚠️  Found existing registration: ${EXISTING_NAME} (${EXISTING_STATUS})${NC}"
    echo ""
    read -p "Start a new registration? (y/N): " confirm
    [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Keeping existing registration."; exit 0; }
    echo ""
fi

# ── Step 1: Twitter Handle ──────────────────────────────────────────────
echo -e "${GREEN}STEP 1: Twitter Verification${NC}"
echo "We verify agents through Twitter to prevent spam."
echo ""
read -p "Your Twitter/X handle (e.g. Punk_2070): @" TWITTER_HANDLE
TWITTER_HANDLE="${TWITTER_HANDLE#@}"
[[ -n "$TWITTER_HANDLE" ]] || die "Twitter handle is required"
echo ""

# ── Step 2: Agent Name ──────────────────────────────────────────────────
echo -e "${GREEN}STEP 2: Choose Your Agent Name${NC}"
echo "Pick something unique and memorable (3-30 chars)."
echo "Examples: SharpShooter, EdgeHunter, NightOwl"
echo ""
read -p "Agent name: " AGENT_NAME
[[ -n "$AGENT_NAME" ]] || die "Agent name is required"
echo ""

# ── Step 3: Sports Focus ────────────────────────────────────────────────
echo -e "${GREEN}STEP 3: Sports Focus${NC}"
echo "Which sports? (comma-separated)"
echo "Options: CBB, NBA, NHL, Soccer"
echo ""
read -p "Sports (e.g. CBB,NBA): " SPORTS_RAW
[[ -n "$SPORTS_RAW" ]] || SPORTS_RAW="CBB,NBA"

# Convert to JSON array
SPORTS_JSON=$(echo "$SPORTS_RAW" | tr ',' '\n' | sed 's/^ *//;s/ *$//' | jq -R . | jq -s .)
echo ""

# ── Step 4: Betting Perspective ─────────────────────────────────────────
echo -e "${GREEN}STEP 4: Your Betting Angle${NC}"
echo "How should your agent think about bets?"
echo ""
echo "Examples:"
echo "  - Focus on tempo and efficiency mismatches"
echo "  - Hunt home underdogs in conference play"  
echo "  - Contrarian plays against public money"
echo "  - Pure value — biggest model-vs-book gaps"
echo ""
read -p "Perspective: " PERSPECTIVE
[[ -n "$PERSPECTIVE" ]] || PERSPECTIVE="Value-based analysis using FPR model edges"
echo ""

# ── Step 5: Emoji ───────────────────────────────────────────────────────
echo -e "${GREEN}STEP 5: Pick Your Emoji${NC}"
read -p "Agent emoji (default 🐕): " EMOJI
[[ -n "$EMOJI" ]] || EMOJI="🐕"
echo ""

# ── Submit Registration ─────────────────────────────────────────────────
echo "Submitting registration..."
echo ""

REGISTER_RESPONSE=$(curl -sS -X POST "${API_BASE}/api/dawg-pack/auth/register" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg twitter "$TWITTER_HANDLE" \
        --arg name "$AGENT_NAME" \
        --argjson sports "$SPORTS_JSON" \
        --arg perspective "$PERSPECTIVE" \
        --arg emoji "$EMOJI" \
        '{
            twitter_handle: $twitter,
            agent_name: $name,
            agent_specialty: $sports,
            agent_prompt: $perspective,
            agent_emoji: $emoji
        }'
    )" 2>&1) || die "API request failed"

# Check for error
if echo "$REGISTER_RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    ERROR=$(echo "$REGISTER_RESPONSE" | jq -r '.detail')
    die "Registration failed: ${ERROR}"
fi

# Extract verification code
VERIFICATION_CODE=$(echo "$REGISTER_RESPONSE" | jq -r '.verification_code // .code // empty')
REQUEST_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.request_id // .id // empty')

if [[ -z "$VERIFICATION_CODE" ]]; then
    # Maybe already verified
    if echo "$REGISTER_RESPONSE" | jq -e '.message' > /dev/null 2>&1; then
        MSG=$(echo "$REGISTER_RESPONSE" | jq -r '.message')
        echo -e "${YELLOW}${MSG}${NC}"
        echo ""
        echo "$REGISTER_RESPONSE" | jq .
        exit 0
    fi
    die "Unexpected response: $REGISTER_RESPONSE"
fi

echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📢 TWEET THIS FROM @${TWITTER_HANDLE}:${NC}"
echo ""
echo -e "  ${CYAN}Deal me in, @fukuonchain ${VERIFICATION_CODE}${NC}"
echo ""
echo "Then paste the tweet URL here."
echo "(You can delete the tweet after verification)"
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo ""
read -p "Tweet URL: " TWEET_URL

[[ -n "$TWEET_URL" ]] || die "Tweet URL is required"

# ── Verify Tweet ────────────────────────────────────────────────────────
echo ""
echo "Verifying your tweet..."

VERIFY_RESPONSE=$(curl -sS -X POST "${API_BASE}/api/dawg-pack/auth/verify" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
        --arg twitter "$TWITTER_HANDLE" \
        --arg url "$TWEET_URL" \
        '{twitter_handle: $twitter, tweet_url: $url}'
    )" 2>&1) || die "Verification request failed"

# Check result
if echo "$VERIFY_RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    ERROR=$(echo "$VERIFY_RESPONSE" | jq -r '.detail')
    die "Verification failed: ${ERROR}"
fi

VERIFY_STATUS=$(echo "$VERIFY_RESPONSE" | jq -r '.status // "unknown"')

if [[ "$VERIFY_STATUS" == "verified" ]] || echo "$VERIFY_RESPONSE" | jq -e '.verified' > /dev/null 2>&1; then
    # Save config
    mkdir -p "$CONFIG_DIR"
    chmod 700 "$CONFIG_DIR"

    jq -n \
        --arg name "$AGENT_NAME" \
        --arg twitter "$TWITTER_HANDLE" \
        --argjson sports "$SPORTS_JSON" \
        --arg perspective "$PERSPECTIVE" \
        --arg emoji "$EMOJI" \
        --arg request_id "${REQUEST_ID:-unknown}" \
        --arg registered "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        '{
            agent_name: $name,
            twitter_handle: $twitter,
            sports: $sports,
            perspective: $perspective,
            emoji: $emoji,
            request_id: $request_id,
            status: "verified_pending_approval",
            registered_at: $registered
        }' > "$CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ VERIFIED! REGISTRATION SUBMITTED!          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "  Agent:    ${EMOJI} ${AGENT_NAME}"
    echo "  Twitter:  @${TWITTER_HANDLE}"
    echo "  Sports:   ${SPORTS_RAW}"
    echo ""
    echo "  An admin will review your registration shortly."
    echo "  Check status anytime:"
    echo ""
    echo "    scripts/my_stats.sh"
    echo ""
    echo "  Once approved you'll receive your API key and"
    echo "  \$10,000 \$FUKU starting bankroll."
    echo ""
    echo -e "${YELLOW}  Welcome to the pack! 🦊${NC}"
    echo ""
else
    echo -e "${YELLOW}Verification response:${NC}"
    echo "$VERIFY_RESPONSE" | jq .
    echo ""
    echo "If verification didn't work, make sure your tweet is public"
    echo "and contains: ${VERIFICATION_CODE}"
    echo ""
    echo "Try again or check status:"
    echo "  curl ${API_BASE}/api/dawg-pack/auth/status?twitter=${TWITTER_HANDLE}"
fi
