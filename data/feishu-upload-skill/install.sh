#!/bin/bash
# Feishu Upload Skill 安装脚本

set -e

echo "🚀 开始安装 Feishu Upload Skill"
echo "=================================================="

# 检查Node.js版本
NODE_VERSION=$(node --version | cut -d'v' -f2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

if [[ $NODE_MAJOR -lt 18 ]]; then
    echo "❌ 错误: 需要 Node.js 18+，当前版本: $NODE_VERSION"
    echo "请升级 Node.js: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js 版本: $NODE_VERSION"

# 检查OpenClaw配置
CONFIG_FILE="/home/node/.openclaw/openclaw.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ 错误: 找不到 OpenClaw 配置文件: $CONFIG_FILE"
    exit 1
fi

echo "✅ 找到 OpenClaw 配置文件"

# 检查飞书配置
FEISHU_CONFIG=$(grep -A5 '"feishu"' "$CONFIG_FILE" || true)
if [[ -z "$FEISHU_CONFIG" ]]; then
    echo "⚠️  警告: 未找到飞书配置，技能可能无法正常工作"
    echo "请确保在 OpenClaw 中配置了飞书通道"
fi

# 创建技能目录
SKILLS_DIR="/home/node/.openclaw/workspace/skills"
if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "创建技能目录: $SKILLS_DIR"
    mkdir -p "$SKILLS_DIR"
fi

# 复制技能文件
SKILL_NAME="feishu-upload"
TARGET_DIR="$SKILLS_DIR/$SKILL_NAME"

if [[ -d "$TARGET_DIR" ]]; then
    echo "⚠️  技能已存在，备份旧版本..."
    BACKUP_DIR="${TARGET_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    mv "$TARGET_DIR" "$BACKUP_DIR"
    echo "已备份到: $BACKUP_DIR"
fi

echo "复制技能文件到: $TARGET_DIR"
cp -r "$(dirname "$0")" "$TARGET_DIR"

# 设置文件权限
chmod +x "$TARGET_DIR"/feishu_complete_upload.js
chmod +x "$TARGET_DIR"/get_feishu_token.sh
chmod +x "$TARGET_DIR"/install.sh

# 测试访问令牌
echo -e "\n🔑 测试飞书访问令牌..."
TOKEN_FILE="/home/node/.openclaw/workspace/feishu_token.txt"
if [[ -f "$TOKEN_FILE" ]]; then
    echo "✅ 找到现有访问令牌"
else
    echo "获取新的访问令牌..."
    cd "$TARGET_DIR" && ./get_feishu_token.sh
fi

# 创建测试文件
TEST_FILE="$TARGET_DIR/test_install.txt"
echo "这是 Feishu Upload Skill 的安装测试文件" > "$TEST_FILE"
echo "安装时间: $(date)" >> "$TEST_FILE"

echo -e "\n🧪 测试技能功能..."
cd "$TARGET_DIR"

# 测试上传功能（不上传，只检查）
echo "测试上传工具..."
if node feishu_complete_upload.js --help 2>&1 | grep -q "用法"; then
    echo "✅ 上传工具测试通过"
else
    # 尝试运行工具
    if node feishu_complete_upload.js test_install.txt 2>&1 | grep -q "上传成功"; then
        echo "✅ 上传功能测试通过"
    else
        echo "⚠️  上传功能测试未完成，但工具可以运行"
    fi
fi

# 清理测试文件
rm -f "$TEST_FILE"

echo -e "\n🎉 Feishu Upload Skill 安装完成!"
echo "=================================================="
echo ""
echo "📖 使用说明:"
echo "1. 上传文件到飞书:"
echo "   node $TARGET_DIR/feishu_complete_upload.js <文件路径> <聊天ID>"
echo ""
echo "2. 仅上传文件:"
echo "   node $TARGET_DIR/feishu_complete_upload.js <文件路径>"
echo ""
echo "3. 获取访问令牌:"
echo "   $TARGET_DIR/get_feishu_token.sh"
echo ""
echo "4. 查看完整文档:"
echo "   cat $TARGET_DIR/SKILL.md"
echo ""
echo "💡 示例:"
echo "   node $TARGET_DIR/feishu_complete_upload.js document.txt oc_dd899cb1a7846915cdd2d6850bd1dafa"
echo ""
echo "🔧 技能位置: $TARGET_DIR"
echo "📁 配置文件: $CONFIG_FILE"
echo "🔑 令牌文件: $TOKEN_FILE"
echo ""
echo "✅ 安装完成，可以开始使用 Feishu Upload Skill 了!"