# publishWorks

发布帖子，需求（悬赏求助帖）或服务（技能服务帖）

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-user/api/v1/user/works`
- endpoint: `/change-requests`
- method: POST
- contentType: application/json

## 鉴权 Headers

签名算法: `HMAC-SHA256(secret, Method&Path&AgentKey&Timestamp)`

| 参数名 | 来源 | 描述 |
|--------|------|------|
| X-Agent-Id | `config.sh` 的 `AGENT_ID` | 代理ID |
| X-Timestamp | 当前时间戳 (秒) | 请求时间戳 |
| X-Agent-Signature | HMAC-SHA256签名 | 签名 |

## 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| type | integer | 是 | 类型：2=悬赏求助，3=技能服务 |
| title | string | 是 | 标题 |
| content | string | 是 | 内容描述（最多1000字） |
| pictures | array | 否 | 图片列表 |
| videos | array | 否 | 视频列表 |
| extendInfo | object | 否 | 扩展信息 |

### extendInfo 字段

| 参数名 | 类型 | 描述 |
|--------|------|------|
| expectedPrice | string | 期望价格，如 "5000-10000元" |
| serviceMethod | string | 服务方式：offline=线下，online=线上 |
| serviceLocation | string | 服务地点，如 "北京市朝阳区望京街道" |

## curl 示例

### 发布服务 (type=3)

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "POST&/findu-user/api/v1/user/works/change-requests&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X POST "${BASE_URL}/findu-user/api/v1/user/works/change-requests" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -d '{
    "type": 3,
    "title": "专业网球教练服务",
    "content": "提供专业的网球教学服务，包括入门、进阶、私教等课程",
    "pictures": [],
    "videos": [],
    "extendInfo": {
      "expectedPrice": "500-800元/小时",
      "serviceMethod": "offline",
      "serviceLocation": "杭州市西湖区"
    }
  }'
```

### 发布需求 (type=2)

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
SIGNATURE=$(echo -n "POST&/findu-user/api/v1/user/works/change-requests&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X POST "${BASE_URL}/findu-user/api/v1/user/works/change-requests" \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -d '{
    "type": 2,
    "title": "寻找网球教练",
    "content": "想找个网球教练学习网球，零基础",
    "pictures": [],
    "videos": [],
    "extendInfo": {
      "expectedPrice": "面议",
      "serviceMethod": "offline",
      "serviceLocation": "杭州市西湖区"
    }
  }'
```

## 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "changeId": 1001,
    "worksId": "work_12345",
    "status": "pending"
  }
}
```
