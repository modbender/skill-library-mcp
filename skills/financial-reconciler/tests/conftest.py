"""Shared test fixtures."""

import os
import sys
import tempfile

import pytest

# Add scripts directory to path
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = str(tmp_path / "test.db")
    from db import get_connection, init_db, seed_categories
    conn = get_connection(db_path)
    init_db(conn)
    seed_categories(conn)
    conn.close()
    return db_path


@pytest.fixture
def sample_data_dir():
    """Return path to sample data directory."""
    return SAMPLE_DATA_DIR
