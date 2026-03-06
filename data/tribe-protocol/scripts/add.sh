#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

# Parse args
NAME=""
TYPE=""
DISCORD_ID=""
TIER="1"
OWNER=""
RELATIONSHIP=""
BIO=""
TIMEZONE=""
SERVER=""
ROLE=""
TAGS=""
FRAMEWORK=""
MODEL=""
MACHINE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) NAME="$2"; shift 2 ;;
        --type) TYPE="$2"; shift 2 ;;
        --discord-id) DISCORD_ID="$2"; shift 2 ;;
        --tier) TIER="$2"; shift 2 ;;
        --owner) OWNER="$2"; shift 2 ;;
        --relationship) RELATIONSHIP="$2"; shift 2 ;;
        --bio) BIO="$2"; shift 2 ;;
        --timezone) TIMEZONE="$2"; shift 2 ;;
        --server) SERVER="$2"; shift 2 ;;
        --role) ROLE="$2"; shift 2 ;;
        --tag) TAGS="$2"; shift 2 ;;
        --framework) FRAMEWORK="$2"; shift 2 ;;
        --model) MODEL="$2"; shift 2 ;;
        --machine) MACHINE="$2"; shift 2 ;;
        *) echo "❌ Unknown option: $1"; exit 1 ;;
    esac
done

# Validate required
if [ -z "$NAME" ] || [ -z "$TYPE" ] || [ -z "$DISCORD_ID" ]; then
    echo "❌ Required: --name, --type (human|bot), --discord-id"
    echo "Usage: tribe add --name X --type human --discord-id 123 --tier 3"
    exit 1
fi

if [[ "$TYPE" != "human" && "$TYPE" != "bot" ]]; then
    echo "❌ --type must be 'human' or 'bot'"
    exit 1
fi

# Validate discord ID is numeric
validate_discord_id "$DISCORD_ID" || exit 1

# Sanitize all string inputs
NAME="$(sql_escape "$NAME")"
RELATIONSHIP="$(sql_escape "$RELATIONSHIP")"
BIO="$(sql_escape "$BIO")"
TIMEZONE="$(sql_escape "$TIMEZONE")"
SERVER="$(sql_escape "$SERVER")"
ROLE="$(sql_escape "$ROLE")"
FRAMEWORK="$(sql_escape "$FRAMEWORK")"
MODEL="$(sql_escape "$MODEL")"
MACHINE="$(sql_escape "$MACHINE")"

# Check if discord ID already exists
EXISTING=$(db_query "SELECT e.name FROM entities e JOIN platform_ids p ON e.id = p.entity_id WHERE p.platform='discord' AND p.platform_id='$DISCORD_ID';" 2>/dev/null || true)
if [ -n "$EXISTING" ]; then
    echo "❌ Discord ID $DISCORD_ID already registered to: $EXISTING"
    exit 1
fi

# Resolve owner entity ID
OWNER_ID=""
if [ -n "$OWNER" ]; then
    # Try as discord_id first, then name
    OWNER_ID=$(db_query "SELECT entity_id FROM platform_ids WHERE platform='discord' AND platform_id='$OWNER';" 2>/dev/null || true)
    if [ -z "$OWNER_ID" ]; then
        OWNER_ID=$(db_query "SELECT id FROM entities WHERE name='$OWNER' LIMIT 1;" 2>/dev/null || true)
    fi
    if [ -z "$OWNER_ID" ]; then
        echo "⚠️  Owner '$OWNER' not found in DB, skipping owner link"
        OWNER_ID=""
    fi
fi

# Build INSERT
OWNER_CLAUSE="NULL"
[ -n "$OWNER_ID" ] && OWNER_CLAUSE="$OWNER_ID"

BIO_CLAUSE="NULL"
[ -n "$BIO" ] && BIO_CLAUSE="'$BIO'"

REL_CLAUSE="NULL"
[ -n "$RELATIONSHIP" ] && REL_CLAUSE="'$RELATIONSHIP'"

TZ_CLAUSE="NULL"
[ -n "$TIMEZONE" ] && TZ_CLAUSE="'$TIMEZONE'"

db_query "INSERT INTO entities (name, type, trust_tier, status, owner_entity_id, bio, relationship, timezone)
    VALUES ('$NAME', '$TYPE', $TIER, 'active', $OWNER_CLAUSE, $BIO_CLAUSE, $REL_CLAUSE, $TZ_CLAUSE);"

ENTITY_ID=$(db_query "SELECT id FROM entities WHERE name='$NAME' ORDER BY id DESC LIMIT 1;")

# Add platform ID
db_query "INSERT INTO platform_ids (entity_id, platform, platform_id, verified, primary_contact) VALUES ($ENTITY_ID, 'discord', '$DISCORD_ID', 1, 1);"

# Add bot metadata if applicable
if [ "$TYPE" = "bot" ] && ([ -n "$FRAMEWORK" ] || [ -n "$MODEL" ] || [ -n "$MACHINE" ]); then
    FW_CLAUSE="NULL"
    [ -n "$FRAMEWORK" ] && FW_CLAUSE="'$FRAMEWORK'"
    MD_CLAUSE="NULL"
    [ -n "$MODEL" ] && MD_CLAUSE="'$MODEL'"
    MC_CLAUSE="NULL"
    [ -n "$MACHINE" ] && MC_CLAUSE="'$MACHINE'"

    HOST_OWNER_CLAUSE="NULL"
    [ -n "$OWNER_ID" ] && HOST_OWNER_CLAUSE="$OWNER_ID"

    db_query "INSERT INTO bot_metadata (entity_id, framework, model, host_machine, host_owner) VALUES ($ENTITY_ID, $FW_CLAUSE, $MD_CLAUSE, $MC_CLAUSE, $HOST_OWNER_CLAUSE);"
fi

# Add server role
if [ -n "$SERVER" ] && [ -n "$ROLE" ]; then
    db_query "INSERT INTO server_roles (entity_id, server_slug, role) VALUES ($ENTITY_ID, '$SERVER', '$ROLE');"
fi

# Add tags
if [ -n "$TAGS" ]; then
    IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
    for tag in "${TAG_ARRAY[@]}"; do
        tag=$(echo "$tag" | xargs)  # trim whitespace
        db_query "INSERT OR IGNORE INTO entity_tags (entity_id, tag) VALUES ($ENTITY_ID, '$tag');"
    done
fi

# Audit log
db_query "INSERT INTO audit_log (entity_id, action, new_value, reason, changed_by) VALUES ($ENTITY_ID, 'add', 'name=$NAME type=$TYPE tier=$TIER', 'Entity added', 'tribe-cli');"

echo "✅ Added: $NAME ($TYPE) | Tier $TIER ($(tier_label "$TIER")) | discord:$DISCORD_ID"
