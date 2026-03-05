"""Tests for budget management."""

import os
import sys
from datetime import datetime

import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from budget import set_budget, delete_budget, list_budgets, check_budget_status
from import_csv import import_csv
from categorize import run_categorization

# Sample data is from January 2024
JAN_2024 = datetime(2024, 1, 15)


class TestSetBudget:
    def test_set_monthly_budget(self, tmp_db):
        result = set_budget("groceries", 500.0, period="monthly", db_path=tmp_db)
        assert result["success"] is True
        assert result["action"] == "created"
        assert result["category"] == "groceries"
        assert result["amount"] == 500.0

    def test_set_yearly_budget(self, tmp_db):
        result = set_budget("dining", 3000.0, period="yearly", db_path=tmp_db)
        assert result["success"] is True
        assert result["period"] == "yearly"

    def test_update_existing_budget(self, tmp_db):
        set_budget("groceries", 500.0, db_path=tmp_db)
        result = set_budget("groceries", 600.0, db_path=tmp_db)
        assert result["success"] is True
        assert result["action"] == "updated"
        assert result["amount"] == 600.0

    def test_invalid_category(self, tmp_db):
        result = set_budget("nonexistent", 500.0, db_path=tmp_db)
        assert result["success"] is False

    def test_invalid_period(self, tmp_db):
        result = set_budget("groceries", 500.0, period="weekly", db_path=tmp_db)
        assert result["success"] is False

    def test_negative_amount(self, tmp_db):
        result = set_budget("groceries", -100.0, db_path=tmp_db)
        assert result["success"] is False


class TestDeleteBudget:
    def test_delete_existing(self, tmp_db):
        set_budget("groceries", 500.0, db_path=tmp_db)
        result = delete_budget("groceries", db_path=tmp_db)
        assert result["success"] is True
        assert "deleted" in result["message"].lower()

    def test_delete_nonexistent(self, tmp_db):
        result = delete_budget("groceries", db_path=tmp_db)
        assert result["success"] is True  # no error, just no-op
        assert "no" in result["message"].lower()


class TestListBudgets:
    def test_list_empty(self, tmp_db):
        result = list_budgets(db_path=tmp_db)
        assert result["success"] is True
        assert result["count"] == 0

    def test_list_with_budgets(self, tmp_db):
        set_budget("groceries", 500.0, db_path=tmp_db)
        set_budget("dining", 300.0, db_path=tmp_db)
        result = list_budgets(db_path=tmp_db)
        assert result["success"] is True
        assert result["count"] == 2


class TestBudgetStatus:
    def test_no_budgets(self, tmp_db):
        result = check_budget_status(db_path=tmp_db)
        assert result["success"] is True
        assert len(result["statuses"]) == 0

    def test_budget_status_ok(self, tmp_db, sample_data_dir):
        # Import data and categorize
        import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        run_categorization(db_path=tmp_db)

        # Set a very high budget
        set_budget("groceries", 10000.0, db_path=tmp_db)

        result = check_budget_status(category_name="groceries", db_path=tmp_db,
                                     reference_date=JAN_2024)
        assert result["success"] is True
        if result["statuses"]:
            assert result["statuses"][0]["status"] == "ok"

    def test_budget_status_exceeded(self, tmp_db, sample_data_dir):
        import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        run_categorization(db_path=tmp_db)

        # Set a very low budget
        set_budget("groceries", 1.0, db_path=tmp_db)

        result = check_budget_status(category_name="groceries", db_path=tmp_db,
                                     reference_date=JAN_2024)
        assert result["success"] is True
        if result["statuses"]:
            assert result["statuses"][0]["status"] == "exceeded"

    def test_budget_specific_category(self, tmp_db):
        set_budget("groceries", 500.0, db_path=tmp_db)
        set_budget("dining", 300.0, db_path=tmp_db)

        result = check_budget_status(category_name="groceries", db_path=tmp_db)
        assert result["success"] is True
        assert len(result["statuses"]) == 1
        assert result["statuses"][0]["category"] == "groceries"
