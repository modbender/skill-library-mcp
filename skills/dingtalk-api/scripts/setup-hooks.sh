#!/bin/sh
# 安装 git hooks

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo "🔧 正在安装 git hooks..."

# 确保 .git/hooks 目录存在
mkdir -p "$HOOKS_DIR"

# 复制 post-commit hook
cp "$SCRIPT_DIR/git-hook-post-commit.sh" "$HOOKS_DIR/post-commit"
chmod +x "$HOOKS_DIR/post-commit"

echo "✅ Git hooks 安装完成！"
echo "   - post-commit: 每次 commit 后自动更新 SKILL.md"
