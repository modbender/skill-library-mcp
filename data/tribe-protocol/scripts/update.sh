#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

COMMAND="${1:-}"
shift 2>/dev/null || true

case "$COMMAND" in
    set-tier)
        DISCORD_ID="${1:-}"
        NEW_TIER="${2:-}"
        shift 2 2>/dev/null || true
        REASON=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --reason) REASON="$2"; shift 2 ;;
                *) shift ;;
            esac
        done

        if [ -z "$DISCORD_ID" ] || [ -z "$NEW_TIER" ]; then
            echo "Usage: tribe set-tier <discord_id> <tier> [--reason \"...\"]"
            exit 1
        fi

        ENTITY_ID=$(resolve_entity_id "$DISCORD_ID")
        if [ -z "$ENTITY_ID" ]; then
            echo "❌ Entity not found for discord:$DISCORD_ID"
            exit 1
        fi

        OLD_TIER=$(db_query "SELECT trust_tier FROM entities WHERE id=$ENTITY_ID;")
        NAME=$(db_query "SELECT name FROM entities WHERE id=$ENTITY_ID;")

        db_query "UPDATE entities SET trust_tier=$NEW_TIER, updated_at=datetime('now') WHERE id=$ENTITY_ID;"

        REASON_CLAUSE="NULL"
        [ -n "$REASON" ] && REASON_CLAUSE="'$(echo "$REASON" | sed "s/'/''/g")'"

        db_query "INSERT INTO audit_log (entity_id, action, old_value, new_value, reason, changed_by) VALUES ($ENTITY_ID, 'set-tier', 'tier=$OLD_TIER', 'tier=$NEW_TIER', $REASON_CLAUSE, 'tribe-cli');"

        echo "✅ $NAME: Tier $OLD_TIER ($(tier_label "$OLD_TIER")) → Tier $NEW_TIER ($(tier_label "$NEW_TIER"))"
        [ -n "$REASON" ] && echo "   Reason: $REASON"
        ;;

    set-status)
        DISCORD_ID="${1:-}"
        NEW_STATUS="${2:-}"
        shift 2 2>/dev/null || true
        REASON=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --reason) REASON="$2"; shift 2 ;;
                *) shift ;;
            esac
        done

        if [ -z "$DISCORD_ID" ] || [ -z "$NEW_STATUS" ]; then
            echo "Usage: tribe set-status <discord_id> <status> [--reason \"...\"]"
            exit 1
        fi

        ENTITY_ID=$(resolve_entity_id "$DISCORD_ID")
        if [ -z "$ENTITY_ID" ]; then
            echo "❌ Entity not found for discord:$DISCORD_ID"
            exit 1
        fi

        OLD_STATUS=$(db_query "SELECT status FROM entities WHERE id=$ENTITY_ID;")
        NAME=$(db_query "SELECT name FROM entities WHERE id=$ENTITY_ID;")

        db_query "UPDATE entities SET status='$NEW_STATUS', updated_at=datetime('now') WHERE id=$ENTITY_ID;"

        REASON_CLAUSE="NULL"
        [ -n "$REASON" ] && REASON_CLAUSE="'$(echo "$REASON" | sed "s/'/''/g")'"

        db_query "INSERT INTO audit_log (entity_id, action, old_value, new_value, reason, changed_by) VALUES ($ENTITY_ID, 'set-status', 'status=$OLD_STATUS', 'status=$NEW_STATUS', $REASON_CLAUSE, 'tribe-cli');"

        echo "✅ $NAME: $OLD_STATUS → $NEW_STATUS"
        [ -n "$REASON" ] && echo "   Reason: $REASON"
        ;;

    *)
        echo "Usage: tribe set-tier <discord_id> <tier> [--reason \"...\"]"
        echo "       tribe set-status <discord_id> <status> [--reason \"...\"]"
        exit 1
        ;;
esac
