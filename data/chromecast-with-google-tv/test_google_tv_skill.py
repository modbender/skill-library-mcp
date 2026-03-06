#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Unit tests for google_tv_skill.py

Run with: uv run test_google_tv_skill.py
or:       python3 -m pytest test_google_tv_skill.py (if pytest installed)
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import functions to test
import sys
sys.path.insert(0, str(Path(__file__).parent))
from google_tv_skill import (
    extract_youtube_id,
    is_youtube_id,
    looks_like_tubi,
    connection_refused,
    load_cache,
    save_cache,
    youtube_package,
    tubi_package,
    find_video_id,
    adb_pair,
)


class TestADBPairing(unittest.TestCase):
    """Test ADB pairing functionality."""

    @patch('google_tv_skill.subprocess.run')
    def test_adb_pair_success(self, mock_run):
        """Test successful ADB pairing."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Successfully paired to 192.168.1.100:12345"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, output = adb_pair("192.168.1.100", 12345, "123456")

        self.assertTrue(success)
        self.assertIn("successfully paired", output.lower())
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "adb")
        self.assertEqual(args[1], "pair")
        self.assertEqual(args[2], "192.168.1.100:12345")
        self.assertEqual(args[3], "123456")

    @patch('google_tv_skill.subprocess.run')
    def test_adb_pair_failure(self, mock_run):
        """Test failed ADB pairing."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Failed to pair: invalid code"
        mock_run.return_value = mock_result

        success, output = adb_pair("192.168.1.100", 12345, "999999")

        self.assertFalse(success)
        self.assertIn("invalid code", output.lower())

    @patch('google_tv_skill.subprocess.run')
    def test_adb_pair_timeout(self, mock_run):
        """Test ADB pairing timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired('adb', 10)

        success, output = adb_pair("192.168.1.100", 12345, "123456")

        self.assertFalse(success)
        self.assertIn("timed out", output.lower())

    @patch('google_tv_skill.subprocess.run')
    def test_adb_pair_adb_not_found(self, mock_run):
        """Test ADB pairing when adb binary not found."""
        mock_run.side_effect = FileNotFoundError()

        success, output = adb_pair("192.168.1.100", 12345, "123456")

        self.assertFalse(success)
        self.assertEqual(output, 'adb not found on PATH')


class TestYouTubeIDExtraction(unittest.TestCase):
    """Test YouTube ID and URL extraction logic."""

    def test_direct_youtube_id(self):
        """Test extraction of direct 11-char YouTube ID."""
        vid = "7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(vid), vid)

    def test_youtube_url_watch_format(self):
        """Test extraction from youtube.com/watch?v=ID format."""
        url = "https://www.youtube.com/watch?v=7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(url), "7m714Ls29ZA")

    def test_youtube_short_url(self):
        """Test extraction from youtu.be short URL."""
        url = "https://youtu.be/7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(url), "7m714Ls29ZA")

    def test_youtube_shorts_url(self):
        """Test extraction from /shorts/ path."""
        url = "https://www.youtube.com/shorts/7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(url), "7m714Ls29ZA")

    def test_youtube_live_url(self):
        """Test extraction from /live/ path."""
        url = "https://www.youtube.com/live/7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(url), "7m714Ls29ZA")

    def test_youtube_embed_url(self):
        """Test extraction from /embed/ path."""
        url = "https://www.youtube.com/embed/7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(url), "7m714Ls29ZA")

    def test_youtube_fragment_url(self):
        """Test extraction from fragment-based URL (#watch?v=ID)."""
        url = "https://www.youtube.com#watch?v=7m714Ls29ZA"
        self.assertEqual(extract_youtube_id(url), "7m714Ls29ZA")

    def test_youtube_id_no_scheme(self):
        """Test that URL without scheme returns None."""
        url = "www.youtube.com/watch?v=7m714Ls29ZA"
        self.assertIsNone(extract_youtube_id(url))

    def test_invalid_youtube_url(self):
        """Test that invalid YouTube URLs return None."""
        self.assertIsNone(extract_youtube_id("https://www.youtube.com/blah"))
        self.assertIsNone(extract_youtube_id("not a url"))

    def test_empty_input(self):
        """Test that empty input returns None."""
        self.assertIsNone(extract_youtube_id(""))
        self.assertIsNone(extract_youtube_id(None))

    def test_short_id_too_short(self):
        """Test that IDs shorter than 6 chars are rejected."""
        self.assertFalse(is_youtube_id("abc12"))


class TestYouTubeIDValidation(unittest.TestCase):
    """Test YouTube ID validation logic."""

    def test_valid_id_11_chars(self):
        """Test valid 11-char ID."""
        self.assertTrue(is_youtube_id("7m714Ls29ZA"))

    def test_valid_id_6_chars(self):
        """Test valid 6-char ID (minimum)."""
        self.assertTrue(is_youtube_id("abc123"))

    def test_valid_id_with_underscore(self):
        """Test valid ID with underscore."""
        self.assertTrue(is_youtube_id("abc_123"))

    def test_valid_id_with_hyphen(self):
        """Test valid ID with hyphen."""
        self.assertTrue(is_youtube_id("abc-123"))

    def test_invalid_id_too_short(self):
        """Test that IDs < 6 chars are invalid."""
        self.assertFalse(is_youtube_id("abc12"))

    def test_invalid_id_special_chars(self):
        """Test that special characters make ID invalid."""
        self.assertFalse(is_youtube_id("abc!@#$"))

    def test_invalid_id_empty(self):
        """Test that empty string is invalid."""
        self.assertFalse(is_youtube_id(""))


class TestTubiDetection(unittest.TestCase):
    """Test Tubi URL detection logic."""

    def test_tubi_https_url(self):
        """Test detection of Tubi https URL."""
        self.assertTrue(looks_like_tubi("https://www.tubitv.com/movies/123"))
        self.assertTrue(looks_like_tubi("https://tubitv.com/movies/123"))

    def test_tubi_without_https(self):
        """Test detection of Tubi URL without https."""
        self.assertTrue(looks_like_tubi("www.tubitv.com/movies/123"))
        self.assertTrue(looks_like_tubi("tubitv.com/movies/123"))

    def test_tubi_partial_match(self):
        """Test that partial 'tubitv.com' in string is detected."""
        self.assertTrue(looks_like_tubi("watch on tubitv.com here"))

    def test_non_tubi_url(self):
        """Test that non-Tubi URLs are rejected."""
        self.assertFalse(looks_like_tubi("https://youtube.com"))
        self.assertFalse(looks_like_tubi("https://hulu.com"))

    def test_empty_tubi_input(self):
        """Test that empty input returns False."""
        self.assertFalse(looks_like_tubi(""))
        self.assertFalse(looks_like_tubi(None))

    def test_tubi_case_insensitive(self):
        """Test that Tubi detection is case-insensitive."""
        self.assertTrue(looks_like_tubi("HTTPS://WWW.TUBITV.COM/"))


class TestConnectionRefusedDetection(unittest.TestCase):
    """Test connection refused detection logic."""

    def test_connection_refused_exact(self):
        """Test detection of 'connection refused' message."""
        self.assertTrue(connection_refused("connection refused"))

    def test_refused_keyword(self):
        """Test detection of 'refused' keyword."""
        self.assertTrue(connection_refused("adb: unable to connect to 192.168.1.1:5555: refused"))

    def test_failed_to_connect(self):
        """Test detection of 'failed to connect' message."""
        self.assertTrue(connection_refused("failed to connect to device"))

    def test_cannot_connect(self):
        """Test detection of 'cannot connect' message."""
        self.assertTrue(connection_refused("cannot connect to device"))

    def test_case_insensitive(self):
        """Test that detection is case-insensitive."""
        self.assertTrue(connection_refused("CONNECTION REFUSED"))
        self.assertTrue(connection_refused("Failed To Connect"))

    def test_not_connection_refused(self):
        """Test that other errors are not detected as refused."""
        self.assertFalse(connection_refused("timeout"))
        self.assertFalse(connection_refused("device offline"))
        self.assertFalse(connection_refused(""))


class TestCacheOperations(unittest.TestCase):
    """Test cache file operations."""

    def setUp(self):
        """Create temporary directory for cache testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_file = Path(self.temp_dir.name) / '.last_device.json'

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_save_and_load_cache(self):
        """Test saving and loading cache."""
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            save_cache("192.168.4.64", 5555)
            cache = load_cache()
            self.assertIsNotNone(cache)
            self.assertEqual(cache['ip'], "192.168.4.64")
            self.assertEqual(cache['port'], 5555)

    def test_load_cache_nonexistent(self):
        """Test loading cache when file doesn't exist."""
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)

    def test_load_cache_invalid_json(self):
        """Test loading cache with invalid JSON."""
        self.cache_file.write_text("not json")
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)

    def test_load_cache_missing_fields(self):
        """Test loading cache with missing required fields."""
        self.cache_file.write_text(json.dumps({"ip": "192.168.4.64"}))
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)

    def test_load_cache_invalid_port(self):
        """Test loading cache with non-integer port."""
        self.cache_file.write_text(json.dumps({"ip": "192.168.4.64", "port": "not-a-number"}))
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)


class TestPackageNames(unittest.TestCase):
    """Test package name resolution from environment."""

    def test_youtube_package_default(self):
        """Test default YouTube package."""
        with patch.dict(os.environ, {}, clear=True):
            pkg = youtube_package()
            self.assertEqual(pkg, "com.google.android.youtube.tv")

    def test_youtube_package_override(self):
        """Test YouTube package from YOUTUBE_PACKAGE env."""
        with patch.dict(os.environ, {"YOUTUBE_PACKAGE": "com.custom.youtube"}):
            pkg = youtube_package()
            self.assertEqual(pkg, "com.custom.youtube")

    def test_youtube_package_strips_whitespace(self):
        """Test that package name whitespace is stripped."""
        with patch.dict(os.environ, {"YOUTUBE_PACKAGE": "  com.custom.youtube  "}):
            pkg = youtube_package()
            self.assertEqual(pkg, "com.custom.youtube")

    def test_tubi_package_default(self):
        """Test default Tubi package."""
        with patch.dict(os.environ, {}, clear=True):
            pkg = tubi_package()
            self.assertEqual(pkg, "com.tubitv")

    def test_tubi_package_override(self):
        """Test Tubi package from TUBI_PACKAGE env."""
        with patch.dict(os.environ, {"TUBI_PACKAGE": "com.custom.tubi"}):
            pkg = tubi_package()
            self.assertEqual(pkg, "com.custom.tubi")


class TestVideoIDFinding(unittest.TestCase):
    """Test recursive video ID extraction from JSON-like structures."""

    def test_find_video_id_direct_key(self):
        """Test finding videoId in dict."""
        data = {"videoId": "7m714Ls29ZA", "title": "example"}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_underscore_key(self):
        """Test finding video_id in dict."""
        data = {"video_id": "7m714Ls29ZA"}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_nested_dict(self):
        """Test finding videoId in nested dict."""
        data = {"data": {"videoId": "7m714Ls29ZA"}}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_in_list(self):
        """Test finding videoId in list of dicts."""
        data = [{"title": "a"}, {"videoId": "7m714Ls29ZA"}]
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_not_found(self):
        """Test that None is returned when no videoId found."""
        data = {"title": "example", "url": "https://example.com"}
        self.assertIsNone(find_video_id(data))

    def test_find_video_id_ignores_invalid_ids(self):
        """Test that invalid IDs are skipped."""
        data = {"videoId": "abc", "id": "7m714Ls29ZA"}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_empty_structures(self):
        """Test with empty structures."""
        self.assertIsNone(find_video_id({}))
        self.assertIsNone(find_video_id([]))


if __name__ == '__main__':
    unittest.main()


class TestYouTubeIDValidation(unittest.TestCase):
    """Test YouTube ID validation logic."""

    def test_valid_id_11_chars(self):
        """Test valid 11-char ID."""
        self.assertTrue(is_youtube_id("7m714Ls29ZA"))

    def test_valid_id_6_chars(self):
        """Test valid 6-char ID (minimum)."""
        self.assertTrue(is_youtube_id("abc123"))

    def test_valid_id_with_underscore(self):
        """Test valid ID with underscore."""
        self.assertTrue(is_youtube_id("abc_123"))

    def test_valid_id_with_hyphen(self):
        """Test valid ID with hyphen."""
        self.assertTrue(is_youtube_id("abc-123"))

    def test_invalid_id_too_short(self):
        """Test that IDs < 6 chars are invalid."""
        self.assertFalse(is_youtube_id("abc12"))

    def test_invalid_id_special_chars(self):
        """Test that special characters make ID invalid."""
        self.assertFalse(is_youtube_id("abc!@#$"))

    def test_invalid_id_empty(self):
        """Test that empty string is invalid."""
        self.assertFalse(is_youtube_id(""))


class TestTubiDetection(unittest.TestCase):
    """Test Tubi URL detection logic."""

    def test_tubi_https_url(self):
        """Test detection of Tubi https URL."""
        self.assertTrue(looks_like_tubi("https://www.tubitv.com/movies/123"))
        self.assertTrue(looks_like_tubi("https://tubitv.com/movies/123"))

    def test_tubi_without_https(self):
        """Test detection of Tubi URL without https."""
        self.assertTrue(looks_like_tubi("www.tubitv.com/movies/123"))
        self.assertTrue(looks_like_tubi("tubitv.com/movies/123"))

    def test_tubi_partial_match(self):
        """Test that partial 'tubitv.com' in string is detected."""
        self.assertTrue(looks_like_tubi("watch on tubitv.com here"))

    def test_non_tubi_url(self):
        """Test that non-Tubi URLs are rejected."""
        self.assertFalse(looks_like_tubi("https://youtube.com"))
        self.assertFalse(looks_like_tubi("https://hulu.com"))

    def test_empty_tubi_input(self):
        """Test that empty input returns False."""
        self.assertFalse(looks_like_tubi(""))
        self.assertFalse(looks_like_tubi(None))

    def test_tubi_case_insensitive(self):
        """Test that Tubi detection is case-insensitive."""
        self.assertTrue(looks_like_tubi("HTTPS://WWW.TUBITV.COM/"))


class TestConnectionRefusedDetection(unittest.TestCase):
    """Test connection refused detection logic."""

    def test_connection_refused_exact(self):
        """Test detection of 'connection refused' message."""
        self.assertTrue(connection_refused("connection refused"))

    def test_refused_keyword(self):
        """Test detection of 'refused' keyword."""
        self.assertTrue(connection_refused("adb: unable to connect to 192.168.1.1:5555: refused"))

    def test_failed_to_connect(self):
        """Test detection of 'failed to connect' message."""
        self.assertTrue(connection_refused("failed to connect to device"))

    def test_cannot_connect(self):
        """Test detection of 'cannot connect' message."""
        self.assertTrue(connection_refused("cannot connect to device"))

    def test_case_insensitive(self):
        """Test that detection is case-insensitive."""
        self.assertTrue(connection_refused("CONNECTION REFUSED"))
        self.assertTrue(connection_refused("Failed To Connect"))

    def test_not_connection_refused(self):
        """Test that other errors are not detected as refused."""
        self.assertFalse(connection_refused("timeout"))
        self.assertFalse(connection_refused("device offline"))
        self.assertFalse(connection_refused(""))


class TestCacheOperations(unittest.TestCase):
    """Test cache file operations."""

    def setUp(self):
        """Create temporary directory for cache testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_file = Path(self.temp_dir.name) / '.last_device.json'

    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_save_and_load_cache(self):
        """Test saving and loading cache."""
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            save_cache("192.168.4.64", 5555)
            cache = load_cache()
            self.assertIsNotNone(cache)
            self.assertEqual(cache['ip'], "192.168.4.64")
            self.assertEqual(cache['port'], 5555)

    def test_load_cache_nonexistent(self):
        """Test loading cache when file doesn't exist."""
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)

    def test_load_cache_invalid_json(self):
        """Test loading cache with invalid JSON."""
        self.cache_file.write_text("not json")
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)

    def test_load_cache_missing_fields(self):
        """Test loading cache with missing required fields."""
        self.cache_file.write_text(json.dumps({"ip": "192.168.4.64"}))
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)

    def test_load_cache_invalid_port(self):
        """Test loading cache with non-integer port."""
        self.cache_file.write_text(json.dumps({"ip": "192.168.4.64", "port": "not-a-number"}))
        with patch('google_tv_skill.CACHE_FILE', self.cache_file):
            cache = load_cache()
            self.assertIsNone(cache)


class TestPackageNames(unittest.TestCase):
    """Test package name resolution from environment."""

    def test_youtube_package_default(self):
        """Test default YouTube package."""
        with patch.dict(os.environ, {}, clear=True):
            pkg = youtube_package()
            self.assertEqual(pkg, "com.google.android.youtube.tv")

    def test_youtube_package_override(self):
        """Test YouTube package from YOUTUBE_PACKAGE env."""
        with patch.dict(os.environ, {"YOUTUBE_PACKAGE": "com.custom.youtube"}):
            pkg = youtube_package()
            self.assertEqual(pkg, "com.custom.youtube")

    def test_youtube_package_strips_whitespace(self):
        """Test that package name whitespace is stripped."""
        with patch.dict(os.environ, {"YOUTUBE_PACKAGE": "  com.custom.youtube  "}):
            pkg = youtube_package()
            self.assertEqual(pkg, "com.custom.youtube")

    def test_tubi_package_default(self):
        """Test default Tubi package."""
        with patch.dict(os.environ, {}, clear=True):
            pkg = tubi_package()
            self.assertEqual(pkg, "com.tubitv")

    def test_tubi_package_override(self):
        """Test Tubi package from TUBI_PACKAGE env."""
        with patch.dict(os.environ, {"TUBI_PACKAGE": "com.custom.tubi"}):
            pkg = tubi_package()
            self.assertEqual(pkg, "com.custom.tubi")


class TestVideoIDFinding(unittest.TestCase):
    """Test recursive video ID extraction from JSON-like structures."""

    def test_find_video_id_direct_key(self):
        """Test finding videoId in dict."""
        data = {"videoId": "7m714Ls29ZA", "title": "example"}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_underscore_key(self):
        """Test finding video_id in dict."""
        data = {"video_id": "7m714Ls29ZA"}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_nested_dict(self):
        """Test finding videoId in nested dict."""
        data = {"data": {"videoId": "7m714Ls29ZA"}}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_in_list(self):
        """Test finding videoId in list of dicts."""
        data = [{"title": "a"}, {"videoId": "7m714Ls29ZA"}]
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_not_found(self):
        """Test that None is returned when no videoId found."""
        data = {"title": "example", "url": "https://example.com"}
        self.assertIsNone(find_video_id(data))

    def test_find_video_id_ignores_invalid_ids(self):
        """Test that invalid IDs are skipped."""
        data = {"videoId": "abc", "id": "7m714Ls29ZA"}
        self.assertEqual(find_video_id(data), "7m714Ls29ZA")

    def test_find_video_id_empty_structures(self):
        """Test with empty structures."""
        self.assertIsNone(find_video_id({}))
        self.assertIsNone(find_video_id([]))


if __name__ == '__main__':
    unittest.main()
