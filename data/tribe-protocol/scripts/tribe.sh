#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMAND="${1:-help}"
shift 2>/dev/null || true

case "$COMMAND" in
    init|lookup|add|update|set-tier|set-status|access|grant|revoke|data-add|data-remove|data-list|tag|roster|log|export|stats|help)
        # Map subcommands to scripts
        case "$COMMAND" in
            set-tier|set-status) exec "$SCRIPT_DIR/update.sh" "$COMMAND" "$@" ;;
            grant|revoke|data-add|data-remove|data-list) exec "$SCRIPT_DIR/access.sh" "$COMMAND" "$@" ;;
            *) exec "$SCRIPT_DIR/${COMMAND}.sh" "$@" ;;
        esac
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        echo "Usage: tribe <command> [args]"
        echo ""
        echo "Commands:"
        echo "  init        Initialize tribe database"
        echo "  lookup      Look up an entity by discord_id, name, or tag"
        echo "  add         Add a new entity"
        echo "  set-tier    Update an entity's trust tier"
        echo "  set-status  Update an entity's status"
        echo "  grant       Grant channel access"
        echo "  revoke      Revoke channel access"
        echo "  data-add    Add a data access rule (tier-based file access)"
        echo "  data-remove Remove a data access rule"
        echo "  data-list   List all data access rules"
        echo "  tag         Manage entity tags"
        echo "  roster      List all entities"
        echo "  log         View audit trail"
        echo "  export      Export DB to markdown"
        echo "  stats       Quick DB summary"
        exit 1
        ;;
esac
