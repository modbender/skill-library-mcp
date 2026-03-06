# Messaging (SMS/MMS)

## 1) Send a message
- Endpoint: `POST /2010-04-01/Accounts/{AccountSid}/Messages.json`
- Required fields:
  - `To`
  - `From` or `MessagingServiceSid`
- Content fields:
  - `Body` (text)
  - `MediaUrl` (for MMS)
  - `ContentSid` (template/content API)

## 2) Receive callbacks
- Status callbacks are sent to your webhook URL.
- Inbound messages can be delivered to your webhook URL.

## 3) Safety
- Enforce opt-in and regional compliance.
- Throttle outbound sends if you receive 429s.
