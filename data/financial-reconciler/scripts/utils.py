#!/usr/bin/env python3
"""Shared helpers: date parsing, merchant cleaning, currency formatting."""

import re
from datetime import datetime, timedelta

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

# Prefixes commonly prepended by banks to transaction descriptions
STRIP_PREFIXES = [
    r"^POS\s+(DEBIT\s+)?",
    r"^DEBIT\s+(CARD\s+)?(PURCHASE\s+)?",
    r"^ACH\s+(DEBIT\s+|CREDIT\s+)?",
    r"^CHECKCARD\s+\d+\s+",
    r"^PURCHASE\s+(AUTHORIZED\s+ON\s+)?",
    r"^RECURRING\s+(DEBIT\s+|PAYMENT\s+)?",
    r"^VISA\s+DDA\s+",
    r"^PENDING\s+",
    r"^ELECTRONIC\s+",
    r"^ONLINE\s+(BANKING\s+)?(PAYMENT\s+|TRANSFER\s+)?",
    r"^WIRE\s+(TRANSFER\s+)?",
    r"^BILL\s+PAY(MENT)?\s+",
    r"^AUTOPAY\s+",
    r"^MOBILE\s+(PURCHASE\s+)?",
    r"^SQ\s+\*",
    r"^TST\s+\*",
    r"^SP\s+\*?\s*",
]

# Suffixes to strip (dates, card numbers, reference numbers)
STRIP_SUFFIXES = [
    r"\s+\d{2}/\d{2}$",
    r"\s+\d{2}/\d{2}/\d{2,4}$",
    r"\s+\d{4,}$",
    r"\s+#\d+$",
    r"\s+REF\s*#?\s*\d+$",
    r"\s+CARD\s+\d+$",
    r"\s+X{2,}\d{4}$",
    r"\s+\d{2}:\d{2}:\d{2}$",
    r"\s+[A-Z]{2}\s+\d{5}(-\d{4})?$",  # state + zip
]


def clean_merchant_name(description):
    if not description:
        return ""

    name = description.strip().upper()

    for prefix in STRIP_PREFIXES:
        name = re.sub(prefix, "", name, flags=re.IGNORECASE).strip()

    for suffix in STRIP_SUFFIXES:
        name = re.sub(suffix, "", name, flags=re.IGNORECASE).strip()

    # Remove multiple spaces
    name = re.sub(r"\s+", " ", name)

    # Title case for readability
    name = name.title()

    return name


def parse_date(date_str):
    if not date_str:
        return None

    date_str = str(date_str).strip()

    # Common bank date formats
    formats = [
        "%m/%d/%Y",
        "%m/%d/%y",
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%m-%d-%y",
        "%d/%m/%Y",
        "%Y%m%d",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback to dateutil
    try:
        return dateutil_parser.parse(date_str).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def parse_amount(amount_str):
    if amount_str is None:
        return None

    if isinstance(amount_str, (int, float)):
        return round(float(amount_str), 2)

    s = str(amount_str).strip()
    s = s.replace("$", "").replace(",", "").strip()

    # Handle parentheses for negative (accounting style)
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]

    try:
        return round(float(s), 2)
    except ValueError:
        return None


def format_currency(amount):
    if amount is None:
        return "$0.00"
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


def resolve_time_reference(text):
    """Resolve natural language time references to (start_date, end_date) tuples."""
    today = datetime.now()
    text = text.lower().strip()

    if text in ("this month", "current month"):
        start = today.replace(day=1)
        end = (start + relativedelta(months=1)) - timedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    if text in ("last month", "previous month"):
        start = (today.replace(day=1) - relativedelta(months=1))
        end = today.replace(day=1) - timedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    if text in ("this year", "current year", "ytd"):
        start = today.replace(month=1, day=1)
        return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

    if text in ("last year", "previous year"):
        start = today.replace(year=today.year - 1, month=1, day=1)
        end = today.replace(year=today.year - 1, month=12, day=31)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    if text in ("this week", "current week"):
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    if text in ("last week", "previous week"):
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    if text == "today":
        d = today.strftime("%Y-%m-%d")
        return d, d

    if text == "yesterday":
        d = (today - timedelta(days=1)).strftime("%Y-%m-%d")
        return d, d

    # "last N days/weeks/months"
    m = re.match(r"last\s+(\d+)\s+(day|week|month|year)s?", text)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit == "day":
            start = today - timedelta(days=n)
        elif unit == "week":
            start = today - timedelta(weeks=n)
        elif unit == "month":
            start = today - relativedelta(months=n)
        elif unit == "year":
            start = today - relativedelta(years=n)
        return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

    # Month names: "january", "february 2024", etc.
    month_names = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "jun": 6, "jul": 7, "aug": 8, "sep": 9, "sept": 9,
        "oct": 10, "nov": 11, "dec": 12,
    }
    m = re.match(r"(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)(?:\s+(\d{4}))?", text)
    if m:
        month = month_names[m.group(1)]
        year = int(m.group(2)) if m.group(2) else today.year
        start = datetime(year, month, 1)
        end = (start + relativedelta(months=1)) - timedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    # Try parsing as explicit date range: "2024-01-01 to 2024-01-31"
    m = re.match(r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1), m.group(2)

    return None, None
