#!/bin/bash
# Kim Channel 快速配置脚本
# 交互式配置 Kim Channel 插件

set -e

echo "=== Kim Channel 快速配置 ==="
echo ""

# 检查是否安装了插件
if ! openclaw plugins list 2>/dev/null | grep -q "kim"; then
    echo "⚠️  Kim 插件未安装"
    read -p "是否现在安装? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在安装插件..."
        export npm_config_registry="https://npm.corp.kuaishou.com"
        openclaw plugins install @ks-openclaw/kim
    else
        echo "请先安装插件后再运行此脚本"
        exit 1
    fi
fi

echo ""
echo "请准备好以下信息："
echo "  1. appKey - 从 OpenApi 服务平台获取"
echo "  2. secretKey - 从 OpenApi 服务平台获取"
echo "  3. verificationToken - 从 Kim 开放平台获取"
echo ""

# 交互式输入
read -p "请输入 appKey: " APP_KEY
read -p "请输入 secretKey: " SECRET_KEY
read -p "请输入 verificationToken: " VERIFICATION_TOKEN
read -p "请输入 webhookPath (默认 /kim): " WEBHOOK_PATH
WEBHOOK_PATH=${WEBHOOK_PATH:-/kim}

echo ""
echo "即将配置以下内容："
echo "  appKey: ${APP_KEY:0:8}..."
echo "  secretKey: ${SECRET_KEY:0:8}..."
echo "  verificationToken: ${VERIFICATION_TOKEN:0:8}..."
echo "  webhookPath: $WEBHOOK_PATH"
echo ""

read -p "确认配置? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "配置已取消"
    exit 0
fi

# 执行配置
echo "正在配置..."
openclaw config set channels.kim.appKey "$APP_KEY"
openclaw config set channels.kim.secretKey "$SECRET_KEY"
openclaw config set channels.kim.verificationToken "$VERIFICATION_TOKEN"
openclaw config set channels.kim.webhookPath "$WEBHOOK_PATH"

echo ""
echo "✅ 配置完成！"
echo ""

read -p "是否重启网关? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在重启网关..."
    openclaw gateway restart
    echo "✅ 网关已重启"
fi

echo ""
echo "现在可以通过 Kim 给 OpenClaw 发送消息了！"
