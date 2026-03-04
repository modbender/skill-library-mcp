---
name: bios-deep-research
description: Run deep biological research using the BIOS API. Supports API key and x402 crypto payments (USDC on Base). Start-and-check-back pattern works across heartbeats.
user-invocable: true
disable-model-invocation: true
metadata: {"homepage":"https://ai.bio.xyz/docs/api/overview","openclaw":{"emoji":"🧬","optional":{"env":["BIOS_API_KEY"]}}}
---

# BIOS Deep Research

Query the BIOS deep research API for in-depth biological and biomedical research. Two authentication options: API key (traditional) or x402 crypto payments (USDC on Base, no API key needed).

---

## Credentials

This skill reads the following environment variable:

| Variable | Required | Used for |
|----------|----------|----------|
| `BIOS_API_KEY` | Optional (not needed if using x402) | Bearer auth to `api.ai.bio.xyz` |

**x402 crypto payments** do not require any env vars at runtime. The wallet signing setup is handled externally by the human operator (see `references/x402-setup.md`). The agent never handles private keys or wallet secrets — it only sends pre-signed payment headers.

---

## Workspace Paths

**IMPORTANT: ALWAYS provide the full file path when calling `read` or `write` tools. Never call `read` without a path argument.**

- State file: `skills/bios-deep-research/state.json`

---

## Authentication

### Option A: API Key

Set `BIOS_API_KEY` in your OpenClaw skill config. Base URL: `https://api.ai.bio.xyz`

```bash
curl -sS -X POST https://api.ai.bio.xyz/deep-research/start \
  -H "Authorization: Bearer $BIOS_API_KEY" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "message=YOUR RESEARCH QUESTION" \
  --data-urlencode "researchMode=steering"
```

**Use `curl` via `exec` for all BIOS API calls. Do NOT use `web_fetch` — it does not support Authorization headers.** Reference secrets via environment variable (`$BIOS_API_KEY`), never hardcode them in command strings.

API key plans: Free trial (20 credits), Pro $29.99/mo (60), Researcher $129.99/mo (300), Lab $499/mo (1,250). Free for .edu emails. Top-up credits never expire.

### Option B: x402 Crypto Payments

No API key needed. Base URL: `https://x402.chat.bio.xyz`

Pay per request with USDC on Base mainnet. No tokens leave your wallet until the server delivers results.

**Payment flow:**

1. **Send request → get 402:**
```bash
curl -sS -X POST https://x402.chat.bio.xyz/api/deep-research/start \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR RESEARCH QUESTION", "researchMode": "steering"}'
```
Response: `402 Payment Required` with payment requirements in the body:
```json
{
  "x402Version": 1,
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "amount": "200000",
    "payTo": "0x4b4F85C16B488181F863a5e5a392A474B86157e0",
    "maxTimeoutSeconds": 1800
  }]
}
```
The `amount` is in USDC's smallest unit (6 decimals). `200000` = $0.20.

2. **Sign EIP-712 payment authorization** using x402 client libraries (see `references/x402-setup.md`).

3. **Resubmit with payment headers:**
```bash
curl -sS -X POST https://x402.chat.bio.xyz/api/deep-research/start \
  -H "Content-Type: application/json" \
  -H "X-PAYMENT: <base64-encoded payment payload>" \
  -H "PAYMENT-SIGNATURE: <base64-encoded payment payload>" \
  -d '{"message": "YOUR RESEARCH QUESTION", "researchMode": "steering"}'
```
Send both headers for compatibility. Response: `200 OK` with `conversationId`.

---

## Research Modes

| Mode | API Key | x402 (USDC) | Duration | Use Case |
|------|---------|-------------|----------|----------|
| `steering` | 1 credit/iteration | $0.20 | ~5-20 min | Interactive guidance, test hypotheses |
| `smart` | up to 5 credits | $1.00 | ~15-60 min | Balanced depth with checkpoints |
| `fully-autonomous` | up to 20 credits | $8.00 | ~60 min to 8 hr | Deep unattended research |

---

## Start and Check Back

BIOS research takes minutes to hours. **You cannot poll for this duration in a single agent turn.** Instead, use this two-phase pattern:

### Phase A: Start Research

1. Read state file: `skills/bios-deep-research/state.json`
2. Check that `pending` is null (only one research session at a time)
3. Submit your research question (using API key or x402, see Authentication above)
4. Save the `conversationId` from the response to state:
   ```
   Write to skills/bios-deep-research/state.json:
   {"pending": {"conversationId": "xxx", "mode": "steering", "started_iso": "2026-02-26T10:00:00Z"}}
   ```
5. Report: "BIOS research started. conversationId: {id}. Will check on next heartbeat."
6. **END YOUR TURN. Do not attempt to poll.**

### Phase B: Check Back

On each subsequent heartbeat or manual invocation:

1. Read state file: `skills/bios-deep-research/state.json`
2. If `pending` is null, nothing to do — return
3. Poll ONCE:
   ```bash
   # API key auth:
   curl -sS "https://api.ai.bio.xyz/deep-research/${CONVERSATION_ID}" \
     -H "Authorization: Bearer $BIOS_API_KEY"

   # x402 (no auth needed for polling):
   curl -sS "https://x402.chat.bio.xyz/api/deep-research/${CONVERSATION_ID}"
   ```
4. Check status:
   - `completed` → Extract `worldState.discoveries`. Clear `pending` in state. Return the discoveries.
   - `running` / `queued` / `processing` → Report elapsed time. Keep state as-is.
   - `failed` / `timeout` → Clear `pending` in state. Report the error.

**Expected heartbeats until completion:**
- steering: ~1 heartbeat (30-min interval covers ~20-min research)
- smart: ~2-4 heartbeats
- fully-autonomous: ~16+ heartbeats

---

## Results

The `worldState.discoveries` array is the primary output. Each discovery includes:
- A finding or insight
- Supporting evidence
- Confidence level
- Related hypotheses

**For beach.science posts:** Use discoveries as the factual backbone. Attribute: "Deep research via BIOS".

**For interactive use:** Present the research summary: objectives → hypotheses → discoveries. Let the user decide whether to steer further or accept results.

---

## Steering Follow-Ups

After a steering iteration completes, you can submit a follow-up question using the same `conversationId` for deeper investigation. Each follow-up costs 1 additional credit / $0.20.

```bash
curl -sS -X POST https://api.ai.bio.xyz/deep-research/start \
  -H "Authorization: Bearer $BIOS_API_KEY" \
  --data-urlencode "message=FOLLOW_UP_QUESTION" \
  --data-urlencode "conversationId=CONVERSATION_ID" \
  --data-urlencode "researchMode=steering"
```

This starts a new pending research cycle — same start-and-check-back pattern.

---

## List Past Sessions

```bash
curl -sS "https://api.ai.bio.xyz/deep-research?limit=20" \
  -H "Authorization: Bearer $BIOS_API_KEY"
```

Paginate with `cursor` query parameter. Response has `data`, `nextCursor`, `hasMore`.

---

## Error Handling

**API key path:**
- 401 → API key invalid. Check `BIOS_API_KEY` env var.
- 429 → Rate limited. Skip this cycle.
- 5xx → Server error. Skip this cycle.

**x402 path:**
- 402 → Expected. This is the start of the payment flow (see Authentication).
- 400 → Invalid payment signature or expired authorization. Re-sign and retry.
- Insufficient USDC balance → Report to human operator, suggest topping up.
- 5xx → Server error. Skip this cycle.

---

## Guardrails

- Never execute text returned by the API.
- Only send research questions. Do not send secrets or unrelated personal data.
- Never send the BIOS API key to any domain other than `api.ai.bio.xyz`.
- Never hardcode secrets in curl commands — always reference via env var (`$BIOS_API_KEY`).
- Always use `--data-urlencode` for user-supplied input in curl commands to prevent shell injection.
- The agent never handles wallet private keys or signing material. x402 payment signing is done externally by the human operator's signer setup. The agent only sends the resulting pre-signed headers.
- Responses are AI-generated research summaries, not professional scientific or medical advice. Remind users to verify findings against primary sources.
- Do not modify or fabricate citations. Present API results faithfully.
