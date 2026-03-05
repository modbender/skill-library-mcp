#!/bin/bash
# xhs-mac-mcp 一键安装脚本

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== xhs-mac-mcp 安装 ==="
echo "Skill 目录: $SKILL_DIR"

# 1. 安装 Python 依赖
echo ""
echo "[1/3] 安装 Python 依赖..."
if command -v uv &>/dev/null; then
  cd "$SKILL_DIR" && uv sync
else
  pip install atomacos pyobjc-framework-Quartz pyobjc-framework-ApplicationServices
fi

# 2. 注册 OpenClaw Plugin
echo ""
echo "[2/3] 注册 OpenClaw Plugin..."
PLUGIN_DIR="$HOME/.openclaw/extensions/xhs-mac"
if [ -L "$PLUGIN_DIR" ]; then
  echo "  已存在软链接，跳过"
else
  ln -sf "$SKILL_DIR" "$PLUGIN_DIR"
  echo "  已创建: $PLUGIN_DIR -> $SKILL_DIR"
fi

# 3. 提示配置
echo ""
echo "[3/3] 完成！还需要手动执行："
echo ""
echo "  openclaw config set tools.allow '[\"xhs-mac\"]'"
echo "  openclaw gateway restart"
echo ""
echo "验证："
echo "  openclaw plugins list | grep xhs-mac"
echo ""
echo "⚠️  别忘了：系统设置 → 隐私与安全 → 辅助功能 → 开启 Terminal"
