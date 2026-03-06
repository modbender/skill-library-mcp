# searchWorks

搜索已发布的需求/服务

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-match/api/v1/inner/match`
- endpoint: `/works_search`
- method: POST
- contentType: application/json

## 鉴权 Headers

签名算法: `HMAC-SHA256(secret, Method&Path&AgentKey&Timestamp)`

| 参数名 | 来源 | 描述 |
|--------|------|------|
| X-Agent-Id | `config.sh` 的 `AGENT_ID` | 代理ID |
| X-Timestamp | 当前时间戳 (秒) | 请求时间戳 |
| X-Agent-Signature | HMAC-SHA256签名 | 签名 |

## 请求参数 (WorksSearchDTO)

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| serviceInfo | string | 否 | - | 搜索关键词 |
| city | string | 否 | - | 城市 |
| district | string | 否 | - | 区县 |
| province | string | 否 | - | 省份 |
| longitude | string | 否 | - | 经度 |
| latitude | string | 否 | - | 纬度 |
| radiusInMeter | string | 否 | - | 搜索半径（米） |
| priceMin | string | 否 | - | 最低价格 |
| priceMax | string | 否 | - | 最高价格 |
| pageNum | integer | 否 | 0 | 页码（从0开始） |
| pageSize | integer | 否 | 6 | 每页条数 |
| type | integer | 否 | - | 类型：2=需求，3=服务 |

## curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "POST&/findu-match/api/v1/inner/match/works_search&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X POST "${BASE_URL}/findu-match/api/v1/inner/match/works_search" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -d '{
    "serviceInfo": "网球教练",
    "city": "杭州",
    "district": "西湖",
    "pageNum": 0,
    "pageSize": 10,
    "type": 3
  }'
```

## 响应示例

成功:
```json
{
  "code": "200",
  "message": "success",
  "data": {
    "query": "default:'网球教练'&&filter=is_deleted=0 AND status=1",
    "result": [
      {
        "worksId": "work_12345",
        "userId": "user_67890",
        "title": "专业网球教练服务",
        "content": "提供专业的网球教学服务",
        "extendInfo": "{\"expectedPrice\":\"500-800元/小时\",\"serviceMethod\":\"线下\"}",
        "type": 3,
        "status": 1
      }
    ]
  }
}
```

## 搜索条件

- `is_deleted = 0` (未删除)
- `status = 1` (正常状态)
- `type = 3` (帖子类型，传入 type 参数可指定)
