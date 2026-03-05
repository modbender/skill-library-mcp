#!/bin/bash
# 飞书日历管理器 - 配置向导
# 帮助用户配置飞书凭证

set -e

CONFIG_FILE="${HOME}/.feishu-config.json"
EXAMPLE_FILE="$(dirname "$0")/feishu-config.example.json"

echo "=== 飞书日历管理器 - 配置向导 ==="
echo ""

# 检查是否已存在配置
if [ -f "$CONFIG_FILE" ]; then
  echo "⚠️  检测到已存在的配置文件: $CONFIG_FILE"
  read -p "是否覆盖？(y/N): " -n 1 -r
  echo ""
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "配置已取消"
    exit 0
  fi
  cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"
  echo "已备份原配置到: ${CONFIG_FILE}.backup"
  echo ""
fi

echo "请输入你的飞书应用凭证："
echo ""

# 提示用户参考文档
echo "💡 提示："
echo "1. 访问 https://open.feishu.cn/ 创建自定义应用"
echo "2. 在应用凭证页面获取 App ID 和 App Secret"
echo "3. 开通日历权限：calendar:calendar.event:create 和 calendar:calendar.event:delete"
echo "4. 查阅 SKILL.md 获取日历 ID 和用户 Open ID 的详细步骤"
echo ""

# 读取凭证
read -p "App ID: " APP_ID
read -p "App Secret: " APP_SECRET
read -p "日历 ID (calendar_id): " CALENDAR_ID
read -p "用户 Open ID: " USER_ID

# 验证输入
if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ] || [ -z "$CALENDAR_ID" ] || [ -z "$USER_ID" ]; then
  echo "❌ 所有字段都必须填写！"
  exit 1
fi

# 创建配置文件
cat > "$CONFIG_FILE" << EOF
{
  "app_id": "$APP_ID",
  "app_secret": "$APP_SECRET",
  "calendar_id": "$CALENDAR_ID",
  "default_user_id": "$USER_ID"
}
EOF

# 设置权限
chmod 600 "$CONFIG_FILE"

echo ""
echo "✅ 配置文件已创建: $CONFIG_FILE"
echo "权限已设置为 600（仅所有者可读写）"
echo ""
echo "🔒 安全提示："
echo "- 请勿将此配置文件分享给他人"
echo "- 配置文件包含敏感信息，请妥善保管"
echo "- 如果使用 Git，请确保将 ~/.feishu-config.json 添加到 .gitignore"
echo ""
echo "🎉 配置完成！现在可以使用飞书日历管理器了。"
