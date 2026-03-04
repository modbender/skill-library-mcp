# Conversations & Messaging API Reference

Base: `https://services.leadconnectorhq.com/conversations/`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/conversations/search?locationId={id}&limit={n}` | Search conversations |
| GET | `/conversations/{conversationId}` | Get conversation |
| POST | `/conversations/` | Create conversation |
| PUT | `/conversations/{conversationId}` | Update conversation |
| DELETE | `/conversations/{conversationId}` | Delete conversation |
| POST | `/conversations/messages` | Send message |
| POST | `/conversations/messages/inbound` | Add inbound message |
| POST | `/conversations/messages/upload` | Upload attachment |
| PUT | `/conversations/messages/{messageId}/status` | Update message status |
| DELETE | `/conversations/messages/{messageId}/schedule` | Cancel scheduled message |
| GET | `/conversations/messages/{messageId}/recording` | Get call recording |
| GET | `/conversations/messages/{messageId}/transcription` | Get call transcription |

## Send Message Body

```json
{
  "type": "SMS",
  "contactId": "contact_id",
  "message": "Hello from Claude!"
}
```

**Supported message types**: `SMS`, `Email`, `WhatsApp`, `FB` (Facebook Messenger), `IG` (Instagram DM), `Live_Chat`, `Custom`

For Email type, include:
```json
{
  "type": "Email",
  "contactId": "contact_id",
  "subject": "Email Subject",
  "message": "<p>HTML email body</p>",
  "emailFrom": "sender@domain.com"
}
```

## Scopes Required
`conversations.readonly`, `conversations.write`, `conversations/message.readonly`, `conversations/message.write`
