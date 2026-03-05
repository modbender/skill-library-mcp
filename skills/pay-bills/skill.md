# SKILL.md — CreditWithBleon API

Buy data, airtime, and digital products for Nigerian phone numbers via wallet balance.

**Base URL:** https://lodu.bleon.net/v1

## Helper Scripts

These Node.js scripts live in the `pay-bills-skill/` directory. Run them with `node` to generate IDs and manage auth state.

| Script                  | Command                                               | Purpose                                                                                                                            |
| ----------------------- | ----------------------------------------------------- |------------------------------------------------------------------------------------------------------------------------------------|
| `generate-order-id.js`  | `node pay-bills-skill/generate-order-id.js`           | Outputs a unique `ORDER_<timestamp>_<random>` string. Use this as `trx_id` for every order — **never hardcode or reuse a trx_id**. |
| `generate-device-id.js` | `node pay-bills-skill/generate-device-id.js [userId]` | Outputs a device ID. With `userId`: `openclaw_<userId>`. Use as `deviceId` in auth requests. |
| `session-token.js`      | see below                                             | Manages the session token for auth.                                                                                                |

### Session Token Commands

```
node pay-bills-skill/session-token.js check              → { "loggedIn": true/false, "sessionToken": "..." | null }
node pay-bills-skill/session-token.js save <token>       → saves the token to .session_token
node pay-bills-skill/session-token.js load               → prints the saved token (exit 1 if none)
node pay-bills-skill/session-token.js clear              → deletes the saved token (logout)
```

### Workflow

1. **Before any `[auth]` request:** run `node pay-bills-skill/session-token.js check` to see if a session token exists.
   - If `loggedIn: true` → use the `sessionToken` value as `Authorization: Bearer <sessionToken>`.
   - If `loggedIn: false` → start the login flow (see Auth below).
2. **After a successful login** (steps that return `sessionToken`): run `node pay-bills-skill/session-token.js save <sessionToken>` to persist it.
3. **Before placing an order:** run `node pay-bills-skill/generate-order-id.js` to get a fresh `trx_id`.
4. **For auth requests:** run `node pay-bills-skill/generate-device-id.js` (no userId before login). After login, run `node pay-bills-skill/generate-device-id.js <userId>` to bind the device to the user.
5. **On logout or 401:** run `node pay-bills-skill/session-token.js clear` and re-auth.

## Auth

All `[auth]` endpoints need `Authorization: Bearer <sessionToken>`. If 401 → run `node pay-bills-skill/session-token.js clear` and re-auth.

**Login flow (no auth needed):**

```
1. POST /auth/start         { "phoneNumber":"08031234567", "deviceId":"<run: node pay-bills-skill/generate-device-id.js>" }
                             → { success, data: { sessionId, nextStep } }

   nextStep will be one of:
   - "verify_otp"        → new user OR unrecognized device
   - "enter_pin"         → known device, go straight to step 3

2. POST /auth/verify-otp    { "sessionId":"<from-step-1>", "code":"123456" }  ← 6 digits from SMS
                             → { success, data: { sessionId, nextStep } }

   nextStep will be one of:
   - "set_pin"           → new user, needs to create 4-digit PIN
   - "enter_pin"         → existing user, new device
   - "complete_profile"  → profile incomplete

2b. POST /auth/set-pin      { "sessionId":"...", "pin":"1234" }  ← 4 digits (new users only)
                             → { success, data: { sessionId, nextStep:"complete_profile" } }

2c. POST /auth/complete-profile  { "sessionId":"...", "fullName":"John Doe", "email":"j@x.com" }
                             → { success, data: { sessionId, nextStep:"verify_email" } }

2d. POST /auth/verify-email  { "sessionId":"...", "code":"123456" }  ← 6 digits from email
                             → { success, sessionToken, userId }  ✓ DONE
                             → then run: node pay-bills-skill/session-token.js save <sessionToken>

3. POST /auth/verify-pin    { "sessionId":"<from-above>", "pin":"1234" }  ← 4 digits
                             → { success, sessionToken, userId }  ✓ DONE
                             → then run: node pay-bills-skill/session-token.js save <sessionToken>
```

**Returning user (known device):** steps 1 → 3 only.
**Returning user (new device):** steps 1 → 2 → 3.
**New user:** steps 1 → 2 → 2b → 2c → 2d.

**Other auth endpoints:**

- `POST /auth/resend-otp { sessionId }` — 60s cooldown, max 5/hour
- `POST /auth/forgot-pin { phoneNumber, deviceId }` → OTP flow → set new PIN
- `POST /auth/logout { sessionToken }` → then run `node pay-bills-skill/session-token.js clear`

**Rate limits:** OTP: 5 sends/hour, 3 verify attempts/code. PIN: 5 attempts/15min, 5min lockout after.

## Buy Data

```
1. POST /utils/phone/normalize   { "phone": "<raw>" }           → { ok, data: "08031234567" }
2. POST /utils/phone/predict     { "phone": "08031234567" }      → { ok, data: { phone, network } }
3. GET  /product/networks                                        → [{ id, name, status }]
4. GET  /product/networks/:networkId/data-plans                  → { categories, plans: { daily[], weekly[], monthly[] } }
   Each plan: { id, name, amount, durationDays, category, status }  — only use status:"active"
5. GET  /user/balance  [auth]                                    → { ok, balance, points }
6. POST /orders  [auth]
   { "type":"data", "payment_method":"wallet", "trx_id":"<run: node pay-bills-skill/generate-order-id.js>", "use_points":false,
     "data": { "phone":"08031234567", "data_id": 42 } }
   → { ok, message, transactionId }
7. GET  /orders/:transactionId/status  [auth]                    → { status, reference, createdAt }
```

## Buy Airtime

Same steps 1-3, skip step 4. Minimum ₦50.

```
POST /orders  [auth]
{ "type":"airtime", "payment_method":"wallet", "trx_id":"<run: node pay-bills-skill/generate-order-id.js>", "use_points":false,
  "data": { "phone":"08031234567", "network_id":1, "amount":500 } }
```

## Order Statuses

| Status            | Meaning                        |
| ----------------- | ------------------------------ |
| `pending_payment` | Awaiting online payment        |
| `order_received`  | Processing — poll every 15-30s |
| `completed`       | Delivered                      |
| `failed`          | Failed, user auto-refunded     |

Call only if the user wants to know the status of an order they placed.

## Other Endpoints (all [auth])

```
GET  /user/balance                → { balance, points }
GET  /user/profile                → { id, balance, fullName, email, phone }
GET  /user/deposit-account        → { account: { AccountNumber, AccountName, BankName } | null }
GET  /transactions?page=&limit=&type=&status=&fromDate=&toDate=  → { transactions[], total, page, totalPages }
GET  /transactions/recent-phones  → { recentlyUsedPhones: [{ phone_number, network_id, network_name }] }
POST /payment/deposit [auth]      { amount (min 100) } → { paymentLink }
```

## Notification Preferences (all [auth])

Users can view and update which notifications they receive.

```
GET   /user/notification-preferences                → { ok, preferences }
PATCH /user/notification-preferences                → { ok, preferences }
```

### Preference Fields (all boolean, all optional on update)

| Field                  | Description                     | Default |
| ---------------------- | ------------------------------- | ------- |
| `emailEnabled`         | Master switch for email channel | true    |
| `chatEnabled`          | Master switch for chat channel  | true    |
| `orderConfirmations`   | Order placed / confirmed        | true    |
| `orderStatusUpdates`   | Order completed / failed        | true    |
| `depositConfirmations` | Deposit successful              | true    |
| `paymentFailures`      | Payment failed / underpaid      | true    |
| `refundNotifications`  | Refund processed                | true    |
| `giveawayUpdates`      | Giveaway created / activated    | true    |
| `giveawayClaimAlerts`  | Someone claimed your giveaway   | true    |
| `pointsAndCashback`    | Cashback & points earned        | true    |
| `promotionalEmails`    | Marketing / promotional content | true    |
| `lowBalanceWarning`    | Balance below threshold         | true    |

### Example

```json
PATCH /user/notification-preferences
{ "promotionalEmails": false, "lowBalanceWarning": false }
→ { "ok": true, "preferences": { ...all fields... } }
```

## Saved Contacts (all [auth])

Users can save phone numbers with names for quick reference. When a user says "buy data for Mum" or "send airtime to John", search their saved contacts first.

```
GET    /contacts?page=&limit=&search=    → { contacts[], total, page, totalPages }
POST   /contacts                          { "name":"Mum", "phoneNumber":"09012345678" } → { ok, contact }
PATCH  /contacts/:id                      { "name":"Mother" } or { "phoneNumber":"..." } or both → { ok, contact }
DELETE /contacts/:id                      → { ok, message:"Contact deleted" }
GET    /contacts/search?name=mum          → { ok, contacts: [{ id, name, phoneNumber }] }  (max 5 results)
```

- A phone number can only be saved once per user (409 Conflict on duplicate)
- `search` param on `GET /contacts` matches name or phone (partial)
- `GET /contacts/search?name=` is a quick lookup — use it to resolve a name to a phone number

### Contact Behaviors

- **After a successful purchase:** if the phone number isn't already saved, suggest saving it: _"Would you like to save 0803 123 4567 with a name so you can quickly buy for them next time?"_
- **When user refers to a name:** search contacts via `GET /contacts/search?name=...`
  - 1 match → use that phone number (confirm with user)
  - Multiple matches → show options, ask which one
  - No match → ask user for the phone number
- **"Buy for Mum"** flow: search contacts → find phone → normalize → predict network → fetch plans → confirm → order

## Product Discovery (no auth)

```
GET /product/networks
GET /product/networks/:id/data-plans
GET /product/data-plans/:dataId
GET /product/education
```

## Key Rules

- **Always normalize phone** before anything — `POST /utils/phone/normalize`
- **Always predict network** — `POST /utils/phone/predict` (don't guess from prefix)
- **Never hardcode network IDs or plan IDs** — fetch fresh every time
- **trx_id must be unique per attempt** — run `node pay-bills-skill/generate-order-id.js` for each order, never reuse even on failure
- **Check balance before wallet orders** — if insufficient, suggest deposit
- **Confirm with user before submitting** — show plan, price, phone, balance
- **Network status must be `up`** — don't order on `down` networks
- **Plan status must be `active`** — skip disabled plans
- **payment_method `wallet`** is preferred for agent purchases (instant, no redirect)
- Use `GET /transactions/recent-phones` for quick re-orders ("buy same as last time")
- Use `GET /contacts/search?name=` when user refers to someone by name ("buy for Mum")
- **After a successful purchase, suggest saving the number** if it's not already in contacts
- User's own phone is in `GET /user/profile` → `phone` field

## Enums

- **type:** `data`, `airtime`
- **payment_method:** `wallet`, `online`
- **transaction type:** `deposit`, `purchase_data`, `purchase_airtime`, `giveaway_funding`, `giveaway_claim`
- **plan category:** `daily`, `weekly`, `monthly`, `yearly`
