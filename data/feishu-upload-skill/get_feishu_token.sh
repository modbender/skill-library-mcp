#!/bin/bash
# 获取飞书访问令牌

APP_ID="cli_a90356d0f2b81cc7"
APP_SECRET="yAqFLNIrCLkqhDfz4Vr3ZcYcNtHzmHAK"

echo "App ID: $APP_ID"
echo "App Secret: ${APP_SECRET:0:10}..."

# 获取访问令牌
echo -e "\n获取访问令牌..."
RESPONSE=$(curl -s -X POST \
  "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}")

echo "响应: $RESPONSE"

# 解析响应
CODE=$(echo "$RESPONSE" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('code', '999'))")
TOKEN=$(echo "$RESPONSE" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('tenant_access_token', ''))")

if [ "$CODE" = "0" ] && [ -n "$TOKEN" ]; then
    echo -e "\n✅ 成功获取访问令牌!"
    echo "令牌: ${TOKEN:0:50}..."
    
    # 保存令牌到文件
    echo "$TOKEN" > /home/node/.openclaw/workspace/feishu_token.txt
    echo "令牌已保存到: /home/node/.openclaw/workspace/feishu_token.txt"
    
    # 测试使用令牌访问API
    echo -e "\n测试API访问..."
    TEST_RESPONSE=$(curl -s -X GET \
      "https://open.feishu.cn/open-apis/drive/v1/files" \
      -H "Authorization: Bearer $TOKEN")
    
    echo "API测试响应: $TEST_RESPONSE"
else
    echo -e "\n❌ 获取令牌失败"
    MSG=$(echo "$RESPONSE" | python3 -c "import json, sys; data=json.load(sys.stdin); print(data.get('msg', '未知错误'))")
    echo "错误信息: $MSG"
fi