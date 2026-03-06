#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

# Parse args
ENTITY_DISCORD=""
LIMIT="20"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --entity) ENTITY_DISCORD="$2"; shift 2 ;;
        --limit) LIMIT="$2"; shift 2 ;;
        *) shift ;;
    esac
done

WHERE=""
if [ -n "$ENTITY_DISCORD" ]; then
    ENTITY_ID=$(resolve_entity_id "$ENTITY_DISCORD")
    if [ -z "$ENTITY_ID" ]; then
        echo "❌ Entity not found for discord:$ENTITY_DISCORD"
        exit 1
    fi
    WHERE="WHERE a.entity_id=$ENTITY_ID"
fi

RESULTS=$(db_query "SELECT a.created_at, COALESCE(e.name, 'system'), a.action, COALESCE(a.old_value, '-'), COALESCE(a.new_value, '-'), COALESCE(a.reason, '-'), a.changed_by
    FROM audit_log a
    LEFT JOIN entities e ON a.entity_id = e.id
    $WHERE
    ORDER BY a.created_at DESC
    LIMIT $LIMIT;" 2>/dev/null || true)

if [ -z "$RESULTS" ]; then
    echo "📜 No audit entries found."
    exit 0
fi

echo "📜 Audit Log (last $LIMIT entries)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

while IFS='|' read -r TS NAME_V ACTION OLD NEW REASON BY; do
    echo "[$TS] $NAME_V: $ACTION"
    [ "$OLD" != "-" ] && echo "   Old: $OLD"
    [ "$NEW" != "-" ] && echo "   New: $NEW"
    [ "$REASON" != "-" ] && echo "   Reason: $REASON"
    echo "   By: $BY"
    echo ""
done <<< "$RESULTS"
