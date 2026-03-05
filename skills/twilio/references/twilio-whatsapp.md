# WhatsApp (Twilio Messaging API)

## 1) Address format
- Use the `whatsapp:` prefix with E.164 numbers.
  - Example: `whatsapp:+14155551234`

## 2) Enablement
- WhatsApp must be enabled for your Twilio sender before production use.

## 3) Sending
- Use the Messaging API endpoint (Messages resource).
- Common fields: `To`, `From`, `Body`, `MediaUrl`.
