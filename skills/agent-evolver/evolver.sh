#!/bin/bash
# Agent Evolver 快捷命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="python3"

show_help() {
    echo "Agent Evolver 快捷命令"
    echo ""
    echo "用法: ./evolver.sh <command> [options]"
    echo ""
    echo "命令:"
    echo "  analyze <result>       分析执行结果"
    echo "  search <query>         搜索相似经验"
    echo "  stats                  查看进化统计"
    echo "  history                查看进化历史"
    echo "  evolve <input>         执行进化周期"
    echo "  export <file>          导出经验库"
    echo ""
    echo "示例:"
    echo "  ./evolver.sh analyze 'ValueError: 不支持负数'"
    echo "  ./evolver.sh search '负数计算错误'"
    echo "  ./evolver.sh stats"
}

case "$1" in
    analyze)
        shift
        "$PYTHON" "$SCRIPT_DIR/scripts/evolution_cli.py" analyze "$@"
        ;;
    search)
        shift
        "$PYTHON" "$SCRIPT_DIR/scripts/evolution_cli.py" search "$@"
        ;;
    stats)
        shift
        "$PYTHON" "$SCRIPT_DIR/scripts/evolution_cli.py" stats "$@"
        ;;
    history)
        shift
        "$PYTHON" "$SCRIPT_DIR/scripts/evolution_cli.py" history "$@"
        ;;
    evolve)
        shift
        "$PYTHON" "$SCRIPT_DIR/scripts/evolution_cli.py" evolve "$@"
        ;;
    export)
        shift
        "$PYTHON" "$SCRIPT_DIR/scripts/evolution_cli.py" export "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac
