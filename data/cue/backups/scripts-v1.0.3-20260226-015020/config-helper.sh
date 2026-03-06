#!/bin/bash
#
# User-friendly Configuration Helper - 用户友好的配置助手
# 提供交互式 API Key 配置

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_header() {
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║     🔧 Cue 监控功能配置向导              ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
}

# 检查当前配置状态
check_current_status() {
    echo "📋 当前配置状态："
    echo ""
    
    if [ -n "$TAVILY_API_KEY" ]; then
        echo -e "  ${GREEN}✓${NC} Tavily API Key: 已配置"
        echo "     功能: 搜索新闻、公告、研报"
    else
        echo -e "  ${RED}✗${NC} Tavily API Key: 未配置"
        echo "     影响: 无法使用监控功能（必需）"
    fi
    
    echo ""
    
    if [ -n "$QVERIS_API_KEY" ]; then
        echo -e "  ${GREEN}✓${NC} QVeris API Key: 已配置"
        echo "     功能: 实时股价、汇率数据"
    else
        echo -e "  ${YELLOW}!${NC} QVeris API Key: 未配置（可选）"
        echo "     影响: 股价监控将使用搜索代替（体验稍差）"
    fi
    
    echo ""
}

# 配置 Tavily
setup_tavily() {
    echo -e "${BLUE}【配置 Tavily】${NC}"
    echo "Tavily 提供新闻搜索能力，是监控功能的基础。"
    echo ""
    echo "步骤："
    echo "  1. 访问 https://tavily.com"
    echo "  2. 注册账号（免费额度足够使用）"
    echo "  3. 在 Dashboard 复制 API Key"
    echo ""
    read -p "请输入 Tavily API Key: " tavily_key
    
    if [ -n "$tavily_key" ]; then
        # 保存到 .env
        if grep -q "TAVILY_API_KEY" ~/.openclaw/.env 2>/dev/null; then
            # 更新现有配置
            sed -i "s/TAVILY_API_KEY=.*/TAVILY_API_KEY=${tavily_key}/" ~/.openclaw/.env
        else
            # 添加新配置
            echo "TAVILY_API_KEY=${tavily_key}" >> ~/.openclaw/.env
        fi
        
        export TAVILY_API_KEY="$tavily_key"
        echo -e "${GREEN}✓ Tavily API Key 已保存${NC}"
    else
        echo "未输入 Key，跳过配置"
    fi
    echo ""
}

# 配置 QVeris
setup_qveris() {
    echo -e "${BLUE}【配置 QVeris】${NC}"
    echo "QVeris 提供实时股价数据，让股价监控更准确。"
    echo ""
    echo "步骤："
    echo "  1. 访问 https://qveris.ai/?ref=OTXNTKI78gS6Gg"
    echo "  2. 注册账号"
    echo "  3. 在设置中复制 API Key"
    echo ""
    read -p "请输入 QVeris API Key (直接回车跳过): " qveris_key
    
    if [ -n "$qveris_key" ]; then
        if grep -q "QVERIS_API_KEY" ~/.openclaw/.env 2>/dev/null; then
            sed -i "s/QVERIS_API_KEY=.*/QVERIS_API_KEY=${qveris_key}/" ~/.openclaw/.env
        else
            echo "QVERIS_API_KEY=${qveris_key}" >> ~/.openclaw/.env
        fi
        
        export QVERIS_API_KEY="$qveris_key"
        echo -e "${GREEN}✓ QVeris API Key 已保存${NC}"
    else
        echo "跳过 QVeris 配置（稍后可在监控提示中配置）"
    fi
    echo ""
}

# 询问是否重启
ask_restart() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ -n "$TAVILY_API_KEY" ] || ([ -n "$tavily_key" ] && [ -n "$qveris_key" ]); then
        echo -e "${GREEN}✓ 配置完成！${NC}"
        echo ""
        echo "为使配置生效，建议重启 OpenClaw Gateway："
        echo ""
        echo "  openclaw gateway restart"
        echo ""
        echo "或者发送任意消息给我，我将自动加载新配置。"
    else
        echo -e "${YELLOW}⚠ 配置未完成${NC}"
        echo "监控功能需要 Tavily API Key 才能使用。"
        echo ""
        echo "您可以："
        echo "  1. 再次运行 /config 完成配置"
        echo "  2. 手动编辑 ~/.openclaw/.env 文件"
    fi
    
    echo ""
}

# 快速配置模式（非交互式）
quick_setup() {
    local key="$1"
    local service="$2"
    
    if [ "$service" = "tavily" ]; then
        if grep -q "TAVILY_API_KEY" ~/.openclaw/.env 2>/dev/null; then
            sed -i "s/TAVILY_API_KEY=.*/TAVILY_API_KEY=${key}/" ~/.openclaw/.env
        else
            echo "TAVILY_API_KEY=${key}" >> ~/.openclaw/.env
        fi
        export TAVILY_API_KEY="$key"
        echo "✓ Tavily API Key 已配置"
        
    elif [ "$service" = "qveris" ]; then
        if grep -q "QVERIS_API_KEY" ~/.openclaw/.env 2>/dev/null; then
            sed -i "s/QVERIS_API_KEY=.*/QVERIS_API_KEY=${key}/" ~/.openclaw/.env
        else
            echo "QVERIS_API_KEY=${key}" >> ~/.openclaw/.env
        fi
        export QVERIS_API_KEY="$key"
        echo "✓ QVeris API Key 已配置"
    fi
}

# 主流程
main() {
    show_header
    check_current_status
    
    # 如果都已经配置，显示完成状态
    if [ -n "$TAVILY_API_KEY" ] && [ -n "$QVERIS_API_KEY" ]; then
        echo -e "${GREEN}🎉 所有配置已完成！${NC}"
        echo ""
        echo "您现在可以使用完整的监控功能："
        echo "  • /cue 主题 → 启动研究并生成监控建议"
        echo "  • 回复 Y → 自动创建监控"
        echo "  • /ct → 查看任务和监控状态"
        echo ""
        return 0
    fi
    
    # Tavily 必需
    if [ -z "$TAVILY_API_KEY" ]; then
        setup_tavily
    fi
    
    # QVeris 可选
    if [ -z "$QVERIS_API_KEY" ]; then
        echo "是否现在配置 QVeris（可选，推荐）？"
        read -p "[Y/n] " choice
        if [ "$choice" != "n" ] && [ "$choice" != "N" ]; then
            setup_qveris
        fi
    fi
    
    ask_restart
}

# 处理命令行参数
if [ "$1" = "--quick" ] && [ -n "$2" ] && [ -n "$3" ]; then
    quick_setup "$2" "$3"
elif [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main
fi
