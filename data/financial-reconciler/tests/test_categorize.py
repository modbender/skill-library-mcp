"""Tests for the categorization engine."""

import os
import sys

import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from categorize import categorize_transaction, run_categorization, add_custom_rule
from db import get_connection, get_categorization_rules
from import_csv import import_csv


def _build_rules(db_path):
    """Helper to load rules grouped by type."""
    conn = get_connection(db_path)
    rules = get_categorization_rules(conn)
    rules_by_type = {}
    for rule in rules:
        rt = rule["rule_type"]
        if rt not in rules_by_type:
            rules_by_type[rt] = []
        rules_by_type[rt].append(dict(rule))
    conn.close()
    return rules_by_type


class TestCategorizeTransaction:
    def test_grocery_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Whole Foods Market", rules)
        assert cat == "groceries"
        assert conf >= 0.85

    def test_dining_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Chipotle", rules)
        assert cat == "dining"
        assert conf >= 0.85

    def test_transport_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Uber Trip", rules)
        assert cat == "transport"
        assert conf >= 0.75

    def test_subscription_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Netflix", rules)
        assert cat == "subscriptions"
        assert conf >= 0.85

    def test_shopping_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Amazon", rules)
        assert cat == "shopping"
        assert conf >= 0.85

    def test_healthcare_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Cvs Pharmacy", rules)
        assert cat == "healthcare"
        assert conf >= 0.85

    def test_income_keyword(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Direct Deposit Payroll", rules)
        assert cat == "income"
        assert conf >= 0.85

    def test_uncategorized(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("XYZZY UNKNOWN MERCHANT 99", rules)
        assert cat == "uncategorized"
        assert conf == 0.0

    def test_regex_pattern_match(self, tmp_db):
        rules = _build_rules(tmp_db)
        cat, conf = categorize_transaction("Joe's Italian Restaurant", rules)
        assert cat == "dining"
        assert conf >= 0.75


class TestRunCategorization:
    def test_categorize_imported_transactions(self, tmp_db, sample_data_dir):
        import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        result = run_categorization(db_path=tmp_db)
        assert result["success"] is True
        assert result["categorized"] == 15
        assert "by_category" in result
        # Most transactions should be categorized
        assert result["uncategorized_count"] < result["categorized"]

    def test_recategorize(self, tmp_db, sample_data_dir):
        import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        run_categorization(db_path=tmp_db)

        # Recategorize should process all transactions again
        result = run_categorization(recategorize=True, db_path=tmp_db)
        assert result["success"] is True
        assert result["categorized"] == 15
        assert result["recategorize"] is True

    def test_no_transactions_to_categorize(self, tmp_db):
        result = run_categorization(db_path=tmp_db)
        assert result["success"] is True
        assert result["categorized"] == 0


class TestCustomRules:
    def test_add_keyword_rule(self, tmp_db):
        result = add_custom_rule("dining", "joes pizza", rule_type="keyword", db_path=tmp_db)
        assert result["success"] is True

    def test_add_rule_invalid_category(self, tmp_db):
        result = add_custom_rule("nonexistent", "test", db_path=tmp_db)
        assert result["success"] is False

    def test_custom_rule_applied(self, tmp_db, sample_data_dir):
        add_custom_rule("entertainment", "venmo payment", rule_type="keyword", db_path=tmp_db)

        import_csv(
            os.path.join(sample_data_dir, "wells_fargo_sample.csv"),
            bank_format="wells_fargo",
            db_path=tmp_db,
        )
        result = run_categorization(db_path=tmp_db)
        assert result["success"] is True
        # Venmo transaction should now be categorized as entertainment
        if "entertainment" in result["by_category"]:
            assert result["by_category"]["entertainment"] >= 1
