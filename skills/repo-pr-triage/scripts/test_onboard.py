#!/usr/bin/env python3
"""Tests for onboard.py - repo context fetching, interview prompt generation."""

import json
import subprocess
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

import onboard


class TestParseRepo(unittest.TestCase):
    def test_full_url(self):
        self.assertEqual(onboard.parse_repo("https://github.com/owner/repo"), "owner/repo")

    def test_trailing_slash(self):
        self.assertEqual(onboard.parse_repo("https://github.com/owner/repo/"), "owner/repo")

    def test_git_suffix(self):
        self.assertEqual(onboard.parse_repo("https://github.com/o/r.git"), "o/r")

    def test_shorthand(self):
        self.assertEqual(onboard.parse_repo("owner/repo"), "owner/repo")

    def test_path_traversal(self):
        result = onboard.parse_repo("https://github.com/../../etc/passwd")
        self.assertIsInstance(result, str)

    def test_url_with_semicolon(self):
        result = onboard.parse_repo("https://github.com/owner/repo; echo pwned")
        self.assertIsInstance(result, str)


class TestRunGh(unittest.TestCase):
    @patch("onboard.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
        self.assertEqual(onboard.run_gh(["repo", "view"]), "output")

    @patch("onboard.subprocess.run")
    def test_failure_returns_empty(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        self.assertEqual(onboard.run_gh(["repo", "view"]), "")

    @patch("onboard.subprocess.run")
    def test_failure_ignored(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="partial", stderr="err")
        self.assertEqual(onboard.run_gh(["api", "test"], ignore_errors=True), "partial")

    @patch("onboard.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gh", timeout=30)
        self.assertEqual(onboard.run_gh(["repo", "view"]), "")

    @patch("onboard.subprocess.run")
    def test_gh_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        self.assertEqual(onboard.run_gh(["repo", "view"]), "")


class TestFetchRepoContext(unittest.TestCase):
    @patch("onboard.run_gh")
    def test_all_fields_populated(self, mock_gh):
        meta = json.dumps({"name": "myrepo", "description": "desc", "stargazerCount": 100,
                           "primaryLanguage": {"name": "Python"}, "repositoryTopics": []})
        mock_gh.side_effect = [meta, "README content", "CONTRIBUTING content", "v1.0", "42"]
        ctx = onboard.fetch_repo_context("owner/repo")
        self.assertEqual(ctx["metadata"]["name"], "myrepo")
        self.assertEqual(ctx["readme"], "README content")
        self.assertEqual(ctx["contributing"], "CONTRIBUTING content")

    @patch("onboard.run_gh")
    def test_all_empty(self, mock_gh):
        mock_gh.return_value = ""
        ctx = onboard.fetch_repo_context("owner/repo")
        self.assertNotIn("metadata", ctx)
        self.assertNotIn("readme", ctx)

    @patch("onboard.run_gh")
    def test_invalid_json_metadata(self, mock_gh):
        mock_gh.side_effect = ["not json", "", "", "", ""]
        ctx = onboard.fetch_repo_context("owner/repo")
        self.assertEqual(ctx.get("metadata"), {})


class TestGenerateInterviewPrompt(unittest.TestCase):
    def test_basic_prompt_generation(self):
        ctx = {
            "metadata": {"name": "myrepo", "description": "A tool", "stargazerCount": 50,
                         "primaryLanguage": {"name": "Go"}, "repositoryTopics": [{"name": "cli"}]},
            "readme": "# MyRepo\nDoes stuff.",
            "releases": "v1.0\tv1.0\tLatest",
            "open_issues": "10",
        }
        prompt = onboard.generate_interview_prompt("owner/myrepo", ctx)
        self.assertIn("myrepo", prompt)
        self.assertIn("A tool", prompt)
        self.assertIn("Interview Questions", prompt)

    def test_missing_metadata(self):
        prompt = onboard.generate_interview_prompt("owner/repo", {})
        self.assertIn("Interview Questions", prompt)
        self.assertIn("repo", prompt)

    def test_primary_language_not_dict(self):
        ctx = {"metadata": {"primaryLanguage": "Python", "repositoryTopics": None}}
        prompt = onboard.generate_interview_prompt("owner/repo", ctx)
        self.assertIn("unknown", prompt)

    def test_shell_injection_in_repo_name(self):
        ctx = {"metadata": {"name": "$(rm -rf /)", "description": "", "stargazerCount": 0,
                             "primaryLanguage": {"name": "Python"}, "repositoryTopics": []}}
        prompt = onboard.generate_interview_prompt("$(rm -rf /)/repo", ctx)
        # Just verify it produces a string without crashing
        self.assertIsInstance(prompt, str)


class TestMainIntegration(unittest.TestCase):
    @patch("onboard.fetch_repo_context")
    @patch("onboard.parse_repo", return_value="owner/repo")
    def test_main_creates_output(self, mock_parse, mock_fetch):
        mock_fetch.return_value = {"metadata": {"name": "repo", "description": "d",
                                                 "stargazerCount": 1, "primaryLanguage": {"name": "Py"},
                                                 "repositoryTopics": []}}
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("sys.argv", ["onboard.py", "https://github.com/owner/repo",
                                    "--output-dir", tmpdir]):
                onboard.main()
            self.assertTrue((Path(tmpdir) / "interview-prompt.md").exists())


if __name__ == "__main__":
    unittest.main()
