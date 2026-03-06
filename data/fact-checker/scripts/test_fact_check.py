#!/usr/bin/env /Users/loki/.pyenv/versions/3.14.3/bin/python3
"""
Unit tests for fact_check.py

Run with:
    python3 -m pytest scripts/test_fact_check.py -v
    # or directly:
    python3 scripts/test_fact_check.py
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Make sure the module can be imported regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))
import fact_check as fc


# ─────────────────────────────────────────────────────────────────────────────
# 1. Numeric claim extraction
# ─────────────────────────────────────────────────────────────────────────────
class TestExtractNumericClaims(unittest.TestCase):
    """Extracts numeric claims from sample text."""

    def test_extracts_run_count(self):
        text = "We have processed 909 runs so far this sprint."
        claims = fc.extract_numeric_claims(text)
        values = [c["value"] for c in claims]
        self.assertIn("909", values)

    def test_extracts_multiple_numbers(self):
        text = "Across 200 evaluated runs we used 1500 tokens per call."
        claims = fc.extract_numeric_claims(text)
        values = [c["value"] for c in claims]
        self.assertIn("200", values)
        self.assertIn("1500", values)

    def test_ignores_numbers_without_domain_context(self):
        """Plain numbers with no relevant context words should be filtered out."""
        text = "The answer is 42 and the page is 17."
        claims = fc.extract_numeric_claims(text)
        self.assertEqual(claims, [])

    def test_extracts_comma_separated_numbers(self):
        text = "Total cost was 1,956 runs over the month."
        claims = fc.extract_numeric_claims(text)
        values = [c["value"] for c in claims]
        self.assertIn("1,956", values)

    def test_context_window_included(self):
        text = "After 500 eval runs the model was promoted."
        claims = fc.extract_numeric_claims(text)
        self.assertTrue(len(claims) >= 1)
        # Context should include surrounding text
        self.assertIn("500", claims[0]["context"])

    def test_extracts_float_param_count(self):
        text = "The 7B param model performed well against the 20B model."
        claims = fc.extract_numeric_claims(text)
        values = [c["value"] for c in claims]
        self.assertIn("7", values)
        self.assertIn("20", values)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Model name extraction
# ─────────────────────────────────────────────────────────────────────────────
class TestExtractModelRefs(unittest.TestCase):
    """Extracts model name references (word/word and word:word)."""

    def test_extracts_slash_pattern(self):
        text = "phi4/classify scored 1.000 on all 23 runs."
        claims = fc.extract_model_refs(text)
        slash_refs = [c for c in claims if c["type"] == "model_slash"]
        self.assertTrue(any(c["value"] == "phi4/classify" for c in slash_refs))

    def test_extracts_colon_pattern(self):
        text = "We use phi4:latest as the control floor."
        claims = fc.extract_model_refs(text)
        colon_refs = [c for c in claims if c["type"] == "model_colon"]
        self.assertTrue(any(c["value"] == "phi4:latest" for c in colon_refs))

    def test_skips_urls(self):
        text = "See https://localhost:8765/status for details."
        claims = fc.extract_model_refs(text)
        colon_refs = [c for c in claims if c["type"] == "model_colon"]
        # Should not match 8765/status or localhost:8765
        values = [c["value"] for c in colon_refs]
        self.assertNotIn("localhost:8765", values)

    def test_extracts_multiple_models(self):
        text = "Both phi4/classify and qwen2.5/format performed above threshold."
        claims = fc.extract_model_refs(text)
        slash_refs = [c["value"] for c in claims if c["type"] == "model_slash"]
        self.assertIn("phi4/classify", slash_refs)
        self.assertIn("qwen2.5/format", slash_refs)

    def test_model_colon_model_tag_parsed(self):
        text = "deepseek-r1:8b was tested on the extract task."
        claims = fc.extract_model_refs(text)
        colon_refs = [c for c in claims if c["type"] == "model_colon"]
        self.assertTrue(any(c["model"] == "deepseek-r1" and c["tag"] == "8b" for c in colon_refs))

    def test_no_false_positives_in_clean_text(self):
        text = "This document contains no model references at all."
        claims = fc.extract_model_refs(text)
        self.assertEqual(claims, [])


# ─────────────────────────────────────────────────────────────────────────────
# 3. Date extraction
# ─────────────────────────────────────────────────────────────────────────────
class TestExtractDateRefs(unittest.TestCase):
    """Extracts YYYY-MM-DD date references."""

    def test_extracts_iso_date(self):
        text = "The sprint ran from 2026-02-25 to 2026-02-27."
        claims = fc.extract_date_refs(text)
        values = [c["value"] for c in claims]
        self.assertIn("2026-02-25", values)
        self.assertIn("2026-02-27", values)

    def test_does_not_match_invalid_dates(self):
        text = "The version 2026-99-99 should not be parsed."
        claims = fc.extract_date_refs(text)
        self.assertEqual(claims, [])

    def test_date_context_captured(self):
        text = "On 2026-01-15 we merged the first sprint branch."
        claims = fc.extract_date_refs(text)
        self.assertEqual(len(claims), 1)
        self.assertIn("2026-01-15", claims[0]["context"])

    def test_no_dates_in_clean_text(self):
        text = "There are no dates mentioned in this short paragraph."
        claims = fc.extract_date_refs(text)
        self.assertEqual(claims, [])

    def test_extracts_date_with_surrounding_context(self):
        text = "Budget approved on 2025-11-01 for Q4 tooling."
        claims = fc.extract_date_refs(text)
        self.assertEqual(len(claims), 1)
        self.assertIn("Budget", claims[0]["context"])


# ─────────────────────────────────────────────────────────────────────────────
# 4. Clean file handling (no claims)
# ─────────────────────────────────────────────────────────────────────────────
class TestCleanFileHandling(unittest.TestCase):
    """Handles a clean file with no verifiable claims gracefully."""

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            path = Path(f.name)
        try:
            result = fc.run_fact_check(path)
            report = "\n".join(result)
            self.assertIn("No verifiable claims", report)
        finally:
            path.unlink()

    def test_file_with_only_prose(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Introduction\n\nThis is a story about a cat who liked to chase mice.\n")
            path = Path(f.name)
        try:
            result = fc.run_fact_check(path)
            report = "\n".join(result)
            self.assertIn("No verifiable claims", report)
        finally:
            path.unlink()

    def test_nonexistent_file(self):
        path = Path("/tmp/this_file_does_not_exist_ever.md")
        result = fc.run_fact_check(path)
        report = "\n".join(result)
        self.assertIn("ERROR", report)
        self.assertIn("not found", report)

    def test_returns_list_of_strings(self):
        """run_fact_check always returns a list of strings, never raises."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Nothing here.\n")
            path = Path(f.name)
        try:
            result = fc.run_fact_check(path)
            self.assertIsInstance(result, list)
            for line in result:
                self.assertIsInstance(line, str)
        finally:
            path.unlink()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Output formatting
# ─────────────────────────────────────────────────────────────────────────────
class TestOutputFormatting(unittest.TestCase):
    """Formats output correctly."""

    def test_confirmed_uses_green_checkmark(self):
        line = fc.format_result("CONFIRMED", "phi4/classify scored 1.000", "/status API: phi4_latest_classify mean=1.000 n=23")
        self.assertTrue(line.startswith("✅"))
        self.assertIn("CONFIRMED", line)
        self.assertIn("→", line)

    def test_unverifiable_uses_warning(self):
        line = fc.format_result("UNVERIFIABLE", "this took about a day", "no timestamp found in logs")
        self.assertTrue(line.startswith("⚠️"))
        self.assertIn("UNVERIFIABLE", line)

    def test_contradicted_uses_red_x(self):
        line = fc.format_result("CONTRADICTED", "909 runs", "/status API shows 958 total runs")
        self.assertTrue(line.startswith("❌"))
        self.assertIn("CONTRADICTED", line)

    def test_long_context_is_truncated(self):
        long_ctx = "a" * 200
        line = fc.format_result("CONFIRMED", long_ctx, "evidence here")
        # Context in the line should be truncated with ellipsis
        self.assertIn("...", line)
        # Total line should not contain the full 200-char context
        self.assertLess(line.index("→"), 200)

    def test_format_result_contains_all_parts(self):
        line = fc.format_result("CONFIRMED", "context snippet", "evidence detail")
        self.assertIn("context snippet", line)
        self.assertIn("evidence detail", line)
        self.assertIn("→", line)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Score extraction
# ─────────────────────────────────────────────────────────────────────────────
class TestExtractScoreClaims(unittest.TestCase):
    """Extracts decimal score values."""

    def test_extracts_perfect_score(self):
        text = "phi4/classify achieved a mean score of 1.000 across all runs."
        claims = fc.extract_score_claims(text)
        values = [c["value"] for c in claims]
        self.assertIn("1.000", values)

    def test_extracts_various_scores(self):
        text = "Scores ranged from 0.423 to 0.987 depending on the task."
        claims = fc.extract_score_claims(text)
        values = [c["value"] for c in claims]
        self.assertIn("0.423", values)
        self.assertIn("0.987", values)

    def test_does_not_extract_large_numbers(self):
        text = "We ran 42000 evaluations in total."
        claims = fc.extract_score_claims(text)
        self.assertEqual(claims, [])

    def test_float_val_is_correct(self):
        text = "The model scored 0.923 on the latest run."
        claims = fc.extract_score_claims(text)
        self.assertTrue(any(abs(c["float_val"] - 0.923) < 1e-6 for c in claims))


# ─────────────────────────────────────────────────────────────────────────────
# 7. Verify model ref against mock API data
# ─────────────────────────────────────────────────────────────────────────────
class TestVerifyModelRef(unittest.TestCase):
    """verify_model_ref returns CONFIRMED when API has matching entry."""

    def _mock_status(self):
        return {
            "confidence": {
                "phi4_latest_classify": {
                    "mean": 1.0,
                    "n": 23,
                    "last_10_mean": 1.0,
                }
            }
        }

    def test_confirmed_via_api(self):
        claim = {"type": "model_slash", "value": "phi4/classify", "model": "phi4", "task": "classify", "context": "phi4/classify scored 1.000", "pos": 0}
        status, ev = fc.verify_model_ref(claim, self._mock_status(), "", {})
        self.assertEqual(status, "CONFIRMED")
        self.assertIn("phi4_latest_classify", ev)

    def test_unverifiable_when_not_in_api(self):
        claim = {"type": "model_slash", "value": "mystery/task", "model": "mystery", "task": "task", "context": "mystery/task", "pos": 0}
        status, ev = fc.verify_model_ref(claim, self._mock_status(), "", {})
        self.assertEqual(status, "UNVERIFIABLE")

    def test_confirmed_via_score_files(self):
        score_files = {"phi4_latest_classify": [1.0, 1.0, 1.0]}
        claim = {"type": "model_slash", "value": "phi4/classify", "model": "phi4", "task": "classify", "context": "...", "pos": 0}
        status, ev = fc.verify_model_ref(claim, None, "", score_files)
        self.assertEqual(status, "CONFIRMED")
        self.assertIn("score file", ev)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Run count contradiction
# ─────────────────────────────────────────────────────────────────────────────
class TestVerifyNumeric(unittest.TestCase):
    """verify_numeric correctly identifies contradicted run counts."""

    def _mock_status_with_runs(self, total_runs: int):
        return {"cost_today": {"total_runs": total_runs}}

    def test_contradicted_run_count(self):
        claim = {"value": "909", "context": "909 total runs in the project", "pos": 0}
        status, ev = fc.verify_numeric(claim, self._mock_status_with_runs(1956), "", "", "")
        self.assertEqual(status, "CONTRADICTED")
        self.assertIn("1956", ev)

    def test_confirmed_run_count_within_tolerance(self):
        claim = {"value": "1956", "context": "1956 total runs processed", "pos": 0}
        status, ev = fc.verify_numeric(claim, self._mock_status_with_runs(1956), "", "", "")
        self.assertEqual(status, "CONFIRMED")

    def test_found_in_findings(self):
        claim = {"value": "200", "context": "after 200 eval runs", "pos": 0}
        status, ev = fc.verify_numeric(claim, None, "After 200 runs the model was promoted.", "", "")
        self.assertEqual(status, "CONFIRMED")
        self.assertIn("FINDINGS.md", ev)

    def test_unverifiable_number(self):
        claim = {"value": "777", "context": "777 total runs analyzed", "pos": 0}
        status, ev = fc.verify_numeric(claim, None, "nothing here", "", "")
        self.assertEqual(status, "UNVERIFIABLE")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Full pipeline integration (uses real files if available)
# ─────────────────────────────────────────────────────────────────────────────
class TestFullPipeline(unittest.TestCase):
    """Integration-level: run_fact_check produces a well-formed report."""

    def test_report_has_header(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Sprint 18\n\nWe ran 200 evals. phi4/classify scored 1.000.\n")
            path = Path(f.name)
        try:
            lines = fc.run_fact_check(path)
            report = "\n".join(lines)
            self.assertIn("Fact-Check Report", report)
            self.assertIn("Source Data", report)
            self.assertIn("Summary", report)
        finally:
            path.unlink()

    def test_report_detects_model_refs(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("The phi4/classify model scored 1.000 on 23 runs.\n")
            path = Path(f.name)
        try:
            lines = fc.run_fact_check(path)
            report = "\n".join(lines)
            self.assertIn("Model References", report)
        finally:
            path.unlink()

    def test_report_detects_dates(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Sprint started on 2026-02-25.\n")
            path = Path(f.name)
        try:
            lines = fc.run_fact_check(path)
            report = "\n".join(lines)
            self.assertIn("Date References", report)
            self.assertIn("2026-02-25", report)
        finally:
            path.unlink()

    def test_summary_counts_are_present(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("phi4/classify scored 1.000 across 23 runs on 2026-02-01.\n")
            path = Path(f.name)
        try:
            lines = fc.run_fact_check(path)
            report = "\n".join(lines)
            self.assertIn("Confirmed", report)
            self.assertIn("Unverifiable", report)
            self.assertIn("Contradicted", report)
        finally:
            path.unlink()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
