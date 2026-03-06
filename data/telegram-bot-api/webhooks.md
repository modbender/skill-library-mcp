# Webhooks & Polling — Telegram Bot API

## Comparison

| Feature | Webhooks | Long Polling |
|---------|----------|--------------|
| Setup | Need HTTPS server | Just run script |
| Latency | Instant | Depends on timeout |
| Server load | On-demand | Constant connection |
| Scalability | Easy to scale | Single process |
| Development | Harder to test | Easy local testing |
| Best for | Production | Development |

---

## Long Polling (getUpdates)

### Basic Polling Loop

```bash
#!/bin/bash
TOKEN="YOUR_TOKEN"
OFFSET=0

while true; do
  response=$(curl -s "https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${OFFSET}&timeout=30")
  
  # Process updates
  echo "$response" | jq -r '.result[] | @json' | while read update; do
    # Handle each update
    echo "Received: $update"
    
    # Get update_id for offset
    update_id=$(echo "$update" | jq -r '.update_id')
    OFFSET=$((update_id + 1))
  done
done
```

### Python Polling

```python
import requests
import time

TOKEN = "YOUR_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
offset = 0

while True:
    try:
        response = requests.get(
            f"{BASE_URL}/getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=35
        )
        updates = response.json().get("result", [])
        
        for update in updates:
            # Process update
            print(f"Received: {update}")
            offset = update["update_id"] + 1
            
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
```

### getUpdates Parameters

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| offset | First update ID to return | last_update_id + 1 |
| limit | Max updates per request | 100 (default) |
| timeout | Long polling timeout (seconds) | 30 |
| allowed_updates | Filter update types | See below |

### Allowed Update Types

```bash
curl "https://api.telegram.org/bot${TOKEN}/getUpdates" \
  -d "allowed_updates=[\"message\",\"callback_query\"]"
```

Available types:
- `message`
- `edited_message`
- `channel_post`
- `edited_channel_post`
- `inline_query`
- `chosen_inline_result`
- `callback_query`
- `shipping_query`
- `pre_checkout_query`
- `poll`
- `poll_answer`
- `my_chat_member`
- `chat_member`
- `chat_join_request`

---

## Webhooks

### Requirements

1. **Valid HTTPS URL** — Must have valid SSL certificate
2. **Ports** — 443, 80, 88, or 8443
3. **Self-signed certs** — Must upload certificate with setWebhook

### Set Webhook

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -d "url=https://example.com/webhook/${TOKEN}" \
  -d "max_connections=40" \
  -d "allowed_updates=[\"message\",\"callback_query\"]"
```

### With Self-Signed Certificate

```bash
# Generate self-signed cert
openssl req -newkey rsa:2048 -sha256 -nodes \
  -keyout private.key \
  -x509 -days 365 \
  -out public.pem \
  -subj "/CN=YOUR_DOMAIN"

# Set webhook with certificate
curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -F "url=https://YOUR_DOMAIN:8443/webhook" \
  -F "certificate=@public.pem"
```

### With Secret Token (recommended)

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -d "url=https://example.com/webhook" \
  -d "secret_token=your_secret_token"
```

Telegram sends secret in `X-Telegram-Bot-Api-Secret-Token` header. Verify it:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET_TOKEN = "your_secret_token"

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify secret token
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403
    
    update = request.get_json()
    # Process update
    return jsonify({"ok": True})
```

### Check Webhook Status

```bash
curl "https://api.telegram.org/bot${TOKEN}/getWebhookInfo"
```

Response:
```json
{
  "ok": true,
  "result": {
    "url": "https://example.com/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40,
    "allowed_updates": ["message", "callback_query"]
  }
}
```

### Delete Webhook

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/deleteWebhook" \
  -d "drop_pending_updates=true"
```

---

## Webhook Server Examples

### Python (Flask)

```python
from flask import Flask, request
import requests

app = Flask(__name__)
TOKEN = "YOUR_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')
        
        # Echo the message
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"You said: {text}"
        })
    
    return {"ok": True}

if __name__ == '__main__':
    app.run(port=8443, ssl_context=('public.pem', 'private.key'))
```

### Node.js (Express)

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const TOKEN = 'YOUR_TOKEN';
const BASE_URL = `https://api.telegram.org/bot${TOKEN}`;

app.post('/webhook', async (req, res) => {
    const update = req.body;
    
    if (update.message) {
        const chatId = update.message.chat.id;
        const text = update.message.text || '';
        
        await axios.post(`${BASE_URL}/sendMessage`, {
            chat_id: chatId,
            text: `You said: ${text}`
        });
    }
    
    res.json({ ok: true });
});

app.listen(8443);
```

---

## Local Development

### Using ngrok

```bash
# Start your local server
python app.py  # Runs on port 5000

# In another terminal, expose it
ngrok http 5000

# Copy the HTTPS URL and set webhook
curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -d "url=https://abc123.ngrok.io/webhook"
```

### Using Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:5000
```

---

## Tips

1. **Return 200 quickly** — Telegram retries on timeout/errors
2. **Process async** — Queue heavy tasks, respond immediately
3. **Use secret_token** — Verify requests are from Telegram
4. **Monitor pending_update_count** — Should be 0 normally
5. **Test locally first** — Use ngrok or polling before production
6. **Handle all update types** — Don't crash on unexpected updates
