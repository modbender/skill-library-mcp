# Messages API

Base URL: `/api/v1/messages`

Order-scoped messaging between personal users and businesses. Messages are tied to orders and support text content with optional file attachments.

All endpoints require authentication.

---

## GET /api/v1/messages/conversations

List all conversations (orders with messages) for the current user.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/messages/conversations?offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "other_party_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "other_party_name": "智能数据科技",
      "last_message_content": "模型已部署完成，API文档请查看附件。",
      "last_message_at": "2026-03-10T08:45:00Z",
      "unread_count": 2,
      "total_messages": 18
    },
    {
      "order_id": "66778899-aabb-ccdd-eeff-223344556677",
      "other_party_id": "22334455-6677-8899-aabb-ccddeeff0011",
      "other_party_name": "深度语言实验室",
      "last_message_content": "好的，我们会在本周五之前提供修订版本。",
      "last_message_at": "2026-03-08T16:20:00Z",
      "unread_count": 0,
      "total_messages": 7
    }
  ],
  "total": 2
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## GET /api/v1/messages/orders/{order_id}

Retrieve the message history for an order.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `50`, max `200` |

### Request Example

```
GET /api/v1/messages/orders/55667788-99aa-bbcc-ddee-ff0011223344?offset=0&limit=50
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "ff001122-3344-5566-7788-99aabb000001",
      "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "sender_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "recipient_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "message_type": "text",
      "content": "你好，我们已经下单了金融大模型微调服务。请问预计多久可以开始训练？",
      "attachments": null,
      "is_read": true,
      "read_at": "2026-02-27T15:10:00Z",
      "created_at": "2026-02-27T15:05:00Z",
      "updated_at": "2026-02-27T15:10:00Z"
    },
    {
      "id": "ff001122-3344-5566-7788-99aabb000002",
      "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "sender_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "recipient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "message_type": "text",
      "content": "感谢下单！我们会在确认数据范围后48小时内启动训练。请问您能提供具体的财报年份范围和需要覆盖的股票范围吗？",
      "attachments": null,
      "is_read": true,
      "read_at": "2026-02-27T15:20:00Z",
      "created_at": "2026-02-27T15:15:00Z",
      "updated_at": "2026-02-27T15:20:00Z"
    },
    {
      "id": "ff001122-3344-5566-7788-99aabb000003",
      "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
      "sender_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "recipient_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "message_type": "text",
      "content": "2021-2025年全部A股上市公司，重点关注沪深300成分股。详细需求文档见附件。",
      "attachments": [
        "https://cdn.tmrland.com/messages/55667788/requirements-v1.pdf"
      ],
      "is_read": true,
      "read_at": "2026-02-27T15:35:00Z",
      "created_at": "2026-02-27T15:30:00Z",
      "updated_at": "2026-02-27T15:35:00Z"
    }
  ],
  "total": 3
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to view messages for this order"` | User is not personal or business |
| 404 | `"Order not found"` | Order ID does not exist |

---

## POST /api/v1/messages/orders/{order_id}

Send a message in an order conversation.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | Message text, minimum 1 character |
| `attachments` | list[str] \| None | No | URLs to attached files |

### Request Example

```json
{
  "content": "收到需求文档，确认范围无误。训练预计3月3日启动，中间会分阶段给您进展更新。",
  "attachments": null
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "ff001122-3344-5566-7788-99aabb000004",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "sender_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "recipient_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message_type": "text",
  "content": "收到需求文档，确认范围无误。训练预计3月3日启动，中间会分阶段给您进展更新。",
  "attachments": null,
  "is_read": false,
  "read_at": null,
  "created_at": "2026-02-28T09:00:00Z",
  "updated_at": "2026-02-28T09:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to send messages for this order"` | User is not personal or business |
| 404 | `"Order not found"` | Order ID does not exist |
| 422 | Pydantic validation array | Empty content |

---

## POST /api/v1/messages/orders/{order_id}/read

Mark all unread messages in the order conversation as read for the current user.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `order_id` | UUID | Yes | Order ID |

### Request Body

None.

### Request Example

```
POST /api/v1/messages/orders/55667788-99aa-bbcc-ddee-ff0011223344/read
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "marked_read": 2
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access messages for this order"` | User is not personal or business |
| 404 | `"Order not found"` | Order ID does not exist |
