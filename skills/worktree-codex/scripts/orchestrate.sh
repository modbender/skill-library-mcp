#!/usr/bin/env bash
# worktree-codex/scripts/orchestrate.sh
# OpenClaw 多 Codex Worktree 编排脚本
#
# 用法:
#   orchestrate.sh <repo_dir> <agent_name> <worktree_path> <branch> <task_prompt> <log_file>
#
# 环境变量（调用方传入或 export）:
#   OPENAI_API_KEY    — API Key（必填，从 ~/.profile 继承或显式传入）
#   OPENAI_BASE_URL   — 默认 http://152.53.52.170:3003/v1（自建代理，支持 /v1/responses）
#   CODEX_MODEL       — 默认 gpt-5.3-codex；省 token 可换 gemini-2.5-flash / deepseek-v3
#   CODEX_BIN         — 默认 ~/.npm-global/bin/codex
#
# ⚠️ OpenRouter 不可用：它不实现 /v1/responses 端点，会报 401。
#    节省 token 请直接换 CODEX_MODEL，自建代理上 gemini/deepseek 等均支持。

set -euo pipefail

REPO_DIR="$1"
AGENT_NAME="$2"
WORKTREE_PATH="$3"
BRANCH="$4"
TASK_PROMPT="$5"
LOG_FILE="$6"

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://152.53.52.170:3003/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:?需要设置 OPENAI_API_KEY（或 source ~/.profile）}"
CODEX_MODEL="${CODEX_MODEL:-gpt-5.3-codex}"
CODEX_BIN="${CODEX_BIN:-$HOME/.npm-global/bin/codex}"

echo "[$(date '+%H:%M:%S')] $AGENT_NAME starting in $WORKTREE_PATH" | tee "$LOG_FILE"
echo "[$(date '+%H:%M:%S')] $AGENT_NAME model=$CODEX_MODEL base=$OPENAI_BASE_URL" | tee -a "$LOG_FILE"

# 通知展板有新任务（如果展板在运行）；静默失败不影响主流程
DASHBOARD_PORT="${DASHBOARD_PORT:-7789}"
curl -s --max-time 1 -X POST "http://localhost:${DASHBOARD_PORT}/reload" \
  -H "Content-Type: application/json" \
  -d "{\"logs\":[\"$LOG_FILE\"]}" > /dev/null 2>&1 || true

cd "$WORKTREE_PATH"

# --full-auto = -a on-request --sandbox workspace-write（允许写文件）
"$CODEX_BIN" exec \
  --model "$CODEX_MODEL" \
  --full-auto \
  --skip-git-repo-check \
  "$TASK_PROMPT" \
  >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
echo "[$(date '+%H:%M:%S')] $AGENT_NAME codex exited with code $EXIT_CODE" | tee -a "$LOG_FILE"

# 有待提交变更则自动 commit
PENDING=$(git status --porcelain)
if [ -n "$PENDING" ]; then
  git add -A
  git commit -m "feat: $AGENT_NAME task complete" --no-verify 2>&1 | tee -a "$LOG_FILE"
  echo "[$(date '+%H:%M:%S')] $AGENT_NAME: committed changes" | tee -a "$LOG_FILE"
else
  echo "[$(date '+%H:%M:%S')] $AGENT_NAME: no changes to commit" | tee -a "$LOG_FILE"
fi

echo "AGENT_DONE:$AGENT_NAME" | tee -a "$LOG_FILE"
