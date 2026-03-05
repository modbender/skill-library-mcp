---
name: whatsapp-local-router
description: Route incoming WhatsApp content to local HTTP endpoints and return endpoint JSON directly to the user. Use when a WhatsApp message contains plain text/random symbols that should be sent to POST http://localhost:8080/process, or when a WhatsApp message contains a QR image that should be sent to POST http://localhost:8080/decode-qr.
---

# WhatsApp Local Router

## Overview

Handle two WhatsApp input types and mirror backend responses back to the user:
- Text input → `/process`
- QR image input → `/decode-qr`

Always send the endpoint response body back to the user with no extra formatting unless the user asks for explanation.

## Workflow

1. Confirm the message comes from WhatsApp context.
2. Choose route:
   - If inbound includes an image attachment path (QR image expected), call decode route.
   - Otherwise treat user text as arbitrary string and call process route.
3. Execute request with `scripts/route_whatsapp.sh`.
4. Return stdout from the script directly to the user.
5. If the endpoint returns an error or invalid JSON, return a short error summary and include raw response body.

## Commands

Run from workspace root:

```bash
# Text -> /process
bash skills/whatsapp-local-router/scripts/route_whatsapp.sh process "<any text>"

# Image -> /decode-qr
bash skills/whatsapp-local-router/scripts/route_whatsapp.sh decode "/path/to/image.png"
```

## Routing Rules

- Preserve text exactly; do not sanitize, trim, or reinterpret symbols.
- Use multipart field name `image` for QR decode uploads.
- Timeout requests after 20 seconds.
- If both text and image are present, prioritize image decode unless user explicitly asks to process text.
- Keep response concise: send backend JSON as-is.
