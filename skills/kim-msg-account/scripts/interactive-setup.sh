#!/bin/bash
# Kim Channel 交互式配置脚本
# 自动安装插件 + 引导配置 + 可选自动配置

set -e

echo "=== Kim Channel 配置助手 ==="
echo ""
echo "👋 你好！我来帮你配置 Kim 消息渠道 💬"
echo ""

# 检查是否已安装插件
echo "🔍 检查插件状态..."
if openclaw plugins list 2>/dev/null | grep -q "kim"; then
    echo "✅ Kim 插件已安装"
    PLUGIN_INSTALLED=true
else
    echo "❌ Kim 插件未安装"
    PLUGIN_INSTALLED=false
fi

echo ""

# 询问是否安装插件
if [ "$PLUGIN_INSTALLED" = false ]; then
    read -p "是否现在安装 Kim 插件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在安装插件..."
        export npm_config_registry="https://npm.corp.kuaishou.com"
        openclaw plugins install @ks-openclaw/kim
        echo "✅ 插件安装完成"
    else
        echo "请先安装插件后再运行此脚本"
        echo "运行：openclaw plugins install @ks-openclaw/kim"
        exit 1
    fi
fi

echo ""
echo "📋 配置方式选择："
echo "1️⃣  自动配置（需要提供凭证，我会帮你完成所有配置）"
echo "2️⃣  手动配置（我会给你命令，你自己执行）"
echo ""

read -p "请选择 (1/2): " CONFIG_MODE

if [ "$CONFIG_MODE" = "1" ]; then
    echo ""
    echo "好的！请提供以下信息："
    echo ""
    
    read -p "appKey: " APP_KEY
    read -p "secretKey: " SECRET_KEY
    read -p "verificationToken: " VERIFICATION_TOKEN
    read -p "webhookPath (默认 /kim): " WEBHOOK_PATH
    WEBHOOK_PATH=${WEBHOOK_PATH:-/kim}
    
    echo ""
    echo "即将配置以下内容："
    echo "  appKey: ${APP_KEY:0:8}..."
    echo "  secretKey: ${SECRET_KEY:0:8}..."
    echo "  verificationToken: ${VERIFICATION_TOKEN:0:8}..."
    echo "  webhookPath: $WEBHOOK_PATH"
    echo ""
    
    read -p "确认配置？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 配置已取消"
        exit 0
    fi
    
    echo ""
    echo "正在配置..."
    openclaw config set channels.kim.appKey "$APP_KEY"
    openclaw config set channels.kim.secretKey "$SECRET_KEY"
    openclaw config set channels.kim.verificationToken "$VERIFICATION_TOKEN"
    openclaw config set channels.kim.webhookPath "$WEBHOOK_PATH"
    
    echo "✅ 配置完成！"
    echo ""
    
    read -p "是否重启网关？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在重启网关..."
        openclaw gateway restart
        echo "✅ 网关已重启"
    fi
    
    echo ""
    echo "🎉 全部完成！现在可以在 Kim 中测试了～"
    
else
    echo ""
    echo "好的！请按照以下步骤手动配置："
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "第 1 步：配置凭证"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "openclaw config set channels.kim.appKey \"<你的 appKey>\""
    echo "openclaw config set channels.kim.secretKey \"<你的 secretKey>\""
    echo "openclaw config set channels.kim.verificationToken \"<你的 verificationToken>\""
    echo "openclaw config set channels.kim.webhookPath \"/kim\""
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "第 2 步：重启网关"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "openclaw gateway restart"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "配置完成后，运行以下命令验证："
    echo "  openclaw config get channels.kim"
    echo ""
fi
