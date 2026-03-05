#!/usr/bin/env python3
"""
Tests for original scripts that had 0% coverage:
  library_analysis, junk_finder, duplicate_finder,
  storage_analyzer, timeline_recap, smart_export.

Uses in-memory SQLite databases with sample data.
"""

import sqlite3
from datetime import datetime
from unittest.mock import patch

import pytest

from _common import datetime_to_coredata

# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def rich_db():
    """
    In-memory database with diverse data suitable for all original scripts.

    Assets:
      1 - High-quality favorite photo with location, person, scene (2024-06-15 10:00)
      2 - Screenshot, old (2024-01-10 09:00)
      3 - Low-quality photo (2025-02-15 08:00)
      4 - Burst leftover (2025-03-01 16:00)
      5 - Video with location (2025-03-01 16:30)
      6 - Apple-detected duplicate photo (2025-01-15 12:00)
      7 - Trashed photo (excluded)
      8 - Second duplicate (same timestamp+dimensions as 6) (2025-01-15 12:00)
      9 - Normal photo (2025-06-20 14:00)
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
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
    c.execute("""
        CREATE TABLE ZADDITIONALASSETATTRIBUTES (
            ZASSET INTEGER,
            ZORIGINALFILESIZE INTEGER,
            ZORIGINALWIDTH INTEGER,
            ZORIGINALHEIGHT INTEGER
        )
    """)
    c.execute("""
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
    c.execute("""
        CREATE TABLE ZPERSON (
            Z_PK INTEGER PRIMARY KEY,
            ZFULLNAME TEXT,
            ZFACECOUNT INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE ZDETECTEDFACE (
            ZASSET INTEGER,
            ZPERSON INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE ZSCENECLASSIFICATION (
            ZASSET INTEGER,
            ZSCENENAME TEXT,
            ZCONFIDENCE REAL
        )
    """)
    c.execute("""
        CREATE TABLE ZGENERICALBUM (
            Z_PK INTEGER PRIMARY KEY,
            ZTITLE TEXT,
            ZKIND INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE Z_27ASSETS (
            Z_27ALBUMS INTEGER,
            Z_3ASSETS INTEGER
        )
    """)

    # People
    c.execute("INSERT INTO ZPERSON VALUES (1, 'Alice', 50)")
    c.execute("INSERT INTO ZPERSON VALUES (2, 'Bob', 30)")

    # Albums
    c.execute("INSERT INTO ZGENERICALBUM VALUES (1, 'Summer Trip', 2)")

    # Asset 1: high-quality favorite
    ts1 = datetime_to_coredata(datetime(2024, 6, 15, 10, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (1,'IMG_001.heic',?,4032,3024,0,0,1,0,0,48.8566,2.3522,0,NULL,0,'public.heic')",
        (ts1,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (1,5000000,4032,3024)")
    c.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (1,0.05,0.1,0.95,0.9,0.8,0.85,0.7,0.6,0.88)")
    c.execute("INSERT INTO ZDETECTEDFACE VALUES (1,1)")
    c.execute("INSERT INTO ZDETECTEDFACE VALUES (1,2)")
    c.execute("INSERT INTO ZSCENECLASSIFICATION VALUES (1,'beach',0.9)")
    c.execute("INSERT INTO Z_27ASSETS VALUES (1,1)")

    # Asset 2: old screenshot
    ts2 = datetime_to_coredata(datetime(2024, 1, 10, 9, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (2,'Screenshot.png',?,1920,1080,0,1,0,0,0,NULL,NULL,0,NULL,0,'public.png')",
        (ts2,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (2,2000000,1920,1080)")

    # Asset 3: low-quality photo
    ts3 = datetime_to_coredata(datetime(2025, 2, 15, 8, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (3,'IMG_003.jpg',?,1024,768,0,0,0,0,0,NULL,NULL,0,NULL,0,'public.jpeg')",
        (ts3,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (3,500000,1024,768)")
    c.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (3,0.8,0.7,0.2,0.15,0.1,0.1,0.1,0.1,0.1)")

    # Asset 4: burst leftover
    ts4 = datetime_to_coredata(datetime(2025, 3, 1, 16, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (4,'IMG_004.heic',?,4032,3024,0,0,0,0,0,48.8566,2.3522,2,0,0,'public.heic')",
        (ts4,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (4,4000000,4032,3024)")
    c.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (4,0.3,0.4,0.6,0.5,0.4,0.4,0.4,0.3,0.5)")

    # Asset 5: video
    ts5 = datetime_to_coredata(datetime(2025, 3, 1, 16, 30, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (5,'VID_001.mov',?,1920,1080,1,0,0,0,0,48.8566,2.3522,0,NULL,0,'com.apple.quicktime-movie')",
        (ts5,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (5,50000000,1920,1080)")

    # Asset 6: apple-detected duplicate
    ts6 = datetime_to_coredata(datetime(2025, 1, 15, 12, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (6,'IMG_006.heic',?,4032,3024,0,0,0,0,0,NULL,NULL,0,NULL,2,'public.heic')",
        (ts6,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (6,4800000,4032,3024)")
    c.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (6,0.2,0.2,0.7,0.7,0.5,0.5,0.5,0.4,0.5)")

    # Asset 7: trashed
    ts7 = datetime_to_coredata(datetime(2025, 3, 2, 10, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (7,'IMG_007.heic',?,4032,3024,0,0,0,0,1,NULL,NULL,0,NULL,0,'public.heic')",
        (ts7,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (7,3000000,4032,3024)")

    # Asset 8: second duplicate (same visibility state as 6, same timestamp+dimensions)
    ts8 = datetime_to_coredata(datetime(2025, 1, 15, 12, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (8,'IMG_008.heic',?,4032,3024,0,0,0,0,0,NULL,NULL,0,NULL,2,'public.heic')",
        (ts8,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (8,4700000,4032,3024)")
    c.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (8,0.25,0.25,0.65,0.65,0.5,0.5,0.5,0.4,0.5)")

    # Asset 9: normal photo
    ts9 = datetime_to_coredata(datetime(2025, 6, 20, 14, 0, 0))
    c.execute(
        "INSERT INTO ZASSET VALUES (9,'IMG_009.heic',?,4032,3024,0,0,0,0,0,42.0,-91.0,0,NULL,0,'public.heic')",
        (ts9,),
    )
    c.execute("INSERT INTO ZADDITIONALASSETATTRIBUTES VALUES (9,4200000,4032,3024)")
    c.execute("INSERT INTO ZCOMPUTEDASSETATTRIBUTES VALUES (9,0.15,0.2,0.8,0.75,0.6,0.6,0.55,0.5,0.7)")
    c.execute("INSERT INTO ZDETECTEDFACE VALUES (9,1)")
    c.execute("INSERT INTO ZSCENECLASSIFICATION VALUES (9,'park',0.7)")

    conn.commit()
    yield conn
    conn.close()


# ── Library Analysis ─────────────────────────────────────────────────────────


class TestLibraryAnalysis:
    """Tests for library_analysis.py."""

    def test_analyze_library(self, rich_db):
        from library_analysis import analyze_library

        with patch("library_analysis.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_library()

        summary = result["summary"]
        # 8 non-trashed assets
        assert summary["total_assets"] == 8
        assert summary["total_storage"] > 0
        assert summary["total_storage_formatted"]
        assert summary["min_date"] is not None
        assert summary["max_date"] is not None

    def test_by_type_counts(self, rich_db):
        from library_analysis import analyze_library

        with patch("library_analysis.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_library()

        by_type = result["by_type"]
        assert by_type["screenshots"] == 1
        assert by_type["favorites"] == 1
        assert by_type["hidden"] == 0
        assert by_type.get("photo", 0) >= 1
        assert by_type.get("video", 0) >= 1

    def test_by_year(self, rich_db):
        from library_analysis import analyze_library

        with patch("library_analysis.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_library()

        assert "2024" in result["by_year"]
        assert "2025" in result["by_year"]

    def test_top_people(self, rich_db):
        from library_analysis import analyze_library

        with patch("library_analysis.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_library()

        assert len(result["top_people"]) >= 1
        assert result["top_people"][0]["name"] == "Alice"

    def test_quality_distribution(self, rich_db):
        from library_analysis import analyze_library

        with patch("library_analysis.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_library()

        q = result["quality_distribution"]
        assert q is not None
        assert q["min"] < q["max"]
        assert q["sample_size"] > 0

    def test_format_summary(self, rich_db):
        from library_analysis import analyze_library, format_summary

        with patch("library_analysis.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_library()

        text = format_summary(result)
        assert "APPLE PHOTOS LIBRARY ANALYSIS" in text
        assert "Total Assets" in text
        assert "By Year" in text


# ── Junk Finder ──────────────────────────────────────────────────────────────


class TestJunkFinder:
    """Tests for junk_finder.py."""

    def test_find_screenshots(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk()

        assert result["totals"]["screenshots"] == 1
        assert result["screenshots"][0]["filename"] == "Screenshot.png"

    def test_old_screenshots(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            # Use a very short age so the 2024 screenshot qualifies
            result = find_junk(screenshot_age_days=1)

        assert result["totals"]["old_screenshots"] >= 1

    def test_low_quality(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk(quality_threshold=0.4)

        assert result["totals"]["low_quality"] >= 1
        # Asset 3 has very low quality
        low_ids = [item["id"] for item in result["low_quality"]]
        assert 3 in low_ids

    def test_burst_leftovers(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk()

        assert result["totals"]["burst_leftovers"] >= 1
        burst_ids = [item["id"] for item in result["burst_leftovers"]]
        assert 4 in burst_ids

    def test_possible_duplicates(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk(include_duplicates=True)

        assert result["totals"]["possible_duplicates"] >= 1

    def test_no_duplicates_flag(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk(include_duplicates=False)

        assert result["totals"]["possible_duplicates"] == 0

    def test_estimated_savings(self, rich_db):
        from junk_finder import find_junk

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk()

        savings = result["estimated_savings"]
        assert savings["conservative"]["bytes"] >= 0
        assert savings["aggressive"]["bytes"] >= savings["conservative"]["bytes"]

    def test_format_summary(self, rich_db):
        from junk_finder import find_junk, format_summary

        with patch("junk_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_junk()

        text = format_summary(result)
        assert "JUNK FINDER RESULTS" in text
        assert "Estimated Savings" in text


# ── Duplicate Finder ─────────────────────────────────────────────────────────


class TestDuplicateFinder:
    """Tests for duplicate_finder.py."""

    def test_find_apple_duplicates(self, rich_db):
        from duplicate_finder import find_duplicates

        with patch("duplicate_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_duplicates()

        assert result["summary"]["total_groups"] >= 1
        assert result["summary"]["total_duplicates"] >= 2

    def test_recommended_keep(self, rich_db):
        from duplicate_finder import find_duplicates

        with patch("duplicate_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_duplicates()

        for group in result["duplicate_groups"]:
            keeps = [i for i in group["items"] if i["recommended_keep"]]
            assert len(keeps) == 1, "Exactly one item should be recommended to keep"

    def test_create_duplicate_group(self):
        from duplicate_finder import create_duplicate_group

        items = [
            {
                "Z_PK": 1,
                "ZFILENAME": "a.jpg",
                "ZDATECREATED": datetime_to_coredata(datetime(2025, 1, 1)),
                "ZORIGINALFILESIZE": 5000000,
                "ZWIDTH": 4032,
                "ZHEIGHT": 3024,
                "ZFAVORITE": 1,
                "ZISDETECTEDSCREENSHOT": 0,
                "ZFAILURESCORE": 0.1,
                "ZNOISESCORE": 0.1,
                "ZPLEASANTCOMPOSITIONSCORE": 0.9,
                "ZPLEASANTLIGHTINGSCORE": 0.8,
            },
            {
                "Z_PK": 2,
                "ZFILENAME": "b.jpg",
                "ZDATECREATED": datetime_to_coredata(datetime(2025, 1, 1)),
                "ZORIGINALFILESIZE": 4000000,
                "ZWIDTH": 4032,
                "ZHEIGHT": 3024,
                "ZFAVORITE": 0,
                "ZISDETECTEDSCREENSHOT": 0,
                "ZFAILURESCORE": 0.2,
                "ZNOISESCORE": 0.2,
                "ZPLEASANTCOMPOSITIONSCORE": 0.7,
                "ZPLEASANTLIGHTINGSCORE": 0.6,
            },
        ]
        group = create_duplicate_group(items, "test")
        assert group["detection_method"] == "test"
        assert group["recommended_keep_id"] == 1  # favorite wins

    def test_potential_savings(self, rich_db):
        from duplicate_finder import find_duplicates

        with patch("duplicate_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_duplicates()

        assert result["summary"]["potential_savings"] >= 0
        assert result["summary"]["can_delete"] >= 1

    def test_format_summary(self, rich_db):
        from duplicate_finder import find_duplicates, format_summary

        with patch("duplicate_finder.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = find_duplicates()

        text = format_summary(result)
        assert "DUPLICATE FINDER" in text
        assert "KEEP" in text or "duplicate groups" in text.lower()


# ── Storage Analyzer ─────────────────────────────────────────────────────────


class TestStorageAnalyzer:
    """Tests for storage_analyzer.py."""

    def test_analyze_storage(self, rich_db):
        from storage_analyzer import analyze_storage

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        assert result["summary"]["total_storage"] > 0
        assert result["summary"]["total_formatted"]

    def test_by_kind(self, rich_db):
        from storage_analyzer import analyze_storage

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        assert "photo" in result["by_kind"]
        assert "video" in result["by_kind"]
        # Video (50MB) should be largest by bytes
        assert result["by_kind"]["video"]["total_bytes"] >= result["by_kind"]["photo"]["total_bytes"]

    def test_by_year(self, rich_db):
        from storage_analyzer import analyze_storage

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        assert "2024" in result["by_year"]
        assert "2025" in result["by_year"]
        assert result["by_year"]["2025"]["count"] > 0

    def test_growth(self, rich_db):
        from storage_analyzer import analyze_storage

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        assert len(result["growth"]) >= 2
        # Cumulative should be non-decreasing
        for i in range(1, len(result["growth"])):
            assert result["growth"][i]["cumulative_bytes"] >= result["growth"][i - 1]["cumulative_bytes"]

    def test_storage_hogs(self, rich_db):
        from storage_analyzer import analyze_storage

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        assert len(result["storage_hogs"]) >= 1
        # Largest should be first (the 50MB video)
        assert result["storage_hogs"][0]["size"] >= result["storage_hogs"][-1]["size"]

    def test_by_file_type(self, rich_db):
        from storage_analyzer import analyze_storage

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        types = [ft["type"] for ft in result["by_file_type"]]
        assert "public.heic" in types

    def test_format_summary(self, rich_db):
        from storage_analyzer import analyze_storage, format_summary

        with patch("storage_analyzer.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_storage()

        text = format_summary(result)
        assert "STORAGE ANALYSIS" in text
        assert "By Type" in text


# ── Timeline Recap ───────────────────────────────────────────────────────────


class TestTimelineRecap:
    """Tests for timeline_recap.py."""

    def test_generate_timeline(self, rich_db):
        from timeline_recap import generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = generate_timeline()

        assert result["summary"]["total_photos"] >= 1
        assert result["summary"]["total_days"] >= 1
        assert result["summary"]["total_events"] >= 1
        assert len(result["timeline"]) >= 1

    def test_date_filter(self, rich_db):
        from timeline_recap import generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = generate_timeline(start_date="2025-03-01", end_date="2025-03-01")

        # Should get the March 1 assets (burst + video)
        assert result["summary"]["total_photos"] >= 1

    def test_date_filter_no_results(self, rich_db):
        from timeline_recap import generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = generate_timeline(start_date="2030-01-01", end_date="2030-12-31")

        assert result["summary"]["total_photos"] == 0
        assert result["timeline"] == []

    def test_event_clustering(self, rich_db):
        from timeline_recap import generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            # Assets 4 and 5 are 30min apart on same day → same event
            result = generate_timeline(start_date="2025-03-01", end_date="2025-03-01", cluster_hours=4)

        for day in result["timeline"]:
            if day["date"] == "2025-03-01":
                # Both should be in one event (30min gap < 4hrs)
                assert day["events"][0]["photo_count"] >= 2

    def test_event_has_people_and_scenes(self, rich_db):
        from timeline_recap import generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = generate_timeline(start_date="2024-06-15", end_date="2024-06-15")

        day = result["timeline"][0]
        event = day["events"][0]
        assert event["photo_count"] >= 1
        # Person data should exist (Alice and Bob on asset 1)
        assert "people" in event

    def test_event_location(self, rich_db):
        from timeline_recap import generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = generate_timeline(start_date="2024-06-15", end_date="2024-06-15")

        event = result["timeline"][0]["events"][0]
        assert event["location"]["has_location"] is True

    def test_format_narrative(self, rich_db):
        from timeline_recap import format_narrative, generate_timeline

        with patch("timeline_recap.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = generate_timeline(start_date="2024-06-15", end_date="2025-06-20")

        text = format_narrative(result)
        assert "PHOTO TIMELINE RECAP" in text
        assert "photos" in text

    def test_format_event(self):
        from timeline_recap import format_event

        event = {
            "start_time": datetime(2025, 3, 1, 10, 0),
            "end_time": datetime(2025, 3, 1, 11, 30),
            "photo_count": 15,
            "video_count": 2,
            "favorites": 3,
            "people": [{"name": "Alice", "count": 5}],
            "scenes": [{"scene": "beach", "count": 10}],
            "location": {"has_location": True, "latitude": 48.85, "longitude": 2.35},
        }
        formatted = format_event(event)
        assert formatted["time"] == "10:00"
        assert formatted["duration_minutes"] == 90
        assert formatted["photo_count"] == 15


# ── Smart Export ─────────────────────────────────────────────────────────────


class TestSmartExport:
    """Tests for smart_export.py."""

    def test_generate_export_plan_year_month(self, rich_db):
        from smart_export import generate_export_plan

        with patch("smart_export.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            plan = generate_export_plan(organize_by="year_month")

        assert plan["summary"]["total_photos"] >= 1
        assert plan["summary"]["folder_count"] >= 1
        assert plan["organize_by"] == "year_month"
        # Should have at least a 2024 and 2025 folder
        folder_keys = list(plan["folders"].keys())
        assert any("2024" in k for k in folder_keys)
        assert any("2025" in k for k in folder_keys)

    def test_generate_export_plan_favorites(self, rich_db):
        from smart_export import generate_export_plan

        with patch("smart_export.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            plan = generate_export_plan(favorites_only=True)

        # Only asset 1 is favorited
        assert plan["summary"]["total_photos"] == 1

    def test_generate_export_plan_date_range(self, rich_db):
        from smart_export import generate_export_plan

        with patch("smart_export.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            plan = generate_export_plan(start_date="2025-01-01", end_date="2025-12-31")

        # All 2025 assets (3,4,5,6,8,9)
        assert plan["summary"]["total_photos"] >= 5

    def test_generate_export_plan_person(self, rich_db):
        from smart_export import generate_export_plan

        with patch("smart_export.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            plan = generate_export_plan(organize_by="person", person_name="Alice")

        # Alice appears in assets 1 and 9
        assert plan["summary"]["total_photos"] >= 1

    def test_generate_export_plan_location(self, rich_db):
        from smart_export import generate_export_plan

        with patch("smart_export.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            plan = generate_export_plan(organize_by="location")

        assert "no_location" in plan["folders"] or any("loc_" in k for k in plan["folders"])

    def test_export_with_applescript(self, tmp_path):
        """Test AppleScript generation (mocked execution)."""
        from smart_export import export_with_applescript

        with patch("smart_export.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = export_with_applescript(["IMG_001.heic"], str(tmp_path), "2025")

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0][0] == "osascript"

    def test_export_with_applescript_failure(self, tmp_path):
        from smart_export import export_with_applescript

        with patch("smart_export.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "error"
            result = export_with_applescript(["test.jpg"], str(tmp_path))

        assert result is False


# ── Cleanup Executor (improve coverage) ──────────────────────────────────────


class TestCleanupExecutorExtended:
    """Additional tests for cleanup_executor.py to increase coverage."""

    def test_low_quality_candidates(self, rich_db):
        from cleanup_executor import get_cleanup_candidates

        with patch("cleanup_executor.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = get_cleanup_candidates(category="low_quality", quality_threshold=0.4)

        assert result["summary"]["category"] == "low_quality"
        assert result["summary"]["count"] >= 1

    def test_all_screenshots_candidates(self, rich_db):
        from cleanup_executor import get_cleanup_candidates

        with patch("cleanup_executor.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = get_cleanup_candidates(category="all_screenshots")

        assert result["summary"]["category"] == "all_screenshots"
        assert result["summary"]["count"] >= 1

    def test_execute_cleanup_dry_run(self):
        from cleanup_executor import execute_cleanup

        candidates = [
            {"filename": "test.jpg", "size": 1000},
            {"filename": "test2.jpg", "size": 2000},
        ]
        result = execute_cleanup(candidates, dry_run=True)
        assert result["dry_run"] is True
        assert "DRY RUN" in result["message"]

    def test_execute_cleanup_real(self):
        from cleanup_executor import execute_cleanup

        candidates = [{"filename": "test.jpg", "size": 1000}]
        with patch("cleanup_executor.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "1 items moved to Recently Deleted"
            result = execute_cleanup(candidates, dry_run=False, batch_size=50)

        assert result["dry_run"] is False
        assert result["success_count"] == 1

    def test_execute_cleanup_error(self):
        from cleanup_executor import execute_cleanup

        candidates = [{"filename": "test.jpg", "size": 1000}]
        with patch("cleanup_executor.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "AppleScript error"
            result = execute_cleanup(candidates, dry_run=False)

        assert len(result["errors"]) >= 1

    def test_execute_cleanup_timeout(self):
        import subprocess as sp

        from cleanup_executor import execute_cleanup

        candidates = [{"filename": "test.jpg", "size": 1000}]
        with patch("cleanup_executor.subprocess.run") as mock_run:
            mock_run.side_effect = sp.TimeoutExpired("osascript", 120)
            result = execute_cleanup(candidates, dry_run=False)

        assert any("timed out" in e for e in result["errors"])

    def test_format_summary_candidates(self, rich_db):
        from cleanup_executor import format_summary, get_cleanup_candidates

        with patch("cleanup_executor.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            data = get_cleanup_candidates(category="burst_leftovers")

        text = format_summary(data)
        assert "CLEANUP EXECUTOR" in text

    def test_format_summary_results(self):
        from cleanup_executor import format_summary

        result_data = {
            "message": "Processed 5/5 items.",
            "errors": ["Batch 2: error"],
        }
        text = format_summary(result_data)
        assert "Processed" in text
        assert "error" in text.lower()


# ── Scene Search (improve coverage) ──────────────────────────────────────────


class TestSceneSearchExtended:
    """Additional tests for scene_search.py to increase coverage."""

    def test_inventory_mode(self, rich_db):
        from scene_search import search_scenes

        with patch("scene_search.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = search_scenes(search_term=None)

        assert result["mode"] == "inventory"
        assert result["summary"]["total_scenes"] >= 1
        assert result["summary"]["total_photos"] > 0

    def test_search_mode(self, rich_db):
        from scene_search import search_scenes

        with patch("scene_search.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = search_scenes(search_term="beach")

        assert result["mode"] == "search"
        assert result["summary"]["total_matches"] >= 1
        assert result["results"][0]["scene"] == "beach"

    def test_search_no_results(self, rich_db):
        from scene_search import search_scenes

        with patch("scene_search.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = search_scenes(search_term="zzz_nonexistent")

        assert result["summary"]["total_matches"] == 0

    def test_related_scenes(self, rich_db):
        from scene_search import search_scenes

        with patch("scene_search.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = search_scenes(search_term="beach")

        # beach appears on asset 1 which also has 'outdoor' classification
        # (not in this fixture, but related_scenes should at least be a list)
        assert isinstance(result["related_scenes"], list)

    def test_format_summary_search(self, rich_db):
        from scene_search import format_summary, search_scenes

        with patch("scene_search.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = search_scenes(search_term="beach")

        text = format_summary(result)
        assert "SCENE" in text
        assert "beach" in text.lower()

    def test_format_summary_inventory(self, rich_db):
        from scene_search import format_summary, search_scenes

        with patch("scene_search.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = search_scenes(search_term=None)

        text = format_summary(result)
        assert "SCENE" in text
        assert "scene labels" in text.lower() or "inventory" in text.lower()


# ── Photo Habits (improve coverage) ──────────────────────────────────────────


class TestPhotoHabitsExtended:
    """Additional tests for photo_habits.py to increase coverage."""

    def test_analyze_habits_full(self, rich_db):
        from photo_habits import analyze_habits

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits()

        s = result["summary"]
        assert s["total_photos"] >= 1
        assert s["total_videos"] >= 1
        assert s["total_screenshots"] >= 1
        assert s["peak_hour"] is not None
        assert s["peak_day"] is not None
        assert s["peak_month"] is not None
        assert s["busiest_day"] is not None

    def test_time_of_day(self, rich_db):
        from photo_habits import analyze_habits

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits()

        tod = result["time_of_day"]
        total = sum(v["count"] for v in tod.values())
        assert total > 0
        assert "morning" in tod
        assert "afternoon" in tod
        assert "evening" in tod
        assert "night" in tod

    def test_year_filter(self, rich_db):
        from photo_habits import analyze_habits

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits(year="2025")

        # Should only include 2025 data
        for yt in result["yearly_trend"]:
            assert yt["year"] == "2025"

    def test_streaks(self, rich_db):
        from photo_habits import analyze_habits

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits()

        st = result["streaks"]
        assert st["max_days"] >= 1
        assert st["total_active_days"] >= 1

    def test_monthly_trend(self, rich_db):
        from photo_habits import analyze_habits

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits()

        assert len(result["monthly_trend"]) >= 1
        for mt in result["monthly_trend"]:
            assert mt["total"] >= 1
            assert "size_formatted" in mt

    def test_yearly_trend(self, rich_db):
        from photo_habits import analyze_habits

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits()

        assert len(result["yearly_trend"]) >= 1
        for yt in result["yearly_trend"]:
            assert "video_ratio" in yt

    def test_format_summary(self, rich_db):
        from photo_habits import analyze_habits, format_summary

        with patch("photo_habits.PhotosDB") as mock_cls:
            mock_cls.return_value.__enter__ = lambda s: rich_db
            mock_cls.return_value.__exit__ = lambda s, *a: None
            result = analyze_habits()

        text = format_summary(result)
        assert "PHOTO HABITS" in text
        assert "When You Shoot" in text
        assert "Streaks" in text or "Day of Week" in text


# ── Common module (improve coverage) ─────────────────────────────────────────


class TestCommonExtended:
    """Additional tests for _common.py to increase coverage."""

    def test_find_photos_db_custom_sqlite_path(self, tmp_path):
        from _common import find_photos_db

        db_file = tmp_path / "Test.sqlite"
        db_file.touch()
        result = find_photos_db(str(db_file))
        assert result == str(db_file)

    def test_find_photos_db_library_path(self, tmp_path):
        from _common import find_photos_db

        lib = tmp_path / "Test.photoslibrary" / "database"
        lib.mkdir(parents=True)
        (lib / "Photos.sqlite").touch()
        result = find_photos_db(str(tmp_path / "Test.photoslibrary"))
        assert "Photos.sqlite" in result

    def test_find_photos_db_not_found(self):
        from _common import find_photos_db

        # Pass a path that doesn't end with .sqlite or .photoslibrary
        # and mock the default path to not exist
        with patch("_common.os.path.exists", return_value=False), pytest.raises(FileNotFoundError):
            find_photos_db("/nonexistent/library")

    def test_photos_db_context_manager(self, tmp_path):
        """Test PhotosDB with a real file (not read-only for test)."""
        from _common import PhotosDB

        db_file = tmp_path / "test.sqlite"
        # Create a real SQLite file so connect_db can open it
        conn = sqlite3.connect(str(db_file))
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()

        with PhotosDB(db_path=str(db_file)) as conn2:
            assert conn2 is not None

    def test_output_json_to_file(self, tmp_path):
        from _common import output_json

        out = tmp_path / "test.json"
        output_json({"key": "value"}, str(out))
        assert out.exists()
        import json

        data = json.loads(out.read_text())
        assert data["key"] == "value"

    def test_build_asset_query_all_options(self):
        from _common import build_asset_query

        query = build_asset_query(
            where_clauses=["a.ZTRASHEDSTATE != 1"],
            join_additional=True,
            join_computed=True,
            order_by="a.ZDATECREATED",
            limit=10,
        )
        assert "ZADDITIONALASSETATTRIBUTES" in query
        assert "ZCOMPUTEDASSETATTRIBUTES" in query
        assert "LIMIT 10" in query
        assert "ORDER BY" in query

    def test_format_date_range_edge_cases(self):
        from _common import format_date_range

        assert format_date_range(None, None) == "Unknown"
        assert "Until" in format_date_range(None, datetime(2025, 1, 1))
        assert "From" in format_date_range(datetime(2025, 1, 1), None)
        # Same date
        d = datetime(2025, 6, 15)
        assert format_date_range(d, d) == "2025-06-15"
