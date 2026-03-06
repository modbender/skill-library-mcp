---
name: pinata-api
description: Pinata IPFS API for file storage, groups, gateways, signatures, x402 payments, and file vectorization.
homepage: https://pinata.cloud
metadata: {"openclaw": {"emoji": "📌", "requires": {"env": ["PINATA_JWT", "PINATA_GATEWAY_URL"]}, "primaryEnv": "PINATA_JWT"}}
---

# Pinata API

Access the Pinata IPFS storage API. Upload files, manage groups, create gateways, add signatures, set up x402 payments, and perform AI-powered vector search.

Repo: https://github.com/PinataCloud/pinata-api-skill

## Authentication

All requests require the header:

```
Authorization: Bearer $PINATA_JWT
```

**Environment Variables:**

- `PINATA_JWT` (required) - Your Pinata API JWT token. Get one at [app.pinata.cloud/developers/api-keys](https://app.pinata.cloud/developers/api-keys)
- `PINATA_GATEWAY_URL` (required) - Your Pinata gateway domain (e.g., `your-gateway.mypinata.cloud`). Find yours at [app.pinata.cloud/gateway](https://app.pinata.cloud/gateway)
- `PINATA_GATEWAY_KEY` (optional) - Gateway key for accessing public IPFS content not tied to your Pinata account. See [Gateway Access Controls](https://docs.pinata.cloud/gateways/gateway-access-controls#gateway-keys)

### Test Authentication

```
GET https://api.pinata.cloud/data/testAuthentication
```

## Base URLs

- **API:** `https://api.pinata.cloud`
- **Uploads:** `https://uploads.pinata.cloud`

## Common Parameters

- `{network}` - IPFS network: `public` (default) or `private`
- Pagination uses `limit` and `pageToken` query parameters

## Files

### Search Files

```
GET https://api.pinata.cloud/v3/files/{network}
```

Query parameters (all optional): `name`, `cid`, `mimeType`, `limit`, `pageToken`

### Get File by ID

```
GET https://api.pinata.cloud/v3/files/{network}/{id}
```

### Update File Metadata

```
PUT https://api.pinata.cloud/v3/files/{network}/{id}
Content-Type: application/json
```

Body:

```json
{
  "name": "new-name",
  "keyvalues": {"key": "value"}
}
```

Both fields are optional.

### Delete File

```
DELETE https://api.pinata.cloud/v3/files/{network}/{id}
```

### Upload File

```
POST https://uploads.pinata.cloud/v3/files
Content-Type: multipart/form-data
```

Form fields:
- `file` (required) - The file to upload
- `network` (optional) - `public` or `private`
- `group_id` (optional) - Group to add the file to
- `keyvalues` (optional) - JSON string of key-value metadata

## Groups

### List Groups

```
GET https://api.pinata.cloud/v3/groups/{network}
```

Query parameters (all optional): `name`, `limit`, `pageToken`

### Create Group

```
POST https://api.pinata.cloud/v3/groups/{network}
Content-Type: application/json
```

Body:

```json
{
  "name": "my-group"
}
```

### Get Group

```
GET https://api.pinata.cloud/v3/groups/{network}/{id}
```

### Update Group

```
PUT https://api.pinata.cloud/v3/groups/{network}/{id}
Content-Type: application/json
```

Body:

```json
{
  "name": "updated-name"
}
```

### Delete Group

```
DELETE https://api.pinata.cloud/v3/groups/{network}/{id}
```

### Add File to Group

```
PUT https://api.pinata.cloud/v3/groups/{network}/{groupId}/ids/{fileId}
```

### Remove File from Group

```
DELETE https://api.pinata.cloud/v3/groups/{network}/{groupId}/ids/{fileId}
```

## Gateway & Downloads

### Create Private Download Link

```
POST https://api.pinata.cloud/v3/files/private/download_link
Content-Type: application/json
```

Creates a temporary signed URL for accessing private files.

Body:

```json
{
  "url": "https://{PINATA_GATEWAY_URL}/files/{cid}",
  "expires": 600,
  "date": 1700000000,
  "method": "GET"
}
```

- `url` (required) - Full gateway URL using your `PINATA_GATEWAY_URL` and the file's CID
- `expires` (optional) - Seconds until expiry (default: 600)
- `date` (required) - Current Unix timestamp in seconds
- `method` (required) - HTTP method, typically `GET`

### Create Signed Upload URL

```
POST https://uploads.pinata.cloud/v3/files/sign
Content-Type: application/json
```

Creates a pre-signed URL for client-side uploads (no JWT needed on the client).

Body:

```json
{
  "date": 1700000000,
  "expires": 3600
}
```

Optional fields: `max_file_size` (bytes), `allow_mime_types` (array), `group_id`, `filename`, `keyvalues`

## Signatures

EIP-712 signatures for verifying content authenticity.

### Add Signature

```
POST https://api.pinata.cloud/v3/files/{network}/signature/{cid}
Content-Type: application/json
```

Body:

```json
{
  "signature": "0x...",
  "address": "0x..."
}
```

### Get Signature

```
GET https://api.pinata.cloud/v3/files/{network}/signature/{cid}
```

### Delete Signature

```
DELETE https://api.pinata.cloud/v3/files/{network}/signature/{cid}
```

## Pin By CID

Pin existing IPFS content by its CID (public network only).

### Pin a CID

```
POST https://api.pinata.cloud/v3/files/public/pin_by_cid
Content-Type: application/json
```

Body:

```json
{
  "cid": "bafybeig..."
}
```

Optional fields: `name`, `group_id`, `keyvalues`, `host_nodes` (array of multiaddrs)

### Query Pin Requests

```
GET https://api.pinata.cloud/v3/files/public/pin_by_cid
```

Query parameters (all optional): `order` (`ASC`/`DESC`), `status`, `cid`, `limit`, `pageToken`

### Cancel Pin Request

```
DELETE https://api.pinata.cloud/v3/files/public/pin_by_cid/{id}
```

## x402 Payment Instructions

Create payment instructions for monetizing IPFS content using the x402 protocol with USDC on Base.

**USDC Contract Addresses:**
- Base mainnet: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- Base Sepolia (testnet): `0x036CbD53842c5426634e7929541eC2318f3dCF7e`

**Important:** The `amount` field uses the smallest USDC unit (6 decimals). For example, $1.50 = `"1500000"`.

### Create Payment Instruction

```
POST https://api.pinata.cloud/v3/x402/payment_instructions
Content-Type: application/json
```

Body:

```json
{
  "name": "My Payment",
  "description": "Pay to access this content",
  "payment_requirements": [
    {
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "pay_to": "0xWALLET_ADDRESS",
      "network": "base",
      "amount": "1500000"
    }
  ]
}
```

- `name` (required) - Display name
- `description` (optional) - Description
- `payment_requirements` (required) - Array with `asset` (USDC contract address), `pay_to` (wallet address), `network` (`base` or `base-sepolia`), `amount` (smallest unit as string)

### List Payment Instructions

```
GET https://api.pinata.cloud/v3/x402/payment_instructions
```

Query parameters (all optional): `limit`, `pageToken`, `cid`, `name`, `id`

### Get Payment Instruction

```
GET https://api.pinata.cloud/v3/x402/payment_instructions/{id}
```

### Delete Payment Instruction

```
DELETE https://api.pinata.cloud/v3/x402/payment_instructions/{id}
```

### Associate CID with Payment

```
PUT https://api.pinata.cloud/v3/x402/payment_instructions/{id}/cids/{cid}
```

### Remove CID from Payment

```
DELETE https://api.pinata.cloud/v3/x402/payment_instructions/{id}/cids/{cid}
```

## Vectorize (AI Search)

Generate vector embeddings for files and perform semantic search across groups.

### Vectorize a File

```
POST https://uploads.pinata.cloud/v3/vectorize/files/{file_id}
```

### Delete File Vectors

```
DELETE https://uploads.pinata.cloud/v3/vectorize/files/{file_id}
```

### Query Vectors (Semantic Search)

```
POST https://uploads.pinata.cloud/v3/vectorize/groups/{group_id}/query
Content-Type: application/json
```

Body:

```json
{
  "text": "search query here"
}
```

## Notes

- All JSON endpoints require `Content-Type: application/json`
- File uploads use `multipart/form-data` — do not set Content-Type manually
- Pagination: use `pageToken` from the previous response to get the next page
- Network defaults to `public` if not specified
- Gateway URLs follow the pattern `https://{PINATA_GATEWAY_URL}/files/{cid}`

## Resources

- [Pinata Documentation](https://docs.pinata.cloud)
- [API Keys](https://app.pinata.cloud/developers/api-keys)
- [Gateway Setup](https://docs.pinata.cloud/gateways)
- [x402 Protocol](https://docs.pinata.cloud/x402)
- [Source (GitHub)](https://github.com/PinataCloud/pinata-api-skill)
