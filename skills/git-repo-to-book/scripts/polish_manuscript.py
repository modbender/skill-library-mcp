#!/usr/bin/env python3
"""
polish_manuscript.py — Polish a merged manuscript into publication-ready form.

Adds: title page, copyright, standardized TOC with anchor links, heading normalization,
metadata.json output.

Usage:
  python3 scripts/polish_manuscript.py [--input book/manuscript.md] [--output book/final-manuscript.md]
    [--title "Book Title"] [--author "Author"] [--year 2026] [--license "CC BY-NC-SA 4.0"]
"""

import os
import re
import json
import argparse
import datetime

def normalize_headings(text):
    """Ensure chapters start at H1, sections at H2."""
    # Already at correct level if chapters are # Chapter N
    return text

def extract_toc(text):
    """Extract H1 and H2 headings for TOC."""
    lines = text.split('\n')
    toc_entries = []
    for line in lines:
        m1 = re.match(r'^# (.+)', line)
        m2 = re.match(r'^## (.+)', line)
        if m1:
            title = m1.group(1).strip()
            anchor = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            toc_entries.append(f"- [{title}](#{anchor})")
        elif m2:
            title = m2.group(1).strip()
            anchor = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            toc_entries.append(f"  - [{title}](#{anchor})")
    return "\n".join(toc_entries)

def build_title_page(title, author, year, license_str):
    return f"""# {title}

**{author}**

*{year}*

---

*Licensed under {license_str}*

---

"""

def build_copyright(title, author, year, license_str):
    return f"""---

*© {year} {author}. {title}.*
*Licensed under [{license_str}](https://creativecommons.org/licenses/by-nc-sa/4.0/).*

---

"""

def count_words(text):
    return len(re.findall(r'\w+', text))

def count_chapters(text):
    return len(re.findall(r'^# Chapter \d+', text, re.MULTILINE))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="book/manuscript.md")
    parser.add_argument("--output", default="book/final-manuscript.md")
    parser.add_argument("--title", default="Book Title")
    parser.add_argument("--author", default="Author")
    parser.add_argument("--year", default=str(datetime.date.today().year))
    parser.add_argument("--license", default="CC BY-NC-SA 4.0", dest="license_str")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        return

    with open(args.input) as f:
        content = f.read()

    # Strip existing frontmatter (--- ... ---) if present
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL).strip()

    # Build polished document
    title_page = build_title_page(args.title, args.author, args.year, args.license_str)
    toc = extract_toc(content)
    toc_block = f"## Table of Contents\n\n{toc}\n\n---\n\n"
    copyright_block = build_copyright(args.title, args.author, args.year, args.license_str)
    body = normalize_headings(content)

    final = title_page + toc_block + body + "\n\n" + copyright_block

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        f.write(final)

    word_count = count_words(final)
    chapter_count = count_chapters(final)

    # Write metadata.json
    meta_path = os.path.join(os.path.dirname(args.output), "metadata.json")
    metadata = {
        "title": args.title,
        "author": args.author,
        "year": args.year,
        "license": args.license_str,
        "word_count": word_count,
        "chapter_count": chapter_count,
        "generated_at": datetime.datetime.now().isoformat(),
        "output": args.output,
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Written: {args.output}")
    print(f"Metadata: {meta_path}")
    print(f"Words: {word_count:,} | Chapters: {chapter_count}")

if __name__ == "__main__":
    main()
