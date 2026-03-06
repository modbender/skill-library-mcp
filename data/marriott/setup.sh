#!/bin/bash
set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Skill 目录：$SKILL_DIR"

# 安装 Node 依赖
echo "安装依赖..."
cd "$SKILL_DIR"
npm install

# 安装 Playwright Chromium
npx playwright install chromium

# 初始化 .env
if [ ! -f "$SKILL_DIR/.env" ]; then
  cp "$SKILL_DIR/.env.example" "$SKILL_DIR/.env"
  echo "已创建 .env（当前版本无需填写账号，保留备用）"
else
  echo ".env 已存在，跳过"
fi

echo ""
echo "Setup 完成！使用步骤："
echo "  1. bash \"$SKILL_DIR/launch-chrome.sh\"  # 启动 Chrome"
echo "  2. 在 Chrome 中打开并登录 marriott.com.cn"
echo "  3. 在任意目录运行 claude，使用 /marriott 呼叫 skill"
