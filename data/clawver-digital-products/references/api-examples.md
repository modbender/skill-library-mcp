# Digital Products API Examples

## Good Example: Correct Digital Product Lifecycle

```bash
curl -X POST https://api.clawver.store/v1/products \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pack","description":"Starter pack","type":"digital","priceInCents":999,"images":["https://example.com/preview.jpg"]}'

curl -X POST https://api.clawver.store/v1/products/{productId}/file \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fileUrl":"https://example.com/pack.zip","fileType":"zip"}'

curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

Why this works: it follows create -> attach file -> activate.

## Bad Example: Wrong Product Type

```json
{"name":"Pack","type":"digital_product","priceInCents":999}
```

Why it fails: type must match API enum (`digital` for downloadable products).

Fix: use `"type":"digital"`.

## Bad Example: Unsupported File Type

```json
{"fileUrl":"https://example.com/pack.exe","fileType":"exe"}
```

Why it fails: unsupported file type.

Fix: use a supported type (`zip`, `pdf`, `epub`, `mp3`, `mp4`, `png`, `jpg`, `jpeg`, `gif`, `txt`).
