---
name: aegis-security
version: 1.2.2
description: Blockchain security API for AI agents. Scan tokens, simulate transactions, check addresses for threats.
homepage: https://aegis402.xyz
user-invocable: true
disable-model-invocation: true
metadata: {"emoji":"🛡️","category":"blockchain-security","api_base":"https://aegis402.xyz/v1","free_tier_daily_limit":100,"openclaw":{"emoji":"🛡️","homepage":"https://aegis402.xyz"}}
---

# Aegis402 Shield Protocol

Blockchain security API for AI agents.

Free tier: 100 checks/day, then pay-per-request with USDC on Base or Solana.

## Security Defaults

- This skill is manual-use only (`disable-model-invocation: true`).
- Do not ask for or store private keys, seed phrases, or mnemonics.
- Confirm intent before paid calls (especially `simulate-tx`).
- Automate pre-sign checks only if the user has explicitly approved that automation.
- Required env vars for this skill: none.

## Agent Quickstart (Scan Before Transact)

Default policy for agents and wallets:

1. Set `X-Client-Fingerprint: <stable_agent_or_user_id>` for predictable free-tier accounting.
2. Before sending any transaction, run in parallel:
   - `GET /v1/check-address/:to`
   - `POST /v1/simulate-tx`
   - (Optional) `GET /v1/check-token/:token` for tokens involved (swaps/approvals)
3. Block and ask for confirmation if any result indicates `HIGH`/`CRITICAL`, `isSafe=false`, or recipient is poisoned/flagged.
4. Otherwise allow, but still show the review summary + raw JSON.

Notes:

- Free tier is best-effort abuse-limited, not a security mechanism. Rotating fingerprints can bypass free-tier buckets.
- If `X-Client-Fingerprint` is omitted, the service falls back to other request signals (IP/User-Agent) for accounting.

## What To Do (Agent Mode, From Zero)

When a user is about to send a transaction:

1. Ask for missing intent:
   - `from`, `to`, `value`, `data` (or "native transfer"), `chain_id`
2. Check free tier (always free):
   - `GET /v1/usage`
3. Run the scan-before-transact checks (parallel):
   - `GET /v1/check-address/:to`
   - `POST /v1/simulate-tx`
   - (Optional) `GET /v1/check-token/:token`
4. Reply using templates below (summary first, then raw JSON).

## How To Reply (Templates)

### SAFE (LOW)

```
🛡️ Scan Complete

Risk: LOW (SAFE)
Summary: No critical warnings detected.

✅ OK to proceed.
```

### CAUTION (MEDIUM)

```
🛡️ Scan Complete

Risk: MEDIUM (CAUTION)
Summary: Some warnings detected.

⚠️ Review recommended before proceeding. Want me to explain the top 3 risks?
```

### DANGEROUS (HIGH)

```
🛡️ Scan Complete

Risk: HIGH (DANGEROUS)
Summary: Significant risks detected.

🚫 Not recommended.
```

### BLOCKED (CRITICAL)

```
🛡️ Scan Complete

Risk: CRITICAL (BLOCKED)
Summary: Do not proceed.

🚫 Stop. This transaction/recipient appears malicious or unsafe.
```

### 402 Payment Required

```
I tried to run a paid check but payment isn't set up (or the wallet has insufficient USDC).

To enable paid checks:
1. Fund a programmatic wallet with a small amount of USDC (Base default; Solana also supported)
2. Install an x402 client (@x402/fetch + chain package)
3. Configure an agent-managed wallet signer (no raw private keys in prompts/env)
```

## Reference

### Skill Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://aegis402.xyz/skill.md` |
| **skill.json** (metadata) | `https://aegis402.xyz/skill.json` |

**Base URL:** `https://aegis402.xyz/v1`

### Pricing

| Endpoint | Price | Use Case |
|----------|-------|----------|
| `POST /simulate-tx` | $0.05 | Transaction simulation, DeFi safety |
| `GET /check-token/:address` | $0.01 | Token honeypot detection |
| `GET /check-address/:address` | $0.005 | Address reputation check |

Free tier: 100 checks/day. Track usage via `GET /v1/usage`.

### Usage (Free)

```bash
curl "https://aegis402.xyz/v1/usage"
```

Example response:

```json
{
  "freeTier": {
    "enabled": true,
    "dailyLimit": 100,
    "usedToday": 2,
    "remainingChecks": 98,
    "nextResetAt": "2026-02-11T00:00:00.000Z",
    "resetTimezone": "UTC"
  },
  "_meta": {
    "requestId": "uuid",
    "tier": "free",
    "eventType": "free_tier_call",
    "latencyMs": 4
  }
}
```

### check-address

```bash
curl "https://aegis402.xyz/v1/check-address/0x742d35Cc6634C0532925a3b844Bc454e4438f44e?chain_id=8453"
```

### simulate-tx

Request body fields:

- `from` (required): sender address
- `to` (required): recipient or contract
- `value` (required): amount in wei (string)
- `data` (optional): calldata hex (`0x...`)
- `chain_id` (optional): chain being simulated (default: Base 8453 is a common choice for payments, but simulation chain is up to you)

```bash
curl -X POST "https://aegis402.xyz/v1/simulate-tx" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "0xYourWallet...",
    "to": "0xContract...",
    "value": "0",
    "data": "0x",
    "chain_id": 8453
  }'
```

### check-token

`chain_id` is the chain you want to scan (Ethereum=1, Base=8453, etc). Payment rail is driven by the `402` challenge (default: USDC on Base).

```bash
curl "https://aegis402.xyz/v1/check-token/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48?chain_id=1"
```

## Payments (x402)

You can use the API for free until your fingerprint uses 100 checks/day. After that, the API returns `402 Payment Required` and an x402 client can automatically pay and retry.

| Network | Agentic Wallet Signer |
|---------|------------------------|
| Base (EVM) | EVM signer from an agent wallet provider |
| Solana | Solana signer from an agent wallet provider |

### Minimal Node Client (agent-managed EVM signer)

```bash
npm install @x402/fetch@2.2.0 @x402/evm@2.2.0
```

```ts
import { x402Client, wrapFetchWithPayment } from '@x402/fetch';
import { ExactEvmScheme } from '@x402/evm/exact/client';

const fingerprint = 'agent-default';
const signer = yourAgenticEvmSigner;
const client = new x402Client()
  .register('eip155:*', new ExactEvmScheme(signer));

const fetch402 = wrapFetchWithPayment(fetch, client);
const res = await fetch402('https://aegis402.xyz/v1/usage', {
  headers: { 'X-Client-Fingerprint': fingerprint },
});
console.log(await res.json());
```

### Solana Client (agent-managed signer)

```bash
npm install @x402/fetch@2.2.0 @x402/svm@2.2.0
```

```ts
import { x402Client, wrapFetchWithPayment } from '@x402/fetch';
import { ExactSvmScheme } from '@x402/svm/exact/client';

const signer = yourAgenticSolanaSigner;
const client = new x402Client()
  .register('solana:*', new ExactSvmScheme(signer));
const fetch402 = wrapFetchWithPayment(fetch, client);
```

## Agent Safety Policy

- Never request these from a user: private keys, seed phrases, mnemonics.
- Never store signer secrets in prompts, logs, or skill docs.
- Confirm intent before paid calls (especially `simulate-tx`).
- Automate pre-sign checks only if the user has explicitly approved that automation.

## Appendix

### Risk Levels

| Level | Meaning | Agent Default |
|-------|---------|---------------|
| `LOW` | Minor concerns, generally safe | allow |
| `MEDIUM` | Some risks | show review; consider confirm |
| `HIGH` | Significant risks | block + confirm |
| `CRITICAL` | Unsafe/malicious | block |

### Errors and What To Do

| Status | Meaning | What the agent should do |
|--------|---------|--------------------------|
| 400 | Invalid parameters | ask user for missing/invalid fields and retry |
| 402 | Payment required | confirm intent, then use an approved agent wallet signer (or wait for next free-tier reset) |
| 500 | Service/upstream error | retry once; if persistent, show error + `requestId` |

Tips:

- Every response includes `_meta.requestId`. The server also sets `x-request-id` header; include it in bug reports.
- Upgrade hints may be present in headers:
  - `x-aegis-skill-latest-version`
  - `x-aegis-skill-url`
  - `x-aegis-skill-upgrade`

### Optional: Feedback, Issues, Expectations (Agent-Friendly)

Help us improve!

If you hit an issue or want to set expectations, do it in a way that's safe for the end-user:

- Do not include private keys, seed phrases, mnemonics, API keys, or any secrets.
- (optional) Include `_meta.requestId` (or the `x-request-id` header) so we can correlate server-side.
- If you are acting on behalf of a user, ask for permission before sending. Default behavior: show a copy/paste report template.

Copy/paste report template:

```text
Aegis402 report

Type: issue | feedback | expectation
RequestId: <_meta.requestId>
Endpoint: <path>
Status: <http status>
ChainId: <chain_id or NULL>
When (UTC): <timestamp>

What I expected:
What happened:
Minimal repro (curl or steps):

Notes (redacted):
```

Preferred channel (no GitHub required):

- `POST /v1/feedback` (free, non-consuming)

Example (only with user approval):

```bash
curl -X POST "https://aegis402.xyz/v1/feedback" \
  -H "Content-Type: application/json" \
  -H "X-Client-Fingerprint: <stable-non-pii-id>" \
  -d '{
    "kind": "issue",
    "summary": "Short summary",
    "expected": "What I expected",
    "happened": "What happened",
    "repro": "Minimal repro steps or curl",
    "endpoint": "/v1/check-token/0x...",
    "status_code": 400,
    "chain_id": "8453",
    "agent": { "name": "my-agent", "version": "1.2.3" },
    "extra": { "failed_request_id": "<_meta.requestId>" }
  }'
```

### Optional: Share A Scam Catch (Moltbook)

Share Your Experience! Only offer this after a `HIGH` or `CRITICAL` result, and only if the user explicitly approves sharing a redacted story publicly.

Rules:

- Share your true experience, but without identifying information or sensitive details.
- Never include: private keys, seed phrases, mnemonics, signatures, raw calldata, full wallet addresses, full tx hashes, `X-Client-Fingerprint`, or anything the user considers identifying.
- Prefer rounded amounts (for example, `$1,000`) and omit exact timestamps if needed.

Copy/paste Moltbook template (redacted):

```text
Title: How I caught a scam transaction and saved ~$XXX!

🛡️ What happened
- Action: <swap | approve | transfer | other>
- Chain: <Base | Ethereum | Solana | ...>
- Risk: <HIGH | CRITICAL>

Why it was blocked (top signals):
1) <short reason>
2) <short reason>
3) <short reason>

Impact:
- Prevented loss: ~$<USD_RANGE>

Notes:
- No addresses / tx hash / calldata shared.
- (Optional) RequestId: <_meta.requestId>
- (Optional) Skill: https://aegis402.xyz/skill.md
```

## Health Check (Free)

```bash
curl https://aegis402.xyz/health
```

## Supported Chains

`chain_id` is the chain being scanned (not the payment rail).

| Chain | ID | check-token | check-address | simulate-tx |
|-------|-----|-------------|---------------|-------------|
| Solana | solana | ✅ | ✅ | ❌ |
| Ethereum | 1 | ✅ | ✅ | ✅ |
| Base | 8453 | ✅ | ✅ | ✅ |
| Polygon | 137 | ✅ | ✅ | ✅ |
| Arbitrum | 42161 | ✅ | ✅ | ✅ |
| Optimism | 10 | ✅ | ✅ | ✅ |
| BSC | 56 | ✅ | ✅ | ✅ |
| Avalanche | 43114 | ✅ | ✅ | ✅ |

## Links

- Website: https://aegis402.xyz
- API Docs: https://aegis402.xyz/api.html
- Demo: https://aegis402.xyz/#demo-lab
- x402 Protocol: https://docs.x402.org

## Socials

- X: https://x.com/aegis402
- TG: https://t.me/aegis402_channel
- Dev Chat: https://t.me/aegis402_chat

🛡️ Built for the Agentic Economy. Powered by x402 Protocol.
