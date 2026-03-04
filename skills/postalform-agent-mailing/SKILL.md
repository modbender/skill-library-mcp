---
name: postalform-machine-order
description: "Send real postal mail through PostalForm using machine payments: prepare/validate print-and-mail payloads, submit `POST /api/machine/orders`, settle x402 payment with any compatible wallet client (purl or custom), and poll fulfillment through completion. Use when an agent must autonomously mail a real physical letter/document with strong first-pass correctness and idempotent retry behavior."
---

# PostalForm Machine Order

Use this workflow when an agent needs to send real postal mail (a physical print-and-mail order) reliably on the first attempt.

## Workflow

### 1. Collect inputs and choose address strategy

Require these inputs:
- `buyer_name`, `buyer_email`
- `sender_name`, `recipient_name`
- PDF source (`upload_token`, `{ download_url, file_id }`, data URL, or allowed `https` URL)
- Mailing options (`double_sided`, `color`, `mail_class`, `certified`)

For each party (`sender`, `recipient`), choose exactly one strategy:
- Manual address: `*_address_type: "Manual"` + `*_address_manual`
- Loqate address: `*_address_type: "Address"` + `*_address_id` + `*_address_text`

Do not mix manual + Loqate for the same party.

### 2. Build payload with strict idempotency

Generate a UUID `request_id` once and keep payload bytes stable across retries.

Set `buyer_email` every time (required for Stripe receipt routing).

For manual addresses:
- Include `line1`, `city`, `state`, `zip`
- Include `line2` only when it has a non-empty string value
- Omit optional fields instead of sending `null`

Use the tested template in `references/payload_templates.md`.

### 3. Preflight with validate endpoint (recommended)

Call:
- `POST https://postalform.com/api/machine/orders/validate`

If response is `200`, confirm:
- `quote.page_count` matches expected page count
- `quote.price_usd` and options are acceptable

If response is `422`, fix payload before paying.

### 4. Create order and settle x402 payment

Endpoint:
- `POST https://postalform.com/api/machine/orders`

Flow:
1. Send order payload without payment header.
2. Receive `402` with `PAYMENT-REQUIRED`.
3. Create payment using your wallet stack on the requested network.
4. Retry the exact same request body with `PAYMENT-SIGNATURE`.
5. Expect `202` and settlement metadata.

Payment client options:
- `purl` CLI (fastest path when available)
- Any x402-compliant client (`@x402/core`, `@x402/evm`, or equivalent custom signer flow)

If using `purl`:
- Prefer wallet alias/keystore over raw private keys
- Use `--password` from secure runtime input
- Set a protective `--max-amount`
- Match `--network` to `PAYMENT-REQUIRED` network

### 5. Poll order status until post-payment completion

Call:
- `GET https://postalform.com/api/machine/orders/:request_id`

Treat this as complete when:
- `is_paid = true`
- `current_step` has advanced through processing (commonly to `email_sent`)
- `order_complete_url` is a real URL

Handle transitional state:
- `status: "settled_pending_webhook"` can persist briefly after on-chain settlement
- Continue polling with backoff; do not resubmit a changed payload under the same `request_id`

## First-Pass Reliability Rules

### Required invariants
- Keep `request_id` constant for retries of the same logical order.
- Keep payload unchanged when retrying after `402`.
- Send `buyer_email` always.
- Match payment network to `PAYMENT-REQUIRED`; do not hardcode network.
- Use only valid US addresses and one address strategy per party.
- Verify page count and quoted price before payment.

### Observed failure modes and prevention
- `422 invalid_type` on manual `line2`:
  - Cause: empty optional fields normalized as `null`.
  - Prevent: omit `line2` unless non-empty string.
- Delay after successful payment (`settled_pending_webhook`):
  - Cause: settlement acknowledged before webhook reconciliation completes.
  - Prevent: poll for up to several minutes with retry/backoff.
- Occasional non-JSON/transient server response during polling:
  - Cause: temporary upstream/render errors.
  - Prevent: parse defensively; if response is non-JSON or `5xx`, retry without changing `request_id` or payload.
- `409 request_id_mismatch`:
  - Cause: same `request_id` reused with modified payload.
  - Prevent: generate a new UUID for changed orders; reuse ID only for exact retries.

## Security Rules

- Avoid printing wallet passwords, private keys, or sensitive env vars in logs.
- Prefer encrypted keystore wallets over raw private keys when tooling supports both.
- Use a payment cap (`max amount`) to avoid accidental overpayment.

## Operator Output

Return these values after execution:
- `request_id` / `order_id`
- price/quote summary (including `page_count`)
- payment settlement details (`network`, `pay_to`, `settlement_tx`, `settled_at`)
- latest status (`is_paid`, `current_step`)
- `order_complete_url` when available

Reference examples and command snippets:
- `references/payload_templates.md`
