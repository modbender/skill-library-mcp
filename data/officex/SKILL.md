---
name: officex
description: |
  Complete OfficeX platform skill for end-user consumers and app developers interacting with
  the OfficeX REST API. Covers the full credit-based app marketplace ("Netflix meets Costco
  for business apps"). Use when: (1) Making HTTP calls to OfficeX cloud API, (2) Building or
  publishing apps on the platform, (3) Implementing billing (reserve/settle/sip/payout),
  (4) Managing users, installs, wallets, (5) Handling webhooks (INSTALL/UNINSTALL/RATE_LIMIT_CHANGE),
  (6) Embedding apps in iframes, (7) Integrating with the AI chat agent (agent_context,
  documentation, context_prompt), (8) Debugging API errors or auth issues.
  Triggers on: officex, cloud officex, credit economy, app marketplace, reserve credits,
  settle, sip, install app, master key, install secret, wallet, vendor inbox, payout,
  voucher, OTP, register user, register app, webhook, iframe, agent context, billing pattern.
---

# OfficeX Platform

OfficeX is a membership-based app store. Users buy credits ($0.03 each: $0.02 profit + $0.01 ecosystem liability). Apps charge credits via reserve/settle. Vendors earn credits and payout to fiat (USDC on Solana or bank transfer, $0.01/credit).

**Get your credentials at:** https://officex.app/store/en/developer/

## Environments

| Env                   | API Base                                       | Chat Stream                               |
| --------------------- | ---------------------------------------------- | ----------------------------------------- |
| **Staging** (default) | `https://staging-backend.cloud.officex.app/v1` | `https://chat-staging.cloud.officex.app/` |
| **Production**        | `https://cloud.officex.app/v1`                 | `https://chat.cloud.officex.app/`         |

## Authentication

| Mode                 | Headers                                                               | Scope                                    |
| -------------------- | --------------------------------------------------------------------- | ---------------------------------------- |
| None                 | —                                                                     | Public catalog, vouchers, auth endpoints |
| Master Key           | `x-officex-user-id` + `x-officex-master-key`                          | Profile, installs, wallets, vendor apps  |
| Install Secret       | `x-officex-install-id` + `x-officex-install-secret`                   | Billing: reserve, settle, cancel, inbox  |
| Install Secret (alt) | `x-officex-user-id` + `x-officex-app-id` + `x-officex-install-secret` | Same as above (alternative lookup)       |
| Superadmin           | `x-officex-admin-secret`                                              | Full system (`/admin/*`)                 |

Install Secret is **billing only** — your app manages its own user authentication separately. The install secret handles the money, your app handles everything else.

## Credit Economy

```
User buys credits → Treasury liability increases (zero-sum: Treasury + all wallets = 0)
App reserves credits → Locked from user wallet
App sips/settles → Credits move to app wallet
Vendor payouts → Credits converted to fiat, Treasury liability decreases
```

### Decimal Credits

Credits support **decimals**. Rounding up to 1 credit ($0.03) is expensive for small operations:

| Operation   | Credits | User Pays |
| ----------- | ------- | --------- |
| Micro task  | 0.1     | $0.003    |
| Small task  | 0.25    | $0.0075   |
| Medium task | 0.5     | $0.015    |
| Standard    | 1.0     | $0.03     |

**Best practice:** Price based on actual cost. If an API call costs $0.001, charge ~0.07 credits (2x markup).

### Dual Roles

A single OfficeX account can be both **Consumer** (install and use apps) and **Vendor** (create apps and earn credits).

---

## API Endpoints

### Auth (No Auth)

```
POST /auth/register              { email }                     → { success, message }
POST /auth/login                 { email, password? }          → { success, api_key?, user_id? }
POST /auth/verify-otp            { email, code }               → { success, api_key, user_id, wallet_id? }
POST /auth/resend                { email }                     → { success, message }
POST /auth/forgot-password       { email }                     → { success, message }
POST /auth/reset-password        { email, code, new_password } → { success, message }
POST /auth/set-password          { password }            [MK]  → { success, message }
POST /auth/rotate-key            { email }                     → { success, message }
POST /auth/confirm-rotate-key    { email, code }               → { success, api_key }
POST /register-user              { email }                     → { user_id, wallet_id, api_key }  (legacy)
```

**Testing mode:** OTP hardcoded to `0000`, email sending disabled.

### User Profile [Master Key]

```
GET    /users/me                                → { user: { user_id, email, wallet_id, status } }
PATCH  /users/me                 { email? }     → { user }
POST   /users/me/rotate-key     { new_master_key } → { success }
GET    /users/me/vouchers                       → { vouchers[] }
```

### Installations [Master Key]

```
GET    /users/me/installs                       → { installs[] }
GET    /users/me/installs/{id}                  → { install (with usage stats) }
POST   /install/{app_id_or_slug} { max_per_hour?, max_per_day?, max_per_month?, allowed_until? }
                                                → { app_id, install_id, install_secret, agent_context? }  ⚠️ secret shown once
DELETE /users/me/installs/{id}                  → { success }
PATCH  /users/me/installs/{id}  { max_per_hour?, max_per_day?, max_per_month?, allowed_until?, lifetime_spend_limit? }
                                                → { install }
POST   /users/me/installs/{id}/rotate-secret    → { install_secret }
PATCH  /users/me/installs/{id}/context  { key: val | null } → { agent_context }
```

`allowed_until`: unix timestamp (-1 = never, default = now + 30d). `lifetime_spend_limit`: -1 = unlimited.

App-scoped routes (Install Secret auth):

```
PATCH  /installs/{install_id}/context  { key: val | null } → { agent_context }
POST   /installs/{install_id}/inbox    { id, title, text, url?, icon? } → { message_id }
```

### Vendor Apps [Master Key]

```
GET    /users/me/apps                           → { apps[] }
POST   /register-app             (see full schema below)
                                                → { app_id, destination_wallet_id }
GET    /users/me/apps/{app_id}                  → { app }
PATCH  /users/me/apps/{app_id}   (see full schema below)
                                                → { app }
DELETE /users/me/apps/{app_id}                  → { success }
GET    /users/me/apps/{app_id}/inbox            → { reservations[], pagination? }
POST   /users/me/apps/{app_id}/inbox/{log_id}/ack → { success }
GET    /users/me/apps/{app_id}/installs         → { installs[] }
```

### Public Catalog (No Auth)

```
GET    /apps                                    → { apps[], pagination? }
GET    /apps/{app_id}                           → { app }
```

### Credits & Balance [Master Key]

```
POST   /purchase-credits         { amount, payment_method: { type, token }, idempotency_key? }
                                                → { credits_added, new_balance, transaction_id }
GET    /balance                                 → { wallet_id, available, reserved, total }
```

### Reserve & Settle [Install Secret]

```
POST   /reserve                  { amount, job_id, metadata? }
                                                → { reservation_id, amount_reserved }
POST   /settle                   { reservation_id, amount, final? }
                                                → { settled_amount, remaining_reserved, status }
GET    /reservations/{id}                       → { reservation }
POST   /reservations/{id}/cancel                → { refunded_amount, status }
POST   /reservations/{id}/settle { amount, final? } → { settled_amount, status }
```

`final: true` = complete + refund remainder. `final: false` (default) = sip (partial).

Reserve errors: `INSTALL_EXPIRED`, `RATE_LIMITED`, `INSUFFICIENT_FUNDS`, `DUPLICATE_JOB`, `LIFETIME_LIMIT_REACHED`

### Wallets [Master Key]

```
GET    /wallets/{id}                            → { wallet_id, available, reserved, total, owner_type }
GET    /wallets/{id}/transactions  ?limit=&cursor= → { transactions[], pagination? }
GET    /wallets/{id}/transactions/{log_id}      → { transaction }
GET    /wallets/{id}/reservations  ?direction=   → { reservations[] }
GET    /wallets/{id}/reservations/{resv_id}     → { reservation }
GET    /wallets/{id}/payouts                    → { payouts[] }
GET    /wallets/{id}/payouts/{payout_id}        → { payout }
```

### Payouts [Master Key]

```
POST   /payout                   { wallet_id, amount, destination: { type, account_id }, idempotency_key? }
                                                → { payout_id, status }
```

Payout state machine: `pending → burned → completed | failed` (failed = credits restored). Frequency: end of every month. Rate: $0.01 per credit.

### Vouchers

```
GET    /vouchers/{code}                         → { voucher }           (No Auth)
POST   /vouchers/{code}/redeem   { wallet_id }  → { credits_added }    [Master Key]
```

### Chat [Master Key]

```
GET    /users/me/chats  ?project_id=&tracer_id= → { threads[] }
POST   /users/me/chats           { title?, project_id?, tracer_id? }     → { thread }
GET    /users/me/chats/{id}                     → { thread, messages[] }
PATCH  /users/me/chats/{id}      { title?, tracer_id?: string|null }      → { thread }
DELETE /users/me/chats/{id}                     → { success }
```

Streaming (Function URL, NOT API Gateway):

```
POST   <CHAT_STREAM_URL>
Headers: x-officex-user-id, x-officex-master-key
Body: { messages[], thread_id?, project_id?, system_prompt?, tracer_id?, include_apps? }
Response: text/event-stream (SSE)
```

Stream protocol lines (emitted before SSE data):
- `t:{threadId}\n` — resolved thread ID (always emitted)
- `tracer:{tracerId}\n` — tracer ID (emitted when `tracer_id` present in request)
- `s:{json}\n` — status updates

### Inbox, Prompts, Refs, Uploads [Master Key]

```
GET    /users/me/inbox                          → { messages[] }
GET/POST/PATCH/DELETE /users/me/prompts[/{id}]  → prompt CRUD
GET    /refs/{slug}                             → { ref }  (No Auth)
GET/POST /users/me/refs[/{slug}]                → ref CRUD [Master Key]
POST   /uploads/presign { filename, content_type } → { presigned_url, key }
```

### Admin [Superadmin]

All under `/admin/*` with `x-officex-admin-secret`:

**Users:** `GET /admin/users`, `GET/PATCH /admin/users/{id}`, `GET /admin/users/{id}/wallets`
**Apps:** `GET /admin/apps`, `GET/PATCH/DELETE /admin/apps/{id}`
**Wallets:** `GET /admin/wallets`, `GET /admin/wallets/{id}`, `POST /admin/wallets/{id}/adjust { amount }`
**Treasury:** `GET /admin/treasury`, `POST /admin/reconcile`, `GET /admin/audit`
**Payouts:** `GET /admin/payouts`, `GET /admin/payouts/{id}`, `POST /admin/payouts/{id}/approve`, `POST /admin/payouts/{id}/reject`
**Vouchers:** `POST /admin/vouchers`, `GET /admin/vouchers`, `GET/PATCH/DELETE /admin/vouchers/{code}`

## Error Format

```json
{ "success": false, "error": { "code": "ERROR_CODE", "message": "..." } }
```

| Code                     | HTTP | Description                                 |
| ------------------------ | ---- | ------------------------------------------- |
| `UNAUTHORIZED`           | 401  | Missing or invalid auth headers             |
| `INVALID_SECRET`         | 401  | Secret doesn't match hash                   |
| `INVALID_REQUEST`        | 400  | Malformed request body                      |
| `APP_NOT_FOUND`          | 404  | App doesn't exist                           |
| `USER_NOT_FOUND`         | 404  | User doesn't exist                          |
| `WALLET_NOT_FOUND`       | 404  | Wallet doesn't exist                        |
| `RESERVATION_NOT_FOUND`  | 404  | Reservation doesn't exist                   |
| `INSTALL_NOT_FOUND`      | 404  | Installation doesn't exist                  |
| `INSTALL_EXPIRED`        | 403  | Billing authorization expired               |
| `RATE_LIMITED`           | 429  | Exceeded rate limit                         |
| `INSUFFICIENT_FUNDS`     | 402  | Wallet balance too low                      |
| `LIFETIME_LIMIT_REACHED` | 403  | Cumulative spending exceeds lifetime limit  |
| `FORBIDDEN`              | 403  | Accessing another user's resources          |
| `DUPLICATE_REQUEST`      | 409  | Idempotency key collision                   |
| `DUPLICATE_JOB`          | 409  | Job ID already has reservation              |
| `PREVIOUS_FAILURE`       | 409  | Idempotency collision (failed, use new key) |
| `PAYMENT_FAILED`         | 402  | External payment rejected                   |
| `PAYOUT_FAILED`          | 500  | Fiat transfer failed                        |
| `INTERNAL_ERROR`         | 500  | Unexpected server error                     |

## Using 3rd Party Apps

Whenever you use an app on OfficeX, you can grab the agent_context from the app installation. This may give you app secrets to interact with their REST API. However, not all apps might have it. Every app has their own skill.md that you can copy online or request via OfficeX API.

---

## App Lifecycle (Developer Guide)

### 1. Create Your App

**Endpoint:** `POST /register-app` [Master Key]

```typescript
{
  name: string,                    // Required: 3-50 chars
  description?: string,
  price_type?: "FREE" | "PAY_PER_USE" | "ONE_TIME" | "SUBSCRIPTION" | "MIXED",
  webhook_url?: string,            // HTTPS URL for lifecycle events
  suggested_rate_limits?: { max_per_hour?, max_per_day?, max_per_month?, expires_at? },
  minimum_rate_limits?: { max_per_hour?, max_per_day?, max_per_month?, expires_at? },
  subtitle?: string,               // Max 200 chars
  category?: string,               // Max 50 chars
  developer?: string,
  app_url?: string,
  iframe_url?: string,             // URL for embedded iframe experience
  support_url?: string,
  contact_email?: string,
  context_prompt?: string,         // AI agent instructions (max 5000 chars)
  documentation?: string,          // API docs for AI agent (max 50000 chars)
  pricing_lines?: string[],        // Max 10 items, 100 chars each
  tags?: string[],                 // Max 10
  icon?: { type: "emoji" | "image", content: string },
  inAppPurchases?: boolean
}
// Response (201): { success, app_id, destination_wallet_id, message }
```

**Example:**

```bash
curl -X POST https://cloud.officex.app/v1/register-app \
  -H "Content-Type: application/json" \
  -H "x-officex-user-id: $OFFICEX_USER_ID" \
  -H "x-officex-master-key: $OFFICEX_API_KEY" \
  -d '{
    "name": "Lead Enrichment Pro",
    "description": "Enrich B2B leads with company data",
    "price_type": "PAY_PER_USE",
    "subtitle": "B2B lead enrichment powered by AI",
    "category": "Marketing",
    "developer": "Acme Corp",
    "webhook_url": "https://myapp.com/webhooks/officex",
    "iframe_url": "https://myapp.com/officex",
    "documentation": "## API Reference\n\nThis app enriches leads...",
    "context_prompt": "This app enriches B2B leads. When the user asks to enrich leads, call the /enrich endpoint.",
    "suggested_rate_limits": { "max_per_hour": 50, "max_per_day": 200, "max_per_month": 2000 },
    "pricing_lines": ["5 credits per lead enrichment", "Bulk discount: 3 credits for 10+ leads"]
  }'
```

Each app gets a **discrete wallet** (`destination_wallet_id`). Earnings go there, not your personal wallet. `documentation` is injected into the AI chat agent's system prompt. `context_prompt` provides additional instructions for the AI agent.

### 2. Update Your App

**Endpoint:** `PATCH /users/me/apps/{app_id}` [Master Key] — All fields optional, set to `null` to clear:

```typescript
{
  name?, description?, price_type?, webhook_url?, iframe_url?, app_url?,
  subtitle?, category?, developer?, support_url?, contact_email?,
  context_prompt?, documentation?, pricing_lines?, tags?,
  icon?, previews?, icon_url?, preview_images?, youtube_url?,
  suggested_rate_limits?, minimum_rate_limits?, inAppPurchases?
}
```

### 3. List App's Installs (Vendor View)

**Endpoint:** `GET /users/me/apps/{app_id}/installs` [Master Key]

```typescript
// Response (200)
{
  success: true,
  installs: Array<{
    user_id: string, install_id: string, nickname?: string, status: string,
    installed_at: string, max_per_hour: number, max_per_day: number,
    max_per_month: number, allowed_until: number,
    usage: { hour: number, day: number, month: number }
  }>
}
```

---

## Installation Flow (When Users Install Your App)

When a user installs your app, OfficeX:

1. Creates an **Installation Record** linking user to app
2. Generates an **Install ID** and **Install Secret** (scoped billing credentials)
3. Sets **rate limits** (user-specified or your suggested defaults)
4. Sets **allowed_until** expiry (default: 30 days, or `-1` for no expiry)
5. Fires an **INSTALL webhook** to your `webhook_url` (if configured)

The install endpoint accepts both `app_id` (UUID) and `slug` (string) in the path parameter.

---

## Webhook Events

Your app receives lifecycle events at `webhook_url`. Envelope: `{ event, payload, uuid }`.

**INSTALL Event:**

```json
{
  "event": "INSTALL",
  "payload": {
    "install_id": "uuid-of-installation",
    "install_secret": "base64url-encoded-secret",
    "user_id": "uuid-of-user",
    "app_id": "uuid-of-your-app",
    "email": "user@example.com",
    "timestamp": "2025-01-25T10:30:00Z"
  },
  "uuid": "unique-request-id"
}
```

**UNINSTALL Event:** payload: `{ install_id, user_id, app_id, timestamp }`

**RATE_LIMIT_CHANGE Event:** payload: `{ install_id, user_id, app_id, max_per_hour, max_per_day, max_per_month, allowed_until, timestamp }`

**Webhook Response:** Your response for `INSTALL` can include `agent_context` (only this key is extracted). Values are stored on the installation and injected into the user's AI agent prompt:

```json
{
  "agent_context": {
    "api_key": "sk-abc123",
    "workspace_id": "ws-456",
    "base_url": "https://myapp.com/api/v1"
  }
}
```

**Delivery:** POST, `application/json`, 25s timeout, fire-and-forget (no retries in v1).

> **Note:** Not all apps need a webhook. Apps where the user supplies their own credentials (e.g., Telegram bot token) can skip the webhook entirely and use `PATCH /installs/{install_id}/context` from within the app UI post-install. See [Agent Context](#agent-context-ai-chat-integration) for details.

---

## Credit Billing System

### The Reserve → Sip → Settle Pattern

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RESERVE   │────►│     SIP     │────►│   SETTLE    │
│  Lock funds │     │  Progressive│     │  Finalize   │
│  for job    │     │  billing    │     │  + refund   │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
                          ▼ (if job fails)
                    ┌─────────────┐
                    │   CANCEL    │
                    │  Full refund│
                    └─────────────┘
```

### Reserve (Lock Funds)

`POST /reserve` [Install Secret]

```typescript
// Request
{ amount: number, job_id: string, metadata?: Record<string, unknown> }
// Response (200)
{ success: true, reservation_id: string, amount_reserved: number }
```

```bash
curl -X POST https://cloud.officex.app/v1/reserve \
  -H "Content-Type: application/json" \
  -H "x-officex-install-id: $INSTALL_ID" \
  -H "x-officex-install-secret: $INSTALL_SECRET" \
  -d '{ "amount": 10, "job_id": "lead-enrich-job-12345", "metadata": { "leads_count": 50 } }'
```

Internally: user's `wallet.available` decreases, `wallet.reserved` increases, creates `RESV#<job_id>`.

| Error Code               | Meaning                               |
| ------------------------ | ------------------------------------- |
| `INSTALL_EXPIRED`        | `allowed_until` timestamp has passed  |
| `LIFETIME_LIMIT_REACHED` | Cumulative spending exceeds limit     |
| `RATE_LIMITED`           | Hourly/daily/monthly limit exceeded   |
| `INSUFFICIENT_FUNDS`     | Not enough available credits          |
| `DUPLICATE_JOB`          | This job_id already has a reservation |

### Sip (Progressive Settlement)

`POST /reservations/{reservation_id}/settle` (or `POST /settle`) [Install Secret]

```typescript
// Request (partial)
{ amount: number, final: false }
// Response (200)
{ success: true, settled_amount: number, remaining_reserved: number, status: "partial" }
```

Example — enriching 100 leads:

```
Reserve 100 credits
├── Sip 10 (processed 10 leads) → settled: 10, reserved: 90
├── Sip 10 (processed 20 leads) → settled: 20, reserved: 80
├── Sip 10 (processed 30 leads) → settled: 30, reserved: 70
└── Settle final 70 → settled: 100, reserved: 0, status: "completed"
```

### Settle (Final)

```typescript
// Request (final)
{ amount: number, final: true }
// Response (200)
{ success: true, settled_amount: number, remaining_reserved: number, status: "completed" }
```

Remaining reserved funds (if any) are refunded to user. Credits move to your app's wallet.

### Cancel (Full Refund)

`POST /reservations/{reservation_id}/cancel` [Install Secret]

```typescript
// Response (200)
{ success: true, refunded_amount: number, status: "cancelled" }
```

---

## Rate Limits & Allowances

Rate limits are **per (user, app) pair** — each installation has independent limits.

| Window  | Default           | Description       |
| ------- | ----------------- | ----------------- |
| Hourly  | 100 reservations  | Resets each hour  |
| Daily   | 300 reservations  | Resets each day   |
| Monthly | 1000 reservations | Resets each month |

**Minimum rate limits** (developer-set floor): Users cannot go below these values.

**`allowed_until`**: Unix timestamp (-1 = never expires, default = now + 30 days). When expired, all `/reserve` calls fail with `INSTALL_EXPIRED`. Enables **pseudo-subscription billing**.

**`lifetime_spend_limit`**: Total credits an app can ever charge across all time. Set to `-1` for unlimited. Fails with `LIFETIME_LIMIT_REACHED` when exceeded.

| App Type         | Suggested Hourly | Daily | Monthly |
| ---------------- | ---------------- | ----- | ------- |
| Lead enrichment  | 50               | 200   | 2000    |
| Data export      | 10               | 50    | 200     |
| AI generation    | 20               | 100   | 1000    |
| Real-time lookup | 100              | 500   | 5000    |

---

## Agent Context (AI Chat Integration)

When users chat with OfficeX AI, the agent receives your app's `documentation` and `context_prompt`. Store per-install credentials via:

`PATCH /users/me/installs/{install_id}/context` [Master Key] or `PATCH /installs/{install_id}/context` [Install Secret]

```typescript
// Request: Record<string, string | null> (null deletes key)
{ "api_key": "sk-abc123", "workspace_id": "ws-456" }
// Response (200)
{ success: true, agent_context: { "api_key": "sk-abc123", "workspace_id": "ws-456" } }
```

Validation: Max 50 keys, 200 chars/key, 1000 chars/value.

**Two patterns for setting `agent_context`:**

1. **Webhook-response (auto):** Return credentials in your INSTALL webhook response → auto-applied as `agent_context`. Best for apps that provision credentials server-side on install.

2. **Post-install from app UI (manual):** App collects credentials from the user inside its own iframe/UI after install, then PATCHes them via install secret auth. Best for apps where the **user supplies their own API key/token** (e.g., Telegram bot token, OpenAI key, Stripe key). Flow:
   - User installs app (no extra params needed)
   - User opens app → enters their credentials in the app's UI
   - App calls `PATCH /installs/{install_id}/context` with install secret auth
   - Credentials are stored on the installation → available to AI agent via `load_app_skill`

```
# App-side context update (install secret auth)
PATCH /v1/installs/{install_id}/context
Headers: X-Officex-Install-Id: {install_id}, X-Officex-Install-Secret: {install_secret}
Body: { "telegram_bot_token": "123456:ABC-DEF..." }
→ { success: true, agent_context: { "telegram_bot_token": "123456:ABC-DEF..." } }
```

---

## Sending Inbox Messages

Notify users about job status, results, or important updates:

`POST /installs/{install_id}/inbox` [Install Secret]

```typescript
// Request
{
  id: string,          // Idempotency key (unique per app+user)
  title: string,       // Max 200 chars
  text: string,        // Max 2000 chars
  url?: string,        // Link to results
  icon?: string        // Icon URL
}
// Response (201) — New message
{ success: true, message_id: string }
// Response (200) — Deduplicated
{ success: true, message_id: string, deduplicated: true }
```

```bash
curl -X POST https://cloud.officex.app/v1/installs/$INSTALL_ID/inbox \
  -H "Content-Type: application/json" \
  -H "x-officex-install-id: $INSTALL_ID" \
  -H "x-officex-install-secret: $INSTALL_SECRET" \
  -d '{
    "id": "job-12345-complete",
    "title": "Lead Enrichment Complete",
    "text": "Successfully enriched 50 leads. 3 could not be found.",
    "url": "https://myapp.com/results/12345"
  }'
```

---

## Billing Patterns

### Pattern 1: Free Apps

No reservations needed. Use inbox messages to communicate.

### Pattern 2: One-Time Purchase

Reserve and settle immediately for discrete actions:

```typescript
const reservation = await reserve({ amount: 0.5, job_id: `enrich-${leadId}` });
const result = await enrichLead(leadId);
await settle({ amount: 0.5, final: true });
```

### Pattern 3: Usage-Based (Progressive Sip)

For long-running jobs, bill incrementally:

```typescript
const reservation = await reserve({ amount: 10, job_id: `batch-${batchId}` });
for (const item of items) {
  await processItem(item);
  await settle({ amount: 0.1, final: false }); // sip per item
}
await settle({ amount: 0, final: true }); // finalize, refund unused
```

### Pattern 4: Subscription-like

Use `allowed_until` for time-based access:

```typescript
if (
  install.allowed_until !== -1 &&
  Date.now() / 1000 >= install.allowed_until
) {
  return { error: "Please renew your subscription" };
}
```

### Pattern 5: Internal Credits System (Recommended)

Decouple your app from OfficeX API by maintaining your own internal ledger:

1. Reserve + settle OfficeX credits in bulk
2. Mint equivalent internal credits in your DB
3. Your app logic consumes internal credits only — no OfficeX API calls during normal operation

```
OfficeX Credits (external)          Your App Credits (internal)
┌─────────────────────┐             ┌─────────────────────┐
│ User's OfficeX      │  reserve    │                     │
│ wallet              │────────────►│  (funds locked)     │
│                     │  settle     │  Internal ledger    │
│                     │────────────►│  += settled amount  │
│                     │             │  App consumes from  │
│                     │             │  internal ledger    │
└─────────────────────┘             └─────────────────────┘
```

```typescript
async function settleAndMintCredits(
  reservationId,
  installId,
  installSecret,
  amount,
  final,
  userId,
) {
  const result = await fetch(
    `https://cloud.officex.app/v1/reservations/${reservationId}/settle`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-officex-install-id": installId,
        "x-officex-install-secret": installSecret,
      },
      body: JSON.stringify({ amount, final }),
    },
  ).then((r) => r.json());
  if (!result.success) throw new Error(result.error.message);
  await db.internalCredits.increment(userId, amount);
  return result;
}

// Reserve a block, settle immediately, user spends internal credits freely
const reservation = await reserve({
  amount: 50,
  job_id: `session-${sessionId}`,
});
await settleAndMintCredits(
  reservation.reservation_id,
  installId,
  installSecret,
  50,
  true,
  userId,
);
// Now user has 50 internal credits — no more OfficeX API calls needed
```

Benefits: decoupled from API availability, flexible internal pricing, auditability, batch funding, simpler error handling.

---

## Frontend Integration (Iframe Embedding)

When users launch your app from OfficeX, it loads in an iframe with credentials as URL params:

```
https://your-app.com/officex?officex_customer_id={user_id}&officex_install_id={install_id}&officex_install_secret={install_secret}
```

### Extracting Credentials

**JavaScript/TypeScript:**

```typescript
const params = new URLSearchParams(window.location.search);
const customerId = params.get("officex_customer_id");
const installId = params.get("officex_install_id");
const installSecret = params.get("officex_install_secret");

if (!installId || !installSecret) {
  showError("Please access this app through the OfficeX app store");
  return;
}
sessionStorage.setItem("officex_install_id", installId);
sessionStorage.setItem("officex_install_secret", installSecret);
```

**Python (Flask):**

```python
@app.route('/officex')
def officex_entry():
    install_id = request.args.get('officex_install_id')
    install_secret = request.args.get('officex_install_secret')
    if not install_id or not install_secret:
        return "Please access this app through OfficeX", 403
    session['officex_install_id'] = install_id
    session['officex_install_secret'] = install_secret
    return render_template('app.html')
```

### Required: Allow OfficeX to Embed Your App

Your app **must** allow the OfficeX domain to embed it via iframe:

```
Content-Security-Policy: frame-ancestors 'self' https://officex.app https://*.officex.app
```

**Next.js (next.config.js):**

```javascript
module.exports = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "Content-Security-Policy",
            value:
              "frame-ancestors 'self' https://officex.app https://*.officex.app",
          },
        ],
      },
    ];
  },
};
```

**Express.js:**

```typescript
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "frame-ancestors 'self' https://officex.app https://*.officex.app",
  );
  next();
});
```

Without this header: blank screen or console errors about "refused to frame."

**Security:**

- Never expose `install_secret` to users (use sessionStorage, not localStorage)
- Validate on backend for sensitive operations
- HTTPS required
- Handle missing params gracefully (users may bookmark deep links)

---

## Webhook Authentication Flow (SSO)

The INSTALL webhook enables seamless single sign-on:

```
User clicks "Install" → OfficeX POSTs webhook → Your app creates/links user
→ Returns agent_context → User launches iframe → Lookup by install_id → Authenticated!
```

### Implementing onInstall Authentication

**Step 1: Handle webhook:**

```typescript
app.post("/webhooks/officex", async (req, res) => {
  const { event, payload, uuid } = req.body;
  if (event === "INSTALL") {
    const { install_id, install_secret, user_id, app_id, email } = payload;
    let user = await db.users.findOne({ officex_user_id: user_id });
    if (!user) {
      user = await db.users.create({
        officex_user_id: user_id,
        officex_install_id: install_id,
        created_at: new Date(),
      });
    } else {
      await db.users.update(
        { officex_user_id: user_id },
        { officex_install_id: install_id },
      );
    }
    // Return agent_context — credentials the AI agent needs to call your API
    res.json({
      agent_context: {
        user_token: user.apiToken,
        base_url: "https://myapp.com/api/v1",
      },
    });
  } else {
    res.json({ received: true });
  }
});
```

**Step 2: Look up user when iframe loads:**

```typescript
app.get("/officex", async (req, res) => {
  const installId = req.query.officex_install_id;
  const customerId = req.query.officex_customer_id;
  const user = await resolveUser(installId, customerId);
  req.session.user = user;
  req.session.officex = {
    install_id: installId,
    install_secret: req.query.officex_install_secret,
  };
  res.redirect("/dashboard");
});
```

### Handling Webhook Failures

Webhooks are fire-and-forget (no retries). Always have a fallback:

```typescript
async function resolveUser(installId, customerId) {
  // Try install_id first (most specific)
  let user = await db.users.findOne({ officex_install_id: installId });
  if (user) return user;
  // Fall back to customer_id (they might have reinstalled)
  user = await db.users.findOne({ officex_user_id: customerId });
  if (user) {
    await db.users.update({ id: user.id }, { officex_install_id: installId });
    return user;
  }
  // No user found — create on-the-fly
  return await db.users.create({
    officex_user_id: customerId,
    officex_install_id: installId,
    created_at: new Date(),
  });
}
```

---

## Fault Tolerance

Your app should treat OfficeX as an **external payment layer**, not a core dependency.

**Principles:**

1. Wrap all OfficeX API calls in try/catch with timeouts (3-5 seconds)
2. Your app should function if all OfficeX code was removed — OfficeX is how you get paid, not your runtime
3. Use the Internal Credits pattern (Pattern 5) for maximum resilience

**Resilient billing wrapper:**

```typescript
async function safeReserve(installId, installSecret, amount, jobId) {
  try {
    const res = await fetch("https://cloud.officex.app/v1/reserve", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-officex-install-id": installId,
        "x-officex-install-secret": installSecret,
      },
      body: JSON.stringify({ amount, job_id: jobId }),
      signal: AbortSignal.timeout(5000),
    }).then((r) => r.json());
    if (!res.success) {
      console.error(`OfficeX reserve failed: ${res.error?.code}`, res.error);
      return res;
    }
    return res;
  } catch (err) {
    console.error("OfficeX API unreachable, queuing for retry:", err.message);
    await billingRetryQueue.enqueue({
      installId,
      amount,
      jobId,
      attemptedAt: new Date(),
    });
    return {
      success: false,
      error: { code: "OFFICEX_UNREACHABLE", message: err.message },
    };
  }
}
```

**Error handling for reservations:**

```typescript
async function reserveWithRetry(installId, amount, jobId) {
  try {
    return await reserve(installId, amount, jobId);
  } catch (error) {
    if (error.code === "INSTALL_EXPIRED") {
      await sendInboxMessage(installId, {
        id: `renew-${jobId}`,
        title: "Authorization Expired",
        text: "Please renew your authorization to continue.",
      });
    }
    if (error.code === "INSUFFICIENT_FUNDS") {
      await sendInboxMessage(installId, {
        id: `topup-${jobId}`,
        title: "Low Balance",
        text: `Need ${amount} credits. Please top up.`,
      });
    }
    if (error.code === "RATE_LIMITED") {
      await sendInboxMessage(installId, {
        id: `ratelimit-${jobId}`,
        title: "Rate Limit Reached",
        text: "You've hit your usage limit for this period.",
      });
    }
    throw error;
  }
}
```

**Practical guidelines:**

- Set aggressive timeouts (3-5 seconds) on all OfficeX API calls
- If reserve fails, consider letting user proceed and retrying billing later
- Webhooks are fire-and-forget — always have a fallback path (create users on-the-fly from iframe params)
- Consider a simple toggle to disable OfficeX billing during development/testing
- Log OfficeX errors instead of throwing unhandled exceptions

---

## Complete Integration Example

**1. Register app:**

```bash
curl -X POST https://cloud.officex.app/v1/register-app \
  -H "Content-Type: application/json" \
  -H "x-officex-user-id: $OFFICEX_USER_ID" \
  -H "x-officex-master-key: $OFFICEX_API_KEY" \
  -d '{
    "name": "My Awesome App",
    "price_type": "PAY_PER_USE",
    "webhook_url": "https://myapp.com/webhooks/officex",
    "iframe_url": "https://myapp.com/officex",
    "documentation": "## API\n\nCall POST /api/enrich with {leadId} to enrich a lead.",
    "context_prompt": "This app enriches leads. Use the /api/enrich endpoint."
  }'
```

**2. Handle webhook:**

```typescript
app.post("/webhooks/officex", async (req, res) => {
  const { event, payload } = req.body;
  if (event === "INSTALL") {
    const user = await db.users.upsert({
      officex_user_id: payload.user_id,
      officex_install_id: payload.install_id,
      officex_install_secret: payload.install_secret,
      email: payload.email,
    });
    return res.json({
      agent_context: {
        api_key: user.apiKey,
        base_url: "https://myapp.com/api/v1",
      },
    });
  }
  res.json({ ok: true });
});
```

**3. Handle iframe entry:**

```typescript
app.get("/officex", async (req, res) => {
  const user = await resolveUser(
    req.query.officex_install_id,
    req.query.officex_customer_id,
  );
  req.session.user = user;
  req.session.officex = {
    install_id: req.query.officex_install_id,
    install_secret: req.query.officex_install_secret,
  };
  res.redirect("/dashboard");
});
```

**4. Bill from your app:**

```typescript
app.post("/api/enrich-lead", async (req, res) => {
  const { install_id, install_secret } = req.session.officex;
  const { leadId } = req.body;

  const reservation = await safeReserve(
    install_id,
    install_secret,
    5,
    `enrich-${leadId}-${Date.now()}`,
  );
  if (!reservation.success)
    return res.status(400).json({ error: reservation.error });

  const enrichedData = await enrichLead(leadId);

  await fetch(
    `https://cloud.officex.app/v1/reservations/${reservation.reservation_id}/settle`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-officex-install-id": install_id,
        "x-officex-install-secret": install_secret,
      },
      body: JSON.stringify({ amount: 5, final: true }),
    },
  );

  res.json({ success: true, data: enrichedData });
});
```

---

## Quick Start Workflows

**Consumer — Register + Fund + Install:**

```bash
curl -X POST $BASE/auth/register -d '{"email":"user@example.com"}'
curl -X POST $BASE/auth/verify-otp -d '{"email":"user@example.com","code":"0000"}'
# → { api_key, user_id, wallet_id }
curl -X POST $BASE/purchase-credits -H "x-officex-user-id: $UID" -H "x-officex-master-key: $KEY" \
  -d '{"amount":1000,"payment_method":{"type":"stripe","token":"tok_xxx"}}'
curl -X POST $BASE/install/$APP_ID -H "x-officex-user-id: $UID" -H "x-officex-master-key: $KEY"
# → { install_id, install_secret }
```

**Developer — Register App + Billing:**

```bash
curl -X POST $BASE/register-app -H "x-officex-user-id: $UID" -H "x-officex-master-key: $KEY" \
  -d '{"name":"My App","price_type":"PAY_PER_USE","webhook_url":"https://myapp.com/webhooks/officex"}'
# → { app_id, destination_wallet_id }

# From app server (using install secret from webhook):
curl -X POST $BASE/reserve -H "x-officex-install-id: $IID" -H "x-officex-install-secret: $SEC" \
  -d '{"amount":10,"job_id":"job-1"}'
curl -X POST $BASE/settle -H "x-officex-install-id: $IID" -H "x-officex-install-secret: $SEC" \
  -d '{"reservation_id":"RESV#job-1","amount":8,"final":true}'
# 2 credits refunded to user, 8 credited to app wallet
```

**Vendor Payout:**

```bash
curl -X POST $BASE/payout -H "x-officex-user-id: $UID" -H "x-officex-master-key: $KEY" \
  -d '{"wallet_id":"$APP_WALLET","amount":500,"destination":{"type":"stripe","account_id":"acct_xxx"}}'
```

## Tracers (Cross-Thread Correlation)

A `tracer_id` is a string (format: `trc_{timestamp36}-{random}`) that links causally-related threads and schedule runs. Use cases: schedule runs weekly → each run creates a thread → all threads share one `tracer_id` → frontend can render a unified timeline.

**Where `tracer_id` appears:**

- **Threads:** `POST /users/me/chats` body accepts `tracer_id`. `GET /users/me/chats?tracer_id=trc_xxx` filters by tracer. `PATCH` can set/clear it (`null` to remove).
- **Schedules:** `POST /users/me/schedules` body accepts `tracer_id` (auto-generated as `trc_*` if omitted). All schedule responses include it.
- **Schedule Runs:** Each run record includes `tracer_id` copied from the schedule.
- **Chat Stream:** Body accepts `tracer_id`. Stream protocol emits `tracer:{tracerId}\n` after `t:{threadId}\n`.

**Example flow:**
1. Create schedule → `tracer_id: "trc_abc123"` auto-generated
2. Schedule runs → creates thread with `tracer_id: "trc_abc123"`
3. Query `GET /users/me/chats?tracer_id=trc_abc123` → returns all threads from this schedule

---

## FAQ

**How do I test without real money?** Use vouchers via admin panel or test voucher codes.

**Can my app have multiple pricing tiers?** Yes. Your app logic decides how many credits to reserve per action.

**What happens if my webhook is down?** Webhooks are fire-and-forget. Handle gracefully by polling installation status or creating users on-the-fly from iframe params.

**Can I transfer credits between apps I own?** No. Credits only flow through reservation/settlement. Each app wallet is independent.

**How do I handle long-running jobs that fail?** Reserve upfront, sip as work completes, cancel on failure (refunds all unsettled credits), send inbox message explaining what happened.

**How does the AI chat agent interact with my app?** The agent receives your `documentation` and `context_prompt`. If `agent_context` has credentials, the agent calls your API via `http_request` tool. Make sure docs include clear API instructions.
