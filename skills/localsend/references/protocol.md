# LocalSend v2 Protocol Reference

## Network Defaults

- Multicast group: `224.0.0.167`
- Port: `53317` (TCP for HTTPS, UDP for multicast)
- Protocol version: `"2.0"` / `"2.1"`

## Discovery

Devices announce via UDP multicast JSON with `"announce": true`. Responders reply via HTTP POST to `/api/localsend/v2/register` (preferred) or multicast with `"announce": false`.

### Device info JSON

```json
{
  "alias": "Device Name",
  "version": "2.0",
  "deviceModel": "Linux",
  "deviceType": "headless",
  "fingerprint": "<sha256-hex>",
  "port": 53317,
  "protocol": "https",
  "download": false,
  "announce": true
}
```

Device types: `mobile`, `desktop`, `web`, `headless`, `server`.

## Send Flow

1. **Prepare**: `POST /api/localsend/v2/prepare-upload` with `{info, files}` — receiver responds with `{sessionId, files: {fileId: token}}`.
2. **Upload**: `POST /api/localsend/v2/upload?sessionId=X&fileId=Y&token=Z` with raw binary body.
3. **Cancel** (optional): `POST /api/localsend/v2/cancel?sessionId=X`.

## Receive Flow

Run HTTPS server on port 53317, handle `/prepare-upload` and `/upload` endpoints. Each device uses a self-signed TLS certificate; clients skip verification.

## Error Codes

| Code | Meaning |
|------|---------|
| 204 | Nothing to transfer |
| 400 | Invalid request |
| 401 | PIN required |
| 403 | Declined |
| 409 | Busy with another session |
| 429 | Too many PIN attempts |
| 500 | Server error |
