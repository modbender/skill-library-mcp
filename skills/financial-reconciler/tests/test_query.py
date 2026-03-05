"""Tests for the natural language query parser and executor."""

import os
import sys

import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from query import parse_query, run_query
from import_csv import import_csv
from categorize import run_categorization


CATEGORIES = [
    "groceries", "dining", "transport", "utilities", "subscriptions",
    "shopping", "healthcare", "entertainment", "income", "uncategorized",
]


class TestParseQuery:
    def test_total_spending(self):
        parsed = parse_query("how much did I spend this month", CATEGORIES)
        assert parsed["aggregation"] == "sum"
        assert parsed["time_reference"] == "this month"

    def test_count_query(self):
        parsed = parse_query("how many transactions last month", CATEGORIES)
        assert parsed["aggregation"] == "count"
        assert parsed["time_reference"] == "last month"

    def test_average_query(self):
        parsed = parse_query("what is my average grocery spending", CATEGORIES)
        assert parsed["aggregation"] == "avg"
        assert parsed["category"] == "groceries"

    def test_max_query(self):
        parsed = parse_query("show my largest transaction this year", CATEGORIES)
        assert parsed["aggregation"] == "max"
        assert parsed["time_reference"] == "this year"

    def test_list_query(self):
        parsed = parse_query("list all dining transactions last month", CATEGORIES)
        assert parsed["aggregation"] == "list"
        assert parsed["category"] == "dining"

    def test_category_detection(self):
        parsed = parse_query("total grocery spending", CATEGORIES)
        assert parsed["category"] == "groceries"

    def test_income_query(self):
        parsed = parse_query("how much income this month", CATEGORIES)
        assert parsed["category"] == "income"

    def test_time_last_30_days(self):
        parsed = parse_query("spending last 30 days", CATEGORIES)
        assert parsed["start_date"] is not None
        assert parsed["end_date"] is not None

    def test_month_name(self):
        parsed = parse_query("spending in january 2024", CATEGORIES)
        assert parsed["start_date"] == "2024-01-01"
        assert parsed["end_date"] == "2024-01-31"

    def test_default_time_is_this_month(self):
        parsed = parse_query("total spending on groceries", CATEGORIES)
        assert parsed["start_date"] is not None  # should default to this month


class TestExecuteQuery:
    @pytest.fixture(autouse=True)
    def setup_data(self, tmp_db, sample_data_dir):
        """Import and categorize sample data before each test."""
        self.db_path = tmp_db
        import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        run_categorization(db_path=tmp_db)

    def test_sum_query(self):
        result = run_query("how much did I spend in january 2024", db_path=self.db_path)
        assert result["success"] is True
        assert result["result"]["type"] == "sum"
        assert result["result"]["total"] > 0

    def test_count_query(self):
        result = run_query("how many transactions in january 2024", db_path=self.db_path)
        assert result["success"] is True
        assert result["result"]["type"] == "count"
        assert result["result"]["count"] > 0

    def test_list_query(self):
        result = run_query("show all transactions january 2024", db_path=self.db_path)
        assert result["success"] is True
        assert result["result"]["type"] == "list"
        assert len(result["result"]["transactions"]) > 0

    def test_max_query(self):
        result = run_query("largest transaction january 2024", db_path=self.db_path)
        assert result["success"] is True
        assert result["result"]["type"] == "max"
        assert result["result"]["amount"] > 0

    def test_category_filter(self):
        result = run_query("total grocery spending january 2024", db_path=self.db_path)
        assert result["success"] is True
        assert result["result"]["query"]["category"] == "groceries"
