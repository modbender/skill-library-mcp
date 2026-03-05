#!/usr/bin/env python3
"""
Create a new multilingual blog post for Astro.

Usage:
    python astro-new-post.py --title "My Post" --langs en,es,fr
    python astro-new-post.py --title "My Post" --langs en,es,fr --dir src/content/blog
"""

import argparse
import os
from datetime import datetime
from pathlib import Path


def create_post(title: str, lang: str, content_dir: Path, author: str = "", tags: list = None) -> Path:
    """Create a markdown file for a specific language."""
    
    # Create language directory
    lang_dir = content_dir / lang
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate slug from title
    slug = title.lower().replace(" ", "-").replace("'", "")
    for char in [",", ".", "!", "?", ":", ";"]:
        slug = slug.replace(char, "")
    
    # Create filename
    filename = f"{slug}.md"
    filepath = lang_dir / filename
    
    # Check if file already exists
    if filepath.exists():
        print(f"⚠️  File already exists: {filepath}")
        return filepath
    
    # Generate frontmatter
    today = datetime.now().strftime("%Y-%m-%d")
    tags_str = str(tags) if tags else "[]"
    
    frontmatter = f"""---
title: "{title}"
description: ""
pubDate: {today}
author: "{author}"
lang: "{lang}"
tags: {tags_str}
---

# {title}

Write your content here...
"""
    
    # Write file
    filepath.write_text(frontmatter, encoding="utf-8")
    print(f"✅ Created: {filepath}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Create a new multilingual blog post for Astro"
    )
    parser.add_argument(
        "--title", "-t",
        required=True,
        help="Post title"
    )
    parser.add_argument(
        "--langs", "-l",
        default="en",
        help="Comma-separated language codes (e.g., en,es,fr)"
    )
    parser.add_argument(
        "--dir", "-d",
        default="src/content/blog",
        help="Content directory path (default: src/content/blog)"
    )
    parser.add_argument(
        "--author", "-a",
        default="",
        help="Author name"
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags (e.g., tutorial,astro)"
    )
    
    args = parser.parse_args()
    
    # Parse languages
    langs = [l.strip() for l in args.langs.split(",")]
    
    # Parse tags
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
    
    # Resolve content directory
    content_dir = Path(args.dir)
    
    print(f"📝 Creating post: '{args.title}'")
    print(f"🌍 Languages: {', '.join(langs)}")
    print()
    
    # Create post for each language
    for lang in langs:
        create_post(args.title, lang, content_dir, args.author, tags)
    
    print()
    print("🎉 Done! Edit the files to add your content.")


if __name__ == "__main__":
    main()
