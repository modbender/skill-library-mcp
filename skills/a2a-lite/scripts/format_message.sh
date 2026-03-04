#!/usr/bin/env bash
# 生成 A2A-Lite 协议消息
# 用法: format_message.sh <type> [params...] -- <body>
# 示例: format_message.sh task id=task-001 skill=research -- "帮我调研 AI Agent"

set -euo pipefail

TYPE="$1"
shift

# 收集参数直到遇到 --
PARAMS=""
while [[ $# -gt 0 && "$1" != "--" ]]; do
    if [[ -n "$PARAMS" ]]; then
        PARAMS="$PARAMS $1"
    else
        PARAMS="$1"
    fi
    shift
done

# 跳过 --
if [[ $# -gt 0 && "$1" == "--" ]]; then
    shift
fi

# 剩余部分作为消息体
BODY="$*"

# 构建消息
if [[ -n "$PARAMS" ]]; then
    echo "[A2A:$TYPE $PARAMS]"
else
    echo "[A2A:$TYPE]"
fi

if [[ -n "$BODY" ]]; then
    echo "$BODY"
fi
