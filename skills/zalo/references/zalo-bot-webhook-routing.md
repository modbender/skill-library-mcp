# Webhook and Polling Routing

## 1) Webhook handling
- Verify incoming requests using the configured webhook secret.
- When `webhookSecret` is set, validate the `X-Bot-Api-Secret-Token` header.
- Respond quickly; process asynchronously.
- De-duplicate events by message ID or event ID.

## 2) Polling handling
- Store and advance the cursor/offset.
- Make handlers idempotent to survive retries.

## 3) Routing rules
- If a postback/callback exists, handle it before plain text.
- Route by intent or command first; fallback last.
