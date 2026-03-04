#!/usr/bin/env bash
# init-community.sh — 初始化社区状态文件
# 用法: bash init-community.sh <workspace_path> <agent_id_1> [agent_id_2] ...

set -euo pipefail

WORKSPACE="${1:?用法: init-community.sh <workspace_path> <agent_id_1> [agent_id_2] ...}"
shift

if [ $# -eq 0 ]; then
  echo "错误: 至少需要一个 agent_id" >&2
  exit 1
fi

EXISTENCE_DIR="$WORKSPACE/existence"
mkdir -p "$EXISTENCE_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')

{
  echo "# 社区状态"
  echo "最后更新：${TIMESTAMP}"
  echo ""
  for AGENT_ID in "$@"; do
    echo "## ${AGENT_ID}"
    echo "- 状态：存活"
    echo "- 最后活跃：刚初始化"
    echo "- 在做：等待第一次唤醒"
    echo "- 最近想法：（尚无）"
    echo ""
  done
} > "$EXISTENCE_DIR/community.md"

echo "✓ 社区状态文件已创建: $EXISTENCE_DIR/community.md"
echo "  包含 agent: $*"
