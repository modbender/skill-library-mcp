"""Tests for CSV and OFX import."""

import os
import sys

import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from import_csv import import_csv
from import_ofx import import_ofx


class TestCSVImport:
    def test_chase_import(self, tmp_db, sample_data_dir):
        result = import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["imported"] == 15
        assert result["duplicates"] == 0
        assert result["errors"] == 0
        assert result["format_detected"] == "chase"
        assert result["date_range"]["start"] == "2024-01-05"

    def test_bofa_import(self, tmp_db, sample_data_dir):
        result = import_csv(
            os.path.join(sample_data_dir, "bofa_sample.csv"),
            bank_format="bofa",
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["imported"] == 12
        assert result["duplicates"] == 0
        assert result["errors"] == 0

    def test_wells_fargo_import(self, tmp_db, sample_data_dir):
        result = import_csv(
            os.path.join(sample_data_dir, "wells_fargo_sample.csv"),
            bank_format="wells_fargo",
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["imported"] == 13
        assert result["duplicates"] == 0

    def test_auto_detect_chase(self, tmp_db, sample_data_dir):
        result = import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["format_detected"] == "chase"

    def test_duplicate_detection(self, tmp_db, sample_data_dir):
        # Import once
        result1 = import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        assert result1["imported"] == 15

        # Import again — all should be duplicates
        result2 = import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            db_path=tmp_db,
        )
        assert result2["imported"] == 0
        assert result2["duplicates"] == 15

    def test_file_not_found(self, tmp_db):
        result = import_csv("/nonexistent/file.csv", db_path=tmp_db)
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_account_name_override(self, tmp_db, sample_data_dir):
        result = import_csv(
            os.path.join(sample_data_dir, "chase_sample.csv"),
            bank_format="chase",
            account_name="my-checking",
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["account"] == "my-checking"


class TestOFXImport:
    def test_ofx_import(self, tmp_db, sample_data_dir):
        result = import_ofx(
            os.path.join(sample_data_dir, "sample.ofx"),
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["imported"] == 8
        assert result["duplicates"] == 0
        assert result["errors"] == 0

    def test_ofx_duplicate_detection(self, tmp_db, sample_data_dir):
        import_ofx(
            os.path.join(sample_data_dir, "sample.ofx"),
            db_path=tmp_db,
        )
        result2 = import_ofx(
            os.path.join(sample_data_dir, "sample.ofx"),
            db_path=tmp_db,
        )
        assert result2["imported"] == 0
        assert result2["duplicates"] == 8

    def test_ofx_file_not_found(self, tmp_db):
        result = import_ofx("/nonexistent/file.ofx", db_path=tmp_db)
        assert result["success"] is False

    def test_ofx_account_override(self, tmp_db, sample_data_dir):
        result = import_ofx(
            os.path.join(sample_data_dir, "sample.ofx"),
            account_name="primary-checking",
            db_path=tmp_db,
        )
        assert result["success"] is True
        assert result["account"] == "primary-checking"
