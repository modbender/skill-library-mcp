#!/usr/bin/env python3
"""
merge_chapters.py — Merge chapter files into a single manuscript.

Discovery order:
  1. chapters/introduction.md (if exists)
  2. chapters/chapter-01.md through chapter-NN.md (sorted, glob-based)

Usage:
  python3 scripts/merge_chapters.py [--output book/manuscript.md] [--title "Book Title"] [--author "Author"]
"""

import os
import re
import glob
import argparse

def clean_content(text):
    return text.strip()

def get_chapter_title(content, fallback="Untitled Chapter"):
    match = re.search(r'^# (.+)', content, re.MULTILINE)
    return match.group(1).strip() if match else fallback

def discover_chapters(chapters_dir="chapters"):
    ordered = []
    intro = os.path.join(chapters_dir, "introduction.md")
    if os.path.exists(intro):
        ordered.append(intro)

    # Glob chapter files, exclude outlines and variants (e.g. chapter-01-outline.md, chapter-03-old.md)
    pattern = os.path.join(chapters_dir, "chapter-*.md")
    candidates = sorted(glob.glob(pattern))
    for f in candidates:
        basename = os.path.basename(f)
        # Only include canonical chapter files: chapter-NN.md
        if re.match(r'^chapter-\d{2}\.md$', basename):
            ordered.append(f)

    return ordered

def build_manuscript(files, title="Book Title", author="Author", date=None):
    import datetime
    date = date or datetime.date.today().isoformat()

    frontmatter = f"""---
title: "{title}"
author: "{author}"
date: "{date}"
---

# {title}

*by {author}*

---

## Table of Contents

"""
    toc_lines = []
    chapter_blocks = []

    for f in files:
        if not os.path.exists(f):
            print(f"WARNING: {f} not found, skipping.")
            continue
        with open(f) as fh:
            content = fh.read()
        chapter_title = get_chapter_title(content, fallback=os.path.basename(f))
        anchor = re.sub(r'[^a-z0-9]+', '-', chapter_title.lower()).strip('-')
        toc_lines.append(f"- [{chapter_title}](#{anchor})")
        chapter_blocks.append("\n\n---\n\n" + clean_content(content))

    toc = "\n".join(toc_lines)
    body = "".join(chapter_blocks)
    return frontmatter + toc + body + "\n"

def main():
    parser = argparse.ArgumentParser(description="Merge chapter files into a manuscript.")
    parser.add_argument("--output", default="book/manuscript.md")
    parser.add_argument("--title", default="Book Title")
    parser.add_argument("--author", default="Author")
    parser.add_argument("--chapters-dir", default="chapters")
    args = parser.parse_args()

    files = discover_chapters(args.chapters_dir)
    if not files:
        print(f"No chapter files found in {args.chapters_dir}/")
        return

    print(f"Merging {len(files)} files: {[os.path.basename(f) for f in files]}")
    manuscript = build_manuscript(files, title=args.title, author=args.author)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as fh:
        fh.write(manuscript)

    word_count = len(manuscript.split())
    print(f"Written to {args.output} — {word_count:,} words")

if __name__ == "__main__":
    main()
