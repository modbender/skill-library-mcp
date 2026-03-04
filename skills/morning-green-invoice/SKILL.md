---
name: morning
description: Use to authenticate with Morning (GreenInvoice) and create/manage clients, items, and accounting documents (invoice/receipt/quote/order/credit).
---

# Morning (GreenInvoice)

## When to use
Use this skill when you need to interact with **Morning / GreenInvoice** to:
- Get an auth token (JWT) using API key credentials
- Create/update **clients**
- Create/update **items**
- Create **documents** (invoice / receipt / quote / order / credit / debit)
- Retrieve document outputs (e.g., IDs / links) if the tool supports it

## What you need from the user
Collect only what’s required for the action:

### Authentication
- `apiKeyId`
- `apiKeySecret`

### Client (if creating or searching)
- `name`
- Optional: `taxId`, `email`, `phone`, `address`, `city`, `country`

### Item (if creating)
- `name`
- `price`
- Optional: `description`, `currency`

### Document (if creating)
- `documentType` (Invoice / Receipt / Quote / Order / CreditInvoice / DebitInvoice)
- `clientId` (or enough info to create the client)
- `lines[]` (each line: description or itemId, quantity, unitPrice)
- Optional: `currency`, `language`, `description`, `discount`

## Tool contract
Use the `morning` tool with an `action` field.

### Supported actions
- `getToken`
- `createClient`
- `createItem`
- `createDocument`
- (Optional, if implemented in your tool): `findClient`, `findItem`, `getDocument`, `listDocuments`

## Guardrails
- Never log or echo `apiKeySecret` or JWTs back to the user.
- Prefer reusing existing `clientId` / `itemId` when available.
- Validate document lines:
  - `quantity` > 0
  - `unitPrice` >= 0
- Currency: default to `"ILS"` unless the user specifies otherwise.
- Language: default to `"Hebrew"` unless the user specifies otherwise.

## Examples

### 1) Authenticate (JWT)
```json
{
  "action": "getToken",
  "apiKeyId": "YOUR_API_KEY_ID",
  "apiKeySecret": "YOUR_API_KEY_SECRET"
}
```

### 2) Create a client
```json
{
  "action": "createClient",
  "jwt": "JWT_FROM_getToken",
  "client": {
    "name": "Acme Ltd",
    "taxId": "515555555",
    "email": "billing@acme.com",
    "phone": "+972-50-000-0000",
    "address": "1 Rothschild Blvd",
    "city": "Tel Aviv",
    "country": "Israel"
  }
}
```

### 3) Create an item
```json
{
  "action": "createItem",
  "jwt": "JWT_FROM_getToken",
  "item": {
    "name": "Consulting hour",
    "description": "Senior engineering consulting",
    "price": 500,
    "currency": "ILS"
  }
}
```

### 4) Create a document (Invoice)
```json
{
  "action": "createDocument",
  "jwt": "JWT_FROM_getToken",
  "document": {
    "documentType": "Invoice",
    "language": "English",
    "currency": "ILS",
    "clientId": "CLIENT_ID",
    "description": "Invoice for January services",
    "lines": [
      {
        "description": "Consulting hour",
        "quantity": 10,
        "unitPrice": 500
      }
    ]
  }
}
```

### 5) Create a document (Receipt) using itemId
```json
{
  "action": "createDocument",
  "jwt": "JWT_FROM_getToken",
  "document": {
    "documentType": "Receipt",
    "language": "Hebrew",
    "currency": "ILS",
    "clientId": "CLIENT_ID",
    "lines": [
      {
        "itemId": "ITEM_ID",
        "quantity": 1,
        "unitPrice": 1200
      }
    ]
  }
}
```

## Error handling
- If token is rejected (401/403): call `getToken` again and retry the request once.
- If client/item already exists:
  - Prefer returning the existing ID (if tool supports lookup),
  - Otherwise surface a clear message: “Client already exists; provide clientId or unique identifier.”
- If validation fails: ask for the missing/invalid fields only (e.g., “quantity must be > 0”).

## Output expectations
Return minimally:
- Created resource IDs (`clientId`, `itemId`, `documentId`)
- Any relevant URLs (PDF / view links) if the API/tool provides them
