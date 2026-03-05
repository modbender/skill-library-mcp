# getConversations

获取当前用户的会话列表

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-imutils/api/v1/im`
- endpoint: `/conversations`
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
| count | number | 否 | 获取会话数量，默认20 |

## curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "GET&/findu-imutils/api/v1/im/conversations&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-imutils/api/v1/im/conversations?count=20" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}"
```

## 响应示例

成功:
```json
{
  "user_id": "当前用户ID",
  "conversations": [
    {
      "conversation_id": "会话ID",
      "nickname": "对方昵称",
      "unread_count": 0
    },
    {
      "conversation_id": "另一会话ID",
      "nickname": null,
      "unread_count": 1
    }
  ]
}
```

说明：
- `user_id`：当前登录用户的 ID
- `conversations`：会话列表
- `conversation_id`：会话唯一标识，用于发送消息时指定目标
- `nickname`：对方用户昵称，可能为 null
- `unread_count`：该会话未读消息数

## 拉取后的本地操作

每次拉取会话列表后，**必须**更新 `references/resources/namelist.md`，记录昵称与 `conversation_id` 的对应关系，便于后续用户通过昵称指定收件人发消息。格式示例：

```markdown
| 昵称 | conversation_id |
|------|-----------------|
| 张三 | conv_xxx |
| 李四 | conv_yyy |
```

若 `nickname` 为 null，可用 `conversation_id` 作为显示名。
