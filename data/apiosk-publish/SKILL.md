---
name: apiosk-publish
description: Publish and manage Apiosk gateway listings with signed wallet authentication, listing-group aware categorization, and update/delete operations.
---

# apiosk-publish

Use this skill for API publishing and lifecycle management on `https://gateway.apiosk.com`.

## When to use

- You need to register a new paid API on Apiosk.
- You need to update, list, or deactivate your published API.
- You need to map an API to the latest listing groups (`api`, `datasets`, `compute`).
- You need to send correctly signed wallet-auth headers for management endpoints.

## Required tools and files

- `curl`
- `jq`
- `cast` (Foundry)
- Wallet:
  - `~/.apiosk/wallet.json` (preferred, includes `address` + `private_key`)
  - or `APIOSK_PRIVATE_KEY` env var
  - or `--private-key` flag

## Management endpoints

- `POST /v1/apis/register`
- `GET /v1/apis/mine?wallet=0x...`
- `POST /v1/apis/:slug`
- `DELETE /v1/apis/:slug?wallet=0x...`

## Signed wallet auth

All management calls require:

- `x-wallet-address`
- `x-wallet-signature`
- `x-wallet-timestamp`
- `x-wallet-nonce`

Canonical message to sign:

```text
Apiosk auth
action:<action>
wallet:<lowercase_wallet>
resource:<resource>
timestamp:<unix_seconds>
nonce:<nonce>
```

Action/resource mapping:

- register: `action=register_api`, `resource=register:<slug>`
- update: `action=update_api`, `resource=update:<slug>`
- mine: `action=my_apis`, `resource=mine:<wallet>`
- delete: `action=delete_api`, `resource=delete:<slug>`

## Listing groups and categories

Discovery groups in gateway:

- `api`
- `datasets`
- `compute`

Register payload currently uses `category` (not explicit `listing_type`).
Use this mapping:

- `api` -> `data`
- `datasets` -> `dataset`
- `compute` -> `compute`

## Register payload

`POST /v1/apis/register`:

```json
{
  "name": "My API",
  "slug": "my-api",
  "endpoint_url": "https://example.com",
  "price_usd": 0.01,
  "description": "My paid API",
  "owner_wallet": "0x...",
  "category": "dataset"
}
```

## Agent behavior requirements

- Always sign management requests; unsigned calls should be treated as invalid.
- Keep wallet value lowercased inside the signed message, even if header uses checksum case.
- If `Unauthorized`, regenerate timestamp + nonce and re-sign once.
- Validate HTTPS endpoint before register/update.
- Use listing-group mapping above so new listings appear in the right discovery surfaces.
