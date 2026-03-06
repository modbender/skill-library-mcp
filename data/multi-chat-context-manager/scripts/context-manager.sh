#!/usr/bin/env bash
# Multi-Chat Context Manager - Shell Wrapper
# Usage: context-manager.sh <command> [args]
# Commands: store, retrieve, clear, list

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/context_manager.py"

# Ensure Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT" >&2
    exit 1
fi

# Parse command
COMMAND="$1"
shift

case "$COMMAND" in
    store)
        # Expect arguments in key=value format for simplicity
        CHANNEL=""
        USER=""
        THREAD=""
        MESSAGE=""
        RESPONSE=""
        MAX_HISTORY="10"
        
        for arg in "$@"; do
            case "$arg" in
                channel=*) CHANNEL="${arg#*=}" ;;
                user=*) USER="${arg#*=}" ;;
                thread=*) THREAD="${arg#*=}" ;;
                message=*) MESSAGE="${arg#*=}" ;;
                response=*) RESPONSE="${arg#*=}" ;;
                max_history=*) MAX_HISTORY="${arg#*=}" ;;
                *) echo "Unknown argument: $arg" >&2; exit 1 ;;
            esac
        done
        
        if [[ -z "$CHANNEL" || -z "$MESSAGE" || -z "$RESPONSE" ]]; then
            echo "Usage: $0 store channel=<id> message=<text> response=<text> [user=<id>] [thread=<id>] [max_history=<n>]" >&2
            exit 1
        fi
        
        python3 "$PYTHON_SCRIPT" store \
            --channel "$CHANNEL" \
            ${USER:+--user "$USER"} \
            ${THREAD:+--thread "$THREAD"} \
            --message "$MESSAGE" \
            --response "$RESPONSE" \
            --max-history "$MAX_HISTORY"
        ;;
    
    retrieve)
        CHANNEL=""
        USER=""
        THREAD=""
        
        for arg in "$@"; do
            case "$arg" in
                channel=*) CHANNEL="${arg#*=}" ;;
                user=*) USER="${arg#*=}" ;;
                thread=*) THREAD="${arg#*=}" ;;
                *) echo "Unknown argument: $arg" >&2; exit 1 ;;
            esac
        done
        
        if [[ -z "$CHANNEL" ]]; then
            echo "Usage: $0 retrieve channel=<id> [user=<id>] [thread=<id>]" >&2
            exit 1
        fi
        
        python3 "$PYTHON_SCRIPT" retrieve \
            --channel "$CHANNEL" \
            ${USER:+--user "$USER"} \
            ${THREAD:+--thread "$THREAD"}
        ;;
    
    clear)
        CHANNEL=""
        USER=""
        THREAD=""
        
        for arg in "$@"; do
            case "$arg" in
                channel=*) CHANNEL="${arg#*=}" ;;
                user=*) USER="${arg#*=}" ;;
                thread=*) THREAD="${arg#*=}" ;;
                *) echo "Unknown argument: $arg" >&2; exit 1 ;;
            esac
        done
        
        python3 "$PYTHON_SCRIPT" clear \
            ${CHANNEL:+--channel "$CHANNEL"} \
            ${USER:+--user "$USER"} \
            ${THREAD:+--thread "$THREAD"}
        ;;
    
    list)
        python3 "$PYTHON_SCRIPT" list
        ;;
    
    *)
        echo "Usage: $0 {store|retrieve|clear|list} [args]" >&2
        echo ""
        echo "Examples:"
        echo "  $0 store channel=telegram-123 message=\"Hello\" response=\"Hi there\" user=user456"
        echo "  $0 retrieve channel=telegram-123 user=user456"
        echo "  $0 clear channel=telegram-123"
        echo "  $0 list"
        exit 1
        ;;
esac