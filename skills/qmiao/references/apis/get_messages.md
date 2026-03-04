# getMessages

获取指定会话的聊天历史

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-imutils/api/v1/im`
- endpoint: `/chat/messages`
- method: GET
- contentType: application/json

## 鉴权 Headers

签名算法: `HMAC-SHA256(secret, Method&Path&AgentKey&Timestamp)`

| 参数名 | 来源 | 描述 |
|--------|------|------|
| X-Agent-Id | `config.sh` 的 `AGENT_ID` | 代理ID |
| X-Timestamp | 当前时间戳 (秒) | 请求时间戳 |
| X-Agent-Signature | HMAC-SHA256签名 | 签名 |

## 请求参数 (Query)

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| peer_id | string | 是 | 对话用户ID |
| count | number | 否 | 获取消息数量，默认20 |

## curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "GET&/findu-imutils/api/v1/im/chat/messages&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-imutils/api/v1/im/chat/messages?peer_id=用户ID&count=20" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}"
```

## 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "messageId": "msg_001",
      "peerId": "用户ID",
      "text": "你好",
      "timestamp": 1700000000,
      "direction": "outgoing"
    }
  ]
}
```
