#!/bin/bash

# GitHub Memory Sync Script
# 将 OpenClaw memory 同步到 GitHub

set -e

WORKSPACE_DIR="${WORKSPACE_DIR:-/root/.openclaw/workspace}"
MEMORY_FILE="$WORKSPACE_DIR/MEMORY.md"
MEMORY_DIR="$WORKSPACE_DIR/memory"
GITHUB_REPO="${GITHUB_REPO}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
GITHUB_TOKEN="${GITHUBTOKEN}"

if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_REPO" ]; then
    echo "❌ 错误：请配置 GITHUBTOKEN 和 GITHUB_REPO 环境变量"
    exit 1
fi

REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"
SYNC_DIR="/tmp/openclaw-memory-sync-$$"

cleanup() {
    rm -rf "$SYNC_DIR"
}
trap cleanup EXIT

copy_memory_files() {
    local src="$1"
    local dst="$2"
    
    # 复制 MEMORY.md
    if [ -f "$src/MEMORY.md" ]; then
        cp "$src/MEMORY.md" "$dst/MEMORY.md"
        echo "  📄 MEMORY.md"
    fi
    
    # 复制 memory/ 目录
    if [ -d "$src/memory" ] && [ "$(ls -A "$src/memory" 2>/dev/null)" ]; then
        mkdir -p "$dst/memory"
        cp -r "$src/memory"/* "$dst/memory/"
        echo "  📁 memory/ 目录"
    fi
}

case "$1" in
    init)
        echo "🔧 初始化 GitHub Memory 同步..."
        echo "📁 Workspace 目录：$WORKSPACE_DIR"
        echo "📦 GitHub 仓库：$GITHUB_REPO"
        echo "🌿 分支：$GITHUB_BRANCH"
        
        mkdir -p "$SYNC_DIR"
        cd "$SYNC_DIR"
        git init -q
        git remote add origin "$REPO_URL"
        
        # 复制 memory 文件
        echo "📋 准备同步的文件："
        copy_memory_files "$WORKSPACE_DIR" "$SYNC_DIR"
        
        # 检查是否有文件
        if [ ! -f "$SYNC_DIR/MEMORY.md" ] && [ ! -d "$SYNC_DIR/memory" ]; then
            echo "⚠️ 没有找到 memory 文件，创建占位符"
            mkdir -p "$SYNC_DIR/memory"
            touch "$SYNC_DIR/memory/.gitkeep"
        fi
        
        git add .
        git commit -m "Initial memory backup - $(date +%Y-%m-%d)"
        
        # 重命名分支并推送
        git branch -M "$GITHUB_BRANCH"
        git push -u origin "$GITHUB_BRANCH" 2>/dev/null || {
            echo "ℹ️ 远程仓库已有内容，正在合并..."
            git pull origin "$GITHUB_BRANCH" --no-rebase --allow-unrelated-histories
            git push -u origin "$GITHUB_BRANCH"
        }
        
        echo "✅ 初始化完成"
        ;;
    
    push)
        echo "📤 推送 memory 到 GitHub..."
        mkdir -p "$SYNC_DIR"
        cd "$SYNC_DIR"
        
        # 克隆或拉取
        if [ -d ".git" ]; then
            git fetch origin "$GITHUB_BRANCH" 2>/dev/null || true
            git reset --hard "origin/$GITHUB_BRANCH" 2>/dev/null || true
        else
            git clone -b "$GITHUB_BRANCH" "$REPO_URL" . 2>/dev/null || {
                echo "ℹ️ 远程仓库为空，初始化新仓库..."
                git init -q
                git remote add origin "$REPO_URL"
            }
        fi
        
        # 复制 memory 文件
        echo "📋 准备同步的文件："
        # 先清理旧文件（保留.git）
        find . -maxdepth 1 -type f ! -name ".git*" -delete
        rm -rf memory
        copy_memory_files "$WORKSPACE_DIR" "."
        
        # 检查是否有文件
        if [ ! -f "./MEMORY.md" ] && [ ! -d "./memory" ]; then
            echo "⚠️ 没有找到 memory 文件，创建占位符"
            mkdir -p memory
            touch memory/.gitkeep
        fi
        
        git add .
        git commit -m "Update memory backup - $(date '+%Y-%m-%d %H:%M')" || {
            echo "ℹ️ 没有更改需要提交"
            echo "✅ 已经是最新状态"
            exit 0
        }
        git push origin "$GITHUB_BRANCH"
        
        echo "✅ 推送成功"
        ;;
    
    pull)
        echo "📥 从 GitHub 拉取 memory..."
        mkdir -p "$SYNC_DIR"
        cd "$SYNC_DIR"
        
        git clone -b "$GITHUB_BRANCH" "$REPO_URL" .
        
        # 复制回 workspace
        echo "📋 恢复文件到 workspace："
        if [ -f "MEMORY.md" ]; then
            cp "MEMORY.md" "$WORKSPACE_DIR/MEMORY.md"
            echo "  📄 MEMORY.md"
        fi
        
        if [ -d "memory" ] && [ "$(ls -A memory 2>/dev/null)" ]; then
            mkdir -p "$WORKSPACE_DIR/memory"
            cp -r memory/* "$WORKSPACE_DIR/memory/"
            echo "  📁 memory/ 目录"
        fi
        
        echo "✅ 拉取成功"
        echo "📂 文件已保存到：$WORKSPACE_DIR"
        ;;
    
    status)
        echo "📊 检查同步状态..."
        mkdir -p "$SYNC_DIR"
        cd "$SYNC_DIR"
        
        if [ ! -d ".git" ]; then
            git clone -b "$GITHUB_BRANCH" "$REPO_URL" . 2>/dev/null || {
                echo "⚠️ 远程仓库不存在，需要先初始化"
                exit 1
            }
        else
            git fetch origin "$GITHUB_BRANCH" 2>/dev/null || true
        fi
        
        echo ""
        echo "📁 本地文件（$WORKSPACE_DIR）："
        if [ -f "$WORKSPACE_DIR/MEMORY.md" ]; then
            echo "  ✅ MEMORY.md"
        else
            echo "  ❌ MEMORY.md (不存在)"
        fi
        if [ -d "$WORKSPACE_DIR/memory" ] && [ "$(ls -A "$WORKSPACE_DIR/memory" 2>/dev/null)" ]; then
            echo "  ✅ memory/ 目录 ($(ls "$WORKSPACE_DIR/memory" | wc -l) 个文件)"
        else
            echo "  ⚠️ memory/ 目录 (空)"
        fi
        
        echo ""
        echo "📁 远程文件（GitHub）："
        if [ -f "MEMORY.md" ]; then
            echo "  ✅ MEMORY.md"
        else
            echo "  ❌ MEMORY.md (不存在)"
        fi
        if [ -d "memory" ] && [ "$(ls -A memory 2>/dev/null)" ]; then
            echo "  ✅ memory/ 目录 ($(ls memory | wc -l) 个文件)"
        else
            echo "  ⚠️ memory/ 目录 (空)"
        fi
        
        echo ""
        # 检查差异
        echo "🔍 差异检查："
        diff_count=0
        
        if [ -f "$WORKSPACE_DIR/MEMORY.md" ] && [ -f "MEMORY.md" ]; then
            if ! diff -q "$WORKSPACE_DIR/MEMORY.md" "MEMORY.md" > /dev/null 2>&1; then
                echo "  ⚠️ MEMORY.md 有差异"
                diff_count=$((diff_count + 1))
            else
                echo "  ✅ MEMORY.md 已同步"
            fi
        fi
        
        if [ -d "$WORKSPACE_DIR/memory" ] && [ -d "memory" ]; then
            if ! diff -rq "$WORKSPACE_DIR/memory" "memory" > /dev/null 2>&1; then
                echo "  ⚠️ memory/ 目录有差异"
                diff_count=$((diff_count + 1))
            else
                echo "  ✅ memory/ 目录已同步"
            fi
        fi
        
        if [ $diff_count -eq 0 ]; then
            echo ""
            echo "✅ 本地和远程完全同步"
        else
            echo ""
            echo "⚠️ 检测到 $diff_count 处差异，建议执行推送或拉取"
        fi
        
        ;;
    
    *)
        echo "GitHub Memory Sync"
        echo ""
        echo "用法：$0 {init|push|pull|status}"
        echo ""
        echo "命令说明:"
        echo "  init   - 初始化 GitHub 仓库连接（首次使用）"
        echo "  push   - 推送本地 memory 到 GitHub"
        echo "  pull   - 从 GitHub 拉取 memory 到本地"
        echo "  status - 检查同步状态"
        echo ""
        echo "环境变量:"
        echo "  GITHUBTOKEN  - GitHub Personal Access Token"
        echo "  GITHUB_REPO  - GitHub 仓库 (格式：username/repo)"
        echo "  GITHUB_BRANCH - 分支名称 (默认：main)"
        echo "  WORKSPACE_DIR - Workspace 目录路径 (默认：/root/.openclaw/workspace)"
        exit 1
        ;;
esac
