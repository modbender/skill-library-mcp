#!/bin/bash
# GitHub 开源贡献自动化脚本（支持自定义根目录）
# 用法: ./github-contribution.sh <your-username> <owner/repo> <issue-number> <feature-branch-name> [projects-root]

set -e

USERNAME="$1"
OWNER_REPO="$2"
ISSUE_NUMBER="$3" 
FEATURE_BRANCH="$4"
PROJECTS_ROOT="${5:-${HOME}/IdeaProjects}"

if [ $# -lt 4 ]; then
    echo "用法: $0 <your-username> <owner/repo> <issue-number> <feature-branch-name> [projects-root]"
    echo "示例: $0 linux2010 openclaw/openclaw 31233 fix-auth-vulnerability ~/Code"
    echo ""
    echo "⚠️  重要前提：请先在 GitHub 网页上 fork 项目！"
    echo "   访问 https://github.com/$OWNER_REPO 并点击 'Fork' 按钮"
    exit 1
fi

OWNER=$(echo "$OWNER_REPO" | cut -d'/' -f1)
REPO=$(echo "$OWNER_REPO" | cut -d'/' -f2)

echo "🚀 开始 GitHub 贡献流程（支持自定义根目录）"
echo "用户名: $USERNAME"
echo "项目: $OWNER_REPO"  
echo "Issue: #$ISSUE_NUMBER"
echo "特性分支: $FEATURE_BRANCH"
echo "项目根目录: $PROJECTS_ROOT"
echo ""

# 创建项目根目录（如果不存在）
mkdir -p "$PROJECTS_ROOT"

# 1. 验证用户是否已经 fork 项目
echo "🔍 验证 Fork 状态..."
FORK_URL="https://github.com/${USERNAME}/${REPO}.git"
if ! git ls-remote --exit-code "$FORK_URL" &>/dev/null; then
    echo "❌ 错误: 无法访问你的 Fork: $FORK_URL"
    echo "💡 请先在 GitHub 网页上 fork 项目: https://github.com/$OWNER_REPO"
    exit 1
fi
echo "✅ 验证通过: 你的 Fork 可访问"

# 2. 克隆或进入项目目录（使用用户的 Fork）
PROJECT_DIR="${PROJECTS_ROOT}/${REPO}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 克隆你的 Fork 到 $PROJECT_DIR"
    git clone "$FORK_URL" "$PROJECT_DIR"
else
    echo "📁 使用现有项目目录: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# 3. 验证当前仓库是否是用户的 Fork
CURRENT_ORIGIN=$(git remote get-url origin)
if [[ "$CURRENT_ORIGIN" != *"${USERNAME}/${REPO}"* ]]; then
    echo "⚠️  警告: 当前目录的 origin 不是指向你的 Fork"
    echo "当前 origin: $CURRENT_ORIGIN"
    echo "期望 origin: $FORK_URL"
    echo "建议删除目录重新开始，或手动修正远程配置"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 4. 添加官方仓库作为 upstream（如果不存在）
if ! git remote get-url upstream &>/dev/null; then
    echo "🔗 添加官方仓库作为 upstream 远程"
    git remote add upstream "https://github.com/${OWNER_REPO}.git"
else
    echo "🔗 Upstream 远程已存在"
fi

# 5. 确保在 main/master 分支并同步到最新
echo "🔄 同步你的 Fork 到官方最新状态"
git checkout main 2>/dev/null || git checkout master
git fetch upstream
git reset --hard upstream/main 2>/dev/null || git reset --hard upstream/master

# 6. 推送同步后的更改到你的 Fork
echo "📤 推送同步后的代码到你的 Fork"
git push origin main 2>/dev/null || git push origin master

# 7. 创建特性分支
echo "🌱 创建特性分支: $FEATURE_BRANCH"
git checkout -b "$FEATURE_BRANCH"

echo ""
echo "✅ 准备就绪！现在你可以:"
echo "1. 在 $PROJECT_DIR 目录中开发修复代码"
echo "2. 测试你的更改"
echo "3. 提交代码: git add . && git commit -m 'fix: 解决 issue #$ISSUE_NUMBER'"
echo "4. 推送到你的 fork: git push origin $FEATURE_BRANCH"
echo "5. 访问 https://github.com/$USERNAME/$REPO/pull/new/$FEATURE_BRANCH 创建 PR"

echo ""
echo "💡 提示: 请确保遵循项目的 CONTRIBUTING.md 和代码规范"