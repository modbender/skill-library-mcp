# Messaging & Notifications

## Send Messages

```bash
# Send message to a user (DIALOG_ID = user ID)
curl -s "${BITRIX24_WEBHOOK_URL}im.message.add.json" \
  -d 'DIALOG_ID=1&MESSAGE=Hello!' | jq .result

# Send message to a group chat (DIALOG_ID = chat{ID})
curl -s "${BITRIX24_WEBHOOK_URL}im.message.add.json" \
  -d 'DIALOG_ID=chat42&MESSAGE=Hello team!' | jq .result

# Update message
curl -s "${BITRIX24_WEBHOOK_URL}im.message.update.json" \
  -d 'MESSAGE_ID=123&MESSAGE=Updated text' | jq .result

# Delete message
curl -s "${BITRIX24_WEBHOOK_URL}im.message.delete.json" \
  -d 'MESSAGE_ID=123' | jq .result
```

## Notifications

```bash
# System notification to a user
curl -s "${BITRIX24_WEBHOOK_URL}im.notify.system.add.json" \
  -d 'USER_ID=1&MESSAGE=Important notification' | jq .result

# Personal notification
curl -s "${BITRIX24_WEBHOOK_URL}im.notify.personal.add.json" \
  -d 'USER_ID=1&MESSAGE=Personal alert' | jq .result

# Delete notification
curl -s "${BITRIX24_WEBHOOK_URL}im.notify.delete.json" -d 'ID=123' | jq .result
```

## Chat Management

```bash
# Create group chat
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.add.json" \
  -d 'TYPE=CHAT&TITLE=Project Chat&USERS[]=1&USERS[]=2&USERS[]=3&MESSAGE=Chat created' | jq .result

# Get chat info
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.get.json" -d 'CHAT_ID=42' | jq .result

# Add user to chat
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.user.add.json" \
  -d 'CHAT_ID=42&USERS[]=4' | jq .result

# Remove user from chat
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.user.delete.json" \
  -d 'CHAT_ID=42&USER_ID=4' | jq .result

# List chat members
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.user.list.json" -d 'CHAT_ID=42' | jq .result

# Update chat title
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.update.json" \
  -d 'CHAT_ID=42&TITLE=New Chat Title' | jq .result

# Leave chat
curl -s "${BITRIX24_WEBHOOK_URL}im.chat.leave.json" -d 'CHAT_ID=42' | jq .result
```

## Dialog History

```bash
# Get messages from a dialog
curl -s "${BITRIX24_WEBHOOK_URL}im.dialog.messages.get.json" \
  -d 'DIALOG_ID=1&LIMIT=20' | jq '.result.messages'

# Get recent dialogs
curl -s "${BITRIX24_WEBHOOK_URL}im.recent.list.json" | jq .result
```

## Message Formatting (BB-code)

Bitrix24 chat uses BB-code:
```
[b]bold[/b]
[i]italic[/i]
[s]strikethrough[/s]
[u]underline[/u]
[code]inline code[/code]
[url=https://example.com]link text[/url]
[user=42]User Name[/user]   (mention)
```

## Reference

**Chat types:** `CHAT` (group), `OPEN` (open channel), `LINES` (open lines).

**DIALOG_ID format:**
- `123` — direct message to user ID 123
- `chat456` — group chat with chat ID 456

## More Methods (MCP)

This file covers common messaging methods. For additional methods or updated parameters, use MCP:
- `bitrix-search "im message"` — find all messaging methods
- `bitrix-search "im chat"` — find chat management methods
- `bitrix-method-details im.message.add` — get full spec for any method
