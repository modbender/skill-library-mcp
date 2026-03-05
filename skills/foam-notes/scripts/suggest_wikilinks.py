#!/usr/bin/env python3
"""
Suggest wikilinks for a note based on existing notes in the archive.

Analyzes note content and identifies words/phrases that match existing note titles,
suggesting them as potential wikilinks.

Usage:
    python3 suggest_wikilinks.py <note-file>
    python3 suggest_wikilinks.py my-note.md
    python3 suggest_wikilinks.py my-note.md --min-length 4

Examples:
    python3 suggest_wikilinks.py meeting-notes.md
    python3 suggest_wikilinks.py research/paper.md --foam-root ~/notes
    python3 suggest_wikilinks.py idea.md --auto-apply  # Apply all non-conflicting
"""

import argparse
import re
import sys
from pathlib import Path
from difflib import SequenceMatcher

from foam_config import load_config, get_foam_root, get_wikilink_config


def similarity(a: str, b: str) -> float:
    """Calculate string similarity (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _stem_matches_title(stem: str, title: str, suffixes: tuple = ()) -> bool:
    """Check whether an H1 title is close enough to the filename stem to be
    used as an independent match key.

    We normalise hyphens/underscores to spaces and compare.  If the title is
    just a cleaned-up version of the stem (e.g. "Docker Networking" from
    "docker-networking") it passes.  Wildly different pairs like "Home" from
    "index" do not.
    """
    norm_stem = stem.lower().replace("-", " ").replace("_", " ")
    norm_title = title.lower()
    # Exact (after normalisation)
    if norm_stem == norm_title:
        return True
    # One contains the other
    if norm_stem in norm_title or norm_title in norm_stem:
        return True
    # Also allow suffix-stripped stem
    for suffix in suffixes:
        if norm_stem.endswith(suffix.replace("-", " ")):
            stripped = norm_stem[: -len(suffix.replace("-", " "))].strip()
            if (
                stripped == norm_title
                or norm_title in stripped
                or stripped in norm_title
            ):
                return True
    # Fuzzy similarity (catches minor differences like plurals, typos)
    if similarity(norm_stem, norm_title) >= 0.7:
        return True
    return False


def get_all_note_titles(
    foam_root: Path,
    title_stopwords: frozenset = frozenset(),
    suffixes: tuple = (),
) -> dict:
    """Get all note titles and their file paths.

    Keys are lowercased strings that will be matched against note content.
    Each note can register multiple keys:
      - filename stem  (always)
      - stem without configured suffix  (if applicable, lower priority than a
        note whose stem matches exactly)
      - H1 title  (only if it resembles the stem or is multi-word)

    Args:
        foam_root: Path to the Foam workspace root.
        title_stopwords: Words that should never be used as match keys
            (too generic / ambiguous). Loaded from config.json wikilinks.title_stopwords.
        suffixes: Filename suffixes whose base stem should also be registered
            as a match key. Loaded from config.json wikilinks.suffixes.
    """
    titles = {}
    suffix_keys = set()  # keys registered via suffix stripping (protected)

    for md_file in foam_root.rglob("*.md"):
        # Skip hidden directories and journals
        rel_path = md_file.relative_to(foam_root)
        if any(part.startswith(".") for part in rel_path.parts):
            continue

        try:
            content = md_file.read_text()
            # Get title from first h1 or filename
            title = None
            for line in content.split("\n")[:10]:
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            if not title:
                title = md_file.stem.replace("-", " ").replace("_", " ")

            info = {
                "path": str(rel_path),
                "title": title,
                "stem": md_file.stem,
            }

            # 1) Register the full filename stem (unless it's a stopword)
            if md_file.stem.lower() not in title_stopwords:
                titles[md_file.stem.lower()] = info

            # 2) Register stem without configured suffix (don't overwrite an
            #    existing exact-stem entry — e.g. if both icedrive.md and
            #    icedrive-hub.md exist, icedrive.md wins)
            for suffix in suffixes:
                if md_file.stem.lower().endswith(suffix):
                    base = md_file.stem[: -len(suffix)]
                    base_key = base.lower()
                    if base_key not in titles:
                        titles[base_key] = info
                        suffix_keys.add(base_key)

            # 3) Register H1 title as a key only when safe:
            #    - skip stopwords
            #    - single-word titles must resemble the stem
            #    - multi-word titles are always registered (low collision risk)
            #    - never overwrite a suffix-derived key (suffix notes are the
            #      canonical target for bare topic words like "Foam")
            title_key = title.lower()
            if title_key not in title_stopwords and title_key not in suffix_keys:
                words = title.split()
                if len(words) >= 2:
                    # Multi-word title: always register
                    titles[title_key] = info
                elif _stem_matches_title(md_file.stem, title, suffixes):
                    # Single-word title that matches the stem: register
                    titles[title_key] = info
                # else: single-word title that doesn't match stem — skip

        except Exception:
            continue

    return titles


def _get_exclusion_zones(line: str) -> list:
    """Return list of (start, end) character ranges where wikilinks must not be inserted.

    Covers: inline code, existing wikilinks, markdown links/images, URLs, file paths,
    HTML tags/comments.
    """
    zones = []

    # Inline code: `...` (handles double-backtick too)
    for m in re.finditer(r"``[^`]+``|`[^`]+`", line):
        zones.append((m.start(), m.end()))

    # Existing wikilinks: [[...]]
    for m in re.finditer(r"\[\[[^\]]+\]\]", line):
        zones.append((m.start(), m.end()))

    # Markdown images and links: ![alt](url) and [text](url)
    for m in re.finditer(r"!?\[[^\]]*\]\([^)]*\)", line):
        zones.append((m.start(), m.end()))

    # Reference-style link definitions: [label]: url
    for m in re.finditer(r"^\s*\[[^\]]+\]:\s+\S+", line):
        zones.append((m.start(), m.end()))

    # URLs: http(s)://... or www.... (extend through spaces for broken URLs on bare lines)
    for m in re.finditer(r"https?://\S+|www\.\S+", line):
        zones.append((m.start(), m.end()))
    # Bare-URL line: if the line is basically just a URL (possibly with spaces in path),
    # exclude the entire line
    if re.match(r"^\s*https?://", line.strip()):
        zones.append((0, len(line)))

    # File paths: things like /foo/bar, ./foo, ../foo, or bare paths with slashes
    # that aren't URLs (already caught above)
    for m in re.finditer(r"(?<!\w)(?:\.{0,2}/[\w./_-]+)", line):
        zones.append((m.start(), m.end()))

    # Filename-like tokens: word.ext where ext is a common file extension
    for m in re.finditer(
        r"\b\w+\.(?:md|py|js|ts|json|yaml|yml|toml|html|css|sh|bash|txt|csv|pdf|png|jpg|xml|conf|cfg|ini|log|sql|r|R|qmd|rmd|bib|tex)\b",
        line,
    ):
        zones.append((m.start(), m.end()))

    # HTML tags and comments
    for m in re.finditer(r"<!--.*?-->|<[^>]+>", line):
        zones.append((m.start(), m.end()))

    # Quoted strings: "..." and '...' (don't linkify inside quotes)
    for m in re.finditer(r'"[^"]*"', line):
        zones.append((m.start(), m.end()))
    for m in re.finditer(r"'[^']*'", line):
        zones.append((m.start(), m.end()))

    return zones


def _in_exclusion_zone(start: int, end: int, zones: list) -> bool:
    """Check if range [start, end) overlaps any exclusion zone."""
    for zs, ze in zones:
        if start < ze and end > zs:
            return True
    return False


def find_wikilink_candidates(content: str, titles: dict, min_length: int = 3) -> list:
    """Find potential wikilink candidates in content."""
    candidates = []
    lines = content.split("\n")

    # Build regex patterns for multi-word titles
    title_patterns = []
    for key, info in titles.items():
        # Skip very short keys
        if len(key) < min_length:
            continue
        # Escape special regex chars but keep spaces
        pattern = re.escape(key)
        # Allow hyphens in stems to match spaces in prose
        # e.g. "agentic-coder" matches "agentic coder"
        pattern = pattern.replace(r"\-", r"[\- ]")
        # Allow optional trailing 's' for simple plural matching
        # e.g. "agentic coder" also matches "agentic coders"
        pattern = pattern + r"s?"
        title_patterns.append((pattern, info))

    # Sort by length (longest first) to prefer multi-word matches
    title_patterns.sort(key=lambda x: len(x[0]), reverse=True)

    # Track what we've already matched to avoid duplicates
    matched_positions = set()
    in_frontmatter = False
    frontmatter_seen = False  # only the first --- pair is frontmatter
    in_code_block = False

    for line_idx, line in enumerate(lines):
        stripped = line.strip()

        # Track YAML frontmatter (must start at line 0)
        if stripped == "---":
            if line_idx == 0 and not frontmatter_seen:
                in_frontmatter = True
                frontmatter_seen = True
                continue
            elif in_frontmatter:
                in_frontmatter = False
                continue

        if in_frontmatter:
            continue

        # Track fenced code blocks (``` or ~~~, possibly with language tag)
        if re.match(r"^(\s*)(```|~~~)", line):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        # Skip Markdown headings
        if stripped.startswith("#"):
            continue

        # Compute per-line exclusion zones
        zones = _get_exclusion_zones(line)

        for pattern, info in title_patterns:
            # Look for whole word matches
            # Use word boundaries for single words, allow flexible matching for multi-word
            if " " in pattern:
                regex = re.compile(pattern, re.IGNORECASE)
            else:
                regex = re.compile(r"\b" + pattern + r"\b", re.IGNORECASE)

            for match in regex.finditer(line):
                start = match.start()
                end = match.end()

                # Skip if already matched at this position
                pos = (line_idx, start)
                if pos in matched_positions:
                    continue

                # Skip if match overlaps any exclusion zone
                if _in_exclusion_zone(start, end, zones):
                    continue

                matched_positions.add(pos)

                candidates.append(
                    {
                        "line": line_idx + 1,
                        "column": start + 1,
                        "text": match.group(),
                        "target": info["stem"],
                        "target_title": info["title"],
                        "context": line.strip(),
                    }
                )

    # Collect targets already wikilinked in the content, so we don't
    # suggest a second link to the same note.
    already_linked = set()
    for m in re.finditer(r"\[\[([^\]|]+)\]\]", content):
        already_linked.add(m.group(1).lower())

    # First mention only: keep only the earliest occurrence per target note,
    # and skip targets that are already wikilinked elsewhere in the note.
    seen_targets = set()
    unique = []
    for c in candidates:
        target = c["target"].lower()
        if target in already_linked:
            continue
        if target not in seen_targets:
            seen_targets.add(target)
            unique.append(c)

    # Sort by line number
    unique.sort(key=lambda x: (x["line"], x["column"]))

    return unique


def format_suggestions(candidates: list) -> str:
    """Format candidates as numbered list."""
    if not candidates:
        return "No wikilink suggestions found."

    lines = [f"Found {len(candidates)} potential wikilink(s):\n"]

    for i, c in enumerate(candidates, 1):
        lines.append(f"{i}. Line {c['line']}, col {c['column']}")
        lines.append(f'   Text: "{c["text"]}"')
        lines.append(f"   Link to: [[{c['target']}]]")
        lines.append(f"   Context: ...{c['context'][:60]}...")
        lines.append("")

    lines.append("Respond with numbers to implement (e.g., '1 3 5'), 'all', or 'none'")
    return "\n".join(lines)


def apply_wikilinks(
    note_path: Path, candidates: list, selections: list, with_aliases: bool = False
) -> bool:
    """Apply selected wikilinks to the note."""
    if not selections:
        return False

    content = note_path.read_text()
    lines = content.split("\n")

    # Sort selections in reverse order (by line, then column) to apply from end to start
    # This preserves line/column positions as we modify
    to_apply = sorted(
        [(i, candidates[i - 1]) for i in selections if 1 <= i <= len(candidates)],
        key=lambda x: (-x[1]["line"], -x[1]["column"]),
    )

    for _, candidate in to_apply:
        line_idx = candidate["line"] - 1
        col_idx = candidate["column"] - 1
        text = candidate["text"]
        target = candidate["target"]

        line = lines[line_idx]
        # Replace the text with wikilink
        # Find the exact match at that position
        before = line[:col_idx]
        after = line[col_idx + len(text) :]

        # Create wikilink with or without alias
        if with_aliases:
            lines[line_idx] = before + f"[[{target}|{text}]]" + after
        else:
            lines[line_idx] = before + f"[[{target}]]" + after

    # Write back
    note_path.write_text("\n".join(lines))
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Suggest wikilinks for a note based on existing notes"
    )
    parser.add_argument(
        "note", help="Path to note file (relative to foam_root or absolute)"
    )
    parser.add_argument(
        "--foam-root", help="Foam workspace root directory (overrides config)"
    )
    parser.add_argument(
        "--min-length",
        "-m",
        type=int,
        default=3,
        help="Minimum word length to consider (default: 3)",
    )
    parser.add_argument(
        "--apply", "-a", help='Comma-separated list of numbers to apply (e.g., "1,3,5")'
    )
    parser.add_argument(
        "--auto-apply",
        action="store_true",
        help="Apply all non-conflicting suggestions without prompting",
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Show suggestions without applying"
    )
    parser.add_argument(
        "--with-aliases",
        action="store_true",
        help="Create wikilinks with aliases (e.g., [[target|text]]) instead of plain links",
    )

    args = parser.parse_args()

    # Get foam root
    config = load_config()
    if args.foam_root:
        foam_root = Path(args.foam_root).expanduser().resolve()
    else:
        foam_root = get_foam_root(config=config)

    if foam_root is None:
        print("Error: Not in a Foam workspace.", file=sys.stderr)
        print("Set foam_root in config.json or use --foam-root", file=sys.stderr)
        sys.exit(1)

    # Resolve note path
    note_path = Path(args.note)
    if not note_path.is_absolute():
        note_path = foam_root / note_path

    if not note_path.exists():
        print(f"Error: Note not found: {note_path}", file=sys.stderr)
        sys.exit(1)

    # Load wikilink config
    wl_config = get_wikilink_config(config)
    title_stopwords = frozenset(wl_config["title_stopwords"])
    suffixes = tuple(wl_config["suffixes"])
    min_length = args.min_length or wl_config["min_length"]

    # Get all note titles
    print("Scanning archive for note titles...")
    titles = get_all_note_titles(foam_root, title_stopwords, suffixes)
    print(f"Found {len(titles) // 2} unique notes.")

    # Read note content
    content = note_path.read_text()

    # Find candidates
    candidates = find_wikilink_candidates(content, titles, min_length)

    if not candidates:
        print("\nNo wikilink suggestions found.")
        print("The note doesn't contain text matching other note titles.")
        return

    # Show suggestions
    print(format_suggestions(candidates))

    # Dry run - stop here
    if args.dry_run:
        return

    # Auto-apply
    if args.auto_apply:
        selections = list(range(1, len(candidates) + 1))
        apply_wikilinks(note_path, candidates, selections, args.with_aliases)
        print(
            f"\nApplied {len(selections)} wikilink(s) to {note_path.relative_to(foam_root)}"
        )
        return

    # Apply specific selections
    if args.apply:
        try:
            selections = [int(x.strip()) for x in args.apply.split(",")]
            apply_wikilinks(note_path, candidates, selections, args.with_aliases)
            print(
                f"\nApplied {len(selections)} wikilink(s) to {note_path.relative_to(foam_root)}"
            )
        except ValueError:
            print("Error: --apply should be comma-separated numbers", file=sys.stderr)
            sys.exit(1)
        return

    # Interactive mode - prompt for input
    print("\nEnter selections (or 'all' for all, 'none' to cancel):")
    try:
        response = input("> ").strip()

        if response.lower() in ("none", "n", ""):
            print("No changes made.")
            return

        if response.lower() == "all":
            selections = list(range(1, len(candidates) + 1))
        else:
            selections = [int(x.strip()) for x in response.split()]

        apply_wikilinks(note_path, candidates, selections, args.with_aliases)
        print(
            f"\nApplied {len(selections)} wikilink(s) to {note_path.relative_to(foam_root)}"
        )

    except (ValueError, KeyboardInterrupt):
        print("\nNo changes made.")
        return


if __name__ == "__main__":
    main()
