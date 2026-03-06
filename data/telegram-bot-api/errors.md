# Error Codes — Telegram Bot API

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Check `ok` field in response |
| 400 | Bad Request | Fix request parameters |
| 401 | Unauthorized | Check bot token |
| 403 | Forbidden | Bot blocked or no permission |
| 404 | Not Found | Wrong method name |
| 409 | Conflict | Webhook/getUpdates conflict |
| 429 | Too Many Requests | Rate limited, wait and retry |
| 500+ | Server Error | Telegram issue, retry later |

---

## Common Error Codes

### Authentication Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Unauthorized` | Invalid bot token | Check token with @BotFather |
| `Not Found` | Token format wrong | Use `bot123456:ABC-DEF...` format |

### Chat Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Bad Request: chat not found` | Invalid chat_id | Verify chat_id is correct |
| `Forbidden: bot was blocked by the user` | User blocked bot | Remove from recipient list |
| `Forbidden: bot was kicked from the group chat` | Bot removed from group | Re-add bot to group |
| `Forbidden: bot is not a member of the channel chat` | Bot not in channel | Add bot as admin |
| `Bad Request: PEER_ID_INVALID` | Never interacted with user | User must /start first |

### Message Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Bad Request: message is not modified` | editMessage with same content | Check if content changed |
| `Bad Request: message to edit not found` | Message deleted or too old | Handle gracefully |
| `Bad Request: message can't be deleted` | Message too old (>48h) | Only own messages >48h |
| `Bad Request: MESSAGE_TOO_LONG` | Text >4096 chars | Split message |
| `Bad Request: can't parse entities` | Invalid parse_mode formatting | Escape special characters |

### Media Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Bad Request: wrong file identifier` | Invalid file_id | file_id is bot-specific |
| `Bad Request: file is too big` | Exceeds size limit | Compress or split file |
| `Bad Request: wrong type of file` | File type mismatch | Use correct send method |
| `Bad Request: PHOTO_INVALID_DIMENSIONS` | Photo too small/large | Resize to valid dimensions |

### Keyboard Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Bad Request: BUTTON_DATA_INVALID` | callback_data >64 bytes | Shorten callback data |
| `Bad Request: can't parse inline keyboard button` | Invalid JSON | Check JSON structure |

### Rate Limit Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Too Many Requests: retry after X` | Rate limited | Wait X seconds, then retry |

---

## Rate Limits

### Per-Chat Limits

| Scope | Limit |
|-------|-------|
| Same chat | ~1 msg/second |
| Same group | ~20 msg/minute |
| Different chats | ~30 msg/second |

### Handling 429 Errors

```python
import time
import requests

def send_message(chat_id, text, max_retries=3):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    for attempt in range(max_retries):
        response = requests.post(url, json={
            "chat_id": chat_id,
            "text": text
        })
        
        if response.status_code == 200:
            return response.json()
        
        if response.status_code == 429:
            retry_after = response.json().get("parameters", {}).get("retry_after", 5)
            print(f"Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
        
        # Other error
        return response.json()
    
    raise Exception("Max retries exceeded")
```

### Best Practices

1. **Queue messages** — Don't send bursts
2. **Batch by chat** — Group messages to same chat
3. **Use exponential backoff** — Start with `retry_after`, increase on repeat
4. **Track per-chat limits** — Maintain separate counters

---

## Response Structure

### Success Response

```json
{
  "ok": true,
  "result": {
    "message_id": 100,
    "chat": {"id": 123456789},
    "text": "Hello"
  }
}
```

### Error Response

```json
{
  "ok": false,
  "error_code": 400,
  "description": "Bad Request: message is not modified",
  "parameters": {
    "retry_after": 30  // Only for 429 errors
  }
}
```

---

## Error Handling Pattern

```python
def api_call(method, **params):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        json=params
    )
    
    data = response.json()
    
    if data["ok"]:
        return data["result"]
    
    error_code = data.get("error_code")
    description = data.get("description", "Unknown error")
    
    if error_code == 429:
        retry_after = data.get("parameters", {}).get("retry_after", 5)
        raise RateLimitError(retry_after)
    
    if error_code == 403:
        if "blocked" in description:
            raise UserBlockedError(params.get("chat_id"))
        if "kicked" in description:
            raise BotKickedError(params.get("chat_id"))
    
    if error_code == 400:
        if "not modified" in description:
            return None  # Ignore, message already has this content
        if "parse entities" in description:
            # Retry without formatting
            params.pop("parse_mode", None)
            return api_call(method, **params)
    
    raise TelegramAPIError(error_code, description)
```

---

## Debugging Tips

1. **Check `ok` field first** — Even 200 responses can have `ok: false`
2. **Log full responses** — Error details are in `description`
3. **Test with curl** — Isolate issues from your code
4. **Use @BotFather /token** — Regenerate if token exposed
5. **Monitor error patterns** — Track which errors are common
