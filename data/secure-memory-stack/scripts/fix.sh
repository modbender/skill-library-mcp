#!/bin/bash
# 修复脚本

COMPONENT="$1"
WORKSPACE="/root/clawd"

case "$COMPONENT" in
    "git"|"-git")
        echo "🔧 修复Git系统..."
        if ! command -v git >/dev/null 2>&1; then
            echo "❌ Git未安装"
            echo "请安装Git后再试"
            exit 1
        fi
        
        if [ ! -d "$WORKSPACE/.git" ]; then
            cd "$WORKSPACE"
            git init
            git config user.name "SecureMemoryBot"
            git config user.email "securememory@example.com"
            echo "✅ Git仓库已初始化"
        else
            echo "✅ Git仓库已存在"
        fi
        ;;
    "permissions"|"-permissions")
        echo "🔧 修复文件权限..."
        chmod -R 755 "$WORKSPACE"
        chmod -R 644 "$WORKSPACE/MEMORY.md" "$WORKSPACE/SESSION-STATE.md" 2>/dev/null || true
        echo "✅ 文件权限已修复"
        ;;
    "baidu"|"-baidu")
        echo "🔧 检查百度Embedding配置..."
        if [ -n "$BAIDU_API_STRING" ] || [ -n "$BAIDU_API_KEY" ]; then
            echo "✅ 百度API配置已设置"
        else
            echo "⚠️ 百度API配置未设置"
            echo "运行: secure-memory configure baidu"
        fi
        ;;
    "all"|"-all")
        echo "🔧 修复所有组件..."
        bash "$0" "git"
        bash "$0" "permissions"
        bash "$0" "baidu"
        ;;
    *)
        echo "❌ 未知组件: $COMPONENT"
        echo "支持的组件: git, permissions, baidu, all"
        ;;
esac