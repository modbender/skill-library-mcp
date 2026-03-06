#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

# Parse args
DISCORD_ID=""
NAME=""
TAG=""
SERVER=""
TIER=""
TYPE=""

if [[ $# -gt 0 ]] && [[ "$1" != --* ]]; then
    DISCORD_ID="$1"
    shift
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --name) NAME="$2"; shift 2 ;;
        --tag) TAG="$2"; shift 2 ;;
        --server) SERVER="$2"; shift 2 ;;
        --tier) TIER="$2"; shift 2 ;;
        --type) TYPE="$2"; shift 2 ;;
        *) DISCORD_ID="${DISCORD_ID:-$1}"; shift ;;
    esac
done

# Build query based on input
if [ -n "$DISCORD_ID" ]; then
    # Primary lookup by discord ID
    # Validate discord ID is numeric to prevent SQL injection
    if ! [[ "$DISCORD_ID" =~ ^[0-9]+$ ]]; then
        echo "❌ Invalid Discord ID: must be numeric."
        exit 1
    fi
    RESULT=$(db_query "SELECT e.id, e.name, e.type, e.trust_tier, e.status, e.relationship, e.bio,
        owner.name, e.timezone
        FROM entities e
        LEFT JOIN entities owner ON e.owner_entity_id = owner.id
        JOIN platform_ids p ON e.id = p.entity_id
        WHERE p.platform='discord' AND p.platform_id='$DISCORD_ID'
        LIMIT 1;" 2>/dev/null || true)

    if [ -z "$RESULT" ]; then
        echo "❌ Unknown entity (discord:$DISCORD_ID). Treat as Tier 1 (stranger)."
        echo "   $(tier_rules 1)"
        exit 0
    fi

    IFS='|' read -r ID NAME_V TYPE_V TIER_V STATUS_V REL_V BIO_V OWNER_V TZ_V <<< "$RESULT"

    # Get platforms
    PLATFORMS=$(db_query "SELECT platform || ':' || platform_id FROM platform_ids WHERE entity_id=$ID;" | tr '\n' ', ' | sed 's/,$//')

    # Get server roles
    SERVERS=$(db_query "SELECT server_slug || '/' || role FROM server_roles WHERE entity_id=$ID;" | tr '\n' ', ' | sed 's/,$//')

    # Get tags
    TAGS=$(db_query "SELECT tag FROM entity_tags WHERE entity_id=$ID;" | tr '\n' ', ' | sed 's/,$//')

    # Format output
    echo "🔍 $NAME_V | $TYPE_V | Tier $TIER_V ($(tier_label "$TIER_V")) | Status: $STATUS_V"
    if [ -n "$OWNER_V" ] && [ -n "$REL_V" ]; then
        echo "   Owner: $OWNER_V | Relationship: $REL_V"
    elif [ -n "$OWNER_V" ]; then
        echo "   Owner: $OWNER_V"
    elif [ -n "$REL_V" ]; then
        echo "   Relationship: $REL_V"
    fi
    [ -n "$BIO_V" ] && echo "   Bio: $BIO_V"
    [ -n "$PLATFORMS" ] && echo "   Platforms: $PLATFORMS"
    [ -n "$SERVERS" ] && echo "   Servers: $SERVERS"
    [ -n "$TAGS" ] && echo "   Tags: $TAGS"
    [ -n "$TZ_V" ] && echo "   Timezone: $TZ_V"
    echo "   $(tier_rules "$TIER_V")"

elif [ -n "$NAME" ]; then
    # Sanitize name input (strip quotes/semicolons)
    SAFE_NAME="${NAME//[\'\";\`]/}"
    RESULTS=$(db_query "SELECT e.id, e.name, e.type, e.trust_tier, e.status
        FROM entities e WHERE e.name LIKE '%$SAFE_NAME%';" 2>/dev/null || true)
    if [ -z "$RESULTS" ]; then
        echo "❌ No entities found matching name: $NAME"
        exit 0
    fi
    echo "🔍 Entities matching '$NAME':"
    while IFS='|' read -r ID NAME_V TYPE_V TIER_V STATUS_V; do
        echo "   $NAME_V | $TYPE_V | Tier $TIER_V ($(tier_label "$TIER_V")) | $STATUS_V"
    done <<< "$RESULTS"

elif [ -n "$TAG" ]; then
    SAFE_TAG="${TAG//[\'\";\`]/}"
    RESULTS=$(db_query "SELECT e.id, e.name, e.type, e.trust_tier, e.status
        FROM entities e JOIN entity_tags et ON e.id = et.entity_id
        WHERE et.tag='$SAFE_TAG';" 2>/dev/null || true)
    if [ -z "$RESULTS" ]; then
        echo "❌ No entities found with tag: $TAG"
        exit 0
    fi
    echo "🏷️  Entities tagged '$TAG':"
    while IFS='|' read -r ID NAME_V TYPE_V TIER_V STATUS_V; do
        echo "   $NAME_V | $TYPE_V | Tier $TIER_V ($(tier_label "$TIER_V")) | $STATUS_V"
    done <<< "$RESULTS"

elif [ -n "$SERVER" ]; then
    SAFE_SERVER="${SERVER//[\'\";\`]/}"
    RESULTS=$(db_query "SELECT e.name, e.type, e.trust_tier, sr.role
        FROM entities e JOIN server_roles sr ON e.id = sr.entity_id
        WHERE sr.server_slug='$SAFE_SERVER';" 2>/dev/null || true)
    if [ -z "$RESULTS" ]; then
        echo "❌ No entities found on server: $SERVER"
        exit 0
    fi
    echo "🖥️  Entities on '$SERVER':"
    while IFS='|' read -r NAME_V TYPE_V TIER_V ROLE_V; do
        echo "   $NAME_V | $TYPE_V | Tier $TIER_V ($(tier_label "$TIER_V")) | Role: $ROLE_V"
    done <<< "$RESULTS"

elif [ -n "$TIER" ]; then
    RESULTS=$(db_query "SELECT e.name, e.type, e.trust_tier, e.status
        FROM entities e WHERE e.trust_tier=$TIER;" 2>/dev/null || true)
    if [ -z "$RESULTS" ]; then
        echo "❌ No entities at tier $TIER"
        exit 0
    fi
    echo "🔍 Tier $TIER ($(tier_label "$TIER")) entities:"
    while IFS='|' read -r NAME_V TYPE_V TIER_V STATUS_V; do
        echo "   $NAME_V | $TYPE_V | $STATUS_V"
    done <<< "$RESULTS"

elif [ -n "$TYPE" ]; then
    RESULTS=$(db_query "SELECT e.name, e.type, e.trust_tier, e.status
        FROM entities e WHERE e.type='$TYPE';" 2>/dev/null || true)
    if [ -z "$RESULTS" ]; then
        echo "❌ No ${TYPE}s found"
        exit 0
    fi
    echo "🔍 All ${TYPE}s:"
    while IFS='|' read -r NAME_V TYPE_V TIER_V STATUS_V; do
        echo "   $NAME_V | Tier $TIER_V ($(tier_label "$TIER_V")) | $STATUS_V"
    done <<< "$RESULTS"

else
    echo "Usage: tribe lookup <discord_id>"
    echo "       tribe lookup --name <name>"
    echo "       tribe lookup --tag <tag>"
    echo "       tribe lookup --server <slug>"
    echo "       tribe lookup --tier <0-4>"
    echo "       tribe lookup --type <human|bot>"
    exit 1
fi
