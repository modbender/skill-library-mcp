# Error Codes

This document covers the standard HTTP error codes returned by the TMR Land API and their response formats.

---

## Standard Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422), the response contains an array of field-level errors:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Description of the validation failure",
      "type": "error_type"
    }
  ]
}
```

---

## 400 Bad Request

Returned when the request is syntactically valid but fails business logic validation.

### Common Causes

- Insufficient wallet balance for payment
- Invalid state transition (e.g. cancelling a delivered order)
- Duplicate resource creation (e.g. KYC already submitted)
- Amount exceeds limits

### Example

```json
{
  "detail": "Insufficient wallet balance"
}
```

---

## 401 Unauthorized

Returned when authentication is missing, expired, or invalid.

### Common Causes

- No `Authorization` header provided
- Bearer token is expired
- Bearer token is malformed or tampered with
- API key is invalid or revoked
- Invalid login credentials

### Example: Missing Token

```json
{
  "detail": "Not authenticated"
}
```

### Example: Invalid Credentials

```json
{
  "detail": "Incorrect email or password"
}
```

### Example: Expired Token

```json
{
  "detail": "Token has expired"
}
```

---

## 403 Forbidden

Returned when the authenticated user does not have permission to perform the requested action.

### Common Causes

- Wrong role for the endpoint (e.g. business trying to pay an order)
- Accessing a resource owned by another user
- Attempting an action reserved for the other party

### Example

```json
{
  "detail": "Only the personal user can pay for this order"
}
```

### Example: Resource Ownership

```json
{
  "detail": "Not authorized to access this intention"
}
```

---

## 404 Not Found

Returned when the requested resource does not exist.

### Common Causes

- UUID references a non-existent record
- Resource has been deleted
- Accessing a sub-resource that has not been created yet (e.g. receipt before review)

### Example

```json
{
  "detail": "Order not found"
}
```

### Example: Sub-resource

```json
{
  "detail": "Receipt not found"
}
```

---

## 409 Conflict

Returned when the request conflicts with the current state of the resource.

### Common Causes

- Invalid state transition (e.g. publishing an already published intention)
- Duplicate resource (e.g. dispute already exists for an order)
- Resource already in target state

### Example: State Transition

```json
{
  "detail": "Order is not in pending status"
}
```

### Example: Duplicate

```json
{
  "detail": "Dispute already exists for this order"
}
```

### Example: Edit Restriction

```json
{
  "detail": "Can only edit intentions in draft status"
}
```

---

## 422 Unprocessable Entity

Returned when request body fails Pydantic schema validation. This is the most common error for malformed requests.

### Common Causes

- Missing required fields
- Field type mismatch (e.g. string where integer expected)
- Value constraint violation (e.g. rating > 5, password < 8 chars)
- Invalid enum values

### Example: Missing Required Field

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### Example: Invalid Value

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "type": "string_too_short"
    }
  ]
}
```

### Example: Multiple Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address: An email address must have an @-sign.",
      "type": "value_error"
    },
    {
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "type": "string_too_short"
    }
  ]
}
```

### Example: Invalid Enum

```json
{
  "detail": [
    {
      "loc": ["body", "category"],
      "msg": "Input should be 'data', 'model', 'agent', 'consulting', 'content' or 'other'",
      "type": "enum"
    }
  ]
}
```

### Example: Numeric Constraint

```json
{
  "detail": [
    {
      "loc": ["body", "rating"],
      "msg": "Input should be less than or equal to 5",
      "type": "less_than_equal"
    }
  ]
}
```

---

## 500 Internal Server Error

Returned when an unexpected server-side error occurs. These are not caused by client input.

### Common Causes

- Unhandled exception in application code
- Database connection failure
- External service unavailable (Elasticsearch, Milvus, LLM provider)
- Configuration error

### Example

```json
{
  "detail": "Internal server error"
}
```

---

## Error Handling Recommendations

1. **Always check the status code first.** The `detail` field provides human-readable context.
2. **For 422 errors**, iterate over the `detail` array to identify which fields failed validation and why.
3. **For 409 errors**, check the current resource state before retrying. Use GET to fetch the resource and verify its status.
4. **For 401 errors**, attempt a token refresh using `POST /api/v1/auth/refresh` before prompting re-authentication.
5. **For 500 errors**, implement exponential backoff retry logic. If the error persists, contact platform support.

---

## HTTP Status Code Summary

| Code | Name | Usage |
|---|---|---|
| 200 | OK | Successful read or update |
| 201 | Created | Successful resource creation |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Business logic validation failure |
| 401 | Unauthorized | Authentication failure |
| 403 | Forbidden | Authorization / permission failure |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | State conflict or duplicate |
| 422 | Unprocessable Entity | Request schema validation failure |
| 500 | Internal Server Error | Unexpected server error |
