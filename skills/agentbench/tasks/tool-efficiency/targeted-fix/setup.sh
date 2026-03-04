#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"

cd "$WORKSPACE"
git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── Directory structure ──────────────────────────────────────────────────────
mkdir -p src/models src/views src/services src/utils tests config

# ── src/models/__init__.py ───────────────────────────────────────────────────
cat > src/models/__init__.py << 'EOF'
"""Data models for the financial dashboard application."""
from .user import User
from .transaction import Transaction as TransactionModel
from .account import Account

__all__ = ["User", "TransactionModel", "Account"]
EOF

# ── src/models/user.py ───────────────────────────────────────────────────────
cat > src/models/user.py << 'EOF'
"""User model for authentication and profile management."""
from datetime import datetime
import hashlib


class User:
    """Represents an application user."""

    def __init__(self, user_id, username, email, created_at=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.now()
        self.is_active = True
        self.preferences = {}

    def set_preference(self, key, value):
        """Set a user preference."""
        self.preferences[key] = value

    def get_preference(self, key, default=None):
        """Get a user preference with optional default."""
        return self.preferences.get(key, default)

    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False

    def get_gravatar_url(self, size=80):
        """Generate Gravatar URL from email."""
        email_hash = hashlib.md5(self.email.lower().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?s={size}"

    def __repr__(self):
        status = "active" if self.is_active else "inactive"
        return f"User({self.user_id}, {self.username}, {status})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id

    def to_dict(self):
        """Serialize user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "preferences": self.preferences,
        }
EOF

# ── src/models/transaction.py ────────────────────────────────────────────────
cat > src/models/transaction.py << 'EOF'
"""Transaction model for financial records."""
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"
    REFUND = "refund"


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Transaction:
    """Represents a financial transaction linked to an account."""

    def __init__(self, txn_id, account_id, amount, txn_type, description="",
                 status=TransactionStatus.PENDING, created_at=None):
        self.txn_id = txn_id
        self.account_id = account_id
        self.amount = amount
        self.txn_type = txn_type if isinstance(txn_type, TransactionType) else TransactionType(txn_type)
        self.description = description
        self.status = status if isinstance(status, TransactionStatus) else TransactionStatus(status)
        self.created_at = created_at or datetime.now()
        self.metadata = {}

    def complete(self):
        """Mark transaction as completed."""
        if self.status == TransactionStatus.PENDING:
            self.status = TransactionStatus.COMPLETED
            return True
        return False

    def cancel(self):
        """Cancel a pending transaction."""
        if self.status == TransactionStatus.PENDING:
            self.status = TransactionStatus.CANCELLED
            return True
        return False

    def add_metadata(self, key, value):
        """Attach metadata to the transaction."""
        self.metadata[key] = value

    def is_debit(self):
        """Check if this is a debit transaction."""
        return self.txn_type == TransactionType.DEBIT

    def __repr__(self):
        return (f"Transaction({self.txn_id}, {self.txn_type.value}, "
                f"${self.amount:.2f}, {self.status.value})")

    def to_dict(self):
        """Serialize to dictionary."""
        return {
            "txn_id": self.txn_id,
            "account_id": self.account_id,
            "amount": self.amount,
            "type": self.txn_type.value,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
EOF

# ── src/models/account.py ────────────────────────────────────────────────────
cat > src/models/account.py << 'EOF'
"""Account model for managing user financial accounts."""
from datetime import datetime


class Account:
    """Represents a financial account belonging to a user."""

    def __init__(self, account_id, user_id, name, balance=0.0, currency="USD"):
        self.account_id = account_id
        self.user_id = user_id
        self.name = name
        self.balance = balance
        self.currency = currency
        self.created_at = datetime.now()
        self.is_frozen = False

    def deposit(self, amount):
        """Add funds to the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        if self.is_frozen:
            raise RuntimeError("Cannot deposit to a frozen account")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        """Remove funds from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.is_frozen:
            raise RuntimeError("Cannot withdraw from a frozen account")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance

    def freeze(self):
        """Freeze the account to prevent transactions."""
        self.is_frozen = True

    def unfreeze(self):
        """Unfreeze the account."""
        self.is_frozen = False

    def __repr__(self):
        status = "FROZEN" if self.is_frozen else "active"
        return f"Account({self.account_id}, {self.name}, ${self.balance:.2f} {self.currency}, {status})"

    def to_dict(self):
        """Serialize to dictionary."""
        return {
            "account_id": self.account_id,
            "user_id": self.user_id,
            "name": self.name,
            "balance": self.balance,
            "currency": self.currency,
            "is_frozen": self.is_frozen,
            "created_at": self.created_at.isoformat(),
        }
EOF

# ── src/views/__init__.py ────────────────────────────────────────────────────
cat > src/views/__init__.py << 'EOF'
"""View layer — handles request/response formatting and presentation logic."""
EOF

# ── src/views/dashboard.py (HAS THE BUG) ────────────────────────────────────
cat > src/views/dashboard.py << 'EOF'
"""Dashboard view — displays user's recent activity."""
from datetime import datetime


class Transaction:
    """Simple transaction data class."""
    def __init__(self, id, description, amount, date):
        self.id = id
        self.description = description
        self.amount = amount
        self.date = datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date

    def __repr__(self):
        return f"Transaction({self.id}, {self.date.strftime('%Y-%m-%d')}, ${self.amount})"


def get_recent_transactions(transactions, limit=10):
    """Get the most recent transactions, sorted newest first.

    Args:
        transactions: List of Transaction objects
        limit: Maximum number to return

    Returns:
        List of Transaction objects sorted by date, newest first
    """
    # BUG: Missing reverse=True — sorts oldest first instead of newest first
    sorted_transactions = sorted(transactions, key=lambda t: t.date)
    return sorted_transactions[:limit]


def get_dashboard_summary(transactions):
    """Generate dashboard summary stats."""
    if not transactions:
        return {"total": 0, "count": 0, "average": 0}
    total = sum(t.amount for t in transactions)
    return {
        "total": round(total, 2),
        "count": len(transactions),
        "average": round(total / len(transactions), 2)
    }
EOF

# ── src/views/profile.py ────────────────────────────────────────────────────
cat > src/views/profile.py << 'EOF'
"""Profile view — handles user profile display and editing."""


def get_profile_data(user):
    """Prepare profile data for rendering.

    Args:
        user: User model instance

    Returns:
        Dictionary with formatted profile fields
    """
    return {
        "display_name": user.username,
        "email": user.email,
        "member_since": user.created_at.strftime("%B %Y"),
        "avatar_url": user.get_gravatar_url(size=120),
        "is_active": user.is_active,
        "preferences": user.preferences,
    }


def update_profile(user, updates):
    """Apply profile updates from form submission.

    Args:
        user: User model instance
        updates: Dictionary of field updates

    Returns:
        List of fields that were changed
    """
    changed = []
    if "email" in updates and updates["email"] != user.email:
        user.email = updates["email"]
        changed.append("email")
    if "username" in updates and updates["username"] != user.username:
        user.username = updates["username"]
        changed.append("username")
    if "preferences" in updates:
        for key, value in updates["preferences"].items():
            user.set_preference(key, value)
        changed.append("preferences")
    return changed
EOF

# ── src/views/settings.py ───────────────────────────────────────────────────
cat > src/views/settings.py << 'EOF'
"""Settings view — application and account settings management."""


NOTIFICATION_CHANNELS = ["email", "sms", "push", "in_app"]
THEME_OPTIONS = ["light", "dark", "auto"]
TIMEZONE_PRESETS = ["UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London"]


def get_settings(user):
    """Retrieve current settings for a user.

    Args:
        user: User model instance

    Returns:
        Dictionary of current settings with defaults applied
    """
    return {
        "theme": user.get_preference("theme", "light"),
        "timezone": user.get_preference("timezone", "UTC"),
        "notifications": {
            "enabled": user.get_preference("notifications_enabled", True),
            "channels": user.get_preference("notification_channels", ["email"]),
            "frequency": user.get_preference("notification_frequency", "daily"),
        },
        "currency_display": user.get_preference("currency_display", "USD"),
        "date_format": user.get_preference("date_format", "YYYY-MM-DD"),
        "page_size": user.get_preference("page_size", 25),
    }


def validate_settings(settings):
    """Validate settings before applying.

    Args:
        settings: Dictionary of proposed settings

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if "theme" in settings and settings["theme"] not in THEME_OPTIONS:
        errors.append(f"Invalid theme. Must be one of: {', '.join(THEME_OPTIONS)}")

    if "timezone" in settings and settings["timezone"] not in TIMEZONE_PRESETS:
        errors.append(f"Invalid timezone. Must be one of: {', '.join(TIMEZONE_PRESETS)}")

    if "notifications" in settings:
        notif = settings["notifications"]
        if "channels" in notif:
            invalid = [ch for ch in notif["channels"] if ch not in NOTIFICATION_CHANNELS]
            if invalid:
                errors.append(f"Invalid notification channels: {', '.join(invalid)}")

    if "page_size" in settings:
        ps = settings["page_size"]
        if not isinstance(ps, int) or ps < 5 or ps > 100:
            errors.append("page_size must be an integer between 5 and 100")

    return (len(errors) == 0, errors)


def apply_settings(user, settings):
    """Apply validated settings to user preferences.

    Args:
        user: User model instance
        settings: Validated settings dictionary
    """
    if "theme" in settings:
        user.set_preference("theme", settings["theme"])
    if "timezone" in settings:
        user.set_preference("timezone", settings["timezone"])
    if "notifications" in settings:
        notif = settings["notifications"]
        if "enabled" in notif:
            user.set_preference("notifications_enabled", notif["enabled"])
        if "channels" in notif:
            user.set_preference("notification_channels", notif["channels"])
        if "frequency" in notif:
            user.set_preference("notification_frequency", notif["frequency"])
    if "currency_display" in settings:
        user.set_preference("currency_display", settings["currency_display"])
    if "date_format" in settings:
        user.set_preference("date_format", settings["date_format"])
    if "page_size" in settings:
        user.set_preference("page_size", settings["page_size"])
EOF

# ── src/views/transactions.py ────────────────────────────────────────────────
cat > src/views/transactions.py << 'EOF'
"""Transactions list view — paginated transaction history."""
import math


def paginate_transactions(transactions, page=1, per_page=20):
    """Paginate a list of transactions.

    Args:
        transactions: Full list of transaction objects
        page: Current page number (1-indexed)
        per_page: Items per page

    Returns:
        Dictionary with paginated results and metadata
    """
    total = len(transactions)
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    page = max(1, min(page, total_pages))

    start = (page - 1) * per_page
    end = start + per_page

    return {
        "items": transactions[start:end],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }


def filter_transactions(transactions, filters):
    """Apply filters to transaction list.

    Args:
        transactions: List of transaction objects
        filters: Dictionary of filter criteria

    Returns:
        Filtered list of transactions
    """
    result = list(transactions)

    if "min_amount" in filters:
        result = [t for t in result if t.amount >= filters["min_amount"]]
    if "max_amount" in filters:
        result = [t for t in result if t.amount <= filters["max_amount"]]
    if "type" in filters:
        result = [t for t in result if t.txn_type.value == filters["type"]]
    if "status" in filters:
        result = [t for t in result if t.status.value == filters["status"]]
    if "description_contains" in filters:
        keyword = filters["description_contains"].lower()
        result = [t for t in result if keyword in t.description.lower()]

    return result


def format_transaction_row(transaction):
    """Format a transaction for display in a table row.

    Args:
        transaction: Transaction model instance

    Returns:
        Dictionary of formatted display values
    """
    return {
        "id": transaction.txn_id,
        "date": transaction.created_at.strftime("%Y-%m-%d %H:%M"),
        "description": transaction.description or "No description",
        "amount": f"${transaction.amount:,.2f}",
        "type": transaction.txn_type.value.capitalize(),
        "status": transaction.status.value.capitalize(),
        "status_class": _status_css_class(transaction.status.value),
    }


def _status_css_class(status):
    """Map transaction status to CSS class name."""
    mapping = {
        "completed": "badge-success",
        "pending": "badge-warning",
        "failed": "badge-danger",
        "cancelled": "badge-secondary",
    }
    return mapping.get(status, "badge-default")
EOF

# ── src/services/__init__.py ─────────────────────────────────────────────────
cat > src/services/__init__.py << 'EOF'
"""Service layer — business logic and external integrations."""
EOF

# ── src/services/auth.py ─────────────────────────────────────────────────────
cat > src/services/auth.py << 'EOF'
"""Authentication service — handles login, logout, and session management."""
import hashlib
import secrets
from datetime import datetime, timedelta


# In-memory store for demo purposes
_sessions = {}
_users_db = {
    "alice": {"password_hash": hashlib.sha256(b"password123").hexdigest(), "role": "admin"},
    "bob": {"password_hash": hashlib.sha256(b"letmein").hexdigest(), "role": "user"},
    "charlie": {"password_hash": hashlib.sha256(b"s3cure!").hexdigest(), "role": "user"},
}

SESSION_TTL_HOURS = 24


def authenticate(username, password):
    """Authenticate a user with username and password.

    Args:
        username: The username
        password: The plaintext password

    Returns:
        Session token string if successful, None otherwise
    """
    user_record = _users_db.get(username)
    if not user_record:
        return None

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user_record["password_hash"]:
        return None

    token = secrets.token_hex(32)
    _sessions[token] = {
        "username": username,
        "role": user_record["role"],
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=SESSION_TTL_HOURS),
    }
    return token


def validate_session(token):
    """Check if a session token is valid and not expired.

    Args:
        token: Session token string

    Returns:
        Session data dictionary if valid, None otherwise
    """
    session = _sessions.get(token)
    if not session:
        return None
    if datetime.now() > session["expires_at"]:
        del _sessions[token]
        return None
    return session


def logout(token):
    """Invalidate a session token.

    Args:
        token: Session token to invalidate

    Returns:
        True if session was found and removed, False otherwise
    """
    if token in _sessions:
        del _sessions[token]
        return True
    return False


def get_active_sessions():
    """Return count of currently active sessions."""
    now = datetime.now()
    active = {k: v for k, v in _sessions.items() if now <= v["expires_at"]}
    return len(active)
EOF

# ── src/services/email.py ────────────────────────────────────────────────────
cat > src/services/email.py << 'EOF'
"""Email service — sends transactional emails."""
from datetime import datetime


class EmailService:
    """Handles composing and sending emails.

    In production this would integrate with an SMTP server or API
    like SendGrid. For the demo it just logs messages.
    """

    def __init__(self, from_address="noreply@financeapp.example.com"):
        self.from_address = from_address
        self.sent_log = []

    def send_welcome(self, user):
        """Send a welcome email to a new user."""
        subject = f"Welcome to FinanceApp, {user.username}!"
        body = (
            f"Hi {user.username},\n\n"
            f"Your account has been created successfully.\n"
            f"You can start tracking your finances right away.\n\n"
            f"Best regards,\nThe FinanceApp Team"
        )
        return self._send(user.email, subject, body)

    def send_transaction_receipt(self, user, transaction):
        """Send a receipt for a completed transaction."""
        subject = f"Transaction Receipt - ${transaction.amount:.2f}"
        body = (
            f"Hi {user.username},\n\n"
            f"Your transaction has been processed:\n"
            f"  Amount: ${transaction.amount:.2f}\n"
            f"  Type: {transaction.txn_type.value}\n"
            f"  Description: {transaction.description}\n"
            f"  Date: {transaction.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Thank you for using FinanceApp."
        )
        return self._send(user.email, subject, body)

    def send_password_reset(self, email, reset_token):
        """Send a password reset email."""
        subject = "Password Reset Request"
        body = (
            f"A password reset was requested for your account.\n\n"
            f"Use this token to reset your password: {reset_token}\n\n"
            f"If you didn't request this, please ignore this email."
        )
        return self._send(email, subject, body)

    def _send(self, to_address, subject, body):
        """Internal send method. Logs the email for demo purposes."""
        record = {
            "from": self.from_address,
            "to": to_address,
            "subject": subject,
            "body": body,
            "sent_at": datetime.now().isoformat(),
        }
        self.sent_log.append(record)
        return True

    def get_sent_count(self):
        """Return number of emails sent."""
        return len(self.sent_log)
EOF

# ── src/services/reporting.py ────────────────────────────────────────────────
cat > src/services/reporting.py << 'EOF'
"""Reporting service — generates financial reports and summaries."""
from datetime import datetime, timedelta
from collections import defaultdict


def generate_monthly_report(transactions, year, month):
    """Generate a monthly financial summary.

    Args:
        transactions: List of Transaction model instances
        year: Report year
        month: Report month (1-12)

    Returns:
        Dictionary with monthly totals and breakdowns
    """
    monthly = [
        t for t in transactions
        if t.created_at.year == year and t.created_at.month == month
    ]

    totals_by_type = defaultdict(float)
    for t in monthly:
        totals_by_type[t.txn_type.value] += t.amount

    total_in = totals_by_type.get("credit", 0) + totals_by_type.get("refund", 0)
    total_out = totals_by_type.get("debit", 0) + totals_by_type.get("transfer", 0)

    return {
        "year": year,
        "month": month,
        "transaction_count": len(monthly),
        "total_in": round(total_in, 2),
        "total_out": round(total_out, 2),
        "net": round(total_in - total_out, 2),
        "by_type": dict(totals_by_type),
    }


def generate_spending_categories(transactions):
    """Group spending by description keywords.

    Args:
        transactions: List of Transaction model instances

    Returns:
        Dictionary mapping category keywords to total amounts
    """
    categories = defaultdict(float)
    for t in transactions:
        if t.is_debit():
            keyword = t.description.split()[0].lower() if t.description else "uncategorized"
            categories[keyword] += t.amount
    return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))


def generate_weekly_trend(transactions, weeks=4):
    """Calculate weekly spending trend.

    Args:
        transactions: List of Transaction model instances
        weeks: Number of weeks to include

    Returns:
        List of dictionaries with weekly totals
    """
    now = datetime.now()
    trend = []
    for i in range(weeks):
        week_end = now - timedelta(weeks=i)
        week_start = week_end - timedelta(weeks=1)
        weekly = [
            t for t in transactions
            if week_start <= t.created_at <= week_end and t.is_debit()
        ]
        trend.append({
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total": round(sum(t.amount for t in weekly), 2),
            "count": len(weekly),
        })
    return trend
EOF

# ── src/utils/__init__.py ────────────────────────────────────────────────────
cat > src/utils/__init__.py << 'EOF'
"""Utility functions — formatters, validators, and common helpers."""
EOF

# ── src/utils/formatters.py ──────────────────────────────────────────────────
cat > src/utils/formatters.py << 'EOF'
"""Formatting utilities for display values."""
from datetime import datetime


def format_currency(amount, currency="USD", locale="en_US"):
    """Format a numeric amount as a currency string.

    Args:
        amount: Numeric amount
        currency: ISO currency code
        locale: Locale for formatting conventions

    Returns:
        Formatted currency string
    """
    symbols = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5"}
    symbol = symbols.get(currency, currency + " ")

    if amount < 0:
        return f"-{symbol}{abs(amount):,.2f}"
    return f"{symbol}{amount:,.2f}"


def format_date(dt, style="short"):
    """Format a datetime object for display.

    Args:
        dt: datetime instance
        style: 'short' (2025-03-15), 'medium' (Mar 15, 2025),
               'long' (March 15, 2025), 'relative' (3 days ago)

    Returns:
        Formatted date string
    """
    if style == "short":
        return dt.strftime("%Y-%m-%d")
    elif style == "medium":
        return dt.strftime("%b %d, %Y")
    elif style == "long":
        return dt.strftime("%B %d, %Y")
    elif style == "relative":
        return _relative_time(dt)
    return dt.isoformat()


def _relative_time(dt):
    """Convert datetime to relative time string."""
    now = datetime.now()
    delta = now - dt
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = seconds // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"


def truncate(text, max_length=50, suffix="..."):
    """Truncate text to a maximum length with suffix.

    Args:
        text: Input string
        max_length: Maximum length including suffix
        suffix: String to append when truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_percentage(value, decimals=1):
    """Format a decimal value as percentage string."""
    return f"{value * 100:.{decimals}f}%"
EOF

# ── src/utils/validators.py ──────────────────────────────────────────────────
cat > src/utils/validators.py << 'EOF'
"""Input validation utilities."""
import re


def validate_email(email):
    """Validate an email address format.

    Args:
        email: Email string to validate

    Returns:
        Tuple of (is_valid, error_message_or_None)
    """
    if not email or not isinstance(email, str):
        return (False, "Email is required")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return (False, "Invalid email format")
    if len(email) > 254:
        return (False, "Email address too long")
    return (True, None)


def validate_username(username):
    """Validate a username.

    Args:
        username: Username string to validate

    Returns:
        Tuple of (is_valid, error_message_or_None)
    """
    if not username or not isinstance(username, str):
        return (False, "Username is required")
    if len(username) < 3:
        return (False, "Username must be at least 3 characters")
    if len(username) > 30:
        return (False, "Username must be at most 30 characters")
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return (False, "Username may only contain letters, numbers, and underscores")
    return (True, None)


def validate_amount(amount):
    """Validate a transaction amount.

    Args:
        amount: Numeric value to validate

    Returns:
        Tuple of (is_valid, error_message_or_None)
    """
    if amount is None:
        return (False, "Amount is required")
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return (False, "Amount must be a number")
    if amount <= 0:
        return (False, "Amount must be positive")
    if amount > 1_000_000:
        return (False, "Amount exceeds maximum limit")
    if round(amount, 2) != amount:
        return (False, "Amount cannot have more than 2 decimal places")
    return (True, None)


def validate_password(password):
    """Validate password strength.

    Args:
        password: Password string

    Returns:
        Tuple of (is_valid, error_message_or_None)
    """
    if not password or not isinstance(password, str):
        return (False, "Password is required")
    if len(password) < 8:
        return (False, "Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        return (False, "Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        return (False, "Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        return (False, "Password must contain at least one digit")
    return (True, None)
EOF

# ── src/__init__.py ──────────────────────────────────────────────────────────
cat > src/__init__.py << 'EOF'
"""FinanceApp — a personal finance dashboard application."""
__version__ = "1.2.0"
EOF

# ── tests/__init__.py ────────────────────────────────────────────────────────
cat > tests/__init__.py << 'EOF'
EOF

# ── tests/test_dashboard.py (HAS FAILING TEST) ──────────────────────────────
cat > tests/test_dashboard.py << 'EOF'
"""Tests for dashboard view."""
import unittest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.views.dashboard import Transaction, get_recent_transactions, get_dashboard_summary


class TestGetRecentTransactions(unittest.TestCase):
    def setUp(self):
        self.transactions = [
            Transaction(1, "Coffee", 4.50, "2025-01-15"),
            Transaction(2, "Groceries", 67.80, "2025-03-01"),
            Transaction(3, "Gas", 45.00, "2025-02-10"),
            Transaction(4, "Restaurant", 32.50, "2025-03-10"),
            Transaction(5, "Books", 29.99, "2025-01-20"),
        ]

    def test_transaction_sort_order(self):
        """Most recent transactions should appear first."""
        result = get_recent_transactions(self.transactions)
        # Newest (2025-03-10) should be first
        self.assertEqual(result[0].id, 4)
        # Second newest (2025-03-01) should be second
        self.assertEqual(result[1].id, 2)

    def test_limit(self):
        """Should respect the limit parameter."""
        result = get_recent_transactions(self.transactions, limit=3)
        self.assertEqual(len(result), 3)

    def test_empty_list(self):
        """Should handle empty list."""
        result = get_recent_transactions([])
        self.assertEqual(result, [])


class TestGetDashboardSummary(unittest.TestCase):
    def test_summary_calculation(self):
        transactions = [
            Transaction(1, "A", 10.00, "2025-01-01"),
            Transaction(2, "B", 20.00, "2025-01-02"),
        ]
        summary = get_dashboard_summary(transactions)
        self.assertEqual(summary["total"], 30.0)
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["average"], 15.0)

    def test_empty_summary(self):
        summary = get_dashboard_summary([])
        self.assertEqual(summary["total"], 0)


if __name__ == '__main__':
    unittest.main()
EOF

# ── tests/test_auth.py ───────────────────────────────────────────────────────
cat > tests/test_auth.py << 'EOF'
"""Tests for authentication service."""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.services.auth import authenticate, validate_session, logout, get_active_sessions


class TestAuthenticate(unittest.TestCase):
    def test_valid_credentials(self):
        """Should return a session token for valid credentials."""
        token = authenticate("alice", "password123")
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 64)  # hex token

    def test_invalid_password(self):
        """Should return None for wrong password."""
        token = authenticate("alice", "wrongpassword")
        self.assertIsNone(token)

    def test_unknown_user(self):
        """Should return None for unknown username."""
        token = authenticate("nonexistent", "password123")
        self.assertIsNone(token)


class TestValidateSession(unittest.TestCase):
    def test_valid_session(self):
        """Should return session data for a valid token."""
        token = authenticate("bob", "letmein")
        session = validate_session(token)
        self.assertIsNotNone(session)
        self.assertEqual(session["username"], "bob")

    def test_invalid_token(self):
        """Should return None for invalid token."""
        session = validate_session("invalid-token-abc123")
        self.assertIsNone(session)


class TestLogout(unittest.TestCase):
    def test_logout_valid_session(self):
        """Should invalidate an existing session."""
        token = authenticate("charlie", "s3cure!")
        self.assertTrue(logout(token))
        self.assertIsNone(validate_session(token))

    def test_logout_invalid_token(self):
        """Should return False for non-existent token."""
        self.assertFalse(logout("fake-token"))


class TestActiveSessions(unittest.TestCase):
    def test_count_after_login(self):
        """Active sessions should increase after login."""
        initial = get_active_sessions()
        authenticate("alice", "password123")
        self.assertGreaterEqual(get_active_sessions(), initial)


if __name__ == '__main__':
    unittest.main()
EOF

# ── tests/test_models.py ─────────────────────────────────────────────────────
cat > tests/test_models.py << 'EOF'
"""Tests for data models."""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.models.user import User
from src.models.account import Account
from src.models.transaction import Transaction, TransactionType, TransactionStatus


class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User(1, "testuser", "test@example.com")

    def test_creation(self):
        self.assertEqual(self.user.user_id, 1)
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.is_active)

    def test_preferences(self):
        self.user.set_preference("theme", "dark")
        self.assertEqual(self.user.get_preference("theme"), "dark")
        self.assertIsNone(self.user.get_preference("missing"))
        self.assertEqual(self.user.get_preference("missing", "default"), "default")

    def test_deactivate(self):
        self.user.deactivate()
        self.assertFalse(self.user.is_active)

    def test_to_dict(self):
        d = self.user.to_dict()
        self.assertEqual(d["username"], "testuser")
        self.assertIn("created_at", d)

    def test_equality(self):
        other = User(1, "different_name", "other@example.com")
        self.assertEqual(self.user, other)
        another = User(2, "testuser", "test@example.com")
        self.assertNotEqual(self.user, another)


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account(100, 1, "Checking", balance=500.0)

    def test_deposit(self):
        result = self.account.deposit(100)
        self.assertEqual(result, 600.0)

    def test_withdraw(self):
        result = self.account.withdraw(200)
        self.assertEqual(result, 300.0)

    def test_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(999)

    def test_negative_deposit(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-50)

    def test_freeze(self):
        self.account.freeze()
        with self.assertRaises(RuntimeError):
            self.account.deposit(100)
        with self.assertRaises(RuntimeError):
            self.account.withdraw(50)

    def test_unfreeze(self):
        self.account.freeze()
        self.account.unfreeze()
        self.account.deposit(100)  # Should not raise


class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.txn = Transaction(1, 100, 50.0, TransactionType.DEBIT, "Test purchase")

    def test_creation(self):
        self.assertEqual(self.txn.txn_id, 1)
        self.assertEqual(self.txn.amount, 50.0)
        self.assertEqual(self.txn.status, TransactionStatus.PENDING)

    def test_complete(self):
        self.assertTrue(self.txn.complete())
        self.assertEqual(self.txn.status, TransactionStatus.COMPLETED)
        # Cannot complete again
        self.assertFalse(self.txn.complete())

    def test_cancel(self):
        self.assertTrue(self.txn.cancel())
        self.assertEqual(self.txn.status, TransactionStatus.CANCELLED)

    def test_is_debit(self):
        self.assertTrue(self.txn.is_debit())
        credit = Transaction(2, 100, 100.0, TransactionType.CREDIT)
        self.assertFalse(credit.is_debit())

    def test_metadata(self):
        self.txn.add_metadata("reference", "INV-001")
        self.assertEqual(self.txn.metadata["reference"], "INV-001")

    def test_string_type_init(self):
        txn = Transaction(3, 100, 25.0, "refund")
        self.assertEqual(txn.txn_type, TransactionType.REFUND)


if __name__ == '__main__':
    unittest.main()
EOF

# ── config/settings.py ───────────────────────────────────────────────────────
cat > config/settings.py << 'EOF'
"""Application configuration settings."""
import os


class Config:
    """Base configuration."""
    APP_NAME = "FinanceApp"
    VERSION = "1.2.0"
    DEBUG = False
    TESTING = False

    # Database
    DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///financeapp.db")
    DATABASE_POOL_SIZE = 5

    # Session
    SESSION_TTL_HOURS = 24
    SESSION_COOKIE_NAME = "financeapp_session"
    SESSION_COOKIE_SECURE = True

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_FROM = "noreply@financeapp.example.com"

    # Pagination
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 100

    # Security
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    DATABASE_URI = "sqlite:///dev.db"


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production environment configuration."""
    DATABASE_POOL_SIZE = 20
    SESSION_COOKIE_SECURE = True


def get_config(env=None):
    """Return configuration for the given environment.

    Args:
        env: Environment name ('development', 'testing', 'production')

    Returns:
        Config class for the environment
    """
    env = env or os.getenv("APP_ENV", "development")
    configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    return configs.get(env, DevelopmentConfig)
EOF

# ── BUG_REPORT.md ────────────────────────────────────────────────────────────
cat > BUG_REPORT.md << 'EOF'
# Bug Report: Dashboard Shows Oldest Transactions First

**Reported by:** Product Manager
**Date:** 2025-03-15
**Severity:** Medium

## Description
The dashboard page shows transactions sorted with the oldest first. Users
expect to see their most recent transactions at the top of the list.

## Expected Behavior
Transactions on the dashboard should be sorted by date with the newest
transactions appearing first (descending order).

## Actual Behavior
Transactions appear in ascending date order (oldest first).

## How to Reproduce
1. View the dashboard
2. Notice transactions are sorted oldest-first instead of newest-first
EOF

# ── README.md ────────────────────────────────────────────────────────────────
cat > README.md << 'EOF'
# FinanceApp

A personal finance dashboard application built with Python.

## Project Structure

```
src/
  models/       — Data models (User, Transaction, Account)
  views/        — View layer (dashboard, profile, settings, transactions)
  services/     — Business logic (auth, email, reporting)
  utils/        — Helpers (formatters, validators)
tests/          — Unit tests
config/         — Application configuration
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Development

This project uses Python 3.8+ with no external dependencies beyond the
standard library (except pytest for testing).
EOF

# ── Initial commit ───────────────────────────────────────────────────────────
git add -A
git commit -q -m "initial: add FinanceApp with dashboard sort bug"
