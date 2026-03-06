# sendMessage

发送单聊消息给指定用户

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-imutils/api/v1/im`
- endpoint: `/chat/send`
- method: POST
- contentType: application/json

## 鉴权 Headers

签名算法: `HMAC-SHA256(secret, Method&Path&AgentKey&Timestamp)`

| 参数名 | 来源 | 描述 |
|--------|------|------|
| X-Agent-Id | `config.sh` 的 `AGENT_ID` | 代理ID |
| X-Timestamp | 当前时间戳 (秒) | 请求时间戳 |
| X-Agent-Signature | HMAC-SHA256签名 | 签名 |

签名计算方式:
```bash
TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "${method}&${path}&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')
```

## 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| to_user_id | string | 是 | 目标用户ID |
| text | string | 是 | 消息文本内容 |

## 通过昵称发送的说明

接口仅支持通过 ID 指定收件人。若用户希望通过**昵称**选择发消息对象，需先查 `references/resources/namelist.md`：

1. **有唯一匹配**：使用该昵称对应的 `conversation_id` 作为 `to_user_id` 发送
2. **有多个相似昵称**：列出候选，让用户选择后再发送
3. **查不到该昵称**：告知用户「找不到该昵称对应的用户」，可建议先拉取会话列表更新 namelist，或让用户提供 ID

## curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "POST&/findu-imutils/api/v1/im/chat/send&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X POST "${BASE_URL}/findu-imutils/api/v1/im/chat/send" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -d '{"to_user_id":"目标用户ID","text":"你好"}'
```

## 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "messageId": "msg_xxx",
    "timestamp": 1700000000
  }
}
```
