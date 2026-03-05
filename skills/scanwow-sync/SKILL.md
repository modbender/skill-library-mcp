---
name: scanwow-sync
description: Sync your OpenClaw agent with the ScanWow iOS app. Start an HTTP webhook to receive high-quality OCR scans directly from your phone into your agent's workspace.
metadata: {"clawdbot":{"emoji":"📸"}}
---

# ScanWow Sync

Connect your OpenClaw agent to your iPhone's camera using the **ScanWow** iOS app. 
Scan documents on your phone, let AI extract the text, and beam it instantly to your agent's workspace using Secure API Export.

## Setup Instructions

1. **Start a Webhook Server** on your OpenClaw host (or through a reverse proxy).
   You can use Python, Node, or netcat. Here is a simple Python webhook to save incoming scans:

```python
# save_scans.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

TOKEN = "YOUR_SECRET_TOKEN"

class ScanHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        auth = self.headers.get("Authorization")
        if auth != f"Bearer {TOKEN}":
            self.send_response(401)
            self.end_headers()
            return
            
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len)
        data = json.loads(post_body)
        
        # Save the OCR text
        filename = f"scan_{data.get('id', 'doc')}.md"
        with open(filename, 'w') as f:
            f.write(data.get('text', ''))
            
        print(f"✅ Saved scan: {filename}")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"success":true}')

print("Listening for ScanWow scans on port 8000...")
HTTPServer(('', 8000), ScanHandler).serve_forever()
```

2. Run the server:
   `python3 save_scans.py`
   *(Ensure port 8000 is accessible from the internet, e.g., using ngrok, Cloudflare Tunnels, or your public IP)*

3. **Configure the ScanWow App**
   - Open ScanWow on your iOS device
   - Tap the Settings gear ⚙️
   - Go to **Secure API Export**
   - Enter your public Endpoint URL (e.g., `https://your-server.com/api/scan`)
   - Enter your Token (`YOUR_SECRET_TOKEN`)
   - Turn it **ON**

## Payload Format

When you capture a document and save it in ScanWow, it will automatically send a POST request with the following JSON:

```json
{
  "id": "uuid-string",
  "text": "Extracted document text...",
  "confidence": 0.98,
  "pages": 1,
  "timestamp": 1708531200000,
  "isEnhanced": true
}
```

Now any scan you take on your phone will appear magically in your OpenClaw agent's workspace!