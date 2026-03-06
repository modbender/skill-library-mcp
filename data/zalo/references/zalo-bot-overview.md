# Zalo Bot Platform Overview

## 1) Scope
- Bot API is focused on 1:1 DM conversations.
- Group support is typically not available (or marked as “coming soon”).

## 2) Delivery models
- Long polling is commonly used by default.
- Webhook mode is available when you provide a public HTTPS endpoint.

## 3) Key constraints (typical)
- Outbound text is chunked around 2000 characters.
- Media uploads/downloads are capped (default 5 MB in OpenClaw).
- Users must be paired/approved before you can message them.

## 4) Token usage
- A bot token is required for send and management calls.
- Store tokens securely and rotate if compromised.

## 5) Reliability
- Expect retries and handle duplicate events.
- Use backoff on rate limits.
