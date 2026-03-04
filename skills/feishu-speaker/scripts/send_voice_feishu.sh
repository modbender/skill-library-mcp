#!/bin/bash
# 发送飞书语音消息
# 用法: send_voice_feishu.sh <音频文件.ogg> [时长毫秒] [接收者ID]

APP_ID="cli_a9037acd2ba19bb5"
APP_SECRET_FILE="${HOME}/.openclaw/.credentials/feishu-app-secret.txt"
RECEIVER_ID="${3:-ou_94f3936f1896b5378404f377da3fae6f}"

# 读取App Secret
if [[ ! -f "$APP_SECRET_FILE" ]]; then
    echo "错误: 找不到App Secret文件: $APP_SECRET_FILE"
    exit 1
fi

APP_SECRET=$(cat "$APP_SECRET_FILE" | tr -d '\n')

if [[ -z "$APP_SECRET" ]]; then
    echo "错误: App Secret为空"
    exit 1
fi

FILE_PATH="${1:-/tmp/test_voice.ogg}"
DURATION="${2:-4650}"

# 获取access token
get_token() {
    local response=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}")
    
    echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tenant_access_token',''))"
}

# 上传语音文件
upload_voice() {
    local token="$1"
    local file_path="$2"
    local duration="$3"
    
    local response=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
        -H "Authorization: Bearer $token" \
        -F "file_type=opus" \
        -F "file_name=voice.ogg" \
        -F "duration=$duration" \
        -F "file=@$file_path")
    
    echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('file_key',''))"
}

# 发送语音消息
send_voice() {
    local token="$1"
    local file_key="$2"
    
    # 使用Python构造正确的JSON
    local json_payload=$(python3 -c "import json; print(json.dumps({\"receive_id\": \"$RECEIVER_ID\", \"msg_type\": \"audio\", \"content\": json.dumps({\"file_key\": \"$file_key\"})}))")
    
    local response=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "$json_payload")
    
    local code=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('code',-1))")
    
    if [[ "$code" == "0" ]]; then
        echo "成功"
    else
        local msg=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('msg','Unknown error'))")
        echo "失败: $msg"
        exit 1
    fi
}

# 主流程
echo "正在发送语音消息..."
TOKEN=$(get_token)
if [[ -z "$TOKEN" ]]; then
    echo "错误: 获取access token失败"
    exit 1
fi

FILE_KEY=$(upload_voice "$TOKEN" "$FILE_PATH" "$DURATION")
if [[ -z "$FILE_KEY" ]]; then
    echo "错误: 上传语音文件失败"
    exit 1
fi

echo "File key: $FILE_KEY"
RESULT=$(send_voice "$TOKEN" "$FILE_KEY")
echo "发送结果: $RESULT"
