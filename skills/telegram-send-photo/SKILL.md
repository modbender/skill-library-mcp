---
name: telegram-send-photo
description: Send photos via Telegram Bot API.
---

## Description
This skill allows sending image files to Telegram using the Bot API. Useful for sharing screenshots, images, or any visual content through Telegram.

## Requirements
- Python 3.x
- requests library (`pip install requests`)
- Telegram Bot Token
- Target Chat ID

## Usage

### Python Script
```python
import requests

# Configuration
bot_token = "YOUR_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"
photo_path = "path/to/image.png"

# Send photo
url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
files = {"photo": open(photo_path, "rb")}
data = {"chat_id": chat_id, "caption": "图片描述"}
resp = requests.post(url, files=files, data=data)

# Check response
if resp.status_code == 200:
    print("Photo sent successfully!")
else:
    print(f"Failed: {resp.text}")
```

### Key Points
1. Open image in binary mode (`"rb"`)
2. `chat_id` is required
3. Use `caption` for optional description
4. Handle encoding issues for special characters

## Configuration
- **Bot Token**: `8610746914:AAHvbRYhGar_DD81-70IeWSSfkDLyvrWKY0`
- **Chat ID**: `8422738233`
- **Photo Storage**: `D:\mimoTool\photo\`

## Files
- `telegram_send_photo.py` - Main script

## Example
```python
# Send a screenshot
photo_path = "D:\\mimoTool\\photo\\20260225_103159.png"
send_photo(photo_path, caption="截图")
```
