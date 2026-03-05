#!/usr/bin/env bash
# cortex-wrapper.sh — Agent-friendly wrapper for Cortex CLI
# Detects workspace memory paths automatically
set -euo pipefail

# Find cortex binary
CORTEX="${CORTEX_BIN:-$(command -v cortex 2>/dev/null || echo "$HOME/bin/cortex")}"
if [[ ! -x "$CORTEX" ]]; then
    echo "ERROR: cortex binary not found. Run the setup script first." >&2
    echo "  bash scripts/setup.sh" >&2
    exit 1
fi

# Auto-detect OpenClaw workspace
WORKSPACE="${OPENCLAW_WORKSPACE:-$(pwd)}"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"

cmd="${1:-help}"
shift || true

case "$cmd" in
    search)
        query="${1:-}"
        limit="${2:-5}"
        if [[ -z "$query" ]]; then
            echo "Usage: cortex-wrapper.sh search <query> [limit]" >&2
            exit 1
        fi
        "$CORTEX" search "$query" --limit "$limit" --json 2>/dev/null
        ;;

    import)
        path="${1:-$MEMORY_DIR}"
        shift || true
        echo "Importing from $path..."
        "$CORTEX" import "$path" "$@" 2>&1
        if [[ -f "$MEMORY_FILE" && "$path" != "$MEMORY_FILE" ]]; then
            echo "Importing $MEMORY_FILE..."
            "$CORTEX" import "$MEMORY_FILE" "$@" 2>&1
        fi
        ;;

    reimport)
        echo "Full re-import from workspace memory..."
        DB="${CORTEX_DB:-$HOME/.cortex/cortex.db}"
        rm -f "$DB"
        if [[ -d "$MEMORY_DIR" ]]; then
            "$CORTEX" import "$MEMORY_DIR" --extract 2>&1
        fi
        if [[ -f "$MEMORY_FILE" ]]; then
            "$CORTEX" import "$MEMORY_FILE" --extract 2>&1
        fi
        echo ""
        "$CORTEX" stats 2>&1
        ;;

    stats)
        "$CORTEX" stats --json 2>/dev/null
        ;;

    stale)
        days="${1:-30}"
        "$CORTEX" stale --days "$days" --json 2>/dev/null
        ;;

    conflicts)
        "$CORTEX" conflicts --json 2>/dev/null
        ;;

    help|--help|-h)
        echo "cortex-wrapper.sh — Cortex memory layer for OpenClaw"
        echo ""
        echo "Commands:"
        echo "  search <query> [limit]  BM25 keyword search (JSON output)"
        echo "  import [path] [flags]   Import files (default: workspace memory/)"
        echo "  reimport                Wipe DB + full re-import"
        echo "  stats                   Memory health overview"
        echo "  stale [days]            Stale facts not reinforced in N days"
        echo "  conflicts               Detect contradictory facts"
        echo ""
        echo "Direct CLI: $CORTEX <command> --help"
        ;;

    *)
        "$CORTEX" "$cmd" "$@" 2>&1
        ;;
esac
