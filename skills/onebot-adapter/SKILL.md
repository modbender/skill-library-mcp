---
name: onebot-adapter
description: Connect OpenClaw to OneBot protocol for QQ bot integration. Use when receiving or sending QQ messages via NapCat or other OneBot servers.
version: 1.0.0
---

# OneBot Adapter

Connect OpenClaw to OneBot protocol servers like NapCat for QQ bot functionality.

## Quick Start

### 1. Configure Connection

Set OneBot server URL in environment or config:
```bash
export ONEBOT_WS_URL="ws://127.0.0.1:3001"
export ONEBOT_HTTP_URL="http://127.0.0.1:3000"
export ONEBOT_TOKEN="your-token"
```

### 2. Receive Messages

Use the WebSocket listener script to receive QQ messages:
```bash
python scripts/onebot_ws_listener.py
```

### 3. Send Messages

Use HTTP API to send messages:
```python
from scripts.onebot_client import OneBotClient

client = OneBotClient()
client.send_private_msg(user_id=123456, message="Hello!")
client.send_group_msg(group_id=789012, message="Group message")
```

## Connection Modes

### WebSocket (Recommended)
- Real-time bidirectional communication
- Receives events instantly
- Supports both sending and receiving

### HTTP
- Request-response model
- Good for simple sending
- Requires polling for receiving

## Common Tasks

### Get Login Info
```python
client.get_login_info()
```

### Get Friend/Group List
```python
client.get_friend_list()
client.get_group_list()
```

### Handle Messages
See [references/message-handling.md](references/message-handling.md) for message parsing and response patterns.

## NapCat Specific

NapCat is a OneBot11 implementation based on NTQQ.

Default ports:
- WebSocket: 3001
- HTTP: 3000
- WebUI: 6099

Token authentication is optional but recommended for public deployments.

## Troubleshooting

**Connection refused**: Check if OneBot server is running and ports are correct.

**Authentication failed**: Verify token matches OneBot server configuration.

**Message not delivered**: Check user_id/group_id exists and bot has permission.
