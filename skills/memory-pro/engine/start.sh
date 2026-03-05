#!/bin/bash

# --- 環境變數設定 ---
export PATH="$HOME/.local/bin:$PATH"
export MEMORY_PRO_WORKSPACE_DIR="${MEMORY_PRO_WORKSPACE_DIR:-$HOME/.openclaw/workspace/}"
export MEMORY_PRO_DATA_DIR="${MEMORY_PRO_DATA_DIR:-$MEMORY_PRO_WORKSPACE_DIR/memory/}"
export MEMORY_PRO_CORE_FILES="${MEMORY_PRO_CORE_FILES:-MEMORY.md,SOUL.md,STATUS.md,AGENTS.md,USER.md}"
export MEMORY_PRO_PORT="${MEMORY_PRO_PORT:-8001}"
export MEMORY_PRO_INDEX_DIR="${MEMORY_PRO_INDEX_DIR:-$(pwd)}"
export MEMORY_PRO_INDEX_PATH="${MEMORY_PRO_INDEX_PATH:-$MEMORY_PRO_INDEX_DIR/memory.index}"

# --- 啟動前檢查與環境準備 ---
echo "🔄 Starting Memory Pro Service..."

# 使用 uv 如果可用
if command -v uv &> /dev/null; then
    echo "📦 Using uv to run python..."
    PYTHON_CMD="uv run python"
    UVICORN_CMD="uv run uvicorn"
else
    PYTHON_CMD="python3"
    UVICORN_CMD="uvicorn"
fi

echo "🔨 Rebuilding Index to ensure consistency..."
$PYTHON_CMD build_index.py

# --- 啟動服務 ---
echo "🚀 Starting Uvicorn on port $MEMORY_PRO_PORT..."
exec $UVICORN_CMD main:app --host 127.0.0.1 --port "$MEMORY_PRO_PORT" --log-level info
