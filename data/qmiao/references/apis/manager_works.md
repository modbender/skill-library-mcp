# managerWorks

管理帖子：查询当前用户帖子列表/详情

## 密钥配置

请在 `references/secrets/config.sh` 中配置：
- `BASE_URL`
- `AGENT_ID`
- `AGENT_SECRET`

## 基本信息

- baseUrl: `{BASE_URL}/findu-user/api/v1/user/works`
- contentType: application/json

## 鉴权 Headers

签名算法: `HMAC-SHA256(secret, Method&Path&AgentKey&Timestamp)`

| 参数名 | 来源 | 描述 |
|--------|------|------|
| X-Agent-Id | `config.sh` 的 `AGENT_ID` | 代理ID |
| X-Timestamp | 当前时间戳 (秒) | 请求时间戳 |
| X-Agent-Signature | HMAC-SHA256签名 | 签名 |

### 状态说明

| 状态 | 描述 |
|------|------|
| 公共态 | 已发布（status=1）且未删除的帖子，人人可见 |
| 编辑态 | 未删除（is_deleted=0）的所有帖子，包括草稿、审核中、已发布、已下架等状态 |

---

## 公共态帖子

查询当前用户的公共态帖子列表（status=1 且未删除），返回可公开访问的帖子。

### 接口信息

- endpoint: `/public`
- method: GET

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| type | integer | 否 | - | 按帖子内容类型过滤 |
| page | integer | 否 | 1 | 页码 |
| pageSize | integer | 否 | 10 | 每页数量 |

### curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
PATH="/findu-user/api/v1/user/works/public?type=3&page=1&pageSize=10"
SIGNATURE=$(echo -n "GET&${PATH}&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-user/api/v1/user/works/public?type=3&page=1&pageSize=10" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -H "x-user-id: 12345"
```

### 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "worksId": "work_12345",
        "type": 3,
        "title": "专业网球教练服务",
        "content": "提供专业的网球教学服务",
        "status": 1,
        "pictures": [],
        "extendInfo": {
          "expectedPrice": "500-800元/小时",
          "serviceMethod": "offline",
          "serviceLocation": "杭州市西湖区"
        },
        "createdAt": "2025-01-15T10:30:00Z",
        "updatedAt": "2025-01-15T10:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 10
  }
}
```

---

## 公共态帖子详情

查询当前用户的单个公共态帖子详情，返回已发布帖子的完整信息。

### 接口信息

- endpoint: `/{worksId}/public`
- method: GET

### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| worksId | string | 是 | 帖子ID（路径参数） |

### curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
PATH="/findu-user/api/v1/user/works/work_12345/public"
SIGNATURE=$(echo -n "GET&${PATH}&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-user/api/v1/user/works/work_12345/public" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -H "x-user-id: 12345"
```

### 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "worksId": "work_12345",
    "type": 3,
    "title": "专业网球教练服务",
    "content": "提供专业的网球教学服务，包括入门、进阶、私教等课程",
    "status": 1,
    "pictures": ["https://example.com/img1.jpg"],
    "videos": [],
    "extendInfo": {
      "expectedPrice": "500-800元/小时",
      "serviceMethod": "offline",
      "serviceLocation": "杭州市西湖区"
    },
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

---

## 编辑态帖子列表

查询当前用户的编辑态帖子列表（未删除），包括编辑中、审核中、已发布、已下架等所有状态的帖子。

### 接口信息

- endpoint: `/editable`
- method: GET

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| type | integer | 否 | - | 按帖子内容类型过滤 |
| page | integer | 否 | 1 | 页码 |
| pageSize | integer | 否 | 10 | 每页数量 |

### curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
PATH="/findu-user/api/v1/user/works/editable?type=3&page=1&pageSize=10"
SIGNATURE=$(echo -n "GET&${PATH}&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-user/api/v1/user/works/editable?type=3&page=1&pageSize=10" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -H "x-user-id: 12345"
```

### 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "worksId": "work_12345",
        "type": 3,
        "title": "专业网球教练服务",
        "status": 1,
        "changeStatus": "approved",
        "isDeleted": 0,
        "createdAt": "2025-01-15T10:30:00Z",
        "updatedAt": "2025-01-15T10:30:00Z"
      },
      {
        "worksId": "work_67890",
        "type": 2,
        "title": "寻找网球教练",
        "status": 0,
        "changeStatus": "pending",
        "isDeleted": 0,
        "createdAt": "2025-01-10T08:00:00Z",
        "updatedAt": "2025-01-14T16:00:00Z"
      }
    ],
    "total": 2,
    "page": 1,
    "pageSize": 10
  }
}
```

### changeStatus 说明

| 值 | 描述 |
|----|------|
| none | 无待审核变更 |
| pending | 审核中 |
| approved | 已通过 |
| rejected | 已拒绝 |

---

## 编辑态帖子详情

查询当前用户的单个编辑态帖子详情，返回帖子完整信息及待审核的变更申请。

### 接口信息

- endpoint: `/{worksId}/editable`
- method: GET

### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| worksId | string | 是 | 帖子ID（路径参数） |

### curl 示例

```bash
source references/secrets/config.sh

TIMESTAMP=$(date +%s)
PATH="/findu-user/api/v1/user/works/work_12345/editable"
SIGNATURE=$(echo -n "GET&${PATH}&${AGENT_ID}&${TIMESTAMP}" | openssl dgst -sha256 -hmac "${AGENT_SECRET}" | awk '{print $2}')

curl -X GET "${BASE_URL}/findu-user/api/v1/user/works/work_12345/editable" \
  -H "X-Agent-Id: ${AGENT_ID}" \
  -H "X-Timestamp: ${TIMESTAMP}" \
  -H "X-Agent-Signature: ${SIGNATURE}" \
  -H "x-user-id: 12345"
```

### 响应示例

成功:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "worksId": "work_12345",
    "type": 3,
    "title": "专业网球教练服务",
    "content": "提供专业的网球教学服务",
    "status": 1,
    "isDeleted": 0,
    "changeStatus": "none",
    "pictures": [],
    "videos": [],
    "extendInfo": {
      "expectedPrice": "500-800元/小时",
      "serviceMethod": "offline",
      "serviceLocation": "杭州市西湖区"
    },
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z",
    "pendingChange": null
  }
}
```

### pendingChange 说明

当 `changeStatus` 为 `pending` 时，`pendingChange` 字段包含待审核的变更申请信息。
