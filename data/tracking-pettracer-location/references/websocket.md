# PetTracer WebSocket (SockJS + STOMP) notes

Use this only when you need near-real-time updates. For one-off “where is my pet?” requests,
prefer the REST snapshot (`/map/getccs`) to keep things simple.

## Endpoint

Base URL (SockJS):
- `wss://pt.pettracer.com/sc`

The web portal uses a derived URL of the form:

```
wss://pt.pettracer.com/sc/<server_id>/<session_id>/websocket?access_token=<token>
```

Where:
- `server_id` is a random 3-digit string (`000`–`999`)
- `session_id` is a random 8-char `[a-z0-9]` string
- `access_token` is the bearer token from `POST /user/login`

## Security note

The token appears in the **URL query string**. Never print full URLs to logs or chat output.
If you must log connection details, redact `access_token`.

## Protocol layers

1) **SockJS framing** from server:
- `o` open frame
- `h` heartbeat
- `a[...]` array of string messages
- `c[...]` close frame

2) **STOMP** inside the SockJS message array

### Minimal connection flow

1. Connect WebSocket to the SockJS URL (includes `access_token`).
2. On SockJS open (`o`), send a STOMP `CONNECT` frame.
3. After STOMP `CONNECTED`, send `SUBSCRIBE` frames to:
   - `/user/queue/messages`
   - `/user/queue/portal`
4. Send a `SEND` frame to `/app/subscribe` with body:
   ```json
   {"deviceIds":[12345,67890]}
   ```
5. Handle `MESSAGE` frames; the body is typically JSON containing updates keyed by device `id`.

Implementation reference:
- `scripts/pettracer_watch.py`
