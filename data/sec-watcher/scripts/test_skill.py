#!/usr/bin/env python3
"""
SEC Watcher — Test Suite
Validates parsing, formatting, signal classification, and edge cases
without hitting the live EDGAR API.
"""

import json
import sys
import os

# Add scripts dir to path so we can import the fetcher's functions
sys.path.insert(0, os.path.dirname(__file__))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "fetch_filings",
    os.path.join(os.path.dirname(__file__), "fetch-filings.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

HIGH_SIGNAL_ITEMS = _mod.HIGH_SIGNAL_ITEMS
MEDIUM_SIGNAL_ITEMS = _mod.MEDIUM_SIGNAL_ITEMS
WATCHLIST = _mod.WATCHLIST
format_filing_text = _mod.format_filing_text
_clean_display_name = _mod._clean_display_name

PASS = 0
FAIL = 0


def assert_eq(label, actual, expected):
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")
        print(f"     Expected: {expected}")
        print(f"     Got:      {actual}")


def assert_in(label, needle, haystack):
    global PASS, FAIL
    if needle in haystack:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")
        print(f"     '{needle}' not found in output")


# ---------------------------------------------------------------------------
# Test 1: Watchlist sanity
# ---------------------------------------------------------------------------
print("\n🧪 Test 1: Watchlist")
assert_eq("Watchlist has 30+ companies", len(WATCHLIST) >= 30, True)
assert_in("NVIDIA in watchlist", "NVIDIA", WATCHLIST)
assert_in("Palantir in watchlist", "Palantir", WATCHLIST)
assert_in("AMD in watchlist", "AMD", WATCHLIST)

# ---------------------------------------------------------------------------
# Test 2: Item code classification
# ---------------------------------------------------------------------------
print("\n🧪 Test 2: Signal classification")
assert_in("1.01 is HIGH signal", "1.01", HIGH_SIGNAL_ITEMS)
assert_in("5.02 is HIGH signal", "5.02", HIGH_SIGNAL_ITEMS)
assert_in("4.02 is HIGH signal", "4.02", HIGH_SIGNAL_ITEMS)
assert_in("7.01 is MEDIUM signal", "7.01", MEDIUM_SIGNAL_ITEMS)
assert_eq("Item 1.01 label", HIGH_SIGNAL_ITEMS["1.01"], "Material agreement")
assert_eq("Item 5.02 label", HIGH_SIGNAL_ITEMS["5.02"], "Director/officer departure or appointment")

# ---------------------------------------------------------------------------
# Test 3: display_names parsing
# ---------------------------------------------------------------------------
print("\n🧪 Test 3: display_names → entity_name")
assert_eq("Strip CIK suffix", _clean_display_name("NVIDIA CORP (CIK 0001045810)"), "NVIDIA CORP")
assert_eq("Strip lowercase CIK", _clean_display_name("Meta Platforms Inc (cik 001326801)"), "Meta Platforms Inc")
assert_eq("No CIK suffix unchanged", _clean_display_name("PALANTIR TECHNOLOGIES INC"), "PALANTIR TECHNOLOGIES INC")
assert_eq("Empty string safe", _clean_display_name(""), "")

# ---------------------------------------------------------------------------
# Test 4: Filing formatting
# ---------------------------------------------------------------------------
print("\n🧪 Test 4: Filing format output")

mock_filing_high = {
    "id": "test-001",
    "entity_name": "NVIDIA CORP",
    "form_type": "8-K",
    "file_date": "2026-02-18",
    "items": ["1.01", "5.02"],
    "items_description": "Material agreement, Director/officer departure or appointment",
    "file_description": "Current report",
    "signal_level": "HIGH",
    "accession_number": "0001045810-26-000123",
    "ciks": ["1045810"],
    "filing_url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000123/0001045810-26-000123-index.htm",
}

output = format_filing_text(mock_filing_high)
assert_in("Contains form type", "[8-K]", output)
assert_in("Contains company name", "NVIDIA CORP", output)
assert_in("Contains date", "2026-02-18", output)
assert_in("Contains signal level", "HIGH", output)
assert_in("Contains item codes", "1.01", output)
assert_in("HIGH signal gets red emoji", "🔴", output)

assert_in("Contains EDGAR link", "sec.gov", output)

mock_filing_medium = {
    "id": "test-002",
    "entity_name": "META PLATFORMS INC",
    "form_type": "8-K",
    "file_date": "2026-02-17",
    "items": ["7.01"],
    "items_description": "Regulation FD disclosure",
    "file_description": "Current report",
    "signal_level": "MEDIUM",
    "filing_url": "",
}

output_med = format_filing_text(mock_filing_medium)
assert_in("MEDIUM signal gets yellow emoji", "🟡", output_med)

mock_filing_low = {
    "id": "test-003",
    "entity_name": "CLOUDFLARE INC",
    "form_type": "10-Q",
    "file_date": "2026-02-15",
    "items": [],
    "items_description": "",
    "file_description": "Quarterly report",
    "signal_level": "LOW",
    "filing_url": "",
}

output_low = format_filing_text(mock_filing_low)
assert_in("LOW signal gets white emoji", "⚪", output_low)
assert_in("10-Q form type shown", "[10-Q]", output_low)

# ---------------------------------------------------------------------------
# Test 5: Edge cases
# ---------------------------------------------------------------------------
print("\n🧪 Test 5: Edge cases")

mock_empty = {
    "id": "",
    "entity_name": "",
    "form_type": "8-K",
    "file_date": "",
    "items": [],
    "items_description": "",
    "file_description": "",
    "signal_level": "LOW",
    "filing_url": "",
}

output_empty = format_filing_text(mock_empty)
assert_in("Empty entity still formats", "[8-K]", output_empty)
assert_eq("No crash on empty data", isinstance(output_empty, str), True)

# Filing with unknown signal level
mock_unknown = {**mock_empty, "signal_level": "UNKNOWN"}
output_unknown = format_filing_text(mock_unknown)
assert_in("Unknown signal gets white emoji fallback", "⚪", output_unknown)

# ---------------------------------------------------------------------------
# Test 6: SKILL.md frontmatter validation
# ---------------------------------------------------------------------------
print("\n🧪 Test 6: SKILL.md frontmatter")

skill_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
with open(skill_path, "r") as f:
    content = f.read()

# Check frontmatter delimiters
lines = content.split("\n")
assert_eq("Starts with ---", lines[0].strip(), "---")

# Find closing ---
closing_idx = None
for i, line in enumerate(lines[1:], 1):
    if line.strip() == "---":
        closing_idx = i
        break

assert_eq("Has closing frontmatter delimiter", closing_idx is not None, True)

# Check required fields
frontmatter = "\n".join(lines[1:closing_idx]) if closing_idx else ""
assert_in("Has name field", "name:", frontmatter)
assert_in("Has description field", "description:", frontmatter)
assert_in("Has metadata field", "metadata:", frontmatter)
assert_in("Name is sec-watcher", "sec-watcher", frontmatter)

# Check metadata is valid JSON
meta_line = [l for l in frontmatter.split("\n") if l.startswith("metadata:")][0]
meta_json_str = meta_line.replace("metadata:", "").strip()
try:
    meta = json.loads(meta_json_str)
    assert_eq("Metadata parses as JSON", True, True)
    assert_in("Has openclaw key", "openclaw", meta)
    assert_eq("Has emoji", meta["openclaw"].get("emoji"), "📊")
    assert_in("Requires python3", "python3", meta["openclaw"].get("requires", {}).get("bins", []))
except json.JSONDecodeError as e:
    assert_eq(f"Metadata parses as JSON (error: {e})", False, True)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'='*50}")
print(f" Results: {PASS} passed, {FAIL} failed")
print(f"{'='*50}")

sys.exit(1 if FAIL > 0 else 0)
