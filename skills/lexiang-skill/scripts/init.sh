#!/bin/bash
# 乐享知识库凭证加载和 Token 获取脚本
# 优先级：环境变量 > openclaw.json (env) > ~/.config/lexiang/credentials
#
# 使用方式：source scripts/init.sh
# 执行后可使用 $LEXIANG_TOKEN 和 $LEXIANG_STAFF_ID 变量

# 1. 检查环境变量（openclaw 会自动从 env 字段注入）
if [ -n "$LEXIANG_APP_KEY" ] && [ -n "$LEXIANG_APP_SECRET" ]; then
  echo "使用环境变量中的凭证"
  if [ -z "$LEXIANG_STAFF_ID" ]; then
    if [ -f ~/.openclaw/openclaw.json ]; then
      STAFF_ID=$(jq -r '.skills.entries.lexiang.env.LEXIANG_STAFF_ID // empty' ~/.openclaw/openclaw.json 2>/dev/null)
      if [ -n "$STAFF_ID" ]; then
        export LEXIANG_STAFF_ID="$STAFF_ID"
      fi
    fi
  fi

# 2. 检查 openclaw.json 的 env 配置
elif [ -f ~/.openclaw/openclaw.json ]; then
  APP_KEY=$(jq -r '.skills.entries.lexiang.env.LEXIANG_APP_KEY // empty' ~/.openclaw/openclaw.json 2>/dev/null)
  APP_SECRET=$(jq -r '.skills.entries.lexiang.env.LEXIANG_APP_SECRET // empty' ~/.openclaw/openclaw.json 2>/dev/null)
  STAFF_ID=$(jq -r '.skills.entries.lexiang.env.LEXIANG_STAFF_ID // empty' ~/.openclaw/openclaw.json 2>/dev/null)
  
  if [ -n "$APP_KEY" ] && [ -n "$APP_SECRET" ]; then
    export LEXIANG_APP_KEY="$APP_KEY"
    export LEXIANG_APP_SECRET="$APP_SECRET"
    if [ -n "$STAFF_ID" ]; then
      export LEXIANG_STAFF_ID="$STAFF_ID"
    fi
    echo "使用 ~/.openclaw/openclaw.json 中的凭证"
  fi

# 3. 检查独立配置文件
elif [ -f ~/.config/lexiang/credentials ]; then
  LEXIANG_CREDS=$(cat ~/.config/lexiang/credentials)
  export LEXIANG_APP_KEY=$(echo $LEXIANG_CREDS | jq -r '.app_key')
  export LEXIANG_APP_SECRET=$(echo $LEXIANG_CREDS | jq -r '.app_secret')
  STAFF_ID=$(echo $LEXIANG_CREDS | jq -r '.staff_id // empty')
  if [ -n "$STAFF_ID" ]; then
    export LEXIANG_STAFF_ID="$STAFF_ID"
  fi
  echo "使用 ~/.config/lexiang/credentials 中的凭证"
fi

# 检查凭证是否已加载
if [ -z "$LEXIANG_APP_KEY" ] || [ -z "$LEXIANG_APP_SECRET" ]; then
  echo "错误：未找到乐享凭证，请配置以下任一方式："
  echo "  1. 设置环境变量 LEXIANG_APP_KEY 和 LEXIANG_APP_SECRET"
  echo "  2. 在 ~/.openclaw/openclaw.json 中配置 skills.entries.lexiang.env"
  echo "  3. 创建 ~/.config/lexiang/credentials 文件"
  return 1 2>/dev/null || exit 1
fi

if [ -z "$LEXIANG_STAFF_ID" ]; then
  echo "警告：未配置 LEXIANG_STAFF_ID，写操作可能会失败"
else
  echo "员工身份标识：$LEXIANG_STAFF_ID"
fi

# 检查是否有缓存的有效 token
if [ -f ~/.config/lexiang/token ]; then
  TOKEN_AGE=$(($(date +%s) - $(stat -f %m ~/.config/lexiang/token 2>/dev/null || stat -c %Y ~/.config/lexiang/token)))
  if [ $TOKEN_AGE -lt 7000 ]; then
    export LEXIANG_TOKEN=$(cat ~/.config/lexiang/token)
    echo "使用缓存的 Token (剩余有效期: $((7200 - TOKEN_AGE))秒)"
    return 0 2>/dev/null || exit 0
  fi
fi

# 获取新 token
export LEXIANG_TOKEN=$(curl -s -X POST "https://lxapi.lexiangla.com/cgi-bin/token" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"grant_type\":\"client_credentials\",\"app_key\":\"$LEXIANG_APP_KEY\",\"app_secret\":\"$LEXIANG_APP_SECRET\"}" \
  | jq -r '.access_token')

mkdir -p ~/.config/lexiang
echo $LEXIANG_TOKEN > ~/.config/lexiang/token
echo "已获取新 Token 并缓存"
