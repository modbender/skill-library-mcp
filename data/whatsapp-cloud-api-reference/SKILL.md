---
name: whatsapp-cloud-api-reference
description: Use when implementing WhatsApp messaging via Meta Cloud API, or diagnosing failures like message not delivered, template rejected, webhook issues, phone not registered, token errors, rate limiting, 24-hour window violations, quality rating drops, or setup mistakes on the WhatsApp Business API.
---

# WhatsApp Messaging via Meta Cloud API

## Overview

The Meta WhatsApp Cloud API is the official, fully hosted path for programmatic WhatsApp messaging. No server management needed. First 1,000 service conversations per month are free.

**Key rules:**
- **Your app can NEVER send a free-form text message first.** The very first message to any user must always be a pre-approved template. Free-form text is only unlocked after the user replies, and only within the 24-hour window that reply opens.
- Business-initiated messages outside a 24h reply window **must** use a pre-approved template
- Phone numbers must be registered in your WABA before sending
- Always use a System User token — user tokens expire in 24 hours

**Conversation flow:**
```
App → user:  MUST be a template (always, for first contact)
User → app:  reply opens a 24-hour free-form window
App → user:  free-form text allowed within that 24h window
  [24h passes with no user reply]
App → user:  MUST use a template again to re-engage
```

---

## Setup Checklist

1. **Create Meta Developer App** — developers.facebook.com → Create App → Business type
2. **Add WhatsApp product** to the app (gives temp test number + 5 test recipient slots)
3. **Create a permanent System User token:**
   - Meta Business Manager → Settings → System Users → Create Admin user
   - Assign permissions: `whatsapp_business_messaging` + `whatsapp_business_management`
   - Generate token — this never expires
4. **Register real phone number** — number cannot already be active on personal/business WhatsApp
5. **Set up webhook** — needs public HTTPS URL (trusted CA cert, no self-signed), must respond in < 10s

---

## Sending Messages

### Text Message (Node.js)

```javascript
// npm install axios
const axios = require('axios');

async function sendMessage(phoneNumber, text) {
    // phoneNumber: E.164 without +, e.g. "14155551234"
    const res = await axios.post(
        `https://graph.facebook.com/v21.0/${process.env.WA_PHONE_NUMBER_ID}/messages`,
        {
            messaging_product: 'whatsapp',
            recipient_type: 'individual',
            to: phoneNumber,
            type: 'text',
            text: { preview_url: false, body: text }
        },
        { headers: { Authorization: `Bearer ${process.env.WA_ACCESS_TOKEN}` } }
    );
    return res.data;
}
```

### Text Message (Python)

```python
# pip install requests
import requests, os

def send_message(phone: str, text: str) -> dict:
    r = requests.post(
        f"https://graph.facebook.com/v21.0/{os.environ['WA_PHONE_NUMBER_ID']}/messages",
        headers={"Authorization": f"Bearer {os.environ['WA_ACCESS_TOKEN']}"},
        json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,        # E.164 without +
            "type": "text",
            "text": {"preview_url": False, "body": text}
        }
    )
    r.raise_for_status()
    return r.json()
```

### Quick test via curl

```bash
curl -X POST "https://graph.facebook.com/v21.0/YOUR_PHONE_ID/messages" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messaging_product":"whatsapp","to":"14155551234","type":"text","text":{"body":"Hello"}}'
```

### Template Message (required when > 24h since last user reply)

```javascript
const payload = {
    messaging_product: 'whatsapp',
    to: phoneNumber,
    type: 'template',
    template: {
        name: 'hello_world',           // your approved template name
        language: { code: 'en_US' },
        components: [{
            type: 'body',
            parameters: [
                { type: 'text', text: 'John' },        // fills {{1}}
                { type: 'text', text: 'Order #4521' }  // fills {{2}}
            ]
        }]
    }
};
```

### Media Messages (Image, Document, Audio, Video)

**Image:**
```javascript
const payload = {
    messaging_product: 'whatsapp',
    to: phoneNumber,
    type: 'image',
    image: {
        link: 'https://your-domain.com/image.jpg'  // must be publicly accessible HTTPS
    }
};
```

**Document:**
```javascript
const payload = {
    messaging_product: 'whatsapp',
    to: phoneNumber,
    type: 'document',
    document: {
        link: 'https://your-domain.com/file.pdf',
        caption: 'Invoice'  // optional
    }
};
```

**Audio:**
```javascript
const payload = {
    messaging_product: 'whatsapp',
    to: phoneNumber,
    type: 'audio',
    audio: {
        link: 'https://your-domain.com/audio.mp3'
    }
};
```

**Video:**
```javascript
const payload = {
    messaging_product: 'whatsapp',
    to: phoneNumber,
    type: 'video',
    video: {
        link: 'https://your-domain.com/video.mp4',
        caption: 'Demo video'  // optional
    }
};
```

**Important constraints:**
- All media URLs must be **publicly accessible HTTPS** (http:// fails)
- Max file sizes: Image 16MB, Document 100MB, Audio 16MB, Video 16MB
- Supported formats: Images (JPEG, PNG), Documents (PDF), Audio (AAC, MP3, OGG, WAV), Video (MP4, 3GPP)
- Media must not require authentication
- URLs cannot use shorteners (bit.ly, tinyurl, etc.)

### Webhook Handler (Express) — Correct Async Pattern

```javascript
// GET — Meta calls this to verify your endpoint
app.get('/webhook', (req, res) => {
    const { 'hub.mode': mode, 'hub.verify_token': token, 'hub.challenge': challenge } = req.query;
    if (mode === 'subscribe' && token === process.env.VERIFY_TOKEN)
        return res.status(200).send(challenge);  // raw string only — NOT JSON
    res.sendStatus(403);
});

// POST — CRITICAL: return 200 IMMEDIATELY, process async
app.post('/webhook', express.json(), (req, res) => {
    // Return 200 immediately so Meta doesn't retry
    res.sendStatus(200);

    // Process webhook payload asynchronously (don't block)
    setImmediate(() => {
        processWebhookAsync(req.body).catch(err => {
            logger.error(`Webhook processing failed: ${err.message}`);
        });
    });
});

async function processWebhookAsync(body) {
    body.entry?.forEach(entry =>
        entry.changes?.forEach(change => {
            const value = change.value;

            // Incoming messages
            if (value.messages) {
                value.messages.forEach(msg => {
                    console.log(`Message from ${msg.from}: ${msg.text?.body}`);
                    handleMessage(msg);
                });
            }

            // Delivery status
            if (value.statuses) {
                value.statuses.forEach(status => {
                    console.log(`Message ${status.id} status: ${status.status}`);
                    handleDeliveryStatus(status);
                });
            }
        })
    );
}
```

---

## Message Status & Delivery Tracking

### Webhook Payload: Delivery Status

Meta sends status updates via webhook when a message is delivered, read, or fails:

```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "statuses": [{
          "id": "wamid.xxx",           // Message ID from your send response
          "status": "delivered",       // "sent" | "delivered" | "read" | "failed"
          "timestamp": "1675262308",
          "recipient_id": "14155551234",
          "type": "message"
        }]
      }
    }]
  }]
}
```

**Status values:**
- `sent` — Message reached Meta servers
- `delivered` — Message delivered to user's device
- `read` — User opened the message
- `failed` — Delivery failed (permanent)

### Tracking Message Delivery

```javascript
// When you send, store the message ID
const sendResult = await sendMessage(phone, text);
const messageId = sendResult.messages[0].id;

// Log it for webhook tracking
db.messages.insert({
    message_id: messageId,
    recipient: phone,
    sent_at: Date.now(),
    status: 'sent',
    body: text
});

// When webhook arrives with status update, match by message_id
function handleDeliveryStatus(statusUpdate) {
    const { id, status, recipient_id } = statusUpdate;

    // Update your database
    db.messages.updateOne(
        { message_id: id },
        { status: status, updated_at: Date.now() }
    );

    // Handle delivery failures
    if (status === 'failed') {
        logger.error(`Message ${id} failed to deliver to ${recipient_id}`);
        // Retry logic here
    }
}
```

---

## WABA Quality Rating & Account Health

### What is Quality Rating?

Your WhatsApp Business Account (WABA) has a quality rating that affects your sending ability:

| Rating | Impact | Recovery |
|--------|--------|----------|
| **GREEN** | Full functionality, no restrictions | Maintain this (stay green) |
| **YELLOW** | Slight rate limit reduction, monitor closely | Improve within 7 days or drops to RED |
| **RED** | Severe restrictions, may lose messaging access | Contact Meta Support |

### How to Check Quality Rating

```bash
curl "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID?fields=quality_rating" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response: { "quality_rating": "GREEN" }
```

### What Causes Quality Rating to Drop?

- **High bounce rate** — sending to invalid/inactive numbers
- **Spam reports** — users marking your messages as spam
- **High failure rate** — messages consistently failing to deliver
- **User blocks** — users blocking your number after messages
- **Policy violations** — sending prohibited content

### How to Improve Quality Rating

1. **Validate phone numbers before sending** — use the WhatsApp contacts check (error 131026)
2. **Only message opted-in users** — don't send unsolicited messages
3. **Keep template content transactional** — avoid marketing spam
4. **Monitor quality metrics** — check rating regularly via API
5. **Respect user preferences** — remove users who opt out
6. **Don't retry failed numbers aggressively** — wait before retrying same number

---

## Group Messages

**Note:** WhatsApp Business API does NOT support group messaging directly. You can only send to individual recipients (1:1 conversations).

If you need group functionality:
- Users must add your business number to a group manually
- Messages sent to the group are treated as individual 1:1 messages
- You cannot initiate group conversations programmatically

---

## API Versioning Strategy

All examples use `v21.0` (current as of February 2026). Meta deprecates API versions annually.

### Checking Your Current Version

```bash
# List all available versions
curl "https://graph.facebook.com/versions" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Current version recommendations
# - v21.0 (current, recommended)
# - v20.0 (previous, will deprecate in 6 months)
```

### Version Update Strategy

```javascript
// Store version in config, not hardcoded
const API_VERSION = process.env.WHATSAPP_API_VERSION || 'v21.0';

const url = `https://graph.facebook.com/${API_VERSION}/${PHONE_NUMBER_ID}/messages`;

// When Meta deprecates a version, update .env:
// WHATSAPP_API_VERSION=v22.0
```

### What Changes Between Versions?

- New message types or features added
- Deprecated fields removed
- Error codes may change slightly
- Response payload structure may change

**Always test before upgrading** — make requests against the new version in your dev environment first.

---

## Message Constraints & Limits

### Text Message Limits

| Constraint | Limit |
|-----------|-------|
| Text body max length | 4,096 characters |
| Link preview | Enabled by default, disable with `preview_url: false` |
| Carriage returns / newlines | Supported (use `\n`) |

### Interactive Message Limits

| Type | Items | Character Limit |
|------|-------|-----------------|
| **Button** | 1-3 | Title: 20 chars |
| **List** | 1-10 | Title: 24 chars per row |

### Media URL Requirements

- Must be **HTTPS only** (http:// rejected)
- Must be **publicly accessible** (no authentication required)
- Must **NOT use shorteners** (bit.ly, tinyurl rejected)
- Must have correct **Content-Type header**
- Max file sizes:
  - Image: 16 MB
  - Audio: 16 MB
  - Video: 16 MB
  - Document: 100 MB

### Rate Limits (Per WABA)

| Limit | Value |
|-------|-------|
| Default throughput | 80 messages/second |
| Burst capacity | 1,000 messages/second (request increase) |
| Requests per minute | 60 API calls/minute |

---

## Template Approval Process

### Template Submission Workflow

```
Create template in Meta Business Manager
        ↓
Submit for review (human review by Meta)
        ↓
Status: PENDING (24-72 hours typical)
        ↓
Status: APPROVED (can now use in messages)
    OR
Status: REJECTED (reason provided in dashboard)
```

### How Long Does Approval Take?

- **Typical**: 24-72 hours
- **Peak times** (weekends, holidays): up to 7 days
- **Fast-track**: Available for high-volume WABAs (request in Meta Support)

### Common Approval Issues

| Issue | Why Rejected |
|-------|-------------|
| **Variable format** | Must use `{{1}}`, `{{2}}` format |
| **Template starts/ends with variable** | Must have text before first variable |
| **URL shorteners** | Use full domain URLs only |
| **Placeholder quality** | Placeholder values must be realistic examples |
| **Sensitive data request** | Never ask for SSN, card numbers, passwords |
| **Unclear purpose** | Purpose field must clearly state intent |
| **Warm language in utility** | Use formal wording; warmth triggers "marketing" category (costs more) |
| **Duplicate template** | Name/wording too similar to existing template |

Check rejection reason in Meta Business Manager → Business Support → Rejected Template Messages.

---

## Common Setup Mistakes

### 1. Phone Number Already on Personal WhatsApp

**Symptom:** Registration fails with error 133010, status stays PENDING

**Cause:** Phone number is already active on a personal WhatsApp account

**Fix:**
```
1. Remove phone from personal WhatsApp (go to Settings → Devices → Remove phone)
2. Wait 24 hours
3. Re-run registration API call
```

### 2. Mixing Phone Number ID with WABA ID

**Symptom:** API returns "Invalid parameters" for phone operations

**How to tell them apart:**
```
PHONE_NUMBER_ID: 120######## (11-12 digits, starts with 120)
WABA_ID: ######### (9-10 digits, higher number)

# Correct endpoint
POST /v21.0/PHONE_NUMBER_ID/messages  ✅

# Wrong endpoint
POST /v21.0/WABA_ID/messages  ❌
```

### 3. Token Validation Passes but Scopes Missing

**Symptom:** Token debug shows valid, but messaging fails with error 3/10

```bash
# Token is "valid" but missing scopes
curl "https://graph.facebook.com/debug_token?input_token=TOKEN&access_token=TOKEN"
# Response: { "is_valid": true, "scopes": ["manage_pages"] }  ← NO whatsapp_business_messaging

# Fix: Regenerate System User token with correct permissions
```

### 4. Webhook Returns JSON Instead of Raw Challenge

**Symptom:** Webhook verification fails silently in Meta dashboard

**Wrong:**
```javascript
return res.json({ challenge });  // ❌ returns JSON
```

**Correct:**
```javascript
return res.status(200).send(challenge);  // ✅ returns raw string
```

### 5. WABA Not Subscribed to App

**Symptom:** Webhooks never arrive (silent failure since 2025 Meta UI change)

**Fix:**
```bash
curl -X POST \
  "https://graph.facebook.com/v21.0/WABA_ID/subscribed_apps" \
  -H "Authorization: Bearer YOUR_SYSTEM_USER_TOKEN"
```

### 6. Sending Template Too Early in Approval Process

**Symptom:** Error 132001 "Template Unavailable"

**Cause:** Template still in PENDING status, not yet APPROVED

**Fix:** Check status in Meta Business Manager → Message Templates → wait for APPROVED status

### 7. Phone Number Not in WABA

**Symptom:** Error 131009 when trying to send

**How to verify:**
```bash
# Check which phone numbers are in your WABA
curl "https://graph.facebook.com/v21.0/WABA_ID/phone_numbers?fields=id,display_phone_number" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8. Sending Free-Form Text as First Message

**Symptom:** API returns 200, message ID issued, but user never receives it

**Root cause:** Only templates allowed as first message to any number

**Fix:** Always use a template for first contact

---



### Phone Number Status Reference

Check the `status` field via API. Each status blocks different operations:

| Status | Meaning | Action |
|--------|---------|--------|
| **PENDING** | Number is registered but not verified | Set up 2FA (either manual or API), then run register call |
| **REGISTERED** | Number is verified and ready | Check `code_verification_status` — should be `VERIFIED` |
| **FLAGGED** | Account or number under review for policy violation | Contact Meta Support |
| **BANNED** | Number permanently disabled | Contact Meta Support |

---

### Error Code Reference

| Code | Name | Cause | Fix |
|------|------|-------|-----|
| **190** | Token Expired | User token (24h lifetime) used in production | Switch to System User token; debug at developers.facebook.com/tools/debug/accesstoken |
| **3 / 10** | Permission Denied | Token missing required scopes | Regenerate System User token with `whatsapp_business_messaging` + `whatsapp_business_management` |
| **100** | Invalid Parameter | Misspelled field or wrong value | Check request body against API docs; verify phone number format (E.164, no `+`) |
| **130429** | Rate Limit (MPS) | Exceeded 80 messages/sec default | Add send queue + exponential backoff (see below) |
| **131047** | 24h Window Expired | > 24h since customer last replied | Replace free-form text with a pre-approved template message |
| **131026** | Undeliverable | Recipient blocked you, no WhatsApp, or outdated app | Verify recipient number; confirm they have WhatsApp installed and accepted Meta terms |
| **131048** | Spam Rate Limit | Messages flagged as spam | Check Quality Rating in WhatsApp Manager; review message content and opt-in practices |
| **131056** | Pair Rate Limit | Too many messages to same recipient too fast | Wait before retrying the same number |
| **131009** | Invalid Parameter Value | Phone number not in WABA, or wrong parameter | Verify number is registered in your WABA under Phone Numbers |
| **131021** | Same Sender/Recipient | `from` and `to` are the same number | Use a different recipient |
| **131031** | Account Locked | Policy violation or wrong 2-step PIN | Contact Meta Support |
| **132001** | Template Unavailable | Wrong template name, wrong language code, or not yet approved | Check WhatsApp Manager → Message Templates for exact name, language, and status |
| **133010** | Phone Not Registered | Sender number not registered in Cloud API | Run the registration API call (see below) |
| **368** | Policy Violation | Account restricted | Contact Meta Support |
| **1 / 2** | API Service Error | Meta outage or server error | Check metastatus.com; retry with exponential backoff |

---

### Fix: Token Problems (Error 190, 3, 10)

**Diagnose first:**
```bash
curl "https://graph.facebook.com/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_APP_ID|YOUR_APP_SECRET"
```
Check `is_valid`, `expires_at` (0 = never expires), and `scopes` in the response.

**Fix — create a non-expiring System User token:**
1. Meta Business Manager → Settings → System Users
2. Create Admin system user
3. Add `whatsapp_business_messaging` + `whatsapp_business_management` permissions
4. Generate token — never set an expiry

---

### Fix: Phone Number Not Registered (Error 133010)

**Step 1 — check phone number status:**

```bash
curl "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID?fields=verified_name,code_verification_status,quality_rating,status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

If `status` is `PENDING`, the number is waiting for verification. Continue below.

**Step 2 — set up Two-Step Verification (choose ONE method):**

**Option A: Manual setup (easy)**
1. Meta Business Manager → WhatsApp Settings → Phone Numbers → Your Number
2. Click "Two-Step Verification" → set a PIN

**Option B: API setup (easier for automation)**

```bash
# Set 2FA PIN via API
curl -X POST \
  "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID/two_step_verification" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pin": "123456"}'  # any 6-digit PIN you choose
```

**Step 3 — register the number with the PIN:**

```bash
curl -X POST \
  "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID/register" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messaging_product": "whatsapp", "pin": "123456"}'  # same PIN from step 2
```

**Step 4 — wait 5 minutes, then verify registration:**

```bash
curl "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID?fields=verified_name,code_verification_status,quality_rating,status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Look for `status: REGISTERED` and `code_verification_status: VERIFIED`.

---

### Fix: Webhook Not Verifying

Diagnose in this order:

1. **Not returning raw challenge** — endpoint must return the `hub.challenge` string value only, not JSON
2. **Token mismatch** — `hub.verify_token` Meta sends must match exactly what you set in the dashboard (case-sensitive)
3. **SSL issue** — Meta requires a valid cert from a trusted CA; self-signed certs are rejected
4. **Timeout** — your server must respond within 10 seconds
5. **WABA not subscribed to App** — common silent failure since 2025 Meta UI change:

```bash
# Subscribe your WABA to your App (run once)
curl -X POST \
  "https://graph.facebook.com/v21.0/WABA_ID/subscribed_apps" \
  -H "Authorization: Bearer YOUR_SYSTEM_USER_TOKEN"

# Verify the subscription exists
curl "https://graph.facebook.com/v21.0/WABA_ID/subscribed_apps" \
  -H "Authorization: Bearer YOUR_SYSTEM_USER_TOKEN"
```

**Local development** — expose localhost with a tunnel:
```bash
# Using ngrok
ngrok http 3000
# Use the https:// URL ngrok provides as your webhook callback URL in Meta
```

---

### Fix: Rate Limiting (Error 130429)

Default limit is 80 messages per second. Fix with a queue and exponential backoff:

```javascript
// npm install limiter
const { RateLimiter } = require('limiter');
const limiter = new RateLimiter({ tokensPerInterval: 70, interval: 'second' });

async function sendWithRetry(phone, message, attempt = 0) {
    await limiter.removeTokens(1);
    try {
        return await sendMessage(phone, message);
    } catch (err) {
        const code = err.response?.data?.error?.code;
        if (code === 130429 && attempt < 5) {
            const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s, 8s, 16s
            await new Promise(r => setTimeout(r, delay));
            return sendWithRetry(phone, message, attempt + 1);
        }
        throw err;
    }
}
```

To increase throughput beyond 80 MPS, apply in Meta Business Manager → WhatsApp → Phone Numbers → Request Increased Messaging Limit.

---

### Fix: 24-Hour Window (Error 131047)

You cannot send free-form text to a user more than 24 hours after their last message. You must use a template.

```javascript
// Instead of free-form text, send an approved template
await sendTemplate(phoneNumber, 'order_update', 'en_US', [
    { type: 'text', text: 'John' },
    { type: 'text', text: '#4521' }
]);
```

Create and submit templates at: Meta Business Manager → WhatsApp → Message Templates.

---

### Fix: Template Rejected (Error 132001 or rejection in WhatsApp Manager)

| Rejection Reason | Fix |
|-----------------|-----|
| Variable format wrong | Use `{{1}}`, `{{2}}` — double curly braces, sequential integers only |
| Template starts/ends with variable | Add plain text before `{{1}}` and after the last variable |
| Variables not sequential | Must be `{{1}}`, `{{2}}` — no gaps allowed |
| URL shorteners used | Use full, unshortened URLs to your own domain |
| Language code mismatch | Match `language.code` to the actual content language, e.g. `en_US`, `pt_BR` |
| Warm language in utility template | Use formal transactional wording; warm language causes auto-reclassification to marketing category |
| Sensitive data | Never request SSNs, full card numbers, or passwords |
| Duplicate of existing template | Change the wording — even minor variation is required |
| Purpose unclear | Each variable must have a descriptive example value in the template submission |

**Where to find rejection reason:**
Meta Business Manager → Business Support Home → Your WhatsApp Account → Rejected Template Messages → view policy issue.

---

### Fix: Message Undeliverable (Error 131026)

Run this to check if a number has WhatsApp before sending:

```bash
curl "https://graph.facebook.com/v21.0/PHONE_NUMBER_ID/contacts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"messaging_product": "whatsapp", "contacts": ["+14155551234"]}'
# Response includes "wa_id" if the number has WhatsApp, empty if not
```

---

### Diagnose: "My message sends but the user never receives it" (first-contact trap)

This is the most common silent failure. The API returns success (`messages[0].id`) but the user receives nothing.

**Root cause:** You sent a free-form text message as the first outreach. Meta silently drops it.

**How to tell:** Check the message status webhook — the message will show `failed` with error `131047` or show `sent` but never `delivered`.

**Rule:** The very first message your app sends to any number must be a template. No exceptions.

```
❌ Wrong — app sends free-form text first:
   POST /messages → type: "text", body: "Hello John, your order is ready"
   → API may return 200 but message is silently dropped or returns 131047

✅ Correct — app sends template first:
   POST /messages → type: "template", name: "order_ready"
   → User receives the message and can reply
   → After user replies, free-form text is allowed for 24h
```

**Fix:** Create and approve a template for every type of first-contact message you need to send. Submit templates at Meta Business Manager → WhatsApp → Message Templates.

---

---

## Practical Patterns from Production

### Phone Number Validation Before Sending

Always validate phone number format and WhatsApp registration before sending:

```python
def is_valid_phone_format(phone_digits: str) -> bool:
    """
    E.164 format validation:
      - 7-15 digits (not including +)
      - Not all same digit (e.g., 0000000 is invalid)
    """
    if not phone_digits or len(phone_digits) < 7 or len(phone_digits) > 15:
        return False
    if len(set(phone_digits)) == 1:  # all same digit
        return False
    return True

def is_registered_on_whatsapp(phone_digits: str, token: str, phone_id: str) -> bool:
    """
    Check if number is a registered WhatsApp user.
    Returns False only on definitive error 131026 (not on WhatsApp).
    Returns True if successful, uncertain (auth error, etc.), or timeout.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": phone_digits,
        "type": "text",
        "text": {"body": "_"}  # minimal text to check
    }
    try:
        r = requests.post(
            f"https://graph.facebook.com/v21.0/{phone_id}/messages",
            headers=headers,
            json=data,
            timeout=10
        )
        if r.status_code == 200:
            return True  # number is valid

        error_code = r.json().get("error", {}).get("code")
        if error_code == 131026:
            return False  # NOT on WhatsApp

        return True  # other errors — don't block
    except:
        return True  # network error — don't block
```

### Structured Error Response Handling

```python
def extract_error_code(response_json: dict) -> int:
    """Extract error code from Meta API response."""
    return (
        response_json.get("error", {}).get("code")
        or response_json.get("error", {}).get("error_subcode")
    )

def send_with_error_handling(phone_id: str, recipient: str, message_body: str, token: str):
    """Send message and extract detailed error info."""
    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message_body}
    }

    try:
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        return {"success": True, "message_id": r.json().get("messages")[0].get("id")}
    except requests.HTTPError as e:
        error_code = extract_error_code(e.response.json())
        error_msg = e.response.json().get("error", {}).get("message")
        return {
            "success": False,
            "error_code": error_code,
            "error_message": error_msg,
            "response_text": e.response.text
        }
```

### Interactive Messages (Smart Buttons vs List)

```python
def send_interactive_message(phone_id: str, recipient: str, text: str, options: list, token: str):
    """
    Intelligently sends:
      - Buttons (up to 3 options)
      - List Menu (4-10 options)

    Each option: {"id": "unique_id", "title": "Text (max 20 chars)"}
    """
    url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if len(options) <= 3:
        # Send as buttons
        button_data = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": opt["id"], "title": opt["title"][:20]}
                        }
                        for opt in options
                    ]
                }
            }
        }
        return requests.post(url, headers=headers, json=button_data)
    else:
        # Send as list menu
        list_data = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": text},
                "action": {
                    "button": "See options",
                    "sections": [{
                        "title": "Available options",
                        "rows": [
                            {
                                "id": opt["id"],
                                "title": opt["title"][:24]
                            }
                            for opt in options
                        ]
                    }]
                }
            }
        }
        return requests.post(url, headers=headers, json=list_data)
```

### Testing & Debugging Helper Scripts

**Token & Phone Verification Script:**
```python
# Check if token is valid and phone number is accessible
import requests, os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_ID = os.getenv('PHONE_NUMBER_ID')

# Debug token
r = requests.get(f"https://graph.facebook.com/debug_token?input_token={TOKEN}&access_token={TOKEN}")
data = r.json()
if 'error' in data:
    print(f"❌ Token Error: {data['error']['message']}")
else:
    print(f"✅ Token Valid")
    print(f"   Expires: {data['data'].get('expires_at')} (0=never)")
    print(f"   Scopes: {data['data'].get('scopes')}")

# Check phone number
r = requests.get(
    f"https://graph.facebook.com/v21.0/{PHONE_ID}",
    headers={"Authorization": f"Bearer {TOKEN}"}
)
if r.status_code == 200:
    print(f"✅ Phone Number Accessible")
    print(f"   Display: {r.json().get('display_phone_number')}")
    print(f"   Quality Rating: {r.json().get('quality_rating')}")
else:
    print(f"❌ Phone Error: {r.json().get('error', {}).get('message')}")
```

---

## Quick Debug Checklist

When a message fails, check in this order:

1. **Token valid?** — `curl "https://graph.facebook.com/debug_token?input_token=TOKEN&access_token=APP_ID|APP_SECRET"`
2. **Phone number format?** — E.164, no `+`, no spaces: `"14155551234"`
3. **Number registered in WABA?** — check WhatsApp Manager → Phone Numbers
4. **Number registered with Cloud API?** — run registration call if error 133010
5. **24h window?** — if > 24h since last user reply, send a template instead
6. **Template approved?** — WhatsApp Manager → Message Templates → check status and rejection reason
7. **Webhook subscribed?** — verify WABA → App subscription via `GET /WABA_ID/subscribed_apps`
8. **Rate limited?** — check Quality Rating in WhatsApp Manager; implement backoff + queue
