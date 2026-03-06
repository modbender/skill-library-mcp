#!/bin/bash

# NightPatch Skill 启动脚本
# 基于虾聊社区「夜间自动修补」理念开发

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 技能目录
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SKILL_DIR}/logs"
REPORT_DIR="${SKILL_DIR}/reports"

# 显示帮助信息
show_help() {
    echo -e "${BLUE}NightPatch Skill - 夜间自动修补${NC}"
    echo "基于虾聊社区热门帖子「试了一下「夜间自动修补」，Master 早上起来直接用上了」开发"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  run          运行夜间修补（手动触发）"
    echo "  test         运行测试"
    echo "  dry-run      干运行（只检测不执行）"
    echo "  report       查看最新报告"
    echo "  logs         查看日志"
    echo "  config       查看配置"
    echo "  status       查看状态"
    echo "  install      安装依赖"
    echo "  help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 run        # 手动运行夜间修补"
    echo "  $0 test       # 运行测试"
    echo "  $0 status     # 查看技能状态"
}

# 检查Node.js
check_nodejs() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: Node.js 未安装${NC}"
        echo "请先安装 Node.js (>=14.0.0)"
        exit 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ $NODE_MAJOR -lt 14 ]; then
        echo -e "${YELLOW}警告: Node.js 版本过低 (${NODE_VERSION})，建议升级到 14.0.0 或更高版本${NC}"
    fi
}

# 安装依赖
install_deps() {
    echo -e "${BLUE}安装依赖...${NC}"
    
    cd "$SKILL_DIR"
    
    if [ -f "package.json" ]; then
        if command -v npm &> /dev/null; then
            npm install
            echo -e "${GREEN}依赖安装完成${NC}"
        else
            echo -e "${YELLOW}警告: npm 未安装，跳过依赖安装${NC}"
        fi
    else
        echo -e "${YELLOW}警告: package.json 不存在${NC}"
    fi
}

# 创建目录结构
create_dirs() {
    echo -e "${BLUE}创建目录结构...${NC}"
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$REPORT_DIR"
    mkdir -p "$SKILL_DIR/logs/night-patch"
    mkdir -p "$SKILL_DIR/reports/night-patch"
    
    echo -e "${GREEN}目录创建完成${NC}"
}

# 运行测试
run_tests() {
    echo -e "${BLUE}运行测试...${NC}"
    
    cd "$SKILL_DIR"
    
    if [ -f "tests/basic.test.js" ]; then
        node tests/basic.test.js
    else
        echo -e "${YELLOW}警告: 测试文件不存在${NC}"
    fi
}

# 手动运行夜间修补
run_night_patch() {
    echo -e "${BLUE}手动运行夜间修补...${NC}"
    
    cd "$SKILL_DIR"
    
    if [ -f "src/index.js" ]; then
        node src/index.js --manual
    else
        echo -e "${RED}错误: 主入口文件不存在${NC}"
        exit 1
    fi
}

# 干运行（只检测不执行）
run_dry_run() {
    echo -e "${BLUE}干运行模式（只检测不执行）...${NC}"
    
    cd "$SKILL_DIR"
    
    # 创建临时配置文件
    TEMP_CONFIG=$(mktemp)
    cat > "$TEMP_CONFIG" << EOF
schedule:
  enabled: true
  time: "03:00"

safety:
  max_changes_per_night: 0  # 设置为0表示不执行任何修补
  require_rollback: true
  dry_run_first: true

detectors:
  shell_alias:
    enabled: true
  note_organization:
    enabled: true
EOF
    
    echo "使用临时配置文件: $TEMP_CONFIG"
    echo "运行检测器..."
    
    # 这里应该调用相应的函数，简化处理
    node -e "
const PatchDetector = require('./src/patch-detector');
const config = require('yaml').parse(require('fs').readFileSync('$TEMP_CONFIG', 'utf8'));
const detector = new PatchDetector(config);

async function run() {
    const opportunities = await detector.runAllDetectors();
    console.log('\\n检测完成:');
    console.log('='.repeat(50));
    opportunities.forEach((opp, i) => {
        console.log(\`\${i+1}. \${opp.description}\`);
        console.log(\`   类型: \${opp.type}, 风险: \${opp.risk_level}\`);
        if (opp.rollback_command) {
            console.log(\`   回滚: \${opp.rollback_command}\`);
        }
    });
    console.log('='.repeat(50));
    console.log(\`总计: \${opportunities.length} 个机会\`);
}

run().catch(console.error);
"
    
    rm -f "$TEMP_CONFIG"
}

# 查看最新报告
show_latest_report() {
    echo -e "${BLUE}查找最新报告...${NC}"
    
    if [ -d "$REPORT_DIR/night-patch" ]; then
        LATEST_REPORT=$(ls -t "$REPORT_DIR/night-patch/"*.md 2>/dev/null | head -1)
        
        if [ -n "$LATEST_REPORT" ]; then
            echo -e "${GREEN}最新报告: $LATEST_REPORT${NC}"
            echo ""
            head -50 "$LATEST_REPORT"
            echo ""
            echo -e "${YELLOW}... (完整报告请查看文件)${NC}"
        else
            echo -e "${YELLOW}暂无报告${NC}"
        fi
    else
        echo -e "${YELLOW}报告目录不存在${NC}"
    fi
}

# 查看日志
show_logs() {
    echo -e "${BLUE}查看日志...${NC}"
    
    if [ -d "$LOG_DIR" ]; then
        LOG_FILES=$(find "$LOG_DIR" -name "*.log" -type f)
        
        if [ -n "$LOG_FILES" ]; then
            for log in $LOG_FILES; do
                echo -e "${GREEN}日志文件: $log${NC}"
                echo "最后10行:"
                tail -10 "$log"
                echo ""
            done
        else
            echo -e "${YELLOW}暂无日志文件${NC}"
        fi
    else
        echo -e "${YELLOW}日志目录不存在${NC}"
    fi
}

# 查看配置
show_config() {
    echo -e "${BLUE}查看配置...${NC}"
    
    CONFIG_FILE="$SKILL_DIR/config/default.yaml"
    
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${GREEN}配置文件: $CONFIG_FILE${NC}"
        echo ""
        head -100 "$CONFIG_FILE"
        echo ""
        echo -e "${YELLOW}... (完整配置请查看文件)${NC}"
    else
        echo -e "${YELLOW}配置文件不存在${NC}"
    fi
}

# 查看状态
show_status() {
    echo -e "${BLUE}技能状态检查...${NC}"
    
    # 检查Node.js
    if command -v node &> /dev/null; then
        echo -e "${GREEN}✅ Node.js: $(node -v)${NC}"
    else
        echo -e "${RED}❌ Node.js: 未安装${NC}"
    fi
    
    # 检查主文件
    if [ -f "$SKILL_DIR/src/index.js" ]; then
        echo -e "${GREEN}✅ 主文件: 存在${NC}"
    else
        echo -e "${RED}❌ 主文件: 不存在${NC}"
    fi
    
    # 检查配置文件
    if [ -f "$SKILL_DIR/config/default.yaml" ]; then
        echo -e "${GREEN}✅ 配置文件: 存在${NC}"
    else
        echo -e "${YELLOW}⚠️  配置文件: 不存在${NC}"
    fi
    
    # 检查报告目录
    if [ -d "$REPORT_DIR/night-patch" ]; then
        REPORT_COUNT=$(ls "$REPORT_DIR/night-patch/"*.md 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ 报告目录: 存在 (${REPORT_COUNT} 个报告)${NC}"
    else
        echo -e "${YELLOW}⚠️  报告目录: 不存在${NC}"
    fi
    
    # 检查日志目录
    if [ -d "$LOG_DIR/night-patch" ]; then
        LOG_COUNT=$(find "$LOG_DIR/night-patch" -name "*.log" -type f 2>/dev/null | wc -l)
        echo -e "${GREEN}✅ 日志目录: 存在 (${LOG_COUNT} 个日志文件)${NC}"
    else
        echo -e "${YELLOW}⚠️  日志目录: 不存在${NC}"
    fi
    
    # 检查技能文档
    if [ -f "$SKILL_DIR/SKILL.md" ]; then
        echo -e "${GREEN}✅ 技能文档: 存在${NC}"
    else
        echo -e "${YELLOW}⚠️  技能文档: 不存在${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}技能信息:${NC}"
    echo "  名称: NightPatch - 夜间自动修补"
    echo "  版本: 1.0.0"
    echo "  作者: OpenClaw Assistant"
    echo "  灵感: 虾聊社区「夜间自动修补」帖子"
    echo "  状态: 开发完成，可手动运行"
}

# 主函数
main() {
    check_nodejs
    
    case "${1:-help}" in
        run)
            run_night_patch
            ;;
        test)
            run_tests
            ;;
        dry-run)
            run_dry_run
            ;;
        report)
            show_latest_report
            ;;
        logs)
            show_logs
            ;;
        config)
            show_config
            ;;
        status)
            show_status
            ;;
        install)
            install_deps
            create_dirs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知命令 '$1'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"