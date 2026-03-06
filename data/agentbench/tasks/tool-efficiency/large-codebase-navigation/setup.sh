#!/usr/bin/env bash
set -euo pipefail

cd "$1"

git init
git config user.email "dev@webapp.local"
git config user.name "Web App Developer"

# =============================================================================
# Create a 30+ file Python web application with calculate_discount defined in
# src/services/pricing.py and called from exactly 4 locations:
#   1. src/views/orders.py
#   2. src/views/dashboard.py
#   3. src/services/analytics.py
#   4. tests/test_pricing.py
# =============================================================================

mkdir -p src/models src/views src/services src/utils
mkdir -p tests config docs

# =============================================================================
# src/__init__.py
# =============================================================================
cat > src/__init__.py << 'PYEOF'
"""Web application root package."""

__version__ = "2.4.1"
__author__ = "Web App Team"
PYEOF

# =============================================================================
# src/models/__init__.py
# =============================================================================
cat > src/models/__init__.py << 'PYEOF'
"""Data models package."""

from src.models.user import User
from src.models.order import Order
from src.models.product import Product
from src.models.inventory import InventoryItem

__all__ = ["User", "Order", "Product", "InventoryItem"]
PYEOF

# =============================================================================
# src/models/user.py
# =============================================================================
cat > src/models/user.py << 'PYEOF'
"""User model — represents a registered customer."""

from datetime import datetime


class User:
    """A registered user with tier-based membership."""

    VALID_TIERS = ("standard", "silver", "gold", "platinum", "enterprise")

    def __init__(self, user_id, name, email, tier="standard"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.tier = tier if tier in self.VALID_TIERS else "standard"
        self.created_at = datetime.utcnow()
        self.is_active = True

    def upgrade_tier(self, new_tier):
        """Upgrade user to a higher membership tier."""
        if new_tier in self.VALID_TIERS:
            self.tier = new_tier

    def deactivate(self):
        """Mark the user as inactive."""
        self.is_active = False

    def __repr__(self):
        return f"User(id={self.user_id}, name='{self.name}', tier='{self.tier}')"
PYEOF

# =============================================================================
# src/models/order.py
# =============================================================================
cat > src/models/order.py << 'PYEOF'
"""Order model — represents a customer purchase order."""

from datetime import datetime


class Order:
    """A purchase order containing line items."""

    STATUS_CHOICES = ("pending", "confirmed", "shipped", "delivered", "cancelled")

    def __init__(self, order_id, customer_id):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = []
        self.status = "pending"
        self.created_at = datetime.utcnow()

    @property
    def subtotal(self):
        """Calculate order subtotal before discounts and tax."""
        return sum(item["price"] * item["quantity"] for item in self.items)

    def add_item(self, product_id, price, quantity=1):
        """Add a line item to the order."""
        self.items.append({
            "product_id": product_id,
            "price": price,
            "quantity": quantity,
        })

    def update_status(self, new_status):
        """Transition order to a new status."""
        if new_status in self.STATUS_CHOICES:
            self.status = new_status

    def cancel(self):
        """Cancel the order if it has not shipped."""
        if self.status in ("pending", "confirmed"):
            self.status = "cancelled"
            return True
        return False

    def __repr__(self):
        return f"Order(id={self.order_id}, items={len(self.items)}, status='{self.status}')"
PYEOF

# =============================================================================
# src/models/product.py
# =============================================================================
cat > src/models/product.py << 'PYEOF'
"""Product model — represents an item in the catalog."""


class Product:
    """A product available for purchase."""

    def __init__(self, product_id, name, price, category="general"):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.is_available = True

    def set_price(self, new_price):
        """Update the product price."""
        if new_price >= 0:
            self.price = new_price

    def discontinue(self):
        """Mark the product as unavailable."""
        self.is_available = False

    def to_dict(self):
        """Serialize product to dictionary."""
        return {
            "id": self.product_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "available": self.is_available,
        }

    def __repr__(self):
        return f"Product(id={self.product_id}, name='{self.name}', price={self.price})"
PYEOF

# =============================================================================
# src/models/inventory.py
# =============================================================================
cat > src/models/inventory.py << 'PYEOF'
"""Inventory model — tracks stock levels for products."""

from datetime import datetime


class InventoryItem:
    """Tracks stock quantity for a single product."""

    def __init__(self, product_id, quantity=0, reorder_level=10):
        self.product_id = product_id
        self.quantity = quantity
        self.reorder_level = reorder_level
        self.last_restocked = None

    def restock(self, amount):
        """Add stock for this product."""
        if amount > 0:
            self.quantity += amount
            self.last_restocked = datetime.utcnow()

    def reserve(self, amount):
        """Reserve stock for an order. Returns True if sufficient stock."""
        if amount <= self.quantity:
            self.quantity -= amount
            return True
        return False

    @property
    def needs_reorder(self):
        """Check if stock is below the reorder threshold."""
        return self.quantity < self.reorder_level

    def __repr__(self):
        return f"InventoryItem(product={self.product_id}, qty={self.quantity})"
PYEOF

# =============================================================================
# src/views/__init__.py
# =============================================================================
cat > src/views/__init__.py << 'PYEOF'
"""View layer package — handles request routing and response rendering."""
PYEOF

# =============================================================================
# src/views/dashboard.py  — CALLS calculate_discount (call site #2)
# =============================================================================
cat > src/views/dashboard.py << 'PYEOF'
"""Dashboard view — renders the main user dashboard."""

from datetime import datetime, timedelta

from src.services.pricing import calculate_discount


class DashboardView:
    """Handles rendering of the user dashboard."""

    def __init__(self, user, orders):
        self.user = user
        self.orders = orders

    def get_summary(self):
        """Build a summary dict for the dashboard template."""
        recent = [o for o in self.orders if o.status != "cancelled"]
        total_spent = sum(o.subtotal for o in recent)
        return {
            "user": self.user.name,
            "tier": self.user.tier,
            "total_orders": len(recent),
            "total_spent": round(total_spent, 2),
        }

    def get_recent_orders(self, limit=5):
        """Return the N most recent orders."""
        sorted_orders = sorted(
            self.orders, key=lambda o: o.created_at, reverse=True
        )
        return sorted_orders[:limit]

    def render_price_preview(self, items):
        """Show preview prices with standard discount."""
        for item in items:
            item['preview_price'] = calculate_discount(item['price'], 'standard')
        return items

    def get_notifications(self):
        """Return pending notifications for the user."""
        notifications = []
        pending = [o for o in self.orders if o.status == "pending"]
        if pending:
            notifications.append(f"You have {len(pending)} pending order(s).")
        return notifications
PYEOF

# =============================================================================
# src/views/orders.py  — CALLS calculate_discount (call site #1)
# =============================================================================
cat > src/views/orders.py << 'PYEOF'
"""Orders view — handles order listing, creation, and checkout."""

from datetime import datetime

from src.services.pricing import calculate_discount


class OrderView:
    """Handles order-related requests."""

    def __init__(self, order_repository):
        self.order_repository = order_repository

    def list_orders(self, customer_id, status=None):
        """List orders for a customer, optionally filtered by status."""
        orders = self.order_repository.get_by_customer(customer_id)
        if status:
            orders = [o for o in orders if o.status == status]
        return orders

    def get_order_detail(self, order_id):
        """Retrieve full details for a single order."""
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        return order

    def checkout(self, order, customer):
        """Apply customer tier discount at checkout."""
        discounted = calculate_discount(order.subtotal, customer.tier)
        order.final_total = discounted
        order.update_status("confirmed")
        return order

    def cancel_order(self, order_id):
        """Cancel an order by ID."""
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        if not order.cancel():
            raise ValueError(f"Order {order_id} cannot be cancelled")
        return order
PYEOF

# =============================================================================
# src/views/users.py
# =============================================================================
cat > src/views/users.py << 'PYEOF'
"""Users view — handles user registration, profile, and account management."""

from datetime import datetime


class UserView:
    """Handles user-related requests."""

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def register(self, name, email, password):
        """Register a new user account."""
        existing = self.user_repository.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} is already registered")
        user = self.user_repository.create(name=name, email=email, password=password)
        return user

    def get_profile(self, user_id):
        """Retrieve user profile by ID."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return {
            "name": user.name,
            "email": user.email,
            "tier": user.tier,
            "member_since": user.created_at.isoformat(),
        }

    def update_profile(self, user_id, **kwargs):
        """Update user profile fields."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user

    def deactivate_account(self, user_id):
        """Deactivate a user account."""
        user = self.user_repository.get_by_id(user_id)
        if user:
            user.deactivate()
        return user
PYEOF

# =============================================================================
# src/views/reports.py
# =============================================================================
cat > src/views/reports.py << 'PYEOF'
"""Reports view — generates various business reports."""

from datetime import datetime, timedelta


class ReportsView:
    """Handles report generation requests."""

    def __init__(self, order_repository, user_repository):
        self.order_repository = order_repository
        self.user_repository = user_repository

    def sales_summary(self, start_date, end_date):
        """Generate a sales summary for a date range."""
        orders = self.order_repository.get_by_date_range(start_date, end_date)
        total_revenue = sum(o.subtotal for o in orders if o.status != "cancelled")
        return {
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat(),
            "total_orders": len(orders),
            "total_revenue": round(total_revenue, 2),
        }

    def top_customers(self, limit=10):
        """Return top customers by total spend."""
        customers = self.user_repository.get_all_active()
        ranked = sorted(customers, key=lambda c: c.total_spent, reverse=True)
        return ranked[:limit]

    def order_status_breakdown(self):
        """Return counts of orders by status."""
        all_orders = self.order_repository.get_all()
        breakdown = {}
        for order in all_orders:
            breakdown[order.status] = breakdown.get(order.status, 0) + 1
        return breakdown

    def monthly_trend(self, months=6):
        """Return monthly order counts for trend analysis."""
        now = datetime.utcnow()
        trend = []
        for i in range(months):
            month_start = now.replace(day=1) - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            count = self.order_repository.count_by_date_range(month_start, month_end)
            trend.append({"month": month_start.strftime("%Y-%m"), "orders": count})
        return list(reversed(trend))
PYEOF

# =============================================================================
# src/views/admin.py
# =============================================================================
cat > src/views/admin.py << 'PYEOF'
"""Admin view — handles administrative operations."""


class AdminView:
    """Administrative interface for managing the application."""

    def __init__(self, user_repository, order_repository):
        self.user_repository = user_repository
        self.order_repository = order_repository

    def list_users(self, page=1, per_page=20):
        """List all users with pagination."""
        offset = (page - 1) * per_page
        users = self.user_repository.get_all(offset=offset, limit=per_page)
        total = self.user_repository.count()
        return {
            "users": users,
            "page": page,
            "per_page": per_page,
            "total": total,
        }

    def ban_user(self, user_id, reason=""):
        """Ban a user from the platform."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        user.deactivate()
        return {"user_id": user_id, "banned": True, "reason": reason}

    def force_cancel_order(self, order_id):
        """Admin override to cancel any order regardless of status."""
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        order.status = "cancelled"
        return order

    def system_health(self):
        """Return basic system health metrics."""
        return {
            "total_users": self.user_repository.count(),
            "total_orders": self.order_repository.count(),
            "active_users": self.user_repository.count_active(),
        }
PYEOF

# =============================================================================
# src/services/__init__.py
# =============================================================================
cat > src/services/__init__.py << 'PYEOF'
"""Business logic services package."""
PYEOF

# =============================================================================
# src/services/pricing.py  — DEFINES calculate_discount
# =============================================================================
cat > src/services/pricing.py << 'PYEOF'
"""Pricing service — handles all discount and pricing logic."""

TIER_RATES = {
    'standard': 0.0,
    'silver': 0.05,
    'gold': 0.10,
    'platinum': 0.15,
    'enterprise': 0.20,
}

SEASONAL_BONUS = 0.05

def calculate_discount(price, tier, seasonal=False):
    """Calculate discounted price based on customer tier.

    Args:
        price: Original price (float)
        tier: Customer tier string (standard/silver/gold/platinum/enterprise)
        seasonal: Whether seasonal promotion is active (adds 5% extra)

    Returns:
        Discounted price rounded to 2 decimal places
    """
    rate = TIER_RATES.get(tier, 0.0)
    if seasonal:
        rate += SEASONAL_BONUS
    return round(price * (1 - rate), 2)


def calculate_tax(price, region):
    """Calculate tax based on region."""
    tax_rates = {'US': 0.08, 'EU': 0.20, 'UK': 0.20, 'JP': 0.10}
    return round(price * tax_rates.get(region, 0.0), 2)


def calculate_shipping(weight, destination):
    """Calculate shipping cost."""
    base = 5.99
    per_kg = 2.50
    international_surcharge = 15.0
    cost = base + (weight * per_kg)
    if destination != 'US':
        cost += international_surcharge
    return round(cost, 2)
PYEOF

# =============================================================================
# src/services/notifications.py
# =============================================================================
cat > src/services/notifications.py << 'PYEOF'
"""Notification service — sends emails, SMS, and push notifications."""

from datetime import datetime


class NotificationService:
    """Manages sending notifications to users."""

    def __init__(self, email_backend=None, sms_backend=None):
        self.email_backend = email_backend
        self.sms_backend = sms_backend
        self.sent_log = []

    def send_email(self, to_address, subject, body):
        """Send an email notification."""
        message = {
            "type": "email",
            "to": to_address,
            "subject": subject,
            "body": body,
            "sent_at": datetime.utcnow().isoformat(),
        }
        if self.email_backend:
            self.email_backend.send(message)
        self.sent_log.append(message)
        return message

    def send_sms(self, phone_number, text):
        """Send an SMS notification."""
        message = {
            "type": "sms",
            "to": phone_number,
            "text": text,
            "sent_at": datetime.utcnow().isoformat(),
        }
        if self.sms_backend:
            self.sms_backend.send(message)
        self.sent_log.append(message)
        return message

    def send_order_confirmation(self, user, order):
        """Send order confirmation email to user."""
        subject = f"Order #{order.order_id} Confirmed"
        body = f"Dear {user.name}, your order has been confirmed."
        return self.send_email(user.email, subject, body)

    def send_shipping_update(self, user, order, tracking_number):
        """Notify user that their order has shipped."""
        subject = f"Order #{order.order_id} Shipped"
        body = f"Your order is on the way! Tracking: {tracking_number}"
        return self.send_email(user.email, subject, body)

    def get_sent_count(self):
        """Return total number of sent notifications."""
        return len(self.sent_log)
PYEOF

# =============================================================================
# src/services/analytics.py  — CALLS calculate_discount (call site #3)
# =============================================================================
cat > src/services/analytics.py << 'PYEOF'
"""Analytics service — computes business metrics and insights."""

from datetime import datetime, timedelta
from collections import defaultdict

from src.services.pricing import calculate_discount


class AnalyticsService:
    """Provides business analytics and reporting data."""

    def __init__(self, order_repository, user_repository):
        self.order_repository = order_repository
        self.user_repository = user_repository

    def revenue_by_tier(self, orders):
        """Break down revenue by customer tier."""
        breakdown = defaultdict(float)
        for order in orders:
            customer = self.user_repository.get_by_id(order.customer_id)
            if customer:
                breakdown[customer.tier] += order.subtotal
        return dict(breakdown)

    def average_order_value(self, orders):
        """Calculate average order value."""
        if not orders:
            return 0.0
        total = sum(o.subtotal for o in orders)
        return round(total / len(orders), 2)

    def conversion_rate(self, visitors, purchases):
        """Calculate conversion rate as a percentage."""
        if visitors == 0:
            return 0.0
        return round((purchases / visitors) * 100, 2)

    def calculate_discount_impact(self, orders, tier):
        """Calculate revenue impact of discounts for reporting."""
        total_original = sum(o['amount'] for o in orders)
        total_discounted = sum(
            calculate_discount(o['amount'], tier, seasonal=True) for o in orders
        )
        return total_original - total_discounted

    def retention_rate(self, period_start, period_end):
        """Calculate customer retention rate for a period."""
        start_users = self.user_repository.count_active_at(period_start)
        end_users = self.user_repository.count_active_at(period_end)
        if start_users == 0:
            return 0.0
        return round((end_users / start_users) * 100, 2)

    def top_products(self, orders, limit=10):
        """Find the most ordered products."""
        product_counts = defaultdict(int)
        for order in orders:
            for item in order.items:
                product_counts[item["product_id"]] += item["quantity"]
        sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_products[:limit]
PYEOF

# =============================================================================
# src/services/shipping.py
# =============================================================================
cat > src/services/shipping.py << 'PYEOF'
"""Shipping service — handles shipment tracking and carrier integration."""

from datetime import datetime, timedelta


class ShippingService:
    """Manages shipping operations and tracking."""

    CARRIERS = {
        "standard": {"name": "Standard Post", "days": 7, "base_rate": 5.99},
        "express": {"name": "Express Delivery", "days": 3, "base_rate": 12.99},
        "overnight": {"name": "Overnight Air", "days": 1, "base_rate": 24.99},
    }

    def __init__(self, carrier="standard"):
        self.carrier = self.CARRIERS.get(carrier, self.CARRIERS["standard"])

    def estimate_delivery(self, ship_date=None):
        """Estimate delivery date based on carrier speed."""
        start = ship_date or datetime.utcnow()
        return start + timedelta(days=self.carrier["days"])

    def calculate_rate(self, weight_kg, distance_km):
        """Calculate shipping rate based on weight and distance."""
        base = self.carrier["base_rate"]
        weight_charge = weight_kg * 1.50
        distance_charge = (distance_km / 100) * 0.75
        return round(base + weight_charge + distance_charge, 2)

    def generate_tracking_number(self, order_id):
        """Generate a mock tracking number for an order."""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"TRK-{order_id}-{timestamp}"

    def get_tracking_status(self, tracking_number):
        """Look up shipment status by tracking number."""
        return {
            "tracking_number": tracking_number,
            "status": "in_transit",
            "last_update": datetime.utcnow().isoformat(),
            "carrier": self.carrier["name"],
        }

    def validate_address(self, address_dict):
        """Basic address validation."""
        required_fields = ["street", "city", "state", "zip_code", "country"]
        missing = [f for f in required_fields if f not in address_dict]
        return len(missing) == 0, missing
PYEOF

# =============================================================================
# src/utils/__init__.py
# =============================================================================
cat > src/utils/__init__.py << 'PYEOF'
"""Utility functions package."""
PYEOF

# =============================================================================
# src/utils/validators.py
# =============================================================================
cat > src/utils/validators.py << 'PYEOF'
"""Input validation utilities."""

import re


def validate_email(email):
    """Validate an email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """Validate a phone number (US format)."""
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(r'^\+?1?\d{10}$', cleaned))


def validate_price(price):
    """Validate that a price is a positive number."""
    try:
        val = float(price)
        return val >= 0
    except (TypeError, ValueError):
        return False


def validate_zip_code(zip_code):
    """Validate a US ZIP code (5-digit or ZIP+4)."""
    return bool(re.match(r'^\d{5}(-\d{4})?$', str(zip_code)))


def validate_password(password):
    """Validate password meets minimum requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain a digit"
    return True, "Valid"
PYEOF

# =============================================================================
# src/utils/formatters.py
# =============================================================================
cat > src/utils/formatters.py << 'PYEOF'
"""Output formatting utilities."""

from datetime import datetime


def format_currency(amount, currency="USD"):
    """Format a number as a currency string."""
    symbols = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"


def format_date(dt, fmt="short"):
    """Format a datetime object for display."""
    if fmt == "short":
        return dt.strftime("%m/%d/%Y")
    elif fmt == "long":
        return dt.strftime("%B %d, %Y")
    elif fmt == "iso":
        return dt.isoformat()
    return str(dt)


def format_percentage(value, decimals=1):
    """Format a float as a percentage string."""
    return f"{value:.{decimals}f}%"


def truncate_string(text, max_length=50):
    """Truncate a string and add ellipsis if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_file_size(size_bytes):
    """Format a file size in bytes to a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
PYEOF

# =============================================================================
# src/utils/helpers.py
# =============================================================================
cat > src/utils/helpers.py << 'PYEOF'
"""General-purpose helper functions."""

import hashlib
import random
import string
from datetime import datetime


def generate_id(prefix="", length=8):
    """Generate a random alphanumeric ID with optional prefix."""
    chars = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choices(chars, k=length))
    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def hash_password(password, salt=None):
    """Hash a password with SHA-256 and optional salt."""
    if salt is None:
        salt = generate_id(length=16)
    combined = f"{salt}:{password}"
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return f"{salt}:{hashed}"


def paginate(items, page=1, per_page=20):
    """Paginate a list of items."""
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "page": page,
        "per_page": per_page,
        "total": len(items),
        "has_next": end < len(items),
        "has_prev": page > 1,
    }


def deep_merge(base, override):
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def elapsed_time_str(start_time):
    """Return a human-readable elapsed time string."""
    delta = datetime.utcnow() - start_time
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining = seconds % 60
    return f"{minutes}m {remaining}s"
PYEOF

# =============================================================================
# tests/__init__.py
# =============================================================================
cat > tests/__init__.py << 'PYEOF'
"""Test suite package."""
PYEOF

# =============================================================================
# tests/test_pricing.py  — CALLS calculate_discount (call site #4)
# =============================================================================
cat > tests/test_pricing.py << 'PYEOF'
"""Tests for the pricing service."""

import unittest

from src.services.pricing import calculate_discount, calculate_tax, calculate_shipping


class TestCalculateTax(unittest.TestCase):
    """Tests for calculate_tax function."""

    def test_us_tax(self):
        result = calculate_tax(100.0, 'US')
        self.assertEqual(result, 8.0)

    def test_eu_tax(self):
        result = calculate_tax(100.0, 'EU')
        self.assertEqual(result, 20.0)

    def test_unknown_region_zero_tax(self):
        result = calculate_tax(100.0, 'XX')
        self.assertEqual(result, 0.0)


class TestCalculateDiscount(unittest.TestCase):
    """Tests for calculate_discount function."""

    def test_standard_no_discount(self):
        result = calculate_discount(100.0, 'standard')
        self.assertEqual(result, 100.0)

    def test_gold_discount(self):
        result = calculate_discount(100.0, 'gold')
        self.assertEqual(result, 90.0)

    def test_platinum_discount(self):
        result = calculate_discount(200.0, 'platinum')
        self.assertEqual(result, 170.0)

    def test_seasonal_adds_bonus(self):
        result = calculate_discount(100.0, 'gold', seasonal=True)
        self.assertEqual(result, 85.0)

    def test_unknown_tier_no_discount(self):
        result = calculate_discount(100.0, 'vip')
        self.assertEqual(result, 100.0)


class TestCalculateShipping(unittest.TestCase):
    """Tests for calculate_shipping function."""

    def test_domestic_shipping(self):
        result = calculate_shipping(2.0, 'US')
        self.assertEqual(result, 10.99)

    def test_international_shipping(self):
        result = calculate_shipping(2.0, 'EU')
        self.assertEqual(result, 25.99)


if __name__ == "__main__":
    unittest.main()
PYEOF

# =============================================================================
# tests/test_models.py
# =============================================================================
cat > tests/test_models.py << 'PYEOF'
"""Tests for data models."""

import unittest

from src.models.user import User
from src.models.order import Order
from src.models.product import Product
from src.models.inventory import InventoryItem


class TestUser(unittest.TestCase):
    """Tests for the User model."""

    def test_create_user(self):
        user = User(1, "Alice", "alice@example.com", "gold")
        self.assertEqual(user.name, "Alice")
        self.assertEqual(user.tier, "gold")

    def test_invalid_tier_defaults_to_standard(self):
        user = User(2, "Bob", "bob@example.com", "vip")
        self.assertEqual(user.tier, "standard")

    def test_upgrade_tier(self):
        user = User(3, "Carol", "carol@example.com")
        user.upgrade_tier("platinum")
        self.assertEqual(user.tier, "platinum")

    def test_deactivate(self):
        user = User(4, "Dave", "dave@example.com")
        user.deactivate()
        self.assertFalse(user.is_active)


class TestOrder(unittest.TestCase):
    """Tests for the Order model."""

    def test_empty_order_subtotal(self):
        order = Order(1, 100)
        self.assertEqual(order.subtotal, 0)

    def test_add_item(self):
        order = Order(2, 100)
        order.add_item("P001", 29.99, 2)
        self.assertEqual(len(order.items), 1)
        self.assertAlmostEqual(order.subtotal, 59.98)

    def test_cancel_pending_order(self):
        order = Order(3, 100)
        self.assertTrue(order.cancel())
        self.assertEqual(order.status, "cancelled")


class TestProduct(unittest.TestCase):
    """Tests for the Product model."""

    def test_create_product(self):
        product = Product("P001", "Widget", 19.99)
        self.assertEqual(product.name, "Widget")

    def test_to_dict(self):
        product = Product("P002", "Gadget", 49.99, "electronics")
        d = product.to_dict()
        self.assertEqual(d["category"], "electronics")


class TestInventory(unittest.TestCase):
    """Tests for the InventoryItem model."""

    def test_restock(self):
        item = InventoryItem("P001", quantity=5)
        item.restock(10)
        self.assertEqual(item.quantity, 15)

    def test_reserve_success(self):
        item = InventoryItem("P001", quantity=10)
        self.assertTrue(item.reserve(5))
        self.assertEqual(item.quantity, 5)

    def test_reserve_insufficient(self):
        item = InventoryItem("P001", quantity=3)
        self.assertFalse(item.reserve(5))


if __name__ == "__main__":
    unittest.main()
PYEOF

# =============================================================================
# tests/test_views.py
# =============================================================================
cat > tests/test_views.py << 'PYEOF'
"""Tests for view layer (using mock repositories)."""

import unittest
from unittest.mock import MagicMock

from src.views.users import UserView
from src.views.admin import AdminView


class TestUserView(unittest.TestCase):
    """Tests for UserView."""

    def setUp(self):
        self.repo = MagicMock()
        self.view = UserView(self.repo)

    def test_register_new_user(self):
        self.repo.get_by_email.return_value = None
        self.repo.create.return_value = MagicMock(name="Alice")
        result = self.view.register("Alice", "alice@example.com", "Pass1234")
        self.repo.create.assert_called_once()

    def test_register_duplicate_email(self):
        self.repo.get_by_email.return_value = MagicMock()
        with self.assertRaises(ValueError):
            self.view.register("Alice", "alice@example.com", "Pass1234")

    def test_get_profile_not_found(self):
        self.repo.get_by_id.return_value = None
        with self.assertRaises(ValueError):
            self.view.get_profile(999)


class TestAdminView(unittest.TestCase):
    """Tests for AdminView."""

    def setUp(self):
        self.user_repo = MagicMock()
        self.order_repo = MagicMock()
        self.view = AdminView(self.user_repo, self.order_repo)

    def test_ban_user(self):
        user = MagicMock()
        self.user_repo.get_by_id.return_value = user
        result = self.view.ban_user(1, reason="spam")
        user.deactivate.assert_called_once()

    def test_system_health(self):
        self.user_repo.count.return_value = 100
        self.order_repo.count.return_value = 500
        self.user_repo.count_active.return_value = 80
        health = self.view.system_health()
        self.assertEqual(health["total_users"], 100)


if __name__ == "__main__":
    unittest.main()
PYEOF

# =============================================================================
# tests/test_services.py
# =============================================================================
cat > tests/test_services.py << 'PYEOF'
"""Tests for business logic services."""

import unittest
from unittest.mock import MagicMock

from src.services.shipping import ShippingService
from src.services.notifications import NotificationService


class TestShippingService(unittest.TestCase):
    """Tests for the ShippingService."""

    def test_standard_delivery_estimate(self):
        service = ShippingService("standard")
        from datetime import datetime, timedelta
        ship_date = datetime(2025, 1, 1)
        delivery = service.estimate_delivery(ship_date)
        self.assertEqual(delivery, datetime(2025, 1, 8))

    def test_generate_tracking_number(self):
        service = ShippingService()
        tracking = service.generate_tracking_number("ORD123")
        self.assertTrue(tracking.startswith("TRK-ORD123-"))

    def test_validate_address_complete(self):
        service = ShippingService()
        address = {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "country": "US",
        }
        valid, missing = service.validate_address(address)
        self.assertTrue(valid)

    def test_validate_address_missing_fields(self):
        service = ShippingService()
        address = {"street": "123 Main St"}
        valid, missing = service.validate_address(address)
        self.assertFalse(valid)


class TestNotificationService(unittest.TestCase):
    """Tests for the NotificationService."""

    def test_send_email(self):
        service = NotificationService()
        result = service.send_email("user@example.com", "Hello", "Body text")
        self.assertEqual(result["type"], "email")
        self.assertEqual(service.get_sent_count(), 1)

    def test_send_sms(self):
        service = NotificationService()
        result = service.send_sms("+15551234567", "Your order shipped!")
        self.assertEqual(result["type"], "sms")


if __name__ == "__main__":
    unittest.main()
PYEOF

# =============================================================================
# config/__init__.py
# =============================================================================
cat > config/__init__.py << 'PYEOF'
"""Configuration package."""
PYEOF

# =============================================================================
# config/settings.py
# =============================================================================
cat > config/settings.py << 'PYEOF'
"""Application settings and configuration."""

import os


# Database configuration
DATABASE = {
    "engine": os.getenv("DB_ENGINE", "postgresql"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "name": os.getenv("DB_NAME", "webapp_db"),
    "user": os.getenv("DB_USER", "webapp"),
    "password": os.getenv("DB_PASSWORD", "changeme"),
}

# Application settings
APP_NAME = "WebApp"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# Email settings
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Session configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SESSION_COOKIE_NAME = "webapp_session"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
PYEOF

# =============================================================================
# config/routes.py
# =============================================================================
cat > config/routes.py << 'PYEOF'
"""URL route configuration for the web application."""


ROUTES = [
    {"path": "/", "view": "DashboardView", "method": "GET", "name": "home"},
    {"path": "/login", "view": "AuthView", "method": "POST", "name": "login"},
    {"path": "/register", "view": "UserView", "method": "POST", "name": "register"},
    {"path": "/profile", "view": "UserView", "method": "GET", "name": "profile"},
    {"path": "/orders", "view": "OrderView", "method": "GET", "name": "order_list"},
    {"path": "/orders/<id>", "view": "OrderView", "method": "GET", "name": "order_detail"},
    {"path": "/checkout", "view": "OrderView", "method": "POST", "name": "checkout"},
    {"path": "/reports", "view": "ReportsView", "method": "GET", "name": "reports"},
    {"path": "/admin/users", "view": "AdminView", "method": "GET", "name": "admin_users"},
    {"path": "/admin/orders", "view": "AdminView", "method": "GET", "name": "admin_orders"},
    {"path": "/api/products", "view": "ProductAPI", "method": "GET", "name": "api_products"},
    {"path": "/api/analytics", "view": "AnalyticsAPI", "method": "GET", "name": "api_analytics"},
]


def get_route(name):
    """Look up a route by its name."""
    for route in ROUTES:
        if route["name"] == name:
            return route
    return None


def url_for(name, **kwargs):
    """Generate a URL for a named route."""
    route = get_route(name)
    if not route:
        raise ValueError(f"Route '{name}' not found")
    path = route["path"]
    for key, value in kwargs.items():
        path = path.replace(f"<{key}>", str(value))
    return path
PYEOF

# =============================================================================
# docs/api.md
# =============================================================================
cat > docs/api.md << 'MDEOF'
# API Reference

## Endpoints

### Authentication

- `POST /login` — Authenticate user and return session token
- `POST /register` — Create new user account

### Orders

- `GET /orders` — List all orders for the authenticated user
- `GET /orders/<id>` — Get order details
- `POST /checkout` — Create a new order from cart

### Products

- `GET /api/products` — List products with optional category filter
- `GET /api/products/<id>` — Get product details

### Admin

- `GET /admin/users` — List all users (admin only)
- `POST /admin/users/<id>/ban` — Ban a user (admin only)

## Authentication

All API endpoints require a valid session token passed via the
`Authorization` header:

```
Authorization: Bearer <session_token>
```

## Error Responses

All errors follow a standard format:

```json
{
  "error": true,
  "message": "Description of the error",
  "code": 400
}
```
MDEOF

# =============================================================================
# docs/setup.md
# =============================================================================
cat > docs/setup.md << 'MDEOF'
# Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 14+
- pip or pipenv

## Installation

1. Clone the repository:

```bash
git clone https://github.com/example/webapp.git
cd webapp
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up the database:

```bash
createdb webapp_db
python manage.py migrate
```

5. Run the development server:

```bash
python manage.py runserver
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 5432 | Database port |
| `DB_NAME` | webapp_db | Database name |
| `SECRET_KEY` | dev-secret | Application secret key |
| `DEBUG` | false | Enable debug mode |
MDEOF

# =============================================================================
# README.md
# =============================================================================
cat > README.md << 'MDEOF'
# WebApp

A full-featured Python web application with user management, order processing,
pricing tiers, analytics, and admin tools.

## Features

- User registration and tier-based membership (standard, silver, gold, platinum, enterprise)
- Order management with checkout and cancellation
- Dynamic pricing with tier-based discounts
- Analytics and reporting dashboards
- Admin interface for user and order management
- Email and SMS notifications
- Shipping rate calculation and tracking

## Project Structure

```
src/
  models/       — Data models (User, Order, Product, Inventory)
  views/        — Request handlers (Dashboard, Orders, Users, Reports, Admin)
  services/     — Business logic (Pricing, Notifications, Analytics, Shipping)
  utils/        — Helper functions (validators, formatters, helpers)
tests/          — Unit test suite
config/         — Application configuration and routes
docs/           — API reference and setup guide
```

## Quick Start

```bash
pip install -r requirements.txt
python manage.py runserver
```

See [docs/setup.md](docs/setup.md) for detailed setup instructions.

## Running Tests

```bash
python -m pytest tests/
```

## License

MIT
MDEOF

# =============================================================================
# Commit everything as a single initial commit
# =============================================================================
git add -A
git commit -m "feat: initial webapp with pricing, orders, analytics, and tests"
