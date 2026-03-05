# OneBot Message Handling

## Message Event Structure

### Private Message
```json
{
  "post_type": "message",
  "message_type": "private",
  "user_id": 123456789,
  "message": "Hello",
  "raw_message": "Hello",
  "message_id": 12345,
  "time": 1234567890
}
```

### Group Message
```json
{
  "post_type": "message",
  "message_type": "group",
  "group_id": 987654321,
  "user_id": 123456789,
  "message": "Hello group",
  "raw_message": "Hello group",
  "message_id": 12345,
  "time": 1234567890
}
```

## Message Segments

### Text
```json
{"type": "text", "data": {"text": "Hello"}}
```

### At (Mention)
```json
{"type": "at", "data": {"qq": "123456789"}}
```

### Image
```json
{"type": "image", "data": {"file": "http://example.com/image.jpg"}}
```

### Reply
```json
{"type": "reply", "data": {"id": "12345"}}
```

## Common Patterns

### 1. Echo Bot (Auto-reply)
```python
async def echo_handler(event):
    if event.get("message") == "ping":
        user_id = event.get("user_id")
        client.send_private_msg(user_id, "pong")
```

### 2. Keyword Response
```python
async def keyword_handler(event):
    message = event.get("message", "")
    
    if "帮助" in message:
        reply = "可用命令: /help, /status, /info"
    elif message.startswith("/"):
        reply = f"执行命令: {message}"
    else:
        return  # Ignore
    
    if event.get("message_type") == "private":
        client.send_private_msg(event["user_id"], reply)
    else:
        client.send_group_msg(event["group_id"], reply)
```

### 3. Group Management
```python
async def admin_handler(event):
    if event.get("message") == "/kick @user":
        group_id = event.get("group_id")
        user_id = extract_user_id(event.get("message"))
        client.set_group_kick(group_id, user_id)
```

## Notice Events

### Group Member Increase
```json
{
  "post_type": "notice",
  "notice_type": "group_increase",
  "group_id": 987654321,
  "user_id": 123456789
}
```

### Group Member Decrease
```json
{
  "post_type": "notice",
  "notice_type": "group_decrease",
  "group_id": 987654321,
  "user_id": 123456789
}
```

### Group Ban
```json
{
  "post_type": "notice",
  "notice_type": "group_ban",
  "group_id": 987654321,
  "user_id": 123456789,
  "duration": 3600
}
```

## Error Handling

### Connection Errors
- Check if OneBot server is running
- Verify WebSocket URL and port
- Check firewall settings

### Authentication Errors
- Verify token is correct
- Check token format (Bearer token)

### Message Errors
- Validate user_id/group_id exists
- Check message format (string or array)
- Verify bot has permission
