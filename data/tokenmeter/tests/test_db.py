"""Tests for database module."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from tokenmeter.db import log_usage, get_usage, get_summary, init_db, DB_PATH


@pytest.fixture
def temp_db(tmp_path):
    """Use a temporary database for testing."""
    test_db = tmp_path / "test_usage.db"
    with patch("tokenmeter.db.DB_PATH", test_db):
        yield test_db


def test_log_usage(temp_db):
    """Test logging a usage record."""
    with patch("tokenmeter.db.DB_PATH", temp_db):
        record_id = log_usage(
            provider="anthropic",
            model="claude-sonnet-4",
            input_tokens=1000,
            output_tokens=500,
            cost=0.0105,
            source="manual",
        )
        assert record_id > 0


def test_get_usage(temp_db):
    """Test retrieving usage records."""
    with patch("tokenmeter.db.DB_PATH", temp_db):
        # Log a record
        log_usage(
            provider="openai",
            model="gpt-4o",
            input_tokens=2000,
            output_tokens=1000,
            cost=0.015,
        )
        
        # Retrieve it
        records = get_usage()
        assert len(records) == 1
        assert records[0].provider == "openai"
        assert records[0].model == "gpt-4o"


def test_get_summary(temp_db):
    """Test summary aggregation."""
    with patch("tokenmeter.db.DB_PATH", temp_db):
        # Log multiple records
        log_usage("anthropic", "claude-sonnet-4", 1000, 500, 0.01)
        log_usage("anthropic", "claude-sonnet-4", 2000, 1000, 0.02)
        log_usage("openai", "gpt-4o", 1500, 750, 0.015)
        
        summary = get_summary(period="day")
        
        assert summary["totals"]["requests"] == 3
        assert "anthropic" in summary["by_provider"]
        assert "openai" in summary["by_provider"]
        assert summary["by_provider"]["anthropic"]["requests"] == 2
