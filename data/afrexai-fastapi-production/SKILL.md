---
name: FastAPI Production Engineering
description: Complete methodology for building, deploying, and scaling
  production FastAPI applications. Not a tutorial — a production operating
  system.
---

# FastAPI Production Engineering

Complete methodology for building, deploying, and scaling production FastAPI applications. Not a tutorial — a production operating system.

## Quick Health Check (/16)

Score 2 points each. Total < 8 = critical work needed.

| Signal | Healthy | Unhealthy |
|--------|---------|-----------|
| Type safety | Pydantic v2 models everywhere | `dict` returns, no validation |
| Error handling | Structured error hierarchy | Bare `HTTPException` strings |
| Auth | JWT + dependency injection | Manual token parsing |
| Testing | 80%+ coverage, async tests | No tests or sync-only |
| Database | Async ORM, migrations | Raw SQL, no migrations |
| Observability | Structured logging + tracing | `print()` debugging |
| Deployment | Multi-stage Docker, health checks | `uvicorn main:app` on bare metal |
| Documentation | Auto-generated, accurate OpenAPI | Default `/docs` untouched |

## Phase 1: Project Architecture

### Recommended Structure

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py              # App factory
│   ├── config.py             # Pydantic Settings
│   ├── dependencies.py       # Shared DI
│   ├── middleware.py          # Custom middleware
│   ├── features/
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── router.py     # Endpoints
│   │   │   ├── schemas.py    # Pydantic models
│   │   │   ├── service.py    # Business logic
│   │   │   ├── repository.py # Data access
│   │   │   ├── models.py     # SQLAlchemy/SQLModel
│   │   │   ├── dependencies.py
│   │   │   └── exceptions.py
│   │   ├── auth/
│   │   ├── orders/
│   │   └── ...
│   ├── core/
│   │   ├── database.py       # Engine, session factory
│   │   ├── security.py       # JWT, hashing
│   │   ├── errors.py         # Error hierarchy
│   │   └── logging.py        # Structlog config
│   └── shared/
│       ├── pagination.py
│       ├── filters.py
│       └── responses.py
├── migrations/               # Alembic
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

### 7 Architecture Rules

1. **Feature-based modules** — group by domain, not by layer
2. **Router → Service → Repository** — strict layering, no skipping
3. **Dependency injection everywhere** — use `Depends()` for testability
4. **Pydantic models at boundaries** — validate all input AND output
5. **No business logic in routers** — routers are thin, services are thick
6. **Config via environment** — Pydantic Settings with `.env` support
7. **Async by default** — use async def for all I/O-bound operations

### Framework Selection Context

```yaml
# When to choose FastAPI over alternatives
fastapi_is_best_when:
  - "You need auto-generated OpenAPI docs"
  - "Team knows Python type hints"
  - "API-first (no server-rendered HTML as primary)"
  - "High concurrency with async I/O"
  - "Microservice or API gateway"

consider_alternatives:
  django: "Full-featured web app with admin, ORM, auth batteries"
  flask: "Simple app, team prefers explicit over magic"
  litestar: "Need WebSocket-heavy or more opinionated framework"
  hono_or_express: "Team prefers TypeScript"
```

## Phase 2: Configuration & Environment

### Pydantic Settings Pattern

```python
from pydantic_settings import BaseSettings
from pydantic import SecretStr, field_validator
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "MyAPI"
    debug: bool = False
    environment: str = "production"  # development | staging | production
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Database
    database_url: SecretStr  # Required — no default
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    
    # Auth
    jwt_secret: SecretStr  # Required
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 5 Configuration Rules

1. **Never hardcode secrets** — use `SecretStr` for sensitive values
2. **Fail fast** — required fields have no defaults; app won't start without them
3. **Validate at startup** — use `@field_validator` for constraint checking
4. **Cache settings** — `@lru_cache` ensures single parse
5. **Type everything** — no `str` for structured values; use enums, Literal types

## Phase 3: Pydantic v2 Mastery

### Schema Design Patterns

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID

# Base with common config
class AppSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,      # ORM mode
        str_strip_whitespace=True,  # Auto-strip
        validate_default=True,      # Validate defaults too
    )

# Input schemas (what the API accepts)
class UserCreate(AppSchema):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)

class UserUpdate(AppSchema):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

# Output schemas (what the API returns)
class UserResponse(AppSchema):
    id: UUID
    email: str
    name: str
    created_at: datetime
    # Note: password is NEVER in response schema

# List response with pagination
class PaginatedResponse[T](AppSchema):
    items: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool
```

### 8 Pydantic Rules

1. **Separate Create/Update/Response schemas** — never reuse input as output
2. **Never expose internal fields** — no passwords, internal IDs, or debug info in responses
3. **Use Field() for constraints** — min/max length, regex patterns, gt/lt for numbers
4. **Enable `from_attributes=True`** — for ORM model → schema conversion
5. **Use generics for wrappers** — `PaginatedResponse[T]`, `ApiResponse[T]`
6. **Validate at boundaries** — request body, query params, path params, headers
7. **Use computed fields** — `@computed_field` for derived values
8. **Document with examples** — `model_config = {"json_schema_extra": {"examples": [...]}}`

## Phase 4: Error Handling Architecture

### Structured Error Hierarchy

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS, HTTP_500_INTERNAL_SERVER_ERROR,
)

class AppError(Exception):
    """Base application error."""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            code="NOT_FOUND",
            status_code=HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )

class ConflictError(AppError):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(
            message=message, code="CONFLICT",
            status_code=HTTP_409_CONFLICT,
            details={"field": field} if field else {},
        )

class AuthenticationError(AppError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=HTTP_401_UNAUTHORIZED)

class AuthorizationError(AppError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, code="FORBIDDEN", status_code=HTTP_403_FORBIDDEN)

class ValidationError(AppError):
    def __init__(self, message: str, errors: list[dict] | None = None):
        super().__init__(
            message=message, code="VALIDATION_ERROR",
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors or []},
        )

class RateLimitError(AppError):
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded", code="RATE_LIMITED",
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
        )

# Global error handler
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )

# Register in app factory
# app.add_exception_handler(AppError, app_error_handler)
```

### 6 Error Handling Rules

1. **Never return bare strings** — always structured `{"error": {"code", "message", "details"}}`
2. **Use domain-specific errors** — `NotFoundError("User", user_id)` not `HTTPException(404)`
3. **Global handler catches all** — register `AppError` handler in app factory
4. **Log server errors, don't expose** — 5xx returns generic message, logs full traceback
5. **Include actionable details** — which field failed, what's allowed, retry-after for rate limits
6. **Never leak internals** — no stack traces, SQL queries, or file paths in responses

## Phase 5: Authentication & Authorization

### JWT + Dependency Injection Pattern

```python
from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

security = HTTPBearer()

def create_access_token(user_id: str, roles: list[str], settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
    except JWTError:
        raise AuthenticationError("Invalid or expired token")
    
    user = await db.get(User, user_id)
    if not user:
        raise AuthenticationError("User not found")
    return user

# Role-based authorization
def require_role(*roles: str):
    async def checker(user: User = Depends(get_current_user)) -> User:
        if not any(r in user.roles for r in roles):
            raise AuthorizationError(f"Requires one of: {', '.join(roles)}")
        return user
    return checker

# Usage in router
@router.get("/admin/users")
async def list_users(
    admin: User = Depends(require_role("admin", "superadmin")),
    service: UserService = Depends(get_user_service),
):
    return await service.list_all()
```

### 10-Point Security Checklist

| # | Check | Priority |
|---|-------|----------|
| 1 | JWT secret ≥ 256 bits, from env | P0 |
| 2 | Token expiry ≤ 30 min for access, ≤ 7 days refresh | P0 |
| 3 | Password hashed with bcrypt/argon2 | P0 |
| 4 | CORS configured per environment | P0 |
| 5 | Rate limiting on auth endpoints | P0 |
| 6 | HTTPS enforced (redirect HTTP) | P0 |
| 7 | Security headers (HSTS, CSP, X-Frame) | P1 |
| 8 | Input validation on ALL endpoints | P1 |
| 9 | SQL injection prevented (parameterized queries) | P0 |
| 10 | Dependency scanning (safety/pip-audit) | P1 |

## Phase 6: Database Patterns

### Async SQLAlchemy + Repository Pattern

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select, func
from uuid import uuid4, UUID
from datetime import datetime, timezone

# Engine setup
engine = create_async_engine(
    settings.database_url.get_secret_value(),
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,  # Check connection health
    echo=settings.debug,
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Base model with common fields
class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

# Repository pattern
class BaseRepository[T]:
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: UUID) -> T | None:
        return await self.session.get(self.model, id)
    
    async def get_or_raise(self, id: UUID) -> T:
        entity = await self.get_by_id(id)
        if not entity:
            raise NotFoundError(self.model.__name__, str(id))
        return entity
    
    async def list(
        self, *, offset: int = 0, limit: int = 20, **filters
    ) -> tuple[list[T], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)
        
        for field, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, field) == value)
                count_query = count_query.where(getattr(self.model, field) == value)
        
        total = await self.session.scalar(count_query) or 0
        result = await self.session.execute(
            query.offset(offset).limit(limit).order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all()), total
    
    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity
    
    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
```

### ORM Selection Guide

| ORM | Best For | Async | Type Safety | Learning Curve |
|-----|----------|-------|-------------|----------------|
| **SQLAlchemy 2.0** | Complex queries, enterprise | ✅ | ✅ Mapped[] | Medium |
| **SQLModel** | Simple CRUD, Pydantic sync | ✅ | ✅ | Low |
| **Tortoise** | Django-like feel | ✅ | Partial | Low |
| **Piccolo** | Modern, migrations built-in | ✅ | ✅ | Low |

**Recommendation:** SQLAlchemy 2.0 for production. SQLModel for prototypes.

### Migration Strategy (Alembic)

```bash
# Setup
alembic init migrations
# Edit alembic.ini: sqlalchemy.url = from env

# Generate migration
alembic revision --autogenerate -m "add users table"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Migration Rules:**
1. Always review autogenerated migrations before applying
2. Never edit applied migrations — create new ones
3. Test migrations in staging before production
4. Include `downgrade()` for every `upgrade()`
5. Use `batch_alter_table` for SQLite compatibility

## Phase 7: Testing Strategy

### Test Pyramid

| Level | Coverage Target | Tools | Focus |
|-------|----------------|-------|-------|
| Unit | 80%+ | pytest, unittest.mock | Service logic, validators |
| Integration | Key paths | pytest-asyncio, testcontainers | DB queries, external APIs |
| E2E | Critical flows | httpx.AsyncClient | Full request→response |
| Contract | API boundaries | schemathesis | OpenAPI compliance |

### Test Patterns

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app

@pytest.fixture
async def app():
    app = create_app()
    yield app

@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_client(client, test_user):
    token = create_access_token(test_user.id, test_user.roles)
    client.headers["Authorization"] = f"Bearer {token}"
    return client

# E2E test
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/users", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data  # Never expose

# Unit test (service layer)
@pytest.mark.asyncio
async def test_user_service_duplicate_email(user_service, mock_repo):
    mock_repo.get_by_email.return_value = existing_user
    with pytest.raises(ConflictError, match="Email already registered"):
        await user_service.create(UserCreate(email="taken@example.com", ...))

# Parametrized validation
@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("invalid", False),
    ("", False),
    ("a@b.c", True),
])
def test_email_validation(email, expected):
    if expected:
        UserCreate(email=email, name="Test", password="12345678")
    else:
        with pytest.raises(ValidationError):
            UserCreate(email=email, name="Test", password="12345678")
```

### 7 Testing Rules

1. **Test services, not routers** — business logic lives in services
2. **Use fixtures for DI override** — swap real DB with test DB via `app.dependency_overrides`
3. **One assertion per test** — clear what broke when it fails
4. **Test error paths** — 40% of tests should be sad-path
5. **Use factories for test data** — `UserFactory.create()` not manual dict construction
6. **Async tests need `@pytest.mark.asyncio`** — or set `asyncio_mode = "auto"` in config
7. **Run tests in CI** — block merge if tests fail

## Phase 8: Structured Logging & Observability

### Structlog Setup

```python
import structlog
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Request ID middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        logger.info(
            "request_completed",
            status_code=response.status_code,
        )
        return response
```

### Health Check Endpoints

```python
@router.get("/health")
async def health():
    """Liveness probe — is the process running?"""
    return {"status": "ok"}

@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    """Readiness probe — can we serve traffic?"""
    checks = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
    
    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
```

## Phase 9: Performance Optimization

### Priority Stack

| # | Technique | Impact | Effort |
|---|-----------|--------|--------|
| 1 | Async database queries | High | Low |
| 2 | Connection pooling (tuned) | High | Low |
| 3 | Response caching (Redis) | High | Medium |
| 4 | Background tasks for heavy work | High | Low |
| 5 | Pagination on all list endpoints | Medium | Low |
| 6 | Select only needed columns | Medium | Low |
| 7 | Eager loading (joinedload) | Medium | Medium |
| 8 | Rate limiting | Medium | Low |

### Background Tasks

```python
from fastapi import BackgroundTasks

@router.post("/users", status_code=201)
async def create_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service),
):
    user = await service.create(user_in)
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    return user
```

### Caching Pattern

```python
from redis.asyncio import Redis
import json

class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get_or_set(self, key: str, factory, ttl: int = 300):
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        result = await factory()
        await self.redis.setex(key, ttl, json.dumps(result, default=str))
        return result
    
    async def invalidate(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

## Phase 10: Production Deployment

### Multi-Stage Dockerfile

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app

RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Production stage
FROM python:3.12-slim
WORKDIR /app

RUN adduser --disabled-password --no-create-home appuser

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD ["python", "-c", "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"]

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### App Factory Pattern

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("starting_up", environment=settings.environment)
    await init_db()
    yield
    # Shutdown
    logger.info("shutting_down")
    await engine.dispose()

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
    )
    
    # Middleware (order matters — last added = first executed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    
    # Error handlers
    app.add_exception_handler(AppError, app_error_handler)
    
    # Routers
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(health_router, tags=["health"])
    
    return app

app = create_app()
```

### GitHub Actions CI

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install uv && uv sync
      - run: uv run ruff check .
      - run: uv run mypy src/
      - run: uv run pytest --cov=src --cov-report=xml -x
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:test@localhost:5432/testdb
          JWT_SECRET: test-secret-key-at-least-32-chars
```

### Production Checklist

**P0 — Mandatory:**
- [ ] All secrets from environment variables (SecretStr)
- [ ] HTTPS enforced
- [ ] CORS configured per environment
- [ ] Rate limiting on auth endpoints
- [ ] Input validation on all endpoints
- [ ] Structured error responses (no stack traces)
- [ ] Health + readiness endpoints
- [ ] Database connection pooling
- [ ] Migrations run before deploy
- [ ] Structured logging (JSON)
- [ ] Tests passing in CI

**P1 — Recommended:**
- [ ] OpenTelemetry tracing
- [ ] Prometheus metrics endpoint
- [ ] Background task queue (Celery/ARQ)
- [ ] Redis caching layer
- [ ] API versioning strategy
- [ ] Request/response logging
- [ ] Dependency security scanning
- [ ] Performance benchmarks established

## Phase 11: Advanced Patterns

### Middleware Stack Order

```python
# Applied bottom-to-top (last added = first executed)
app.add_middleware(GZipMiddleware, minimum_size=1000)    # 5. Compress
app.add_middleware(CORSMiddleware, ...)                  # 4. CORS
app.add_middleware(RequestIDMiddleware)                   # 3. Request ID
app.add_middleware(RateLimitMiddleware)                   # 2. Rate limit
app.add_middleware(TrustedHostMiddleware, allowed=["*"])  # 1. Host check
```

### Pagination with Cursor-Based Option

```python
from fastapi import Query

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.offset = (page - 1) * page_size
        self.limit = page_size
        self.page = page
        self.page_size = page_size

@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    service: UserService = Depends(get_user_service),
):
    items, total = await service.list(
        offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=items, total=total,
        page=pagination.page, page_size=pagination.page_size,
        has_next=(pagination.offset + pagination.limit) < total,
    )
```

### WebSocket Pattern

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, ws: WebSocket):
        await ws.accept()
        self.connections[user_id] = ws
    
    def disconnect(self, user_id: str):
        self.connections.pop(user_id, None)
    
    async def send(self, user_id: str, message: dict):
        if ws := self.connections.get(user_id):
            await ws.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Process message
    except WebSocketDisconnect:
        manager.disconnect(user_id)
```

### File Upload Pattern

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    user: User = Depends(get_current_user),
):
    # Validate
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("File too large (max 10MB)")
    
    allowed_types = {"image/jpeg", "image/png", "application/pdf"}
    if file.content_type not in allowed_types:
        raise ValidationError(f"File type not allowed: {file.content_type}")
    
    # Save
    contents = await file.read()
    path = f"uploads/{user.id}/{file.filename}"
    # Save to S3/local storage...
    
    return {"filename": file.filename, "size": len(contents)}
```

## Phase 12: Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Sync database calls in async app | Use async SQLAlchemy/databases |
| 2 | Business logic in route handlers | Move to service layer |
| 3 | No input validation | Pydantic models on every endpoint |
| 4 | Returning ORM models directly | Use response schemas (from_attributes) |
| 5 | Hardcoded config values | Pydantic Settings + env vars |
| 6 | No error handling strategy | Custom exception hierarchy + global handler |
| 7 | Missing health checks | /health + /ready endpoints |
| 8 | `print()` for logging | structlog with JSON output |
| 9 | No pagination on list endpoints | Default limit, max cap (100) |
| 10 | Testing against production DB | Test fixtures with separate DB |

## Quality Scoring (0–100)

| Dimension | Weight | 0–25 | 50 | 75 | 100 |
|-----------|--------|------|----|----|-----|
| Type Safety | 15% | No types | Partial Pydantic | Full schemas | Strict mypy pass |
| Error Handling | 15% | Bare HTTPException | Custom errors | Full hierarchy | + monitoring |
| Testing | 15% | None | Happy path | 80%+ coverage | + contract tests |
| Security | 15% | No auth | Basic JWT | + RBAC + rate limit | + scanning + audit |
| Performance | 10% | Sync everything | Async DB | + caching | + profiling |
| Observability | 10% | print() | Structured logs | + tracing | + metrics + alerts |
| Database | 10% | Raw SQL | ORM + migrations | + repository pattern | + connection tuning |
| Deployment | 10% | Manual | Dockerfile | + CI/CD | + health + rollback |

**Scoring:** Your Score = Σ (dimension score × weight). **< 40 = critical, 40–60 = needs work, 60–80 = solid, 80+ = production-grade.**

## 10 Commandments of FastAPI Production

1. **Pydantic models at every boundary** — request, response, config
2. **Async all the way down** — one sync call blocks the event loop
3. **Services own business logic** — routers are thin wrappers
4. **Dependency injection for testability** — `Depends()` is your best friend
5. **Structured errors, structured logs** — JSON everything
6. **Health checks are non-negotiable** — liveness + readiness
7. **Test the sad paths** — 40% of tests should be error cases
8. **Migrations before deployment** — never modify schema manually
9. **Secrets in environment, never in code** — `SecretStr` enforces this
10. **Profile before optimizing** — measure, don't guess

## Natural Language Commands

- `audit my FastAPI project` → Run health check, identify gaps
- `set up a new FastAPI project` → Generate project structure + config
- `add authentication to my API` → JWT + RBAC dependency pattern
- `create a CRUD feature for [resource]` → Full router/service/repo/schemas
- `optimize my database queries` → Connection pooling + async + N+1 prevention
- `add structured logging` → Structlog + request ID middleware
- `write tests for [feature]` → Async test patterns + fixtures
- `prepare for production deployment` → Dockerfile + CI + checklist
- `add caching to my API` → Redis caching pattern
- `set up error handling` → Custom exception hierarchy + global handler
- `add WebSocket support` → Connection manager pattern
- `review my API security` → 10-point security checklist audit

---

⚡ **Level up your FastAPI APIs** → Get the [AfrexAI SaaS Context Pack ($47)](https://afrexai-cto.github.io/context-packs/) for complete SaaS architecture, pricing strategies, and go-to-market playbooks.

🔗 **More free skills by AfrexAI:**
- [afrexai-python-production](https://clawhub.com/skills/afrexai-python-production) — Python production engineering
- [afrexai-api-architecture](https://clawhub.com/skills/afrexai-api-architecture) — API design methodology
- [afrexai-database-engineering](https://clawhub.com/skills/afrexai-database-engineering) — Database patterns
- [afrexai-test-automation-engineering](https://clawhub.com/skills/afrexai-test-automation-engineering) — Testing strategy
- [afrexai-cicd-engineering](https://clawhub.com/skills/afrexai-cicd-engineering) — CI/CD pipeline design

🛒 Browse all packs → [AfrexAI Storefront](https://afrexai-cto.github.io/context-packs/)
