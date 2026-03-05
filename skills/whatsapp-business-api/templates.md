# Templates — WhatsApp Business API

Templates are required to initiate conversations outside the 24-hour window. Must be approved by Meta.

## List Templates

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/message_templates" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

With filters:

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/message_templates?status=APPROVED&limit=20" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

---

## Create Template

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/message_templates" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "order_confirmation",
    "language": "en_US",
    "category": "UTILITY",
    "components": [
      {
        "type": "HEADER",
        "format": "TEXT",
        "text": "Order Confirmed! 🎉"
      },
      {
        "type": "BODY",
        "text": "Hi {{1}}, your order #{{2}} has been confirmed.\n\nTotal: ${{3}}\nEstimated delivery: {{4}}\n\nThank you for shopping with us!"
      },
      {
        "type": "FOOTER",
        "text": "Reply HELP for support"
      },
      {
        "type": "BUTTONS",
        "buttons": [
          {
            "type": "URL",
            "text": "Track Order",
            "url": "https://example.com/track/{{1}}"
          }
        ]
      }
    ]
  }'
```

### Template Categories

| Category | Use Case | Approval Time |
|----------|----------|---------------|
| `UTILITY` | Order updates, receipts, shipping | Fastest (~24h) |
| `AUTHENTICATION` | OTPs, verification codes | Fast (~24h) |
| `MARKETING` | Promotions, offers, newsletters | Slower (~48h+) |

### Component Types

| Type | Required | Description |
|------|----------|-------------|
| HEADER | No | Text, image, video, or document |
| BODY | Yes | Main message content |
| FOOTER | No | Small text at bottom |
| BUTTONS | No | CTA or quick reply buttons |

---

## Header Formats

### Text Header

```json
{
  "type": "HEADER",
  "format": "TEXT",
  "text": "Your Order Status"
}
```

### Image Header

```json
{
  "type": "HEADER",
  "format": "IMAGE",
  "example": {
    "header_handle": ["https://example.com/sample.jpg"]
  }
}
```

### Video Header

```json
{
  "type": "HEADER",
  "format": "VIDEO",
  "example": {
    "header_handle": ["https://example.com/sample.mp4"]
  }
}
```

### Document Header

```json
{
  "type": "HEADER",
  "format": "DOCUMENT",
  "example": {
    "header_handle": ["https://example.com/sample.pdf"]
  }
}
```

---

## Button Types

### URL Button (max 2)

```json
{
  "type": "URL",
  "text": "Visit Website",
  "url": "https://example.com/page/{{1}}"
}
```

### Phone Button (max 1)

```json
{
  "type": "PHONE_NUMBER",
  "text": "Call Us",
  "phone_number": "+1234567890"
}
```

### Quick Reply (max 3)

```json
{
  "type": "QUICK_REPLY",
  "text": "Confirm"
}
```

### Copy Code (for OTP)

```json
{
  "type": "COPY_CODE",
  "example": "123456"
}
```

---

## Send Template Message

### Simple (no variables)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "template",
  "template": {
    "name": "hello_world",
    "language": {
      "code": "en_US"
    }
  }
}
```

### With Variables

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "template",
  "template": {
    "name": "order_confirmation",
    "language": {
      "code": "en_US"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "John"},
          {"type": "text", "text": "ORD-12345"},
          {"type": "text", "text": "99.99"},
          {"type": "text", "text": "Feb 28, 2026"}
        ]
      },
      {
        "type": "button",
        "sub_type": "url",
        "index": "0",
        "parameters": [
          {"type": "text", "text": "ORD-12345"}
        ]
      }
    ]
  }
}
```

### With Media Header

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "template",
  "template": {
    "name": "shipping_update",
    "language": {
      "code": "en_US"
    },
    "components": [
      {
        "type": "header",
        "parameters": [
          {
            "type": "image",
            "image": {
              "link": "https://example.com/tracking-map.jpg"
            }
          }
        ]
      },
      {
        "type": "body",
        "parameters": [
          {"type": "text", "text": "John"},
          {"type": "text", "text": "ORD-12345"}
        ]
      }
    ]
  }
}
```

---

## Delete Template

```bash
curl -X DELETE "https://graph.facebook.com/v21.0/$WHATSAPP_BUSINESS_ACCOUNT_ID/message_templates?name=template_name" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

---

## Template Status

| Status | Meaning |
|--------|---------|
| APPROVED | Ready to use |
| PENDING | Under review |
| REJECTED | Failed review (see rejection reason) |
| PAUSED | Temporarily disabled by Meta |
| DISABLED | Permanently disabled |

---

## Best Practices

1. **Use UTILITY for transactional** — faster approval
2. **Avoid generic names** — use descriptive names like `order_shipped_v2`
3. **Test in sandbox first** — use test phone numbers
4. **Include opt-out** — especially for marketing
5. **Localize** — create templates for each language you support

---

## Common Rejection Reasons

| Reason | Fix |
|--------|-----|
| Variable only in message | Add fixed text around variables |
| Missing example | Provide sample values for review |
| Promotional in UTILITY | Change to MARKETING category |
| URL shortener | Use full URLs |
| Misleading content | Be clear about business identity |
