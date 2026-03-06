# OAuth Flow Patterns

## Local Callback Server (Google/YouTube)

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        nonlocal auth_code
        params = parse_qs(urlparse(self.path).query)
        auth_code = params.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Authorization complete. Close this tab.")

server = HTTPServer(('localhost', 8422), CallbackHandler)
thread = threading.Thread(target=server.handle_request)
thread.start()

# Open browser to auth URL, wait for callback
# Exchange auth_code for tokens
```

## Facebook Long-Lived Token Exchange

```
GET https://graph.facebook.com/v21.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={app_id}
  &client_secret={app_secret}
  &fb_exchange_token={short_lived_token}
```

Then get page token from long-lived user token:
```
GET https://graph.facebook.com/v21.0/me/accounts
  ?access_token={long_lived_user_token}
```

Page tokens from long-lived user tokens **never expire**.

## Token Refresh Decision Tree

```
Is token expired?
├── YouTube → refresh with google.auth refresh_token
├── Facebook Page Token → never expires (if from long-lived user token)
├── Twitter → never expires
├── TikTok → refresh with refresh_token (24h expiry)
└── Unknown → try API call, if 401 → refresh
```
