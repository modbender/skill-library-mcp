# getFeeds

获取公共 Feed 流列表

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-feed/api/v1/public`
- endpoint: `/feeds`
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

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | number | 否 | 1 | 页码 |
| page_size | number | 否 | 20 | 每页数量 |
| type | number | 否 | - | 类型筛选：2=需求，3=服务，不传则显示全部 |

## curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "GET&/findu-feed/api/v1/public/feeds&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

# 获取全部 Feed
curl -X GET "${BASE_URL}/findu-feed/api/v1/public/feeds?page=1&page_size=20" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}"

# 仅获取服务类 Feed (type=3)
curl -X GET "${BASE_URL}/findu-feed/api/v1/public/feeds?page=1&page_size=20&type=3" \
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
      "id": 1,
      "type": 3,
      "title": "专业网球教练服务",
      "content": "提供专业的网球教学服务",
      "authorId": "user_001",
      "authorName": "张教练",
      "pictures": ["https://example.com/pic1.jpg"],
      "extendInfo": {
        "expectedPrice": "500-800元/小时",
        "serviceMethod": "offline"
      },
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ]
}
```

## type 说明

| type 值 | 描述 |
|---------|------|
| 2 | 需求 |
| 3 | 服务 |
