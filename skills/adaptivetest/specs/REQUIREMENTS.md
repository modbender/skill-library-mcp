# AdaptiveTest Skill -- Requirements Spec

> **Functional and non-functional requirements. Covers usage tiers, purchase flow, API key management, security, and testing.**
> **Target repo:** `adaptivetest-platform` (backend work), `adaptivetest-marketing` (landing page)

---

## Usage Tiers

| | Free Trial | Pro | Enterprise |
|---|---|---|---|
| **Price** | $0 | $49/mo | Custom |
| **Duration** | 7 days | Monthly or annual | Custom |
| **API calls/mo** | 100 | 10,000 | Unlimited |
| **AI calls/mo** | 10 | 1,000 | Unlimited |
| **API keys** | 1 | 5 | Unlimited |
| **Rate limit** | 10 req/min | 60 req/min | Custom |
| **Support** | Docs only | Email | Dedicated |
| **LTI access** | No | Yes | Yes |
| **OneRoster access** | No | Yes | Yes |
| **WebSocket sessions** | No | Yes | Yes |

**Annual pricing:** Pro tier available at $490/yr (2 months free vs monthly).

### Tier Enforcement

- Rate limits enforced per API key (not per IP)
- Monthly API call counts reset on the 1st of each month at 00:00 UTC
- AI calls are a subset of total API calls (endpoints: `/api/gen-q`, `/api/recs`)
- When a limit is reached, return `403` with body: `{"detail": "Monthly API call limit exceeded. Upgrade at https://adaptivetest.io/developers"}`
- When rate limit is reached, return `429` with `Retry-After` header
- Trial expiration: return `403` with body: `{"detail": "Trial expired. Subscribe at https://adaptivetest.io/developers"}`

---

## Purchase Flow

### Flow Diagram

```
ClawHub Listing
  └─> "Get API Key" link
        └─> adaptivetest.io/developers (landing page)
              └─> "Start Free Trial" button
                    └─> Stripe Checkout (hosted redirect)
                          ├─> success_url: /developers?session_id={CHECKOUT_SESSION_ID}
                          └─> cancel_url: /developers
                                │
                          Stripe webhook: checkout.session.completed
                                │
                          Platform provisions API key
                                │
                          Key displayed on success page (show once, no email)
```

### Stripe Checkout Configuration

- **Mode:** `subscription` (not `payment`)
- **Product:** "AdaptiveTest Pro API Access"
- **Price:** $49/month recurring
- **Trial:** 7-day free trial via `subscription_data.trial_period_days: 7`
- **Success URL:** `https://adaptivetest.io/developers?session_id={CHECKOUT_SESSION_ID}`
- **Cancel URL:** `https://adaptivetest.io/developers`
- **Metadata:** `{"product": "adaptivetest-skill", "tier": "pro"}`
- **Collect email:** Yes (Stripe handles this)
- **No embedded Stripe.js** -- use hosted Checkout redirect (simpler, no CSP changes needed on marketing site)

### Webhook Events

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Provision API key with TRIAL tier, store Stripe customer/subscription IDs |
| `customer.subscription.updated` | Update tier (TRIAL -> PRO when trial converts, or handle plan changes) |
| `customer.subscription.deleted` | Revoke all API keys for this subscription |
| `invoice.payment_failed` | No immediate action -- Stripe retries on days 1, 3, 5. Keys stay active during retry window. |
| `customer.subscription.deleted` (after retries exhaust) | Revoke all API keys for this subscription (7-day grace period effectively provided by Stripe's retry schedule) |

### Webhook Security

- Verify Stripe webhook signature using `stripe.Webhook.construct_event()`
- Webhook secret stored in `STRIPE_WEBHOOK_SECRET_APIKEYS` env var (separate from existing billing webhook secret)
- Return `200` for all handled events, `400` for signature failures
- Idempotent: check if key already exists for this subscription before provisioning

---

## API Key Management

### Key Format

- **Live keys:** `at_live_` + 32 random bytes encoded as base64url (no padding) = `at_live_` + 43 chars = 51 chars total
- **Test keys:** `at_test_` + 32 random bytes encoded as base64url (no padding) = `at_test_` + 43 chars = 51 chars total
- **Generation:** `secrets.token_urlsafe(32)` for the random part
- **Storage:** SHA-256 hash of the full key string. The plaintext key is shown once at creation and never stored.
- **Prefix storage:** First 12 chars stored in plaintext for identification (e.g., `at_live_abc1`)

### Key Lifecycle

1. **Provision:** Stripe webhook creates key -> hash stored -> plaintext returned in response (show once)
2. **Authenticate:** Request includes `X-API-Key` header -> hash the value -> lookup by hash -> resolve tier/limits
3. **Rotate:** User requests new key -> old key revoked -> new key provisioned -> plaintext shown once
4. **Revoke:** Key marked as revoked (soft delete) -> `revoked_at` timestamp set -> auth lookups reject revoked keys

### Key Validation (per request)

1. Extract `X-API-Key` header
2. Check prefix format (`at_live_` or `at_test_`)
3. SHA-256 hash the full key
4. Lookup by hash in `api_keys` table
5. Check `revoked_at IS NULL`
6. Check `expires_at > now()` (for trial keys)
7. Check monthly usage against tier limits
8. Check per-minute rate against tier limits
9. Return `AuthenticatedAPIKeyUser` with tier, limits, key_id

### Dual Auth Model

The platform currently uses Clerk JWT auth (`Authorization: Bearer <jwt>`). API key auth must coexist:

- **New middleware:** `get_api_key_user()` -- validates `X-API-Key` header, returns user context with tier/limits
- **Existing middleware:** `get_current_user()` -- validates Clerk JWT, returns user context with role
- **Combined dependency:** `get_any_authenticated_user()` -- tries API key first, falls back to JWT. Used on endpoints that accept either auth method.
- AI proxy endpoints (`/api/gen-q`, `/api/recs`) should accept either auth method
- Admin endpoints (`/api/keys/*`) should require Clerk JWT with admin role
- Assessment CRUD endpoints should accept either auth method
- OneRoster/LTI/QTI endpoints remain Clerk JWT only (Pro tier gated as-is)

---

## Security Requirements

### API Key Security
- Keys stored as SHA-256 hashes only -- never store plaintext
- Key prefix stored separately for identification/display
- Revoked keys remain in database (audit trail) but are rejected on auth
- No key recovery -- if lost, revoke and provision a new one

### Stripe Webhook Security
- Always verify webhook signature before processing
- Use separate webhook secret from existing billing webhooks
- Log all webhook events via `log_event()` for audit trail
- Idempotent processing -- handle duplicate webhook deliveries gracefully

### Rate Limiting
- Per API key, not per IP
- Sliding window counter (not fixed window) to prevent burst-at-boundary attacks
- Rate limit headers on every response (see CONTENT.md > API Overview)
- Use Redis or in-memory counter (SlowAPI already in platform)

**Anomaly detection (v1):** Simple threshold alerting via `log_event()`:
- Flag keys that hit >80% of monthly API or AI call limit
- Flag keys with >5x their rolling 7-day average daily usage
- Audit log only for v1 -- no Slack/email notifications until v2

### Input Validation
- API key format validated before hash lookup (reject malformed keys early)
- All request bodies validated via Pydantic schemas (existing pattern)
- SQL injection prevented by SQLAlchemy parameterized queries (existing pattern)

---

## Testing Requirements

### Target
- 80%+ code coverage for new `src/apikeys/` module
- All tests async (pytest-asyncio, matches platform patterns)

### Required Test Categories

**Unit Tests:**
- API key generation (format, prefix, uniqueness)
- API key hashing (SHA-256 consistency)
- Tier limit checking (each tier boundary)
- Rate limit checking (within and exceeded)
- Key validation (valid, expired, revoked, malformed)

**Integration Tests:**
- Stripe webhook processing (mock Stripe events)
- Key provisioning end-to-end (webhook -> key created -> auth works)
- Key revocation (revoke -> subsequent auth rejected)
- Dual auth (API key accepted, JWT accepted, neither rejected)
- Usage tracking (request -> log entry -> monthly rollup)

**Edge Cases:**
- Duplicate webhook delivery (idempotent)
- Expired trial key (rejected with correct error)
- Key at exact rate limit boundary
- Key at exact monthly limit boundary
- Multiple keys on same subscription
- Subscription deleted with active keys

---

## Deployment

### Environment Variables (new, on adaptivetest-platform Railway)

```
- [ ] STRIPE_WEBHOOK_SECRET_APIKEYS -- separate webhook secret for API key provisioning
- [ ] STRIPE_PRICE_ID_PRO -- Stripe price ID for $49/mo Pro tier
```

Existing env vars (`STRIPE_SECRET_KEY`, `DATABASE_URL`, etc.) are already configured.

### Migration

- Single Alembic migration per PR (platform convention)
- Migration creates `api_keys`, `api_key_usage`, `api_key_monthly_usage` tables
- No data migration needed (new tables only)

### Monitoring

- Audit log events for all key mutations (provision, revoke, tier change)
- Usage metrics queryable via admin endpoints
- Anomaly events logged via `log_event("api_key.usage_anomaly", ...)` -- audit log only for v1
