# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "rich>=13.0.0",
# ]
# ///
"""Edge-case tests for cost estimation functions in scripts/research.py.

Run with:  uv run tests/test_cost_estimation.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path

# Ensure the project root is on sys.path so `scripts.research` is importable.
PROJECT_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("PROJECT_DIR", str(PROJECT_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from scripts.research import (
    _estimate_context_cost,
    _estimate_research_cost,
    _estimate_usage_from_output,
    _PRICE_ESTIMATES,
    _collect_files,
    _resolve_mime,
)

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

_results: list[tuple[str, bool, str]] = []


def run_test(func):
    """Decorator that runs a test function and records pass/fail."""
    name = func.__name__
    try:
        func()
        _results.append((name, True, ""))
        print(f"  PASS  {name}")
    except Exception as exc:
        tb = traceback.format_exc()
        _results.append((name, False, tb))
        print(f"  FAIL  {name}")
        print(f"        {exc}")
    return func


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@run_test
def test_empty_directory():
    """An empty directory should yield zero files and zero cost."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _estimate_context_cost(Path(tmpdir))
        assert result["files"] == 0, f"Expected 0 files, got {result['files']}"
        assert result["total_bytes"] == 0, f"Expected 0 bytes, got {result['total_bytes']}"
        assert result["estimated_tokens"] == 0, f"Expected 0 tokens, got {result['estimated_tokens']}"
        assert result["estimated_cost_usd"] == 0.0, f"Expected $0.00, got {result['estimated_cost_usd']}"


@run_test
def test_binary_only_directory():
    """A directory containing only binary files (.exe, .png) should have 0 uploadable files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for name in ("app.exe", "image.png", "archive.zip", "font.woff2"):
            (Path(tmpdir) / name).write_bytes(b"\x00" * 64)
        result = _estimate_context_cost(Path(tmpdir))
        assert result["files"] == 0, f"Expected 0 uploadable files, got {result['files']}"
        assert result["estimated_cost_usd"] == 0.0, f"Expected $0.00, got {result['estimated_cost_usd']}"


@run_test
def test_large_file_token_estimation():
    """Token estimation for a large file uses integer division by chars_per_token.

    Verify the formula: tokens = total_bytes // chars_per_token, and that
    the math works for sizes exceeding 1 MB without overflow or error.
    """
    chars_per_token = _PRICE_ESTIMATES["chars_per_token"]
    embedding_rate = _PRICE_ESTIMATES["embedding_per_1m_tokens"]

    # Simulate a 10 MB file (just verify the math -- no real file needed)
    large_bytes = 10 * 1024 * 1024  # 10 MB
    expected_tokens = large_bytes // chars_per_token
    expected_cost = (expected_tokens / 1_000_000) * embedding_rate

    assert expected_tokens == large_bytes // 4, (
        f"Token formula mismatch: {expected_tokens} != {large_bytes // 4}"
    )
    assert expected_cost > 0, "Cost for 10 MB should be > 0"
    assert isinstance(expected_cost, float), "Cost should be a float"

    # Also verify with a real (small) temp file that the function pipeline works
    with tempfile.TemporaryDirectory() as tmpdir:
        big_file = Path(tmpdir) / "big.txt"
        # Write 2000 bytes (small but enough to exercise the path)
        big_file.write_text("A" * 2000)
        result = _estimate_context_cost(big_file)
        assert result["files"] == 1
        assert result["estimated_tokens"] == 2000 // chars_per_token


@run_test
def test_unicode_heavy_content():
    """Files with CJK / emoji text should still produce a positive cost.

    The chars_per_token ratio of 4 is for English; CJK characters use 3 bytes
    each in UTF-8, so byte-based estimation still produces tokens and cost > 0.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        uni_file = Path(tmpdir) / "unicode.txt"
        # Mix of CJK ideographs -- each CJK char is 3 bytes in UTF-8.
        # Use enough repetitions so the cost survives round(..., 4).
        content = "\u4f60\u597d\u4e16\u754c" * 10_000  # 40 000 CJK characters
        uni_file.write_text(content, encoding="utf-8")

        result = _estimate_context_cost(uni_file)
        assert result["files"] == 1, f"Expected 1 file, got {result['files']}"
        assert result["total_bytes"] > 0, "Byte count should be > 0"
        assert result["estimated_tokens"] > 0, "Token estimate should be > 0 for CJK text"
        assert result["estimated_cost_usd"] > 0, "Cost should be > 0 for CJK text"

        # CJK chars are 3 bytes each in UTF-8 so total_bytes > number of characters
        num_chars = len(content)
        assert result["total_bytes"] > num_chars, (
            f"UTF-8 bytes ({result['total_bytes']}) should exceed char count ({num_chars}) for CJK"
        )


@run_test
def test_mixed_history_grounded_filter():
    """_estimate_research_cost should only use history entries matching the grounded flag."""
    history = [
        # 5 grounded entries with high durations
        {"grounded": True, "duration_seconds": 300},
        {"grounded": True, "duration_seconds": 360},
        {"grounded": True, "duration_seconds": 240},
        {"grounded": True, "duration_seconds": 280},
        {"grounded": True, "duration_seconds": 320},
        # 5 non-grounded entries with low durations
        {"grounded": False, "duration_seconds": 60},
        {"grounded": False, "duration_seconds": 80},
        {"grounded": False, "duration_seconds": 70},
        {"grounded": False, "duration_seconds": 90},
        {"grounded": False, "duration_seconds": 50},
    ]

    grounded_result = _estimate_research_cost(grounded=True, history=history)
    non_grounded_result = _estimate_research_cost(grounded=False, history=history)

    assert grounded_result["basis"] == "historical_average", (
        f"Grounded should use history, got {grounded_result['basis']}"
    )
    assert non_grounded_result["basis"] == "historical_average", (
        f"Non-grounded should use history, got {non_grounded_result['basis']}"
    )
    # Grounded runs are longer duration -> more tokens -> higher cost
    assert grounded_result["estimated_cost_usd"] > non_grounded_result["estimated_cost_usd"], (
        f"Grounded cost ({grounded_result['estimated_cost_usd']}) should exceed "
        f"non-grounded ({non_grounded_result['estimated_cost_usd']})"
    )


@run_test
def test_history_invalid_entries():
    """History entries with missing duration_seconds or wrong types are skipped gracefully."""
    history = [
        # Invalid: missing duration_seconds
        {"grounded": False},
        # Invalid: duration_seconds is a string
        {"grounded": False, "duration_seconds": "fast"},
        # Invalid: duration_seconds is None
        {"grounded": False, "duration_seconds": None},
        # Valid entries (only 2, below the threshold of 3)
        {"grounded": False, "duration_seconds": 120},
        {"grounded": False, "duration_seconds": 150},
    ]

    result = _estimate_research_cost(grounded=False, history=history)
    # With only 2 valid entries (< 3 threshold), should fall back to default
    assert result["basis"] == "default_estimate", (
        f"Expected default_estimate with <3 valid entries, got {result['basis']}"
    )


@run_test
def test_zero_duration_no_division_by_zero():
    """A zero-duration research run should not cause division by zero.

    The scale formula is max(0.5, duration / 120.0), so 0 / 120.0 = 0.0,
    clamped to 0.5, which avoids any division-by-zero issue.
    """
    result = _estimate_usage_from_output(
        report_text="Some report",
        duration_seconds=0,
        grounded=False,
    )
    # scale = max(0.5, 0 / 120.0) = 0.5
    expected_input = int(_PRICE_ESTIMATES["research_base_input_tokens"] * 0.5)
    assert result["estimated_input_tokens"] == expected_input, (
        f"Expected {expected_input} input tokens, got {result['estimated_input_tokens']}"
    )
    assert result["estimated_cost_usd"] > 0, "Cost should be > 0 even with 0 duration"

    # Also verify _estimate_research_cost handles zero-duration history
    history = [
        {"grounded": False, "duration_seconds": 0},
        {"grounded": False, "duration_seconds": 0},
        {"grounded": False, "duration_seconds": 0},
    ]
    res2 = _estimate_research_cost(grounded=False, history=history)
    assert res2["basis"] == "historical_average"
    assert res2["estimated_input_tokens"] > 0, "Should produce positive tokens even with 0-duration history"


@run_test
def test_negative_duration_clamping():
    """Negative duration_seconds should be clamped via max(0.5, ...) in the scale formula.

    scale = max(0.5, negative / 120.0) = 0.5, same as zero duration.
    """
    result_neg = _estimate_usage_from_output(
        report_text="Report text here",
        duration_seconds=-60,
        grounded=False,
    )
    result_zero = _estimate_usage_from_output(
        report_text="Report text here",
        duration_seconds=0,
        grounded=False,
    )
    # Both should clamp to scale=0.5, yielding identical input token estimates
    assert result_neg["estimated_input_tokens"] == result_zero["estimated_input_tokens"], (
        f"Negative duration ({result_neg['estimated_input_tokens']}) should match "
        f"zero duration ({result_zero['estimated_input_tokens']})"
    )


@run_test
def test_empty_report_text():
    """An empty report string should produce 0 output tokens."""
    result = _estimate_usage_from_output(
        report_text="",
        duration_seconds=120,
        grounded=False,
    )
    assert result["output_bytes"] == 0, f"Expected 0 output bytes, got {result['output_bytes']}"
    assert result["estimated_output_tokens"] == 0, (
        f"Expected 0 output tokens, got {result['estimated_output_tokens']}"
    )


@run_test
def test_context_cost_single_file_vs_directory():
    """_estimate_context_cost should work for both a single file and a directory containing it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "hello.py"
        test_file.write_text("print('hello world')\n")

        # Single file
        file_result = _estimate_context_cost(test_file)
        assert file_result["files"] == 1, f"Single file: expected 1, got {file_result['files']}"
        assert file_result["total_bytes"] > 0

        # Directory containing the file
        dir_result = _estimate_context_cost(Path(tmpdir))
        assert dir_result["files"] == 1, f"Directory: expected 1, got {dir_result['files']}"
        assert dir_result["total_bytes"] == file_result["total_bytes"], (
            f"Byte counts should match: file={file_result['total_bytes']}, dir={dir_result['total_bytes']}"
        )
        assert dir_result["estimated_cost_usd"] == file_result["estimated_cost_usd"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print()
    total = len(_results)
    passed = sum(1 for _, ok, _ in _results if ok)
    failed = total - passed
    print()
    print(f"Results: {passed}/{total} passed, {failed} failed")

    if failed:
        print("\nFailed tests:")
        for name, ok, tb in _results:
            if not ok:
                print(f"\n--- {name} ---")
                print(tb)
        sys.exit(1)
    else:
        print("All tests passed.")
        sys.exit(0)
