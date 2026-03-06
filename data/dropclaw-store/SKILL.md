---
name: dropclaw-store
description: Store and retrieve encrypted files permanently on Monad blockchain via DropClaw x402 gateway
homepage: https://dropclaw.cloud
user-invocable: true
---

# DropClaw Store — Permanent Encrypted File Storage

Store any file permanently on-chain using AES-256-GCM client-side encryption and the x402 payment protocol. Zero-knowledge: the server never sees your encryption key.

## Quick Reference

- **API Base**: `https://dropclaw.cloud`
- **Protocol**: x402 (HTTP 402 payment flow)
- **Storage chain**: Monad (chainId 143)
- **Payment**: MON, SOL, or Base USDC
- **Cost**: ~$30 USD + gas to store. Free to retrieve.

## How to Store a File

1. Read the file into a buffer
2. Compute SHA-256 hash of the original
3. Compress with zlib deflate
4. Generate random 32-byte AES key + 12-byte IV
5. Encrypt with AES-256-GCM → output: `[IV:12][AuthTag:16][Ciphertext]`
6. `POST /vault/store` with the encrypted blob as multipart form data (field: `file`)
7. You will get a `402` response with payment options — pick a chain and send payment
8. Retry the POST with header `X-PAYMENT: base64(JSON({ network, txHash }))`
9. **CRITICAL**: Save BOTH the returned skill file AND your encryption key locally

## How to Retrieve a File

1. `POST /vault/retrieve/{fileId}` with the skill file JSON in the body
2. Receive encrypted blob
3. Extract IV (first 12 bytes), AuthTag (next 16 bytes), then ciphertext
4. Decrypt with AES-256-GCM using your saved key
5. Decompress with zlib inflate
6. Verify SHA-256 matches

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/vault/store` | x402 | Store encrypted file |
| POST | `/vault/retrieve/{fileId}` | none | Retrieve encrypted file |
| GET | `/vault/pricing?size={bytes}` | none | Get pricing for file size |
| GET | `/.well-known/x402` | none | x402 discovery manifest |
| GET | `/dropclaw-skill.json` | none | Full skill spec (JSON) |
| GET | `/claude-tools.json` | none | Claude tool definitions |
| GET | `/openai-tools.json` | none | OpenAI tool definitions |

## MCP Server

For Claude Desktop / Claude Code integration:
```
claude mcp add dropclaw -- node /path/to/mcp/index.js
```

Install SDK: `npm i dropclaw` or `pip install dropclaw`

## Payment Chains

- **Monad** (eip155:143) — MON native
- **Solana** (solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp) — SOL native
- **Base** (eip155:8453) — USDC

## Important

- The encryption key is generated client-side and NEVER sent to the server
- Without your key, files cannot be decrypted by anyone
- 50% of all fees go to FARNS token buyback
