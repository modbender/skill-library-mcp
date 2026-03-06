# Notifications API

Base URL: `/api/v1/notifications`

Platform notifications for order updates, match results, dispute activity, and system announcements.

All endpoints require authentication.

---

## GET /api/v1/notifications/

List notifications for the current user with optional filtering.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `unread_only` | bool | No | If `true`, only return unread notifications. Default `false` |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/notifications/?unread_only=true&offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "11002233-4455-6677-8899-aabbccddeeff",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "order_delivered",
      "title": "订单交付通知",
      "body": "商家「智能数据科技」已完成订单交付，请查看交付物并确认收货。",
      "resource_type": "order",
      "resource_id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-03-10T09:00:00Z"
    },
    {
      "id": "22003344-5566-7788-99aa-bbccddeeff00",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "match_completed",
      "title": "匹配完成",
      "body": "您的需求「需要金融行业大模型微调服务」已完成商家匹配，共找到3个候选商家。",
      "resource_type": "intention",
      "resource_id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-02-27T14:00:00Z"
    },
    {
      "id": "33004455-6677-8899-aabb-ccddeeff0011",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "type": "dispute_message",
      "title": "争议回复",
      "body": "商家在争议 #77889900 中提交了新回复。",
      "resource_type": "dispute",
      "resource_id": "77889900-aabb-ccdd-eeff-112233445566",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-03-12T10:30:00Z"
    }
  ],
  "total": 3
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## GET /api/v1/notifications/unread-count

Get the count of unread notifications for the current user.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/notifications/unread-count
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "count": 3
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## POST /api/v1/notifications/{notification_id}/read

Mark a single notification as read.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `notification_id` | UUID | Yes | Notification ID |

### Request Body

None.

### Request Example

```
POST /api/v1/notifications/11002233-4455-6677-8899-aabbccddeeff/read
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "11002233-4455-6677-8899-aabbccddeeff",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "type": "order_delivered",
  "title": "订单交付通知",
  "body": "商家「智能数据科技」已完成订单交付，请查看交付物并确认收货。",
  "resource_type": "order",
  "resource_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "is_read": true,
  "read_at": "2026-03-10T09:30:00Z",
  "created_at": "2026-03-10T09:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Notification not found"` | Notification ID does not exist or belongs to another user |

---

## POST /api/v1/notifications/read-all

Mark all unread notifications as read for the current user.

**Auth:** Required

### Request Body

None.

### Request Example

```
POST /api/v1/notifications/read-all
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "marked_read": 3
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
