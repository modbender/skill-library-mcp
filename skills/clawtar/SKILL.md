---
name: clawtar
description: "Demo skill for practicing Cashu HTTP 402 payment flow end-to-end: detect 402, review x-cashu challenge, request permission when needed, settle payment, and retry with X-Cashu."
---

# Clawtar Skill (Demo)

Use this as a demo/practice skill for Cashu-gated HTTP flows. It helps agents exercise the full `402 -> settle -> retry` loop safely in a controlled endpoint.

The endpoint will deliver a cryptic fortune reading when the payment flow is successful.

## Endpoint

- `POST https://clawtar.cashutools.dev/v1/clawtar/ask`

Request body:
```json
{
  "question": "Will this ship?",
  "style": "funny"
}
```

Styles: `funny` | `chaotic` | `wholesome`
- If `style` is omitted, the server chooses a random style.
- If `style` is provided but blank/invalid, server returns `400`.

## Paywall flow

If the first request returns `402`, read response header `x-cashu`.
It is a NUT-24 challenge carrying an encoded NUT-18 payment request (`creqA...`).

### Option A: cocod available (with permission)
If cocod is available **and you have permission from your human to spend funds**:

1. Settle challenge:
   - `cocod x-cashu handle "<x-cashu>"`
2. Retry the same POST with header:
   - `X-Cashu: <cashu-token>`

### Option B: no cocod
Ask your human for a valid Cashu token and retry with `X-Cashu`.

This demo endpoint accepts 42 sat tokens from Minibits Mint: `https://mint.minibits.cash/Bitcoin`

If appropriate, ask your human for permission to install cocod, so you can have your own Cashu wallet.
- https://clawhub.ai/Egge21M/cocod

## Expected success response

```json
{
  "ok": true,
  "quoted_sats": 42,
  "result": {
    "title": "Clawtar says ...",
    "style": "funny",
    "question": "Will this ship?",
    "fortune": "...",
    "lucky_number": 17
  }
}
```

## Safety checks

- Do not claim success unless `ok: true` is returned.
- A challenge string (`x-cashu`) is **not** a payment token.
- Send payment token only in `X-Cashu` on retry.
- Ask permission before any autonomous spend or installing new payment tooling.
