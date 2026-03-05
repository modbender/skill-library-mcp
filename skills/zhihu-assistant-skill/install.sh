#!/bin/bash
# 知乎助手 Skill 安装脚本

set -e

echo "=== 安装知乎助手 Skill ==="

# 获取 skill 目录
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace/zhihu-assistant"

echo "1. 创建工作目录: $WORKSPACE_DIR"
mkdir -p "$WORKSPACE_DIR"
mkdir -p "$WORKSPACE_DIR/data"
mkdir -p "$WORKSPACE_DIR/logs"

# 复制核心文件
echo "2. 复制核心文件..."
cp -r "$SKILL_DIR"/*.py "$WORKSPACE_DIR/"
cp -r "$SKILL_DIR/modules" "$WORKSPACE_DIR/"

# 安装依赖
echo "3. 安装 Python 依赖..."
pip3 install -q pyyaml requests httpx openai 2>/dev/null || pip3 install --break-system-packages -q pyyaml requests httpx openai 2>/dev/null || {
    echo "   警告: pip 安装失败，请手动安装: pyyaml requests httpx openai"
}

# 创建启动脚本
echo "4. 创建快捷命令..."
mkdir -p "$HOME/.openclaw/skills/zhihu-assistant"

cat > "$HOME/.openclaw/skills/zhihu-assistant/zhihu" << 'EOF'
#!/bin/bash
# 知乎助手快捷命令

WORKSPACE_DIR="$HOME/.openclaw/workspace/zhihu-assistant"

# 检查工作目录是否存在
if [ ! -d "$WORKSPACE_DIR" ]; then
    echo "错误: 知乎助手未安装"
    exit 1
fi

cd "$WORKSPACE_DIR"

COMMAND=$1
shift

case $COMMAND in
    fetch)
        python3 main.py fetch "$@"
        ;;
    stats)
        python3 main.py stats
        ;;
    notify)
        python3 main.py notify
        ;;
    logs)
        python3 main.py logs
        ;;
    reject)
        python3 main.py reject "$@"
        ;;
    config)
        echo "配置文件路径: $WORKSPACE_DIR/config.yaml"
        echo ""
        echo "当前配置（从 OpenClaw 读取）:"
        openclaw config get skills.zhihu-assistant 2>/dev/null || echo "  暂无配置"
        ;;
    help|--help|-h|*)
        echo "知乎助手 - 热榜抓取与内容管理"
        echo ""
        echo "使用: openclaw zhihu <command> [options]"
        echo ""
        echo "Commands:"
        echo "  fetch [--limit N]     抓取热榜并生成草稿"
        echo "  stats                 查看统计信息"
        echo "  notify                获取待推送列表"
        echo "  logs                  查看操作日志"
        echo "  reject --id ID        拒绝草稿"
        echo "  config                查看配置"
        echo "  help                  显示帮助"
        echo ""
        echo "配置方法:"
        echo "  openclaw config set skills.zhihu-assistant.zhihu_cookie 'xxx'"
        echo "  openclaw config set skills.zhihu-assistant.kimi_api_key 'xxx'"
        echo "  openclaw config set skills.zhihu-assistant.feishu_user_id 'xxx'"
        ;;
esac
EOF

chmod +x "$HOME/.openclaw/skills/zhihu-assistant/zhihu"

# 创建 tools 目录的快捷方式
mkdir -p "$SKILL_DIR/tools"
ln -sf "$HOME/.openclaw/skills/zhihu-assistant/zhihu" "$SKILL_DIR/tools/zhihu" 2>/dev/null || true

echo ""
echo "=== 安装完成 ==="
echo ""
echo "工作目录: $WORKSPACE_DIR"
echo ""
echo "使用前请先配置:"
echo "  openclaw config set skills.zhihu-assistant.zhihu_cookie 'your_cookie'"
echo "  openclaw config set skills.zhihu-assistant.kimi_api_key 'your_api_key'"
echo "  openclaw config set skills.zhihu-assistant.feishu_user_id 'your_user_id'"
echo ""
echo "使用命令:"
echo "  openclaw zhihu fetch --limit 10    # 抓取热榜"
echo "  openclaw zhihu stats               # 查看统计"
echo "  openclaw zhihu notify              # 推送到飞书"
echo "  openclaw zhihu help                # 显示帮助"
echo ""
