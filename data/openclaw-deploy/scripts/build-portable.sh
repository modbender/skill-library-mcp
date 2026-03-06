#!/bin/bash
# OpenClaw Portable Package Builder v1.0.1
# 支持自定义路径配置

set -e

VERSION="1.0.1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/../templates"

# 默认配置（可通过环境变量覆盖）
: "${OPENCLAW_INSTALL_DIR:=/home/$(whoami)/.nvm/versions/node/v22.22.0/lib/node_modules/openclaw}"
: "${OPENCLAW_CONFIG_DIR:=/home/$(whoami)/.openclaw}"
: "${OUTPUT_DIR:=$(pwd)/openclaw-portable-output}"
: "${CLEAN_CONFIG_FILE:=${SCRIPT_DIR}/../clean/config/openclaw.json}"

echo "=========================================="
echo "OpenClaw Portable Package Builder v${VERSION}"
echo "=========================================="

# 检查模板目录
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "❌ 模板目录不存在: $TEMPLATE_DIR"
    exit 1
fi

# 检查依赖
echo ""
echo "🔍 检查依赖..."
if ! command -v cp >/dev/null 2>&1 || ! command -v mkdir >/dev/null 2>&1; then
    echo "❌ 缺少必要工具 (cp, mkdir)"
    exit 1
fi
echo "  ✅ 依赖检查通过"

# 检查源文件
echo ""
echo "📁 检查源文件..."
if [ ! -d "$OPENCLAW_INSTALL_DIR" ]; then
    echo "  ❌ OpenClaw 安装目录不存在: $OPENCLAW_INSTALL_DIR"
    echo "     可通过环境变量设置:"
    echo "     export OPENCLAW_INSTALL_DIR=/path/to/openclaw"
    exit 1
fi
echo "  ✅ OpenClaw 安装目录: $OPENCLAW_INSTALL_DIR"

if [ ! -d "$OPENCLAW_CONFIG_DIR" ]; then
    echo "  ⚠️  配置目录不存在: $OPENCLAW_CONFIG_DIR"
else
    echo "  ✅ 配置目录: $OPENCLAW_CONFIG_DIR"
fi

# 显示配置
echo ""
echo "⚙️  当前配置:"
echo "    OpenClaw 安装: $OPENCLAW_INSTALL_DIR"
echo "    配置目录: $OPENCLAW_CONFIG_DIR"
echo "    输出目录: $OUTPUT_DIR"

# 准备目录
echo ""
echo "🗂️  准备输出目录..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/clean/openclaw/app"
mkdir -p "$OUTPUT_DIR/clean/openclaw/.openclaw"
mkdir -p "$OUTPUT_DIR/full/openclaw/app"
mkdir -p "$OUTPUT_DIR/full/openclaw/.openclaw"
echo "  ✅ 目录创建完成"

# 构建纯净版
echo ""
echo "📦 构建纯净版..."
cp -r "$OPENCLAW_INSTALL_DIR"/* "$OUTPUT_DIR/clean/openclaw/app/"
echo "  ✅ 复制 OpenClaw 应用"

if [ -f "$CLEAN_CONFIG_FILE" ]; then
    cp "$CLEAN_CONFIG_FILE" "$OUTPUT_DIR/clean/openclaw/.openclaw/"
    echo "  ✅ 复制纯净版配置"
else
    echo "  ⚠️  使用默认配置"
fi

cp "$TEMPLATE_DIR/start-clean.sh" "$OUTPUT_DIR/clean/start.sh"
chmod +x "$OUTPUT_DIR/clean/start.sh"
echo "  ✅ 创建启动脚本"

# 构建完整版
echo ""
echo "📦 构建完整版..."
cp -r "$OPENCLAW_INSTALL_DIR"/* "$OUTPUT_DIR/full/openclaw/app/"
echo "  ✅ 复制 OpenClaw 应用"

if [ -d "$OPENCLAW_CONFIG_DIR" ]; then
    cp -r "$OPENCLAW_CONFIG_DIR"/* "$OUTPUT_DIR/full/openclaw/.openclaw/" 2>/dev/null || true
    echo "  ✅ 复制完整配置"
else
    echo "  ⚠️  配置目录不存在，跳过"
fi

cp "$TEMPLATE_DIR/start-full.sh" "$OUTPUT_DIR/full/start.sh"
chmod +x "$OUTPUT_DIR/full/start.sh"
echo "  ✅ 创建启动脚本"

# 复制辅助文件
echo ""
echo "📄 创建辅助文件..."
cp "$TEMPLATE_DIR/install-node.sh" "$OUTPUT_DIR/" 2>/dev/null || echo "  ⚠️  install-node.sh 模板不存在"
cp "$TEMPLATE_DIR/check-env.sh" "$OUTPUT_DIR/" 2>/dev/null || echo "  ⚠️  check-env.sh 模板不存在"
cp "$TEMPLATE_DIR/README.md" "$OUTPUT_DIR/" 2>/dev/null || echo "  ⚠️  README.md 模板不存在"
echo "  ✅ 辅助文件创建完成"

# 显示结果
echo ""
echo "=========================================="
echo "✅ 构建完成！"
echo "=========================================="
echo ""
echo "📁 输出目录: $OUTPUT_DIR"
echo ""
echo "文件列表:"
ls -la "$OUTPUT_DIR/" 2>/dev/null || echo "  (目录为空)"
echo ""
echo "目录大小:"
du -sh "$OUTPUT_DIR/clean" "$OUTPUT_DIR/full" 2>/dev/null || true
