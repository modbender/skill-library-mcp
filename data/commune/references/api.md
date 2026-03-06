# Commune API Reference

Full documentation: [commune.email/docs](https://commune.email)
Python SDK: `pip install commune-mail`
MCP server: `pip install commune-mcp`
Base URL: `https://api.commune.email`

---

## Authentication

All requests use Bearer token authentication:

```
Authorization: Bearer comm_your_key_here
```

Or set `COMMUNE_API_KEY` in the environment.

---

## Concepts

```
Domain → Inbox → Thread → Message
```

- **Domain** — A custom email domain (e.g. `example.com`). Verified via DNS.
- **Inbox** — A mailbox under a domain (`support@example.com`). Can use auto-assigned domain.
- **Thread** — A conversation (group of related messages sharing a subject/reply chain).
- **Message** — A single email (inbound or outbound) within a thread.

---

## Inboxes

### Create Inbox

```python
inbox = client.inboxes.create(local_part="support")
# inbox.address → "support@agents.postking.io"  (auto-assigned domain)
# inbox.id      → "i_abc123"
```

No domain setup needed — domain is auto-resolved. For custom domains, pass `domain_id`.

### List Inboxes

```python
inboxes = client.inboxes.list()            # all inboxes
inboxes = client.inboxes.list(domain_id)   # filtered by domain
```

### Set Webhook

```python
client.inboxes.set_webhook(
    domain_id, inbox_id,
    endpoint="https://your-app.com/webhook",
    events=["inbound"],
)
```

Receives a `POST` with signed payload when emails arrive. Verify with `verify_signature()`.

---

## Threads

### List Threads

```python
result = client.threads.list(inbox_id="i_xyz", limit=20)
# result.data       → list of Thread objects
# result.next_cursor → pass to next call for pagination
# result.has_more   → bool
```

Thread fields: `thread_id`, `subject`, `message_count`, `last_message_at`,
`first_message_at`, `snippet`, `last_direction`, `has_attachments`.

### Get Messages in Thread

```python
messages = client.threads.messages("conv_abc123", limit=50, order="asc")
```

Message fields: `message_id`, `thread_id`, `direction`, `participants`,
`content`, `content_html`, `attachments`, `created_at`, `metadata.subject`, `metadata.inbox_id`.

### Search Threads (Semantic)

```python
result = client.threads.search(
    query="order not received",
    inbox_id="i_xyz",
    limit=10,
)
```

Uses vector search when available, falls back to text matching. Returns same structure as `list`.

---

## Triage (Tags & Status)

Set via MCP tools or direct API calls:

| Operation | MCP Tool | REST |
|-----------|----------|------|
| Get metadata | `get_thread_metadata` | `GET /v1/threads/{id}/metadata` |
| Set status | `set_thread_status` | `PATCH /v1/threads/{id}/status` |
| Add tags | `tag_thread` | `POST /v1/threads/{id}/tags` |
| Remove tags | `untag_thread` | `DELETE /v1/threads/{id}/tags` |
| Assign | `assign_thread` | `PATCH /v1/threads/{id}/assign` |

**Status values:** `open`, `needs_reply`, `waiting`, `closed`

**Tags:** Free-form strings, comma-separated. Additive — existing tags preserved.

---

## Messages

### Send Email

```python
client.messages.send(
    to="user@example.com",
    subject="Hello",
    text="Hi there!",         # plain text
    # html="<p>Hi!</p>",      # or HTML
    inbox_id="i_xyz",
)
```

### Reply in Thread

```python
client.messages.send(
    to="user@example.com",
    subject="Re: Hello",
    text="Following up...",
    thread_id="conv_abc123",  # continues the thread
    inbox_id="i_xyz",
)
```

Parameters: `to`, `subject`, `html`*, `text`*, `from_address`, `cc`, `bcc`,
`reply_to`, `thread_id`, `domain_id`, `inbox_id`, `attachments`.

*At least one of `html` or `text` required.

---

## Attachments

```python
import base64

# Upload
with open("report.pdf", "rb") as f:
    content = base64.b64encode(f.read()).decode()

upload = client.attachments.upload(content, "report.pdf", "application/pdf")
# upload.attachment_id → "att_abc123"

# Send with attachment
client.messages.send(
    to="user@example.com",
    subject="Report",
    text="See attached.",
    attachments=[upload.attachment_id],
)

# Get download URL (expires in 1 hour by default)
url_info = client.attachments.url("att_abc123", expires_in=3600)
# url_info.url → "https://..."
```

---

## Webhooks

Commune signs webhook deliveries with HMAC-SHA256:

```
x-commune-signature: v1=5a3f2b...
x-commune-timestamp: 1707667200000
```

Verify in your handler:

```python
from commune import verify_signature, WebhookVerificationError

try:
    verify_signature(
        payload=request.body,
        signature=request.headers["x-commune-signature"],
        secret="whsec_...",
        timestamp=request.headers["x-commune-timestamp"],
    )
except WebhookVerificationError:
    return 401
```

---

## Deliverability

```python
# Stats: sent, delivered, bounced, complained, failed
stats = client.deliverability.stats(inbox_id="i_xyz", period="7d")
# Periods: "24h", "7d", "30d"

# Suppression list (bounced/complained addresses)
suppressions = client.deliverability.suppressions(inbox_id="i_xyz")

# Delivery event log
events = client.deliverability.events(inbox_id="i_xyz")
```

---

## Rate Limits

| Tier | Emails/hour | Emails/day |
|------|-------------|------------|
| Free | 100 | 1,000 |
| Pro | 10,000 | 100,000 |
| Enterprise | Unlimited | Unlimited |

Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
Exceeded limits return `429 Too Many Requests` → catch `RateLimitError`.

---

## Error Handling

```python
from commune import (
    CommuneClient, CommuneError, AuthenticationError,
    NotFoundError, ValidationError, RateLimitError,
)

try:
    client.domains.get("nonexistent")
except AuthenticationError:  # 401
    print("Invalid API key")
except NotFoundError:        # 404
    print("Not found")
except ValidationError as e: # 400
    print(f"Bad request: {e.message}")
except RateLimitError:       # 429
    print("Slow down")
except CommuneError as e:    # catch-all
    print(f"Error {e.status_code}: {e.message}")
```

---

## MCP Tools Quick Reference

When using the MCP server, these tools are available:

| Tool | What it does |
|------|-------------|
| `list_domains` | List all domains |
| `create_domain` | Register a new domain |
| `get_domain_records` | Get DNS records for verification |
| `verify_domain` | Trigger DNS verification |
| `list_inboxes` | List inboxes (optionally filtered) |
| `create_inbox` | Create a new inbox |
| `delete_inbox` | Delete an inbox |
| `set_extraction_schema` | Configure structured data extraction |
| `list_threads` | List threads with pagination |
| `get_thread_messages` | Read full conversation |
| `search_threads` | Semantic search across emails |
| `get_thread_metadata` | Get tags/status/assignment |
| `set_thread_status` | Set `open`/`needs_reply`/`waiting`/`closed` |
| `tag_thread` | Add labels to a thread |
| `untag_thread` | Remove labels from a thread |
| `assign_thread` | Assign to an agent/user |
| `send_email` | Send or reply to an email |
| `upload_attachment` | Upload a file (returns attachment_id) |
| `get_attachment_url` | Get temporary download URL |
| `get_deliverability_stats` | Sent/delivered/bounced rates |
| `get_suppressions` | List suppressed addresses |
| `get_delivery_events` | Delivery event log |
