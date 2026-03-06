#!/usr/bin/env python3
"""
Tests for new scripts: best_photos, people_analyzer, location_mapper,
scene_search, photo_habits, on_this_day, album_auditor, cleanup_executor.

Uses in-memory SQLite databases with sample data.
"""

import sqlite3
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from _common import datetime_to_coredata


def create_full_test_db():
    """Create an in-memory test database with comprehensive sample data."""
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
            ZISDETECTEDSCREENSHOT INTEGER DEFAULT 0,
            ZFAVORITE INTEGER DEFAULT 0,
            ZHIDDEN INTEGER DEFAULT 0,
            ZTRASHEDSTATE INTEGER DEFAULT 0,
            ZLATITUDE REAL,
            ZLONGITUDE REAL,
            ZAVALANCHEKIND INTEGER DEFAULT 0,
            ZAVALANCHEPICKTYPE INTEGER,
            ZDUPLICATEASSETVISIBILITYSTATE INTEGER DEFAULT 0,
            ZUNIFORMTYPEIDENTIFIER TEXT
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
            ZPLEASANTLIGHTINGSCORE REAL,
            ZPLEASANTPATTERNSCORE REAL,
            ZPLEASANTPERSPECTIVESCORE REAL,
            ZPLEASANTPOSTPROCESSINGSCORE REAL,
            ZPLEASANTREFLECTIONSSCORE REAL,
            ZPLEASANTSYMMETRYSCORE REAL
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
            ZASSET INTEGER,
            ZPERSON INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE ZSCENECLASSIFICATION (
            ZASSET INTEGER,
            ZSCENENAME TEXT,
            ZCONFIDENCE REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE ZGENERICALBUM (
            Z_PK INTEGER PRIMARY KEY,
            ZTITLE TEXT,
            ZKIND INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE Z_27ASSETS (
            Z_27ALBUMS INTEGER,
            Z_3ASSETS INTEGER
        )
    """)

    # -- Insert sample data --

    # People
    cursor.execute("INSERT INTO ZPERSON VALUES (1, 'Jonah', 100)")
    cursor.execute("INSERT INTO ZPERSON VALUES (2, 'Silas', 80)")
    cursor.execute("INSERT INTO ZPERSON VALUES (3, NULL, 10)")  # unnamed

    # Albums
    cursor.execute("INSERT INTO ZGENERICALBUM VALUES (1, 'Vacation 2024', 2)")
    cursor.execute("INSERT INTO ZGENERICALBUM VALUES (2, 'Summer 2024', 2)")
    cursor.execute("INSERT INTO ZGENERICALBUM VALUES (3, 'Empty Album', 2)")

    # Photo 1: High quality favorite, with location, in album
    ts1 = datetime_to_coredata(datetime(2024, 3, 3, 10, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            1, 'IMG_001.heic', ?, 4032, 3024, 0, 0, 1, 0, 0,
            41.5369, -90.5776, 0, NULL, 0, 'public.heic'
        )
    """,
        (ts1,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (1, 5000000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (1, 0.05, 0.1, 0.95, 0.9, 0.8, 0.85, 0.7, 0.6, 0.88)")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (1, 1)")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (1, 2)")
    cursor.execute("INSERT INTO ZSCENECLASSIFICATION VALUES (1, 'beach', 0.9)")
    cursor.execute("INSERT INTO ZSCENECLASSIFICATION VALUES (1, 'outdoor', 0.8)")
    cursor.execute("INSERT INTO Z_27ASSETS VALUES (1, 1)")
    cursor.execute("INSERT INTO Z_27ASSETS VALUES (2, 1)")  # overlap

    # Photo 2: Good quality, not favorited (hidden gem), same date different year
    ts2 = datetime_to_coredata(datetime(2025, 3, 3, 14, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            2, 'IMG_002.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            41.5370, -90.5775, 0, NULL, 0, 'public.heic'
        )
    """,
        (ts2,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (2, 4500000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (2, 0.1, 0.15, 0.85, 0.8, 0.7, 0.75, 0.65, 0.5, 0.78)")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (2, 1)")
    cursor.execute("INSERT INTO ZSCENECLASSIFICATION VALUES (2, 'portrait', 0.85)")
    cursor.execute("INSERT INTO Z_27ASSETS VALUES (1, 2)")

    # Photo 3: Screenshot, old
    ts3 = datetime_to_coredata(datetime(2024, 1, 1, 9, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            3, 'Screenshot_001.png', ?, 1920, 1080, 0, 1, 0, 0, 0,
            NULL, NULL, 0, NULL, 0, 'public.png'
        )
    """,
        (ts3,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (3, 2000000, 1920, 1080)")

    # Photo 4: Low quality
    ts4 = datetime_to_coredata(datetime(2025, 2, 15, 8, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            4, 'IMG_003.jpg', ?, 1024, 768, 0, 0, 0, 0, 0,
            NULL, NULL, 0, NULL, 0, 'public.jpeg'
        )
    """,
        (ts4,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (4, 500000, 1024, 768)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (4, 0.8, 0.7, 0.2, 0.15, 0.1, 0.1, 0.1, 0.1, 0.1)")

    # Photo 5: Burst leftover
    ts5 = datetime_to_coredata(datetime(2025, 3, 1, 16, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            5, 'IMG_004.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            41.5369, -90.5776, 2, 0, 0, 'public.heic'
        )
    """,
        (ts5,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (5, 4000000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (5, 0.3, 0.4, 0.6, 0.5, 0.4, 0.4, 0.4, 0.3, 0.5)")

    # Photo 6: Video
    ts6 = datetime_to_coredata(datetime(2025, 3, 1, 16, 30, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            6, 'VID_001.mov', ?, 1920, 1080, 1, 0, 0, 0, 0,
            41.5369, -90.5776, 0, NULL, 0, 'com.apple.quicktime-movie'
        )
    """,
        (ts6,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (6, 50000000, 1920, 1080)")

    # Photo 7: Trashed (should be excluded)
    ts7 = datetime_to_coredata(datetime(2025, 3, 2, 10, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            7, 'IMG_005.heic', ?, 4032, 3024, 0, 0, 0, 0, 1,
            NULL, NULL, 0, NULL, 0, 'public.heic'
        )
    """,
        (ts7,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (7, 3000000, 4032, 3024)")

    # Photo 8: Duplicate
    ts8 = datetime_to_coredata(datetime(2025, 1, 15, 12, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            8, 'IMG_006.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            NULL, NULL, 0, NULL, 2, 'public.heic'
        )
    """,
        (ts8,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (8, 4800000, 4032, 3024)")

    # Photo 9: Orphan photo (not in any album)
    ts9 = datetime_to_coredata(datetime(2025, 2, 20, 11, 0, 0))
    cursor.execute(
        """
        INSERT INTO ZASSET VALUES (
            9, 'IMG_007.heic', ?, 4032, 3024, 0, 0, 0, 0, 0,
            42.0, -91.0, 0, NULL, 0, 'public.heic'
        )
    """,
        (ts9,),
    )
    cursor.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (9, 3500000, 4032, 3024)")
    cursor.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (9, 0.2, 0.3, 0.7, 0.65, 0.5, 0.5, 0.5, 0.4, 0.6)")
    cursor.execute("INSERT INTO ZDETECTEDFACE VALUES (9, 1)")
    cursor.execute("INSERT INTO ZSCENECLASSIFICATION VALUES (9, 'dog', 0.7)")

    conn.commit()
    return conn


# ===== Best Photos Tests =====


class TestBestPhotos:
    """Test best_photos.py functionality."""

    def test_find_best_photos(self):
        """Test finding best quality photos."""
        from best_photos import find_best_photos

        conn = create_full_test_db()

        with patch("best_photos.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = find_best_photos(db_path="test", min_quality=0.5, top_n=10)

        assert result["summary"]["total_with_scores"] > 0
        assert len(result["top_photos"]) > 0
        # Photo 1 should be top (highest quality)
        assert result["top_photos"][0]["filename"] == "IMG_001.heic"
        assert result["top_photos"][0]["quality_score"] > 0.8
        conn.close()

    def test_hidden_gems_only(self):
        """Test filtering to hidden gems (not favorited)."""
        from best_photos import find_best_photos

        conn = create_full_test_db()

        with patch("best_photos.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = find_best_photos(db_path="test", min_quality=0.5, hidden_gems_only=True)

        # Photo 1 is favorited, so should not appear in hidden gems
        for photo in result["top_photos"]:
            assert not photo["is_favorite"]
        conn.close()

    def test_quality_distribution(self):
        """Test quality distribution histogram."""
        from best_photos import find_best_photos

        conn = create_full_test_db()

        with patch("best_photos.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = find_best_photos(db_path="test", min_quality=0.0)

        dist = result["quality_distribution"]
        total = sum(dist.values())
        assert total > 0
        assert dist["excellent"] >= 0
        conn.close()

    def test_format_summary(self):
        """Test human-readable format."""
        from best_photos import format_summary

        data = {
            "top_photos": [
                {
                    "filename": "test.jpg",
                    "quality_score": 0.9,
                    "size_formatted": "4 MB",
                    "dimensions": "4032x3024",
                    "is_favorite": False,
                    "detail_scores": {"composition": 0.95, "lighting": 0.88},
                }
            ],
            "summary": {
                "total_with_scores": 100,
                "total_above_threshold": 50,
                "hidden_gems": 40,
                "favorited_high_quality": 10,
                "total_favorites": 15,
                "min_quality_threshold": 0.7,
                "top_n": 50,
            },
            "quality_distribution": {
                "excellent": 10,
                "good": 40,
                "average": 30,
                "below_average": 15,
                "poor": 5,
            },
        }
        output = format_summary(data)
        assert "⭐" in output
        assert "Hidden gems" in output
        assert "test.jpg" in output


# ===== People Analyzer Tests =====


class TestPeopleAnalyzer:
    """Test people_analyzer.py functionality."""

    def test_analyze_people(self):
        """Test people analysis."""
        from people_analyzer import analyze_people

        conn = create_full_test_db()

        with patch("people_analyzer.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_people(db_path="test", min_photos=1)

        assert result["summary"]["total_named_people"] >= 1
        # Jonah should be in results (appears in photos 1, 2, 9)
        names = [p["name"] for p in result["people"]]
        assert "Jonah" in names
        conn.close()

    def test_co_occurrences(self):
        """Test co-occurrence detection."""
        from people_analyzer import analyze_people

        conn = create_full_test_db()

        with patch("people_analyzer.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_people(db_path="test", min_photos=1)

        # Jonah + Silas appear together in photo 1
        if result["co_occurrences"]:
            pair = result["co_occurrences"][0]
            assert pair["shared_photos"] >= 1
        conn.close()

    def test_format_summary(self):
        """Test human-readable format."""
        from people_analyzer import format_summary

        data = {
            "people": [{"name": "Jonah", "photo_count": 100, "favorites": 5, "by_year": {"2025": 50}}],
            "co_occurrences": [{"person_1": "Jonah", "person_2": "Silas", "shared_photos": 30}],
            "summary": {"total_named_people": 2, "unnamed_face_photos": 10, "min_photos_threshold": 5},
        }
        output = format_summary(data)
        assert "👥" in output
        assert "Jonah" in output


# ===== Location Mapper Tests =====


class TestLocationMapper:
    """Test location_mapper.py functionality."""

    def test_haversine(self):
        """Test haversine distance calculation."""
        from location_mapper import haversine_km

        # Same point = 0
        assert haversine_km(0, 0, 0, 0) == 0
        # Known distance: ~111 km per degree latitude at equator
        dist = haversine_km(0, 0, 1, 0)
        assert 110 < dist < 112

    def test_clustering(self):
        """Test location clustering."""
        from location_mapper import cluster_locations

        photos = [
            {"latitude": 41.5369, "longitude": -90.5776},
            {"latitude": 41.5370, "longitude": -90.5775},
            {"latitude": 42.0, "longitude": -91.0},  # far away
        ]
        clusters = cluster_locations(photos, radius_km=1.0)
        assert len(clusters) == 2  # Two clusters
        assert clusters[0]["photo_count"] == 2  # First cluster has 2
        assert clusters[1]["photo_count"] == 1

    def test_analyze_locations(self):
        """Test location analysis."""
        from location_mapper import analyze_locations

        conn = create_full_test_db()

        with patch("location_mapper.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_locations(db_path="test", min_photos=1)

        assert result["summary"]["total_with_location"] > 0
        assert len(result["locations"]) > 0
        conn.close()

    def test_format_summary(self):
        """Test human-readable format."""
        from location_mapper import format_summary

        data = {
            "locations": [
                {
                    "centroid_lat": 41.5,
                    "centroid_lon": -90.5,
                    "photo_count": 10,
                    "favorites": 2,
                    "is_trip": True,
                    "total_size_formatted": "5 MB",
                    "first_photo": "2025-01-01",
                    "last_photo": "2025-01-05",
                    "people": [],
                }
            ],
            "trips": [],
            "summary": {
                "total_with_location": 100,
                "total_without_location": 20,
                "location_coverage": 83.3,
                "unique_locations": 5,
                "identified_trips": 1,
                "cluster_radius_km": 1.0,
            },
        }
        output = format_summary(data)
        assert "📍" in output
        assert "41.5" in output


# ===== Scene Search Tests =====


class TestSceneSearch:
    """Test scene_search.py functionality."""

    def test_search_by_scene(self):
        """Test searching for a specific scene."""
        from scene_search import search_scenes

        conn = create_full_test_db()

        with patch("scene_search.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = search_scenes(db_path="test", search_term="beach")

        assert result["mode"] == "search"
        assert result["summary"]["total_matches"] >= 1
        assert result["results"][0]["scene"] == "beach"
        conn.close()

    def test_inventory_mode(self):
        """Test content inventory (no search term)."""
        from scene_search import search_scenes

        conn = create_full_test_db()

        with patch("scene_search.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = search_scenes(db_path="test")

        assert result["mode"] == "inventory"
        assert result["summary"]["total_scenes"] > 0
        scene_names = [s["scene"] for s in result["scenes"]]
        assert "beach" in scene_names
        conn.close()

    def test_no_results(self):
        """Test search with no matches."""
        from scene_search import search_scenes

        conn = create_full_test_db()

        with patch("scene_search.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = search_scenes(db_path="test", search_term="zzz_nonexistent")

        assert result["summary"]["total_matches"] == 0
        conn.close()


# ===== Photo Habits Tests =====


class TestPhotoHabits:
    """Test photo_habits.py functionality."""

    def test_analyze_habits(self):
        """Test habits analysis."""
        from photo_habits import analyze_habits

        conn = create_full_test_db()

        with patch("photo_habits.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_habits(db_path="test")

        s = result["summary"]
        assert s["total_photos"] > 0
        assert s["total_videos"] >= 1  # VID_001.mov
        assert s["total_screenshots"] >= 1  # Screenshot_001.png
        assert len(result["by_hour"]) == 24
        assert len(result["by_day_of_week"]) == 7
        assert len(result["by_month"]) == 12
        conn.close()

    def test_streaks(self):
        """Test streak calculation."""
        from photo_habits import analyze_habits

        conn = create_full_test_db()

        with patch("photo_habits.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_habits(db_path="test")

        streaks = result["streaks"]
        # Photos on March 1 (2 photos) and consecutive days should form a streak
        assert streaks.get("max_days", 0) >= 1
        assert streaks.get("total_active_days", 0) > 0
        conn.close()

    def test_time_of_day(self):
        """Test time-of-day categorization."""
        from photo_habits import analyze_habits

        conn = create_full_test_db()

        with patch("photo_habits.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = analyze_habits(db_path="test")

        tod = result["time_of_day"]
        total = sum(v["count"] for v in tod.values())
        assert total > 0
        # We have photos at 10:00, 14:00, 8:00, 16:00, etc.
        assert tod["morning"]["count"] >= 0
        assert tod["afternoon"]["count"] >= 0
        conn.close()


# ===== On This Day Tests =====


class TestOnThisDay:
    """Test on_this_day.py functionality."""

    def test_on_this_day_match(self):
        """Test finding photos on March 3 from previous years."""
        from on_this_day import on_this_day

        conn = create_full_test_db()

        with patch("on_this_day.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            # Photos on March 3: ID 1 (2024) and ID 2 (2025)
            result = on_this_day(db_path="test", target_date="2026-03-03")

        assert result["target_month_day"] == "March 3"
        assert result["summary"]["total_photos"] >= 1
        conn.close()

    def test_on_this_day_no_match(self):
        """Test date with no photos."""
        from on_this_day import on_this_day

        conn = create_full_test_db()

        with patch("on_this_day.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = on_this_day(db_path="test", target_date="2026-07-15")

        assert result["summary"]["total_photos"] == 0
        conn.close()

    def test_window(self):
        """Test date window expands results."""
        from on_this_day import on_this_day

        conn = create_full_test_db()

        with patch("on_this_day.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            # March 1 photos (ID 5, 6) within window of March 3 ±2
            result = on_this_day(db_path="test", target_date="2026-03-03", window_days=2)

        assert result["summary"]["total_photos"] >= 1
        conn.close()

    def test_format_summary(self):
        """Test human-readable format."""
        from on_this_day import format_summary

        data = {
            "target_date": "2026-03-03",
            "target_month_day": "March 3",
            "window_days": 0,
            "years": [
                {
                    "year": 2024,
                    "years_ago": 2,
                    "photo_count": 5,
                    "favorites": 1,
                    "people": [{"name": "Jonah", "count": 3}],
                    "scenes": [{"scene": "beach", "count": 2}],
                    "best_photo": {"filename": "IMG_001.heic", "quality_score": 0.9},
                },
            ],
            "summary": {"total_photos": 5, "years_with_photos": 1},
        }
        output = format_summary(data)
        assert "📅" in output
        assert "March 3" in output
        assert "2024" in output


# ===== Album Auditor Tests =====


class TestAlbumAuditor:
    """Test album_auditor.py functionality."""

    def test_audit_albums(self):
        """Test album audit."""
        from album_auditor import audit_albums

        conn = create_full_test_db()

        with patch("album_auditor.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = audit_albums(db_path="test")

        s = result["summary"]
        assert s["total_albums"] >= 3
        assert s["empty_albums"] >= 1  # "Empty Album"
        assert s["orphan_photos"] >= 0
        conn.close()

    def test_album_overlap(self):
        """Test overlap detection."""
        from album_auditor import audit_albums

        conn = create_full_test_db()

        with patch("album_auditor.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = audit_albums(db_path="test")

        # Photo 1 is in both "Vacation 2024" and "Summer 2024"
        if result["overlaps"]:
            assert result["overlaps"][0]["shared_count"] >= 1
        conn.close()

    def test_find_junction_table(self):
        """Test junction table discovery."""
        from album_auditor import _find_album_junction_table

        conn = create_full_test_db()
        cursor = conn.cursor()
        result = _find_album_junction_table(cursor)
        assert result is not None
        _album_col, _asset_col, table_name = result
        assert table_name == "Z_27ASSETS"
        conn.close()

    def test_format_summary(self):
        """Test human-readable format."""
        from album_auditor import format_summary

        data = {
            "albums": [{"title": "Vacation", "photo_count": 100, "total_size_formatted": "500 MB"}],
            "empty_albums": [{"title": "Empty"}],
            "tiny_albums": [{"title": "Tiny", "photo_count": 2}],
            "overlaps": [
                {
                    "album_1": "A",
                    "album_2": "B",
                    "album_1_count": 10,
                    "album_2_count": 20,
                    "shared_count": 5,
                    "overlap_pct_album_1": 50,
                    "overlap_pct_album_2": 25,
                }
            ],
            "orphans": {"count": 500, "total_size": 1000000, "total_size_formatted": "1 MB"},
            "summary": {
                "total_albums": 10,
                "albums_with_photos": 8,
                "empty_albums": 1,
                "tiny_albums": 2,
                "total_photos": 1000,
                "photos_in_albums": 500,
                "orphan_photos": 500,
                "albums_with_overlap": 1,
            },
        }
        output = format_summary(data)
        assert "📁" in output
        assert "Orphan" in output


# ===== Cleanup Executor Tests =====


class TestCleanupExecutor:
    """Test cleanup_executor.py functionality."""

    def test_get_candidates_screenshots(self):
        """Test getting old screenshot candidates."""
        from cleanup_executor import get_cleanup_candidates

        conn = create_full_test_db()

        with patch("cleanup_executor.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_cleanup_candidates(
                db_path="test",
                category="old_screenshots",
                screenshot_age_days=30,
            )

        # Screenshot_001.png is from Jan 2024, should be old
        assert result["summary"]["count"] >= 1
        assert result["summary"]["category"] == "old_screenshots"
        filenames = [c["filename"] for c in result["candidates"]]
        assert "Screenshot_001.png" in filenames
        conn.close()

    def test_get_candidates_burst(self):
        """Test getting burst leftover candidates."""
        from cleanup_executor import get_cleanup_candidates

        conn = create_full_test_db()

        with patch("cleanup_executor.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_cleanup_candidates(db_path="test", category="burst_leftovers")

        assert result["summary"]["count"] >= 1
        filenames = [c["filename"] for c in result["candidates"]]
        assert "IMG_004.heic" in filenames
        conn.close()

    def test_get_candidates_duplicates(self):
        """Test getting duplicate candidates."""
        from cleanup_executor import get_cleanup_candidates

        conn = create_full_test_db()

        with patch("cleanup_executor.PhotosDB") as mock_db:
            mock_db.return_value.__enter__ = MagicMock(return_value=conn)
            mock_db.return_value.__exit__ = MagicMock(return_value=False)
            result = get_cleanup_candidates(db_path="test", category="duplicates")

        assert result["summary"]["count"] >= 1
        filenames = [c["filename"] for c in result["candidates"]]
        assert "IMG_006.heic" in filenames
        conn.close()

    def test_generate_applescript(self):
        """Test AppleScript generation."""
        from cleanup_executor import generate_trash_applescript

        script = generate_trash_applescript(["IMG_001.jpg", "IMG_002.jpg"])
        assert 'tell application "Photos"' in script
        assert "IMG_001.jpg" in script
        assert "IMG_002.jpg" in script
        assert "delete" in script

    def test_dry_run(self):
        """Test dry run mode."""
        from cleanup_executor import execute_cleanup

        candidates = [
            {"id": 1, "filename": "test.jpg", "size": 1000},
            {"id": 2, "filename": "test2.jpg", "size": 2000},
        ]
        result = execute_cleanup(candidates, dry_run=True)
        assert result["dry_run"] is True
        assert "DRY RUN" in result["message"]
        assert result["success_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
