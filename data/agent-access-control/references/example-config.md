# Example Configuration

## memory/access-control.json

```json
{
  "ownerIds": [
    "+1234567890",
    "telegram:123456789",
    "discord:987654321"
  ],
  
  "approvedContacts": {
    "+1987654321": {
      "tier": 2,
      "label": "trusted",
      "approvedAt": "2026-02-07T10:00:00Z",
      "platform": "whatsapp",
      "note": "Friend"
    },
    "telegram:555555555": {
      "tier": 1,
      "label": "chat-only",
      "approvedAt": "2026-02-07T12:00:00Z",
      "platform": "telegram",
      "note": ""
    }
  },
  
  "pendingApprovals": {},
  
  "blockedIds": [
    "+1111111111"
  ],
  
  "strangerMessage": "Hi there! 👋 I'm Alex, an AI assistant. I'm currently set up to help my owner with personal tasks, so I'm not able to chat freely just yet. I've let them know you reached out — if they'd like to connect us, they'll set that up. Have a great day! 😊",
  
  "notifyChannel": "telegram",
  "notifyTarget": "YOUR_TELEGRAM_ID_HERE",
  
  "rateLimits": {}
}
```

## Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ownerIds` | string[] | Yes | Owner identifiers across all platforms |
| `approvedContacts` | object | Yes | Map of approved sender IDs to their config |
| `pendingApprovals` | object | Yes | Strangers awaiting owner decision |
| `blockedIds` | string[] | Yes | Permanently blocked sender IDs |
| `strangerMessage` | string | Yes | Message sent to unknown contacts |
| `notifyChannel` | string | Yes | Channel to notify owner (`telegram`/`whatsapp`/`discord`/`signal`) |
| `notifyTarget` | string | Yes | Owner's ID on the notify channel |
| `rateLimits` | object | No | Per-contact rate limit tracking (auto-managed) |

## ID Format Examples

| Platform | Format | Example |
|----------|--------|---------|
| WhatsApp | Phone with country code | `+61430830888` |
| Telegram | `telegram:` + numeric ID | `telegram:123456789` |
| Discord | `discord:` + numeric ID | `discord:987654321` |
| Signal | Phone with country code | `+14155551234` |
| iMessage | Phone or email | `+14155551234` or `user@icloud.com` |

## Approved Contact Object

```json
{
  "tier": 2,
  "label": "trusted",
  "approvedAt": "2026-02-07T10:00:00Z",
  "platform": "whatsapp",
  "note": "Optional note about this contact"
}
```

- `tier`: 1 (chat-only) or 2 (trusted)
- `label`: Human-readable tier name
- `approvedAt`: ISO-8601 timestamp of approval
- `platform`: Platform they first contacted on
- `note`: Optional owner note about this contact
