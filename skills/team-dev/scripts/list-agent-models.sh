#!/bin/bash
# list-agent-models.sh - List available models for an agent (currently cursor-focused)

set -e

AGENT="${1:-cursor}"

case "$AGENT" in
    cursor)
        if ! command -v cursor >/dev/null 2>&1; then
            echo "cursor CLI not found"
            exit 1
        fi
        if ! out=$(cursor agent status 2>&1 || true); then
            :
        fi
        if echo "$out" | grep -qi "not logged in"; then
            echo "cursor 未登录，先执行: cursor agent login"
            echo "说明: 你提到常用 composer 1.5，登录后可直接在 spawn-agent 使用 --agent cursor --agent-model composer-1.5"
            exit 1
        fi
        cursor agent --list-models
        ;;
    *)
        echo "Unsupported agent: $AGENT"
        echo "Usage: $0 [cursor]"
        exit 1
        ;;
esac

