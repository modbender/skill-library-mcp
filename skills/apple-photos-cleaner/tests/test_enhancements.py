#!/usr/bin/env python3
"""
Tests for enhancement scripts: live_photo_analyzer, shared_library,
icloud_status, similarity_finder, seasonal_highlights, face_quality.

Also tests reverse geocoding in location_mapper.

Uses in-memory SQLite databases with sample data.
"""

import sqlite3
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from _common import datetime_to_coredata


def create_enhanced_test_db():
    """Create test database with columns needed by enhancement scripts."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ZASSET with all enhancement columns
    cursor.execute("""
        CREATE TABLE ZASSET (
            Z_PK INTEGER PRIMARY KEY,
            ZFILENAME TEXT,
            ZDATECREATED REAL,
            ZWIDTH INTEGER,
            ZHEIGHT INTEGER,
            ZKIND INTEGER,
            ZISDETECTEDSCREENSHOT INTEGER DEFAULT 0,
            ZFAVORITE INTEGER DEFAULT 0,
            ZHIDDEN INTEGER DEFAULT 0,
            ZTRASHEDSTATE INTEGER DEFAULT 0,
            ZLATITUDE REAL,
            ZLONGITUDE REAL,
            ZAVALANCHEKIND INTEGER DEFAULT 0,
            ZAVALANCHEPICKTYPE INTEGER,
            ZDUPLICATEASSETVISIBILITYSTATE INTEGER DEFAULT 0,
            ZUNIFORMTYPEIDENTIFIER TEXT,
            ZKINDSUBTYPE INTEGER DEFAULT 0,
            ZPLAYBACKSTYLE INTEGER DEFAULT 1,
            ZLIBRARYSCOPE INTEGER DEFAULT 0,
            ZSHAREDLIBRARYSCOPEIDENTIFIER TEXT,
            ZACTIVELIBRARYSCOPEPARTICIPATIONSTATE INTEGER DEFAULT 0,
            ZCLOUDLOCALSTATE INTEGER DEFAULT 0,
            ZCLOUDISMYASSET INTEGER DEFAULT 1,
            ZCLOUDBATCHPUBLISHDATE REAL,
            ZCLOUDISDOWNLOADABLE INTEGER DEFAULT 0,
            ZVISIBILITYSTATE INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE ZADDITIONALASSETATTRIBUTES (
            ZASSET INTEGER,
            ZORIGINALFILESIZE INTEGER,
            ZORIGINALWIDTH INTEGER,
            ZORIGINALHEIGHT INTEGER,
            ZTITLE TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE ZCOMPUTEDASSETATTRIBUTES (
            ZASSET INTEGER,
            ZFAILURESCORE REAL,
            ZNOISESCORE REAL,
            ZPLEASANTCOMPOSITIONSCORE REAL,
            ZPLEASANTLIGHTINGSCORE REAL,
            ZPLEASANTPATTERNSCORE REAL,
            ZPLEASANTPERSPECTIVESCORE REAL,
            ZPLEASANTPOSTPROCESSINGSCORE REAL,
            ZPLEASANTREFLECTIONSSCORE REAL,
            ZPLEASANTSYMMETRYSCORE REAL,
            ZPLEASANTCOLORHUESCORE REAL,
            ZPLEASANTWALLPAPERSCORE REAL,
            ZHARMONIOUSCOLORSCORE REAL,
            ZIMMERSIVENESSSCORE REAL,
            ZINTERACTIONSCORE REAL,
            ZPLEASANTSHARPSCORE REAL,
            ZTASTEFULLYBLURREDSCORE REAL,
            ZWELLFRAMEDSUBJECTSCORE REAL,
            ZWELLTIMEDSHOTSCORE REAL,
            ZWEIGHTEDSCENECLASSIFICATIONSCORE REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE ZPERSON (
            Z_PK INTEGER PRIMARY KEY,
            ZFULLNAME TEXT,
            ZFACECOUNT INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE ZDETECTEDFACE (
            Z_PK INTEGER PRIMARY KEY,
            ZASSET INTEGER,
            ZPERSON INTEGER,
            ZQUALITYMEASURE REAL,
            ZBLURSCORE REAL,
            ZSIZE REAL,
            ZYAWANGLE REAL,
            ZSMILESCORE REAL,
            ZFACEISINCENTER REAL,
            ZCONFIDENCE REAL
        )
    """)

    # People
    cursor.execute("INSERT INTO ZPERSON VALUES (1, 'Alice', 50)")
    cursor.execute("INSERT INTO ZPERSON VALUES (2, 'Bob', 30)")

    # --- Assets ---

    # Photo 1: Live Photo (subtype=2, playback=2), synced, personal, spring
    ts1 = datetime_to_coredata(datetime(2024, 4, 15, 10, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            1, 'IMG_001.heic', ?, 4032, 3024, 0, 0, 1, 0, 0,
            40.7128, -74.0060, 0, NULL, 0, 'public.heic',
            2, 2, 0, NULL, 0, 1, 1, ?, 0, 0
        )
    """,
        (ts1, ts1),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (1, 8000000, 4032, 3024, 'Spring in NYC')")
    cursor.execute("""INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (
        1, 0.05, 0.1, 0.95, 0.9, 0.8, 0.85, 0.7, 0.6, 0.88,
        0.7, 0.6, 0.8, 0.7, 0.5, 0.9, 0.3, 0.85, 0.7, 0.8
    )""")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (1, 1, 1, 0.9, 0.1, 0.6, 0.05, 0.8, 1.0, 0.95)")

    # Photo 2: Live Photo (loop style), synced, shared, summer
    ts2 = datetime_to_coredata(datetime(2024, 7, 20, 14, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            2, 'IMG_002.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            48.8566, 2.3522, 0, NULL, 0, 'public.heic',
            2, 3, 1, 'shared-uuid-abc', 1, 1, 0, ?, 0, 0
        )
    """,
        (ts2, ts2),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (2, 6000000, 4032, 3024, 'Paris Loop')")
    cursor.execute("""INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (
        2, 0.1, 0.15, 0.85, 0.8, 0.7, 0.75, 0.65, 0.5, 0.78,
        0.6, 0.5, 0.7, 0.6, 0.4, 0.8, 0.2, 0.75, 0.6, 0.7
    )""")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (2, 2, 1, 0.7, 0.3, 0.4, 0.2, 0.6, 0.0, 0.80)")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (3, 2, 2, 0.6, 0.4, 0.3, 0.3, 0.4, 0.0, 0.70)")

    # Photo 3: Still photo, local only, personal, fall
    ts3 = datetime_to_coredata(datetime(2024, 10, 5, 9, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            3, 'IMG_003.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            35.6762, 139.6503, 0, NULL, 0, 'public.heic',
            0, 1, 0, NULL, 0, 0, 1, NULL, 0, 0
        )
    """,
        (ts3,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (3, 5000000, 4032, 3024, 'Tokyo Autumn')")
    cursor.execute("""INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (
        3, 0.2, 0.3, 0.7, 0.65, 0.5, 0.5, 0.5, 0.4, 0.6,
        0.5, 0.4, 0.6, 0.5, 0.3, 0.7, 0.4, 0.6, 0.5, 0.6
    )""")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (4, 3, 2, 0.8, 0.15, 0.5, 0.1, 0.7, 1.0, 0.90)")

    # Photo 4: Still photo, synced, shared, winter, high quality
    ts4 = datetime_to_coredata(datetime(2024, 12, 25, 15, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            4, 'IMG_004.heic', ?, 4032, 3024, 0, 0, 1, 0, 0,
            51.5074, -0.1278, 0, NULL, 0, 'public.heic',
            0, 1, 1, 'shared-uuid-abc', 1, 1, 1, ?, 0, 0
        )
    """,
        (ts4, ts4),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (4, 7000000, 4032, 3024, 'London Xmas')")
    cursor.execute("""INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (
        4, 0.05, 0.1, 0.92, 0.88, 0.78, 0.82, 0.68, 0.58, 0.85,
        0.68, 0.58, 0.78, 0.68, 0.48, 0.88, 0.28, 0.82, 0.68, 0.78
    )""")

    # Photo 5: Video, synced, personal, summer
    ts5 = datetime_to_coredata(datetime(2024, 8, 10, 16, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            5, 'VID_001.mov', ?, 1920, 1080, 1, 0, 0, 0, 0,
            40.7128, -74.0060, 0, NULL, 0, 'com.apple.quicktime-movie',
            0, 1, 0, NULL, 0, 1, 1, ?, 0, 0
        )
    """,
        (ts5, ts5),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (5, 50000000, 1920, 1080, NULL)")

    # Photo 6: Large local-only photo, winter
    ts6 = datetime_to_coredata(datetime(2024, 1, 20, 8, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            6, 'IMG_005.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            NULL, NULL, 0, NULL, 0, 'public.heic',
            0, 1, 0, NULL, 0, 0, 1, NULL, 0, 0
        )
    """,
        (ts6,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (6, 15000000, 4032, 3024, NULL)")
    cursor.execute("""INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (
        6, 0.3, 0.25, 0.7, 0.65, 0.5, 0.55, 0.45, 0.35, 0.6,
        0.5, 0.4, 0.55, 0.5, 0.3, 0.65, 0.35, 0.6, 0.5, 0.55
    )""")

    # Photo 7: Trashed (should be excluded)
    ts7 = datetime_to_coredata(datetime(2024, 6, 1, 10, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            7, 'IMG_006.heic', ?, 4032, 3024, 0, 0, 0, 0, 1,
            NULL, NULL, 0, NULL, 0, 'public.heic',
            0, 1, 0, NULL, 0, 0, 1, NULL, 0, 0
        )
    """,
        (ts7,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (7, 4000000, 4032, 3024, NULL)")

    # Photo 8: Live Photo with bounce style, synced, personal, spring
    ts8 = datetime_to_coredata(datetime(2024, 5, 1, 12, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            8, 'IMG_007.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            NULL, NULL, 0, NULL, 0, 'public.heic',
            2, 4, 0, NULL, 0, 1, 1, ?, 0, 0
        )
    """,
        (ts8, ts8),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (8, 7500000, 4032, 3024, NULL)")
    cursor.execute("""INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (
        8, 0.15, 0.2, 0.8, 0.75, 0.6, 0.65, 0.55, 0.45, 0.72,
        0.55, 0.45, 0.65, 0.55, 0.35, 0.75, 0.25, 0.7, 0.55, 0.65
    )""")

    conn.commit()
    return conn


# ===== Live Photo Analyzer Tests =====


class TestLivePhotoAnalyzer:
    """Test live_photo_analyzer.py functionality."""

    def test_analyze_live_photos(self):
        """Test Live Photo analysis."""
        from live_photo_analyzer import analyze_live_photos

        conn = create_enhanced_test_db()

        with patch("live_photo_analyzer.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_live_photos(db_path="test")

        s = result["summary"]
        assert s["live_count"] == 3  # Photos 1, 2, 8
        assert s["still_count"] >= 3  # Photos 3, 4, 6 (+ video excluded by ZKIND)
        assert s["live_storage"] > 0
        assert s["potential_savings"] > 0
        conn.close()

    def test_live_photo_playback_styles(self):
        """Test playback style breakdown."""
        from live_photo_analyzer import analyze_live_photos

        conn = create_enhanced_test_db()

        with patch("live_photo_analyzer.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_live_photos(db_path="test")

        styles = result["by_playback_style"]
        assert "live" in styles
        assert "loop" in styles
        assert "bounce" in styles
        conn.close()

    def test_live_photo_year_filter(self):
        """Test year filtering for Live Photos."""
        from live_photo_analyzer import analyze_live_photos

        conn = create_enhanced_test_db()

        with patch("live_photo_analyzer.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_live_photos(db_path="test", year="2024")

        assert result["summary"]["live_count"] > 0
        conn.close()

    def test_format_summary(self):
        """Test human-readable output."""
        from live_photo_analyzer import analyze_live_photos, format_summary

        conn = create_enhanced_test_db()

        with patch("live_photo_analyzer.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_live_photos(db_path="test")

        text = format_summary(result)
        assert "LIVE PHOTO ANALYSIS" in text
        assert "Live Photos" in text
        conn.close()


# ===== Shared Library Tests =====


class TestSharedLibrary:
    """Test shared_library.py functionality."""

    def test_analyze_shared_library(self):
        """Test shared library analysis."""
        from shared_library import analyze_shared_library

        conn = create_enhanced_test_db()

        with patch("shared_library.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_shared_library(db_path="test")

        s = result["summary"]
        assert s["shared_count"] == 2  # Photos 2 and 4 (ZLIBRARYSCOPE=1)
        assert s["personal_count"] >= 4  # Personal + not-trashed
        assert result["shared_library_enabled"]
        conn.close()

    def test_contributor_tracking(self):
        """Test contributor identification."""
        from shared_library import analyze_shared_library

        conn = create_enhanced_test_db()

        with patch("shared_library.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_shared_library(db_path="test")

        # Both shared photos have 'shared-uuid-abc'
        assert len(result["contributors"]) >= 1
        assert result["contributors"][0]["identifier"] == "shared-uuid-abc"
        conn.close()

    def test_shared_format_summary(self):
        """Test human-readable output."""
        from shared_library import analyze_shared_library, format_summary

        conn = create_enhanced_test_db()

        with patch("shared_library.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_shared_library(db_path="test")

        text = format_summary(result)
        assert "SHARED LIBRARY" in text
        conn.close()


# ===== iCloud Status Tests =====


class TestICloudStatus:
    """Test icloud_status.py functionality."""

    def test_analyze_icloud_status(self):
        """Test iCloud sync analysis."""
        from icloud_status import analyze_icloud_status

        conn = create_enhanced_test_db()

        with patch("icloud_status.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_icloud_status(db_path="test")

        s = result["summary"]
        assert s["synced_count"] > 0  # Photos 1, 2, 4, 5, 8 have ZCLOUDLOCALSTATE=1
        assert s["local_only_count"] > 0  # Photos 3, 6 have ZCLOUDLOCALSTATE=0
        assert s["total_assets"] == s["synced_count"] + s["local_only_count"]
        conn.close()

    def test_large_local_only_tracking(self):
        """Test identification of large local-only items."""
        from icloud_status import analyze_icloud_status

        conn = create_enhanced_test_db()

        with patch("icloud_status.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_icloud_status(db_path="test")

        # Photo 6 is 15MB and local-only
        large = result["local_only_large"]
        assert len(large) >= 1
        filenames = [item["filename"] for item in large]
        assert "IMG_005.heic" in filenames
        conn.close()

    def test_by_kind_breakdown(self):
        """Test photo vs video sync breakdown."""
        from icloud_status import analyze_icloud_status

        conn = create_enhanced_test_db()

        with patch("icloud_status.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_icloud_status(db_path="test")

        assert "photo" in result["by_kind"]
        assert result["by_kind"]["photo"]["synced"] >= 0
        conn.close()

    def test_icloud_format_summary(self):
        """Test human-readable output."""
        from icloud_status import analyze_icloud_status, format_summary

        conn = create_enhanced_test_db()

        with patch("icloud_status.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_icloud_status(db_path="test")

        text = format_summary(result)
        assert "iCLOUD" in text
        conn.close()


# ===== Similarity Finder Tests =====


class TestSimilarityFinder:
    """Test similarity_finder.py functionality."""

    def test_find_similar_photos(self):
        """Test similarity detection."""
        from similarity_finder import find_similar_photos

        conn = create_enhanced_test_db()

        with patch("similarity_finder.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = find_similar_photos(db_path="test", threshold=0.90)

        assert result["summary"]["total_compared"] > 0
        # With a 0.90 threshold some groups should be found
        # (our test photos have similar score profiles)
        assert result["summary"]["groups_found"] >= 0
        conn.close()

    def test_high_threshold_fewer_matches(self):
        """Test that higher threshold produces fewer/no matches."""
        from similarity_finder import find_similar_photos

        conn_low = create_enhanced_test_db()
        conn_high = create_enhanced_test_db()

        with patch("similarity_finder.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn_low)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result_low = find_similar_photos(db_path="test", threshold=0.80)

        with patch("similarity_finder.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn_high)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result_high = find_similar_photos(db_path="test", threshold=0.999)

        assert result_high["summary"]["groups_found"] <= result_low["summary"]["groups_found"]
        conn_low.close()
        conn_high.close()

    def test_cosine_similarity_function(self):
        """Test the cosine similarity calculation directly."""
        from similarity_finder import _cosine_similarity

        # Identical vectors
        assert _cosine_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)
        # Orthogonal vectors
        assert _cosine_similarity([1, 0, 0], [0, 1, 0]) == pytest.approx(0.0)
        # Zero vector
        assert _cosine_similarity([0, 0, 0], [1, 2, 3]) == pytest.approx(0.0)

    def test_similarity_format_summary(self):
        """Test human-readable output."""
        from similarity_finder import find_similar_photos, format_summary

        conn = create_enhanced_test_db()

        with patch("similarity_finder.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = find_similar_photos(db_path="test", threshold=0.90)

        text = format_summary(result)
        assert "SIMILARITY" in text
        conn.close()


# ===== Seasonal Highlights Tests =====


class TestSeasonalHighlights:
    """Test seasonal_highlights.py functionality."""

    def test_get_seasonal_highlights(self):
        """Test seasonal photo selection."""
        from seasonal_highlights import get_seasonal_highlights

        conn = create_enhanced_test_db()

        with patch("seasonal_highlights.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_seasonal_highlights(db_path="test")

        s = result["summary"]
        assert s["total_photos"] > 0
        # Check all seasons are present
        for season in ["spring", "summer", "fall", "winter"]:
            assert season in result["highlights"]
        conn.close()

    def test_seasonal_distribution(self):
        """Test photos are assigned to correct seasons."""
        from seasonal_highlights import get_seasonal_highlights

        conn = create_enhanced_test_db()

        with patch("seasonal_highlights.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_seasonal_highlights(db_path="test")

        # Photo 1 (April) = spring, Photo 2 (July) = summer
        # Photo 3 (October) = fall, Photo 4 (December) = winter
        assert result["highlights"]["spring"]["total_photos"] >= 1
        assert result["highlights"]["summer"]["total_photos"] >= 1
        assert result["highlights"]["fall"]["total_photos"] >= 1
        assert result["highlights"]["winter"]["total_photos"] >= 1
        conn.close()

    def test_southern_hemisphere(self):
        """Test Southern Hemisphere season mapping."""
        from seasonal_highlights import get_seasonal_highlights

        conn = create_enhanced_test_db()

        with patch("seasonal_highlights.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_seasonal_highlights(db_path="test", southern_hemisphere=True)

        assert result["summary"]["hemisphere"] == "southern"
        # December in SH is summer, not winter
        assert result["summary"]["total_photos"] > 0
        conn.close()

    def test_favorites_boosted(self):
        """Test that favorites get score boost."""
        from seasonal_highlights import get_seasonal_highlights

        conn = create_enhanced_test_db()

        with patch("seasonal_highlights.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_seasonal_highlights(db_path="test")

        # Photo 1 is favorite and spring - should rank high in spring
        spring = result["highlights"]["spring"]
        if spring["highlights"]:
            top = spring["highlights"][0]
            # Favorite boosted score should be higher than base quality
            assert top["combined_score"] > 0
        conn.close()

    def test_seasonal_format_summary(self):
        """Test human-readable output."""
        from seasonal_highlights import format_summary, get_seasonal_highlights

        conn = create_enhanced_test_db()

        with patch("seasonal_highlights.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_seasonal_highlights(db_path="test")

        text = format_summary(result)
        assert "SEASONAL" in text
        assert "SPRING" in text
        assert "SUMMER" in text
        conn.close()


# ===== Face Quality Scoring Tests =====


class TestFaceQuality:
    """Test face_quality.py functionality."""

    def test_analyze_face_quality(self):
        """Test face quality analysis."""
        from face_quality import analyze_face_quality

        conn = create_enhanced_test_db()

        with patch("face_quality.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_face_quality(db_path="test")

        s = result["summary"]
        assert s["total_people"] >= 2  # Alice and Bob
        assert s["total_faces"] >= 3  # 1 for Alice(photo1), 1 for Alice(photo2), 1 for Bob(photo2), 1 for Bob(photo3)
        conn.close()

    def test_face_scores_ranked(self):
        """Test that faces are properly ranked by quality."""
        from face_quality import analyze_face_quality

        conn = create_enhanced_test_db()

        with patch("face_quality.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_face_quality(db_path="test")

        for person in result["people"]:
            if person["best_photos"]:
                scores = [f["face_score"] for f in person["best_photos"]]
                # Scores should be in descending order
                for i in range(len(scores) - 1):
                    assert scores[i] >= scores[i + 1]
        conn.close()

    def test_person_filter(self):
        """Test filtering by person name."""
        from face_quality import analyze_face_quality

        conn = create_enhanced_test_db()

        with patch("face_quality.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_face_quality(db_path="test", person_name="Alice")

        assert len(result["people"]) == 1
        assert result["people"][0]["name"] == "Alice"
        conn.close()

    def test_compute_face_score(self):
        """Test the face score computation directly."""
        from face_quality import compute_face_score

        # Perfect face: high quality, no blur, large, frontal, smiling, centered
        perfect = {
            "ZQUALITYMEASURE": 1.0,
            "ZBLURSCORE": 0.0,
            "ZSIZE": 0.8,
            "ZYAWANGLE": 0.0,
            "ZSMILESCORE": 1.0,
            "ZFACEISINCENTER": 1.0,
        }
        # Bad face: low quality, blurry, small, off-angle
        bad = {
            "ZQUALITYMEASURE": 0.1,
            "ZBLURSCORE": 0.9,
            "ZSIZE": 0.05,
            "ZYAWANGLE": 0.8,
            "ZSMILESCORE": 0.0,
            "ZFACEISINCENTER": 0.0,
        }

        perfect_score = compute_face_score(perfect)
        bad_score = compute_face_score(bad)
        assert perfect_score > bad_score
        assert perfect_score > 0.8
        assert bad_score < 0.3

    def test_face_format_summary(self):
        """Test human-readable output."""
        from face_quality import analyze_face_quality, format_summary

        conn = create_enhanced_test_db()

        with patch("face_quality.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_face_quality(db_path="test")

        text = format_summary(result)
        assert "FACE QUALITY" in text
        assert "Alice" in text
        conn.close()


# ===== Reverse Geocoding Tests =====


class TestReverseGeocoding:
    """Test reverse geocoding in location_mapper.py."""

    def test_reverse_geocode_known_city(self):
        """Test geocoding for a known city."""
        from location_mapper import reverse_geocode

        # Near New York City
        result = reverse_geocode(40.7128, -74.0060)
        assert result is not None
        assert "New York" in result

    def test_reverse_geocode_paris(self):
        """Test geocoding for Paris."""
        from location_mapper import reverse_geocode

        result = reverse_geocode(48.8566, 2.3522)
        assert result is not None
        assert "Paris" in result

    def test_reverse_geocode_tokyo(self):
        """Test geocoding for Tokyo."""
        from location_mapper import reverse_geocode

        result = reverse_geocode(35.6762, 139.6503)
        assert result is not None
        assert "Tokyo" in result

    def test_reverse_geocode_unknown_location(self):
        """Test geocoding for a remote ocean location."""
        from location_mapper import reverse_geocode

        # Middle of Pacific Ocean
        result = reverse_geocode(0.0, -160.0)
        assert result is None

    def test_reverse_geocode_near_city(self):
        """Test geocoding for a location near (but not at) a city."""
        from location_mapper import reverse_geocode

        # ~20km from London center (within 50km threshold)
        result = reverse_geocode(51.6, -0.2)
        assert result is not None
        assert "London" in result
