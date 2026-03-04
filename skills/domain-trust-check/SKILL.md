---
name: domain-trust-check
description: "URL safety scanner and domain reputation checker. Use when: checking if a URL is safe before visiting, scanning links in emails/messages, verifying domains for phishing/malware/scam. NOT for: submitting malicious domains for bounty rewards (use outtake-bounty-network)."
metadata: { "openclaw": { "emoji": "🛡️", "requires": { "env": ["OUTTAKE_API_KEY"], "bins": ["curl"] }, "primaryEnv": "OUTTAKE_API_KEY", "homepage": "https://outtake.ai" } }
---

# Domain Trust Check

Check any URL for phishing, malware, brand abuse, and scams before visiting or recommending it. Powered by the [Outtake](https://outtake.ai) Trust API.

## Quick Start

> **Already registered?** If `OUTTAKE_API_KEY` is set, skip to the curl command. Do not re-register.

```bash
curl -s -X POST https://app.outtake.ai/api/v1/trust/check \
  -H "Authorization: Bearer $OUTTAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://suspicious-site.com"}'
# → {"data": {"url": "...", "verdict": "malicious", "confidence": 0.92, "safe_to_visit": "unsafe", "recommended_action": "block", ...}}
```

## Registration

One-time setup. The same key works across all Outtake skills.

```bash
curl -s -X POST https://app.outtake.ai/api/v1/agent/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "email": "agent@example.com"}'
```

Save the returned `api_key` — it is only shown once:

```bash
export OUTTAKE_API_KEY="outtake_..."
```

| Status | Meaning |
|---|---|
| 409 | Email already registered — use your existing key |
| 429 | Rate limited (5 registrations/hour) |

Optional fields: `wallet_address` (Ethereum, needed for bounty payouts), `agent_framework` (e.g. "langchain").

## Interpreting Results

| verdict | safe_to_visit | Action |
|---|---|---|
| `malicious` | `unsafe` | **Block.** Do NOT visit. Warn the user. |
| `suspicious` | `safe` or `unsafe` | **Warn** the user. If `unsafe`, treat as malicious. |
| `safe` | `safe` | Safe to visit. |
| `unknown` | `unknown` | No data. Proceed with caution. |

**Confidence:** `1.0` = human-reviewed, `0.7–0.99` = ML classification, `0.0` = no data.

## Batch Checking

Check up to 50 URLs in one request using `POST /trust/check-batch`:

```bash
curl -s -X POST https://app.outtake.ai/api/v1/trust/check-batch \
  -H "Authorization: Bearer $OUTTAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://link1.com", "https://link2.com"]}'
```

Use batch when checking 3+ URLs to reduce round trips. Requests with more than 50 URLs return `400`.

## Related Skills

- **[outtake-bounty-network](https://clawhub.ai/skill/outtake-bounty-network)** — Earn $5 USDC per verified malicious domain. Scan with trust-check, then submit confirmed threats. Same API key.
