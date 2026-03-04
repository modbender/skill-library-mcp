#!/usr/bin/env bash
# Stop litd (Lightning Terminal) containers.
#
# Usage:
#   docker-stop.sh                  # Stop standalone (preserve data)
#   docker-stop.sh --clean          # Stop and remove volumes
#   docker-stop.sh --watchonly      # Stop watch-only + signer
#   docker-stop.sh --regtest        # Stop regtest mode
#   docker-stop.sh --all            # Stop all litd containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"
MODE=""
CLEAN=false

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean|-v)
            CLEAN=true
            shift
            ;;
        --watchonly)
            MODE="watchonly"
            shift
            ;;
        --regtest)
            MODE="regtest"
            shift
            ;;
        --all)
            MODE="all"
            shift
            ;;
        -h|--help)
            echo "Usage: docker-stop.sh [options]"
            echo ""
            echo "Stop litd containers."
            echo ""
            echo "Options:"
            echo "  --clean, -v       Remove volumes (clean state)"
            echo "  --watchonly        Stop watch-only + signer containers"
            echo "  --regtest          Stop regtest containers"
            echo "  --all              Stop all litd containers regardless of mode"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Auto-detect mode from running containers if not specified.
if [ -z "$MODE" ]; then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^litd-bitcoind$'; then
        MODE="regtest"
    elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^litd-signer$'; then
        MODE="watchonly"
    elif docker ps --format '{{.Names}}' 2>/dev/null | grep -q '^litd$'; then
        MODE="standalone"
    else
        echo "No litd containers found running."
        exit 0
    fi
fi

cd "$TEMPLATE_DIR"

# Stop all litd containers regardless of mode.
if [ "$MODE" = "all" ]; then
    echo "Stopping all litd containers..."
    for file in docker-compose.yml docker-compose-watchonly.yml docker-compose-regtest.yml; do
        if [ -f "$file" ]; then
            if [ "$CLEAN" = true ]; then
                docker compose -f "$file" down -v 2>/dev/null || true
            else
                docker compose -f "$file" down 2>/dev/null || true
            fi
        fi
    done
    echo "Done."
    exit 0
fi

# Select compose file based on mode.
case "$MODE" in
    standalone)
        COMPOSE_FILE="docker-compose.yml"
        ;;
    watchonly)
        COMPOSE_FILE="docker-compose-watchonly.yml"
        ;;
    regtest)
        COMPOSE_FILE="docker-compose-regtest.yml"
        ;;
esac

echo "Stopping litd ($MODE mode)..."

if [ "$CLEAN" = true ]; then
    docker compose -f "$COMPOSE_FILE" down -v
    echo "Stopped and removed volumes."
else
    docker compose -f "$COMPOSE_FILE" down
    echo "Stopped (volumes preserved)."
fi
