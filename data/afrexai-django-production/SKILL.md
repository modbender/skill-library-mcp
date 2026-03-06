---
name: Django Production Engineering
description: Complete methodology for building, scaling, and operating
  production Django applications. From project structure to deployment, security
  to performance — every decision framework a Django team needs.
---

# Django Production Engineering

Complete methodology for building, scaling, and operating production Django applications. From project structure to deployment, security to performance — every decision framework a Django team needs.

## Quick Health Check

Run this 8-signal triage on any Django project:

| # | Signal | Check | Healthy |
|---|--------|-------|---------|
| 1 | Settings split | `settings/base.py`, `local.py`, `production.py` exist | ✅ Split by env |
| 2 | Secret management | `SECRET_KEY` not in code, `DEBUG=False` in prod | ✅ Env vars / vault |
| 3 | Database | Using connection pooling (pgbouncer / django-db-conn-pool) | ✅ Pool configured |
| 4 | Migrations | `python manage.py showmigrations` — no unapplied | ✅ All applied |
| 5 | Static files | `collectstatic` + CDN/whitenoise configured | ✅ Served properly |
| 6 | Async tasks | Celery/django-q/Huey for background work | ✅ Not blocking views |
| 7 | Caching | Cache backend configured (Redis/Memcached) | ✅ Not DummyCache |
| 8 | Security | `python manage.py check --deploy` passes | ✅ All checks pass |

**Score: count ✅ / 8** — Below 6 = stop and fix foundations first.

---

## Phase 1: Project Architecture

### Recommended Structure

```
myproject/
├── config/                    # Project config (was myproject/)
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py           # Shared settings
│   │   ├── local.py          # Development
│   │   ├── staging.py        # Staging
│   │   └── production.py     # Production
│   ├── urls.py               # Root URL conf
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py             # Celery app
├── apps/
│   ├── users/                # Custom user model (ALWAYS)
│   │   ├── models.py
│   │   ├── managers.py
│   │   ├── admin.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py       # Business logic
│   │   ├── selectors.py      # Complex queries
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_services.py
│   │   └── migrations/
│   ├── core/                 # Shared utilities
│   │   ├── models.py         # Abstract base models
│   │   ├── permissions.py
│   │   ├── pagination.py
│   │   ├── exceptions.py
│   │   └── middleware.py
│   └── <domain>/             # Feature apps
├── templates/
├── static/
├── media/
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── docker/
├── scripts/
├── manage.py
├── pyproject.toml
├── Makefile
└── .env.example
```

### 7 Architecture Rules

1. **Custom user model from Day 1** — `AUTH_USER_MODEL = 'users.User'`. Changing later is extremely painful.
2. **Fat services, thin views** — Views handle HTTP; `services.py` handles business logic; `selectors.py` handles complex queries.
3. **One app per domain** — Not per model. Group related models in one app.
4. **Settings split by environment** — Never use `if DEBUG` conditionally in a single file.
5. **Abstract base models in core** — `TimeStampedModel`, `UUIDModel` shared across apps.
6. **Separate requirements files** — `base.txt` (shared), `local.txt` (dev tools), `production.txt` (gunicorn, sentry).
7. **Keep apps decoupled** — Apps communicate through services, not by importing each other's models directly. Use signals sparingly.

### Abstract Base Models

```python
# apps/core/models.py
import uuid
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        from django.utils import timezone
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])
```

---

## Phase 2: ORM Mastery & Query Optimization

### N+1 Query Prevention

```python
# ❌ N+1 — fires 1 + N queries
for order in Order.objects.all():
    print(order.customer.name)        # Each access = new query
    for item in order.items.all():    # Each access = new query
        print(item.product.name)      # Each access = new query

# ✅ Optimized — fires 3 queries total
orders = (
    Order.objects
    .select_related("customer")              # FK/OneToOne — JOIN
    .prefetch_related(
        Prefetch(
            "items",
            queryset=OrderItem.objects
                .select_related("product")   # Nested FK
                .only("id", "quantity", "product__name")  # Only needed fields
        )
    )
)
```

### select_related vs prefetch_related Decision

| Relationship | Use | Why |
|---|---|---|
| ForeignKey (forward) | `select_related` | SQL JOIN, single query |
| OneToOneField | `select_related` | SQL JOIN, single query |
| ManyToMany | `prefetch_related` | Separate query, Python join |
| Reverse FK (set) | `prefetch_related` | Separate query, Python join |
| Filtered prefetch | `Prefetch()` object | Custom queryset |

### QuerySet Evaluation Rules

```python
# QuerySets are LAZY — no database hit until evaluated
qs = Order.objects.filter(status="pending")  # No query yet

# These EVALUATE the queryset (trigger SQL):
list(qs)           # Iteration
len(qs)            # Use qs.count() instead
bool(qs)           # Use qs.exists() instead
qs[0]              # Indexing
repr(qs)           # In shell/debugger
for obj in qs:     # Iteration
if qs:             # Use qs.exists()
```

### Bulk Operations

```python
# ❌ N queries
for item in items:
    Product.objects.create(name=item["name"], price=item["price"])

# ✅ 1 query
Product.objects.bulk_create(
    [Product(name=i["name"], price=i["price"]) for i in items],
    batch_size=1000,
    ignore_conflicts=True,  # Skip duplicates
)

# ✅ Bulk update
Product.objects.filter(category="sale").update(
    price=F("price") * 0.9  # 10% discount — single query, no race conditions
)

# ✅ Bulk update with different values
products = Product.objects.filter(id__in=ids)
for p in products:
    p.price = new_prices[p.id]
Product.objects.bulk_update(products, ["price"], batch_size=1000)
```

### Database Functions & Expressions

```python
from django.db.models import F, Q, Value, Count, Avg, Sum, Case, When
from django.db.models.functions import Coalesce, Lower, TruncMonth

# Conditional aggregation
Order.objects.aggregate(
    total_revenue=Sum("amount"),
    paid_revenue=Sum("amount", filter=Q(status="paid")),
    refund_count=Count("id", filter=Q(status="refunded")),
    avg_order_value=Avg("amount", filter=Q(status="paid")),
)

# Annotate with computed fields
customers = (
    Customer.objects
    .annotate(
        order_count=Count("orders"),
        total_spent=Coalesce(Sum("orders__amount"), Value(0)),
        last_order=Max("orders__created_at"),
    )
    .filter(order_count__gte=5)
    .order_by("-total_spent")
)

# Monthly revenue report
monthly = (
    Order.objects
    .filter(status="paid")
    .annotate(month=TruncMonth("created_at"))
    .values("month")
    .annotate(
        revenue=Sum("amount"),
        count=Count("id"),
        avg=Avg("amount"),
    )
    .order_by("month")
)

# Case/When for computed status
users = User.objects.annotate(
    tier=Case(
        When(total_spent__gte=10000, then=Value("platinum")),
        When(total_spent__gte=5000, then=Value("gold")),
        When(total_spent__gte=1000, then=Value("silver")),
        default=Value("bronze"),
    )
)
```

### Index Strategy

```python
class Order(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, db_index=True)  # Single column
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        indexes = [
            # Composite index — for queries filtering both
            models.Index(fields=["status", "created_at"], name="idx_order_status_created"),
            # Partial index — only index what you query
            models.Index(
                fields=["customer"],
                condition=Q(status="pending"),
                name="idx_order_pending_customer",
            ),
            # Covering index (Postgres) — avoid table lookup
            models.Index(
                fields=["status"],
                include=["amount", "created_at"],
                name="idx_order_status_covering",
            ),
        ]
        # Default ordering impacts ALL queries — be intentional
        ordering = ["-created_at"]
```

### 8 ORM Rules

1. **Always use `select_related`/`prefetch_related`** — install django-debug-toolbar and watch query count.
2. **Never use `.count()` + `.all()` together** — use `.exists()` for boolean checks.
3. **Use `F()` expressions** for atomic updates — avoids race conditions.
4. **Use `.only()` / `.defer()`** for large text/JSON fields you don't need.
5. **Use `.values()` / `.values_list()`** when you don't need model instances.
6. **Use `iterator(chunk_size=2000)`** for large result sets — reduces memory.
7. **Profile with `django-silk` or `django-debug-toolbar`** — never guess at performance.
8. **Use `Exists()` subqueries** instead of `__in` with large lists.

---

## Phase 3: Django REST Framework (DRF)

### Serializer Patterns

```python
# apps/orders/serializers.py
from rest_framework import serializers

class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight for list views — minimal fields."""
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "customer_name", "status", "amount", "created_at"]
        read_only_fields = ["id", "created_at"]

class OrderDetailSerializer(serializers.ModelSerializer):
    """Full detail with nested items."""
    items = OrderItemSerializer(many=True, read_only=True)
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = "__all__"

class OrderCreateSerializer(serializers.Serializer):
    """Explicit create — don't use ModelSerializer for writes."""
    customer_id = serializers.UUIDField()
    items = OrderItemInputSerializer(many=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item required.")
        return value
    
    def create(self, validated_data):
        # Delegate to service layer
        from apps.orders.services import create_order
        return create_order(**validated_data)
```

### Service Layer Pattern

```python
# apps/orders/services.py
from django.db import transaction
from django.core.exceptions import ValidationError

def create_order(*, customer_id: str, items: list[dict], notes: str = "") -> Order:
    """
    Create order with items atomically.
    
    Raises:
        ValidationError: If customer not found or insufficient stock.
    """
    customer = Customer.objects.filter(id=customer_id).first()
    if not customer:
        raise ValidationError("Customer not found.")
    
    with transaction.atomic():
        order = Order.objects.create(customer=customer, notes=notes)
        
        order_items = []
        for item_data in items:
            product = Product.objects.select_for_update().get(id=item_data["product_id"])
            if product.stock < item_data["quantity"]:
                raise ValidationError(f"Insufficient stock for {product.name}")
            
            product.stock -= item_data["quantity"]
            product.save(update_fields=["stock"])
            
            order_items.append(
                OrderItem(order=order, product=product, quantity=item_data["quantity"], unit_price=product.price)
            )
        
        OrderItem.objects.bulk_create(order_items)
        order.amount = sum(i.unit_price * i.quantity for i in order_items)
        order.save(update_fields=["amount"])
    
    # Side effects OUTSIDE transaction
    send_order_confirmation.delay(order.id)
    return order
```

### ViewSet Best Practices

```python
# apps/orders/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Always scope to current user. Never return all objects."""
        return (
            Order.objects
            .filter(customer__user=self.request.user)
            .select_related("customer")
            .prefetch_related("items__product")
        )
    
    def get_serializer_class(self):
        """Different serializers for different actions."""
        if self.action == "list":
            return OrderListSerializer
        if self.action in ("create",):
            return OrderCreateSerializer
        return OrderDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        from apps.orders.services import cancel_order
        try:
            cancel_order(order=order, cancelled_by=request.user)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "cancelled"})
    
    @action(detail=False, methods=["get"])
    def summary(self, request):
        from apps.orders.selectors import get_order_summary
        data = get_order_summary(user=request.user)
        return Response(data)
```

### Pagination

```python
# apps/core/pagination.py
from rest_framework.pagination import CursorPagination

class StandardCursorPagination(CursorPagination):
    """Cursor pagination — O(1) performance regardless of offset."""
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"

# settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardCursorPagination",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
}
```

---

## Phase 4: Authentication & Security

### JWT Authentication (SimpleJWT)

```python
# config/settings/base.py
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Custom user model
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from apps.users.managers import UserManager

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = UserManager()
```

### Security Settings (Production)

```python
# config/settings/production.py
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Content security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# CORS (django-cors-headers)
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")
CORS_ALLOW_CREDENTIALS = True

# CSP (django-csp)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

### Permission Patterns

```python
# apps/core/permissions.py
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """Object-level: only the owner can access."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.is_staff

class HasRole(BasePermission):
    """Role-based access control."""
    required_role = None
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.roles.filter(name=self.required_role).exists()

class IsManager(HasRole):
    required_role = "manager"
```

### 10-Point Security Checklist

| # | Check | How | Priority |
|---|-------|-----|----------|
| 1 | `manage.py check --deploy` | All warnings resolved | P0 |
| 2 | `SECRET_KEY` from env/vault | Not in source code | P0 |
| 3 | `DEBUG = False` in production | Env-specific settings | P0 |
| 4 | HTTPS enforced | `SECURE_SSL_REDIRECT = True` | P0 |
| 5 | CSRF protection enabled | Default — don't disable it | P0 |
| 6 | SQL injection prevented | Always use ORM, never raw SQL with f-strings | P0 |
| 7 | Input validation | Serializer validation on all inputs | P1 |
| 8 | Rate limiting | DRF throttling configured | P1 |
| 9 | Admin URL changed | Not `/admin/` — use random path | P1 |
| 10 | Dependency audit | `pip-audit` or `safety check` in CI | P1 |

---

## Phase 5: Migrations & Database Management

### Migration Safety Rules

1. **Never edit a migration after it's been applied in production** — create a new one.
2. **Always review auto-generated migrations** — `makemigrations` can produce destructive changes.
3. **Add columns as nullable first** — `null=True` → deploy → backfill → make non-null.
4. **Never rename columns directly** — add new, migrate data, remove old (3 deployments).
5. **Use `RunPython` with `reverse_code`** — always make migrations reversible.
6. **Squash periodically** — `squashmigrations app_name 0001 0050` for performance.
7. **Lock table awareness** — `ALTER TABLE ADD COLUMN NOT NULL DEFAULT` locks the table in Postgres < 11.

### Zero-Downtime Migration Pattern

```python
# Step 1: Add nullable column (safe, no lock)
# migrations/0042_add_new_field.py
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]

# Step 2: Backfill data (separate migration)
# migrations/0043_backfill_tracking.py
def backfill_tracking(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    batch_size = 1000
    while True:
        ids = list(
            Order.objects.filter(tracking_number__isnull=True)
            .values_list("id", flat=True)[:batch_size]
        )
        if not ids:
            break
        Order.objects.filter(id__in=ids).update(tracking_number="LEGACY")

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(backfill_tracking, migrations.RunPython.noop),
    ]

# Step 3: Make non-null (after backfill verified)
# migrations/0044_tracking_not_null.py
```

### Migration Conflict Resolution

```bash
# When two developers create migrations from same parent:
python manage.py makemigrations --merge  # Creates merge migration

# To detect conflicts in CI:
python manage.py makemigrations --check --dry-run
```

---

## Phase 6: Caching Strategy

### Cache Hierarchy

```python
# config/settings/base.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": "myapp",
        "TIMEOUT": 300,  # 5 min default
    }
}

# Session storage in Redis (faster than DB)
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### Caching Patterns

```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# View-level caching
@cache_page(60 * 15)  # 15 minutes
def product_list(request):
    ...

# Manual cache with invalidation
def get_product_stats(product_id: str) -> dict:
    cache_key = f"product_stats:{product_id}"
    stats = cache.get(cache_key)
    if stats is None:
        stats = _compute_product_stats(product_id)
        cache.set(cache_key, stats, timeout=600)
    return stats

def invalidate_product_cache(product_id: str):
    cache.delete(f"product_stats:{product_id}")

# Signal-based cache invalidation
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    invalidate_product_cache(str(instance.id))
    cache.delete("product_list")

# Template fragment caching
# {% load cache %}
# {% cache 600 sidebar request.user.id %}
#   ... expensive template fragment ...
# {% endcache %}
```

### Cache Decision Guide

| Data Type | Strategy | TTL | Invalidation |
|---|---|---|---|
| User session | Redis session backend | 2 weeks | On logout |
| API list endpoint | `cache_page` | 5 min | Time-based |
| Computed aggregations | Manual `cache.set` | 10-30 min | Signal on write |
| Per-user dashboard | Manual with user key | 5 min | On user action |
| Static config/settings | Manual, long TTL | 1 hour | On admin save |
| Full-page (anonymous) | Nginx/CDN | 1-60 min | Purge API |

---

## Phase 7: Background Tasks (Celery)

### Celery Configuration

```python
# config/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
app = Celery("myapp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# config/settings/base.py
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300  # 5 min hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 min soft limit
CELERY_TASK_ACKS_LATE = True  # Re-deliver if worker crashes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Fair scheduling
```

### Task Patterns

```python
# apps/orders/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    acks_late=True,
)
def send_order_confirmation(self, order_id: str):
    """Send confirmation email with exponential backoff retry."""
    try:
        order = Order.objects.select_related("customer__user").get(id=order_id)
        send_email(
            to=order.customer.user.email,
            template="order_confirmation",
            context={"order": order},
        )
        logger.info("Confirmation sent", extra={"order_id": order_id})
    except Order.DoesNotExist:
        logger.error("Order not found", extra={"order_id": order_id})
        # Don't retry — order doesn't exist

@shared_task
def generate_daily_report():
    """Periodic task — scheduled via beat."""
    from apps.reports.services import build_daily_report
    report = build_daily_report()
    notify_admins(report)

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    "daily-report": {
        "task": "apps.orders.tasks.generate_daily_report",
        "schedule": crontab(hour=6, minute=0),
    },
    "cleanup-expired-sessions": {
        "task": "apps.users.tasks.cleanup_sessions",
        "schedule": crontab(hour=3, minute=0),
    },
}
```

### 6 Celery Rules

1. **Always pass IDs, not objects** — `task.delay(order.id)` not `task.delay(order)`. Objects can't serialize and may be stale.
2. **Set time limits** — Every task needs `time_limit` to prevent zombies.
3. **Make tasks idempotent** — They may run more than once (acks_late + crash = re-delivery).
4. **Use `autoretry_for`** — Declarative retry for transient errors.
5. **Separate queues** — Critical tasks (payments) on different queue than bulk (emails).
6. **Monitor with Flower** — `celery -A config flower` for real-time task monitoring.

---

## Phase 8: Testing Strategy

### Test Pyramid

| Level | Tool | Target | Speed |
|---|---|---|---|
| Unit | pytest | Services, utils, models | <1s each |
| Integration | pytest + Django test client | Views, serializers, DB | <5s each |
| E2E | Playwright/Selenium | Full user flows | <30s each |
| Contract | schemathesis/dredd | API schema compliance | <10s each |

### Testing Patterns

```python
# conftest.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com", password="testpass123")

@pytest.fixture
def order_factory(db):
    def create(**kwargs):
        defaults = {"status": "pending", "amount": 100}
        defaults.update(kwargs)
        if "customer" not in defaults:
            defaults["customer"] = CustomerFactory.create()
        return Order.objects.create(**defaults)
    return create

# Test service layer
class TestCreateOrder:
    def test_creates_order_with_items(self, db, customer, product):
        order = create_order(
            customer_id=customer.id,
            items=[{"product_id": product.id, "quantity": 2}],
        )
        assert order.amount == product.price * 2
        assert order.items.count() == 1
        assert product.stock == Product.objects.get(id=product.id).stock  # Verify stock deducted

    def test_rejects_insufficient_stock(self, db, customer, product):
        product.stock = 0
        product.save()
        with pytest.raises(ValidationError, match="Insufficient stock"):
            create_order(
                customer_id=customer.id,
                items=[{"product_id": product.id, "quantity": 1}],
            )

# Test views
class TestOrderAPI:
    def test_list_returns_only_user_orders(self, authenticated_client, user, order_factory):
        my_order = order_factory(customer__user=user)
        other_order = order_factory()  # Different user
        
        response = authenticated_client.get("/api/orders/")
        assert response.status_code == 200
        ids = [o["id"] for o in response.data["results"]]
        assert str(my_order.id) in ids
        assert str(other_order.id) not in ids

    def test_create_order_validates_items(self, authenticated_client):
        response = authenticated_client.post("/api/orders/", {"items": []}, format="json")
        assert response.status_code == 400
```

### 7 Testing Rules

1. **Use `pytest-django`** — not Django's `TestCase`. Faster, better fixtures.
2. **Use factories** — `factory_boy` or custom fixtures. Never seed test DB manually.
3. **Test services, not views** — Business logic in services = easy to test without HTTP.
4. **Use `@pytest.mark.django_db`** — Only tests that need DB should hit it.
5. **Freeze time** — `freezegun` for time-dependent logic.
6. **Mock external services** — `responses` for HTTP, `unittest.mock` for others.
7. **CI runs `pytest --cov --cov-fail-under=80`** — Enforce coverage floor.

---

## Phase 9: Performance & Monitoring

### Gunicorn Configuration

```python
# config/gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"  # or "uvicorn.workers.UvicornWorker" for async
threads = 4
max_requests = 1000
max_requests_jitter = 50
timeout = 30
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Django Middleware Order (Performance)

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # Static files (before everything)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",           # CORS (before CommonMiddleware)
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.RequestIDMiddleware",         # Custom: attach request ID
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

### Structured Logging

```python
# config/settings/base.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {"level": "WARNING"},  # Quiet SQL logs
        "apps": {"level": "INFO", "propagate": True},
    },
}
```

### Performance Targets

| Metric | Target | How to Measure |
|---|---|---|
| p50 response time | <100ms | django-silk / APM |
| p99 response time | <500ms | APM (Sentry, Datadog) |
| DB queries per request | <10 | django-debug-toolbar |
| Memory per worker | <256MB | Gunicorn + monitoring |
| Celery task latency | <5s | Flower / Prometheus |

---

## Phase 10: Deployment

### Production Dockerfile

```dockerfile
# Multi-stage build
FROM python:3.12-slim AS builder
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY requirements/production.txt .
RUN uv pip install --system --no-cache -r production.txt

FROM python:3.12-slim
RUN adduser --disabled-password --no-create-home app
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

RUN python manage.py collectstatic --noinput
USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "-c", "config/gunicorn.conf.py"]
```

### GitHub Actions CI/CD

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
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ["5432:5432"]
      redis:
        image: redis:7
        ports: ["6379:6379"]
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements/local.txt
      - run: python manage.py check --deploy
        env:
          DJANGO_SETTINGS_MODULE: config.settings.local
      - run: python manage.py makemigrations --check --dry-run
      - run: pytest --cov --cov-fail-under=80 -n auto
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
      - run: ruff check .
      - run: ruff format --check .
      - run: mypy apps/
```

### Production Checklist

**P0 — Must have before deploy:**
- [ ] `manage.py check --deploy` passes with zero warnings
- [ ] `SECRET_KEY` from environment variable
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enforced
- [ ] Database connection pooling
- [ ] Static files served via WhiteNoise/CDN
- [ ] Error tracking (Sentry) configured
- [ ] Backups scheduled

**P1 — Should have within first week:**
- [ ] Rate limiting on all endpoints
- [ ] Admin URL changed from `/admin/`
- [ ] Cache backend configured (Redis)
- [ ] Background tasks via Celery
- [ ] Structured JSON logging
- [ ] CI/CD pipeline
- [ ] Health check endpoint
- [ ] `pip-audit` in CI

---

## Phase 11: Common Patterns Library

### Soft Delete Manager

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Order(SoftDeleteModel):
    objects = ActiveManager()      # Default: excludes deleted
    all_objects = models.Manager() # Include deleted
```

### Multi-Tenant Pattern

```python
# Middleware: set tenant from request
class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request.tenant = Tenant.objects.get(id=tenant_id)
        return self.get_response(request)

# Auto-filter all queries by tenant
class TenantManager(models.Manager):
    def get_queryset(self):
        from threading import local
        _thread_local = local()
        qs = super().get_queryset()
        tenant = getattr(_thread_local, "tenant", None)
        if tenant:
            qs = qs.filter(tenant=tenant)
        return qs
```

### Webhook Handler

```python
import hashlib, hmac
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({"error": "Invalid signature"}, status=400)
    
    handlers = {
        "checkout.session.completed": handle_checkout,
        "invoice.paid": handle_invoice_paid,
        "customer.subscription.deleted": handle_cancellation,
    }
    
    handler = handlers.get(event["type"])
    if handler:
        handler(event["data"]["object"])
    
    return JsonResponse({"status": "ok"})
```

---

## Phase 12: Django 5.x Features

### GeneratedField (Django 5.0+)

```python
class Product(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.20)
    
    total_price = models.GeneratedField(
        expression=F("price") * (1 + F("tax_rate")),
        output_field=models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True,  # Stored column, not virtual
    )
```

### Field Groups in Forms (Django 5.0+)

```python
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    
    # Template: {{ form.as_field_group }}
```

### Database-Computed Default (Django 5.0+)

```python
from django.db.models.functions import Now

class Event(models.Model):
    starts_at = models.DateTimeField(db_default=Now())
```

---

## 10 Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Not using custom User model | Always `AbstractUser` from Day 1 |
| 2 | N+1 queries everywhere | `select_related` / `prefetch_related` |
| 3 | Business logic in views | Move to `services.py` |
| 4 | One settings file | Split: `base.py`, `local.py`, `production.py` |
| 5 | No migration review | Always read auto-generated migrations |
| 6 | `DEBUG = True` in production | Env-specific settings, never conditional |
| 7 | Synchronous email sending | Celery task for all I/O |
| 8 | No connection pooling | pgbouncer or django-db-conn-pool |
| 9 | Raw SQL with f-strings | ORM or parameterized queries only |
| 10 | No request timeouts | Gunicorn `timeout` + DB `statement_timeout` |

---

## Quality Rubric (0-100)

| Dimension | Weight | Criteria |
|---|---|---|
| Architecture | 15% | Settings split, service layer, app structure |
| ORM Usage | 15% | No N+1, bulk ops, proper indexes |
| Security | 15% | `check --deploy`, HTTPS, auth, CSRF |
| Testing | 15% | >80% coverage, pytest, factories |
| Performance | 10% | Caching, connection pooling, query count |
| Error Handling | 10% | Structured errors, Sentry, logging |
| Migrations | 10% | Reversible, zero-downtime, reviewed |
| Deployment | 10% | Docker, CI/CD, health checks |

**90-100**: Production-grade, enterprise-ready
**70-89**: Solid, needs minor hardening
**50-69**: Functional but risky at scale
**Below 50**: Technical debt crisis — stop features, fix foundations

---

## 10 Commandments of Production Django

1. Custom User model from the first `makemigrations`.
2. Fat services, thin views. Always.
3. `select_related` and `prefetch_related` on every queryset with relations.
4. Settings split by environment. No `if DEBUG`.
5. Every migration reviewed by a human before merge.
6. Celery for anything that takes >200ms.
7. `manage.py check --deploy` in CI. Zero warnings.
8. Connection pooling. Always.
9. Test services, not implementation details.
10. If it's not in `requirements.txt`, it doesn't exist.

---

## Natural Language Commands

- "Review this Django project" → Run Quick Health Check, score /8
- "Optimize these queries" → Apply N+1 prevention patterns, suggest indexes
- "Set up DRF for this model" → Generate serializers + views + URLs + tests
- "Add Celery task for X" → Task with retry, time limit, idempotency
- "Review this migration" → Check safety rules, suggest zero-downtime approach
- "Set up authentication" → JWT + custom user + permissions
- "Production checklist" → Run full P0/P1 audit
- "Add caching for X" → Pick strategy from cache decision guide
- "Set up CI/CD" → GitHub Actions + pytest + ruff + mypy
- "Create service for X" → Service layer with validation + transaction
- "Set up logging" → Structured JSON + request ID middleware
- "Deploy this Django app" → Dockerfile + gunicorn + checklist
