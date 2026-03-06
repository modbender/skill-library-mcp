#!/bin/bash
set -e

# arr-all main entry point
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Source libraries
source "$DIR/lib/common.sh"
source "$DIR/lib/radarr.sh"
source "$DIR/lib/sonarr.sh"
source "$DIR/lib/lidarr.sh"

# Check dependencies
check_deps

# Help function
show_help() {
    echo "Usage: arr-all <type> <action> [args] OR arr-all <command> [args]"
    echo ""
    echo "Types:"
    echo "  movie (Radarr) | tv (Sonarr) | music (Lidarr)"
    echo ""
    echo "Common Commands:"
    echo "  search <query>          Search for content"
    echo "  add <id>                Add content by ID"
    echo "  remove <id>             Remove content"
    echo "  exists <id>             Check if content exists"
    echo "  config                  Show configuration"
    echo ""
    echo "Global Commands:"
    echo "  calendar [days]         Show upcoming releases"
    echo "  health                  Check health of all apps"
    echo "  search <query>          Search all apps"
    echo "  status                  Check connection status"
    echo ""
    echo "See SKILL.md for full documentation."
}

# Main dispatch
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Check for global commands first
case "$1" in
    calendar)
        shift
        "$DIR/arr-all-calendar.sh" "$@"
        exit $?
        ;;
    health)
        "$DIR/../hooks/health-check.sh"
        exit $?
        ;;
    status)
        echo "Checking connections..."
        if load_config "radarr"; then echo -e "${GREEN}Radarr:${NC} Connected"; else echo -e "${RED}Radarr:${NC} Not configured"; fi
        if load_config "sonarr"; then echo -e "${GREEN}Sonarr:${NC} Connected"; else echo -e "${RED}Sonarr:${NC} Not configured"; fi
        if load_config "lidarr"; then echo -e "${GREEN}Lidarr:${NC} Connected"; else echo -e "${RED}Lidarr:${NC} Not configured"; fi
        exit 0
        ;;
    search)
        if [ "$#" -lt 2 ]; then
            echo "Usage: arr-all search <query>"
            exit 1
        fi
        query="$2"
        echo "=== Movies ==="
        radarr_search "$query"
        echo ""
        echo "=== TV Shows ==="
        sonarr_search "$query"
        echo ""
        echo "=== Music ==="
        lidarr_search "$query"
        exit 0
        ;;
esac

# Type-specific dispatch
TYPE="$1"
shift
ACTION="$1"
shift || true

# Validate type
case "$TYPE" in
    movie|radarr)
        SERVICE="radarr"
        ;;
    tv|sonarr|show)
        SERVICE="sonarr"
        ;;
    music|lidarr)
        SERVICE="lidarr"
        ;;
    *)
        show_help
        exit 1
        ;;
esac

if [ -z "$ACTION" ]; then
    echo "Error: Missing action for $TYPE"
    show_help
    exit 1
fi

# Dispatch to service function
# Pattern: service_action [args]
FUNC="${SERVICE}_${ACTION//-/_}"

if declare -f "$FUNC" > /dev/null; then
    # Pass all remaining arguments
    "$FUNC" "$@"
else
    # Try mapping common aliases if needed, or just fail
    # Special cases handling
    if [[ "$SERVICE" == "lidarr" && "$ACTION" == "albums" ]]; then
        lidarr_albums "$@"
        exit 0
    fi
    
    echo "Error: Unknown action '$ACTION' for $TYPE"
    exit 1
fi
