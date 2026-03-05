---
name: consortium-ai-create-account
displayName: Consortium AI Create Account
description: Create a custodial wallet account on Consortium AI.
requirements: TRADING_ANALYSIS_API_KEY
author: Consortium AI
authorUrl: https://consortiumai.org/
keywords: ["crypto", "wallet", "create", "account", "custodial", "API"]
category: trading
---

## Instructions

This skill provides **account creation** functionality for Consortium AI.

It calls an external API that creates a custodial wallet account on Consortium AI.

### How to run (implementation)

From the skill directory, you can call the API either by making HTTP requests (see API Reference) or by running the bundled script:

- **Create Account:**
  `node scripts/create-account.js <WALLET_ADDRESS>`
  or `npm run create-account -- <WALLET_ADDRESS>`
  Example: `node scripts/create-account.js 5h4...3k1`

The script requires `TRADING_ANALYSIS_API_KEY` to be set. It prints the API response as JSON to stdout on success, or error JSON to stderr and exits non-zero on failure.

---

## Setup

Set the API key as an environment variable before using this skill:

```bash
export TRADING_ANALYSIS_API_KEY=your-secret-api-key
```

To get an API key, contact [Consortium AI on X](https://x.com/Consortium_AI).

---

## API Reference

**Backend API base URL:** `https://api.consortiumai.org`

**Endpoint:** `POST https://api.consortiumai.org/api/custodial-wallet/create-with-api-key`
Creates a new custodial wallet account.

### Authentication

API key only (no JWT). Send the key in one of:

- **Header:** `x-api-key: <TRADING_ANALYSIS_API_KEY>`
- **Header:** `Authorization: Bearer <TRADING_ANALYSIS_API_KEY>`

### Request Body

```json
{
  "walletAddress": "5h4...YourWalletAddress...3k1"
}
```

### Success response (201 Created)

```json
{
  "message": "Custodial wallet created successfully",
  "data": {
    "id": "wallet_uuid",
    "wallet_address": "GeneratedCustodialWalletAddress",
    "user_id": "user_uuid",
    "created_at": "2024-03-20T10:00:00.000Z",
    "updated_at": "2024-03-20T10:00:00.000Z"
  }
}
```

### Error responses

| Status | When | Body (example) |
|--------|------|----------------|
| **400** | Missing walletAddress | `{ "error": "Missing walletAddress" }` |
| **401** | Missing or wrong API key | `{ "success": false, "message": "Invalid or missing API key" }` |
| **404** | User not found for wallet address | `{ "error": "User not found for the provided wallet address" }` |

---

## Available Functions

### createCustodialWallet(walletAddress)

**Purpose**
Create a new custodial wallet account on Consortium AI.

**Parameters**

- `walletAddress` (string): The user's wallet address.

**Expected Behavior**

- Sends a POST request to `https://api.consortiumai.org/api/custodial-wallet/create-with-api-key`
- Authenticates with `x-api-key` using `TRADING_ANALYSIS_API_KEY`
- Returns the created wallet details.

**Returns**

- Wallet ID
- Generated Custodial Wallet Address
- User ID
- Creation timestamp