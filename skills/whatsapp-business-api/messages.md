# Messages — WhatsApp Business API

## Base Endpoint

```
POST https://graph.facebook.com/v21.0/{phone_number_id}/messages
Authorization: Bearer {access_token}
Content-Type: application/json
```

All message requests require `"messaging_product": "whatsapp"`.

---

## Text Messages

### Simple Text

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "text",
  "text": {
    "body": "Hello! How can I help you today?"
  }
}
```

### Text with Link Preview

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "text",
  "text": {
    "preview_url": true,
    "body": "Check out our website: https://example.com"
  }
}
```

---

## Media Messages

### Image

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "image",
  "image": {
    "link": "https://example.com/image.jpg",
    "caption": "Product photo"
  }
}
```

Using uploaded media ID:

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "image",
  "image": {
    "id": "media_id_here",
    "caption": "Product photo"
  }
}
```

### Video

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "video",
  "video": {
    "link": "https://example.com/video.mp4",
    "caption": "Product demo"
  }
}
```

### Audio

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "audio",
  "audio": {
    "link": "https://example.com/audio.mp3"
  }
}
```

### Document

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "document",
  "document": {
    "link": "https://example.com/invoice.pdf",
    "filename": "invoice_001.pdf",
    "caption": "Your invoice"
  }
}
```

### Sticker

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "sticker",
  "sticker": {
    "id": "sticker_media_id"
  }
}
```

---

## Location Messages

### Send Location

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "location",
  "location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "name": "Our Store",
    "address": "123 Main St, San Francisco, CA"
  }
}
```

### Request Location

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "location_request_message",
    "body": {
      "text": "Please share your delivery location"
    },
    "action": {
      "name": "send_location"
    }
  }
}
```

---

## Contact Messages

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "contacts",
  "contacts": [
    {
      "name": {
        "formatted_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "phones": [
        {
          "phone": "+1987654321",
          "type": "WORK"
        }
      ],
      "emails": [
        {
          "email": "john@example.com",
          "type": "WORK"
        }
      ]
    }
  ]
}
```

---

## Interactive Messages

### Reply Buttons (max 3)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "header": {
      "type": "text",
      "text": "Confirm Order"
    },
    "body": {
      "text": "Your order #12345 is ready. Would you like to proceed?"
    },
    "footer": {
      "text": "Reply within 24 hours"
    },
    "action": {
      "buttons": [
        {"type": "reply", "reply": {"id": "confirm", "title": "✅ Confirm"}},
        {"type": "reply", "reply": {"id": "cancel", "title": "❌ Cancel"}},
        {"type": "reply", "reply": {"id": "modify", "title": "✏️ Modify"}}
      ]
    }
  }
}
```

### List Message (max 10 items per section, max 10 sections)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "header": {
      "type": "text",
      "text": "Our Menu"
    },
    "body": {
      "text": "Select an item from our menu:"
    },
    "footer": {
      "text": "Prices may vary"
    },
    "action": {
      "button": "View Menu",
      "sections": [
        {
          "title": "Main Courses",
          "rows": [
            {"id": "pizza", "title": "🍕 Pizza", "description": "$12.99"},
            {"id": "burger", "title": "🍔 Burger", "description": "$9.99"},
            {"id": "pasta", "title": "🍝 Pasta", "description": "$11.99"}
          ]
        },
        {
          "title": "Drinks",
          "rows": [
            {"id": "soda", "title": "🥤 Soda", "description": "$2.99"},
            {"id": "juice", "title": "🧃 Juice", "description": "$3.99"}
          ]
        }
      ]
    }
  }
}
```

### CTA URL Button

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "cta_url",
    "header": {
      "type": "text",
      "text": "Track Your Order"
    },
    "body": {
      "text": "Click below to track your order in real-time."
    },
    "action": {
      "name": "cta_url",
      "parameters": {
        "display_text": "Track Order",
        "url": "https://example.com/track/12345"
      }
    }
  }
}
```

---

## Reactions

### Add Reaction

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.xxxxx",
    "emoji": "👍"
  }
}
```

### Remove Reaction

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.xxxxx",
    "emoji": ""
  }
}
```

---

## Reply to Specific Message

Add `context` to any message type:

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "context": {
    "message_id": "wamid.xxxxx"
  },
  "type": "text",
  "text": {
    "body": "This is a reply to your previous message"
  }
}
```

---

## Mark as Read

```json
{
  "messaging_product": "whatsapp",
  "status": "read",
  "message_id": "wamid.xxxxx"
}
```

---

## Response Format

Successful send returns:

```json
{
  "messaging_product": "whatsapp",
  "contacts": [
    {"input": "1234567890", "wa_id": "1234567890"}
  ],
  "messages": [
    {"id": "wamid.HBgLMTIzNDU2Nzg5MBUCABIYFjNFQjBDNUM3..."}
  ]
}
```

---

## Common Errors

| Code | Error | Solution |
|------|-------|----------|
| 131030 | Recipient not on WhatsApp | Verify phone number |
| 131047 | Re-engagement required | Send template message first |
| 131051 | Unsupported message type | Check type field |
| 130429 | Rate limit exceeded | Slow down requests |
| 132000 | Template not found | Verify template name and status |
