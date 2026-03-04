#!/bin/bash
###############################################################################
# AI内容流水线主控脚本
# 一键执行: 收集 → 分析 → 输出
# 用法: ./pipeline.sh [日期，格式YYYY-MM-DD，默认为今天]
###############################################################################

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE_DIR="$(dirname "$SCRIPT_DIR")"
DATE="${1:-$(date +%Y-%m-%d)}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║        AI内容收集流水线 - 公众号选题推荐系统              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_step "检查依赖..."
    
    local deps_ok=true
    
    if ! command -v jq &> /dev/null; then
        print_error "未找到 jq，请先安装: brew install jq"
        deps_ok=false
    fi
    
    if ! command -v curl &> /dev/null; then
        print_error "未找到 curl"
        deps_ok=false
    fi
    
    if [[ "$deps_ok" == false ]]; then
        exit 1
    fi
    
    print_success "依赖检查通过"
}

# 显示目录结构
show_structure() {
    print_info "项目结构:"
    echo ""
    echo "  ai-content-pipeline/"
    echo "  ├── config/"
    echo "  │   └── sources.json          # 数据源配置"
    echo "  ├── scripts/"
    echo "  │   ├── collect.sh            # 内容收集脚本"
    echo "  │   ├── analyze.sh            # 分析准备脚本"
    echo "  │   └── pipeline.sh           # 本主控脚本"
    echo "  ├── collected/"
    echo "  │   └── $DATE/"
    echo "  │       ├── raw-content.json  # 原始JSON数据"
    echo "  │       └── raw-content.md    # Markdown报告"
    echo "  └── filtered/"
    echo "      └── $DATE/"
    echo "          └── wechat-worthy.md  # 公众号选题推荐"
    echo ""
}

# 执行收集
run_collect() {
    print_step "Step 1/3: 收集AI内容..."
    
    if "$SCRIPT_DIR/collect.sh" "$DATE"; then
        print_success "内容收集完成"
    else
        print_error "内容收集失败"
        exit 1
    fi
}

# 执行分析准备
run_analyze() {
    print_step "Step 2/3: 准备分析任务..."
    
    if "$SCRIPT_DIR/analyze.sh" "$DATE"; then
        print_success "分析准备完成"
    else
        print_error "分析准备失败"
        exit 1
    fi
}

# 显示结果
show_results() {
    print_step "Step 3/3: 结果汇总"
    echo ""
    
    COLLECTED_DIR="$PIPELINE_DIR/collected/$DATE"
    FILTERED_DIR="$PIPELINE_DIR/filtered/$DATE"
    
    # 统计数据
    if [[ -f "$COLLECTED_DIR/raw-content.json" ]]; then
        TOTAL=$(jq '[.sources[].items | length] | add' "$COLLECTED_DIR/raw-content.json")
        print_success "共收集 $TOTAL 条AI相关内容"
    fi
    
    echo ""
    echo "📁 输出文件:"
    echo ""
    
    if [[ -f "$COLLECTED_DIR/raw-content.md" ]]; then
        echo "  📄 原始内容: $COLLECTED_DIR/raw-content.md"
    fi
    
    if [[ -f "$FILTERED_DIR/analysis-task.md" ]]; then
        echo "  📋 分析任务: $FILTERED_DIR/analysis-task.md"
    fi
    
    if [[ -f "$FILTERED_DIR/wechat-worthy.md" ]]; then
        echo "  ⭐ 选题推荐: $FILTERED_DIR/wechat-worthy.md"
    fi
    
    echo ""
}

# 主流程
main() {
    print_header
    
    print_info "运行日期: $DATE"
    echo ""
    
    check_dependencies
    show_structure
    
    run_collect
    run_analyze
    show_results
    
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                    流水线执行完成!                          ${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "下一步操作:"
    echo ""
    echo "  1. 查看收集的内容:"
    echo "     cat $PIPELINE_DIR/collected/$DATE/raw-content.md"
    echo ""
    echo "  2. 使用OpenClaw进行AI分析:"
    echo "     在OpenClaw中使用 sessions_spawn 工具分析:"
    echo "     任务: $PIPELINE_DIR/filtered/$DATE/analysis-task.md"
    echo ""
    echo "  3. 配置定时任务 (Cron):"
    echo "     参考 ~/.openclaw/workspace/ai-content-pipeline/config/cron-example.json"
    echo ""
}

# 运行主流程
main "$@"
