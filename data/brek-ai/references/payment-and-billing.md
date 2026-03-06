# Payment and Billing

Handle two different payment problems:
- End-user card input for booking.
- B2B settlement for agent-to-agent usage.

## A) End-user card input (booking flow)

Use this state machine:
1. Receive `status=payment_setup_required` with `artifacts.payment.setupUrl`.
2. Return setup URL to human user and ask them to complete setup in Brek portal.
3. Human completes card setup in portal (provider-hosted fields only).
4. User returns and confirms completion (for example, "done").
5. Refresh session state and verify payment method is available.
6. Ask explicit final confirmation.
7. Send `action_confirm_payment_card` with `idempotencyKey`.

Never collect raw PAN/CVV in agent chat.
Agent must not attempt to perform card setup on behalf of user.

## Payment setup prompt template

Use this short prompt when setup is required:

```text
Payment setup is required before booking.
Please open this secure Brek portal link and complete card setup: <setupUrl>
After you finish, reply "done" and I will continue.
```

## B) Agent-to-agent billing (usage settlement)

Implement metering per API call.

## Usage event schema

Store one immutable event per call:

```json
{
  "eventId": "uuid",
  "timestamp": "2026-02-23T10:20:30Z",
  "partnerId": "acme",
  "actorId": "partner_user_001",
  "sessionId": "sess_xxx",
  "endpoint": "POST /events",
  "requestId": "x-request-id from Brek",
  "statusCode": 200,
  "tokensIn": 0,
  "tokensOut": 0,
  "providerCostUsd": 0.0000,
  "markupMultiplier": 1.00,
  "billableAmountUsd": 0.0000
}
```

Use `requestId` + endpoint as dedupe key for retries.

## Settlement models

Choose one model first, keep it simple:
1. Prepaid wallet: partner prepays credits; reject calls when balance is below threshold.
2. Postpaid monthly invoice: aggregate usage events daily; invoice monthly.
3. Hybrid: prepaid for high-risk tenants, postpaid for approved partners.

## Booking-transaction fee (optional)

If your business is booking-led, add a second meter:
- Fixed fee per successful booking.
- Or percentage of booking value.

Record only after final confirmed booking event.

## Reconciliation

Run daily reconciliation job:
1. Group by `partnerId` and UTC date.
2. Sum `billableAmountUsd`.
3. Compare with gateway logs by `x-request-id`.
4. Flag drift above 0.5% for manual review.

## Abuse-resistant billing rules

- Do not charge duplicate idempotent writes.
- Do not charge requests that fail auth (`401/403`).
- Optionally charge for valid but bad input (`400`) only if abuse controls detect intentional spam.
