#!/usr/bin/env bash
# Ghostclaw — main entry point
# Usage: ghostclaw.sh <mode> [args...]
# Modes: review <repo_path> | watcher

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/.."
PYTHON="${PYTHON:-python3}"

review() {
    local repo_path="$1"
    echo "👻 Ghostclaw scanning: $repo_path"
    echo ""

    if [[ ! -d "$repo_path" ]]; then
        echo "Error: directory not found: $repo_path" >&2
        exit 1
    fi

    # Run analysis
    local report_json
    report_json="$("$PYTHON" "$SCRIPT_DIR/analyze.py" "$repo_path" 2>/dev/null || echo '{"error":"analysis failed"}')"

    # Pretty print
    local vibe_score stack files total blem arch_ghosts red_flags
    vibe_score=$(echo "$report_json" | jq -r '.vibe_score // 0')
    stack=$(echo "$report_json" | jq -r '.stack // "unknown"')
    files=$(echo "$report_json" | jq -r '.files_analyzed // 0')
    total=$(echo "$report_json" | jq -r '.total_lines // 0')
    blem=$(echo "$report_json" | jq -c '.plings // []')
    arch_ghosts=$(echo "$report_json" | jq -c '.architectural_ghosts // []')
    red_flags=$(echo "$report_json" | jq -c '.red_flags // []')

    # Print vibe header
    if (( vibe_score >= 80 )); then
        emoji="🟢"
    elif (( vibe_score >= 60 )); then
        emoji="🟡"
    elif (( vibe_score >= 40 )); then
        emoji="🟠"
    else
        emoji="🔴"
    fi

    echo "${emoji} Vibe Score: ${vibe_score}/100"
    echo "   Stack: $stack"
    echo "   Files: $files, Lines: $total"
    echo ""

    # Print blem
    if [[ "$blem" != "[]" ]]; then
   echo "Issues detected:"
        echo "$blem" | jq -r '.[]' | sed 's/^/  • /'
        echo ""
    fi

    # Architectural ghosts
    if [[ "$arch_ghosts" != "[]" ]]; then
        echo "👻 Architectural Ghosts:"
        echo "$arch_ghosts" | jq -r '.[]' | sed 's/^/   /'
        echo ""
    fi

    # Red flags
    if [[ "$red_flags" != "[]" ]]; then
        echo "🚨 Red Flags:"
        echo "$red_flags" | jq -r '.[]' | sed 's/^/   /'
        echo ""
    fi

    # TODO: generate patches
    echo "💡 Tip: Run with '--patch' to generate refactor suggestions (not yet implemented)"
}

watcher() {
    echo "👻 Ghostclaw watcher starting..."
    # TODO: implement loop over repos list
    echo "Not implemented yet. Edit $SCRIPT_DIR/watcher.sh"
}

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 {review <repo_path>|watcher}"
    exit 1
fi

MODE="$1"
shift

case "$MODE" in
    review) review "$1" ;;
    watcher) watcher ;;
    *) echo "Unknown mode: $MODE"; exit 1 ;;
esac
