# Disputes API

Base URL: `/api/v1/disputes`

The disputes system handles conflict resolution between personal users and businesses. Disputes are created via the orders API (`POST /api/v1/orders/{order_id}/dispute`) and managed through these endpoints for messaging, evidence submission, and escalation.

All endpoints require authentication.

---

## GET /api/v1/disputes/{dispute_id}

Retrieve full dispute details including messages and evidence snapshots.

**Auth:** Required (party or admin)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

None.

### Request Example

```
GET /api/v1/disputes/77889900-aabb-ccdd-eeff-112233445566
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "77889900-aabb-ccdd-eeff-112233445566",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "initiator_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "reason": "商家交付的模型微调质量严重不达标，评测指标低于合同约定的基线阈值。",
  "evidence": [
    "https://cdn.tmrland.com/evidence/eval-report-55667788.pdf",
    "https://cdn.tmrland.com/evidence/chat-log-55667788.html"
  ],
  "contract_snapshot": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%"
  },
  "status": "open",
  "resolution": null,
  "resolution_notes": null,
  "resolved_at": null,
  "messages": [
    {
      "id": "dd001122-3344-5566-7788-99aabbccdd01",
      "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
      "sender_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "content": "模型在金融问答测试集上的准确率仅为45%，合同约定的基线为70%。请查看附件中的评测报告。",
      "created_at": "2026-03-12T09:15:00Z"
    },
    {
      "id": "dd001122-3344-5566-7788-99aabbccdd02",
      "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
      "sender_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "content": "评测集版本有误，我们使用的是V2测试集。V1测试集包含了大量非金融问题。请使用附件中的V2测试集重新评测。",
      "created_at": "2026-03-12T10:30:00Z"
    }
  ],
  "evidence_snapshots": [
    {
      "id": "ee001122-3344-5566-7788-99aabbccdd01",
      "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
      "evidence_type": "delta",
      "content": "Delta评分: 0.45，低于合同约定的0.70基线",
      "linked_resource_id": "99001122-3344-5566-7788-99aabbccddee",
      "created_at": "2026-03-12T09:10:00Z"
    },
    {
      "id": "ee001122-3344-5566-7788-99aabbccdd02",
      "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
      "evidence_type": "contract_term",
      "content": "合同第4.2条：商家交付的模型在指定测试集上的准确率不低于70%",
      "linked_resource_id": "66778899-aabb-ccdd-eeff-001122334455",
      "created_at": "2026-03-12T09:12:00Z"
    }
  ],
  "created_at": "2026-03-12T09:00:00Z",
  "updated_at": "2026-03-12T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to view this dispute"` | User is not a party or admin |
| 404 | `"Dispute not found"` | Dispute ID does not exist |

---

## GET /api/v1/disputes/{dispute_id}/messages

List all messages in a dispute thread.

**Auth:** Required (party or admin)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

None.

### Request Example

```
GET /api/v1/disputes/77889900-aabb-ccdd-eeff-112233445566/messages
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
[
  {
    "id": "dd001122-3344-5566-7788-99aabbccdd01",
    "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
    "sender_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "content": "模型在金融问答测试集上的准确率仅为45%，合同约定的基线为70%。请查看附件中的评测报告。",
    "created_at": "2026-03-12T09:15:00Z"
  },
  {
    "id": "dd001122-3344-5566-7788-99aabbccdd02",
    "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
    "sender_id": "11223344-5566-7788-99aa-bbccddeeff00",
    "content": "评测集版本有误，我们使用的是V2测试集。V1测试集包含了大量非金融问题。请使用附件中的V2测试集重新评测。",
    "created_at": "2026-03-12T10:30:00Z"
  }
]
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to view dispute messages"` | User is not a party or admin |
| 404 | `"Dispute not found"` | Dispute ID does not exist |

---

## POST /api/v1/disputes/{dispute_id}/messages

Send a message in the dispute thread.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | Message content, minimum 1 character |

### Request Example

```json
{
  "content": "我已使用V2测试集重新评测，准确率为52%，仍然低于合同约定的70%。完整评测结果见附件。"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "dd001122-3344-5566-7788-99aabbccdd03",
  "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
  "sender_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "content": "我已使用V2测试集重新评测，准确率为52%，仍然低于合同约定的70%。完整评测结果见附件。",
  "created_at": "2026-03-12T14:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to send messages in this dispute"` | User is not a party |
| 404 | `"Dispute not found"` | Dispute ID does not exist |
| 409 | `"Cannot send messages to a resolved dispute"` | Dispute has been resolved |
| 422 | Pydantic validation array | Empty content |

---

## POST /api/v1/disputes/{dispute_id}/evidence

Submit a piece of evidence to support a dispute claim.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `evidence_type` | str | Yes | Type of evidence. One of: `"receipt"`, `"delta"`, `"chat_export"`, `"contract_term"`, `"user_claim"`, `"business_claim"` |
| `content` | str | Yes | Evidence description or content, minimum 1 character |
| `linked_resource_id` | UUID \| None | No | Optional ID of a linked resource (order, delta, contract, etc.) |

### Request Example

```json
{
  "evidence_type": "user_claim",
  "content": "使用V2测试集重新评测后，准确率为52%，仍远低于合同约定的70%基线。评测脚本和结果日志已上传至 https://cdn.tmrland.com/evidence/v2-eval-55667788.zip",
  "linked_resource_id": "55667788-99aa-bbcc-ddee-ff0011223344"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "ee001122-3344-5566-7788-99aabbccdd03",
  "dispute_id": "77889900-aabb-ccdd-eeff-112233445566",
  "evidence_type": "user_claim",
  "content": "使用V2测试集重新评测后，准确率为52%，仍远低于合同约定的70%基线。评测脚本和结果日志已上传至 https://cdn.tmrland.com/evidence/v2-eval-55667788.zip",
  "linked_resource_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "created_at": "2026-03-12T14:05:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to submit evidence for this dispute"` | User is not a party |
| 404 | `"Dispute not found"` | Dispute ID does not exist |
| 409 | `"Cannot submit evidence to a resolved dispute"` | Dispute has been resolved |
| 422 | Pydantic validation array | Invalid evidence_type or empty content |

---

## POST /api/v1/disputes/{dispute_id}/escalate

Escalate a dispute to platform admin review. This changes the dispute status to `escalated`.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID (must be in `open` status) |

### Request Body

None.

### Request Example

```
POST /api/v1/disputes/77889900-aabb-ccdd-eeff-112233445566/escalate
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "77889900-aabb-ccdd-eeff-112233445566",
  "order_id": "55667788-99aa-bbcc-ddee-ff0011223344",
  "initiator_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "reason": "商家交付的模型微调质量严重不达标，评测指标低于合同约定的基线阈值。",
  "evidence": [
    "https://cdn.tmrland.com/evidence/eval-report-55667788.pdf",
    "https://cdn.tmrland.com/evidence/chat-log-55667788.html"
  ],
  "status": "escalated",
  "resolution": null,
  "resolution_notes": null,
  "resolved_at": null,
  "created_at": "2026-03-12T09:00:00Z",
  "updated_at": "2026-03-12T15:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to escalate this dispute"` | User is not a party |
| 404 | `"Dispute not found"` | Dispute ID does not exist |
| 409 | `"Dispute is not in open status"` | Dispute already escalated or resolved |
