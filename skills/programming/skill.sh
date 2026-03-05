#!/bin/bash
# 编程技能主执行脚本

# 该脚本根据输入的任务类型执行相应的编程相关操作
# 参数:
# $1: 任务类型 (claude_cli, workflow, review)
# $2: 具体任务描述或上下文

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
  "claude_cli")
    echo "执行 Claude CLI 编程指南查询..."
    cat "$SKILL_DIR/claude_cli_guide.md"
    ;;
    
  "workflow")
    echo "执行编程工作流程指导..."
    cat "$SKILL_DIR/workflow_guide.md"
    ;;
    
  "review")
    echo "执行代码审查和优化建议..."
    cat "$SKILL_DIR/code_review_optimization.md"
    ;;
  
  "all")
    echo "# Claude CLI 编程指南"
    echo ""
    cat "$SKILL_DIR/claude_cli_guide.md"
    echo ""
    echo "# 编程工作流程指导"
    echo ""
    cat "$SKILL_DIR/workflow_guide.md"
    echo ""
    echo "# 代码审查和优化建议"
    echo ""
    cat "$SKILL_DIR/code_review_optimization.md"
    ;;
    
  *)
    echo "用法: $0 {claude_cli|workflow|review|all} [context]"
    echo ""
    echo "选项:"
    echo "  claude_cli - 获取 Claude CLI 编程指南"
    echo "  workflow   - 获取编程工作流程指导"
    echo "  review     - 获取代码审查和优化建议"
    echo "  all        - 获取所有编程相关内容"
    echo ""
    echo "示例:"
    echo "  $0 claude_cli"
    echo "  $0 workflow"
    ;;
esac