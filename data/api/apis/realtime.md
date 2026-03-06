# Index

| API | Line |
|-----|------|
| Stream Chat | 105 |
| Pusher Channels | 223 |
| Ably | 303 |
| OneSignal | 375 |
| Courier | 438 |
| Knock | 531 |
| Novu | 611 |

---

# Sendbird

Chat and messaging API for in-app communication with channels, messages, and moderation.

## Base URL
`https://api-{APPLICATION_ID}.sendbird.com/v3`

Get your Application ID from Sendbird Dashboard.

## Authentication
API Token in header (Master or Secondary token).

```bash
curl "https://api-APP_ID.sendbird.com/v3/users" \
  -H "Api-Token: YOUR_API_TOKEN" \
  -H "Content-Type: application/json"
```

## Core Endpoints

### Create User
```bash
curl -X POST "https://api-APP_ID.sendbird.com/v3/users" \
  -H "Api-Token: YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "nickname": "John Doe",
    "profile_url": "https://example.com/avatar.jpg"
  }'
```

### Create Group Channel
```bash
curl -X POST "https://api-APP_ID.sendbird.com/v3/group_channels" \
  -H "Api-Token: YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sales Team",
    "user_ids": ["user-1", "user-2", "user-3"],
    "is_distinct": true
  }'
```

### Send Message
```bash
curl -X POST "https://api-APP_ID.sendbird.com/v3/group_channels/CHANNEL_URL/messages" \
  -H "Api-Token: YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "MESG",
    "user_id": "user-123",
    "message": "Hello everyone!"
  }'
```

### List Messages
```bash
curl "https://api-APP_ID.sendbird.com/v3/group_channels/CHANNEL_URL/messages?message_ts=0" \
  -H "Api-Token: YOUR_API_TOKEN"
```

### Update User
```bash
curl -X PUT "https://api-APP_ID.sendbird.com/v3/users/user-123" \
  -H "Api-Token: YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "John D.",
    "metadata": {"role": "admin"}
  }'
```

### Ban User from Channel
```bash
curl -X POST "https://api-APP_ID.sendbird.com/v3/group_channels/CHANNEL_URL/ban" \
  -H "Api-Token: YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "bad-user",
    "seconds": 86400,
    "description": "Violated community guidelines"
  }'
```

## Rate Limits
- Default: Varies by plan and endpoint
- Free tier: ~100 requests/second
- Message sends: Check plan limits
- Rate limit headers in response: `X-Ratelimit-Remaining`

## Gotchas
- API Token goes in `Api-Token` header, NOT `Authorization`
- Channel URLs are URL-encoded—handle special characters
- `message_ts` parameter required for listing messages (use 0 for all)
- User IDs must be unique within app—use your internal IDs
- Master token has full access; Secondary tokens can be scoped
- DON'T use Platform API from client apps—use Chat SDKs instead
- File uploads require `multipart/form-data` with different Content-Type

## Links
- [Docs](https://sendbird.com/docs/chat/platform-api/v3/overview)
- [Dashboard](https://dashboard.sendbird.com)
# Stream Chat

Scalable chat API with channels, threads, reactions, and activity feeds.

## Base URL
`https://chat.stream-io-api.com`

## Authentication
Server-side uses API Key + Secret to generate JWT tokens for users.

```bash
# Server-side requests use query params
curl "https://chat.stream-io-api.com/channels?api_key=YOUR_API_KEY" \
  -H "Authorization: YOUR_SERVER_TOKEN" \
  -H "stream-auth-type: jwt"
```

## Core Endpoints

### Create User Token (Server-side)
```python
# Python SDK example - generate JWT for client auth
import stream_chat

server_client = stream_chat.StreamChat(
    api_key="YOUR_API_KEY", 
    api_secret="YOUR_API_SECRET"
)
token = server_client.create_token("user-123")
```

### Upsert Users
```bash
curl -X POST "https://chat.stream-io-api.com/users?api_key=YOUR_API_KEY" \
  -H "Authorization: YOUR_SERVER_TOKEN" \
  -H "stream-auth-type: jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "users": {
      "user-123": {
        "id": "user-123",
        "name": "John Doe",
        "image": "https://example.com/avatar.jpg"
      }
    }
  }'
```

### Create Channel
```bash
curl -X POST "https://chat.stream-io-api.com/channels/messaging/general?api_key=YOUR_API_KEY" \
  -H "Authorization: YOUR_SERVER_TOKEN" \
  -H "stream-auth-type: jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "name": "General",
      "members": ["user-1", "user-2"],
      "created_by_id": "user-1"
    }
  }'
```

### Send Message
```bash
curl -X POST "https://chat.stream-io-api.com/channels/messaging/general/message?api_key=YOUR_API_KEY" \
  -H "Authorization: YOUR_SERVER_TOKEN" \
  -H "stream-auth-type: jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "text": "Hello everyone!",
      "user_id": "user-123"
    }
  }'
```

### Query Channels
```bash
curl -X POST "https://chat.stream-io-api.com/channels?api_key=YOUR_API_KEY" \
  -H "Authorization: YOUR_SERVER_TOKEN" \
  -H "stream-auth-type: jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "filter_conditions": {"members": {"$in": ["user-123"]}},
    "sort": [{"field": "last_message_at", "direction": -1}],
    "user_id": "user-123"
  }'
```

### Revoke User Token
```bash
curl -X POST "https://chat.stream-io-api.com/users/user-123/revoke?api_key=YOUR_API_KEY" \
  -H "Authorization: YOUR_SERVER_TOKEN" \
  -H "stream-auth-type: jwt" \
  -H "Content-Type: application/json" \
  -d '{"revoke_tokens_issued_before": "2024-01-15T00:00:00Z"}'
```

## Rate Limits
- Default: 60 requests/minute for most endpoints
- Messages: Higher limits based on plan
- Server-side: Generally higher than client-side
- Check `X-Ratelimit-Remaining` header

## Gotchas
- API Key is public (used client-side), API Secret is private (server-only)
- Tokens must include `iat` (issued at) claim for revocation to work
- Channel type (e.g., `messaging`) is part of URL path
- `user_id` required on most requests to identify the acting user
- Development tokens work only with "Disable Auth Checks" enabled
- Use SDKs for client apps—REST API mainly for server-side operations
- Channel IDs must be unique within a channel type

## Links
- [Docs](https://getstream.io/chat/docs/)
- [REST API Spec](https://getstream.github.io/protocol/?urls.primaryName=Chat)
- [Dashboard](https://getstream.io/dashboard)
# Pusher Channels

Realtime messaging infrastructure for websocket-based pub/sub communication.

## Base URL
`https://api-{CLUSTER}.pusher.com/apps/{APP_ID}`

Replace `{CLUSTER}` with your app's cluster (e.g., `mt1`, `eu`, `ap1`).

## Authentication
HMAC SHA256 signature-based authentication. All requests require signed query parameters.

```bash
# Parameters required on every request:
# auth_key, auth_timestamp, auth_version, auth_signature
# POST requests also need: body_md5

curl -X POST "https://api-mt1.pusher.com/apps/APP_ID/events?\
auth_key=KEY&auth_timestamp=TIMESTAMP&auth_version=1.0&\
body_md5=MD5&auth_signature=SIGNATURE" \
  -H "Content-Type: application/json" \
  -d '{"name":"my-event","channels":["my-channel"],"data":"{\"message\":\"hello\"}"}'
```

## Core Endpoints

### Trigger Event
```bash
# POST /apps/{app_id}/events
curl -X POST "https://api-mt1.pusher.com/apps/APP_ID/events" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-event",
    "channels": ["my-channel"],
    "data": "{\"message\": \"Hello World\"}"
  }'
```

### Batch Trigger Events
```bash
# POST /apps/{app_id}/batch_events
curl -X POST "https://api-mt1.pusher.com/apps/APP_ID/batch_events" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": [
      {"channel": "channel-1", "name": "event-1", "data": "{}"},
      {"channel": "channel-2", "name": "event-2", "data": "{}"}
    ]
  }'
```

### Get Channel Info
```bash
# GET /apps/{app_id}/channels/{channel_name}
curl "https://api-mt1.pusher.com/apps/APP_ID/channels/presence-channel?info=user_count"
```

### Get Users in Presence Channel
```bash
# GET /apps/{app_id}/channels/{channel_name}/users
curl "https://api-mt1.pusher.com/apps/APP_ID/channels/presence-channel/users"
```

## Rate Limits
- Event data: Max 10KB per message
- Channels per request: Max 100
- Batch events: Up to 10 per request (multi-tenant clusters)
- Timestamp must be within 600 seconds of server time

## Gotchas
- `data` field must be a JSON-encoded STRING, not raw JSON object
- Signature calculation requires specific string format with newlines
- `subscription_count` not available by default—enable in App Settings
- Presence channels require `presence-` prefix
- Private channels require `private-` prefix
- HTTP Keep-Alive supported for better throughput

## Links
- [Docs](https://pusher.com/docs/channels/library_auth_reference/rest-api/)
- [Dashboard](https://dashboard.pusher.com)
# Ably

Realtime infrastructure for pub/sub messaging, presence, and history.

## Base URL
`https://rest.ably.io`

## Authentication
Basic Auth with API key, or Token Auth for client-side.

```bash
# Basic Auth (API key as username:password)
curl "https://rest.ably.io/channels/my-channel/messages" \
  -u "YOUR_API_KEY"

# Or with Authorization header
curl "https://rest.ably.io/channels/my-channel/messages" \
  -H "Authorization: Basic BASE64_ENCODED_KEY"
```

## Core Endpoints

### Publish Message
```bash
curl -X POST "https://rest.ably.io/channels/my-channel/messages" \
  -u "YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "greeting", "data": "Hello World"}'
```

### Get Message History
```bash
curl "https://rest.ably.io/channels/my-channel/messages" \
  -u "YOUR_API_KEY"
```

### Get Presence
```bash
curl "https://rest.ably.io/channels/my-channel/presence" \
  -u "YOUR_API_KEY"
```

### Get Channel Status
```bash
curl "https://rest.ably.io/channels/my-channel" \
  -u "YOUR_API_KEY"
```

### Request Token
```bash
curl -X POST "https://rest.ably.io/keys/KEY_NAME/requestToken" \
  -u "YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ttl": 3600000, "capability": "{\"*\":[\"*\"]}"}'
```

## Rate Limits
- Default: 100 requests/second per account
- Message size: 64KB default, 256KB max
- Batch publish: Up to 100 messages per request

## Gotchas
- API key format is `keyName:keySecret`—split at first colon for user:pass auth
- Supports JSON, MessagePack, and form-encoded request bodies
- Use `X-Ably-Version: 1.2` header for explicit API versioning
- Paginated responses use RFC 5988 Link headers
- Timestamps must be in milliseconds since epoch
- Channel names are case-sensitive

## Links
- [Docs](https://ably.com/docs/api/rest-api)
- [Dashboard](https://ably.com/dashboard)
# OneSignal

Multi-channel push notification service supporting mobile, web, email, and SMS.

## Base URL
`https://api.onesignal.com`

## Authentication
REST API Key in header. Get your key from Settings > Keys & IDs in the dashboard.

```bash
curl -X POST "https://api.onesignal.com/notifications" \
  -H "Authorization: Basic YOUR_REST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "YOUR_APP_ID", "contents": {"en": "Hello"}}'
```

## Core Endpoints

### Create Notification
```bash
curl -X POST "https://api.onesignal.com/notifications" \
  -H "Authorization: Basic YOUR_REST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "YOUR_APP_ID",
    "contents": {"en": "Hello World"},
    "included_segments": ["Subscribed Users"]
  }'
```

### View Notification
```bash
curl "https://api.onesignal.com/notifications/NOTIFICATION_ID?app_id=YOUR_APP_ID" \
  -H "Authorization: Basic YOUR_REST_API_KEY"
```

### Create User/Subscription
```bash
curl -X POST "https://api.onesignal.com/apps/YOUR_APP_ID/users" \
  -H "Authorization: Basic YOUR_REST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "identity": {"external_id": "user123"},
    "subscriptions": [{"type": "Email", "token": "user@example.com"}]
  }'
```

## Rate Limits
- Default: No strict rate limits, but large sends are throttled
- Batch sends: Up to 20,000 recipients per request
- Recommended: Use segments for large audiences

## Gotchas
- `include_aliases`, `included_segments`, and `filters` are mutually exclusive—use only one targeting method per request
- Event data limited to 10KB per notification
- `app_id` required in body for POST requests, in query string for GET
- Email/SMS requires separate channel setup in dashboard
- Filters limited to 200 entries per request

## Links
- [Docs](https://documentation.onesignal.com/reference)
- [Dashboard](https://dashboard.onesignal.com)
# Courier

Notification orchestration platform for multi-channel delivery with routing and templates.

## Base URL
`https://api.courier.com`

## Authentication
Bearer token with API key.

```bash
curl "https://api.courier.com/profiles/user-123" \
  -H "Authorization: Bearer pk_prod_YOUR_API_KEY"
```

## Core Endpoints

### Send Message
```bash
curl -X POST "https://api.courier.com/send" \
  -H "Authorization: Bearer pk_prod_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "to": {
        "email": "user@example.com"
      },
      "template": "TEMPLATE_ID",
      "data": {
        "name": "John"
      }
    }
  }'
```

### Send to User Profile
```bash
curl -X POST "https://api.courier.com/send" \
  -H "Authorization: Bearer pk_prod_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "to": {
        "user_id": "user-123"
      },
      "template": "welcome-notification"
    }
  }'
```

### Create/Update Profile
```bash
curl -X POST "https://api.courier.com/profiles/user-123" \
  -H "Authorization: Bearer pk_prod_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "email": "user@example.com",
      "phone_number": "+15551234567",
      "name": "John Doe"
    }
  }'
```

### Get Message Status
```bash
curl "https://api.courier.com/messages/MESSAGE_ID" \
  -H "Authorization: Bearer pk_prod_YOUR_API_KEY"
```

### List User Preferences
```bash
curl "https://api.courier.com/users/user-123/preferences" \
  -H "Authorization: Bearer pk_prod_YOUR_API_KEY"
```

## Rate Limits
- Standard: 20,000 requests/minute
- Send endpoint: 10,000 messages/minute
- Bulk send: 1,000 recipients per request

## Gotchas
- Templates must be created in Courier Studio before sending
- `template` can be template ID or notification ID
- Use `routing` object to specify channel order/priority
- Profile `user_id` is your internal ID, not Courier's
- Test keys start with `pk_test_`, prod with `pk_prod_`
- Idempotency supported via `Idempotency-Key` header
- `content` object can replace `template` for inline content

## Links
- [Docs](https://www.courier.com/docs/reference/)
- [Studio](https://app.courier.com)
# Knock

Notification infrastructure for in-app, email, push, SMS, and Slack.

## Base URL
`https://api.knock.app/v1`

## Authentication
Bearer token with secret API key.

```bash
curl "https://api.knock.app/v1/users/user-123" \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY"
```

## Core Endpoints

### Trigger Workflow
```bash
curl -X POST "https://api.knock.app/v1/workflows/welcome-email/trigger" \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user-123"],
    "data": {
      "name": "John",
      "welcome_message": "Welcome to our app!"
    }
  }'
```

### Identify User
```bash
curl -X PUT "https://api.knock.app/v1/users/user-123" \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

### Get User Feed
```bash
curl "https://api.knock.app/v1/users/user-123/feeds/in-app-feed" \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY"
```

### Mark Notifications as Read
```bash
curl -X POST "https://api.knock.app/v1/users/user-123/feeds/in-app-feed/mark_as_read" \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message_ids": ["msg-1", "msg-2"]}'
```

### Set Channel Data (Push Tokens)
```bash
curl -X PUT "https://api.knock.app/v1/users/user-123/channel_data/apns" \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tokens": ["device-token-123"]}'
```

## Rate Limits
- Standard: 1,000 requests/minute per environment
- Workflow triggers: 10,000/minute
- Bulk operations: 1,000 recipients per request

## Gotchas
- Use `sk_test_` keys for development, `sk_live_` for production
- Workflows must be created in dashboard before triggering via API
- User IDs are strings—use your internal user IDs
- `recipients` can be user IDs, objects, or object references
- Feed IDs are configured in dashboard (e.g., `in-app-feed`)
- Idempotency key header supported: `Idempotency-Key`

## Links
- [Docs](https://docs.knock.app/reference)
- [Dashboard](https://dashboard.knock.app)
# Novu

Open-source notification infrastructure for in-app, email, SMS, push, and chat.

## Base URL
`https://api.novu.co/v1`

EU Region: `https://eu.api.novu.co/v1`

## Authentication
API Key in Authorization header with `ApiKey` prefix.

```bash
curl "https://api.novu.co/v1/subscribers" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

## Core Endpoints

### Trigger Workflow Event
```bash
curl -X POST "https://api.novu.co/v1/events/trigger" \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "workflow-identifier",
    "to": {
      "subscriberId": "user-123",
      "email": "user@example.com"
    },
    "payload": {
      "name": "John",
      "orderNumber": "12345"
    }
  }'
```

### Bulk Trigger
```bash
curl -X POST "https://api.novu.co/v1/events/trigger/bulk" \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {"name": "workflow-id", "to": "user-1", "payload": {}},
      {"name": "workflow-id", "to": "user-2", "payload": {}}
    ]
  }'
```

### Create Subscriber
```bash
curl -X POST "https://api.novu.co/v1/subscribers" \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "subscriberId": "user-123",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
  }'
```

### Get Subscriber Preferences
```bash
curl "https://api.novu.co/v1/subscribers/user-123/preferences" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

### Update Subscriber Preferences
```bash
curl -X PATCH "https://api.novu.co/v1/subscribers/user-123/preferences" \
  -H "Authorization: ApiKey YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": {"type": "email", "enabled": false}
  }'
```

## Rate Limits
- Standard: 300 requests/minute
- Trigger events: 5,000/minute
- Bulk operations: 100 events per bulk request

## Gotchas
- Workflow must exist in dashboard before triggering
- `subscriberId` is YOUR user ID, not Novu's internal ID
- `to` field can be string (subscriberId), object, or array (max 100 recipients)
- Use `transactionId` for idempotent triggers to prevent duplicates
- API key header format: `Authorization: ApiKey {key}` (not Bearer!)
- Server-side only—CORS blocked for client-side requests

## Links
- [Docs](https://docs.novu.co/api-reference/overview)
- [Dashboard](https://dashboard.novu.co)
