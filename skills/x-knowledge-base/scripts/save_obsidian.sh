#!/bin/bash
# save_obsidian.sh - 將書籤轉化為 Obsidian 格式
# 依賴：Python 3, bookmark_enhancer.py

set -e

# 設定
SOURCE_DIR="${SOURCE_DIR:-/home/ubuntu/clawd/memory/bookmarks}"
OBSIDIAN_DIR="${OBSIDIAN_DIR:-/home/ubuntu/clawd/obsidian-vault}"
TOOLS_DIR="${TOOLS_DIR:-/home/ubuntu/clawd/skills/x-knowledge-base/tools}"
INTERESTS_FILE="${INTERESTS_FILE:-/home/ubuntu/clawd/skills/x-knowledge-base/config/interests.yaml}"

echo "📚 開始轉化為 Obsidian 格式..."

# 確保輸出目錄存在
mkdir -p "$OBSIDIAN_DIR"

# 直接用 bookmark_enhancer.py 處理（它會自己找書籤）
echo "🔬 AI 濃縮處理..."
python3 "$TOOLS_DIR/bookmark_enhancer.py" 3 2>&1 || echo "⚠️ AI 濃縮部分失敗"

# 複製所有書籤到 Obsidian 目錄
echo "📦 複製書籤到 Obsidian 目錄..."
cp -n "$SOURCE_DIR"/*.md "$OBSIDIAN_DIR/" 2>/dev/null || true

# 更新趨勢分析
echo "📈 更新趨勢分析..."
python3 "$TOOLS_DIR/trend_analyzer.py" "$OBSIDIAN_DIR" 2>/dev/null || true

echo "✅ Obsidian 格式轉化完成"
echo "📁 輸出目錄: $OBSIDIAN_DIR"
