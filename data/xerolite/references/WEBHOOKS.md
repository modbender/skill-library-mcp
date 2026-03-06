# Xerolite Webhook Reference

## Endpoint

After running `install.sh`:

```
POST /hooks/xerolite
Authorization: Bearer <hooks.token>
Content-Type: application/json
```

## Behavior

Payloads are passed through the `transforms/xerolite.js` transformer, then delivered to the user's active channel.  
The transform:

- Always starts with a `📥 **Xerolite Notification**` header.
- If `event` is present, adds `**Event:** <value>`.
- If `message` is present, adds `**Message:** <value>`.
- If `data` is present:
  - When `data` is an object, prints each key/value as bullet points under `**Data:**`.
  - Otherwise prints `**Data:** <value>`.
- For any other top-level fields (not `event`, `message`, or `data`), prints them as `**field:** value` (objects are JSON-stringified).

## Payload Format

Any valid JSON. The transform will format and forward whatever fields are present.

### Examples

Order event:

```json
{
  "event": "order.created",
  "message": " This order come from provider and place success.",
  "data": {
    "order_id": "ORD-001",
    "customer": "Alice",
    "total": 99.00
  }
}
```

Alert / strategy event:

```json
{
  "event": "alert",
  "message": "Low inventory warning",
  "data": "warning"
}
```

Simple notification:

```json
{
  "event": "notification",
  "message": "Backup completed successfully"
}
```

## Testing

```bash
curl -X POST http://localhost:18789/hooks/xerolite \
  -H 'Authorization: Bearer YOUR_HOOKS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"event": "notify", "message": "Hello from Xerolite"}'
```

## Delivery

- Uses `deliver: true` — agent response goes to active channel
- If no active channel, falls back to last used channel
