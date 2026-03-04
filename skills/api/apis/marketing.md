# Index

| API | Line |
|-----|------|
| Drift | 2 |
| Crisp | 108 |
| Front | 207 |
| Customer.io | 296 |
| Braze | 395 |
| Iterable | 509 |
| Klaviyo | 624 |

---

# Drift

Conversational marketing platform with chatbots, live chat, and meeting scheduling.

## Base URL
`https://driftapi.com`

## Authentication
OAuth 2.0 Authorization Code flow. Tokens obtained after user authorizes your app.

```bash
curl https://driftapi.com/contacts \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN"
```

### Token Exchange
```bash
# Exchange auth code for tokens
curl -X POST https://driftapi.com/oauth2/token \
  -d "client_id=$DRIFT_CLIENT_ID" \
  -d "client_secret=$DRIFT_CLIENT_SECRET" \
  -d "code=$AUTH_CODE" \
  -d "grant_type=authorization_code"
```

## Core Endpoints

### List Contacts
```bash
curl https://driftapi.com/contacts \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN"
```

### Get Contact
```bash
curl https://driftapi.com/contacts/123456 \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN"
```

### Create/Update Contact
```bash
curl -X POST https://driftapi.com/contacts \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "email": "customer@example.com",
      "name": "John Doe",
      "phone": "+15551234567"
    }
  }'
```

### List Conversations
```bash
curl "https://driftapi.com/conversations?status=open" \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN"
```

### Get Conversation Messages
```bash
curl https://driftapi.com/conversations/789/messages \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN"
```

### Send Message
```bash
curl -X POST https://driftapi.com/conversations/789/messages \
  -H "Authorization: Bearer $DRIFT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Thanks for your interest! How can I help?",
    "type": "chat"
  }'
```

## Rate Limits
- Standard rate limits apply (varies by endpoint)
- HTTP 429 when exceeded with `Retry-After` header
- Use webhooks for real-time updates instead of polling

## Gotchas
- **OAuth only** — no API keys for server-to-server auth
- Access tokens expire in 2 hours — use refresh tokens
- `orgId` in token response identifies the customer's organization
- Contact attributes are flexible key-value pairs
- Conversation `status`: `open`, `closed`, `pending`
- Webhooks recommended over polling for conversation updates
- Browser SDK (`drift.api`) for client-side widget control
- **Use TLS, not SSL** — SSL connections may be rejected

## Scopes
| Scope | Description |
|-------|-------------|
| contact_read | Read contacts |
| contact_write | Create/update contacts |
| conversation_read | Read conversations and messages |
| conversation_write | Send messages via bot |
| user_read | Read user data |
| gdpr_read | Data retrieval requests |
| gdpr_write | Data deletion requests |

## Links
- [Docs](https://devdocs.drift.com/)
- [Authentication](https://devdocs.drift.com/docs/authentication-and-scopes)
- [Webhook Events](https://devdocs.drift.com/docs/webhook-events-1)
# Crisp

Customer messaging platform with live chat, chatbot, and knowledge base.

## Base URL
`https://api.crisp.chat/v1`

## Authentication
HTTP Basic Auth with plugin token identifier and key. Requires `X-Crisp-Tier: plugin` header.

```bash
curl https://api.crisp.chat/v1/website/$WEBSITE_ID \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin"
```

Note: Tokens generated via Crisp Marketplace (marketplace.crisp.chat).

## Core Endpoints

### Get Website Info
```bash
curl https://api.crisp.chat/v1/website/$WEBSITE_ID \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin"
```

### List Conversations
```bash
curl "https://api.crisp.chat/v1/website/$WEBSITE_ID/conversations/1" \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin"
```

### Get Conversation
```bash
curl https://api.crisp.chat/v1/website/$WEBSITE_ID/conversation/$SESSION_ID \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin"
```

### Send Message
```bash
curl -X POST https://api.crisp.chat/v1/website/$WEBSITE_ID/conversation/$SESSION_ID/message \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "from": "operator",
    "origin": "chat",
    "content": "Hello! How can I help you today?"
  }'
```

### Create/Update People Profile
```bash
curl -X PUT https://api.crisp.chat/v1/website/$WEBSITE_ID/people/profile/$PEOPLE_ID \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "person": {"nickname": "John Doe"},
    "company": {"name": "Acme Corp"}
  }'
```

### Change Conversation State
```bash
curl -X PATCH https://api.crisp.chat/v1/website/$WEBSITE_ID/conversation/$SESSION_ID/state \
  -u "$CRISP_IDENTIFIER:$CRISP_KEY" \
  -H "X-Crisp-Tier: plugin" \
  -H "Content-Type: application/json" \
  -d '{"state": "resolved"}'
```

## Rate Limits
- **Plugin tokens:** Daily quota system (not per-minute)
- **User tokens:** Per-minute rate limits apply
- Plugin tokens bypass per-route limits but have daily caps
- Request quota increase via Marketplace dashboard
- HTTP 429 or 420 when exceeded
- Cached GET routes more permissive (check `Bloom-Status` header)

## Gotchas
- **Must include `X-Crisp-Tier: plugin` header** — auth fails without it
- Token keypair from Crisp Marketplace, not main Crisp app
- Website ID = your Crisp workspace identifier
- Session ID = conversation identifier (unique per visitor session)
- Conversation states: `pending`, `unresolved`, `resolved`
- Message `from`: `operator` (you) or `user` (visitor)
- People profiles separate from conversation sessions
- Plugin must be installed on each website you want to access

## Links
- [Docs](https://docs.crisp.chat/)
- [REST API Reference](https://docs.crisp.chat/references/rest-api/v1/)
- [Authentication Guide](https://docs.crisp.chat/guides/rest-api/authentication/)
# Front

Shared inbox platform for team email, collaboration, and customer communication.

## Base URL
`https://api2.frontapp.com`

## Authentication
Bearer token via API token or OAuth 2.0.

```bash
curl https://api2.frontapp.com/me \
  -H "Authorization: Bearer $FRONT_API_TOKEN" \
  -H "Accept: application/json"
```

## Core Endpoints

### List Conversations
```bash
curl "https://api2.frontapp.com/conversations?limit=25" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

### Get Conversation
```bash
curl https://api2.frontapp.com/conversations/cnv_abc123 \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

### Reply to Conversation
```bash
curl -X POST https://api2.frontapp.com/conversations/cnv_abc123/messages \
  -H "Authorization: Bearer $FRONT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "author_id": "tea_xyz789",
    "body": "Thanks for reaching out! Here is the answer...",
    "type": "reply"
  }'
```

### Create Contact
```bash
curl -X POST https://api2.frontapp.com/contacts \
  -H "Authorization: Bearer $FRONT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "handles": [{"source": "email", "handle": "customer@example.com"}],
    "name": "John Doe"
  }'
```

### Search Conversations
```bash
curl "https://api2.frontapp.com/conversations/search/query?q=subject:invoice" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

### Assign Conversation
```bash
curl -X PUT https://api2.frontapp.com/conversations/cnv_abc123/assignee \
  -H "Authorization: Bearer $FRONT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assignee_id": "tea_xyz789"}'
```

## Rate Limits
- **Starter:** 50 requests per minute
- **Professional:** 100 requests per minute
- **Enterprise:** 200 requests per minute
- **OAuth apps:** 120 rpm per company (separate from customer's limit)
- Tier 1 endpoints (analytics): 1 req/sec
- Tier 2 endpoints (messages): 5 req/sec per resource
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Gotchas
- ID prefixes indicate type: `cnv_` (conversation), `tea_` (teammate), `inb_` (inbox)
- Conversations contain Messages (the individual emails/chats)
- Search endpoint has proportional rate limit (40% of global limit)
- `author_id` required for replies — use teammate ID
- Contact handles = email addresses, phone numbers, etc.
- Burst rate limits (`X-RateLimit-Burst-Limit`) provide extra allowance for spikes
- Comments vs Replies: comments are internal, replies go to customer

## Links
- [Docs](https://dev.frontapp.com/)
- [API Reference](https://dev.frontapp.com/reference/introduction)
- [Rate Limits](https://dev.frontapp.com/docs/rate-limiting)
# Customer.io

Customer messaging platform for behavioral emails, push, SMS, and in-app messages.

## Base URLs
- **Track API:** `https://track.customer.io/api/v1`
- **App API:** `https://api.customer.io/v1`

## Authentication
Track API uses Basic Auth with Site ID and API Key.

```bash
# Track API (for sending data)
curl "https://track.customer.io/api/v1/customers/user-123" \
  -u "SITE_ID:API_KEY"

# App API (for campaigns, exports)
curl "https://api.customer.io/v1/campaigns" \
  -H "Authorization: Bearer APP_API_KEY"
```

## Core Endpoints

### Identify Customer (Track API)
```bash
curl -X PUT "https://track.customer.io/api/v1/customers/user-123" \
  -u "SITE_ID:API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "created_at": 1704067200,
    "name": "John Doe",
    "plan": "premium"
  }'
```

### Track Event (Track API)
```bash
curl -X POST "https://track.customer.io/api/v1/customers/user-123/events" \
  -u "SITE_ID:API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "purchase",
    "data": {
      "product_id": "abc123",
      "price": 99.99
    }
  }'
```

### Delete Customer (Track API)
```bash
curl -X DELETE "https://track.customer.io/api/v1/customers/user-123" \
  -u "SITE_ID:API_KEY"
```

### Add Device Token (Track API)
```bash
curl -X PUT "https://track.customer.io/api/v1/customers/user-123/devices" \
  -u "SITE_ID:API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device": {
      "id": "device-token",
      "platform": "ios"
    }
  }'
```

### Send Transactional Email (App API)
```bash
curl -X POST "https://api.customer.io/v1/send/email" \
  -H "Authorization: Bearer APP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "transactional_message_id": "1",
    "to": "user@example.com",
    "identifiers": {"id": "user-123"},
    "message_data": {"name": "John"}
  }'
```

## Rate Limits
- Track API: 100 requests/second per workspace
- App API: 10 requests/second for most endpoints
- Batch operations: 1,000 items per request

## Gotchas
- Track API and App API use DIFFERENT authentication methods
- `created_at` must be Unix timestamp (seconds), not milliseconds
- Customer IDs are strings—your internal user IDs
- Events require customer to exist first (identify before tracking)
- `anonymous_id` supported for users without accounts
- Timestamps sent as integers, not ISO strings

## Links
- [Track API Docs](https://docs.customer.io/api/track/)
- [App API Docs](https://docs.customer.io/api/app/)
- [Dashboard](https://fly.customer.io)
# Braze

Customer engagement platform for push, email, SMS, in-app messaging, and content cards.

## Base URL
Instance-specific. Check your dashboard for the correct endpoint.

Common endpoints:
- US-01: `https://rest.iad-01.braze.com`
- US-03: `https://rest.iad-03.braze.com`
- EU-01: `https://rest.fra-01.braze.eu`

## Authentication
API Key in `Authorization` header with `Bearer` prefix.

```bash
curl "https://rest.iad-01.braze.com/users/export/ids" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

## Core Endpoints

### Track User Attributes
```bash
curl -X POST "https://rest.iad-01.braze.com/users/track" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": [{
      "external_id": "user-123",
      "first_name": "John",
      "email": "john@example.com",
      "custom_attribute": "value"
    }]
  }'
```

### Track Events
```bash
curl -X POST "https://rest.iad-01.braze.com/users/track" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "external_id": "user-123",
      "name": "completed_purchase",
      "time": "2024-01-15T10:30:00Z",
      "properties": {"product_id": "abc123"}
    }]
  }'
```

### Send Messages
```bash
curl -X POST "https://rest.iad-01.braze.com/messages/send" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_ids": ["user-123"],
    "messages": {
      "email": {
        "app_id": "YOUR_APP_ID",
        "from": "noreply@company.com",
        "subject": "Hello",
        "body": "<html>Your message here</html>"
      }
    }
  }'
```

### Send Campaign
```bash
curl -X POST "https://rest.iad-01.braze.com/campaigns/trigger/send" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "CAMPAIGN_ID",
    "recipients": [{
      "external_user_id": "user-123",
      "trigger_properties": {"name": "John"}
    }]
  }'
```

### Export User Data
```bash
curl -X POST "https://rest.iad-01.braze.com/users/export/ids" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "external_ids": ["user-123"],
    "fields_to_export": ["email", "custom_attributes"]
  }'
```

## Rate Limits
- Default: 250,000 requests/hour per workspace
- `/users/track`: 50,000 requests/minute
- Batch size: 75 attributes/events/purchases per request
- Export endpoints have lower limits—check docs

## Gotchas
- REST endpoint is instance-specific—wrong URL = 401 error
- `external_id` is YOUR user ID, `braze_id` is Braze's internal ID
- Timestamps must be ISO 8601 format with timezone
- API keys have specific permissions—create dedicated keys per use case
- `/users/track` batches attributes, events, and purchases together
- IP allowlisting available for API keys (recommended for security)
- Subscription status changes require specific endpoints

## Links
- [Docs](https://www.braze.com/docs/api/basics/)
- [Dashboard](https://dashboard.braze.com)
# Iterable

Marketing automation platform for cross-channel campaigns (email, push, SMS, in-app).

## Base URL
`https://api.iterable.com/api`

## Authentication
API Key in header.

```bash
curl "https://api.iterable.com/api/users/user@example.com" \
  -H "Api-Key: YOUR_API_KEY"
```

## Core Endpoints

### Update User
```bash
curl -X POST "https://api.iterable.com/api/users/update" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "userId": "user-123",
    "dataFields": {
      "firstName": "John",
      "lastName": "Doe",
      "plan": "premium"
    }
  }'
```

### Track Event
```bash
curl -X POST "https://api.iterable.com/api/events/track" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "eventName": "purchase",
    "dataFields": {
      "productId": "abc123",
      "price": 99.99
    }
  }'
```

### Send Email
```bash
curl -X POST "https://api.iterable.com/api/email/target" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipientEmail": "user@example.com",
    "campaignId": 12345,
    "dataFields": {
      "name": "John"
    }
  }'
```

### Trigger Workflow
```bash
curl -X POST "https://api.iterable.com/api/workflows/triggerWorkflow" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": 12345,
    "email": "user@example.com",
    "dataFields": {
      "orderId": "order-789"
    }
  }'
```

### Register Push Token
```bash
curl -X POST "https://api.iterable.com/api/users/registerDeviceToken" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "device": {
      "token": "device-token",
      "platform": "APNS",
      "applicationName": "MyApp"
    }
  }'
```

### Get User
```bash
curl "https://api.iterable.com/api/users/user@example.com" \
  -H "Api-Key: YOUR_API_KEY"
```

## Rate Limits
- Standard: 500 requests/second per project
- Bulk endpoints: Lower limits, check specific endpoint docs
- `/users/update`: 500/second
- `/events/track`: 2,000/second

## Gotchas
- Users can be identified by `email` OR `userId`, but must pick one consistently
- If using both email and userId, they must be linked first
- `dataFields` is the custom attributes object—use this for all custom data
- Campaign/workflow IDs are integers, not strings
- API key header is `Api-Key`, not `Authorization`
- Timestamps expected as Unix milliseconds
- Bulk endpoints have different response formats

## Links
- [Docs](https://api.iterable.com/api/docs)
- [Dashboard](https://app.iterable.com)
# Klaviyo

Email and SMS marketing automation platform with advanced segmentation.

## Base URL
`https://a.klaviyo.com/api`

## Authentication
API Key in header with `Klaviyo-API-Key` prefix.

```bash
curl "https://a.klaviyo.com/api/profiles/" \
  -H "Authorization: Klaviyo-API-Key YOUR_PRIVATE_API_KEY" \
  -H "revision: 2024-02-15"
```

## Core Endpoints

### Create/Update Profile
```bash
curl -X POST "https://a.klaviyo.com/api/profiles/" \
  -H "Authorization: Klaviyo-API-Key YOUR_PRIVATE_API_KEY" \
  -H "revision: 2024-02-15" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "profile",
      "attributes": {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "properties": {
          "plan": "premium"
        }
      }
    }
  }'
```

### Track Event
```bash
curl -X POST "https://a.klaviyo.com/api/events/" \
  -H "Authorization: Klaviyo-API-Key YOUR_PRIVATE_API_KEY" \
  -H "revision: 2024-02-15" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "event",
      "attributes": {
        "metric": {"data": {"type": "metric", "attributes": {"name": "Placed Order"}}},
        "profile": {"data": {"type": "profile", "attributes": {"email": "user@example.com"}}},
        "properties": {
          "OrderId": "12345",
          "Value": 99.99
        }
      }
    }
  }'
```

### Get Profile
```bash
curl "https://a.klaviyo.com/api/profiles/PROFILE_ID/" \
  -H "Authorization: Klaviyo-API-Key YOUR_PRIVATE_API_KEY" \
  -H "revision: 2024-02-15"
```

### Subscribe to List
```bash
curl -X POST "https://a.klaviyo.com/api/lists/LIST_ID/relationships/profiles/" \
  -H "Authorization: Klaviyo-API-Key YOUR_PRIVATE_API_KEY" \
  -H "revision: 2024-02-15" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"type": "profile", "id": "PROFILE_ID"}
    ]
  }'
```

### Create Campaign
```bash
curl -X POST "https://a.klaviyo.com/api/campaigns/" \
  -H "Authorization: Klaviyo-API-Key YOUR_PRIVATE_API_KEY" \
  -H "revision: 2024-02-15" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "type": "campaign",
      "attributes": {
        "name": "Welcome Campaign",
        "channel": "email",
        "audiences": {
          "included": ["LIST_ID"]
        }
      }
    }
  }'
```

## Rate Limits
- Standard: Varies by endpoint (10-75 requests/second)
- Burst limit: 3x standard for short periods
- Rate limit headers returned in response
- `/events/` endpoint: 350/second

## Gotchas
- API uses JSON:API format—`data`, `type`, `attributes` structure required
- `revision` header REQUIRED on all requests (date format: `YYYY-MM-DD`)
- Private API key for server-side, public key for client-side tracking
- Profile ID is Klaviyo's internal ID, not your user ID
- Use `/api/profiles/?filter=equals(email,"...")` to lookup by email
- Events create profiles automatically if they don't exist
- Lists vs Segments: Lists are static, Segments are dynamic

## Links
- [Docs](https://developers.klaviyo.com/en/reference/api_overview)
- [Dashboard](https://www.klaviyo.com/dashboard)
