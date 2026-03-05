# Index

| API | Line |
|-----|------|
| Intercom | 2 |
| Zendesk | 100 |
| Freshdesk | 191 |
| Help Scout | 274 |

---

# Intercom

## Base URL
```
https://api.intercom.io
```

## Authentication
```bash
curl https://api.intercom.io/me \
  -H "Authorization: Bearer $INTERCOM_TOKEN" \
  -H "Accept: application/json"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /contacts | GET | List contacts |
| /contacts | POST | Create contact |
| /conversations | GET | List conversations |
| /conversations/:id/reply | POST | Reply to conversation |
| /messages | POST | Send message |

## Quick Examples

### List Contacts
```bash
curl "https://api.intercom.io/contacts" \
  -H "Authorization: Bearer $INTERCOM_TOKEN" \
  -H "Accept: application/json"
```

### Create Contact
```bash
curl -X POST "https://api.intercom.io/contacts" \
  -H "Authorization: Bearer $INTERCOM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "email": "user@example.com",
    "name": "John Doe",
    "custom_attributes": {
      "plan": "premium"
    }
  }'
```

### Search Contacts
```bash
curl -X POST "https://api.intercom.io/contacts/search" \
  -H "Authorization: Bearer $INTERCOM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "field": "email",
      "operator": "=",
      "value": "user@example.com"
    }
  }'
```

### Reply to Conversation
```bash
curl -X POST "https://api.intercom.io/conversations/$CONVO_ID/reply" \
  -H "Authorization: Bearer $INTERCOM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "comment",
    "type": "admin",
    "admin_id": "ADMIN_ID",
    "body": "Thanks for reaching out!"
  }'
```

### Send In-App Message
```bash
curl -X POST "https://api.intercom.io/messages" \
  -H "Authorization: Bearer $INTERCOM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "inapp",
    "body": "Hello!",
    "from": {"type": "admin", "id": "ADMIN_ID"},
    "to": {"type": "user", "id": "USER_ID"}
  }'
```

## Common Traps

- Contacts = users/leads (unified model)
- Role: "user" (known) or "lead" (anonymous)
- custom_attributes must be created in Intercom first
- Conversations have parts (messages)
- Rate limit: varies by plan

## Official Docs
https://developers.intercom.com/docs/references/rest-api/api.intercom.io/
# Zendesk

## Base URL
```
https://{subdomain}.zendesk.com/api/v2
```

## Authentication
```bash
# API Token
curl "https://{subdomain}.zendesk.com/api/v2/tickets.json" \
  -u "email@example.com/token:$ZENDESK_API_TOKEN"

# OAuth
curl "https://{subdomain}.zendesk.com/api/v2/tickets.json" \
  -H "Authorization: Bearer $ZENDESK_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /tickets | GET | List tickets |
| /tickets | POST | Create ticket |
| /tickets/:id | PUT | Update ticket |
| /users | GET | List users |
| /search | GET | Search |

## Quick Examples

### List Tickets
```bash
curl "https://{subdomain}.zendesk.com/api/v2/tickets.json?sort_by=created_at&sort_order=desc" \
  -u "email/token:$ZENDESK_API_TOKEN"
```

### Create Ticket
```bash
curl -X POST "https://{subdomain}.zendesk.com/api/v2/tickets.json" \
  -u "email/token:$ZENDESK_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "subject": "Help needed",
      "comment": {"body": "I need assistance with..."},
      "requester": {"email": "customer@example.com"},
      "priority": "normal"
    }
  }'
```

### Update Ticket
```bash
curl -X PUT "https://{subdomain}.zendesk.com/api/v2/tickets/$TICKET_ID.json" \
  -u "email/token:$ZENDESK_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket": {
      "status": "solved",
      "comment": {"body": "Issue resolved", "public": true}
    }
  }'
```

### Search
```bash
curl "https://{subdomain}.zendesk.com/api/v2/search.json?query=type:ticket+status:open" \
  -u "email/token:$ZENDESK_API_TOKEN"
```

## Ticket Status Values

| Status | Meaning |
|--------|---------|
| new | Not assigned |
| open | Assigned, working |
| pending | Waiting on customer |
| hold | On hold |
| solved | Resolved |
| closed | Archived |

## Common Traps

- Auth format: `email/token:API_TOKEN` (note the /token)
- Wrap data in object (`ticket`, `user`, etc.)
- Endpoints end in `.json`
- Pagination via `page` and `per_page`
- Rate limit: 400 requests/minute (Team), higher on Enterprise

## Official Docs
https://developer.zendesk.com/api-reference/
# Freshdesk

Support ticketing system with multi-channel support, automation, and knowledge base.

## Base URL
`https://yourdomain.freshdesk.com/api/v2`

Replace `yourdomain` with your Freshdesk subdomain.

## Authentication
HTTP Basic Auth with API key as username and `X` as password.

```bash
curl https://yourdomain.freshdesk.com/api/v2/tickets \
  -u "$FRESHDESK_API_KEY:X"

# Note: password is literally "X"
```

## Core Endpoints

### List Tickets
```bash
curl "https://yourdomain.freshdesk.com/api/v2/tickets?per_page=30&page=1" \
  -u "$FRESHDESK_API_KEY:X"
```

### Create Ticket
```bash
curl -X POST https://yourdomain.freshdesk.com/api/v2/tickets \
  -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Support Request",
    "description": "Customer needs help with...",
    "email": "customer@example.com",
    "priority": 2,
    "status": 2
  }'
```

### Reply to Ticket
```bash
curl -X POST https://yourdomain.freshdesk.com/api/v2/tickets/123/reply \
  -u "$FRESHDESK_API_KEY:X" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Thanks for reaching out! Here is the solution..."
  }'
```

### Get Contact
```bash
curl https://yourdomain.freshdesk.com/api/v2/contacts/456 \
  -u "$FRESHDESK_API_KEY:X"
```

### Search Tickets
```bash
curl "https://yourdomain.freshdesk.com/api/v2/search/tickets?query=\"status:2 AND priority:3\"" \
  -u "$FRESHDESK_API_KEY:X"
```

## Rate Limits
- **Sprout/Blossom:** 50 requests per minute
- **Garden:** 100 requests per minute
- **Estate:** 200 requests per minute
- **Forest:** 400 requests per minute
- Headers: `X-RateLimit-Total`, `X-RateLimit-Remaining`, `X-RateLimit-Used-CurrentRequest`

## Gotchas
- Password in Basic Auth is literally the letter `X`, not empty
- Status codes: 2=Open, 3=Pending, 4=Resolved, 5=Closed
- Priority codes: 1=Low, 2=Medium, 3=High, 4=Urgent
- Search query uses Freshdesk Query Language (FQL), must be URL-encoded
- Conversations (ticket replies) are separate from tickets
- Custom fields use format `custom_fields.cf_fieldname`
- File attachments require multipart/form-data

## Links
- [Docs](https://developers.freshdesk.com/)
- [API Reference](https://developers.freshdesk.com/api/)
- [Solution Articles API](https://developers.freshdesk.com/api/#solution_article)
# Help Scout

Customer support platform with shared inbox, knowledge base, and customer profiles.

## Base URL
`https://api.helpscout.net/v2`

## Authentication
OAuth 2.0 with Authorization Code or Client Credentials flow.

```bash
# Get access token (Client Credentials)
curl -X POST https://api.helpscout.net/v2/oauth2/token \
  -d "grant_type=client_credentials" \
  -d "client_id=$HELPSCOUT_APP_ID" \
  -d "client_secret=$HELPSCOUT_APP_SECRET"

# Use token
curl https://api.helpscout.net/v2/users/me \
  -H "Authorization: Bearer $HELPSCOUT_ACCESS_TOKEN"
```

## Core Endpoints

### List Conversations
```bash
curl "https://api.helpscout.net/v2/conversations?mailbox=12345&status=active" \
  -H "Authorization: Bearer $HELPSCOUT_ACCESS_TOKEN"
```

### Create Conversation
```bash
curl -X POST https://api.helpscout.net/v2/conversations \
  -H "Authorization: Bearer $HELPSCOUT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Need help with order",
    "customer": {"email": "customer@example.com"},
    "mailboxId": 12345,
    "type": "email",
    "status": "active",
    "threads": [{
      "type": "customer",
      "customer": {"email": "customer@example.com"},
      "text": "I have a question about my order..."
    }]
  }'
```

### Reply to Conversation
```bash
curl -X POST "https://api.helpscout.net/v2/conversations/123/reply" \
  -H "Authorization: Bearer $HELPSCOUT_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Thanks for reaching out! Here is the answer...",
    "user": 789
  }'
```

### Get Customer
```bash
curl https://api.helpscout.net/v2/customers/456 \
  -H "Authorization: Bearer $HELPSCOUT_ACCESS_TOKEN"
```

### Search Conversations
```bash
curl "https://api.helpscout.net/v2/conversations?query=(status:active)" \
  -H "Authorization: Bearer $HELPSCOUT_ACCESS_TOKEN"
```

## Rate Limits
- **Standard:** 400 requests per minute
- **Burst:** Up to 200 requests in 10 seconds
- Headers returned with rate limit info
- HTTP 429 when exceeded

## Gotchas
- OAuth only — no API keys (Client Credentials is simplest for internal use)
- Tokens expire in 48 hours, use refresh tokens for long-running apps
- Conversations contain Threads (messages/replies)
- Customer vs User: Customers are external, Users are your team
- Mailbox ID required for creating conversations
- `_embedded` contains related resources in list responses
- HAL+JSON format with `_links` for navigation

## Links
- [Docs](https://developer.helpscout.com/)
- [Mailbox API Reference](https://developer.helpscout.com/mailbox-api/)
- [Authentication](https://developer.helpscout.com/mailbox-api/overview/authentication/)
