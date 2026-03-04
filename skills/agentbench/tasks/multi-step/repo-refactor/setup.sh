#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"

cd "$WORKSPACE"
git init -q
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

# ── data/sample.csv ──────────────────────────────────────────────────────────
mkdir -p data

cat > data/sample.csv << 'CSV_EOF'
id,name,email,phone,amount,score,tier,date
1,Alice Johnson,alice@example.com,555-123-4567,150.00,0.85,gold,2024-01-15
2,Bob Smith,bob@example.com,555-234-5678,230.50,0.72,silver,2024-02-20
3,Carol White,carol@example.com,555-345-6789,89.99,0.93,platinum,2024-03-10
4,Dave Brown,dave@example.com,555-456-7890,415.00,0.68,standard,2024-04-05
5,Eve Davis,eve@example.com,555-567-8901,67.25,0.91,gold,2024-05-22
CSV_EOF

# ── utils.py (~200 lines, 15 functions across 4 groups) ─────────────────────
cat > utils.py << 'UTILS_EOF'
"""Utility functions for the application."""
import csv
import json
import re
from datetime import datetime


# === IO Functions ===

def read_csv(filepath):
    """Read CSV file and return list of dicts."""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(filepath, data, fieldnames=None):
    """Write list of dicts to CSV file."""
    if not data:
        return
    if fieldnames is None:
        fieldnames = list(data[0].keys())
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def read_json(filepath):
    """Read JSON file and return parsed data."""
    with open(filepath, 'r') as f:
        return json.load(f)


def write_json(filepath, data, indent=2):
    """Write data to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


# === Validation Functions ===

def validate_email(email):
    """Check if email format is valid."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """Check if phone number format is valid."""
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    return bool(re.match(r'^\+?\d{10,15}$', cleaned))


def validate_date(date_str, fmt='%Y-%m-%d'):
    """Check if date string matches expected format."""
    try:
        datetime.strptime(date_str, fmt)
        return True
    except ValueError:
        return False


def validate_required_fields(record, required):
    """Check that all required fields exist and are non-empty.

    Returns a list of field names that are missing or empty.
    """
    missing = []
    for field in required:
        if field not in record or not record[field]:
            missing.append(field)
    return missing


# === Formatting Functions ===

def format_currency(amount, symbol='$', decimals=2):
    """Format number as currency string.

    Args:
        amount: Numeric value to format.
        symbol: Currency symbol to prepend (default '$').
        decimals: Number of decimal places (default 2).

    Returns:
        Formatted currency string like '$1,234.56'.
    """
    return f"{symbol}{amount:,.{decimals}f}"


def format_date(date_str, from_fmt='%Y-%m-%d', to_fmt='%B %d, %Y'):
    """Convert date string from one format to another.

    Args:
        date_str: Date string in the source format.
        from_fmt: Source format (default '%Y-%m-%d').
        to_fmt: Target format (default '%B %d, %Y').

    Returns:
        Reformatted date string.
    """
    dt = datetime.strptime(date_str, from_fmt)
    return dt.strftime(to_fmt)


def format_phone(phone):
    """Format phone number as (XXX) XXX-XXXX.

    Only formats 10-digit US phone numbers; returns original string otherwise.
    """
    cleaned = re.sub(r'\D', '', phone)
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    return phone


def format_percentage(value, decimals=1):
    """Format number as percentage string.

    Args:
        value: A decimal value (e.g. 0.85 for 85%).
        decimals: Number of decimal places (default 1).

    Returns:
        Formatted percentage string like '85.0%'.
    """
    return f"{value * 100:.{decimals}f}%"


# === Calculation Functions ===

def calculate_total(items, key='amount'):
    """Calculate sum of a specific field across items.

    Args:
        items: List of dicts containing the target field.
        key: Field name to sum (default 'amount').

    Returns:
        Sum of the field values as a float.
    """
    return sum(float(item[key]) for item in items)


def calculate_average(items, key='amount'):
    """Calculate average of a specific field across items.

    Args:
        items: List of dicts containing the target field.
        key: Field name to average (default 'amount').

    Returns:
        Average of the field values, or 0 if items is empty.
    """
    if not items:
        return 0
    return calculate_total(items, key) / len(items)


def calculate_discount(price, tier, seasonal=False):
    """Calculate discount based on customer tier.

    Args:
        price: Original price.
        tier: Customer tier ('standard', 'silver', 'gold', 'platinum').
        seasonal: Whether to apply extra 5% seasonal discount.

    Returns:
        Discounted price rounded to 2 decimal places.
    """
    rates = {'standard': 0, 'silver': 0.05, 'gold': 0.10, 'platinum': 0.15}
    rate = rates.get(tier, 0)
    if seasonal:
        rate += 0.05
    return round(price * (1 - rate), 2)
UTILS_EOF

# ── app.py ───────────────────────────────────────────────────────────────────
cat > app.py << 'APP_EOF'
"""Main application module."""
from utils import read_csv, validate_required_fields, format_currency, calculate_total


class App:
    """Core application that loads and processes order data."""

    REQUIRED_FIELDS = ['id', 'name', 'amount']

    def __init__(self, data_path):
        self.data = read_csv(data_path)

    def validate_records(self):
        """Return list of records with missing required fields."""
        invalid = []
        for record in self.data:
            missing = validate_required_fields(record, self.REQUIRED_FIELDS)
            if missing:
                invalid.append({'record': record, 'missing': missing})
        return invalid

    def get_total_display(self):
        """Return the formatted total of all order amounts."""
        total = calculate_total(self.data, 'amount')
        return format_currency(total)

    def summary(self):
        """Return a summary dict with record count and total."""
        return {
            'record_count': len(self.data),
            'total': self.get_total_display(),
            'invalid_records': len(self.validate_records()),
        }
APP_EOF

# ── reports.py ───────────────────────────────────────────────────────────────
cat > reports.py << 'REPORTS_EOF'
"""Reporting module for generating formatted summaries."""
from utils import read_csv, format_date, format_currency, format_percentage, calculate_average


class ReportGenerator:
    """Generates formatted reports from data files."""

    def __init__(self, data_path):
        self.data = read_csv(data_path)

    def average_amount_display(self):
        """Return the average order amount as a formatted currency string."""
        avg = calculate_average(self.data, 'amount')
        return format_currency(avg)

    def average_score_display(self):
        """Return the average score as a formatted percentage."""
        avg = calculate_average(self.data, 'score')
        return format_percentage(avg)

    def format_record_dates(self, to_fmt='%B %d, %Y'):
        """Return list of records with dates reformatted for display."""
        formatted = []
        for record in self.data:
            entry = dict(record)
            entry['date'] = format_date(record['date'], to_fmt=to_fmt)
            formatted.append(entry)
        return formatted
REPORTS_EOF

# ── invoices.py ──────────────────────────────────────────────────────────────
cat > invoices.py << 'INVOICES_EOF'
"""Invoice generation module."""
from utils import write_csv, validate_email, format_currency, calculate_total, calculate_discount


class InvoiceProcessor:
    """Processes and writes invoice data."""

    def __init__(self, orders):
        self.orders = orders

    def apply_discounts(self):
        """Apply tier-based discounts to all orders and return updated list."""
        result = []
        for order in self.orders:
            price = float(order['amount'])
            tier = order.get('tier', 'standard')
            discounted = calculate_discount(price, tier)
            entry = dict(order)
            entry['discounted_amount'] = discounted
            entry['discounted_display'] = format_currency(discounted)
            result.append(entry)
        return result

    def validate_contacts(self):
        """Return list of orders with invalid email addresses."""
        invalid = []
        for order in self.orders:
            if not validate_email(order.get('email', '')):
                invalid.append(order)
        return invalid

    def get_total(self):
        """Return total of all order amounts."""
        return calculate_total(self.orders, 'amount')

    def export(self, filepath):
        """Apply discounts and write invoices to CSV."""
        invoices = self.apply_discounts()
        write_csv(filepath, invoices)
INVOICES_EOF

# ── contacts.py ──────────────────────────────────────────────────────────────
cat > contacts.py << 'CONTACTS_EOF'
"""Contact management module."""
from utils import read_json, write_json, validate_email, validate_phone, format_phone


class ContactManager:
    """Manages a contact list stored as JSON."""

    def __init__(self, filepath):
        self.filepath = filepath
        try:
            self.contacts = read_json(filepath)
        except FileNotFoundError:
            self.contacts = []

    def add_contact(self, name, email, phone):
        """Add a new contact after validation."""
        errors = []
        if not validate_email(email):
            errors.append(f"Invalid email: {email}")
        if not validate_phone(phone):
            errors.append(f"Invalid phone: {phone}")
        if errors:
            return {'success': False, 'errors': errors}
        self.contacts.append({
            'name': name,
            'email': email,
            'phone': format_phone(phone),
        })
        return {'success': True, 'errors': []}

    def save(self):
        """Persist contacts to the JSON file."""
        write_json(self.filepath, self.contacts)

    def find_by_email(self, email):
        """Look up a contact by email address."""
        for contact in self.contacts:
            if contact.get('email') == email:
                return contact
        return None
CONTACTS_EOF

# ── dashboard.py ─────────────────────────────────────────────────────────────
cat > dashboard.py << 'DASHBOARD_EOF'
"""Dashboard module for at-a-glance metrics."""
from utils import read_csv, format_percentage, calculate_average


class Dashboard:
    """Provides summary metrics for a dashboard view."""

    def __init__(self, data_path):
        self.data = read_csv(data_path)

    def get_average_score(self):
        """Return average score as a formatted percentage."""
        avg = calculate_average(self.data, 'score')
        return format_percentage(avg)

    def get_average_amount(self):
        """Return average order amount as a float."""
        return calculate_average(self.data, 'amount')

    def get_metrics(self):
        """Return a dict of dashboard metrics."""
        return {
            'record_count': len(self.data),
            'avg_score': self.get_average_score(),
            'avg_amount': self.get_average_amount(),
        }
DASHBOARD_EOF

# ── importer.py ──────────────────────────────────────────────────────────────
cat > importer.py << 'IMPORTER_EOF'
"""Data import module supporting CSV and JSON sources."""
from utils import read_csv, read_json, validate_required_fields, validate_date


class DataImporter:
    """Imports and validates data from various file formats."""

    REQUIRED_FIELDS = ['id', 'name', 'date']

    def import_csv(self, filepath):
        """Import records from a CSV file with validation."""
        records = read_csv(filepath)
        return self._validate_records(records)

    def import_json(self, filepath):
        """Import records from a JSON file with validation."""
        records = read_json(filepath)
        return self._validate_records(records)

    def _validate_records(self, records):
        """Validate a list of records and split into valid/invalid."""
        valid = []
        invalid = []
        for record in records:
            missing = validate_required_fields(record, self.REQUIRED_FIELDS)
            date_ok = validate_date(record.get('date', ''))
            if missing or not date_ok:
                invalid.append({
                    'record': record,
                    'missing_fields': missing,
                    'date_valid': date_ok,
                })
            else:
                valid.append(record)
        return {'valid': valid, 'invalid': invalid}
IMPORTER_EOF

# ── exporter.py ──────────────────────────────────────────────────────────────
cat > exporter.py << 'EXPORTER_EOF'
"""Data export module supporting CSV and JSON outputs."""
from utils import write_csv, write_json, format_date, format_currency


class DataExporter:
    """Exports data to various formats with optional formatting."""

    def __init__(self, records):
        self.records = records

    def to_csv(self, filepath, format_dates=False, format_amounts=False):
        """Export records to CSV, optionally formatting dates and amounts."""
        output = self._prepare(format_dates, format_amounts)
        write_csv(filepath, output)

    def to_json(self, filepath, format_dates=False, format_amounts=False):
        """Export records to JSON, optionally formatting dates and amounts."""
        output = self._prepare(format_dates, format_amounts)
        write_json(filepath, output)

    def _prepare(self, format_dates, format_amounts):
        """Apply formatting transformations to a copy of the records."""
        result = []
        for record in self.records:
            entry = dict(record)
            if format_dates and 'date' in entry:
                entry['date'] = format_date(entry['date'])
            if format_amounts and 'amount' in entry:
                entry['amount'] = format_currency(float(entry['amount']))
            result.append(entry)
        return result
EXPORTER_EOF

# ── analytics.py ─────────────────────────────────────────────────────────────
cat > analytics.py << 'ANALYTICS_EOF'
"""Analytics module for business intelligence calculations."""
from utils import read_csv, calculate_total, calculate_average, calculate_discount


class Analytics:
    """Provides analytical computations over order data."""

    def __init__(self, data_path):
        self.data = read_csv(data_path)

    def revenue_total(self):
        """Return the total revenue across all orders."""
        return calculate_total(self.data, 'amount')

    def revenue_average(self):
        """Return the average revenue per order."""
        return calculate_average(self.data, 'amount')

    def projected_revenue(self, seasonal=False):
        """Calculate projected revenue after applying tier discounts."""
        total = 0.0
        for record in self.data:
            price = float(record['amount'])
            tier = record.get('tier', 'standard')
            total += calculate_discount(price, tier, seasonal=seasonal)
        return round(total, 2)

    def discount_savings(self, seasonal=False):
        """Return the total savings from discounts."""
        original = self.revenue_total()
        discounted = self.projected_revenue(seasonal=seasonal)
        return round(original - discounted, 2)
ANALYTICS_EOF

# ── tests/ ───────────────────────────────────────────────────────────────────
mkdir -p tests

cat > tests/__init__.py << 'INIT_EOF'
INIT_EOF

cat > tests/test_io.py << 'TEST_IO_EOF'
"""Tests for IO utility functions."""
import os
import json
import tempfile
import pytest
from utils import read_csv, write_csv, read_json, write_json


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestReadCSV:
    def test_reads_sample_data(self):
        """read_csv returns a list of dicts from the sample file."""
        data = read_csv('data/sample.csv')
        assert isinstance(data, list)
        assert len(data) == 5
        assert data[0]['name'] == 'Alice Johnson'

    def test_keys_match_header(self):
        """Each record should have the expected column keys."""
        data = read_csv('data/sample.csv')
        expected_keys = {'id', 'name', 'email', 'phone', 'amount', 'score', 'tier', 'date'}
        assert set(data[0].keys()) == expected_keys


class TestWriteCSV:
    def test_roundtrip(self, tmp_dir):
        """Writing then reading CSV should return equivalent data."""
        records = [
            {'a': '1', 'b': '2'},
            {'a': '3', 'b': '4'},
        ]
        path = os.path.join(tmp_dir, 'out.csv')
        write_csv(path, records)
        result = read_csv(path)
        assert result == records

    def test_empty_data(self, tmp_dir):
        """Writing empty list should not create a file (no-op)."""
        path = os.path.join(tmp_dir, 'empty.csv')
        write_csv(path, [])
        assert not os.path.exists(path)


class TestReadJSON:
    def test_reads_json_file(self, tmp_dir):
        """read_json should parse a JSON file into Python objects."""
        path = os.path.join(tmp_dir, 'data.json')
        with open(path, 'w') as f:
            json.dump({'key': 'value', 'nums': [1, 2, 3]}, f)
        result = read_json(path)
        assert result == {'key': 'value', 'nums': [1, 2, 3]}


class TestWriteJSON:
    def test_roundtrip(self, tmp_dir):
        """Writing then reading JSON should return equivalent data."""
        data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        path = os.path.join(tmp_dir, 'out.json')
        write_json(path, data)
        result = read_json(path)
        assert result == data

    def test_custom_indent(self, tmp_dir):
        """write_json should respect custom indent parameter."""
        path = os.path.join(tmp_dir, 'indented.json')
        write_json(path, {'a': 1}, indent=4)
        with open(path) as f:
            content = f.read()
        assert '    "a"' in content
TEST_IO_EOF

cat > tests/test_validation.py << 'TEST_VAL_EOF'
"""Tests for validation utility functions."""
import pytest
from utils import validate_email, validate_phone, validate_date, validate_required_fields


class TestValidateEmail:
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "first.last@domain.org",
        "user+tag@sub.domain.co",
    ])
    def test_valid_emails(self, email):
        assert validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "",
        "not-an-email",
        "@no-user.com",
        "user@",
        "user@.com",
    ])
    def test_invalid_emails(self, email):
        assert validate_email(email) is False


class TestValidatePhone:
    @pytest.mark.parametrize("phone", [
        "5551234567",
        "555-123-4567",
        "(555) 123-4567",
        "+15551234567",
    ])
    def test_valid_phones(self, phone):
        assert validate_phone(phone) is True

    @pytest.mark.parametrize("phone", [
        "",
        "123",
        "abcdefghij",
        "12345",
    ])
    def test_invalid_phones(self, phone):
        assert validate_phone(phone) is False


class TestValidateDate:
    def test_valid_default_format(self):
        assert validate_date("2024-01-15") is True

    def test_invalid_default_format(self):
        assert validate_date("01/15/2024") is False

    def test_custom_format(self):
        assert validate_date("15/01/2024", fmt='%d/%m/%Y') is True

    def test_invalid_date_value(self):
        assert validate_date("2024-13-01") is False

    def test_empty_string(self):
        assert validate_date("") is False


class TestValidateRequiredFields:
    def test_all_present(self):
        record = {'name': 'Alice', 'email': 'a@b.com', 'age': '30'}
        assert validate_required_fields(record, ['name', 'email']) == []

    def test_missing_field(self):
        record = {'name': 'Alice'}
        result = validate_required_fields(record, ['name', 'email'])
        assert result == ['email']

    def test_empty_field(self):
        record = {'name': '', 'email': 'a@b.com'}
        result = validate_required_fields(record, ['name', 'email'])
        assert result == ['name']

    def test_multiple_missing(self):
        record = {}
        result = validate_required_fields(record, ['a', 'b', 'c'])
        assert result == ['a', 'b', 'c']
TEST_VAL_EOF

cat > tests/test_calculations.py << 'TEST_CALC_EOF'
"""Tests for calculation utility functions."""
import pytest
from utils import calculate_total, calculate_average, calculate_discount


class TestCalculateTotal:
    def test_basic_sum(self):
        items = [{'amount': '10'}, {'amount': '20'}, {'amount': '30'}]
        assert calculate_total(items) == 60.0

    def test_custom_key(self):
        items = [{'price': '5.5'}, {'price': '4.5'}]
        assert calculate_total(items, key='price') == 10.0

    def test_single_item(self):
        items = [{'amount': '42'}]
        assert calculate_total(items) == 42.0


class TestCalculateAverage:
    def test_basic_average(self):
        items = [{'amount': '10'}, {'amount': '20'}, {'amount': '30'}]
        assert calculate_average(items) == 20.0

    def test_empty_list(self):
        assert calculate_average([]) == 0

    def test_single_item(self):
        items = [{'amount': '50'}]
        assert calculate_average(items) == 50.0

    def test_custom_key(self):
        items = [{'score': '0.8'}, {'score': '0.6'}]
        assert calculate_average(items, key='score') == 0.7


class TestCalculateDiscount:
    def test_standard_no_discount(self):
        assert calculate_discount(100, 'standard') == 100.0

    def test_silver_discount(self):
        assert calculate_discount(100, 'silver') == 95.0

    def test_gold_discount(self):
        assert calculate_discount(100, 'gold') == 90.0

    def test_platinum_discount(self):
        assert calculate_discount(100, 'platinum') == 85.0

    def test_unknown_tier(self):
        assert calculate_discount(100, 'unknown') == 100.0

    def test_seasonal_bonus(self):
        assert calculate_discount(100, 'gold', seasonal=True) == 85.0

    def test_seasonal_with_standard(self):
        assert calculate_discount(100, 'standard', seasonal=True) == 95.0

    def test_rounding(self):
        result = calculate_discount(99.99, 'silver')
        assert result == 94.99
TEST_CALC_EOF

# ── REFACTOR_PLAN.md ─────────────────────────────────────────────────────────
cat > REFACTOR_PLAN.md << 'PLAN_EOF'
# Refactor Plan: Split utils.py

## Goal
Split the monolithic utils.py into 4 focused modules organized by responsibility.

## New Modules
1. `io_utils.py` — File I/O functions: read_csv, write_csv, read_json, write_json
2. `validation.py` — Data validation: validate_email, validate_phone, validate_date, validate_required_fields
3. `formatting.py` — Display formatting: format_currency, format_date, format_phone, format_percentage
4. `calculations.py` — Business logic: calculate_total, calculate_average, calculate_discount

## Steps
1. Create the 4 new module files with functions moved from utils.py
2. Update all imports in consumer files (app.py, reports.py, invoices.py, contacts.py, dashboard.py, importer.py, exporter.py, analytics.py)
3. Update test imports
4. Run tests to verify nothing broke
5. Delete utils.py
6. Commit each logical step separately
PLAN_EOF

# ── Initial commit ───────────────────────────────────────────────────────────
git add -A
git commit -q -m "initial: add Python project with monolithic utils.py"
