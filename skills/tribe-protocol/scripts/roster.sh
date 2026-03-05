#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

# Parse filters
SERVER=""
ROLE=""
TIER=""
TYPE=""
TAG=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --server) SERVER="$2"; shift 2 ;;
        --role) ROLE="$2"; shift 2 ;;
        --tier) TIER="$2"; shift 2 ;;
        --type) TYPE="$2"; shift 2 ;;
        --tag) TAG="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Build WHERE clause
WHERE="WHERE e.status='active'"
[ -n "$TIER" ] && WHERE="$WHERE AND e.trust_tier=$TIER"
[ -n "$TYPE" ] && WHERE="$WHERE AND e.type='$TYPE'"

# Server/role filter requires join
JOIN=""
if [ -n "$SERVER" ] || [ -n "$ROLE" ]; then
    JOIN="JOIN server_roles sr2 ON e.id = sr2.entity_id"
    [ -n "$SERVER" ] && WHERE="$WHERE AND sr2.server_slug='$SERVER'"
    [ -n "$ROLE" ] && WHERE="$WHERE AND sr2.role='$ROLE'"
fi

# Tag filter
if [ -n "$TAG" ]; then
    JOIN="$JOIN JOIN entity_tags et2 ON e.id = et2.entity_id"
    WHERE="$WHERE AND et2.tag='$TAG'"
fi

QUERY="SELECT DISTINCT e.id, e.name, e.type, e.trust_tier, e.status,
    COALESCE(owner.name, '-') AS owner,
    COALESCE(GROUP_CONCAT(DISTINCT sr.server_slug || '/' || sr.role), '-') AS servers,
    COALESCE(GROUP_CONCAT(DISTINCT et.tag), '-') AS tags
FROM entities e
LEFT JOIN entities owner ON e.owner_entity_id = owner.id
LEFT JOIN server_roles sr ON e.id = sr.entity_id
LEFT JOIN entity_tags et ON e.id = et.entity_id
$JOIN
$WHERE
GROUP BY e.id
ORDER BY e.trust_tier DESC, e.type, e.name;"

RESULTS=$(db_query "$QUERY" 2>/dev/null || true)

if [ -z "$RESULTS" ]; then
    echo "📋 No entities found matching filters."
    exit 0
fi

echo "📋 Tribe Roster"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "%-12s %-6s %-20s %-10s %-25s %s\n" "Name" "Type" "Tier" "Owner" "Servers" "Tags"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

while IFS='|' read -r ID NAME_V TYPE_V TIER_V STATUS_V OWNER_V SERVERS_V TAGS_V; do
    TIER_LABEL="T${TIER_V} ($(tier_label "$TIER_V"))"
    printf "%-12s %-6s %-20s %-10s %-25s %s\n" "$NAME_V" "$TYPE_V" "$TIER_LABEL" "$OWNER_V" "$SERVERS_V" "$TAGS_V"
done <<< "$RESULTS"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$(echo "$RESULTS" | wc -l | xargs)
echo "Total: $TOTAL entities"
