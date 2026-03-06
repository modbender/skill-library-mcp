#!/bin/bash
# CodeFlicker Workspace 管理
# 用法: workspace.sh [create|list|complete|delete] [选项]

COMMAND="$1"
NAME="$2"

if [ -z "$COMMAND" ]; then
    echo "用法: workspace.sh <命令> [选项]"
    echo ""
    echo "命令:"
    echo "  create [options]     创建 workspace"
    echo "    --name <name>     自定义名称"
    echo "    --branch, -b      基于分支 (默认: main)"
    echo "  list                 列出所有 workspace"
    echo "  complete             完成并合并 (从根目录运行)"
    echo "  delete <name>       删除 workspace"
    echo ""
    echo "示例:"
    echo "  workspace.sh create"
    echo "  workspace.sh create --name feature-login"
    echo "  workspace.sh create -b develop"
    echo "  workspace.sh list"
    echo "  workspace.sh delete tokyo"
    exit 0
fi

if ! command -v flickcli &> /dev/null; then
    echo "❌ flickcli 未安装"
    exit 1
fi

case "$COMMAND" in
    create)
        if [ -n "$NAME" ] && [ "$NAME" != "--name" ]; then
            flickcli workspace create --name "$NAME"
        else
            flickcli workspace create "$@"
        fi
        ;;
    list|ls)
        flickcli workspace list
        ;;
    complete)
        flickcli workspace complete
        ;;
    delete|rm)
        if [ -z "$NAME" ]; then
            echo "用法: workspace.sh delete <名称>"
            exit 1
        fi
        flickcli workspace delete "$NAME"
        ;;
    *)
        echo "未知命令: $COMMAND"
        exit 1
        ;;
esac