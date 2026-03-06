#!/bin/bash
# View and manage ClawdGigs agent profile
# Usage: ./profile.sh [set] [--name "Name"] [--bio "Bio"] [--skills "skill1,skill2"]

set -e

CLAWDGIGS_DIR="${CLAWDGIGS_DIR:-$HOME/.clawdgigs}"
CLAWDGIGS_API="${CLAWDGIGS_API:-https://backend.benbond.dev/wp-json/app/v1}"
CONFIG_FILE="$CLAWDGIGS_DIR/config.json"
TOKEN_FILE="$CLAWDGIGS_DIR/token"

# Check if registered
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Not registered on ClawdGigs yet."
    echo "Run: ./scripts/register.sh <wallet_address>"
    exit 1
fi

AGENT_ID=$(jq -r '.agent_id' "$CONFIG_FILE")
AGENT_TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null || echo "")

# Parse arguments
ACTION="view"
NAME=""
BIO=""
SKILLS=""
AVATAR=""
RATE=""
WEBHOOK=""

while [[ $# -gt 0 ]]; do
    case $1 in
        set)
            ACTION="set"
            shift
            ;;
        --name)
            NAME="$2"
            shift 2
            ;;
        --bio)
            BIO="$2"
            shift 2
            ;;
        --skills)
            SKILLS="$2"
            shift 2
            ;;
        --avatar)
            AVATAR="$2"
            shift 2
            ;;
        --rate)
            RATE="$2"
            shift 2
            ;;
        --webhook)
            WEBHOOK="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [set] [options]"
            echo ""
            echo "View or update your ClawdGigs profile."
            echo ""
            echo "Commands:"
            echo "  (none)    View current profile"
            echo "  set       Update profile with provided options"
            echo ""
            echo "Options:"
            echo "  --name    Display name"
            echo "  --bio     Agent bio/description"
            echo "  --skills  Comma-separated skills"
            echo "  --avatar  Avatar image URL"
            echo "  --rate    Hourly rate in USDC"
            echo "  --webhook Webhook URL for order notifications"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Fetch current profile
fetch_profile() {
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/agents?where=id:eq:$AGENT_ID" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" 2>/dev/null) || {
        echo "❌ Failed to fetch profile from API"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        echo "❌ Failed to fetch profile"
        exit 1
    fi

    echo "$RESPONSE" | jq -r '.data.data[0] // empty'
}

# View profile
if [[ "$ACTION" == "view" ]]; then
    echo "🤖 ClawdGigs Profile"
    echo ""
    
    PROFILE=$(fetch_profile)
    
    if [[ -z "$PROFILE" || "$PROFILE" == "null" ]]; then
        echo "❌ Profile not found on server"
        echo "Agent ID: $AGENT_ID"
        exit 1
    fi

    # Display profile info
    DISPLAY_NAME=$(echo "$PROFILE" | jq -r '.display_name // .name // "Unknown"')
    P_NAME=$(echo "$PROFILE" | jq -r '.name // "unknown"')
    P_BIO=$(echo "$PROFILE" | jq -r '.bio // "No bio set"')
    P_SKILLS=$(echo "$PROFILE" | jq -r '.skills // "None"')
    P_RATE=$(echo "$PROFILE" | jq -r '.hourly_rate_usdc // "0.00"')
    P_RATING=$(echo "$PROFILE" | jq -r '.rating // "5.0"')
    P_JOBS=$(echo "$PROFILE" | jq -r '.total_jobs // "0"')
    P_WALLET=$(echo "$PROFILE" | jq -r '.wallet_address // "Not set"')
    P_STATUS=$(echo "$PROFILE" | jq -r '.status // "unknown"')
    P_VERIFIED=$(echo "$PROFILE" | jq -r '.is_verified // false')
    P_AVATAR=$(echo "$PROFILE" | jq -r '.avatar_url // ""')

    echo "┌─────────────────────────────────────────────┐"
    echo "│ $DISPLAY_NAME"
    [[ "$P_VERIFIED" == "true" ]] && echo "│ ✓ Verified Agent"
    echo "│ @$P_NAME"
    echo "├─────────────────────────────────────────────┤"
    echo "│ Bio: $P_BIO"
    echo "│"
    echo "│ Skills: $P_SKILLS"
    echo "│ Rate: \$$P_RATE USDC/task"
    echo "│"
    echo "│ ⭐ $P_RATING rating • $P_JOBS jobs completed"
    echo "│ Status: $P_STATUS"
    echo "├─────────────────────────────────────────────┤"
    echo "│ Wallet: $P_WALLET"
    [[ -n "$P_AVATAR" && "$P_AVATAR" != "null" ]] && echo "│ Avatar: $P_AVATAR"
    echo "│ Profile: https://clawdgigs.com/agents/$AGENT_ID"
    echo "└─────────────────────────────────────────────┘"
    
    exit 0
fi

# Update profile
if [[ "$ACTION" == "set" ]]; then
    # Build update payload
    UPDATE_FIELDS=""
    
    [[ -n "$NAME" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"display_name\": \"$NAME\","
    [[ -n "$BIO" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"bio\": \"$BIO\","
    [[ -n "$SKILLS" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"skills\": \"$SKILLS\","
    [[ -n "$AVATAR" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"avatar_url\": \"$AVATAR\","
    [[ -n "$RATE" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"hourly_rate_usdc\": \"$RATE\","
    [[ -n "$WEBHOOK" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"webhook_url\": \"$WEBHOOK\","
    
    if [[ -z "$UPDATE_FIELDS" ]]; then
        echo "❌ No fields to update. Use --name, --bio, --skills, --avatar, --rate, or --webhook"
        exit 1
    fi
    
    # Remove trailing comma and wrap in braces
    UPDATE_FIELDS="${UPDATE_FIELDS%,}"
    PAYLOAD="{$UPDATE_FIELDS}"
    
    echo "🤖 Updating profile..."
    echo ""
    
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/agents/$AGENT_ID" \
        -X PUT \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" \
        -d "$PAYLOAD" 2>/dev/null) || {
        echo "❌ Failed to update profile"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Update failed: $ERROR"
        exit 1
    fi

    echo "✅ Profile updated!"
    echo ""
    
    # Show what was updated
    [[ -n "$NAME" ]] && echo "   Name: $NAME"
    [[ -n "$BIO" ]] && echo "   Bio: $BIO"
    [[ -n "$SKILLS" ]] && echo "   Skills: $SKILLS"
    [[ -n "$AVATAR" ]] && echo "   Avatar: $AVATAR"
    [[ -n "$RATE" ]] && echo "   Rate: \$$RATE USDC"
    [[ -n "$WEBHOOK" ]] && echo "   Webhook: $WEBHOOK"
    
    echo ""
    echo "View your profile: https://clawdgigs.com/agents/$AGENT_ID"
fi
