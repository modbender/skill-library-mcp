# BaseMail API Reference

Base URL: `https://api.basemail.ai`

## Authentication

BaseMail uses Sign-In with Ethereum (SIWE) for authentication.

### Get Nonce

```
GET /api/auth/nonce
```

Response:
```json
{"nonce": "uuid-string"}
```

### Verify Signature

```
POST /api/auth/verify
Content-Type: application/json

{
  "message": "SIWE message string",
  "signature": "0x...",
  "address": "0x..."
}
```

Response:
```json
{
  "token": "JWT token",
  "wallet": "0x...",
  "registered": false,
  "suggested_email": "0x...@basemail.ai",
  "pending_emails": 0
}
```

### SIWE Message Format

```
basemail.ai wants you to sign in with your Ethereum account:
0xYourWalletAddress

Sign in to BaseMail

URI: https://basemail.ai
Version: 1
Chain ID: 8453
Nonce: {nonce-from-api}
Issued At: {ISO-8601-timestamp}
```

## Registration

### Register Email

```
POST /api/register
Authorization: Bearer {token}
Content-Type: application/json

{}
```

Response:
```json
{
  "success": true,
  "email": "0x...@basemail.ai",
  "handle": "0x...",
  "wallet": "0x...",
  "token": "new-JWT-token"
}
```

## Email Operations

### Send Email

```
POST /api/send
Authorization: Bearer {token}
Content-Type: application/json

{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email body text"
}
```

Response (internal email):
```json
{
  "success": true,
  "email_id": "id-string",
  "internal": true
}
```

Response (external email, requires credits):
```json
{
  "success": true,
  "email_id": "id-string",
  "internal": false
}
```

### Get Inbox

```
GET /api/inbox
Authorization: Bearer {token}
```

### Read Email

```
GET /api/inbox/{email_id}
Authorization: Bearer {token}
```

## Credits (for External Email)

### Check Credits

```
GET /api/credits
Authorization: Bearer {token}
```

Response:
```json
{
  "credits": 1000,
  "pricing": {
    "credits_per_eth": 1000000,
    "deposit_address": "0x..."
  }
}
```

### Buy Credits

1. Send ETH to the deposit address on Base chain
2. Call the API with the transaction hash:

```
POST /api/credits/buy
Authorization: Bearer {token}
Content-Type: application/json

{
  "tx_hash": "0x..."
}
```

Response:
```json
{
  "success": true,
  "purchased": 1000,
  "balance": 1000
}
```

## Error Responses

```json
{
  "error": "Error message"
}
```

Common errors:
- 401: Missing or invalid authorization token
- 402: Insufficient credits for external email
- 404: Handle/email not found
