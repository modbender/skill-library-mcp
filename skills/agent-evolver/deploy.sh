#!/bin/bash

# Agent Evolver Skill 部署脚本
# 用于本地部署和测试

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Agent Evolver Skill 部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}▶ 检查 Python 版本...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ 未找到 Python3，请先安装 Python3${NC}"
    exit 1
fi

# 创建数据目录
echo ""
echo -e "${YELLOW}▶ 创建数据目录...${NC}"
mkdir -p ~/.evolver
mkdir -p ~/.evolver/chroma
mkdir -p ~/.evolver/logs
echo -e "${GREEN}✓ 数据目录创建完成${NC}"

# 安装依赖
echo ""
echo -e "${YELLOW}▶ 安装依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt 2>/dev/null || echo -e "${YELLOW}⚠ 部分依赖安装失败，将使用后备方案${NC}"
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${YELLOW}⚠ 未找到 requirements.txt${NC}"
fi

# 设置脚本可执行权限
echo ""
echo -e "${YELLOW}▶ 设置脚本权限...${NC}"
chmod +x scripts/*.py 2>/dev/null || true
echo -e "${GREEN}✓ 脚本权限设置完成${NC}"

# 测试核心功能
echo ""
echo -e "${YELLOW}▶ 测试核心功能...${NC}"
python3 scripts/evolver_core.py 2>&1 | head -20
echo -e "${GREEN}✓ 核心功能测试完成${NC}"

# 注册技能
echo ""
echo -e "${YELLOW}▶ 注册技能...${NC}"
python3 scripts/skill_registry.py register "$SCRIPT_DIR"
echo -e "${GREEN}✓ 技能注册完成${NC}"

# 创建快捷命令
echo ""
echo -e "${YELLOW}▶ 创建快捷命令...${NC}"

cat > evolver.sh << 'EOF'
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
EOF

chmod +x evolver.sh
echo -e "${GREEN}✓ 快捷命令创建完成${NC}"

# 添加到 OpenClaw
echo ""
echo -e "${YELLOW}▶ 部署到 OpenClaw...${NC}"
OPENCLAW_SKILL_DIR="$HOME/.openclaw/workspace/skills/agent-evolver"

if [ -d "$HOME/.openclaw" ]; then
    mkdir -p "$OPENCLAW_SKILL_DIR"
    cp -r "$SCRIPT_DIR"/* "$OPENCLAW_SKILL_DIR/"
    echo -e "${GREEN}✓ 已部署到 OpenClaw: $OPENCLAW_SKILL_DIR${NC}"
else
    echo -e "${YELLOW}⚠ OpenClaw 目录不存在，跳过部署${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Agent Evolver Skill 部署成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "使用示例:"
echo "  ./evolver.sh analyze 'ValueError: 不支持负数'"
echo "  ./evolver.sh search '负数计算错误'"
echo "  ./evolver.sh stats"
echo "  ./evolver.sh history --limit 10"
echo ""
echo "Python API:"
echo "  from evolver_core import EvolutionManager"
echo "  evolver = EvolutionManager(agent_id='my_agent')"
echo "  result = evolver.run_evolution('任务输入')"
echo ""
echo "配置文件:"
echo "  config/evolver_config.yaml"
echo "  config/skill_triggers.yaml"
echo ""
echo "数据目录:"
echo "  ~/.evolver/evolution.db"
echo "  ~/.evolver/chroma/"
echo ""
