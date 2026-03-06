#!/usr/bin/env python3
"""Unit tests for auto_review module.

Tests the core logic of package auto-review without making real API calls.
All external dependencies are mocked.
"""

import json
import sys
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import auto_review


class TestVersionParsing(unittest.TestCase):
    """Tests for version parsing functions."""
    
    def test_parse_version_standard(self):
        """Test parsing standard semver versions."""
        self.assertEqual(auto_review.parse_version("1.2.3"), (1, 2, 3))
        self.assertEqual(auto_review.parse_version("10.20.30"), (10, 20, 30))
    
    def test_parse_version_with_v_prefix(self):
        """Test parsing versions with v/V prefix."""
        self.assertEqual(auto_review.parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(auto_review.parse_version("V2.0.0"), (2, 0, 0))
    
    def test_parse_version_brew_style(self):
        """Test parsing brew-style versions with underscore."""
        self.assertEqual(auto_review.parse_version("1.3.1_1"), (1, 3, 1))
        self.assertEqual(auto_review.parse_version("2.0.0_5"), (2, 0, 0))
    
    def test_parse_version_partial(self):
        """Test parsing partial versions."""
        self.assertEqual(auto_review.parse_version("1.2"), (1, 2, 0))
        self.assertEqual(auto_review.parse_version("1"), (1, 0, 0))
    
    def test_parse_version_with_prerelease(self):
        """Test parsing versions with prerelease tags."""
        self.assertEqual(auto_review.parse_version("1.2.3-beta"), (1, 2, 3))
        self.assertEqual(auto_review.parse_version("2.0.0-alpha.1"), (2, 0, 0))
    
    def test_parse_version_invalid(self):
        """Test parsing invalid versions returns (0, 0, 0)."""
        self.assertEqual(auto_review.parse_version("invalid"), (0, 0, 0))
        self.assertEqual(auto_review.parse_version(""), (0, 0, 0))


class TestVersionTypeDetection(unittest.TestCase):
    """Tests for version type detection (patch/minor/major)."""
    
    def test_patch_version(self):
        """Test detecting patch version changes."""
        self.assertEqual(
            auto_review.get_version_type("1.2.3", "1.2.4"),
            auto_review.VersionType.PATCH
        )
        self.assertEqual(
            auto_review.get_version_type("1.2.3", "1.2.10"),
            auto_review.VersionType.PATCH
        )
    
    def test_minor_version(self):
        """Test detecting minor version changes."""
        self.assertEqual(
            auto_review.get_version_type("1.2.3", "1.3.0"),
            auto_review.VersionType.MINOR
        )
        self.assertEqual(
            auto_review.get_version_type("1.2.3", "1.10.5"),
            auto_review.VersionType.MINOR
        )
    
    def test_major_version(self):
        """Test detecting major version changes."""
        self.assertEqual(
            auto_review.get_version_type("1.2.3", "2.0.0"),
            auto_review.VersionType.MAJOR
        )
        self.assertEqual(
            auto_review.get_version_type("1.2.3", "10.0.0"),
            auto_review.VersionType.MAJOR
        )


class TestChangelogAnalysis(unittest.TestCase):
    """Tests for changelog analysis."""
    
    def test_no_danger_keywords(self):
        """Test changelog without danger keywords."""
        changelog = """
        ## 1.2.3
        - Fixed minor bug
        - Improved performance
        - Added new feature
        """
        result = auto_review.analyze_changelog(changelog, "1.2.2", "1.2.3")
        self.assertFalse(result["has_danger_keywords"])
        self.assertEqual(result["danger_matches"], [])
    
    def test_breaking_keyword(self):
        """Test changelog with breaking change keyword."""
        changelog = """
        ## 2.0.0
        - **Breaking change**: Removed deprecated API
        - New features added
        """
        result = auto_review.analyze_changelog(changelog, "1.9.0", "2.0.0")
        self.assertTrue(result["has_danger_keywords"])
        self.assertIn("breaking", result["danger_matches"])
    
    def test_regression_keyword(self):
        """Test changelog with regression keyword."""
        changelog = """
        ## 1.2.3
        - Fixed regression in data processing
        """
        result = auto_review.analyze_changelog(changelog, "1.2.2", "1.2.3")
        self.assertTrue(result["has_danger_keywords"])
        self.assertIn("regression", result["danger_matches"])
    
    def test_security_keyword(self):
        """Test changelog with security vulnerability keyword."""
        changelog = """
        ## 1.2.3
        - Fixed security vulnerability (CVE-2024-1234)
        """
        result = auto_review.analyze_changelog(changelog, "1.2.2", "1.2.3")
        self.assertTrue(result["has_danger_keywords"])
        self.assertIn("security vulnerability", result["danger_matches"])
    
    def test_empty_changelog(self):
        """Test analysis of None/empty changelog."""
        result = auto_review.analyze_changelog(None, "1.0.0", "1.0.1")
        self.assertFalse(result["has_danger_keywords"])
        
        result = auto_review.analyze_changelog("", "1.0.0", "1.0.1")
        self.assertFalse(result["has_danger_keywords"])
    
    def test_version_section_extraction(self):
        """Test extracting version-specific section."""
        changelog = """## 1.2.4
- Latest fix

## 1.2.3
- Target fix
- Another change

## 1.2.2
- Old fix
"""
        result = auto_review.analyze_changelog(changelog, "1.2.2", "1.2.3")
        self.assertIsNotNone(result["version_section"])
        self.assertIn("Target fix", result["version_section"])


class TestIssueAnalysis(unittest.TestCase):
    """Tests for GitHub issue analysis."""
    
    def test_no_issues(self):
        """Test with empty issues list."""
        result = auto_review.analyze_issues([])
        self.assertFalse(result["has_critical_issues"])
        self.assertEqual(result["critical_count"], 0)
    
    def test_critical_label_bug(self):
        """Test detecting bug label."""
        issues = [{
            "title": "Something is broken",
            "labels": ["bug", "help wanted"],
            "state": "open",
        }]
        result = auto_review.analyze_issues(issues)
        self.assertTrue(result["has_critical_issues"])
        self.assertEqual(result["critical_count"], 1)
    
    def test_critical_label_security(self):
        """Test detecting security label."""
        issues = [{
            "title": "Security issue",
            "labels": ["security", "critical"],
            "state": "open",
        }]
        result = auto_review.analyze_issues(issues)
        self.assertTrue(result["has_critical_issues"])
    
    def test_danger_keyword_in_title(self):
        """Test detecting danger keyword in issue title."""
        issues = [{
            "title": "CRITICAL: Regression in latest release",
            "labels": ["question"],
            "state": "open",
        }]
        result = auto_review.analyze_issues(issues)
        self.assertTrue(result["has_critical_issues"])
        self.assertIn("Regression", result["blocking_issues"][0])
    
    def test_non_critical_issues(self):
        """Test that non-critical issues are ignored."""
        issues = [
            {
                "title": "Feature request: add dark mode",
                "labels": ["enhancement"],
                "state": "open",
            },
            {
                "title": "Documentation typo",
                "labels": ["documentation"],
                "state": "open",
            },
        ]
        result = auto_review.analyze_issues(issues)
        self.assertFalse(result["has_critical_issues"])
        self.assertEqual(result["critical_count"], 0)


class TestDueForReview(unittest.TestCase):
    """Tests for release date checking."""
    
    def test_release_3_days_ago(self):
        """Test package released 3 days ago is due for review."""
        release_date = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        self.assertTrue(auto_review.is_due_for_auto_review(release_date, days=2))
    
    def test_release_1_day_ago(self):
        """Test package released 1 day ago is not due for review."""
        release_date = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        self.assertFalse(auto_review.is_due_for_auto_review(release_date, days=2))
    
    def test_no_release_date(self):
        """Test package with no release date is not due for review."""
        self.assertFalse(auto_review.is_due_for_auto_review(None, days=2))
        self.assertFalse(auto_review.is_due_for_auto_review("", days=2))


class TestAutoReviewLogic(unittest.TestCase):
    """Tests for the main auto-review logic."""
    
    @patch.object(auto_review, 'check_npm_package')
    @patch.object(auto_review, 'fetch_changelog')
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_patch_version_auto_approved(
        self, mock_is_due, mock_fetch_changelog, mock_check_npm
    ):
        """Test patch version is auto-approved after grace period."""
        mock_is_due.return_value = True
        mock_check_npm.return_value = {
            "release_date": "2024-01-01T00:00:00Z",
            "github_repo": "owner/repo",
            "issues": [],
            "changelog_url": "https://example.com/CHANGELOG.md",
        }
        mock_fetch_changelog.return_value = "## 1.2.4\n- Bug fix"
        
        meta = auto_review.PackageMeta(
            name="test-pkg",
            current_version="1.2.3",
            latest_version="1.2.4",
            manager="npm",
            release_date="2024-01-01T00:00:00Z",
        )
        
        result, reason = auto_review.auto_review_package(meta)
        self.assertEqual(result, auto_review.ReviewResult.OK)
        self.assertIn("Patch version", reason)
    
    @patch.object(auto_review, 'check_npm_package')
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_major_version_blocked(
        self, mock_is_due, mock_check_npm
    ):
        """Test major version is always blocked."""
        mock_is_due.return_value = True
        mock_check_npm.return_value = {}
        
        meta = auto_review.PackageMeta(
            name="test-pkg",
            current_version="1.2.3",
            latest_version="2.0.0",
            manager="npm",
            release_date="2024-01-01T00:00:00Z",
        )
        
        result, reason = auto_review.auto_review_package(meta)
        self.assertEqual(result, auto_review.ReviewResult.BLOCKED)
        self.assertIn("Major version", reason)
    
    @patch.object(auto_review, 'check_npm_package')
    @patch.object(auto_review, 'fetch_changelog')
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_dangerous_changelog_blocked(
        self, mock_is_due, mock_fetch_changelog, mock_check_npm
    ):
        """Test package with breaking changes in changelog is blocked."""
        mock_is_due.return_value = True
        mock_check_npm.return_value = {
            "release_date": "2024-01-01T00:00:00Z",
            "github_repo": "owner/repo",
            "issues": [],
            "changelog_url": "https://example.com/CHANGELOG.md",
        }
        mock_fetch_changelog.return_value = "## 1.3.0\n- Breaking: changed API"
        
        meta = auto_review.PackageMeta(
            name="test-pkg",
            current_version="1.2.3",
            latest_version="1.3.0",
            manager="npm",
            release_date="2024-01-01T00:00:00Z",
        )
        
        result, reason = auto_review.auto_review_package(meta)
        self.assertEqual(result, auto_review.ReviewResult.BLOCKED)
        self.assertIn("danger keywords", reason)
    
    @patch.object(auto_review, 'check_npm_package')
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_critical_issues_blocked(
        self, mock_is_due, mock_check_npm
    ):
        """Test package with critical issues is blocked."""
        mock_is_due.return_value = True
        mock_check_npm.return_value = {
            "release_date": "2024-01-01T00:00:00Z",
            "github_repo": "owner/repo",
            "issues": [
                {
                    "title": "CRITICAL BUG: Data loss",
                    "labels": ["bug", "critical"],
                    "state": "open",
                }
            ],
            "changelog_url": None,
        }
        
        meta = auto_review.PackageMeta(
            name="test-pkg",
            current_version="1.2.3",
            latest_version="1.3.0",
            manager="npm",
            release_date="2024-01-01T00:00:00Z",
        )
        
        result, reason = auto_review.auto_review_package(meta)
        self.assertEqual(result, auto_review.ReviewResult.BLOCKED)
        self.assertIn("Critical issues", reason)
    
    def test_max_failed_attempts_blocked(self):
        """Test package with 3+ failed attempts is auto-blocked."""
        meta = auto_review.PackageMeta(
            name="test-pkg",
            current_version="1.2.3",
            latest_version="1.2.4",
            manager="npm",
            failed_attempts=3,
        )
        
        result, reason = auto_review.auto_review_package(meta)
        self.assertEqual(result, auto_review.ReviewResult.BLOCKED)
        self.assertIn("failed upgrade attempts", reason)
    
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_not_due_pending(self, mock_is_due):
        """Test package not due for review returns pending."""
        mock_is_due.return_value = False
        
        meta = auto_review.PackageMeta(
            name="test-pkg",
            current_version="1.2.3",
            latest_version="1.2.4",
            manager="npm",
            release_date="2024-01-15T00:00:00Z",
        )
        
        result, reason = auto_review.auto_review_package(meta)
        self.assertEqual(result, auto_review.ReviewResult.PENDING)


class TestSinglePackageReview(unittest.TestCase):
    """Tests for review_single_package function."""
    
    @patch.object(auto_review, 'check_npm_package')
    @patch.object(auto_review, 'fetch_changelog')
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_review_updates_metadata(
        self, mock_is_due, mock_fetch_changelog, mock_check_npm
    ):
        """Test that review updates metadata correctly."""
        mock_is_due.return_value = True
        mock_check_npm.return_value = {
            "release_date": "2024-01-01T00:00:00Z",
            "github_repo": "owner/repo",
            "issues": [],
            "changelog_url": None,
        }
        mock_fetch_changelog.return_value = None
        
        meta = {
            "firstSeenAt": "2024-01-01T00:00:00Z",
            "currentVersion": "1.2.3",
            "latestVersion": "1.2.4",
            "planned": False,
            "blocked": False,
            "manager": "npm",
        }
        
        updated = auto_review.review_single_package("test-pkg", meta, "npm")
        
        self.assertEqual(updated["reviewResult"], "ok")
        self.assertEqual(updated["reviewedBy"], "auto")
        self.assertTrue(updated["planned"])
        self.assertIn("autoReviewAt", updated)  # Field is autoReviewAt, not reviewedAt
    
    def test_skip_manual_review(self):
        """Test that manually reviewed packages are skipped."""
        meta = {
            "firstSeenAt": "2024-01-01T00:00:00Z",
            "currentVersion": "1.2.3",
            "latestVersion": "1.2.4",
            "reviewedBy": "manual",
            "planned": False,
        }
        
        updated = auto_review.review_single_package("test-pkg", meta, "npm")
        self.assertEqual(updated["reviewedBy"], "manual")


class TestRunAutoReview(unittest.TestCase):
    """Tests for run_auto_review function."""
    
    def setUp(self):
        """Create temporary test files."""
        self.test_dir = Path(__file__).parent
        self.npm_path = self.test_dir / "test_npm_tracked.json"
        self.brew_path = self.test_dir / "test_brew_tracked.json"
    
    def tearDown(self):
        """Clean up test files."""
        if self.npm_path.exists():
            self.npm_path.unlink()
        if self.brew_path.exists():
            self.brew_path.unlink()
    
    @patch.object(auto_review, 'check_npm_package')
    @patch.object(auto_review, 'check_brew_formula')
    @patch.object(auto_review, 'fetch_changelog')
    @patch.object(auto_review, 'is_due_for_auto_review')
    def test_run_auto_review_summary(
        self, mock_is_due, mock_fetch_changelog, mock_check_brew, mock_check_npm
    ):
        """Test run_auto_review produces correct summary."""
        mock_is_due.return_value = True
        mock_check_npm.return_value = {
            "release_date": "2024-01-01T00:00:00Z",
            "github_repo": None,
            "issues": [],
            "changelog_url": None,
        }
        mock_check_brew.return_value = {
            "release_date": "2024-01-01T00:00:00Z",
            "github_repo": None,
            "issues": [],
            "changelog_url": None,
        }
        mock_fetch_changelog.return_value = None
        
        # Create test npm data
        npm_data = {
            "items": {
                "pkg1": {
                    "firstSeenAt": "2024-01-01T00:00:00Z",
                    "currentVersion": "1.2.3",
                    "latestVersion": "1.2.4",
                    "planned": False,
                    "blocked": False,
                    "manager": "npm",
                }
            }
        }
        
        # Create test brew data
        brew_data = {
            "items": {
                "formula1": {
                    "firstSeenAt": "2024-01-01T00:00:00Z",
                    "currentVersion": "1.0.0",
                    "latestVersion": "2.0.0",  # Major - should be blocked
                    "planned": False,
                    "blocked": False,
                    "manager": "brew",
                }
            }
        }
        
        self.npm_path.write_text(json.dumps(npm_data))
        self.brew_path.write_text(json.dumps(brew_data))
        
        result = auto_review.run_auto_review(
            self.npm_path, self.brew_path, dry_run=True
        )
        
        self.assertEqual(result["npm"]["reviewed"], 1)
        self.assertEqual(result["brew"]["reviewed"], 1)
        # npm pkg1 is patch - should be approved
        self.assertEqual(result["npm"]["approved"], 1)
        # brew formula1 is major - should be blocked
        self.assertEqual(result["brew"]["blocked"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
