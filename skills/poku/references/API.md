# Poku API Reference

## Endpoint

```
POST https://api.pokulabs.com/phone/call
```

## Authentication

```
Authorization: Bearer $POKU_API_KEY
```

## Request Parameters

| Parameter | Required | Description |
|---|---|---|
| `message` | Yes | Full voice agent prompt (structured markdown) |
| `to` | Yes | Destination phone number in E.164 format (e.g. `+15551234567`) |

## Error Responses

| Error | Meaning | Action |
|---|---|---|
| `"human did not respond"` | Call connected but no one answered or engaged | Report to user and stop |
| `"invalid to number"` | `to` field is malformed or unroutable | Report to user; re-check E.164 formatting from Step 1 |
| `"timeout"` | Call exceeded 5-minute limit with no result | Report to user; do not retry automatically |

On any error not listed above, report the raw response to the user and do not retry.
