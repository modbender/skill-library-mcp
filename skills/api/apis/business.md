# Index

| API | Line |
|-----|------|
| Shopify | 2 |
| DocuSign | 83 |
| Bitly | 287 |
| Dub | 380 |

---

# Shopify

## Base URL
```
https://{store}.myshopify.com/admin/api/2024-01
```

## Authentication
```bash
# Admin API (access token)
curl "https://{store}.myshopify.com/admin/api/2024-01/products.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /products.json | GET | List products |
| /products.json | POST | Create product |
| /orders.json | GET | List orders |
| /customers.json | GET | List customers |
| /inventory_levels.json | GET | Get inventory |

## Quick Examples

### List Products
```bash
curl "https://{store}.myshopify.com/admin/api/2024-01/products.json?limit=10" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Create Product
```bash
curl -X POST "https://{store}.myshopify.com/admin/api/2024-01/products.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": {
      "title": "New Product",
      "body_html": "<p>Description</p>",
      "vendor": "Vendor",
      "product_type": "Type",
      "variants": [{"price": "19.99", "sku": "SKU001"}]
    }
  }'
```

### List Orders
```bash
curl "https://{store}.myshopify.com/admin/api/2024-01/orders.json?status=any&limit=50" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Update Inventory
```bash
curl -X POST "https://{store}.myshopify.com/admin/api/2024-01/inventory_levels/set.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 123456,
    "inventory_item_id": 789012,
    "available": 100
  }'
```

## Common Traps

- API version in URL (2024-01, etc.) - use latest stable
- Pagination via Link header, not offset
- Products have variants for different sizes/colors
- Inventory requires location_id
- Rate limit: 2 requests/second (bucket of 40)

## Rate Limits

- 2 requests/second with bucket of 40
- Plus plan: 4 req/s, bucket 80

## Official Docs
https://shopify.dev/docs/api/admin-rest
# DocuSign

DocuSign eSignature REST API for sending documents, managing envelopes, and collecting signatures.

## Base URL
`https://demo.docusign.net/restapi` (sandbox)
`https://{server}.docusign.net/restapi` (production)

## Authentication
OAuth 2.0 (Authorization Code Grant or JWT). Requires DocuSign Developer account.

```bash
curl -X GET "https://demo.docusign.net/restapi/v2.1/accounts/{ACCOUNT_ID}/envelopes" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Core Endpoints

### Get User Info
```bash
curl -X GET "https://account-d.docusign.com/oauth/userinfo" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Create Envelope (Send for Signature)
```bash
curl -X POST "https://demo.docusign.net/restapi/v2.1/accounts/{ACCOUNT_ID}/envelopes" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "emailSubject": "Please sign this document",
    "documents": [{
      "documentBase64": "{BASE64_PDF}",
      "name": "Contract.pdf",
      "fileExtension": "pdf",
      "documentId": "1"
    }],
    "recipients": {
      "signers": [{
        "email": "signer@example.com",
        "name": "John Signer",
        "recipientId": "1",
        "routingOrder": "1",
        "tabs": {
          "signHereTabs": [{
            "documentId": "1",
            "pageNumber": "1",
            "xPosition": "100",
            "yPosition": "500"
          }]
        }
      }]
    },
    "status": "sent"
  }'
```

### Get Envelope Status
```bash
curl -X GET "https://demo.docusign.net/restapi/v2.1/accounts/{ACCOUNT_ID}/envelopes/{ENVELOPE_ID}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### List Envelopes
```bash
curl -X GET "https://demo.docusign.net/restapi/v2.1/accounts/{ACCOUNT_ID}/envelopes?from_date=2024-01-01" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Download Signed Document
```bash
curl -X GET "https://demo.docusign.net/restapi/v2.1/accounts/{ACCOUNT_ID}/envelopes/{ENVELOPE_ID}/documents/combined" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -o "signed_document.pdf"
```

### Create Embedded Signing URL
```bash
curl -X POST "https://demo.docusign.net/restapi/v2.1/accounts/{ACCOUNT_ID}/envelopes/{ENVELOPE_ID}/views/recipient" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "returnUrl": "https://example.com/signing-complete",
    "authenticationMethod": "none",
    "email": "signer@example.com",
    "userName": "John Signer"
  }'
```

## Rate Limits
- 1000 requests/hour (per integration key)
- Burst limit: 20 requests/second
- Polling: Use webhooks instead (Connect)

## Gotchas
- **Sandbox vs Production**: Different base URLs and accounts
- `status: "sent"` sends immediately; use `"created"` for draft
- Account ID from `/oauth/userinfo` response (not visible in UI)
- Tab positions are in pixels from bottom-left
- JWT auth requires RSA key pair and consent
- Webhooks configured via DocuSign Connect
- Envelope status: `sent`, `delivered`, `completed`, `declined`, `voided`

## Links
- [Docs](https://developers.docusign.com/docs/esign-rest-api/)
- [API Reference](https://developers.docusign.com/docs/esign-rest-api/reference/)
- [Authentication](https://developers.docusign.com/platform/auth/)
- [API Explorer](https://developers.docusign.com/tools/api-explorer)
# HelloSign (Dropbox Sign)

Dropbox Sign (formerly HelloSign) API for e-signatures and document workflows.

## Base URL
`https://api.hellosign.com/v3`

## Authentication
HTTP Basic Auth with API key as username (password empty), or OAuth 2.0.

```bash
curl -X GET "https://api.hellosign.com/v3/account" \
  -u "{API_KEY}:"
```

## Core Endpoints

### Get Account
```bash
curl -X GET "https://api.hellosign.com/v3/account" \
  -u "{API_KEY}:"
```

### Create Signature Request
```bash
curl -X POST "https://api.hellosign.com/v3/signature_request/send" \
  -u "{API_KEY}:" \
  -F "title=Contract Agreement" \
  -F "subject=Please sign this document" \
  -F "message=Review and sign at your convenience" \
  -F "signers[0][email_address]=signer@example.com" \
  -F "signers[0][name]=John Signer" \
  -F "file[0]=@/path/to/document.pdf"
```

### Create Signature Request with Template
```bash
curl -X POST "https://api.hellosign.com/v3/signature_request/send_with_template" \
  -u "{API_KEY}:" \
  -F "template_ids[0]=abc123def456" \
  -F "subject=Please sign" \
  -F "signers[Signer][email_address]=signer@example.com" \
  -F "signers[Signer][name]=John Signer"
```

### Get Signature Request
```bash
curl -X GET "https://api.hellosign.com/v3/signature_request/{SIGNATURE_REQUEST_ID}" \
  -u "{API_KEY}:"
```

### Download Files
```bash
curl -X GET "https://api.hellosign.com/v3/signature_request/files/{SIGNATURE_REQUEST_ID}" \
  -u "{API_KEY}:" \
  -o "signed_document.pdf"
```

### Cancel Signature Request
```bash
curl -X POST "https://api.hellosign.com/v3/signature_request/cancel/{SIGNATURE_REQUEST_ID}" \
  -u "{API_KEY}:"
```

### Create Embedded Signing URL
```bash
curl -X POST "https://api.hellosign.com/v3/embedded/sign_url/{SIGNATURE_ID}" \
  -u "{API_KEY}:"
```

### List Templates
```bash
curl -X GET "https://api.hellosign.com/v3/template/list" \
  -u "{API_KEY}:"
```

## Rate Limits
- Test mode: 20 requests/minute
- Production: Based on plan (typically 200+/minute)
- Burst protection applies

## Gotchas
- **Rebranded**: HelloSign is now Dropbox Sign; API URLs unchanged
- Basic Auth: API key as username, password left empty (note the trailing colon)
- Test mode requests don't count against quota (add `test_mode=1`)
- Embedded signing requires approved API App
- `signature_id` different from `signature_request_id` (per-signer vs per-request)
- Templates created in web UI or via API
- Webhooks (Events) configured via API App settings
- SMS authentication and eID available for additional verification

## Links
- [Docs](https://developers.hellosign.com/docs)
- [API Reference](https://developers.hellosign.com/api/reference)
- [OAuth Walkthrough](https://developers.hellosign.com/docs/guides/o-auth/walkthrough)
- [Events/Webhooks](https://developers.hellosign.com/docs/guides/events-and-callbacks/overview)
# Bitly

Bitly link management API for shortening, customizing, and tracking links.

## Base URL
`https://api-ssl.bitly.com/v4`

## Authentication
Bearer token via Authorization header. Get token from Bitly Settings > API.

```bash
curl -X GET "https://api-ssl.bitly.com/v4/user" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Core Endpoints

### Shorten Link (Simple)
```bash
curl -X POST "https://api-ssl.bitly.com/v4/shorten" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "long_url": "https://example.com/very-long-url",
    "domain": "bit.ly"
  }'
```

### Create Bitlink (Full Options)
```bash
curl -X POST "https://api-ssl.bitly.com/v4/bitlinks" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "long_url": "https://example.com/page",
    "domain": "bit.ly",
    "title": "My Link",
    "tags": ["marketing", "campaign"],
    "deeplinks": []
  }'
```

### Get Bitlink
```bash
curl -X GET "https://api-ssl.bitly.com/v4/bitlinks/bit.ly/abc123" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Update Bitlink
```bash
curl -X PATCH "https://api-ssl.bitly.com/v4/bitlinks/bit.ly/abc123" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### Delete Bitlink
```bash
curl -X DELETE "https://api-ssl.bitly.com/v4/bitlinks/bit.ly/abc123" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Get Click Summary
```bash
curl -X GET "https://api-ssl.bitly.com/v4/bitlinks/bit.ly/abc123/clicks/summary" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Get Clicks by Country
```bash
curl -X GET "https://api-ssl.bitly.com/v4/bitlinks/bit.ly/abc123/countries" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Rate Limits
- Free: 1,000 API calls/month, 10 links/month
- Paid plans: Higher limits based on tier
- 429 error: `MONTHLY_LIMIT_EXCEEDED`

## Gotchas
- Bitlink ID format: `domain/hash` (e.g., `bit.ly/abc123`)
- `group_guid` required for most operations (get from `/groups`)
- Custom domains (BSDs) require paid plan setup
- Can only delete unedited hash bitlinks
- Expiration available via `expiration_at` parameter
- Deep links for mobile app routing require additional setup
- QR codes available at separate endpoint

## Links
- [Docs](https://dev.bitly.com/)
- [API Reference](https://dev.bitly.com/api-reference)
- [Authentication](https://dev.bitly.com/docs/getting-started/authentication)
- [Rate Limits](https://dev.bitly.com/docs/getting-started/rate-limits)
# Dub

Dub.co link shortener API for creating and managing short links with analytics.

## Base URL
`https://api.dub.co`

## Authentication
API Key via Authorization header with Bearer token. Keys start with `dub_`.

```bash
curl -X GET "https://api.dub.co/links" \
  -H "Authorization: Bearer dub_xxxxxx"
```

## Core Endpoints

### Create Short Link
```bash
curl -X POST "https://api.dub.co/links" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/long-url",
    "domain": "dub.sh",
    "key": "my-custom-slug"
  }'
```

### Get Links
```bash
curl -X GET "https://api.dub.co/links" \
  -H "Authorization: Bearer {API_KEY}"
```

### Get Link by ID
```bash
curl -X GET "https://api.dub.co/links/{LINK_ID}" \
  -H "Authorization: Bearer {API_KEY}"
```

### Update Link
```bash
curl -X PATCH "https://api.dub.co/links/{LINK_ID}" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/new-destination"}'
```

### Delete Link
```bash
curl -X DELETE "https://api.dub.co/links/{LINK_ID}" \
  -H "Authorization: Bearer {API_KEY}"
```

### Get Analytics
```bash
curl -X GET "https://api.dub.co/analytics?domain=dub.sh&key=my-link&interval=30d" \
  -H "Authorization: Bearer {API_KEY}"
```

### Track Lead Event
```bash
curl -X POST "https://api.dub.co/track/lead" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "clickId": "click_xxxxx",
    "eventName": "Sign Up",
    "customerId": "user_123"
  }'
```

## Rate Limits
- Rate limited per workspace
- 429 error returned when exceeded
- Retry-After header indicates wait time

## Gotchas
- `key` is the custom slug/path (optional, auto-generated if omitted)
- `domain` defaults to dub.sh; custom domains require workspace setup
- Link IDs are prefixed (e.g., `lnk_xxxxx`)
- Analytics intervals: `1h`, `24h`, `7d`, `30d`, `90d`, `ytd`, `1y`, `all`
- QR codes auto-generated for each link
- Workspace slug required in some endpoints

## Links
- [Docs](https://dub.co/docs)
- [API Reference](https://dub.co/docs/api-reference/introduction)
- [SDKs](https://dub.co/docs/sdks/overview) (TypeScript, Python, Go, Ruby, PHP)
- [Authentication](https://dub.co/docs/api-reference/authentication)
