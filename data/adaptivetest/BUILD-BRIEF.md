# Build Brief: AdaptiveTest Skill

> Generated from `specs/` on 2026-02-24. Two target repos, two implementation phases.

This project has **three deliverables** across **two repos**:

| Deliverable | Target Repo | Branch Policy | Scope |
|-------------|-------------|---------------|-------|
| API key management module (`src/apikeys/`) | `adaptivetest-platform` | Tier 1 -- PR required | Large |
| `/developers` landing page | `adaptivetest-marketing` | Tier 1 -- PR required | Medium |
| SKILL.md + references/ | This repo (done) | Non-production | Done |

**Implementation order:** Platform first (backend creates the API keys system), then Marketing (landing page needs working Stripe + key retrieval endpoints).

---

## Brief 1: Platform -- API Key Management Module

### Context

You are working on `adaptivetest-platform` at `/Users/james/projects/adaptivetest-platform`. Read `CLAUDE.md` for full context.

This brief adds a new `src/apikeys/` module that enables external developers to authenticate via API keys (in addition to existing Clerk JWT auth). Keys are provisioned via Stripe webhooks and tracked for usage/billing.

### Branch

**Tier 1 -- PR required.** Create a feature branch:
```
git checkout -b feature/api-key-management
```

### Spec Files to Read (in order)

1. `/Users/james/projects/adaptivetest-skill/specs/REQUIREMENTS.md` -- tiers, purchase flow, key format, security
2. `/Users/james/projects/adaptivetest-skill/specs/DATA-MODEL.md` -- tables, endpoints, auth middleware, schemas

### Implementation Steps

#### Step 1: Create Module Structure

**Source:** DATA-MODEL.md > New Module

```
src/apikeys/
  __init__.py
  models.py
  schemas.py
  service.py
  auth.py
  routes.py
  stripe_webhooks.py
```

#### Step 2: Database Models + Migration

**Source:** DATA-MODEL.md > Database Schema

Create three models following existing platform conventions:

**`APIKeyTier` enum** (separate from existing `Tier`):
- `TRIAL`, `PRO`, `ENTERPRISE`

**`APIKey` table:**
- `key_hash` (String(64), unique, indexed) -- SHA-256 of full key
- `key_prefix` (String(12)) -- first 12 chars for display
- `tier` (Enum APIKeyTier)
- `user_email` (String(255), indexed)
- `stripe_customer_id`, `stripe_subscription_id` (indexed)
- Denormalized limits: `monthly_api_limit`, `monthly_ai_limit`, `rate_limit_per_min`
- Lifecycle: `is_test_key`, `expires_at`, `revoked_at`, `last_used_at`
- Standard `created_at`, `updated_at`

**`APIKeyUsage` table:**
- Per-request log: `key_id` (FK), `endpoint`, `method`, `status_code`, `response_time_ms`, `is_ai_call`
- Index on `(key_id, created_at)`

**`APIKeyMonthlyUsage` table:**
- Monthly rollup: `key_id` (FK), `month` (String(7), "2026-02"), `api_call_count`, `ai_call_count`
- Unique constraint on `(key_id, month)` -- enables upsert pattern

**Conventions to match:**
- `UUID(as_uuid=False)` PKs with `default=lambda: str(uuid4())`
- `DateTime(timezone=True)` for all timestamps
- `Mapped[...]` / `mapped_column(...)` syntax
- Single Alembic migration

#### Step 3: Pydantic Schemas

**Source:** DATA-MODEL.md > Pydantic Schemas

- `APIKeyCreate` -- email, tier, optional name
- `APIKeyUpdate` -- partial update for limits/tier
- `APIKeyResponse` -- all fields except plaintext key
- `APIKeyCreatedResponse(APIKeyResponse)` -- includes `api_key` (plaintext, shown once)
- `APIKeyListResponse` -- paginated list
- `APIKeyUsageResponse` -- current month + history
- `APIKeyFromSessionResponse` -- for success page retrieval

All with `class Config: from_attributes = True`.

#### Step 4: Service Layer

**Source:** REQUIREMENTS.md > API Key Management

Key generation:
```python
import secrets, hashlib
prefix = "at_live_"  # or "at_test_"
random_part = secrets.token_urlsafe(32)
full_key = prefix + random_part  # 51 chars total
key_hash = hashlib.sha256(full_key.encode()).hexdigest()
key_prefix = full_key[:12]
```

Service functions:
- `provision_key(email, tier, stripe_ids)` -- generate, hash, store, return plaintext once
- `revoke_key(key_id)` -- set `revoked_at`
- `revoke_keys_for_subscription(subscription_id)` -- bulk revoke
- `update_keys_for_subscription(subscription_id, tier, limits)` -- tier upgrade
- `validate_key(key_hash)` -- lookup, check revoked/expired/limits
- `track_usage(key_id, endpoint, method, status_code, response_time_ms, is_ai)` -- insert log + upsert monthly rollup
- `get_usage_stats(key_id)` -- current month + history

Audit logging: call `log_event()` for all key mutations (provision, revoke, tier change).

#### Step 5: Auth Middleware

**Source:** DATA-MODEL.md > Auth Middleware

Create `get_api_key_user()`:
1. Extract `X-API-Key` header
2. Validate prefix format (`at_live_` or `at_test_`)
3. SHA-256 hash -> lookup by hash
4. Check `revoked_at IS NULL`
5. Check `expires_at > now()` for trial keys
6. Check monthly usage against limits
7. Check per-minute rate limit
8. Update `last_used_at`
9. Return `AuthenticatedAPIKeyUser(key_id, tier, email, limits)`

Create `get_any_authenticated_user()`:
- Try `X-API-Key` header first -> `get_api_key_user()`
- Fall back to `Authorization` header -> existing `get_current_user()`
- Neither -> 401

**Rate limit headers** on every API-key-authenticated response:
- `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

#### Step 6: Admin Routes

**Source:** DATA-MODEL.md > Admin Key Management

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/api/keys` | JWT (admin) |
| `GET` | `/api/keys` | JWT (admin) |
| `GET` | `/api/keys/{id}` | JWT (admin) |
| `DELETE` | `/api/keys/{id}` | JWT (admin) |
| `GET` | `/api/keys/{id}/usage` | JWT (admin) |
| `GET` | `/api/keys/from-session` | None (session_id) |

The `/from-session` endpoint is callable once per session_id. After retrieval, plaintext is cleared.

#### Step 7: Stripe Webhook Handler

**Source:** REQUIREMENTS.md > Webhook Events, DATA-MODEL.md > Webhook Endpoint

Route: `POST /api/webhooks/stripe-apikeys`

1. Verify Stripe signature using `STRIPE_WEBHOOK_SECRET_APIKEYS` env var
2. Handle events:
   - `checkout.session.completed` -> provision TRIAL key (100 API/10 AI, 10 req/min, 7-day expiry)
   - `customer.subscription.updated` -> upgrade to PRO (10K API/1K AI, 60 req/min, no expiry) when trial converts
   - `customer.subscription.deleted` -> revoke all keys for subscription
3. Idempotent: check if key exists for subscription before provisioning
4. Return 200 for handled events, 400 for signature failures

#### Step 8: Mount Routes in main.py

**Source:** DATA-MODEL.md > Router Registration

```python
from src.apikeys.routes import router as apikeys_router
from src.apikeys.stripe_webhooks import router as apikeys_webhook_router

app.include_router(apikeys_router, prefix="/api/keys", tags=["API Keys"], dependencies=[Depends(require_admin)])
app.include_router(apikeys_webhook_router, prefix="/api/webhooks", tags=["Webhooks"])
```

#### Step 9: Enable Dual Auth on Existing Endpoints

**Source:** DATA-MODEL.md > Endpoint Auth Matrix

Update these existing routers to use `get_any_authenticated_user()` instead of `get_current_user()`:
- `/api/tests/*`
- `/api/sessions/*`
- `/api/students/*`
- `/api/classes/*`
- `/api/gen-q`
- `/api/recs`

Leave these on JWT-only: `/api/oneroster/*`, `/api/lti/*`, `/api/qti/*`, `/api/audit/*`

For API-key-authenticated requests to AI endpoints (`/api/gen-q`, `/api/recs`), count the call against the key's AI call limit.

#### Step 10: Usage Tracking Middleware

**Source:** DATA-MODEL.md > Usage Tracking Middleware

For every request authenticated by API key:
1. Log to `api_key_usage` table (endpoint, method, status_code, response_time_ms, is_ai_call)
2. Upsert `api_key_monthly_usage` rollup using `ON CONFLICT DO UPDATE`
3. Track `is_ai_call = True` for `/api/gen-q` and `/api/recs`

#### Step 11: Tests

**Source:** REQUIREMENTS.md > Testing Requirements

Target: 80%+ coverage on `src/apikeys/`

**Unit tests:**
- Key generation (format, prefix, uniqueness)
- Key hashing (SHA-256 consistency)
- Tier limit checking (each boundary)
- Rate limit checking
- Key validation (valid, expired, revoked, malformed)

**Integration tests:**
- Stripe webhook processing (mock events)
- Key provisioning end-to-end
- Key revocation -> auth rejected
- Dual auth (API key accepted, JWT accepted, neither rejected)
- Usage tracking (request -> log -> rollup)

**Edge cases:**
- Duplicate webhook delivery (idempotent)
- Expired trial key rejection
- Exact limit boundaries
- Subscription deleted with active keys

### Key Values from Specs

**Tier limits:**
| | TRIAL | PRO | ENTERPRISE |
|---|---|---|---|
| API calls/mo | 100 | 10,000 | Unlimited |
| AI calls/mo | 10 | 1,000 | Unlimited |
| Rate limit | 10/min | 60/min | Custom |
| Keys | 1 | 5 | Unlimited |
| Expiry | 7 days | None | None |

**Key format:** `at_live_` + `secrets.token_urlsafe(32)` = 51 chars total
**Key storage:** SHA-256 hash, prefix first 12 chars
**AI endpoints:** `/api/gen-q`, `/api/recs`

### Environment Variables (new)

```
STRIPE_WEBHOOK_SECRET_APIKEYS -- separate from existing billing webhook
STRIPE_PRICE_ID_PRO -- Stripe price ID for $49/mo
```

### Acceptance Criteria

- [ ] Alembic migration creates 3 tables cleanly (up and down)
- [ ] API key generation produces correct format (`at_live_` + 43 chars)
- [ ] Keys stored as SHA-256 hash only (no plaintext in DB)
- [ ] `X-API-Key` auth works on assessment/session/student/class/AI endpoints
- [ ] Clerk JWT auth continues to work on all endpoints
- [ ] `get_any_authenticated_user()` accepts either auth method
- [ ] Stripe webhook provisions key on `checkout.session.completed`
- [ ] Stripe webhook upgrades tier on subscription activation
- [ ] Stripe webhook revokes keys on subscription deletion
- [ ] Duplicate webhook delivery is idempotent
- [ ] Rate limit headers present on all API-key-authenticated responses
- [ ] Monthly usage limits enforced (403 when exceeded)
- [ ] Per-minute rate limits enforced (429 when exceeded)
- [ ] Trial keys rejected after expiration (403)
- [ ] Revoked keys rejected (401)
- [ ] Admin CRUD endpoints require JWT admin role
- [ ] `/api/keys/from-session` works once per session_id
- [ ] AI calls tracked separately in monthly usage
- [ ] All key mutations logged via `log_event()`
- [ ] Tests pass, 80%+ coverage on `src/apikeys/`
- [ ] Lint clean (ruff)

### Warnings

- **Match existing patterns exactly** -- read `src/billing/models.py` and `src/oneroster/auth.py` before writing models/auth
- Do NOT use Fernet encryption for keys -- SHA-256 hash only (keys are random, never need decryption)
- Keep `APIKeyTier` enum separate from existing `Tier` enum (different domains)
- The webhook endpoint path is `/api/webhooks/stripe-apikeys` (not the existing `/api/webhooks/stripe`)
- Use a **separate** webhook secret env var (`STRIPE_WEBHOOK_SECRET_APIKEYS`)
- Single Alembic migration for all 3 tables

---

## Brief 2: Marketing -- `/developers` Landing Page

### Context

You are working on `adaptivetest-marketing` at `/Users/james/projects/adaptivetest-marketing`. Read `CLAUDE.md` for full context.

This brief adds a `/developers` landing page that showcases the AdaptiveTest API to developers and handles Stripe checkout for API key subscriptions.

### Branch

**Tier 1 -- PR required.** Create a feature branch:
```
git checkout -b feature/developers-landing-page
```

### Spec Files to Read (in order)

1. `/Users/james/projects/adaptivetest-skill/specs/DESIGN-SYSTEM.md` -- colors, typography, component patterns
2. `/Users/james/projects/adaptivetest-skill/specs/CONTENT.md` -- all copy
3. `/Users/james/projects/adaptivetest-skill/specs/PAGES.md` -- page structure
4. `/Users/james/projects/adaptivetest-skill/specs/SITE-ARCHITECTURE.md` -- routes, SEO, Stripe integration

### Implementation Steps

#### Step 1: New Components

**Source:** DESIGN-SYSTEM.md > Component Patterns, PAGES.md > Component Dependencies

Build 4 new components (check if PricingCard already exists):

**`CodeBlock.tsx`** -- Terminal-style code display:
- Container: `bg-gray-900 rounded-2xl overflow-hidden shadow-xl`
- Header: `bg-gray-800 px-6 py-3` with traffic light dots + language label
- Body: `font-mono text-sm text-gray-300 leading-relaxed`
- Syntax colors: strings `text-green-400`, keywords `text-purple-400`, functions `text-blue-400`, comments `text-gray-400`

**`StepCard.tsx`** -- Numbered step:
- Number circle: `w-12 h-12 rounded-full bg-indigo-600 text-white font-bold`
- Title: `text-xl font-semibold text-gray-900`
- Description: `text-gray-600`

**`FAQAccordion.tsx`** -- Expandable Q&A:
- Container: `max-w-3xl mx-auto divide-y divide-gray-200`
- Question: `text-lg font-semibold text-gray-900` with ChevronDown icon
- Accordion mode: one open at a time, first item open by default

**`PricingCard.tsx`** (if not existing):
- Container: `bg-white rounded-2xl overflow-hidden shadow-lg border border-gray-200`
- Popular variant: `ring-2 ring-indigo-600 md:scale-105` with indigo badge
- Full-width CTA button

#### Step 2: Update Navbar + Footer

**Source:** DESIGN-SYSTEM.md > Navbar Updates, Footer Updates

Add "Developers" link:
- Navbar: position after existing links, before CTA buttons. Style: `text-gray-600 hover:text-indigo-600 transition`
- Footer: add to Product or Resources column. Style: `text-gray-400 hover:text-white transition`
- Include in mobile menu

#### Step 3: Build `/developers` Page

**Source:** PAGES.md > Developers Page, CONTENT.md > Landing Page Copy

Create `src/app/developers/page.tsx` with 7 sections in order:

**Section 1 -- Hero:**
- Gradient: `bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800`
- Label: "For Developers" (`text-indigo-200 text-sm font-semibold tracking-wider uppercase`)
- Headline: "Add Adaptive Testing to Any Application"
- Subtitle: "Production-grade IRT/CAT engine..."
- CTAs: "Start Free Trial" (primary) + "View Documentation" (ghost -> `#capabilities`)

**Section 2 -- Capabilities Grid:** (white bg, `id="capabilities"`)
- "What You Can Build" heading
- 3-column grid with 6 Feature Cards
- Icons: Brain, Sparkles, GraduationCap, BarChart3, Users, LineChart (from lucide-react)
- Icon colors: see CONTENT.md capability table (map to indigo/purple/green/orange)

**Section 3 -- Code Example:** (gray-50 bg)
- Two-column: text left, CodeBlock right
- "Simple to Integrate" heading
- 4 bullet points with Check icons
- Python code block from CONTENT.md

**Section 4 -- How It Works:** (white bg)
- "From ClawHub to Production in Minutes"
- 4 StepCards in 2x2 grid
- Steps: Sign Up, Install the Skill, Configure, Build

**Section 5 -- Pricing:** (gray-50 bg)
- "Simple, Predictable Pricing"
- 3 PricingCards: Free Trial, Pro (popular), Enterprise
- Pro card: `ring-2 ring-indigo-600 md:scale-105`
- CTAs: Free Trial + Subscribe -> Stripe Checkout, Enterprise -> mailto

**Section 6 -- FAQ:** (white bg)
- "Frequently Asked Questions"
- 6 Q&A items in FAQAccordion
- All copy from CONTENT.md > FAQ Section

**Section 7 -- Bottom CTA:** (indigo gradient)
- "Ready to Build?"
- Same CTA pair as hero

#### Step 4: SEO Metadata

**Source:** SITE-ARCHITECTURE.md > SEO Metadata

Add exact metadata export to page:
```tsx
export const metadata: Metadata = {
  title: "Developers - AdaptiveTest",
  description: "Add adaptive testing to any application...",
  openGraph: { ... },
  twitter: { ... },
};
```

#### Step 5: Stripe Checkout Integration

**Source:** SITE-ARCHITECTURE.md > Stripe Checkout Integration

Create `src/app/api/create-checkout-session/route.ts`:
- POST handler that creates a Stripe Checkout session
- Mode: `subscription`
- Trial: 7 days (`subscription_data.trial_period_days: 7`)
- Success URL: `/developers?session_id={CHECKOUT_SESSION_ID}`
- Cancel URL: `/developers`

Wire the "Start Free Trial" and "Subscribe" buttons to call this endpoint and redirect.

#### Step 6: Success Page State

**Source:** SITE-ARCHITECTURE.md > Success Page Behavior

When `?session_id=` query param is present:
1. Call `GET {ADAPTIVETEST_API_URL}/api/keys/from-session?session_id=<id>`
2. Display the API key in a copy-able code block
3. Show "Key shown once -- copy it now" warning
4. Show next steps: install skill, configure env var

This requires a client component section. The rest of the page can remain server-rendered.

#### Step 7: Sitemap Update

**Source:** SITE-ARCHITECTURE.md > Sitemap Update

Add `/developers` to sitemap with priority 0.8.

### Key Values from Specs

**Colors:**
- Primary: `#4F46E5` / `indigo-600`
- Gradient: `from-indigo-600 via-purple-600 to-indigo-800`
- Backgrounds: white, `#F9FAFB` / `gray-50` (alternating)
- Text: `#111827` / `gray-900` (headings), `#4B5563` / `gray-600` (body)

**Typography:**
- Font: Inter via `next/font/google`
- H1: `text-5xl md:text-6xl font-bold`
- H2: `text-4xl md:text-5xl font-bold`
- Body: `text-base`

**Layout:**
- Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- Section spacing: `py-20`
- Grid gaps: `gap-8` (standard), `gap-12` (two-column split)

**Lucide icons:** Brain, Sparkles, GraduationCap, BarChart3, Users, LineChart, Check, ChevronDown

### Environment Variables (new)

```
STRIPE_SECRET_KEY -- for creating Checkout sessions
NEXT_PUBLIC_SITE_URL -- https://adaptivetest.io
NEXT_PUBLIC_STRIPE_PRICE_ID_PRO -- Stripe price ID
NEXT_PUBLIC_ADAPTIVETEST_API_URL -- platform API URL
```

### Acceptance Criteria

- [ ] `/developers` page renders with all 7 sections
- [ ] All copy matches CONTENT.md exactly (no invented text)
- [ ] All colors match DESIGN-SYSTEM.md hex values
- [ ] Font is Inter (not Geist)
- [ ] Capabilities grid: 3 columns on desktop, 2 on tablet, 1 on mobile
- [ ] Code block has syntax highlighting with correct colors
- [ ] FAQ accordion: one item open at a time, first open by default
- [ ] Pricing cards: Pro card is visually prominent (ring + scale)
- [ ] "Start Free Trial" / "Subscribe" buttons redirect to Stripe Checkout
- [ ] Success page displays API key when `session_id` is present
- [ ] "Developers" link appears in navbar and footer
- [ ] SEO metadata matches SITE-ARCHITECTURE.md exactly
- [ ] `/developers` appears in sitemap
- [ ] All buttons have focus, active, and disabled states
- [ ] `prefers-reduced-motion` respected (no forced animations)
- [ ] Page renders correctly on mobile (375px+)
- [ ] Lighthouse: Performance >= 90, Accessibility >= 95
- [ ] No CSP violations (Stripe redirect, not embedded)

### Warnings

- **Do NOT use Geist font** -- the marketing site uses Inter
- **Do NOT add Framer Motion** -- the existing site uses CSS transitions only
- **Do NOT embed Stripe.js** -- use hosted Checkout redirect (full page navigation)
- All copy comes from `specs/CONTENT.md` -- do not invent marketing text
- Match existing marketing site patterns for navbar, footer, section spacing
- The success page key retrieval only works after Brief 1 (platform) is deployed

---

## Implementation Order

```
Brief 1: Platform (API key module)     -- must be first
  └─> Deploy to Railway
      └─> Create Stripe product/price
          └─> Brief 2: Marketing (landing page)
              └─> Deploy to Vercel
                  └─> Brief 3: ClawHub submission (2-5 day review)
```

Brief 1 blocks Brief 2 because the landing page needs:
- Working Stripe webhook endpoint (to provision keys)
- Working `/api/keys/from-session` endpoint (for success page)
- Stripe product/price IDs (for checkout session creation)

---

## Brief 3: ClawHub Submission

### Prerequisites
- Platform deployed with API key module (Brief 1)
- Marketing site deployed with `/developers` page (Brief 2)
- ClawHub CLI installed: `npm i -g clawhub`
- Authenticated: `clawhub login` (GitHub OAuth)

### Submission Command
```bash
cd /Users/james/projects/adaptivetest-skill
clawhub publish . --slug adaptivetest --version 1.0.0 --changelog "Initial release: adaptive testing with IRT/CAT, AI question generation, learning recommendations"
```

### Review Process
- Initial review: 2-5 business days
- VirusTotal automated scan + human review
- Permission justification required: `ADAPTIVETEST_API_KEY` is needed to authenticate API requests (skill is a wrapper around a paid SaaS API)
- Future updates go through expedited review

### Files Published to ClawHub
These become **publicly visible** on ClawHub (repo stays private):
- `SKILL.md` + `clawhub.json` + `CHANGELOG.md`
- `references/` (API docs, IRT concepts, calibration guide)

### Screenshots Needed
Before submission, capture screenshots for the ClawHub listing:
- [ ] Code example showing adaptive test session
- [ ] API response with ability estimate
- [ ] Landing page hero section
<!-- TODO: Create these after marketing site is live -->

---

## Resolved TODOs

All 8 TODOs resolved (2026-02-24):

| # | Question | Decision |
|---|----------|----------|
| 1 | Annual pricing discount? | $490/yr (2 months free) |
| 2 | Email delivery for API keys? | Show once on success page only, no email |
| 3 | `invoice.payment_failed` handling? | 7-day grace period, revoke after Stripe retries exhaust |
| 4 | Stripe API route vs Payment Link? | Option A: API route (needed for session_id flow) |
| 5 | Anomaly detection? | Simple threshold: 80% monthly limit + 5x daily spike |
| 6 | Alerting mechanism? | Audit log only for v1, Slack/email is v2 |
| 7 | Dual auth endpoint matrix? | Confirmed as spec'd |
| 8 | ClawHub submission format? | `clawhub` CLI + `clawhub.json` manifest, 2-5 day review |
