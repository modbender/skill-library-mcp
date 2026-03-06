#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

COMMAND="${1:-}"
shift 2>/dev/null || true

case "$COMMAND" in
    grant)
        DISCORD_ID="${1:-}"
        shift 2>/dev/null || true
        SERVER=""
        CHANNEL=""
        CHANNEL_NAME=""
        READ_ONLY=0
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --server) SERVER="$2"; shift 2 ;;
                --channel) CHANNEL="$2"; shift 2 ;;
                --channel-name) CHANNEL_NAME="$2"; shift 2 ;;
                --read-only) READ_ONLY=1; shift ;;
                *) shift ;;
            esac
        done

        if [ -z "$DISCORD_ID" ] || [ -z "$SERVER" ]; then
            echo "Usage: tribe grant <discord_id> --server <slug> [--channel <id>] [--read-only]"
            exit 1
        fi

        ENTITY_ID=$(resolve_entity_id "$DISCORD_ID")
        if [ -z "$ENTITY_ID" ]; then
            echo "❌ Entity not found for discord:$DISCORD_ID"
            exit 1
        fi

        NAME=$(db_query "SELECT name FROM entities WHERE id=$ENTITY_ID;")
        CAN_WRITE=$((1 - READ_ONLY))
        CHAN_CLAUSE="NULL"
        [ -n "$CHANNEL" ] && CHAN_CLAUSE="'$CHANNEL'"
        CHAN_NAME_CLAUSE="NULL"
        [ -n "$CHANNEL_NAME" ] && CHAN_NAME_CLAUSE="'$CHANNEL_NAME'"

        db_query "INSERT OR REPLACE INTO channel_access (entity_id, server_slug, channel_id, channel_name, can_read, can_write)
            VALUES ($ENTITY_ID, '$SERVER', $CHAN_CLAUSE, $CHAN_NAME_CLAUSE, 1, $CAN_WRITE);"

        db_query "INSERT INTO audit_log (entity_id, action, new_value, changed_by)
            VALUES ($ENTITY_ID, 'grant-access', 'server=$SERVER channel=${CHANNEL:-all} write=$CAN_WRITE', 'tribe-cli');"

        SCOPE="${CHANNEL:-all channels}"
        PERM="read/write"
        [ "$READ_ONLY" = "1" ] && PERM="read-only"
        echo "✅ Granted $NAME $PERM access to $SERVER ($SCOPE)"
        ;;

    revoke)
        DISCORD_ID="${1:-}"
        shift 2>/dev/null || true
        SERVER=""
        CHANNEL=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --server) SERVER="$2"; shift 2 ;;
                --channel) CHANNEL="$2"; shift 2 ;;
                *) shift ;;
            esac
        done

        if [ -z "$DISCORD_ID" ] || [ -z "$SERVER" ]; then
            echo "Usage: tribe revoke <discord_id> --server <slug> [--channel <id>]"
            exit 1
        fi

        ENTITY_ID=$(resolve_entity_id "$DISCORD_ID")
        if [ -z "$ENTITY_ID" ]; then
            echo "❌ Entity not found for discord:$DISCORD_ID"
            exit 1
        fi

        NAME=$(db_query "SELECT name FROM entities WHERE id=$ENTITY_ID;")

        if [ -n "$CHANNEL" ]; then
            db_query "DELETE FROM channel_access WHERE entity_id=$ENTITY_ID AND server_slug='$SERVER' AND channel_id='$CHANNEL';"
        else
            db_query "DELETE FROM channel_access WHERE entity_id=$ENTITY_ID AND server_slug='$SERVER';"
        fi

        db_query "INSERT INTO audit_log (entity_id, action, old_value, changed_by)
            VALUES ($ENTITY_ID, 'revoke-access', 'server=$SERVER channel=${CHANNEL:-all}', 'tribe-cli');"

        echo "✅ Revoked $NAME access from $SERVER (${CHANNEL:-all channels})"
        ;;

    data-add)
        DA_TIER=""
        DA_PATTERN=""
        DA_DESC=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --tier) DA_TIER="$2"; shift 2 ;;
                --pattern) DA_PATTERN="$2"; shift 2 ;;
                --desc) DA_DESC="$2"; shift 2 ;;
                *) shift ;;
            esac
        done

        if [ -z "$DA_TIER" ] || [ -z "$DA_PATTERN" ]; then
            echo "Usage: tribe data-add --tier <0-4> --pattern 'health/*' [--desc 'Description']"
            exit 1
        fi

        DA_PATTERN="$(sql_escape "$DA_PATTERN")"
        DA_DESC="$(sql_escape "$DA_DESC")"

        db_query "INSERT INTO data_access (min_tier, resource_pattern, allowed, description) VALUES ($DA_TIER, '$DA_PATTERN', 1, '$DA_DESC');"
        echo "✅ Data access rule added: tier $DA_TIER+ can access '$DA_PATTERN'"
        ;;

    data-remove)
        DA_PATTERN=""
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --pattern) DA_PATTERN="$2"; shift 2 ;;
                *) shift ;;
            esac
        done

        if [ -z "$DA_PATTERN" ]; then
            echo "Usage: tribe data-remove --pattern 'health/*'"
            exit 1
        fi

        DA_PATTERN="$(sql_escape "$DA_PATTERN")"
        db_query "DELETE FROM data_access WHERE resource_pattern='$DA_PATTERN';"
        echo "✅ Data access rule removed: '$DA_PATTERN'"
        ;;

    data-list)
        RULES=$(db_query_column "SELECT min_tier, resource_pattern, description FROM data_access ORDER BY min_tier DESC, resource_pattern;" 2>/dev/null || true)
        if [ -z "$RULES" ]; then
            echo "No data access rules configured."
        else
            echo "📋 Data access rules:"
            echo "$RULES"
        fi
        ;;

    *)
        echo "Channel access:"
        echo "  tribe grant <discord_id> --server <slug> [--channel <id>] [--read-only]"
        echo "  tribe revoke <discord_id> --server <slug> [--channel <id>]"
        echo ""
        echo "Data access:"
        echo "  tribe data-add --tier <0-4> --pattern 'path/*' [--desc 'Description']"
        echo "  tribe data-remove --pattern 'path/*'"
        echo "  tribe data-list"
        exit 1
        ;;
esac
