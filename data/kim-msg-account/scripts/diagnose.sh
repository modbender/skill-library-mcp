#!/bin/bash
# Kim Channel 诊断脚本
# 用于检查 Kim Channel 插件配置状态

set -e

echo "=== Kim Channel 诊断 ==="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. 检查插件安装
echo "1. 检查插件安装状态..."
if openclaw plugins list 2>/dev/null | grep -q "kim"; then
    check_pass "Kim 插件已安装"
else
    check_fail "Kim 插件未安装"
    echo "   运行: openclaw plugins install @ks-openclaw/kim"
fi
echo ""

# 2. 检查配置
echo "2. 检查配置..."

# appKey
APP_KEY=$(openclaw config get channels.kim.appKey 2>/dev/null || echo "")
if [ -n "$APP_KEY" ] && [ "$APP_KEY" != "null" ]; then
    check_pass "appKey 已配置: ${APP_KEY:0:8}..."
else
    check_fail "appKey 未配置"
fi

# secretKey
SECRET_KEY=$(openclaw config get channels.kim.secretKey 2>/dev/null || echo "")
if [ -n "$SECRET_KEY" ] && [ "$SECRET_KEY" != "null" ]; then
    check_pass "secretKey 已配置"
else
    check_fail "secretKey 未配置"
fi

# verificationToken
TOKEN=$(openclaw config get channels.kim.verificationToken 2>/dev/null || echo "")
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    check_pass "verificationToken 已配置"
else
    check_fail "verificationToken 未配置"
fi

# webhookPath
WEBHOOK_PATH=$(openclaw config get channels.kim.webhookPath 2>/dev/null || echo "")
if [ -n "$WEBHOOK_PATH" ] && [ "$WEBHOOK_PATH" != "null" ]; then
    check_pass "webhookPath: $WEBHOOK_PATH"
else
    check_warn "webhookPath 未配置，使用默认值 /kim"
fi
echo ""

# 3. 检查网关状态
echo "3. 检查网关状态..."
if openclaw gateway status 2>/dev/null | grep -q "running"; then
    check_pass "网关运行中"
else
    check_fail "网关未运行"
    echo "   运行: openclaw gateway restart"
fi
echo ""

# 4. 检查网络连通性
echo "4. 检查 webhook 端点..."
WEBHOOK_URL=$(openclaw config get channels.kim.webhookUrl 2>/dev/null || echo "")
if [ -z "$WEBHOOK_URL" ] || [ "$WEBHOOK_URL" = "null" ]; then
    # 尝试本地测试
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:18789/kim 2>/dev/null | grep -q "405\|200"; then
        check_pass "本地 webhook 端点可访问"
    else
        check_warn "无法访问本地 webhook 端点"
    fi
else
    if curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" 2>/dev/null | grep -q "405\|200"; then
        check_pass "webhook URL 可访问: $WEBHOOK_URL"
    else
        check_fail "webhook URL 不可访问: $WEBHOOK_URL"
    fi
fi
echo ""

echo "=== 诊断完成 ==="
