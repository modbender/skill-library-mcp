# BlueBubbles API Reference

Endpoints used by this skill. Full docs: https://documenter.getpostman.com/view/765844/UVR4PVmG

## Base URL

Default: `http://127.0.0.1:1234`  
Configure via `BB_URL` env var.

## Authentication

All requests require password auth (one of):
- Query param: `?password=YOUR_PASSWORD`
- Header: `Authorization: Bearer YOUR_PASSWORD`

Password set in BlueBubbles Server → Settings → API.

---

## Endpoints

### Health Check
```
GET /api/v1/ping
```
Returns `{"message": "pong", ...}` if server is running.

### List Webhooks
```
GET /api/v1/webhook
```
Returns array of registered webhooks with `id`, `url`, `events[]`.

### Register Webhook
```
POST /api/v1/webhook
Content-Type: application/json

{
  "url": "http://localhost:18789/api/channels/bluebubbles/webhook",
  "events": ["*"]
}
```
Returns created webhook object with `id`.

### Delete Webhook
```
DELETE /api/v1/webhook/:id
```
Removes webhook by ID. Use to clear broken registrations before re-registering.

### Server Logs
```
GET /api/v1/server/logs
```
Returns recent server logs. Used to check for webhook delivery failures/backoff state.

---

## Quick Test Commands

```bash
# Health check
curl "http://127.0.0.1:1234/api/v1/ping?password=YOUR_PASSWORD"

# List webhooks
curl "http://127.0.0.1:1234/api/v1/webhook?password=YOUR_PASSWORD"

# Check logs for delivery issues
curl "http://127.0.0.1:1234/api/v1/server/logs?password=YOUR_PASSWORD" | grep -i webhook
```
