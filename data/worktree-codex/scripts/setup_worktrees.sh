#!/usr/bin/env bash
# worktree-agents/scripts/setup_worktrees.sh
# 为每个 Agent 创建 git worktree 并返回路径
#
# 用法: setup_worktrees.sh <repo_dir> <worktrees_base_dir> <agent_names_space_separated>
# 输出: 每行一个 "agent_name:worktree_path:branch_name"

set -euo pipefail

REPO_DIR="$1"
WORKTREES_BASE="$2"
shift 2
AGENTS=("$@")

cd "$REPO_DIR"
mkdir -p "$WORKTREES_BASE"

# 记录起始分支，避免 checkout - 行为不确定
ORIGINAL_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD)

# 共享时间戳（秒级），再加随机4位，防止并行时撞名
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

for AGENT in "${AGENTS[@]}"; do
  RAND=$(tr -dc 'a-z0-9' < /dev/urandom | head -c4 || true)
  BRANCH="feature/${AGENT}-${TIMESTAMP}-${RAND}"
  WORKTREE_PATH="$WORKTREES_BASE/$AGENT"

  # 清理已存在的 worktree
  if git worktree list | grep -q "$WORKTREE_PATH"; then
    git worktree remove --force "$WORKTREE_PATH" 2>/dev/null || true
  fi
  rm -rf "$WORKTREE_PATH"

  # 从原始分支创建新分支，明确基点（不依赖当前 HEAD 位置）
  git branch "$BRANCH" "$ORIGINAL_BRANCH"

  # 创建 worktree（不切换主 repo 的 HEAD）
  git worktree add "$WORKTREE_PATH" "$BRANCH"

  echo "$AGENT:$WORKTREE_PATH:$BRANCH"
done
