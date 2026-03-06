#!/bin/bash
# secure-memory-stack 主脚本
# 提供统一的命令接口

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/root/clawd"

CMD="${1:-help}"
shift || true

case "$CMD" in
    setup)
        echo "🚀 初始化安全记忆系统..."
        bash "/root/clawd/create/secure-memory-stack/scripts/setup.sh"
        ;;
    status|health)
        echo "🔍 检查系统状态..."
        bash "/root/clawd/create/secure-memory-stack/scripts/status.sh"
        ;;
    search)
        QUERY="$1"
        if [ -z "$QUERY" ]; then
            echo "❌ 请提供搜索查询"
            echo "用法: secure-memory search <query>"
            exit 1
        fi
        bash "/root/clawd/skills/secure-memory-stack/scripts/search.sh" "$QUERY"
        ;;
    hierarchical-search|layered-search)
        QUERY="$1"
        if [ -z "$QUERY" ]; then
            echo "❌ 请提供搜索查询"
            echo "用法: secure-memory hierarchical-search <query>"
            exit 1
        fi
        echo "🔍 使用分层搜索策略搜索: $QUERY"
        bash "/root/clawd/hierarchical_memory_search.sh" "$QUERY"
        ;;
    remember)
        CONTENT="$1"
        if [ -z "$CONTENT" ]; then
            echo "❌ 请提供要记住的内容"
            echo "用法: secure-memory remember <content> [--tags tag1,tag2] [--importance h|n|l]"
            exit 1
        fi
        bash "/root/clawd/create/secure-memory-stack/scripts/remember.sh" "$CONTENT" "$@"
        ;;
    configure)
        SERVICE="$1"
        if [ -z "$SERVICE" ]; then
            echo "❌ 请指定要配置的服务"
            echo "用法: secure-memory configure <baidu|all>"
            exit 1
        fi
        bash "/root/clawd/create/secure-memory-stack/scripts/configure.sh" "$SERVICE"
        ;;
    fix)
        COMPONENT="$1"
        if [ -z "$COMPONENT" ]; then
            echo "❌ 请指定要修复的组件"
            echo "用法: secure-memory fix <git|permissions|baidu|all>"
            exit 1
        fi
        bash "/root/clawd/create/secure-memory-stack/scripts/fix.sh" "$COMPONENT"
        ;;
    stats)
        bash "/root/clawd/create/secure-memory-stack/scripts/stats.sh"
        ;;
    diagnose)
        bash "/root/clawd/create/secure-memory-stack/scripts/diagnose.sh"
        ;;
    *)
        echo "🛡️  安全记忆系统 (Secure Memory Stack)"
        echo ""
        echo "用法: secure-memory <command> [options]"
        echo ""
        echo "主要命令:"
        echo "  setup                    - 初始化系统"
        echo "  status                   - 检查系统状态"
        echo "  search <query>          - 语义搜索"
        echo "  hierarchical-search     - 分层搜索(最近3天→7天→20天)"
        echo "  remember <content>      - 添加记忆"
        echo "  configure <service>     - 配置API"
        echo "  fix <component>         - 修复组件"
        echo "  stats                    - 查看统计"
        echo "  diagnose                 - 系统诊断"
        echo "  help                     - 显示此帮助"
        echo ""
        echo "示例:"
        echo "  secure-memory setup"
        echo "  secure-memory search '安全配置'"
        echo "  secure-memory hierarchical-search '用户偏好'"
        echo "  secure-memory remember '用户偏好：简洁高效' --tags preferences --importance high"
        ;;
esac