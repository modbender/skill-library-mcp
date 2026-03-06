# Contracts API

Base URL: `/api/v1/contracts` and `/api/v1/contract-templates`

Contracts govern the terms of personal-business transactions. Personal users can read contract templates, create contract instances from templates, negotiate terms, and accept or reject contracts.

All endpoints require authentication.

---

## GET /api/v1/contract-templates/{template_id}

Retrieve a single contract template. Templates are created by businesses or the system and define default terms, locked fields, and negotiable fields.

**Auth:** Required

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `template_id` | UUID | Yes | Contract template ID |

### Request Body

None.

### Request Example

```
GET /api/v1/contract-templates/44556677-8899-aabb-ccdd-eeff00112233
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "44556677-8899-aabb-ccdd-eeff00112233",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "name": "标准大模型微调服务合同",
  "default_terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "data_retention_days": 90,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%",
    "payment_schedule": "escrow_full"
  },
  "default_contract_type": "service",
  "locked_fields": ["confidentiality", "payment_schedule"],
  "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
  "status": "active",
  "is_system_template": false,
  "created_at": "2026-01-20T10:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Contract template not found"` | Template ID does not exist |

---

## POST /api/v1/contracts/

Create a new contract instance from a template. The contract starts in `draft` status with terms copied from the template.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `template_id` | UUID | Yes | Contract template to instantiate from |
| `personal_id` | UUID \| None | No | Personal ID; defaults to the current user if omitted |

### Request Example

```json
{
  "template_id": "44556677-8899-aabb-ccdd-eeff00112233"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "66778899-aabb-ccdd-eeff-001122334455",
  "template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_type": "service",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "terms": {
    "delivery_days": 14,
    "revision_rounds": 2,
    "data_retention_days": 90,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%",
    "payment_schedule": "escrow_full"
  },
  "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
  "negotiation_history": [],
  "disclaimer": null,
  "status": "draft",
  "confirmed_at": null,
  "fulfilled_at": null,
  "created_at": "2026-02-27T14:00:00Z",
  "updated_at": "2026-02-27T14:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 404 | `"Contract template not found"` | Template ID does not exist |
| 422 | Pydantic validation array | Invalid template_id format |

---

## GET /api/v1/contracts/

List contract instances for the current user.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `role` | str | No | Filter by role perspective, default `"business"`. Values: `"business"`, `"business"` |
| `offset` | int | No | Pagination offset, default `0` |
| `limit` | int | No | Items per page, default `20`, max `100` |

### Request Example

```
GET /api/v1/contracts/?role=personal&offset=0&limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "items": [
    {
      "id": "66778899-aabb-ccdd-eeff-001122334455",
      "template_id": "44556677-8899-aabb-ccdd-eeff00112233",
      "contract_type": "service",
      "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "terms": {
        "delivery_days": 14,
        "revision_rounds": 2,
        "data_retention_days": 90,
        "ip_ownership": "personal",
        "confidentiality": true,
        "sla_uptime": "99.5%",
        "payment_schedule": "escrow_full"
      },
      "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
      "negotiation_history": [],
      "disclaimer": null,
      "status": "draft",
      "confirmed_at": null,
      "fulfilled_at": null,
      "created_at": "2026-02-27T14:00:00Z",
      "updated_at": "2026-02-27T14:00:00Z"
    }
  ],
  "total": 1
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## GET /api/v1/contracts/{contract_id}

Retrieve a single contract instance. Both parties can access.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `contract_id` | UUID | Yes | Contract instance ID |

### Request Body

None.

### Request Example

```
GET /api/v1/contracts/66778899-aabb-ccdd-eeff-001122334455
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "66778899-aabb-ccdd-eeff-001122334455",
  "template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_type": "service",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "terms": {
    "delivery_days": 21,
    "revision_rounds": 3,
    "data_retention_days": 90,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%",
    "payment_schedule": "escrow_full"
  },
  "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
  "negotiation_history": [
    {
      "round": 1,
      "party": "personal",
      "changes": {"delivery_days": 21, "revision_rounds": 3},
      "timestamp": "2026-02-27T15:00:00Z"
    }
  ],
  "disclaimer": null,
  "status": "negotiating",
  "confirmed_at": null,
  "fulfilled_at": null,
  "created_at": "2026-02-27T14:00:00Z",
  "updated_at": "2026-02-27T15:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to access this contract"` | User is not personal or business |
| 404 | `"Contract not found"` | Contract ID does not exist |

---

## POST /api/v1/contracts/{contract_id}/negotiate

Propose changes to negotiable fields. Each call appends a new entry to `negotiation_history`.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `contract_id` | UUID | Yes | Contract instance ID |

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `changes` | dict | Yes | Key-value pairs of field changes. Only negotiable fields are allowed. |

### Request Example

```json
{
  "changes": {
    "delivery_days": 21,
    "revision_rounds": 3
  }
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "66778899-aabb-ccdd-eeff-001122334455",
  "template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_type": "service",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "terms": {
    "delivery_days": 21,
    "revision_rounds": 3,
    "data_retention_days": 90,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%",
    "payment_schedule": "escrow_full"
  },
  "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
  "negotiation_history": [
    {
      "round": 1,
      "party": "personal",
      "changes": {"delivery_days": 21, "revision_rounds": 3},
      "timestamp": "2026-02-27T15:00:00Z"
    }
  ],
  "disclaimer": null,
  "status": "negotiating",
  "confirmed_at": null,
  "fulfilled_at": null,
  "created_at": "2026-02-27T14:00:00Z",
  "updated_at": "2026-02-27T15:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Cannot modify locked field: confidentiality"` | Attempting to change a locked field |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to negotiate this contract"` | User is not a party |
| 404 | `"Contract not found"` | Contract ID does not exist |
| 409 | `"Contract is not in a negotiable status"` | Contract is already accepted/rejected |
| 422 | Pydantic validation array | Empty changes dict |

---

## POST /api/v1/contracts/{contract_id}/accept

Accept the current contract terms. Both parties must accept for the contract to become `confirmed`.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `contract_id` | UUID | Yes | Contract instance ID |

### Request Body

None.

### Request Example

```
POST /api/v1/contracts/66778899-aabb-ccdd-eeff-001122334455/accept
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "66778899-aabb-ccdd-eeff-001122334455",
  "template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_type": "service",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "terms": {
    "delivery_days": 21,
    "revision_rounds": 3,
    "data_retention_days": 90,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%",
    "payment_schedule": "escrow_full"
  },
  "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
  "negotiation_history": [
    {
      "round": 1,
      "party": "personal",
      "changes": {"delivery_days": 21, "revision_rounds": 3},
      "timestamp": "2026-02-27T15:00:00Z"
    }
  ],
  "disclaimer": null,
  "status": "confirmed",
  "confirmed_at": "2026-02-27T16:00:00Z",
  "fulfilled_at": null,
  "created_at": "2026-02-27T14:00:00Z",
  "updated_at": "2026-02-27T16:00:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to accept this contract"` | User is not a party |
| 404 | `"Contract not found"` | Contract ID does not exist |
| 409 | `"Contract is not in a status that can be accepted"` | Contract is already confirmed/rejected |

---

## POST /api/v1/contracts/{contract_id}/reject

Reject the contract. This terminates the negotiation.

**Auth:** Required (party)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `contract_id` | UUID | Yes | Contract instance ID |

### Request Body

None.

### Request Example

```
POST /api/v1/contracts/66778899-aabb-ccdd-eeff-001122334455/reject
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "66778899-aabb-ccdd-eeff-001122334455",
  "template_id": "44556677-8899-aabb-ccdd-eeff00112233",
  "contract_type": "service",
  "business_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "personal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "terms": {
    "delivery_days": 21,
    "revision_rounds": 3,
    "data_retention_days": 90,
    "ip_ownership": "personal",
    "confidentiality": true,
    "sla_uptime": "99.5%",
    "payment_schedule": "escrow_full"
  },
  "negotiable_fields": ["delivery_days", "revision_rounds", "data_retention_days", "ip_ownership"],
  "negotiation_history": [
    {
      "round": 1,
      "party": "personal",
      "changes": {"delivery_days": 21, "revision_rounds": 3},
      "timestamp": "2026-02-27T15:00:00Z"
    }
  ],
  "disclaimer": null,
  "status": "rejected",
  "confirmed_at": null,
  "fulfilled_at": null,
  "created_at": "2026-02-27T14:00:00Z",
  "updated_at": "2026-02-27T16:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to reject this contract"` | User is not a party |
| 404 | `"Contract not found"` | Contract ID does not exist |
| 409 | `"Contract is not in a status that can be rejected"` | Contract is already confirmed/rejected |
