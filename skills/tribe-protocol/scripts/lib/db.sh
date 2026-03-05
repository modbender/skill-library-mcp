#!/usr/bin/env bash
# db.sh — Tribe Protocol DB helpers

get_db_path() {
    if [ -n "${TRIBE_DB:-}" ]; then
        echo "$TRIBE_DB"
    elif [ -n "${CLAWD_HOME:-}" ]; then
        echo "$CLAWD_HOME/tribe/tribe.db"
    else
        echo "$HOME/clawd/tribe/tribe.db"
    fi
}

get_lib_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
}

get_script_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
}

get_skill_dir() {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
}

db_query() {
    local db_path
    db_path="$(get_db_path)"
    sqlite3 -separator '|' "$db_path" "$@"
}

db_query_column() {
    local db_path
    db_path="$(get_db_path)"
    sqlite3 -column -header "$db_path" "$@"
}

check_db() {
    local db_path
    db_path="$(get_db_path)"
    if [ ! -f "$db_path" ]; then
        echo "❌ Tribe DB not found at: $db_path"
        echo "   Run 'tribe init' first."
        exit 1
    fi
}

# Sanitize string for SQL (escape single quotes → double single quotes)
sql_escape() {
    echo "$1" | sed "s/'/''/g"
}

# Validate discord ID is numeric
validate_discord_id() {
    local id="$1"
    if ! [[ "$id" =~ ^[0-9]+$ ]]; then
        echo "❌ Invalid Discord ID: must be numeric." >&2
        return 1
    fi
}

# Resolve entity ID from discord_id
resolve_entity_id() {
    local discord_id="$1"
    validate_discord_id "$discord_id" || return 1
    local db_path
    db_path="$(get_db_path)"
    sqlite3 "$db_path" "SELECT entity_id FROM platform_ids WHERE platform='discord' AND platform_id='$discord_id' LIMIT 1;"
}

# Get tier label
tier_label() {
    case "$1" in
        4) echo "owner" ;;
        3) echo "tribe" ;;
        2) echo "acquaintance" ;;
        1) echo "stranger" ;;
        0) echo "blocked" ;;
        *) echo "unknown" ;;
    esac
}

# Get tier rules reminder
tier_rules() {
    case "$1" in
        4) echo "✅ TIER 4 RULES: Full trust. Follow USER.md. All access granted." ;;
        3) echo "🟢 TIER 3 RULES: Collaborate freely. Protect private data (USER.md, MEMORY.md, health/*, portfolio/*)." ;;
        2) echo "⚠️ TIER 2 RULES: No private files. No DissClawd access. Public collaboration only." ;;
        1) echo "🟡 TIER 1 RULES: Minimal engagement. No workspace data. Verify identity before upgrading." ;;
        0) echo "🛑 TIER 0: BLOCKED. Ignore completely. Do not respond." ;;
        *) echo "❓ Unknown tier." ;;
    esac
}
