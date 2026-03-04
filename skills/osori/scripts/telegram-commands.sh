#!/usr/bin/env bash
# Telegram bot command handler for osori
# Usage: telegram-commands.sh <command> [args...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY_FILE="${OSORI_REGISTRY:-$HOME/.openclaw/osori.json}"

# Note: each cmd_* handler calls load_registry() internally.
# No upfront load needed — avoids duplicate I/O and backup creation.

show_help() {
    cat << 'EOF'
🦦 *Osori Bot Commands*

/list [root] — Show all projects (optionally filter by root)
/status [root] — Check project statuses (optionally filter by root)
/find <name> [root|--root <root>] — Find a project path (optional root scope)
/switch <name> [root|--root <root>] [--index <n>] — Switch to project & load context (multi-match selection)
/fingerprints [name] [--root <root>] — Show repo/commit/PR/issue fingerprints
/doctor [--fix] [--dry-run] [--yes] [--json] — Registry health check (preview-first)
/list-roots — List roots, labels, paths, project counts
/root-add <key> [label] — Add/update root
/root-path-add <key> <path> — Add discovery path to root
/root-path-remove <key> <path> — Remove discovery path from root
/root-set-label <key> <label> — Update root label
/root-remove <key> [--reassign <target>] [--force] — Safely remove root
/alias-add <alias> <project> — Add alias for project
/alias-remove <alias> — Remove alias
/favorites — Show favorite projects
/favorite-add <project> — Mark project as favorite
/favorite-remove <project> — Unmark favorite
/entire-status <project> [root|--root <root>] — Show Entire status in project
/entire-enable <project> [root|--root <root>] [--agent <name>] [--strategy <name>] — Enable Entire in project
/entire-rewind-list <project> [root|--root <root>] — List Entire rewind points (JSON)
/add <path> — Add project to registry
/remove <name> — Remove project from registry
/scan <path> [root] — Scan directory for projects (optional root key)
/help — Show this help

*Examples:*
`/list work`
`/status personal`
`/find agent-avengers work`
`/switch Tesella --root personal`
`/switch Tesella --root personal --index 1`
`/fingerprints Tesella --root personal`
`/doctor --fix`
`/list-roots`
`/root-add work Work`
`/root-path-add work /path/to/workspace`
`/root-remove work --reassign default`
`/alias-add rh RunnersHeart`
`/favorites`
`/entire-status osori`
`/entire-enable osori --agent claude-code --strategy manual-commit`
`/scan /path/to/workspace work`
EOF
}

cmd_list() {
    local root_filter="${1:-}"
    OSORI_ROOT_FILTER="$root_filter" OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" \
      python3 "$SCRIPT_DIR/list_handler.py"
}

cmd_status() {
    local root_filter="${1:-}"
    OSORI_ROOT_FILTER="$root_filter" OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" \
      python3 "$SCRIPT_DIR/status_handler.py"
}

cmd_find() {
    local name=""
    local root_filter=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --root)
                root_filter="${2:-}"
                shift 2
                ;;
            *)
                if [[ -z "$name" ]]; then
                    name="$1"
                elif [[ -z "$root_filter" ]]; then
                    root_filter="$1"
                fi
                shift
                ;;
        esac
    done

    [[ -z "$name" ]] && { echo "❌ Usage: /find <project-name> [root|--root <root>]"; exit 1; }

    OSORI_NAME="$name" OSORI_ROOT_FILTER="$root_filter" OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" \
      python3 "$SCRIPT_DIR/find_handler.py"
}

cmd_switch() {
    local name=""
    local root_filter=""
    local index_arg=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --root)
                root_filter="${2:-}"
                shift 2
                ;;
            --index)
                index_arg="${2:-}"
                shift 2
                ;;
            *)
                if [[ -z "$name" ]]; then
                    name="$1"
                elif [[ -z "$root_filter" ]]; then
                    root_filter="$1"
                fi
                shift
                ;;
        esac
    done

    [[ -z "$name" ]] && { echo "❌ Usage: /switch <project-name> [root|--root <root>] [--index <n>]"; exit 1; }

    OSORI_NAME="$name" OSORI_ROOT_FILTER="$root_filter" OSORI_SWITCH_INDEX="$index_arg" OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" \
      python3 "$SCRIPT_DIR/switch_handler.py"
}

cmd_fingerprints() {
    bash "$SCRIPT_DIR/project-fingerprints.sh" "$@"
}

cmd_add() {
    local path="${1:-}"
    [[ -z "$path" ]] && { echo "❌ Usage: /add <path>"; exit 1; }
    [[ ! -d "$path" ]] && { echo "❌ Directory not found: $path"; exit 1; }

    bash "$SCRIPT_DIR/add-project.sh" "$path"
}

cmd_remove() {
    local name="${1:-}"
    [[ -z "$name" ]] && { echo "❌ Usage: /remove <project-name>"; exit 1; }

    OSORI_NAME="$name" OSORI_SCRIPT_DIR="$SCRIPT_DIR" OSORI_REG="$REGISTRY_FILE" \
      python3 "$SCRIPT_DIR/remove_handler.py"
}

cmd_scan() {
    local path=""
    local root_key=""
    local depth="2"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --depth)
                depth="${2:-2}"
                shift 2
                ;;
            *)
                if [[ -z "$path" ]]; then
                    path="$1"
                elif [[ -z "$root_key" ]]; then
                    root_key="$1"
                fi
                shift
                ;;
        esac
    done

    local default_scan_root="${OSORI_SCAN_DEFAULT:-${OSORI_SEARCH_PATHS%%:*}}"
    if [[ -z "$path" ]]; then
      path="${default_scan_root:-.}"
    fi

    [[ ! -d "$path" ]] && { echo "❌ Directory not found: $path"; exit 1; }

    if [[ -n "$root_key" ]]; then
      echo "🔍 *Scanning for git repositories...* (root=$root_key, depth=$depth)"
      OSORI_ROOT_KEY="$root_key" bash "$SCRIPT_DIR/scan-projects.sh" "$path" --depth "$depth"
    else
      echo "🔍 *Scanning for git repositories...* (depth=$depth)"
      bash "$SCRIPT_DIR/scan-projects.sh" "$path" --depth "$depth"
    fi
}

cmd_doctor() {
    bash "$SCRIPT_DIR/doctor.sh" "$@"
}

cmd_list_roots() {
    bash "$SCRIPT_DIR/root-manager.sh" list
}

cmd_root_add() {
    local key="${1:-}"
    shift || true
    local label="${*:-}"

    [[ -z "$key" ]] && { echo "❌ Usage: /root-add <key> [label]"; exit 1; }

    if [[ -n "$label" ]]; then
      bash "$SCRIPT_DIR/root-manager.sh" add "$key" "$label"
    else
      bash "$SCRIPT_DIR/root-manager.sh" add "$key"
    fi
}

cmd_root_path_add() {
    local key="${1:-}"
    local path="${2:-}"
    [[ -z "$key" || -z "$path" ]] && { echo "❌ Usage: /root-path-add <key> <path>"; exit 1; }
    bash "$SCRIPT_DIR/root-manager.sh" path-add "$key" "$path"
}

cmd_root_path_remove() {
    local key="${1:-}"
    local path="${2:-}"
    [[ -z "$key" || -z "$path" ]] && { echo "❌ Usage: /root-path-remove <key> <path>"; exit 1; }
    bash "$SCRIPT_DIR/root-manager.sh" path-remove "$key" "$path"
}

cmd_root_set_label() {
    local key="${1:-}"
    shift || true
    local label="${*:-}"

    [[ -z "$key" || -z "$label" ]] && { echo "❌ Usage: /root-set-label <key> <label>"; exit 1; }
    bash "$SCRIPT_DIR/root-manager.sh" set-label "$key" "$label"
}

cmd_root_remove() {
    local key="${1:-}"
    shift || true

    [[ -z "$key" ]] && { echo "❌ Usage: /root-remove <key> [--reassign <target>] [--force]"; exit 1; }

    bash "$SCRIPT_DIR/root-manager.sh" remove "$key" "$@"
}

cmd_alias_add() {
    local alias_key="${1:-}"
    local project="${2:-}"
    [[ -z "$alias_key" || -z "$project" ]] && { echo "❌ Usage: /alias-add <alias> <project>"; exit 1; }
    bash "$SCRIPT_DIR/alias-favorite-manager.sh" alias-add "$alias_key" "$project"
}

cmd_alias_remove() {
    local alias_key="${1:-}"
    [[ -z "$alias_key" ]] && { echo "❌ Usage: /alias-remove <alias>"; exit 1; }
    bash "$SCRIPT_DIR/alias-favorite-manager.sh" alias-remove "$alias_key"
}

cmd_favorites() {
    bash "$SCRIPT_DIR/alias-favorite-manager.sh" favorites
}

cmd_favorite_add() {
    local project="${1:-}"
    [[ -z "$project" ]] && { echo "❌ Usage: /favorite-add <project>"; exit 1; }
    bash "$SCRIPT_DIR/alias-favorite-manager.sh" favorite-add "$project"
}

cmd_favorite_remove() {
    local project="${1:-}"
    [[ -z "$project" ]] && { echo "❌ Usage: /favorite-remove <project>"; exit 1; }
    bash "$SCRIPT_DIR/alias-favorite-manager.sh" favorite-remove "$project"
}

cmd_entire_status() {
    [[ $# -lt 1 ]] && { echo "❌ Usage: /entire-status <project> [root|--root <root>]"; exit 1; }
    bash "$SCRIPT_DIR/entire-manager.sh" status "$@"
}

cmd_entire_enable() {
    [[ $# -lt 1 ]] && { echo "❌ Usage: /entire-enable <project> [root|--root <root>] [--agent <name>] [--strategy <name>]"; exit 1; }
    bash "$SCRIPT_DIR/entire-manager.sh" enable "$@"
}

cmd_entire_rewind_list() {
    [[ $# -lt 1 ]] && { echo "❌ Usage: /entire-rewind-list <project> [root|--root <root>]"; exit 1; }
    bash "$SCRIPT_DIR/entire-manager.sh" rewind-list "$@"
}

# Main dispatch
command="${1:-help}"
if [[ $# -gt 0 ]]; then
  shift
fi

case "$command" in
    list) cmd_list "${1:-}" ;;
    status) cmd_status "${1:-}" ;;
    find) cmd_find "$@" ;;
    switch) cmd_switch "$@" ;;
    fingerprints) cmd_fingerprints "$@" ;;
    doctor) cmd_doctor "$@" ;;
    list-roots|roots) cmd_list_roots ;;
    root-add) cmd_root_add "$@" ;;
    root-path-add) cmd_root_path_add "$@" ;;
    root-path-remove) cmd_root_path_remove "$@" ;;
    root-set-label) cmd_root_set_label "$@" ;;
    root-remove) cmd_root_remove "$@" ;;
    alias-add) cmd_alias_add "${1:-}" "${2:-}" ;;
    alias-remove) cmd_alias_remove "${1:-}" ;;
    favorites) cmd_favorites ;;
    favorite-add) cmd_favorite_add "${1:-}" ;;
    favorite-remove) cmd_favorite_remove "${1:-}" ;;
    entire-status) cmd_entire_status "$@" ;;
    entire-enable) cmd_entire_enable "$@" ;;
    entire-rewind-list) cmd_entire_rewind_list "$@" ;;
    add) cmd_add "${1:-}" ;;
    remove) cmd_remove "${1:-}" ;;
    scan) cmd_scan "$@" ;;
    help|--help|-h) show_help ;;
    *) echo "❌ Unknown command: $command"; show_help; exit 1 ;;
esac