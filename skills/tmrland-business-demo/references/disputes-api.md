# Disputes API

Base URL: `/api/v1/disputes`

Dispute resolution endpoints for managing order disputes after they have been created (via `POST /api/v1/orders/{order_id}/dispute`). Both personal and business parties can exchange messages, submit evidence, and escalate disputes for admin review.

---

## GET /api/v1/disputes/{dispute_id}

Retrieve detailed information about a dispute.

**Auth:** Required (personal, business party, or admin)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Example

```
GET /api/v1/disputes/99887766-5544-3322-1100-ffeeddccbbaa
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "initiated_by": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "reason": "The personal user has not responded to the delivery for over 7 days, requesting auto-confirmation of the order.",
  "evidence": [
    "https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png",
    "https://cdn.tmrland.com/evidence/message-history-export.pdf"
  ],
  "status": "open",
  "resolution": null,
  "resolution_notes": null,
  "resolved_by": null,
  "resolved_at": null,
  "escalated_at": null,
  "created_at": "2026-03-05T14:00:00Z",
  "updated_at": "2026-03-05T14:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this dispute or an admin |
| 404 | `dispute_not_found` | No dispute with this ID |

---

## GET /api/v1/disputes/{dispute_id}/messages

Retrieve all messages in a dispute thread.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Example

```
GET /api/v1/disputes/99887766-5544-3322-1100-ffeeddccbbaa/messages
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
[
  {
    "id": "aa001122-3344-5566-7788-99aabbccddee",
    "dispute_id": "99887766-5544-3322-1100-ffeeddccbbaa",
    "sender_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "content": "I delivered the report on Feb 28 and have not received any feedback or confirmation from the personal user in 7 days. The order should be auto-confirmed per the platform terms.",
    "created_at": "2026-03-05T14:05:00Z"
  },
  {
    "id": "bb112233-4455-6677-8899-aabbccddeeff",
    "dispute_id": "99887766-5544-3322-1100-ffeeddccbbaa",
    "sender_id": "aabbccdd-eeff-0011-2233-445566778899",
    "content": "I was traveling and unable to review the delivery. I have now reviewed it and found several data discrepancies that need to be addressed before I can confirm.",
    "created_at": "2026-03-06T09:20:00Z"
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this dispute |
| 404 | `dispute_not_found` | No dispute with this ID |

---

## POST /api/v1/disputes/{dispute_id}/messages

Send a message in a dispute thread.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | str | Yes | Message content |

### Request Example

```json
{
  "content": "I have uploaded a revised version of the report addressing all data discrepancies. The updated deliverable URL has been attached to the order. Please review at your convenience."
}
```

### Response Example

```json
{
  "id": "cc223344-5566-7788-99aa-bbccddeeff00",
  "dispute_id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "sender_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "content": "I have uploaded a revised version of the report addressing all data discrepancies. The updated deliverable URL has been attached to the order. Please review at your convenience.",
  "created_at": "2026-03-06T14:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this dispute |
| 404 | `dispute_not_found` | No dispute with this ID |
| 409 | `dispute_closed` | Cannot send messages on a resolved dispute |

---

## POST /api/v1/disputes/{dispute_id}/evidence

Submit additional evidence for a dispute.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `evidence_type` | str | Yes | Type of evidence (e.g., `"screenshot"`, `"document"`, `"url"`, `"message_log"`) |
| `content` | str | Yes | Evidence content or URL |
| `linked_resource_id` | UUID \| null | No | Optional link to a related resource (order, message, etc.) |

### Request Example

```json
{
  "evidence_type": "document",
  "content": "https://cdn.tmrland.com/evidence/revised-report-diff.pdf",
  "linked_resource_id": "11223344-5566-7788-99aa-bbccddeeff00"
}
```

### Response Example

```json
{
  "id": "dd334455-6677-8899-aabb-ccddeeff0011",
  "dispute_id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "submitted_by": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "evidence_type": "document",
  "content": "https://cdn.tmrland.com/evidence/revised-report-diff.pdf",
  "linked_resource_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "created_at": "2026-03-06T14:35:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this dispute |
| 404 | `dispute_not_found` | No dispute with this ID |
| 409 | `dispute_closed` | Cannot submit evidence on a resolved dispute |

---

## POST /api/v1/disputes/{dispute_id}/escalate

Escalate a dispute for admin review. Use when parties cannot reach resolution.

**Auth:** Required (personal or business party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `dispute_id` | UUID | Yes | Dispute ID |

### Request Body

None.

### Request Example

```
POST /api/v1/disputes/99887766-5544-3322-1100-ffeeddccbbaa/escalate
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "99887766-5544-3322-1100-ffeeddccbbaa",
  "order_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "initiated_by": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "personal_id": "aabbccdd-eeff-0011-2233-445566778899",
  "business_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "reason": "The personal user has not responded to the delivery for over 7 days, requesting auto-confirmation of the order.",
  "evidence": [
    "https://cdn.tmrland.com/evidence/delivery-confirmation-screenshot.png",
    "https://cdn.tmrland.com/evidence/message-history-export.pdf"
  ],
  "status": "escalated",
  "resolution": null,
  "resolution_notes": null,
  "resolved_by": null,
  "resolved_at": null,
  "escalated_at": "2026-03-07T10:00:00Z",
  "created_at": "2026-03-05T14:00:00Z",
  "updated_at": "2026-03-07T10:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_party` | User is not a party to this dispute |
| 404 | `dispute_not_found` | No dispute with this ID |
| 409 | `already_escalated` | Dispute has already been escalated |
| 409 | `dispute_closed` | Cannot escalate a resolved dispute |
