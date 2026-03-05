#!/bin/bash
# librarian.sh - 👷 Sandwich wrapper for librarian skill
# Protocol-driven research with hard stops

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOKS_DIR="${SKILL_DIR}/../books"
RESEARCH_PY="${SKILL_DIR}/../engine/scripts/research.py"

# Exit codes
EXIT_SUCCESS=0
EXIT_NO_METADATA=1
EXIT_BROKEN=2
EXIT_NO_RESULTS=3

# 👷 Node 1: Load Metadata
load_metadata() {
    local lib_index="${BOOKS_DIR}/.library-index.json"
    
    if [[ ! -f "$lib_index" ]]; then
        echo "ERROR_NO_METADATA"
        return $EXIT_NO_METADATA
    fi
    
    # Export for downstream use
    export LIB_INDEX="$lib_index"
    
    echo "METADATA_OK"
    return $EXIT_SUCCESS
}

# 👷 Node 3: Build Command
build_command() {
    local query="$1"
    local scope_type="$2"  # "topic" or "book"
    local scope_value="$3"  # topic_id or book filename
    local top_k="${4:-5}"
    
    local cmd=()
    cmd+=("python3" "$RESEARCH_PY" "$query")
    
    if [[ "$scope_type" == "topic" ]]; then
        cmd+=("--topic" "$scope_value")
    elif [[ "$scope_type" == "book" ]]; then
        cmd+=("--book" "$scope_value")
    else
        echo "ERROR_INVALID_SCOPE"
        return $EXIT_BROKEN
    fi
    
    cmd+=("--top-k" "$top_k")
    
    # Return command as string
    printf '%q ' "${cmd[@]}"
    return $EXIT_SUCCESS
}

# 👷 Node 4: Validate JSON Output
validate_json() {
    local json_file="$1"
    
    # Check if valid JSON
    if ! jq empty "$json_file" 2>/dev/null; then
        echo "ERROR_INVALID_JSON"
        return $EXIT_BROKEN
    fi
    
    # Check if results exist
    local result_count
    result_count=$(jq '.results | length' "$json_file" 2>/dev/null || echo 0)
    
    if [[ "$result_count" -eq 0 ]]; then
        echo "ERROR_NO_RESULTS"
        return $EXIT_NO_RESULTS
    fi
    
    echo "JSON_VALID"
    return $EXIT_SUCCESS
}

# Main flow
main() {
    local query="$1"
    local scope_type="${2:-}"
    local scope_value="${3:-}"
    local top_k="${4:-5}"
    
    # Node 1: Load metadata
    local metadata_status
    metadata_status=$(load_metadata)
    
    if [[ "$metadata_status" != "METADATA_OK" ]]; then
        echo "$metadata_status"
        exit $EXIT_NO_METADATA
    fi
    
    # Node 3: Build command (AI infers scope in Node 2, passes to us)
    local cmd
    cmd=$(build_command "$query" "$scope_type" "$scope_value" "$top_k")
    
    if [[ "$cmd" =~ ERROR ]]; then
        echo "$cmd"
        exit $EXIT_BROKEN
    fi
    
    # Execute research.py (Node: ⚙️ EXEC)
    # Redirect stderr to suppress warnings/logs
    local tmp_json="/tmp/librarian-$$.json"
    if ! eval "$cmd" 2>/dev/null > "$tmp_json"; then
        echo "ERROR_EXECUTION_FAILED"
        rm -f "$tmp_json"
        exit $EXIT_BROKEN
    fi
    
    # Node 4: Validate JSON
    local validation_status
    validation_status=$(validate_json "$tmp_json")
    
    if [[ "$validation_status" != "JSON_VALID" ]]; then
        echo "$validation_status"
        rm -f "$tmp_json"
        exit $?
    fi
    
    # Success: return JSON to skill for formatting
    cat "$tmp_json"
    rm -f "$tmp_json"
    exit $EXIT_SUCCESS
}

# Entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 3 ]]; then
        echo "Usage: $0 QUERY SCOPE_TYPE SCOPE_VALUE [TOP_K]"
        echo "  SCOPE_TYPE: topic|book"
        echo "  SCOPE_VALUE: topic_id or book filename"
        exit 1
    fi
    
    main "$@"
fi
