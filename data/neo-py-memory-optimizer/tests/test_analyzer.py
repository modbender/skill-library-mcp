#!/usr/bin/env python3
"""Tests for the analyzer module."""

import os
import sys
import pytest

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import analyzer
import optimizer
import utils


# ---------------------------------------------------------------------------
# analyzer.analyze_source tests
# ---------------------------------------------------------------------------

class TestUnclosedFile:
    def test_detects_open_without_with(self):
        code = "f = open('test.txt', 'r')\ndata = f.read()\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "unclosed_file" in types

    def test_no_issue_with_context_manager(self):
        code = "with open('test.txt', 'r') as f:\n    data = f.read()\n"
        issues = analyzer.analyze_source(code, "test.py")
        unclosed = [i for i in issues if i["type"] == "unclosed_file"]
        assert len(unclosed) == 0

    def test_captures_file_arg(self):
        code = "f = open('myfile.csv')\n"
        issues = analyzer.analyze_source(code, "test.py")
        unclosed = [i for i in issues if i["type"] == "unclosed_file"]
        assert len(unclosed) == 1
        assert unclosed[0]["file_arg"] == "myfile.csv"

    def test_no_file_arg_for_variable(self):
        code = "f = open(some_var)\n"
        issues = analyzer.analyze_source(code, "test.py")
        unclosed = [i for i in issues if i["type"] == "unclosed_file"]
        assert len(unclosed) == 1
        assert unclosed[0]["file_arg"] is None


class TestListComprehension:
    def test_detects_list_comprehension(self):
        code = "result = [x for x in range(10)]\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "large_list_comprehension" in types

    def test_estimates_range_size(self):
        code = "result = [x for x in range(50000)]\n"
        issues = analyzer.analyze_source(code, "test.py")
        comp = [i for i in issues if i["type"] == "large_list_comprehension"]
        assert len(comp) == 1
        assert comp[0]["size_estimate"] == 50000
        assert comp[0]["severity"] == "high"

    def test_small_range_is_low_severity(self):
        code = "result = [x for x in range(5)]\n"
        issues = analyzer.analyze_source(code, "test.py")
        comp = [i for i in issues if i["type"] == "large_list_comprehension"]
        assert len(comp) == 1
        assert comp[0]["severity"] == "low"

    def test_unknown_iterable_is_medium(self):
        code = "result = [x for x in some_function()]\n"
        issues = analyzer.analyze_source(code, "test.py")
        comp = [i for i in issues if i["type"] == "large_list_comprehension"]
        assert len(comp) == 1
        assert comp[0]["severity"] == "medium"


class TestStringConcatInLoop:
    def test_detects_concat_in_for_loop(self):
        code = "s = ''\nfor x in items:\n    s += str(x)\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "string_concat_in_loop" in types

    def test_detects_concat_in_while_loop(self):
        code = "s = ''\nwhile True:\n    s += 'x'\n    break\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "string_concat_in_loop" in types

    def test_no_issue_outside_loop(self):
        code = "s = 'hello'\ns += ' world'\n"
        issues = analyzer.analyze_source(code, "test.py")
        concat = [i for i in issues if i["type"] == "string_concat_in_loop"]
        assert len(concat) == 0


class TestMutableDefaultArg:
    def test_detects_list_default(self):
        code = "def func(items=[]):\n    pass\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "mutable_default_arg" in types

    def test_detects_dict_default(self):
        code = "def func(config={}):\n    pass\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "mutable_default_arg" in types

    def test_no_issue_with_none_default(self):
        code = "def func(items=None):\n    pass\n"
        issues = analyzer.analyze_source(code, "test.py")
        mutable = [i for i in issues if i["type"] == "mutable_default_arg"]
        assert len(mutable) == 0


class TestUnnecessaryListCall:
    def test_detects_list_wrapping_generator(self):
        code = "result = list(x * 2 for x in data)\n"
        issues = analyzer.analyze_source(code, "test.py")
        types = [i["type"] for i in issues]
        assert "unnecessary_list_call" in types


# ---------------------------------------------------------------------------
# optimizer.generate_suggestion tests
# ---------------------------------------------------------------------------

class TestOptimizer:
    def test_unclosed_file_suggestion(self):
        issue = {"type": "unclosed_file", "file_arg": "data.csv"}
        result = optimizer.generate_suggestion(issue)
        assert "suggestion" in result
        assert "context manager" in result["suggestion"]
        assert "example" in result
        assert "data.csv" in result["example"]

    def test_list_comprehension_suggestion(self):
        issue = {"type": "large_list_comprehension", "severity": "high"}
        result = optimizer.generate_suggestion(issue)
        assert "generator" in result["suggestion"].lower()
        assert "estimated_savings" in result

    def test_string_concat_suggestion(self):
        issue = {"type": "string_concat_in_loop"}
        result = optimizer.generate_suggestion(issue)
        assert "join" in result["suggestion"]

    def test_mutable_default_suggestion(self):
        issue = {"type": "mutable_default_arg"}
        result = optimizer.generate_suggestion(issue)
        assert "None" in result["suggestion"]

    def test_unknown_type_returns_generic(self):
        issue = {"type": "unknown_pattern_xyz"}
        result = optimizer.generate_suggestion(issue)
        assert "suggestion" in result


# ---------------------------------------------------------------------------
# utils tests
# ---------------------------------------------------------------------------

class TestUtils:
    def test_get_source_segment(self):
        import ast as _ast

        code = "a = 1\nb = 2\nc = 3\n"
        tree = _ast.parse(code)
        # First statement node
        node = tree.body[0]
        segment = utils.get_source_segment(code, node)
        assert "a = 1" in segment

    def test_severity_rank(self):
        assert utils.severity_rank("high") > utils.severity_rank("low")
        assert utils.severity_rank("critical") > utils.severity_rank("high")
        assert utils.severity_rank("unknown") == 0

    def test_count_by_severity(self):
        issues = [
            {"severity": "high"},
            {"severity": "low"},
            {"severity": "high"},
        ]
        counts = utils.count_by_severity(issues)
        assert counts["high"] == 2
        assert counts["low"] == 1


# ---------------------------------------------------------------------------
# Integration: analyze sample files
# ---------------------------------------------------------------------------

class TestSampleFiles:
    ASSETS_DIR = os.path.join(
        os.path.dirname(__file__), "..", "assets", "sample_code"
    )

    def test_bad_practices_has_issues(self):
        path = os.path.join(self.ASSETS_DIR, "bad_practices.py")
        with open(path, "r") as f:
            source = f.read()
        issues = analyzer.analyze_source(source, path)
        assert len(issues) > 0
        types = {i["type"] for i in issues}
        assert "unclosed_file" in types
        assert "large_list_comprehension" in types
        assert "mutable_default_arg" in types

    def test_clean_code_has_fewer_issues(self):
        path = os.path.join(self.ASSETS_DIR, "clean_code.py")
        with open(path, "r") as f:
            source = f.read()
        issues = analyzer.analyze_source(source, path)
        # Clean code may still have some detected patterns (e.g. generator expr
        # inside sum is fine but list comp would be flagged). It should have
        # zero unclosed_file and zero mutable_default_arg issues.
        unclosed = [i for i in issues if i["type"] == "unclosed_file"]
        mutable = [i for i in issues if i["type"] == "mutable_default_arg"]
        assert len(unclosed) == 0
        assert len(mutable) == 0
