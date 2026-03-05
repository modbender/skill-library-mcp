---
name: xproof
description: Certify agent outputs on the MultiversX blockchain. Anchor hashes, text, files, and decisions with tamper-proof on-chain proof. $0.05/cert, 6-second finality. Supports API key and x402 payment (no account required).
homepage: https://xproof.app
version: 1.2.0
author: jasonxkensei
tags: [blockchain, proof, certification, multiversx, agents, trust, mx-8004, x402]
metadata: {"clawdbot":{"emoji":"🔏","category":"blockchain","requires":{"env":["XPROOF_API_KEY"]},"primaryEnv":"XPROOF_API_KEY"}}
---

# xProof — Blockchain Proof of Existence for Agents

xProof anchors agent outputs to the MultiversX blockchain. Any text, hash, file, or decision becomes a permanent, tamper-proof record with a verifiable on-chain certificate.

**Use this skill when:**
- Certifying agent outputs, decisions, or reports that need to be verifiable
- Anchoring content before it is shared, published, or acted upon
- Building audit trails for autonomous agent pipelines
- Proving a document or output existed at a specific point in time

## Authentication

**Option 1 — API Key (recommended):**
Set `XPROOF_API_KEY` in your environment. Get a key at https://xproof.app.

**Option 2 — x402 (no account required):**
Send USDC on Base. The API returns a `402` with payment instructions; include the `X-Payment` header (base64-encoded JSON) in your follow-up request.

## Certify Text or a Hash

```bash
# Certify text content
curl -s -X POST https://xproof.app/api/proof \
  -H "Authorization: Bearer $XPROOF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The agent decided: deploy to production at 2026-02-20T14:00:00Z",
    "metadata": {"agent": "deploy-bot", "pipeline": "release-v2.1"}
  }'

# Certify a SHA-256 hash (if you already have it)
curl -s -X POST https://xproof.app/api/proof \
  -H "Authorization: Bearer $XPROOF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"hash": "sha256:<64-char-hex>"}'
```

**Response:**
```json
{
  "id": "cert_abc123",
  "status": "pending",
  "hash": "sha256:...",
  "txHash": "...",
  "blockchainUrl": "https://explorer.multiversx.com/transactions/...",
  "verifyUrl": "https://xproof.app/verify/cert_abc123",
  "certifiedAt": "2026-02-20T14:00:05Z"
}
```

## Certify a File

```bash
# Hash a file locally and certify the hash
FILE_HASH=$(sha256sum report.pdf | awk '{print $1}')

curl -s -X POST https://xproof.app/api/proof \
  -H "Authorization: Bearer $XPROOF_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"hash\": \"sha256:${FILE_HASH}\", \"metadata\": {\"filename\": \"report.pdf\"}}"
```

## Batch Certify (up to 50)

```bash
curl -s -X POST https://xproof.app/api/batch \
  -H "Authorization: Bearer $XPROOF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "proofs": [
      {"content": "Output 1"},
      {"content": "Output 2"},
      {"hash": "sha256:<hash-3>"}
    ]
  }'
```

## Verify a Certificate

```bash
# By certificate ID
curl -s https://xproof.app/api/proof/cert_abc123

# Response includes on-chain status: pending | confirmed | failed
```

## MX-8004 Integration (MultiversX Agent Validation Loop)

xProof implements the full MX-8004 validation loop. To submit a certified proof as an on-chain MX-8004 validation:

```bash
# Step 1: Certify the output
CERT=$(curl -s -X POST https://xproof.app/api/proof \
  -H "Authorization: Bearer $XPROOF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "Agent output to validate"}')

CERT_ID=$(echo $CERT | jq -r '.id')
CERT_HASH=$(echo $CERT | jq -r '.hash')

# Step 2: Submit as MX-8004 proof (handled by xProof internally)
# xProof anchors on MultiversX and calls giveFeedback on the Validation Registry.
# The verifyUrl in the response is the permanent on-chain reference.
echo "Certificate: $CERT_ID"
echo "Verify at: $(echo $CERT | jq -r '.verifyUrl')"
```

## x402 Payment (No Account Required)

```bash
# Step 1: Attempt the request — receive 402
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://xproof.app/api/proof \
  -H "Content-Type: application/json" \
  -d '{"content": "Certify this"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "402" ]; then
  # Step 2: Parse payment instructions and pay with USDC on Base
  # Then resubmit with X-Payment header (base64-encoded payment JSON)
  echo "Payment required: $(echo $BODY | jq -r '.accepts[0]')"
fi
```

## MCP Server

xProof exposes an MCP server at `https://xproof.app/mcp`.

Add to your OpenClaw config:
```json
{
  "mcp": {
    "servers": {
      "xproof": {
        "url": "https://xproof.app/mcp",
        "headers": {"Authorization": "Bearer ${XPROOF_API_KEY}"}
      }
    }
  }
}
```

Available MCP tools: `certify_content`, `certify_hash`, `certify_batch`, `verify_proof`.

## Pricing

| Volume | Price |
|--------|-------|
| 0 - 100K certs/month | $0.05/cert |
| 100K - 1M certs/month | $0.025/cert |
| 1M+ certs/month | $0.01/cert |

Check current pricing: `curl https://xproof.app/api/pricing`

## Security & Privacy

- Content submitted via `content` field is hashed server-side before anchoring; the original text is not stored on-chain.
- Only the SHA-256 hash and optional metadata are written to MultiversX.
- API keys are scoped to a single account and can be rotated at https://xproof.app.
- x402 payments are processed on Base; no account or email required.

**External endpoints called:** `https://xproof.app` only.

By using this skill, hashes and optional metadata are sent to xproof.app for blockchain anchoring on MultiversX.

## Resources

- Homepage: https://xproof.app
- API docs: https://xproof.app/llms.txt
- Full reference: https://xproof.app/llms-full.txt
- Agent manifest: https://xproof.app/.well-known/agent.json
- MCP Registry: https://registry.modelcontextprotocol.io/v0/servers?search=xproof
- MultiversX explorer: https://explorer.multiversx.com
