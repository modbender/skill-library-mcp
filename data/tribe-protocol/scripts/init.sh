#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/db.sh"

# Defaults
BOT_NAME=""
BOT_DISCORD_ID=""
HUMAN_NAME=""
HUMAN_DISCORD_ID=""
DB_PATH=""
SERVERS=()

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --bot-name) BOT_NAME="$2"; shift 2 ;;
        --bot-discord-id) BOT_DISCORD_ID="$2"; shift 2 ;;
        --human-name) HUMAN_NAME="$2"; shift 2 ;;
        --human-discord-id) HUMAN_DISCORD_ID="$2"; shift 2 ;;
        --db-path) DB_PATH="$2"; shift 2 ;;
        --server) SERVERS+=("$2"); shift 2 ;;
        *) echo "❌ Unknown option: $1"; exit 1 ;;
    esac
done

# Check sqlite3
if ! command -v sqlite3 &>/dev/null; then
    echo "❌ sqlite3 is required but not found. Install it first."
    exit 1
fi

# Set DB path
if [ -n "$DB_PATH" ]; then
    export TRIBE_DB="$DB_PATH"
fi
DB_FILE="$(get_db_path)"
DB_DIR="$(dirname "$DB_FILE")"

# Check if already initialized
if [ -f "$DB_FILE" ]; then
    echo "⚠️  Tribe DB already exists at: $DB_FILE"
    echo "   Delete it manually to re-initialize."
    exit 1
fi

# Create directory
mkdir -p "$DB_DIR"

echo "🏛️  Initializing Tribe Protocol..."
echo "   DB: $DB_FILE"

# Create schema
LIB_DIR="$(get_lib_dir)"
sqlite3 "$DB_FILE" < "$LIB_DIR/schema.sql"

# Seed default data access rules (universal — not bot-specific)
# These are safe defaults; customize post-init with `tribe access` command
sqlite3 "$DB_FILE" <<'EOF'
INSERT INTO data_access (min_tier, resource_pattern, allowed, description) VALUES
(4, 'USER.md', 1, 'Only owner sees USER.md'),
(4, 'MEMORY.md', 1, 'Only owner sees MEMORY.md'),
(4, 'memory/*', 1, 'Only owner sees daily logs'),
(4, '.env', 1, 'Only owner sees env files'),
(3, 'projects/*', 1, 'Tribe can access projects'),
(3, 'research/*', 1, 'Tribe can access research'),
(2, 'public/*', 1, 'Acquaintances see public stuff');
EOF
# NOTE: Bot-specific paths (health/*, portfolio/*, calendar, etc.)
# should be added post-init: tribe access --add --tier 4 --pattern 'health/*'

# Seed bot entity if provided
if [ -n "$BOT_NAME" ] && [ -n "$BOT_DISCORD_ID" ]; then
    sqlite3 "$DB_FILE" "INSERT INTO entities (name, type, trust_tier, status, relationship) VALUES ('$BOT_NAME', 'bot', 4, 'active', 'self');"
    BOT_ID=$(sqlite3 "$DB_FILE" "SELECT id FROM entities WHERE name='$BOT_NAME';")
    sqlite3 "$DB_FILE" "INSERT INTO platform_ids (entity_id, platform, platform_id, verified, primary_contact) VALUES ($BOT_ID, 'discord', '$BOT_DISCORD_ID', 1, 1);"
    echo "   ✅ Bot entity created: $BOT_NAME (Tier 4)"
fi

# Seed human owner if provided
if [ -n "$HUMAN_NAME" ] && [ -n "$HUMAN_DISCORD_ID" ]; then
    sqlite3 "$DB_FILE" "INSERT INTO entities (name, type, trust_tier, status, relationship) VALUES ('$HUMAN_NAME', 'human', 4, 'active', 'owner');"
    HUMAN_ID=$(sqlite3 "$DB_FILE" "SELECT id FROM entities WHERE name='$HUMAN_NAME';")
    sqlite3 "$DB_FILE" "INSERT INTO platform_ids (entity_id, platform, platform_id, verified, primary_contact) VALUES ($HUMAN_ID, 'discord', '$HUMAN_DISCORD_ID', 1, 1);"

    # Link bot to owner if both exist
    if [ -n "${BOT_ID:-}" ]; then
        sqlite3 "$DB_FILE" "UPDATE entities SET owner_entity_id=$HUMAN_ID WHERE id=$BOT_ID;"
    fi
    echo "   ✅ Owner entity created: $HUMAN_NAME (Tier 4)"
fi

# Seed server roles if --server provided (format: slug:guild_id e.g. electrons:000000000000000008)
for SERVER_ENTRY in "${SERVERS[@]}"; do
    IFS=':' read -r S_SLUG S_GUILD_ID <<< "$SERVER_ENTRY"
    if [ -n "$S_SLUG" ]; then
        GUILD_CLAUSE="NULL"
        [ -n "${S_GUILD_ID:-}" ] && GUILD_CLAUSE="'$S_GUILD_ID'"
        # Add bot to server
        if [ -n "${BOT_ID:-}" ]; then
            sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO server_roles (entity_id, server_slug, server_id, role) VALUES ($BOT_ID, '$S_SLUG', $GUILD_CLAUSE, 'bot');"
        fi
        # Add owner to server
        if [ -n "${HUMAN_ID:-}" ]; then
            sqlite3 "$DB_FILE" "INSERT OR IGNORE INTO server_roles (entity_id, server_slug, server_id, role) VALUES ($HUMAN_ID, '$S_SLUG', $GUILD_CLAUSE, 'admin');"
        fi
        echo "   ✅ Server added: $S_SLUG (guild: ${S_GUILD_ID:-unknown})"
    fi
done

# Audit log
sqlite3 "$DB_FILE" "INSERT INTO audit_log (action, new_value, reason, changed_by) VALUES ('init', 'schema_v1', 'Initial database setup', '${BOT_NAME:-system}');"

# Generate TRIBE.md from template
SKILL_DIR="$(get_skill_dir)"
TEMPLATE="$SKILL_DIR/templates/TRIBE.md.template"
if [ -f "$TEMPLATE" ]; then
    WORKSPACE="${CLAWD_HOME:-$HOME/clawd}"
    TRIBE_MD="$WORKSPACE/TRIBE.md"
    sed -e "s|{{HUMAN_DISCORD_ID}}|${HUMAN_DISCORD_ID:-OWNER_DISCORD_ID}|g" \
        -e "s|{{SKILL_DIR}}|$SKILL_DIR|g" \
        -e "s|{{DB_PATH}}|$DB_FILE|g" \
        "$TEMPLATE" > "$TRIBE_MD"
    echo "   ✅ TRIBE.md generated at: $TRIBE_MD"
fi

echo ""
echo "🎉 Tribe Protocol initialized!"
echo ""
echo "📋 Add this to your AGENTS.md:"
echo "   $(cat "$SKILL_DIR/templates/AGENTS.md.snippet" 2>/dev/null || echo '**Non-owner messages → ALWAYS check TRIBE.md first (mandatory trust lookup).**')"
echo ""
echo "Next steps:"
echo "  tribe add --name <name> --type human --discord-id <id> --tier 3"
echo "  tribe lookup <discord_id>"
