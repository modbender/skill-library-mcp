# AdaptiveTest Skill -- Data Model Spec

> **Database schema, API endpoints, and auth model for the API key management system.**
> **Target repo:** `adaptivetest-platform` -- new `src/apikeys/` module

---

## Patterns Reference

All models follow existing `adaptivetest-platform` conventions:

- SQLAlchemy 2.0 `Mapped[...]` / `mapped_column(...)` syntax
- `UUID(as_uuid=False)` primary keys with `default=lambda: str(uuid4())`
- `DateTime(timezone=True)` for all timestamps
- `String(255)` for names/identifiers, `String(500)` for URLs, `String(50)` for enum-like strings
- Pydantic v2 schemas with `class Config: from_attributes = True`
- Audit logging via `log_event()` for all mutations
- Single Alembic migration per PR

---

## New Module: `src/apikeys/`

```
src/apikeys/
├── __init__.py
├── models.py          # SQLAlchemy models (APIKey, APIKeyUsage, APIKeyMonthlyUsage)
├── schemas.py         # Pydantic request/response schemas
├── service.py         # Business logic (provision, revoke, validate, usage tracking)
├── auth.py            # get_api_key_user() dependency, get_any_authenticated_user()
├── routes.py          # Admin endpoints for key management
└── stripe_webhooks.py # Webhook handler for checkout/subscription events
```

---

## Database Schema

### `api_keys` Table

```python
class APIKeyTier(str, PyEnum):
    """Separate from existing Tier enum -- different domain (external developers vs internal users)."""
    TRIAL = "trial"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class APIKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    tier: Mapped[APIKeyTier] = mapped_column(
        Enum(APIKeyTier), default=APIKeyTier.TRIAL, nullable=False
    )
    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Stripe references
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), index=True)

    # Limits (denormalized from tier for Enterprise overrides)
    monthly_api_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    monthly_ai_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Lifecycle
    is_test_key: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    usage_logs: Mapped[list["APIKeyUsage"]] = relationship(
        back_populates="api_key", cascade="all, delete-orphan"
    )
    monthly_usage: Mapped[list["APIKeyMonthlyUsage"]] = relationship(
        back_populates="api_key", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_api_keys_stripe_sub", "stripe_subscription_id"),
        Index("ix_api_keys_email", "user_email"),
    )
```

### `api_key_usage` Table

Per-request tracking. High-volume -- consider retention policy.

```python
class APIKeyUsage(Base):
    __tablename__ = "api_key_usage"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    key_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False
    )
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    is_ai_call: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    api_key: Mapped["APIKey"] = relationship(back_populates="usage_logs")

    __table_args__ = (
        Index("ix_api_key_usage_key_created", "key_id", "created_at"),
    )
```

### `api_key_monthly_usage` Table

Rollup for fast limit checks. Mirrors the existing `AIUsageLog` pattern from `src/billing/models.py`.

```python
class APIKeyMonthlyUsage(Base):
    __tablename__ = "api_key_monthly_usage"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    key_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("api_keys.id", ondelete="CASCADE"), nullable=False
    )
    month: Mapped[str] = mapped_column(String(7), nullable=False)  # "2026-02" format
    api_call_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_call_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    api_key: Mapped["APIKey"] = relationship(back_populates="monthly_usage")

    __table_args__ = (
        UniqueConstraint("key_id", "month", name="uq_api_key_monthly_usage_key_month"),
        Index("ix_api_key_monthly_key_month", "key_id", "month"),
    )
```

---

## API Endpoints

### Webhook Endpoint (public, Stripe-signed)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/webhooks/stripe-apikeys` | Handle Stripe events for API key provisioning | Stripe signature |

**Request:** Raw body (Stripe webhook payload)
**Verification:** `stripe.Webhook.construct_event(payload, sig_header, webhook_secret)`

**Handled events:**

`checkout.session.completed`:
```python
# Extract from session
email = session.customer_details.email
customer_id = session.customer
subscription_id = session.subscription

# Provision key
key = generate_api_key(prefix="at_live_")
store_key(
    key_hash=sha256(key),
    key_prefix=key[:12],
    tier=APIKeyTier.TRIAL,  # starts as trial even on paid checkout (7-day trial)
    user_email=email,
    stripe_customer_id=customer_id,
    stripe_subscription_id=subscription_id,
    monthly_api_limit=100,
    monthly_ai_limit=10,
    rate_limit_per_min=10,
    expires_at=now + timedelta(days=7),
)
log_event("api_key.provisioned", key_id=key.id, email=email)

# Return key in checkout session metadata for success page retrieval
# (The success page calls GET /api/keys/from-session?session_id=...)
```

`customer.subscription.updated`:
```python
# Check subscription status
if subscription.status == "active" and previous_attributes.get("status") == "trialing":
    # Trial converted to paid -- upgrade tier
    update_keys_for_subscription(
        subscription_id=subscription.id,
        tier=APIKeyTier.PRO,
        monthly_api_limit=10000,
        monthly_ai_limit=1000,
        rate_limit_per_min=60,
        expires_at=None,  # No expiration for paid subscriptions
    )
    log_event("api_key.tier_upgraded", subscription_id=subscription.id)
```

`customer.subscription.deleted`:
```python
# Revoke all keys for this subscription
revoke_keys_for_subscription(subscription_id=subscription.id)
log_event("api_key.subscription_cancelled", subscription_id=subscription.id)
```

### Key Retrieval (for success page)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/api/keys/from-session` | Get API key from Stripe checkout session | None (session_id is secret) |

**Query params:** `session_id` (Stripe checkout session ID)
**Response:**
```json
{
  "api_key": "at_live_abc123...",
  "tier": "trial",
  "expires_at": "2026-03-03T00:00:00Z",
  "limits": {
    "monthly_api_calls": 100,
    "monthly_ai_calls": 10,
    "rate_limit_per_min": 10
  }
}
```

**Security:** This endpoint is only callable once per session_id. After retrieval, the plaintext key is cleared from temporary storage. The session_id itself is a sufficient secret (Stripe session IDs are unguessable).

### Admin Key Management (Clerk JWT, admin role)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/api/keys` | Provision a key manually | Clerk JWT (admin) |
| `GET` | `/api/keys` | List all keys (paginated) | Clerk JWT (admin) |
| `GET` | `/api/keys/{id}` | Get key details | Clerk JWT (admin) |
| `DELETE` | `/api/keys/{id}` | Revoke a key | Clerk JWT (admin) |
| `GET` | `/api/keys/{id}/usage` | Get usage stats for a key | Clerk JWT (admin) |

**POST /api/keys** (manual provision):
```json
// Request
{
  "user_email": "dev@example.com",
  "tier": "pro",
  "name": "Dev's production key"
}

// Response (201)
{
  "id": "uuid",
  "api_key": "at_live_abc123...",  // shown once
  "key_prefix": "at_live_abc1",
  "tier": "pro",
  "user_email": "dev@example.com",
  "monthly_api_limit": 10000,
  "monthly_ai_limit": 1000,
  "rate_limit_per_min": 60,
  "created_at": "2026-02-24T00:00:00Z"
}
```

**GET /api/keys** (list):
```json
// Response (200)
{
  "items": [
    {
      "id": "uuid",
      "key_prefix": "at_live_abc1",
      "name": "Dev's production key",
      "tier": "pro",
      "user_email": "dev@example.com",
      "is_test_key": false,
      "monthly_api_limit": 10000,
      "monthly_ai_limit": 1000,
      "rate_limit_per_min": 60,
      "last_used_at": "2026-02-24T12:00:00Z",
      "revoked_at": null,
      "created_at": "2026-02-24T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

**GET /api/keys/{id}/usage**:
```json
// Response (200)
{
  "key_id": "uuid",
  "key_prefix": "at_live_abc1",
  "current_month": {
    "month": "2026-02",
    "api_call_count": 247,
    "ai_call_count": 12,
    "api_limit": 10000,
    "ai_limit": 1000
  },
  "recent_requests": [
    {
      "endpoint": "/api/tests",
      "method": "POST",
      "status_code": 201,
      "response_time_ms": 45,
      "is_ai_call": false,
      "created_at": "2026-02-24T12:00:00Z"
    }
  ],
  "monthly_history": [
    {"month": "2026-02", "api_calls": 247, "ai_calls": 12},
    {"month": "2026-01", "api_calls": 1823, "ai_calls": 89}
  ]
}
```

---

## Auth Middleware

### New: `get_api_key_user()`

```python
class AuthenticatedAPIKeyUser:
    """Represents a validated API key holder."""

    def __init__(
        self,
        key_id: str,
        tier: APIKeyTier,
        email: str,
        monthly_api_limit: int,
        monthly_ai_limit: int,
        rate_limit_per_min: int,
        is_test_key: bool = False,
    ):
        self.key_id = key_id
        self.tier = tier
        self.email = email
        self.monthly_api_limit = monthly_api_limit
        self.monthly_ai_limit = monthly_ai_limit
        self.rate_limit_per_min = rate_limit_per_min
        self.is_test_key = is_test_key


async def get_api_key_user(
    x_api_key: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedAPIKeyUser:
    """Validate X-API-Key header and return authenticated API key user."""
    if not x_api_key:
        raise HTTPException(401, detail="Missing X-API-Key header")

    # Validate prefix format
    if not x_api_key.startswith(("at_live_", "at_test_")):
        raise HTTPException(401, detail="Invalid API key format")

    # Hash and lookup
    key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
    api_key = await db.execute(
        select(APIKey).where(APIKey.key_hash == key_hash)
    )
    api_key = api_key.scalar_one_or_none()

    if not api_key:
        raise HTTPException(401, detail="Invalid API key")
    if api_key.revoked_at:
        raise HTTPException(401, detail="API key has been revoked")
    if api_key.expires_at and api_key.expires_at < datetime.now(UTC):
        raise HTTPException(403, detail="Trial expired. Subscribe at https://adaptivetest.io/developers")

    # Check monthly usage
    # ... (query api_key_monthly_usage for current month)

    # Update last_used_at
    api_key.last_used_at = datetime.now(UTC)
    await db.commit()

    return AuthenticatedAPIKeyUser(
        key_id=api_key.id,
        tier=api_key.tier,
        email=api_key.user_email,
        monthly_api_limit=api_key.monthly_api_limit,
        monthly_ai_limit=api_key.monthly_ai_limit,
        rate_limit_per_min=api_key.rate_limit_per_min,
        is_test_key=api_key.is_test_key,
    )
```

### New: `get_any_authenticated_user()`

```python
async def get_any_authenticated_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser | AuthenticatedAPIKeyUser:
    """Try API key auth first, fall back to Clerk JWT."""
    x_api_key = request.headers.get("X-API-Key")
    if x_api_key:
        return await get_api_key_user(x_api_key=x_api_key, db=db)

    authorization = request.headers.get("Authorization")
    if authorization:
        return await get_current_user(...)  # existing Clerk JWT flow

    raise HTTPException(401, detail="Authentication required. Provide X-API-Key or Authorization header.")
```

### Endpoint Auth Matrix

**Confirmed:** The following matrix is approved. Dual auth endpoints accept both `X-API-Key` and `Authorization: Bearer` headers.

| Endpoint Group | Auth Method | Notes |
|---------------|-------------|-------|
| `/api/tests/*` | API key OR JWT | Core assessment CRUD |
| `/api/sessions/*` | API key OR JWT | Adaptive testing sessions |
| `/api/students/*` | API key OR JWT | Student management |
| `/api/classes/*` | API key OR JWT | Class management |
| `/api/gen-q` | API key OR JWT | AI question generation (counts as AI call) |
| `/api/recs` | API key OR JWT | AI learning recommendations (counts as AI call) |
| `/api/keys/*` | JWT only (admin) | Key management admin endpoints |
| `/api/webhooks/stripe-apikeys` | Stripe signature | Webhook processing |
| `/api/oneroster/*` | JWT only (pro) | OneRoster 1.2 (existing pro gate) |
| `/api/lti/*` | LTI signature | LTI 1.3 (existing) |
| `/api/qti/*` | JWT only (pro) | QTI 3.0 export (existing pro gate) |
| `/api/audit/*` | JWT only (admin) | Audit logs (existing) |

---

## Router Registration

Mount new routes in `src/main.py`:

```python
from src.apikeys.routes import router as apikeys_router
from src.apikeys.stripe_webhooks import router as apikeys_webhook_router

# API key admin routes (JWT admin only)
app.include_router(
    apikeys_router,
    prefix="/api/keys",
    tags=["API Keys"],
    dependencies=[Depends(require_admin)]
)

# Stripe webhook for API key provisioning (no auth dependency -- uses Stripe signature)
app.include_router(
    apikeys_webhook_router,
    prefix="/api/webhooks",
    tags=["Webhooks"]
)
```

For dual-auth endpoints, update existing routers to use `get_any_authenticated_user()` instead of `get_current_user()` where applicable.

---

## Usage Tracking Middleware

Implement as FastAPI middleware or dependency that runs after auth:

```python
async def track_api_key_usage(
    request: Request,
    response: Response,
    user: AuthenticatedAPIKeyUser,
    db: AsyncSession,
):
    """Log API key usage after request completes."""
    is_ai_call = request.url.path in ("/api/gen-q", "/api/recs")

    # Insert raw usage log
    usage = APIKeyUsage(
        key_id=user.key_id,
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        response_time_ms=...,  # calculated from request start time
        is_ai_call=is_ai_call,
    )
    db.add(usage)

    # Upsert monthly rollup
    month = datetime.now(UTC).strftime("%Y-%m")
    await db.execute(
        insert(APIKeyMonthlyUsage)
        .values(key_id=user.key_id, month=month, api_call_count=1, ai_call_count=int(is_ai_call))
        .on_conflict_do_update(
            constraint="uq_api_key_monthly_usage_key_month",
            set_={
                "api_call_count": APIKeyMonthlyUsage.api_call_count + 1,
                "ai_call_count": APIKeyMonthlyUsage.ai_call_count + int(is_ai_call),
                "updated_at": datetime.now(UTC),
            }
        )
    )
    await db.commit()
```

---

## Pydantic Schemas

```python
# --- Request schemas ---

class APIKeyCreate(BaseModel):
    user_email: str = Field(..., max_length=255)
    tier: APIKeyTier = APIKeyTier.PRO
    name: str | None = Field(None, max_length=255)

class APIKeyUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    tier: APIKeyTier | None = None
    monthly_api_limit: int | None = Field(None, ge=0)
    monthly_ai_limit: int | None = Field(None, ge=0)
    rate_limit_per_min: int | None = Field(None, ge=1)

# --- Response schemas ---

class APIKeyResponse(BaseModel):
    id: str
    key_prefix: str
    name: str | None
    tier: APIKeyTier
    user_email: str
    is_test_key: bool
    monthly_api_limit: int
    monthly_ai_limit: int
    rate_limit_per_min: int
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class APIKeyCreatedResponse(APIKeyResponse):
    """Includes plaintext key -- only returned at creation time."""
    api_key: str  # plaintext, shown once

class APIKeyListResponse(BaseModel):
    items: list[APIKeyResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

class MonthlyUsage(BaseModel):
    month: str
    api_call_count: int
    ai_call_count: int

class APIKeyUsageResponse(BaseModel):
    key_id: str
    key_prefix: str
    current_month: MonthlyUsage | None
    monthly_history: list[MonthlyUsage]

class APIKeyFromSessionResponse(BaseModel):
    api_key: str  # plaintext, shown once
    tier: APIKeyTier
    expires_at: datetime | None
    limits: dict  # {monthly_api_calls, monthly_ai_calls, rate_limit_per_min}
```
