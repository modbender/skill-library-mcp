# Auth and Webhook Validation

## 1) REST authentication
- Use HTTP Basic auth with API Key + Secret.
- Account SID + Auth Token is acceptable for local testing.

## 2) Webhook validation (Twilio requests)
- Validate the `X-Twilio-Signature` header.
- The signature is computed from the request URL and parameters using your Auth Token.
- For JSON webhooks, use `bodySHA256` with the body payload.
- Prefer Twilio helper libraries for validation to avoid mistakes.

## 3) Operational guidance
- Always validate webhook signatures before processing.
- Log minimal identifiers only.
