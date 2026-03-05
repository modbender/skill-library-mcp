#!/usr/bin/env python3
"""Tests for report.py - markdown report generation from scan JSON."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report


def _make_scored_pr(number=1, title="Test PR", score=50, action="review",
                    author="dev", modifiers=None, labels=None, **extra):
    pr = {
        "number": number,
        "title": title,
        "score": score,
        "action": action,
        "author": author,
        "created_at": "2026-01-01T00:00:00Z",
        "modifiers": modifiers or [],
        "labels": labels or [],
        "stats": {"additions": extra.get("additions", 10),
                  "deletions": extra.get("deletions", 5),
                  "changed_files": extra.get("changed_files", 2)},
    }
    pr.update({k: v for k, v in extra.items() if k not in ("additions", "deletions", "changed_files")})
    return pr


def _make_scan_output(prs, repo="owner/repo"):
    scored = prs
    return {
        "repo": repo,
        "total_prs": len(scored),
        "scored_prs": scored,
        "potential_duplicates": [],
        "distribution": {
            "prioritize": len([p for p in scored if p["score"] >= 80]),
            "review": len([p for p in scored if 50 <= p["score"] < 80]),
            "close": len([p for p in scored if p["score"] < 50]),
        }
    }


class TestLoadScores(unittest.TestCase):
    def test_valid_json(self):
        data = _make_scan_output([])
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            result = report.load_scores(f.name)
        self.assertEqual(result["total_prs"], 0)

    def test_file_not_found_exits(self):
        with self.assertRaises(SystemExit):
            report.load_scores("/nonexistent/scores.json")

    def test_invalid_json_exits(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not json {{{")
            f.flush()
            with self.assertRaises(SystemExit):
                report.load_scores(f.name)


class TestPrToMarkdown(unittest.TestCase):
    def test_basic_format(self):
        pr = _make_scored_pr(number=42, title="Fix login", score=75, author="alice",
                             modifiers=[{"modifier": "bug_fix", "points": 5}],
                             labels=["bugfix"])
        md = report.pr_to_markdown(pr, "owner/repo")
        self.assertIn("Fix login", md)
        self.assertIn("#42", md)
        self.assertIn("alice", md)
        self.assertIn("bug_fix (+5)", md)
        self.assertIn("bugfix", md)

    def test_no_modifiers_no_labels(self):
        pr = _make_scored_pr()
        md = report.pr_to_markdown(pr, "owner/repo")
        self.assertIn("none", md)

    def test_shell_injection_in_title(self):
        pr = _make_scored_pr(title="$(rm -rf /)")
        md = report.pr_to_markdown(pr, "owner/repo")
        self.assertIn("$(rm -rf /)", md)


class TestGenerateReport(unittest.TestCase):
    def test_empty_prs(self):
        md = report.generate_report([], "owner/repo", "Test", "Desc")
        self.assertIn("No PRs in this category", md)

    def test_with_prs(self):
        prs = [_make_scored_pr(number=i, title=f"PR {i}") for i in range(3)]
        md = report.generate_report(prs, "owner/repo", "Title", "Desc")
        self.assertIn("Count:** 3", md)
        self.assertIn("PR 0", md)
        self.assertIn("PR 2", md)


class TestGenerateSummary(unittest.TestCase):
    def test_empty_prs(self):
        data = _make_scan_output([])
        md = report.generate_summary(data)
        self.assertIn("Total PRs scored:** 0", md)
        self.assertIn("No potential duplicates", md)

    def test_distribution_math(self):
        prs = [
            _make_scored_pr(number=1, score=90, action="prioritize"),
            _make_scored_pr(number=2, score=60, action="review"),
            _make_scored_pr(number=3, score=20, action="close"),
        ]
        data = _make_scan_output(prs)
        md = report.generate_summary(data)
        self.assertIn("Prioritize (80+):** 1", md)
        self.assertIn("Review (50-79):** 1", md)
        self.assertIn("Close (<50):** 1", md)

    def test_duplicates_section_rendered(self):
        prs = [_make_scored_pr(number=1), _make_scored_pr(number=2)]
        data = _make_scan_output(prs)
        data["potential_duplicates"] = [{"pr_a": 1, "pr_b": 2, "similarity": 0.85}]
        md = report.generate_summary(data)
        self.assertIn("#1 and #2", md)
        self.assertIn("85%", md)

    def test_multiple_duplicates(self):
        data = _make_scan_output([_make_scored_pr()])
        data["potential_duplicates"] = [
            {"pr_a": 1, "pr_b": 2, "similarity": 0.9},
            {"pr_a": 3, "pr_b": 4, "similarity": 0.7},
        ]
        md = report.generate_summary(data)
        self.assertIn("#1 and #2", md)
        self.assertIn("#3 and #4", md)

    def test_common_patterns(self):
        prs = [_make_scored_pr(modifiers=[{"modifier": "security_fix", "points": 20}]) for _ in range(5)]
        data = _make_scan_output(prs)
        md = report.generate_summary(data)
        self.assertIn("security_fix: 5 PRs", md)

    def test_most_active_authors(self):
        prs = [_make_scored_pr(number=i, author="alice") for i in range(3)]
        data = _make_scan_output(prs)
        md = report.generate_summary(data)
        self.assertIn("alice: 3 PRs", md)


class TestMainIntegration(unittest.TestCase):
    def test_main_creates_all_files(self):
        prs = [
            _make_scored_pr(number=1, score=90, action="prioritize"),
            _make_scored_pr(number=2, score=60, action="review"),
            _make_scored_pr(number=3, score=20, action="close"),
        ]
        data = _make_scan_output(prs)
        with tempfile.TemporaryDirectory() as tmpdir:
            scores_path = Path(tmpdir) / "scores.json"
            scores_path.write_text(json.dumps(data))
            out_dir = Path(tmpdir) / "reports"
            with patch("sys.argv", ["report.py", str(scores_path), "--output-dir", str(out_dir)]):
                report.main()
            for fname in ["prioritize.md", "review.md", "close.md", "summary.md"]:
                self.assertTrue((out_dir / fname).exists(), f"{fname} not created")

    def test_main_empty_prs(self):
        data = _make_scan_output([])
        with tempfile.TemporaryDirectory() as tmpdir:
            scores_path = Path(tmpdir) / "scores.json"
            scores_path.write_text(json.dumps(data))
            out_dir = Path(tmpdir) / "reports"
            with patch("sys.argv", ["report.py", str(scores_path), "--output-dir", str(out_dir)]):
                report.main()
            content = (out_dir / "summary.md").read_text()
            self.assertIn("Total PRs scored:** 0", content)


if __name__ == "__main__":
    unittest.main()
