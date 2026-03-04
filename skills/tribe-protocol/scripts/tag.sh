#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"
check_db

DISCORD_ID="${1:-}"
ACTION="${2:-}"
TAG="${3:-}"

if [ -z "$DISCORD_ID" ] || [ -z "$ACTION" ]; then
    echo "Usage: tribe tag <discord_id> add <tag>"
    echo "       tribe tag <discord_id> remove <tag>"
    echo "       tribe tag <discord_id> list"
    exit 1
fi

ENTITY_ID=$(resolve_entity_id "$DISCORD_ID")
if [ -z "$ENTITY_ID" ]; then
    echo "❌ Entity not found for discord:$DISCORD_ID"
    exit 1
fi

NAME=$(db_query "SELECT name FROM entities WHERE id=$ENTITY_ID;")

case "$ACTION" in
    add)
        if [ -z "$TAG" ]; then
            echo "❌ Tag name required"
            exit 1
        fi
        db_query "INSERT OR IGNORE INTO entity_tags (entity_id, tag) VALUES ($ENTITY_ID, '$TAG');"
        db_query "INSERT INTO audit_log (entity_id, action, new_value, changed_by) VALUES ($ENTITY_ID, 'tag-add', '$TAG', 'tribe-cli');"
        echo "✅ Tagged $NAME with '$TAG'"
        ;;
    remove)
        if [ -z "$TAG" ]; then
            echo "❌ Tag name required"
            exit 1
        fi
        db_query "DELETE FROM entity_tags WHERE entity_id=$ENTITY_ID AND tag='$TAG';"
        db_query "INSERT INTO audit_log (entity_id, action, old_value, changed_by) VALUES ($ENTITY_ID, 'tag-remove', '$TAG', 'tribe-cli');"
        echo "✅ Removed tag '$TAG' from $NAME"
        ;;
    list)
        TAGS=$(db_query "SELECT tag FROM entity_tags WHERE entity_id=$ENTITY_ID ORDER BY tag;" | tr '\n' ', ' | sed 's/,$//')
        if [ -z "$TAGS" ]; then
            echo "🏷️  $NAME has no tags"
        else
            echo "🏷️  $NAME tags: $TAGS"
        fi
        ;;
    *)
        echo "❌ Unknown action: $ACTION (use add, remove, or list)"
        exit 1
        ;;
esac
