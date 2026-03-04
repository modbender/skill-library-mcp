#!/bin/bash
# email-163-com 技能安装脚本
# 使用方法：curl -L <URL> | bash  或  bash install.sh

set -e

SKILL_NAME="email-163-com"
SKILL_URL="https://your-server.com/email-163-com.tar.gz"  # 替换为实际 URL
TARGET_DIR="$HOME/.openclaw/workspace/skills"

echo "📦 安装 $SKILL_NAME ..."

# 检查目标目录
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ OpenClaw 技能目录不存在：$TARGET_DIR"
    exit 1
fi

# 下载技能包
if command -v curl &> /dev/null; then
    curl -L "$SKILL_URL" -o "/tmp/$SKILL_NAME.tar.gz"
elif command -v wget &> /dev/null; then
    wget "$SKILL_URL" -O "/tmp/$SKILL_NAME.tar.gz"
else
    echo "❌ 需要 curl 或 wget"
    exit 1
fi

# 解压
echo "📂 解压到 $TARGET_DIR ..."
tar -xzf "/tmp/$SKILL_NAME.tar.gz" -C "$TARGET_DIR"

# 设置权限
chmod +x "$TARGET_DIR/$SKILL_NAME/email-163-com"
chmod +x "$TARGET_DIR/$SKILL_NAME/main.py"

# 验证安装
if [ -f "$TARGET_DIR/$SKILL_NAME/email-163-com" ]; then
    echo "✅ 安装成功！"
    echo ""
    echo "📚 使用帮助:"
    echo "   $TARGET_DIR/$SKILL_NAME/email-163-com --help"
    echo ""
    echo "🔧 配置文件:"
    echo "   ~/.config/email-163-com/config.json"
else
    echo "❌ 安装失败"
    exit 1
fi

# 清理
rm -f "/tmp/$SKILL_NAME.tar.gz"
