# Index

| API | Line |
|-----|------|
| Twilio | 2 |
| Mailgun | 186 |
| Postmark | 265 |
| Resend | 334 |
| Mailchimp | 400 |
| Slack | 492 |
| Discord | 598 |
| Telegram Bot API | 700 |
| Zoom | 770 |

---

# Twilio

## Base URL
```
https://api.twilio.com/2010-04-01
```

## Authentication
```bash
curl https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID.json \
  -u $TWILIO_SID:$TWILIO_AUTH_TOKEN
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /Accounts/:sid/Messages | POST | Send SMS |
| /Accounts/:sid/Messages | GET | List messages |
| /Accounts/:sid/Calls | POST | Make call |
| /Accounts/:sid/Calls | GET | List calls |

## Quick Examples

### Send SMS
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages.json" \
  -u "$TWILIO_SID:$TWILIO_AUTH_TOKEN" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "Body=Hello from Twilio!"
```

### Send WhatsApp Message
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages.json" \
  -u "$TWILIO_SID:$TWILIO_AUTH_TOKEN" \
  -d "From=whatsapp:+14155238886" \
  -d "To=whatsapp:+15559876543" \
  -d "Body=Hello from WhatsApp!"
```

### Make Voice Call
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Calls.json" \
  -u "$TWILIO_SID:$TWILIO_AUTH_TOKEN" \
  -d "From=+15551234567" \
  -d "To=+15559876543" \
  -d "Url=http://demo.twilio.com/docs/voice.xml"
```

### Get Message Status
```bash
curl "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages/$MESSAGE_SID.json" \
  -u "$TWILIO_SID:$TWILIO_AUTH_TOKEN"
```

## Message Status Values

| Status | Meaning |
|--------|---------|
| queued | In queue |
| sending | Being sent |
| sent | Sent to carrier |
| delivered | Delivered |
| failed | Failed |
| undelivered | Not delivered |

## Common Traps

- Phone numbers must be E.164 format (+15551234567)
- WhatsApp requires sandbox approval for production
- Test credentials only work with magic numbers
- Status callbacks need public URL
- Rate limits per phone number, not account

## Rate Limits

- SMS: 1 message/second per phone number
- API: 100 requests/second per account
- Concurrent calls: varies by account

## Pricing

SMS and calls are charged per segment/minute. Check your console for rates.

## Official Docs
https://www.twilio.com/docs/usage/api
# SendGrid

## Base URL
```
https://api.sendgrid.com/v3
```

## Authentication
```bash
curl https://api.sendgrid.com/v3/user/profile \
  -H "Authorization: Bearer $SENDGRID_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /mail/send | POST | Send email |
| /templates | GET | List templates |
| /contactdb/recipients | POST | Add contacts |
| /suppressions/bounces | GET | Get bounces |
| /stats | GET | Get statistics |

## Quick Examples

### Send Simple Email
```bash
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{"to": [{"email": "user@example.com"}]}],
    "from": {"email": "sender@yourdomain.com"},
    "subject": "Hello",
    "content": [{"type": "text/plain", "value": "Hello, World!"}]
  }'
```

### Send HTML Email
```bash
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{"to": [{"email": "user@example.com"}]}],
    "from": {"email": "sender@yourdomain.com"},
    "subject": "Hello",
    "content": [
      {"type": "text/plain", "value": "Hello"},
      {"type": "text/html", "value": "<h1>Hello</h1>"}
    ]
  }'
```

### Send with Template
```bash
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{
      "to": [{"email": "user@example.com"}],
      "dynamic_template_data": {"name": "John"}
    }],
    "from": {"email": "sender@yourdomain.com"},
    "template_id": "d-xxxxxxxxxxxxx"
  }'
```

### Add Contacts to List
```bash
curl -X PUT https://api.sendgrid.com/v3/marketing/contacts \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contacts": [
      {"email": "user@example.com", "first_name": "John"}
    ]
  }'
```

## Common Traps

- Send returns 202 (accepted), not 200
- From address must be verified domain
- personalizations array required even for single recipient
- Template variables use Handlebars syntax
- Free tier: 100 emails/day

## Rate Limits

- 100 emails/second
- 10,000 recipients/request in personalizations

## Official Docs
https://docs.sendgrid.com/api-reference
# Mailgun

## Base URL
```
https://api.mailgun.net/v3
```

## Authentication
```bash
curl "https://api.mailgun.net/v3/domains" \
  -u "api:$MAILGUN_API_KEY"
```

## Send Email
```bash
curl -X POST "https://api.mailgun.net/v3/$DOMAIN/messages" \
  -u "api:$MAILGUN_API_KEY" \
  -F from="sender@$DOMAIN" \
  -F to="recipient@example.com" \
  -F subject="Hello" \
  -F text="Plain text body" \
  -F html="<h1>HTML body</h1>"
```

## Send with Template
```bash
curl -X POST "https://api.mailgun.net/v3/$DOMAIN/messages" \
  -u "api:$MAILGUN_API_KEY" \
  -F from="sender@$DOMAIN" \
  -F to="recipient@example.com" \
  -F subject="Welcome" \
  -F template="welcome" \
  -F h:X-Mailgun-Variables='{"name": "John"}'
```

## Send with Attachment
```bash
curl -X POST "https://api.mailgun.net/v3/$DOMAIN/messages" \
  -u "api:$MAILGUN_API_KEY" \
  -F from="sender@$DOMAIN" \
  -F to="recipient@example.com" \
  -F subject="File attached" \
  -F text="See attachment" \
  -F attachment=@/path/to/file.pdf
```

## Get Logs
```bash
curl "https://api.mailgun.net/v3/$DOMAIN/events?event=delivered&limit=100" \
  -u "api:$MAILGUN_API_KEY"
```

## Validate Email
```bash
curl "https://api.mailgun.net/v4/address/validate?address=user@example.com" \
  -u "api:$MAILGUN_API_KEY"
```

## Event Types

| Event | Description |
|-------|-------------|
| accepted | Mailgun accepted |
| delivered | Delivered to recipient |
| opened | Email opened |
| clicked | Link clicked |
| failed | Failed to deliver |
| bounced | Hard bounce |

## Common Traps

- Domain must be verified in Mailgun
- EU region uses api.eu.mailgun.net
- Use form data (-F), not JSON for sending
- Free tier: only to authorized recipients
- Rate limit: varies by plan

## Official Docs
https://documentation.mailgun.com/en/latest/api-intro.html
# Postmark

## Base URL
```
https://api.postmarkapp.com
```

## Authentication
```bash
curl https://api.postmarkapp.com/email \
  -H "X-Postmark-Server-Token: $POSTMARK_SERVER_TOKEN" \
  -H "Content-Type: application/json"
```

## Send Email
```bash
curl -X POST https://api.postmarkapp.com/email \
  -H "X-Postmark-Server-Token: $POSTMARK_SERVER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "From": "sender@example.com",
    "To": "recipient@example.com",
    "Subject": "Hello",
    "TextBody": "Plain text content",
    "HtmlBody": "<h1>HTML content</h1>"
  }'
```

## Send with Template
```bash
curl -X POST https://api.postmarkapp.com/email/withTemplate \
  -H "X-Postmark-Server-Token: $POSTMARK_SERVER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "From": "sender@example.com",
    "To": "recipient@example.com",
    "TemplateAlias": "welcome",
    "TemplateModel": {
      "name": "John"
    }
  }'
```

## Send Batch
```bash
curl -X POST https://api.postmarkapp.com/email/batch \
  -H "X-Postmark-Server-Token: $POSTMARK_SERVER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"From": "...", "To": "user1@...", "Subject": "...", "TextBody": "..."},
    {"From": "...", "To": "user2@...", "Subject": "...", "TextBody": "..."}
  ]'
```

## Get Delivery Stats
```bash
curl https://api.postmarkapp.com/deliverystats \
  -H "X-Postmark-Server-Token: $POSTMARK_SERVER_TOKEN"
```

## Common Traps

- Server Token for sending, Account Token for account ops
- From address must be verified sender signature
- Batch max 500 emails
- Returns MessageID for tracking

## Official Docs
https://postmarkapp.com/developer/api/overview
# Resend

## Base URL
```
https://api.resend.com
```

## Authentication
```bash
curl https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY"
```

## Send Email
```bash
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "Acme <onboarding@resend.dev>",
    "to": ["user@example.com"],
    "subject": "Hello World",
    "html": "<p>Welcome to Resend!</p>"
  }'
```

## Send with React Email Template
```bash
curl -X POST https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "Acme <onboarding@resend.dev>",
    "to": ["user@example.com"],
    "subject": "Welcome",
    "react": "<Email><Text>Hello {name}</Text></Email>"
  }'
```

## Get Email Status
```bash
curl "https://api.resend.com/emails/$EMAIL_ID" \
  -H "Authorization: Bearer $RESEND_API_KEY"
```

## Send Batch
```bash
curl -X POST https://api.resend.com/emails/batch \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[
    {"from": "...", "to": ["user1@..."], "subject": "...", "html": "..."},
    {"from": "...", "to": ["user2@..."], "subject": "...", "html": "..."}
  ]'
```

## Common Traps

- `to` is always an array
- Free tier: 100 emails/day, test domain only
- `from` must be verified domain
- Returns email ID for tracking
- Supports React Email components

## Official Docs
https://resend.com/docs/api-reference/introduction
# Mailchimp

## Base URL
```
https://{dc}.api.mailchimp.com/3.0
```
Note: `{dc}` is your data center (e.g., us19) - find it in your API key after the dash.

## Authentication
```bash
curl "https://us19.api.mailchimp.com/3.0/" \
  -u "anystring:$MAILCHIMP_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /lists | GET | List audiences |
| /lists/:id/members | GET | List subscribers |
| /lists/:id/members | POST | Add subscriber |
| /campaigns | GET | List campaigns |
| /campaigns | POST | Create campaign |

## Quick Examples

### List Audiences
```bash
curl "https://us19.api.mailchimp.com/3.0/lists" \
  -u "anystring:$MAILCHIMP_API_KEY"
```

### Add Subscriber
```bash
curl -X POST "https://us19.api.mailchimp.com/3.0/lists/$LIST_ID/members" \
  -u "anystring:$MAILCHIMP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "user@example.com",
    "status": "subscribed",
    "merge_fields": {
      "FNAME": "John",
      "LNAME": "Doe"
    }
  }'
```

### Update Subscriber
```bash
# MD5 hash of lowercase email
SUBSCRIBER_HASH=$(echo -n "user@example.com" | md5sum | cut -d' ' -f1)
curl -X PATCH "https://us19.api.mailchimp.com/3.0/lists/$LIST_ID/members/$SUBSCRIBER_HASH" \
  -u "anystring:$MAILCHIMP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"merge_fields": {"FNAME": "Jane"}}'
```

### Create Campaign
```bash
curl -X POST "https://us19.api.mailchimp.com/3.0/campaigns" \
  -u "anystring:$MAILCHIMP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "regular",
    "recipients": {"list_id": "LIST_ID"},
    "settings": {
      "subject_line": "Subject",
      "from_name": "Sender",
      "reply_to": "reply@example.com"
    }
  }'
```

## Subscriber Status Values

| Status | Meaning |
|--------|---------|
| subscribed | Active subscriber |
| unsubscribed | Opted out |
| pending | Awaiting confirmation |
| cleaned | Bounced/invalid |

## Common Traps

- Data center (dc) in URL - get from API key (key-dc)
- Subscriber ID is MD5 hash of lowercase email
- Status "subscribed" bypasses double opt-in
- Merge fields (FNAME, LNAME) are customizable per list
- Rate limit: 10 concurrent connections

## Official Docs
https://mailchimp.com/developer/marketing/api/
# Slack

## Base URL
```
https://slack.com/api
```

## Authentication
```bash
curl https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /chat.postMessage | POST | Send message |
| /conversations.list | GET | List channels |
| /conversations.history | GET | Get messages |
| /users.list | GET | List users |
| /users.info | GET | Get user |
| /files.upload | POST | Upload file |
| /reactions.add | POST | Add reaction |

## Quick Examples

### Send Message
```bash
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C0123456",
    "text": "Hello, world!"
  }'
```

### Send Message with Blocks
```bash
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "C0123456",
    "blocks": [
      {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*Bold* and _italic_"}
      }
    ]
  }'
```

### List Channels
```bash
curl "https://slack.com/api/conversations.list?types=public_channel,private_channel" \
  -H "Authorization: Bearer $SLACK_TOKEN"
```

### Get Channel History
```bash
curl "https://slack.com/api/conversations.history?channel=C0123456&limit=100" \
  -H "Authorization: Bearer $SLACK_TOKEN"
```

### Upload File
```bash
curl -X POST https://slack.com/api/files.upload \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -F file=@document.pdf \
  -F channels=C0123456 \
  -F title="My Document"
```

## Message Formatting

| Format | Syntax |
|--------|--------|
| Bold | `*text*` |
| Italic | `_text_` |
| Strike | `~text~` |
| Code | `` `code` `` |
| Link | `<https://url|text>` |
| User | `<@U0123456>` |
| Channel | `<#C0123456>` |

## Common Traps

- Always returns 200, check `ok` field in response
- Channel IDs start with C, user IDs with U
- Rate limit varies by method (Tier 1-4)
- files.upload v1 deprecated, use v2 for new code
- Private channels need bot to be invited

## Rate Limits

| Tier | Limit |
|------|-------|
| Tier 1 | 1/min |
| Tier 2 | 20/min |
| Tier 3 | 50/min |
| Tier 4 | 100/min |

## Official Docs
https://api.slack.com/methods
# Discord

## Base URL
```
https://discord.com/api/v10
```

## Authentication
```bash
# Bot token
curl https://discord.com/api/v10/users/@me \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN"

# OAuth Bearer token
curl https://discord.com/api/v10/users/@me \
  -H "Authorization: Bearer $DISCORD_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /channels/:id/messages | POST | Send message |
| /channels/:id/messages | GET | Get messages |
| /guilds/:id | GET | Get server |
| /guilds/:id/members | GET | List members |
| /users/@me | GET | Current user |
| /webhooks/:id/:token | POST | Execute webhook |

## Quick Examples

### Send Message
```bash
curl -X POST https://discord.com/api/v10/channels/$CHANNEL_ID/messages \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, World!"}'
```

### Send Embed
```bash
curl -X POST https://discord.com/api/v10/channels/$CHANNEL_ID/messages \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "Embed Title",
      "description": "Description here",
      "color": 5814783,
      "fields": [
        {"name": "Field 1", "value": "Value 1", "inline": true}
      ]
    }]
  }'
```

### Execute Webhook (no auth needed)
```bash
curl -X POST "https://discord.com/api/webhooks/$WEBHOOK_ID/$WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Webhook message",
    "username": "Custom Name"
  }'
```

### Get Channel Messages
```bash
curl "https://discord.com/api/v10/channels/$CHANNEL_ID/messages?limit=50" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN"
```

### Add Reaction
```bash
curl -X PUT "https://discord.com/api/v10/channels/$CHANNEL_ID/messages/$MESSAGE_ID/reactions/%F0%9F%91%8D/@me" \
  -H "Authorization: Bot $DISCORD_BOT_TOKEN"
# %F0%9F%91%8D = 👍 URL encoded
```

## Common Traps

- Bot tokens use "Bot" prefix, OAuth uses "Bearer"
- Emoji in URLs must be URL encoded
- Rate limits are per-route, not global
- Snowflake IDs are strings, not numbers
- Intents required for certain events (member list, presence)

## Rate Limits

- Global: 50 requests/second
- Per route: varies (usually 5/5s or 10/10s)
- Message send: 5 messages/5 seconds per channel

Check headers:
```
X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset
```

## Official Docs
https://discord.com/developers/docs/reference
# Telegram Bot API

## Base URL
```
https://api.telegram.org/bot{TOKEN}
```

## Send Message
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -d chat_id="$CHAT_ID" \
  -d text="Hello, World!"
```

## Send Message with Formatting
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "$CHAT_ID",
    "text": "*Bold* and _italic_",
    "parse_mode": "Markdown"
  }'
```

## Send Photo
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendPhoto" \
  -F chat_id="$CHAT_ID" \
  -F photo=@image.jpg \
  -F caption="Photo caption"
```

## Get Updates (polling)
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?offset=0&limit=10"
```

## Set Webhook
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d url="https://yourdomain.com/webhook"
```

## Send Inline Keyboard
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "$CHAT_ID",
    "text": "Choose:",
    "reply_markup": {
      "inline_keyboard": [[
        {"text": "Option 1", "callback_data": "opt1"},
        {"text": "Option 2", "callback_data": "opt2"}
      ]]
    }
  }'
```

## Common Traps

- Token in URL path, not header
- chat_id can be negative (groups)
- getUpdates and webhooks are mutually exclusive
- File uploads use multipart/form-data
- Rate limit: 30 messages/second to same chat

## Official Docs
https://core.telegram.org/bots/api
# Zoom

## Base URL
```
https://api.zoom.us/v2
```

## Authentication
```bash
curl https://api.zoom.us/v2/users/me \
  -H "Authorization: Bearer $ZOOM_ACCESS_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /users/me | GET | Current user |
| /users/:id/meetings | GET | List meetings |
| /users/:id/meetings | POST | Create meeting |
| /meetings/:id | GET | Get meeting |
| /meetings/:id | DELETE | Delete meeting |

## Create Meeting
```bash
curl -X POST "https://api.zoom.us/v2/users/me/meetings" \
  -H "Authorization: Bearer $ZOOM_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Team Sync",
    "type": 2,
    "start_time": "2024-01-15T10:00:00Z",
    "duration": 30,
    "timezone": "America/New_York"
  }'
```

## Meeting Types

| Type | Meaning |
|------|---------|
| 1 | Instant meeting |
| 2 | Scheduled meeting |
| 3 | Recurring (no fixed time) |
| 8 | Recurring (fixed time) |

## Common Traps

- OAuth required, Server-to-Server or User-level
- Meeting IDs are numbers, not strings
- Duration in minutes
- Rate limit: 10 requests/second

## Official Docs
https://developers.zoom.us/docs/api/
