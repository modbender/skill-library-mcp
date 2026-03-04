#!/usr/bin/env python3
"""
Suggest tags for a note based on its content and existing tags in the archive.

Analyzes note content and existing tags to suggest relevant tags.

Usage:
    python3 suggest_tags.py <note-file>
    python3 suggest_tags.py my-note.md
    python3 suggest_tags.py my-note.md --min-count 2

Examples:
    python3 suggest_tags.py meeting-notes.md
    python3 suggest_tags.py research/paper.md --foam-root ~/notes
    python3 suggest_tags.py idea.md --apply 1,3,5  # Auto-apply selections
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from foam_config import load_config, get_foam_root, get_tags_config


def extract_existing_tags(foam_root: Path) -> dict:
    """Extract all existing tags from the archive."""
    tags_counter = Counter()
    tag_locations = {}

    for md_file in foam_root.rglob("*.md"):
        rel_path = md_file.relative_to(foam_root)
        if any(part.startswith(".") for part in rel_path.parts):
            continue

        try:
            content = md_file.read_text()

            # Find inline tags
            inline_pattern = r"#([a-zA-Z][\w/-]*)"
            for match in re.finditer(inline_pattern, content):
                tag = match.group(1).lower()
                # Filter out hex colors
                if not re.match(r"^[0-9a-fA-F]{6}$", tag):
                    tags_counter[tag] += 1
                    if tag not in tag_locations:
                        tag_locations[tag] = []
                    tag_locations[tag].append(str(rel_path))

            # Find frontmatter tags
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    fm = content[3:end]
                    # Look for tags: [...]
                    fm_tags = re.findall(r"tags:\s*\[([^\]]+)\]", fm)
                    for tag_list in fm_tags:
                        for tag in re.findall(r"[\'\"]?([^\s,\'\"]+)[\'\"]?", tag_list):
                            tag = tag.lower().strip()
                            if tag:
                                tags_counter[tag] += 1
                                if tag not in tag_locations:
                                    tag_locations[tag] = []
                                tag_locations[tag].append(str(rel_path))

        except Exception:
            continue

    return {"counts": dict(tags_counter), "locations": tag_locations}


def extract_content_tags(content: str, editorial_stopwords: set = None) -> set:
    """Extract potential tags from note content.

    Args:
        content: The note's markdown content.
        editorial_stopwords: Additional domain-specific words to exclude,
            loaded from config.json tags.editorial_stopwords.
    """
    # Remove code blocks and frontmatter
    clean_content = content
    if clean_content.startswith("---"):
        end = clean_content.find("---", 3)
        if end > 0:
            clean_content = clean_content[end + 3 :]

    # Remove code blocks
    clean_content = re.sub(r"```[\s\S]*?```", "", clean_content)
    clean_content = re.sub(r"`[^`]+`", "", clean_content)

    # Remove existing wikilinks and markdown links
    clean_content = re.sub(r"\[\[[^\]]+\]\]", "", clean_content)
    clean_content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean_content)

    # Remove punctuation except hyphens
    clean_content = re.sub(r"[^\w\s-]", " ", clean_content)

    # Extract words
    words = clean_content.lower().split()

    # NLP stopwords: common English function words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "my",
        "your",
        "his",
        "her",
        "its",
        "our",
        "their",
        "what",
        "which",
        "who",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "now",
        "then",
        "here",
        "there",
        "up",
        "down",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "once",
        "me",
        "him",
        "them",
        "us",
        "can",
        "may",
        "might",
        "must",
        "shall",
        "should",
        "from",
        "as",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "within",
        "without",
        "against",
    }

    # Merge in editorial stopwords from config
    if editorial_stopwords:
        stop_words |= editorial_stopwords

    potential = set()
    for word in words:
        word = word.strip("-")
        if len(word) >= 3 and word not in stop_words and not word.isdigit():
            potential.add(word)

    # Also look for multi-word phrases (2-3 words that appear together)
    lines = clean_content.split("\n")
    for line in lines:
        # Find phrases like "machine learning", "project management", etc.
        phrase_pattern = r"([a-z]{3,}(?:\s+[a-z]{3,}){1,2})"
        for match in re.finditer(phrase_pattern, line):
            phrase = match.group(1)
            words_in_phrase = phrase.split()
            if all(w not in stop_words for w in words_in_phrase):
                potential.add(phrase.replace(" ", "-"))

    return potential


def suggest_tags(
    note_content: str,
    existing_tags: dict,
    min_count: int = 1,
    editorial_stopwords: set = None,
) -> dict:
    """Suggest tags for a note."""
    content_tags = extract_content_tags(note_content, editorial_stopwords)
    existing = set(existing_tags["counts"].keys())

    suggestions = {"existing": [], "new": [], "content_keywords": []}

    # Find content words that match existing tags
    for tag in content_tags:
        if tag in existing:
            count = existing_tags["counts"][tag]
            if count >= min_count:
                suggestions["existing"].append(
                    {"tag": tag, "usage_count": count, "match_type": "content"}
                )
        else:
            # New tag suggestion
            suggestions["new"].append({"tag": tag, "match_type": "extracted"})

    # Sort existing by usage count
    suggestions["existing"].sort(key=lambda x: -x["usage_count"])

    # Sort new by tag length (prefer compound tags)
    suggestions["new"].sort(key=lambda x: len(x["tag"]), reverse=True)

    # Also suggest popular existing tags that might be relevant
    # based on similarity to content
    for tag, count in existing_tags["counts"].items():
        if count >= min_count and tag not in content_tags:
            # Check if any content word is similar
            for word in content_tags:
                if similarity(tag, word) > 0.7:
                    if tag not in [e["tag"] for e in suggestions["existing"]]:
                        suggestions["existing"].append(
                            {"tag": tag, "usage_count": count, "match_type": "similar"}
                        )
                    break

    return suggestions


def similarity(a: str, b: str) -> float:
    """Calculate string similarity."""
    if a == b:
        return 1.0
    # Simple similarity: common substring ratio
    shorter = min(len(a), len(b))
    matches = sum(1 for i in range(shorter) if a[i] == b[i])
    return matches / max(len(a), len(b))


def format_suggestions(suggestions: dict, existing_tags: dict) -> str:
    """Format tag suggestions as numbered list."""
    lines = []
    all_suggestions = []

    # Section 1: Existing tags found in content
    if suggestions["existing"]:
        lines.append("## Existing Tags (found in your content)")
        lines.append("")
        for i, s in enumerate(suggestions["existing"], 1):
            lines.append(f"{i}. #{s['tag']}")
            lines.append(f"   Used {s['usage_count']} time(s) in archive")
            if s["match_type"] == "content":
                lines.append(f"   ✓ Found in note content")
            elif s["match_type"] == "similar":
                lines.append(f"   ~ Similar to content")
            lines.append("")
            all_suggestions.append(s["tag"])
        start_new = len(suggestions["existing"]) + 1
    else:
        start_new = 1
        lines.append("No existing tags found in note content.")
        lines.append("")

    # Section 2: New tag suggestions
    if suggestions["new"]:
        lines.append("## New Tag Suggestions")
        lines.append("")
        # Show top 15 new suggestions
        for i, s in enumerate(suggestions["new"][:15], start_new):
            lines.append(f"{i}. #{s['tag']}")
            lines.append(f"   Extracted from content")
            lines.append("")
            all_suggestions.append(s["tag"])
    else:
        lines.append("No new tag suggestions from content.")

    lines.append("")
    lines.append(
        "Respond with numbers to add (e.g., '1 3 5'), 'all', 'existing', 'new', or 'none'"
    )
    lines.append("Or type custom tags to add (e.g., '#mytag #project')")

    return "\n".join(lines), all_suggestions


def apply_tags(note_path: Path, tags_to_add: list, mode: str = "inline") -> bool:
    """Add tags to note."""
    if not tags_to_add:
        return False

    content = note_path.read_text()

    # Clean up tags (remove # if present)
    clean_tags = [t.lstrip("#") for t in tags_to_add]

    if mode == "frontmatter":
        # Add to frontmatter
        if content.startswith("---"):
            # Has frontmatter
            end = content.find("---", 3)
            if end > 0:
                # Check if tags field exists
                fm = content[3:end]
                if "tags:" in fm:
                    # Append to existing tags
                    # This is tricky - need to parse YAML properly
                    # For now, add inline instead
                    mode = "inline"
                else:
                    # Add tags field
                    new_fm = fm.rstrip() + f"\ntags: [{', '.join(clean_tags)}]\n"
                    content = "---" + new_fm + content[end:]
        else:
            # No frontmatter, add one
            fm = f"---\ntags: [{', '.join(clean_tags)}]\n---\n\n"
            content = fm + content

    if mode == "inline":
        # Add tags at top of content (after frontmatter if present)
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                insert_pos = end + 3
                if not content[insert_pos:].startswith("\n"):
                    insert_pos = content.find("\n", insert_pos) + 1
            else:
                insert_pos = 0
        else:
            insert_pos = 0

        tag_line = " ".join(f"#{t}" for t in clean_tags) + "\n\n"
        content = content[:insert_pos] + tag_line + content[insert_pos:]

    note_path.write_text(content)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Suggest tags for a note based on content and existing tags"
    )
    parser.add_argument(
        "note", help="Path to note file (relative to foam_root or absolute)"
    )
    parser.add_argument(
        "--foam-root", help="Foam workspace root directory (overrides config)"
    )
    parser.add_argument(
        "--min-count",
        "-m",
        type=int,
        default=1,
        help="Minimum usage count for existing tags (default: 1)",
    )
    parser.add_argument(
        "--apply", "-a", help='Comma-separated numbers to apply (e.g., "1,3,5")'
    )
    parser.add_argument(
        "--frontmatter",
        "-f",
        action="store_true",
        help="Add tags to frontmatter instead of inline",
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true", help="Show suggestions without applying"
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

    # Load editorial stopwords from config
    tags_config = get_tags_config(config)
    editorial_stopwords = set(tags_config["editorial_stopwords"])

    # Extract existing tags
    print("Scanning archive for existing tags...")
    existing_tags = extract_existing_tags(foam_root)
    print(f"Found {len(existing_tags['counts'])} unique tags in archive.")

    # Read note content
    content = note_path.read_text()

    # Generate suggestions
    suggestions = suggest_tags(
        content, existing_tags, args.min_count, editorial_stopwords
    )

    if not suggestions["existing"] and not suggestions["new"]:
        print("\nNo tag suggestions found.")
        print("The note content didn't yield extractable keywords.")
        return

    # Format and show
    formatted, all_tags = format_suggestions(suggestions, existing_tags)
    print(formatted)

    # Dry run
    if args.dry_run:
        return

    # Auto-apply
    if args.apply:
        try:
            if args.apply.lower() == "all":
                selections = list(range(1, len(all_tags) + 1))
            elif args.apply.lower() == "existing":
                selections = list(range(1, len(suggestions["existing"]) + 1))
            elif args.apply.lower() == "new":
                start = len(suggestions["existing"]) + 1
                selections = list(range(start, len(all_tags) + 1))
            else:
                selections = [int(x.strip()) for x in args.apply.split(",")]

            tags_to_add = [
                all_tags[i - 1] for i in selections if 1 <= i <= len(all_tags)
            ]
            mode = "frontmatter" if args.frontmatter else "inline"
            apply_tags(note_path, tags_to_add, mode)
            print(
                f"\nAdded {len(tags_to_add)} tag(s) to {note_path.relative_to(foam_root)}"
            )
        except ValueError:
            print("Error: Invalid selection format", file=sys.stderr)
            sys.exit(1)
        return

    # Interactive mode
    print("\nEnter selections:")
    try:
        response = input("> ").strip()

        if response.lower() in ("none", "n", ""):
            print("No changes made.")
            return

        if response.lower() == "all":
            tags_to_add = all_tags
        elif response.lower() == "existing":
            tags_to_add = [s["tag"] for s in suggestions["existing"]]
        elif response.lower() == "new":
            tags_to_add = [s["tag"] for s in suggestions["new"]]
        elif response.startswith("#"):
            # Custom tags
            tags_to_add = [t.strip() for t in response.split()]
        else:
            # Numbers
            try:
                selections = [int(x.strip()) for x in response.split()]
                tags_to_add = [
                    all_tags[i - 1] for i in selections if 1 <= i <= len(all_tags)
                ]
            except ValueError:
                print("Invalid input. No changes made.")
                return

        mode = "frontmatter" if args.frontmatter else "inline"
        apply_tags(note_path, tags_to_add, mode)
        print(
            f"\nAdded {len(tags_to_add)} tag(s) to {note_path.relative_to(foam_root)}"
        )

    except (ValueError, KeyboardInterrupt):
        print("\nNo changes made.")
        return


if __name__ == "__main__":
    main()
