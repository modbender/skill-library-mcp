#!/usr/bin/env python3
"""
Tests for _common.py utilities.
"""

import sqlite3
from datetime import datetime

import pytest

from _common import (
    coredata_to_datetime,
    datetime_to_coredata,
    escape_applescript,
    format_size,
    get_asset_kind_name,
    get_quality_score,
    is_burst,
    is_favorite,
    is_hidden,
    is_screenshot,
    is_trashed,
    sanitize_folder_name,
    validate_year,
)


class TestTimestampConversion:
    """Test Core Data timestamp conversion."""

    def test_coredata_to_datetime_epoch(self):
        """Test conversion of epoch (0) returns Jan 1, 2001."""
        dt = coredata_to_datetime(0)
        assert dt == datetime(2001, 1, 1, 0, 0, 0)

    def test_coredata_to_datetime_none(self):
        """Test None timestamp returns None."""
        assert coredata_to_datetime(None) is None

    def test_coredata_to_datetime_positive(self):
        """Test positive timestamp."""
        # 1 day = 86400 seconds
        dt = coredata_to_datetime(86400)
        assert dt == datetime(2001, 1, 2, 0, 0, 0)

    def test_datetime_to_coredata_epoch(self):
        """Test conversion of Jan 1, 2001 to 0."""
        dt = datetime(2001, 1, 1, 0, 0, 0)
        timestamp = datetime_to_coredata(dt)
        assert timestamp == 0.0

    def test_datetime_to_coredata_positive(self):
        """Test conversion of later date."""
        dt = datetime(2001, 1, 2, 0, 0, 0)
        timestamp = datetime_to_coredata(dt)
        assert timestamp == 86400.0

    def test_roundtrip(self):
        """Test roundtrip conversion."""
        original = datetime(2025, 3, 3, 12, 30, 45)
        timestamp = datetime_to_coredata(original)
        converted = coredata_to_datetime(timestamp)
        assert converted == original


class TestFormatSize:
    """Test human-readable size formatting."""

    def test_zero(self):
        assert format_size(0) == "0 B"
        assert format_size(None) == "0 B"

    def test_bytes(self):
        assert format_size(500) == "500 B"

    def test_kilobytes(self):
        assert format_size(1024) == "1.00 KB"
        assert format_size(1536) == "1.50 KB"

    def test_megabytes(self):
        assert format_size(1024 * 1024) == "1.00 MB"
        assert format_size(int(2.5 * 1024 * 1024)) == "2.50 MB"

    def test_gigabytes(self):
        assert format_size(1024 * 1024 * 1024) == "1.00 GB"

    def test_large_bytes(self):
        """Test very large sizes."""
        size = 1024 * 1024 * 1024 * 1024  # 1 TB
        result = format_size(size)
        assert "TB" in result


class TestAssetHelpers:
    """Test asset type and attribute helpers."""

    def test_get_asset_kind_name(self):
        assert get_asset_kind_name(0) == "photo"
        assert get_asset_kind_name(1) == "video"
        assert get_asset_kind_name(99) == "unknown_99"

    def test_is_screenshot(self):
        """Test screenshot detection."""
        row = {"ZISDETECTEDSCREENSHOT": 1}
        assert is_screenshot(row) is True

        row = {"ZISDETECTEDSCREENSHOT": 0}
        assert is_screenshot(row) is False

    def test_is_burst(self):
        """Test burst detection."""
        row = {"ZAVALANCHEKIND": 2}
        assert is_burst(row) is True

        row = {"ZAVALANCHEKIND": 0}
        assert is_burst(row) is False

        row = {"ZAVALANCHEKIND": None}
        assert is_burst(row) is False

    def test_is_favorite(self):
        """Test favorite detection."""
        row = {"ZFAVORITE": 1}
        assert is_favorite(row) is True

        row = {"ZFAVORITE": 0}
        assert is_favorite(row) is False

        row = {}
        assert is_favorite(row) is False

    def test_is_hidden(self):
        """Test hidden detection."""
        row = {"ZHIDDEN": 1}
        assert is_hidden(row) is True

        row = {"ZHIDDEN": 0}
        assert is_hidden(row) is False

    def test_is_trashed(self):
        """Test trash detection."""
        row = {"ZTRASHEDSTATE": 1}
        assert is_trashed(row) is True

        row = {"ZTRASHEDSTATE": 0}
        assert is_trashed(row) is False


class TestQualityScore:
    """Test quality score calculation."""

    def test_all_scores_present(self):
        """Test with all quality scores."""
        row = {
            "ZPLEASANTCOMPOSITIONSCORE": 0.8,
            "ZPLEASANTLIGHTINGSCORE": 0.7,
            "ZFAILURESCORE": 0.1,  # Inverted, so 0.9
            "ZNOISESCORE": 0.2,  # Inverted, so 0.8
        }
        score = get_quality_score(row)
        # Average of [0.8, 0.7, 0.9, 0.8] = 0.8
        assert score == pytest.approx(0.8, abs=0.01)

    def test_partial_scores(self):
        """Test with some scores missing."""
        row = {
            "ZPLEASANTCOMPOSITIONSCORE": 0.8,
            "ZFAILURESCORE": 0.2,  # Inverted = 0.8
        }
        score = get_quality_score(row)
        # Average of [0.8, 0.8] = 0.8
        assert score == pytest.approx(0.8, abs=0.01)

    def test_no_scores(self):
        """Test with no quality scores."""
        row = {}
        score = get_quality_score(row)
        assert score is None

    def test_high_quality(self):
        """Test high quality photo."""
        row = {
            "ZPLEASANTCOMPOSITIONSCORE": 0.95,
            "ZPLEASANTLIGHTINGSCORE": 0.9,
            "ZFAILURESCORE": 0.05,
            "ZNOISESCORE": 0.1,
        }
        score = get_quality_score(row)
        assert score > 0.85

    def test_low_quality(self):
        """Test low quality photo."""
        row = {
            "ZPLEASANTCOMPOSITIONSCORE": 0.2,
            "ZPLEASANTLIGHTINGSCORE": 0.3,
            "ZFAILURESCORE": 0.8,
            "ZNOISESCORE": 0.7,
        }
        score = get_quality_score(row)
        assert score < 0.4


def create_test_db():
    """Create in-memory test database with sample data."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create tables
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

    # Insert sample data
    # Photo 1: Normal photo
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            1, 'IMG_001.jpg', ?, 4032, 3024, 0, 0, 1, 0, 0, 41.5, -90.5, 0, NULL, 0
        )
    """,
        (datetime_to_coredata(datetime(2025, 1, 1, 12, 0, 0)),),
    )

    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (1, 5000000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (1, 0.1, 0.2, 0.8, 0.7)")

    # Photo 2: Screenshot
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            2, 'Screenshot.png', ?, 1920, 1080, 0, 1, 0, 0, 0, NULL, NULL, 0, NULL, 0
        )
    """,
        (datetime_to_coredata(datetime(2025, 2, 1, 10, 0, 0)),),
    )

    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (2, 2000000, 1920, 1080)")

    # Photo 3: Burst photo (unpicked)
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            3, 'IMG_002.jpg', ?, 4032, 3024, 0, 0, 0, 0, 0, 41.5, -90.5, 2, 0, 0
        )
    """,
        (datetime_to_coredata(datetime(2025, 3, 1, 15, 0, 0)),),
    )

    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (3, 4500000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (3, 0.3, 0.4, 0.6, 0.5)")

    # Photo 4: Trashed
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            4, 'IMG_003.jpg', ?, 4032, 3024, 0, 0, 0, 0, 1, NULL, NULL, 0, NULL, 0
        )
    """,
        (datetime_to_coredata(datetime(2025, 3, 2, 16, 0, 0)),),
    )

    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (4, 3000000, 4032, 3024)")

    conn.commit()
    return conn


class TestDatabaseQueries:
    """Test database query helpers with test data."""

    def test_query_non_trashed(self):
        """Test querying non-trashed items."""
        conn = create_test_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM ZASSET WHERE ZTRASHEDSTATE != 1")
        results = cursor.fetchall()

        assert len(results) == 3  # Should exclude trashed item

        conn.close()

    def test_query_screenshots(self):
        """Test querying screenshots."""
        conn = create_test_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM ZASSET
            WHERE ZTRASHEDSTATE != 1 AND ZISDETECTEDSCREENSHOT = 1
        """)
        results = cursor.fetchall()

        assert len(results) == 1
        assert results[0]["ZFILENAME"] == "Screenshot.png"

        conn.close()

    def test_query_with_joins(self):
        """Test queries with joins."""
        conn = create_test_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.*, aa.ZORIGINALFILESIZE, ca.ZPLEASANTCOMPOSITIONSCORE
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            LEFT JOIN ZCOMPUTEDASSETATTRIBUTES ca ON a.Z_PK = ca.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
        """)
        results = cursor.fetchall()

        assert len(results) == 3

        # Check that joins worked
        for row in results:
            assert row["ZORIGINALFILESIZE"] is not None

        conn.close()

    def test_storage_calculation(self):
        """Test storage calculation."""
        conn = create_test_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(aa.ZORIGINALFILESIZE) as total
            FROM ZASSET a
            LEFT JOIN ZADDITIONALASSETATTRIBUTES aa ON a.Z_PK = aa.ZASSET
            WHERE a.ZTRASHEDSTATE != 1
        """)
        result = cursor.fetchone()

        # 5MB + 2MB + 4.5MB = 11.5MB
        assert result["total"] == 11500000

        conn.close()


class TestValidateYear:
    """Test year validation."""

    def test_valid_year(self):
        assert validate_year("2025") == "2025"

    def test_valid_year_old(self):
        assert validate_year("1999") == "1999"

    def test_none_returns_none(self):
        assert validate_year(None) is None

    def test_rejects_non_digits(self):
        with pytest.raises(ValueError, match="4-digit number"):
            validate_year("abcd")

    def test_rejects_sql_injection(self):
        with pytest.raises(ValueError, match="4-digit number"):
            validate_year("2025' OR '1'='1")

    def test_rejects_short(self):
        with pytest.raises(ValueError, match="4-digit number"):
            validate_year("25")

    def test_rejects_five_digits(self):
        with pytest.raises(ValueError, match="4-digit number"):
            validate_year("20250")


class TestEscapeApplescript:
    """Test AppleScript string escaping."""

    def test_plain_string(self):
        assert escape_applescript("hello") == "hello"

    def test_escapes_quotes(self):
        assert escape_applescript('say "hi"') == 'say \\"hi\\"'

    def test_escapes_backslashes(self):
        assert escape_applescript("path\\to\\file") == "path\\\\to\\\\file"

    def test_backslash_before_quote(self):
        # Critical: backslashes must be escaped BEFORE quotes
        # Input: photo\"test.jpg  ->  photo\\"test.jpg
        result = escape_applescript('photo\\"test.jpg')
        assert result == 'photo\\\\\\"test.jpg'

    def test_empty_string(self):
        assert escape_applescript("") == ""


class TestSanitizeFolderName:
    """Test folder name sanitization."""

    def test_plain_name(self):
        assert sanitize_folder_name("Vacation 2025") == "Vacation 2025"

    def test_strips_path_traversal(self):
        result = sanitize_folder_name("../../etc/passwd")
        assert "/" not in result
        assert "\\" not in result
        # Path separators removed — no traversal possible
        assert not result.startswith(".")

    def test_strips_leading_dot(self):
        result = sanitize_folder_name(".hidden")
        assert not result.startswith(".")
        assert "hidden" in result

    def test_replaces_slashes(self):
        result = sanitize_folder_name("path/to/folder")
        assert "/" not in result

    def test_replaces_backslashes(self):
        result = sanitize_folder_name("path\\to\\folder")
        assert "\\" not in result

    def test_empty_returns_unnamed(self):
        assert sanitize_folder_name("") == "unnamed"

    def test_dots_only_returns_unnamed(self):
        assert sanitize_folder_name("...") == "unnamed"

    def test_special_chars(self):
        result = sanitize_folder_name('file<>:"|?*name')
        assert all(c not in result for c in '<>:"|?*')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
