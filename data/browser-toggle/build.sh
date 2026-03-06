#!/bin/bash
# 发布脚本 - 创建 Skill 安装包

set -e

SKILL_NAME="browser-toggle"
SKILL_VERSION="1.0.0"
PACKAGE_NAME="${SKILL_NAME}-v${SKILL_VERSION}"
BUILD_DIR="/tmp/skill-build/$PACKAGE_NAME"
OUTPUT_DIR="$(pwd)/dist"

echo "========================================"
echo "构建 $SKILL_NAME v$SKILL_VERSION"
echo "========================================"
echo ""

# 清理旧构建
echo "🧹 清理旧构建..."
rm -rf "$BUILD_DIR" "$OUTPUT_DIR"
mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"

# 复制文件
echo "📦 复制文件..."
cp -r ./* "$BUILD_DIR/"

# 删除不必要的文件
echo "🗑️ 删除不必要的文件..."
rm -f "$BUILD_DIR"/*.pyc
rm -rf "$BUILD_DIR"/__pycache__
rm -f "$BUILD_DIR"/dist/*.tar.gz 2>/dev/null || true

# 创建 README
echo "📝 创建发布说明..."
cat > "$BUILD_DIR/RELEASE.md" << EOF
# $SKILL_NAME v$SKILL_VERSION 发布说明

## 📦 安装

\`\`\`bash
# 解压
tar -xzf $PACKAGE_NAME.tar.gz
cd $PACKAGE_NAME

# 安装
bash setup.sh
\`\`\`

## 🚀 快速开始

\`\`\`bash
# 启用内置浏览器
openclaw-browser --enable
openclaw gateway restart

# 查看状态
openclaw-browser --status
\`\`\`

## 📚 文档

- README.md - 项目说明
- INSTALL.md - 安装指南
- 使用指南.md - 详细使用文档

## 📞 支持

- GitHub: https://github.com/openclaw/openclaw
- 文档：https://docs.openclaw.ai

## 📋 变更日志

### v1.0.0 (2026-02-28)
- ✅ 首次发布
- ✅ 一键启用/禁用内置浏览器
- ✅ 自动备份配置
- ✅ 失败自动恢复
- ✅ 支持 Linux/macOS/Windows
EOF

# 创建压缩包
echo "📦 创建压缩包..."
cd /tmp/skill-build
tar -czf "$OUTPUT_DIR/$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

# 创建校验和
echo "🔐 创建校验和..."
cd "$OUTPUT_DIR"
sha256sum "$PACKAGE_NAME.tar.gz" > "$PACKAGE_NAME.tar.gz.sha256"

# 显示结果
echo ""
echo "========================================"
echo "✅ 构建完成！"
echo "========================================"
echo ""
echo "📦 发布包：$OUTPUT_DIR/$PACKAGE_NAME.tar.gz"
echo "🔐 校验和：$OUTPUT_DIR/$PACKAGE_NAME.tar.gz.sha256"
echo ""
echo "📊 文件大小："
ls -lh "$OUTPUT_DIR/$PACKAGE_NAME.tar.gz"
echo ""
echo "🔐 SHA256："
cat "$OUTPUT_DIR/$PACKAGE_NAME.tar.gz.sha256"
echo ""
echo "========================================"
