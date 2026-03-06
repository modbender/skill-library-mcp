# Wallet API

Base URL: `/api/v1/wallet`

Virtual escrow wallet for managing funds on TMR Land. Supports USD and USDC balances. Funds are frozen during active orders and released upon completion. No real payment gateway (MVP).

---

## GET /api/v1/wallet

Retrieve the authenticated user's wallet balance and status.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/wallet
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "id": "44556677-8899-aabb-ccdd-eeff00112233",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "balance": 2450.00,
  "frozen_balance": 300.00,
  "currency": "USD",
  "status": "active",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T14:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `wallet_not_found` | User does not have a wallet |

---

## POST /api/v1/wallet/charge

Add funds to the wallet. In the MVP this is a simulated deposit.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `amount` | float | Yes | Amount to deposit, must be greater than 0 |
| `currency` | str | No | Currency code. Default `"USD"` |

### Request Example

```json
{
  "amount": 500.00,
  "currency": "USD"
}
```

### Response Example

```json
{
  "id": "44556677-8899-aabb-ccdd-eeff00112233",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "balance": 2950.00,
  "frozen_balance": 300.00,
  "currency": "USD",
  "status": "active",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T15:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 422 | `validation_error` | Amount must be greater than 0 |

---

## POST /api/v1/wallet/withdraw

Withdraw funds from the wallet. Businesses use this to cash out earnings.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `amount` | float | Yes | Amount to withdraw, must be greater than 0 |
| `currency` | str | No | Currency code. Default `"USD"` |

### Request Example

```json
{
  "amount": 1000.00,
  "currency": "USD"
}
```

### Response Example

```json
{
  "id": "44556677-8899-aabb-ccdd-eeff00112233",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "balance": 1950.00,
  "frozen_balance": 300.00,
  "currency": "USD",
  "status": "active",
  "created_at": "2026-02-27T10:30:00Z",
  "updated_at": "2026-02-27T15:30:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 400 | `insufficient_balance` | Available balance (balance - frozen) is less than the withdrawal amount |
| 422 | `validation_error` | Amount must be greater than 0 |

---

## GET /api/v1/wallet/transactions

List wallet transaction history.

**Auth:** Required

### Query Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `offset` | int | No | Pagination offset. Default `0` |
| `limit` | int | No | Number of results. Default `20` |

### Request Example

```
GET /api/v1/wallet/transactions?offset=0&limit=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "items": [
    {
      "id": "aabb0011-2233-4455-6677-8899aabbccdd",
      "wallet_id": "44556677-8899-aabb-ccdd-eeff00112233",
      "type": "credit",
      "amount": 135.00,
      "currency": "USD",
      "description": "Order payout: 11223344-5566-7788-99aa-bbccddeeff00",
      "reference_id": "11223344-5566-7788-99aa-bbccddeeff00",
      "reference_type": "order",
      "created_at": "2026-03-01T16:30:00Z"
    },
    {
      "id": "bbcc1122-3344-5566-7788-99aabbccddee",
      "wallet_id": "44556677-8899-aabb-ccdd-eeff00112233",
      "type": "freeze",
      "amount": 150.00,
      "currency": "USD",
      "description": "Escrow freeze: order 22334455-6677-8899-aabb-ccddeeff0011",
      "reference_id": "22334455-6677-8899-aabb-ccddeeff0011",
      "reference_type": "order",
      "created_at": "2026-02-28T09:00:00Z"
    },
    {
      "id": "ccdd2233-4455-6677-8899-aabbccddeeff",
      "wallet_id": "44556677-8899-aabb-ccdd-eeff00112233",
      "type": "deposit",
      "amount": 500.00,
      "currency": "USD",
      "description": "Manual deposit",
      "reference_id": null,
      "reference_type": null,
      "created_at": "2026-02-27T15:00:00Z"
    }
  ],
  "total": 3
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## POST /api/v1/wallet/kyc

Submit KYC (Know Your Customer) verification information.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `full_name` | str | Yes | Legal full name |
| `id_type` | str | Yes | ID document type (e.g., `"passport"`, `"national_id"`, `"driver_license"`) |
| `id_number` | str | Yes | ID document number |

### Request Example

```json
{
  "full_name": "张明",
  "id_type": "national_id",
  "id_number": "310101199001011234"
}
```

### Response Example

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "full_name": "张明",
  "id_type": "national_id",
  "id_number": "310101****1234",
  "status": "pending",
  "submitted_at": "2026-02-27T10:30:00Z",
  "verified_at": null
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 409 | `kyc_already_submitted` | KYC verification has already been submitted |
| 422 | `validation_error` | Missing required fields |

---

## GET /api/v1/wallet/kyc

Retrieve the current KYC verification status.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/wallet/kyc
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "full_name": "张明",
  "id_type": "national_id",
  "id_number": "310101****1234",
  "status": "verified",
  "submitted_at": "2026-02-27T10:30:00Z",
  "verified_at": "2026-02-27T12:00:00Z"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 404 | `kyc_not_found` | No KYC submission found for this user |
