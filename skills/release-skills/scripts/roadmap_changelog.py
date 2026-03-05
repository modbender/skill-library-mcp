#!/usr/bin/env python3
"""
roadmap_changelog.py -- Generate changelog entries from completed roadmap items.

Reads roadmap.md (or TODO.md as fallback), finds completed items since a given
date, categorizes them by changelog type, cross-references against CHANGELOG.md
to avoid duplicates, and outputs in Keep a Changelog format.

Usage:
    python roadmap_changelog.py                          # generate from roadmap.md
    python roadmap_changelog.py --source TODO.md         # use TODO.md instead
    python roadmap_changelog.py --since "2024-01-01"     # since date
    python roadmap_changelog.py --version "1.3.0"        # set version
    python roadmap_changelog.py --append                 # append to CHANGELOG.md
    python roadmap_changelog.py --dry-run                # preview only

No external dependencies required (stdlib only).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CHANGELOG_CATEGORIES = [
    "Added", "Changed", "Fixed", "Removed", "Security", "Deprecated",
]

# Keywords that map completed items to changelog categories.
# Order matters — first match wins.
CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("Security", [
        r"\bsecurity\b", r"\bauth\b", r"\bvulnerab", r"\baudit\b",
        r"\bCVE\b", r"\bencrypt", r"\bsecret",
    ]),
    ("Fixed", [
        r"\bfix\b", r"\bbug\b", r"\bresolve[ds]?\b", r"\bpatch\b",
        r"\bhotfix\b", r"\bcorrect\b", r"\brepair\b",
    ]),
    ("Removed", [
        r"\bremov\w+", r"\bdelet\w+", r"\bdrop\w+", r"\bdeprecated\b.*remov",
        r"\bstrip\b",
    ]),
    ("Deprecated", [
        r"\bdeprecat\w+",
    ]),
    ("Changed", [
        r"\bupdat\w+", r"\brefactor\w*", r"\breorganiz\w+", r"\brestruc\w+",
        r"\bimprov\w+", r"\benhance\w+", r"\bmigrat\w+", r"\bmov\w+ .+ to\b",
        r"\bexpand\w*", r"\brename\w*", r"\bconvert\w*",
    ]),
    # Default — anything else is "Added"
    ("Added", []),
]

# Regex for completed checkbox items: lines starting with `- [x]`
COMPLETED_RE = re.compile(
    r"^[\s]*-\s+\[x\]\s+(.+)$", re.MULTILINE | re.IGNORECASE
)

# Match a "Completed:" trailing line that often follows the checkbox line
COMPLETED_DATE_RE = re.compile(r"Completed.*?(\d{4}-\d{2}-\d{2})")

# Strip priority tags like `[high]`, `[medium]`, `[low]`
PRIORITY_RE = re.compile(r"\s*`\[(?:high|medium|low)\]`\s*")

# Strip bold markers
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


# ---------------------------------------------------------------------------
# Terminal colors
# ---------------------------------------------------------------------------
def _has_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

_COLOR = _has_color()

def _c(code: str, t: str) -> str:
    return f"\033[{code}m{t}\033[0m" if _COLOR else t

def bold(t: str) -> str:   return _c("1", t)
def dim(t: str) -> str:    return _c("2", t)
def cyan(t: str) -> str:   return _c("36", t)
def green(t: str) -> str:  return _c("32", t)
def yellow(t: str) -> str: return _c("33", t)
def red(t: str) -> str:    return _c("31", t)


# ---------------------------------------------------------------------------
# Source file resolution
# ---------------------------------------------------------------------------
def resolve_source(explicit: Optional[str]) -> Optional[Path]:
    """Find the roadmap/TODO source file.  Priority:
    1. Explicitly provided path
    2. roadmap.md
    3. TODO.md
    """
    if explicit:
        p = Path(explicit)
        return p if p.is_file() else None

    for candidate in ("roadmap.md", "TODO.md"):
        p = Path(candidate)
        if p.is_file():
            return p
    return None


# ---------------------------------------------------------------------------
# Parsing completed items
# ---------------------------------------------------------------------------
def parse_completed_items(text: str, since: Optional[str]) -> list[dict[str, str]]:
    """Extract completed checkbox items from markdown text.

    Each item is a dict with keys: 'raw', 'summary', 'detail', 'section'.
    Items are filtered by *since* date if a 'Completed:' annotation or
    surrounding context contains a date.
    """
    lines = text.splitlines()
    items: list[dict[str, str]] = []
    current_section = ""

    for i, line in enumerate(lines):
        # Track the current H3 section heading
        h3 = re.match(r"^###\s+(.+)", line)
        if h3:
            current_section = h3.group(1).strip()
            continue

        m = re.match(r"^[\s]*-\s+\[x\]\s+(.+)$", line, re.IGNORECASE)
        if not m:
            continue

        raw = m.group(1).strip()

        # Look ahead for a "Completed:" line with a date (up to 5 lines)
        item_date: Optional[str] = None
        for j in range(i + 1, min(i + 6, len(lines))):
            dm = COMPLETED_DATE_RE.search(lines[j])
            if dm:
                item_date = dm.group(1)
                break
            # Stop scanning at the next checkbox or heading
            if re.match(r"^[\s]*-\s+\[", lines[j]) or re.match(r"^##", lines[j]):
                break

        # Filter by since date
        if since and item_date:
            if item_date < since:
                continue

        # Build a clean summary
        summary = _clean_summary(raw)

        # Gather the indented detail block (lines indented under this item)
        detail_lines: list[str] = []
        for j in range(i + 1, len(lines)):
            nxt = lines[j]
            if nxt.strip() == "":
                detail_lines.append("")
                continue
            if nxt.startswith("  ") or nxt.startswith("\t"):
                detail_lines.append(nxt.strip())
            else:
                break
        detail = " ".join(l for l in detail_lines if l).strip()

        items.append({
            "raw": raw,
            "summary": summary,
            "detail": detail,
            "section": current_section,
            "date": item_date or "",
        })

    return items


def _clean_summary(raw: str) -> str:
    """Produce a concise one-line summary from a raw checkbox label."""
    text = PRIORITY_RE.sub("", raw)
    # Un-bold
    text = BOLD_RE.sub(r"\1", text)
    # Remove trailing colon descriptions after first sentence
    text = text.split(":")[0] if ":" in text else text
    # Trim leading/trailing junk
    text = text.strip(" *")
    return text


# ---------------------------------------------------------------------------
# Categorization
# ---------------------------------------------------------------------------
def categorize(item: dict[str, str]) -> str:
    """Assign a Keep a Changelog category to an item."""
    blob = f"{item['raw']} {item['detail']}".lower()
    for category, patterns in CATEGORY_RULES:
        for pat in patterns:
            if re.search(pat, blob, re.IGNORECASE):
                return category
    return "Added"


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------
def load_existing_entries(changelog_path: Path) -> set[str]:
    """Load existing changelog entries to avoid duplicates.

    Returns a set of normalised entry strings (lowercase, stripped of
    leading '- ' and whitespace) for fuzzy matching.
    """
    if not changelog_path.is_file():
        return set()

    entries: set[str] = set()
    text = changelog_path.read_text()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            normalised = stripped[2:].strip().lower()
            # Also store a condensed version (alpha-only) for fuzzy match
            condensed = re.sub(r"[^a-z0-9]", "", normalised)
            entries.add(normalised)
            if condensed:
                entries.add(condensed)
    return entries


def is_duplicate(summary: str, existing: set[str]) -> bool:
    """Check whether a summary already appears in the changelog."""
    norm = summary.strip().lower()
    condensed = re.sub(r"[^a-z0-9]", "", norm)
    if norm in existing:
        return True
    if condensed and condensed in existing:
        return True
    return False


# ---------------------------------------------------------------------------
# Changelog generation
# ---------------------------------------------------------------------------
def build_changelog(
    items: list[dict[str, str]],
    version: str,
    today: str,
    existing: set[str],
) -> tuple[str, int, int]:
    """Build a changelog section in Keep a Changelog format.

    Returns (changelog_text, included_count, duplicate_count).
    """
    categorised: dict[str, list[str]] = {cat: [] for cat in CHANGELOG_CATEGORIES}
    duplicates = 0

    for item in items:
        if is_duplicate(item["summary"], existing):
            duplicates += 1
            continue
        cat = categorize(item)
        # Build the entry line with optional detail
        entry = item["summary"]
        detail = item.get("detail", "")
        # If detail has a "Completed:" note, extract the useful part
        completed_m = re.match(r"^Completed:\s*(.+)", detail)
        if completed_m:
            extra = completed_m.group(1).strip()
            if extra and len(extra) < 120:
                entry = f"{entry} — {extra}"
        categorised[cat].append(entry)

    # Build markdown
    lines: list[str] = [f"## [{version}] — {today}", ""]
    included = 0
    for cat in CHANGELOG_CATEGORIES:
        entries = categorised[cat]
        if not entries:
            continue
        lines.append(f"### {cat}")
        for e in entries:
            lines.append(f"- {e}")
            included += 1
        lines.append("")

    if included == 0:
        lines.append("No new entries.")
        lines.append("")

    return "\n".join(lines), included, duplicates


# ---------------------------------------------------------------------------
# Append to CHANGELOG.md
# ---------------------------------------------------------------------------
def append_to_changelog(changelog_path: Path, new_section: str) -> None:
    """Insert the new section into CHANGELOG.md after the header."""
    if not changelog_path.is_file():
        # Create a new file with Keep a Changelog header
        header = (
            "# Changelog\n\n"
            "All notable changes to this project will be documented in this file.\n\n"
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).\n\n"
        )
        changelog_path.write_text(header + new_section)
        return

    content = changelog_path.read_text()

    # Insert after the header block (first ## or end of preamble)
    insert_re = re.search(r"^## ", content, re.MULTILINE)
    if insert_re:
        pos = insert_re.start()
        updated = content[:pos] + new_section + "\n" + content[pos:]
    else:
        updated = content.rstrip("\n") + "\n\n" + new_section

    changelog_path.write_text(updated)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate changelog entries from completed roadmap/TODO items.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python roadmap_changelog.py\n"
            '  python roadmap_changelog.py --source TODO.md\n'
            '  python roadmap_changelog.py --since "2024-01-01"\n'
            '  python roadmap_changelog.py --version "1.3.0"\n'
            "  python roadmap_changelog.py --append\n"
            "  python roadmap_changelog.py --dry-run\n"
        ),
    )
    p.add_argument("--source", metavar="FILE", default=None,
                   help="Source file (default: roadmap.md, fallback: TODO.md)")
    p.add_argument("--since", metavar="DATE", default=None,
                   help="Only include items completed since this date (YYYY-MM-DD)")
    p.add_argument("--version", metavar="VER", default=None,
                   help="Version label for the changelog section (default: Unreleased)")
    p.add_argument("--changelog", metavar="FILE", default="CHANGELOG.md",
                   help="Path to CHANGELOG.md for dedup / append (default: CHANGELOG.md)")
    p.add_argument("--append", action="store_true",
                   help="Append the generated section to CHANGELOG.md")
    p.add_argument("--dry-run", action="store_true",
                   help="Preview output without writing anything")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Validate --since date
    if args.since:
        try:
            datetime.strptime(args.since[:10], "%Y-%m-%d")
        except ValueError:
            print(red(f"Invalid date format: {args.since}. Use YYYY-MM-DD."),
                  file=sys.stderr)
            return 1

    # Resolve source file
    source = resolve_source(args.source)
    if source is None:
        tried = args.source or "roadmap.md / TODO.md"
        print(red(f"Source file not found: {tried}"), file=sys.stderr)
        return 1

    print(dim(f"Reading: {source}"))

    text = source.read_text()
    items = parse_completed_items(text, args.since)

    if not items:
        print(yellow("No completed items found."))
        return 0

    print(dim(f"Found {len(items)} completed item(s)"))

    # Cross-reference with existing changelog
    changelog_path = Path(args.changelog)
    existing = load_existing_entries(changelog_path)

    version = args.version or "Unreleased"
    today = date.today().isoformat()

    changelog_text, included, duplicates = build_changelog(
        items, version, today, existing,
    )

    # Print summary
    if duplicates:
        print(dim(f"Skipped {duplicates} duplicate(s) already in {args.changelog}"))
    print(dim(f"Included {included} entry/entries\n"))

    # Output
    if args.dry_run:
        print(cyan("=== DRY RUN — preview only ===\n"))

    print(changelog_text)

    if args.append and not args.dry_run:
        append_to_changelog(changelog_path, changelog_text)
        print(green(f"Appended to {changelog_path}"))
    elif args.append and args.dry_run:
        print(dim(f"Would append to {changelog_path} (dry-run, skipped)"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
