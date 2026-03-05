"""Tests for the report generator."""

import os
import sys

import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from report import generate_report
from import_csv import import_csv
from categorize import run_categorization
from budget import set_budget


@pytest.fixture
def populated_db(tmp_db, sample_data_dir):
    """Database with imported and categorized transactions."""
    import_csv(
        os.path.join(sample_data_dir, "chase_sample.csv"),
        bank_format="chase",
        db_path=tmp_db,
    )
    run_categorization(db_path=tmp_db)
    set_budget("groceries", 200.0, db_path=tmp_db)
    set_budget("dining", 100.0, db_path=tmp_db)
    return tmp_db


class TestJSONReport:
    def test_monthly_report_structure(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="json",
                                 db_path=populated_db)
        assert "period" in report
        assert "summary" in report
        assert "by_category" in report
        assert "top_merchants" in report
        assert "largest_transactions" in report
        assert "trends" in report
        assert "budget_compliance" in report

    def test_monthly_report_values(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="json",
                                 db_path=populated_db)
        summary = report["summary"]
        assert summary["total_spending"] > 0
        assert summary["total_income"] > 0
        assert summary["transaction_count"] > 0
        assert "total_spending_formatted" in summary

    def test_yearly_report(self, populated_db):
        report = generate_report(year=2024, period="yearly", output_format="json",
                                 db_path=populated_db)
        assert report["period"] == "2024"
        assert report["summary"]["total_spending"] > 0

    def test_category_breakdown(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="json",
                                 db_path=populated_db)
        assert len(report["by_category"]) > 0
        # Each category should have required fields
        for cat in report["by_category"]:
            assert "category" in cat
            assert "total" in cat
            assert "percent" in cat
            assert "count" in cat

    def test_top_merchants(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="json",
                                 db_path=populated_db)
        assert len(report["top_merchants"]) > 0
        for m in report["top_merchants"]:
            assert "merchant" in m
            assert "total" in m

    def test_budget_compliance(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="json",
                                 db_path=populated_db)
        assert len(report["budget_compliance"]) > 0
        for b in report["budget_compliance"]:
            assert "category" in b
            assert "budget" in b
            assert "spent" in b
            assert "status" in b
            assert b["status"] in ("ok", "warning", "exceeded")


class TestTextReport:
    def test_text_output(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="text",
                                 db_path=populated_db)
        assert isinstance(report, str)
        assert "Financial Report" in report
        assert "SUMMARY" in report
        assert "SPENDING BY CATEGORY" in report

    def test_text_contains_amounts(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="text",
                                 db_path=populated_db)
        assert "$" in report  # Should contain currency formatting


class TestHTMLReport:
    def test_html_output(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="html",
                                 db_path=populated_db)
        assert isinstance(report, str)
        assert "<!DOCTYPE html>" in report
        assert "Financial Report" in report

    def test_html_has_tables(self, populated_db):
        report = generate_report(month=1, year=2024, output_format="html",
                                 db_path=populated_db)
        assert "<table>" in report
        assert "<th>" in report


class TestEmptyReport:
    def test_empty_db_report(self, tmp_db):
        report = generate_report(month=1, year=2024, output_format="json",
                                 db_path=tmp_db)
        assert report["summary"]["total_spending"] == 0
        assert report["summary"]["total_income"] == 0
        assert report["summary"]["transaction_count"] == 0
