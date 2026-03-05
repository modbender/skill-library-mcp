#!/usr/bin/env python3
"""
Shared fixtures for all test modules.
"""

import sqlite3
import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable across all test files
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from datetime import datetime

from _common import datetime_to_coredata


@pytest.fixture
def basic_db():
    """
    In-memory test database with 4 simple assets.

    Assets:
      1 - Normal photo (favorite, with location and quality scores)
      2 - Screenshot
      3 - Burst photo (unpicked)
      4 - Trashed photo
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE ZASSET (
            Z_PK INTEGER PRIMARY KEY,
            ZFILENAME TEXT,
            ZDATECREATED REAL,
            ZWIDTH INTEGER,
            ZHEIGHT INTEGER,
            ZKIND INTEGER,
            ZISDETECTEDSCREENSHOT INTEGER,
            ZFAVORITE INTEGER,
            ZHIDDEN INTEGER,
            ZTRASHEDSTATE INTEGER,
            ZLATITUDE REAL,
            ZLONGITUDE REAL,
            ZAVALANCHEKIND INTEGER,
            ZAVALANCHEPICKTYPE INTEGER,
            ZDUPLICATEASSETVISIBILITYSTATE INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE ZADDITIONALASSETATTRIBUTES (
            ZASSET INTEGER,
            ZORIGINALFILESIZE INTEGER,
            ZORIGINALWIDTH INTEGER,
            ZORIGINALHEIGHT INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE ZCOMPUTEDASSETATTRIBUTES (
            ZASSET INTEGER,
            ZFAILURESCORE REAL,
            ZNOISESCORE REAL,
            ZPLEASANTCOMPOSITIONSCORE REAL,
            ZPLEASANTLIGHTINGSCORE REAL
        )
    """)

    cursor.execute(
        """
        INSERT INTO ZASSET VALUES
          (1, 'IMG_001.jpg', ?, 4032, 3024, 0, 0, 1, 0, 0, 41.5, -90.5, 0, NULL, 0)
    """,
        (datetime_to_coredata(datetime(2025, 1, 1, 12, 0, 0)),),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (1, 5000000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (1, 0.1, 0.2, 0.8, 0.7)")

    cursor.execute(
        """
        INSERT INTO ZASSET VALUES
          (2, 'Screenshot.png', ?, 1920, 1080, 0, 1, 0, 0, 0, NULL, NULL, 0, NULL, 0)
    """,
        (datetime_to_coredata(datetime(2025, 2, 1, 10, 0, 0)),),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (2, 2000000, 1920, 1080)")

    cursor.execute(
        """
        INSERT INTO ZASSET VALUES
          (3, 'IMG_002.jpg', ?, 4032, 3024, 0, 0, 0, 0, 0, 41.5, -90.5, 2, 0, 0)
    """,
        (datetime_to_coredata(datetime(2025, 3, 1, 15, 0, 0)),),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (3, 4500000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (3, 0.3, 0.4, 0.6, 0.5)")

    cursor.execute(
        """
        INSERT INTO ZASSET VALUES
          (4, 'IMG_003.jpg', ?, 4032, 3024, 0, 0, 0, 0, 1, NULL, NULL, 0, NULL, 0)
    """,
        (datetime_to_coredata(datetime(2025, 3, 2, 16, 0, 0)),),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (4, 3000000, 4032, 3024)")

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def full_db():
    """
    In-memory test database with comprehensive data for advanced scripts.

    Includes tables: ZASSET, ZADDITIONALASSETATTRIBUTES, ZCOMPUTEDASSETATTRIBUTES,
    ZPERSON, ZDETECTEDFACE, ZSCENECLASSIFICATION, ZGENERICALBUM, Z_27ASSETS.

    Assets:
      1 - High-quality favorite with location, people, scenes (2024-03-03)
      2 - Good quality, not favorited / hidden gem (2025-03-03)
      3 - Screenshot, old (2024-01-01)
      4 - Low quality photo (2025-02-15)
      5 - Burst leftover (2025-03-01)
      6 - Video (2025-03-01)
      7 - Trashed (excluded)
      8 - Duplicate (2025-01-15)
      9 - Orphan photo not in any album (2025-02-20)
    """
    from test_new_scripts import create_full_test_db

    conn = create_full_test_db()
    yield conn
    conn.close()
