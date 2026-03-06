#!/usr/bin/env python3
"""
Validate translation completeness across all locales.

Checks that for each content file in the default language,
corresponding files exist in all other locales.

Usage:
    python astro-i18n-check.py
    python astro-i18n-check.py --content-dir src/content/docs
    python astro-i18n-check.py --default-lang en --langs en,es,fr
"""

import argparse
import os
from pathlib import Path
from collections import defaultdict


def get_content_files(content_dir: Path, lang: str) -> set:
    """Get all markdown files for a specific language."""
    lang_dir = content_dir / lang
    if not lang_dir.exists():
        return set()
    
    files = set()
    for md_file in lang_dir.rglob("*.md"):
        # Get relative path within language directory
        relative = md_file.relative_to(lang_dir)
        files.add(str(relative))
    
    return files


def check_translations(content_dir: Path, default_lang: str, langs: list) -> dict:
    """Check translation coverage for all content."""
    
    results = {
        "missing": defaultdict(list),
        "extra": defaultdict(list),
        "complete": [],
        "stats": {}
    }
    
    # Get files in default language
    default_files = get_content_files(content_dir, default_lang)
    
    if not default_files:
        print(f"⚠️  No content found in default language '{default_lang}'")
        return results
    
    results["stats"]["total"] = len(default_files)
    results["stats"]["default_lang"] = default_lang
    results["stats"]["langs"] = langs
    
    # Check each other language
    for lang in langs:
        if lang == default_lang:
            continue
        
        lang_files = get_content_files(content_dir, lang)
        
        # Missing: in default but not in this lang
        missing = default_files - lang_files
        for f in sorted(missing):
            results["missing"][lang].append(f)
        
        # Extra: in this lang but not in default
        extra = lang_files - default_files
        for f in sorted(extra):
            results["extra"][lang].append(f)
        
        # Track complete files
        if not missing and not extra:
            results["complete"].append(lang)
    
    return results


def print_report(results: dict):
    """Print a formatted report."""
    
    stats = results["stats"]
    print("=" * 60)
    print("📊 Translation Coverage Report")
    print("=" * 60)
    print(f"Default language: {stats['default_lang']}")
    print(f"Total content files: {stats['total']}")
    print(f"Target languages: {', '.join(stats['langs'])}")
    print()
    
    # Missing translations
    if results["missing"]:
        print("❌ Missing Translations:")
        print("-" * 40)
        for lang, files in sorted(results["missing"].items()):
            print(f"\n{lang.upper()} ({len(files)} missing):")
            for f in files:
                print(f"  • {f}")
        print()
    
    # Extra translations
    if results["extra"]:
        print("⚠️  Extra Translations (not in default):")
        print("-" * 40)
        for lang, files in sorted(results["extra"].items()):
            print(f"\n{lang.upper()} ({len(files)} extra):")
            for f in files:
                print(f"  • {f}")
        print()
    
    # Summary
    total_missing = sum(len(files) for files in results["missing"].values())
    total_extra = sum(len(files) for files in results["extra"].values())
    
    if total_missing == 0 and total_extra == 0:
        print("✅ All translations are complete!")
    else:
        print("=" * 60)
        print(f"📈 Summary: {total_missing} missing, {total_extra} extra")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Validate translation completeness"
    )
    parser.add_argument(
        "--content-dir", "-c",
        default="src/content",
        help="Content directory path"
    )
    parser.add_argument(
        "--default-lang", "-d",
        default="en",
        help="Default language code"
    )
    parser.add_argument(
        "--langs", "-l",
        default="en",
        help="Comma-separated language codes"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Parse languages
    langs = [l.strip() for l in args.langs.split(",")]
    content_dir = Path(args.content_dir)
    
    if not content_dir.exists():
        print(f"❌ Content directory not found: {content_dir}")
        return 1
    
    results = check_translations(content_dir, args.default_lang, langs)
    
    if args.json:
        import json
        # Convert defaultdicts to regular dicts for JSON
        output = {
            "missing": {k: v for k, v in results["missing"].items()},
            "extra": {k: v for k, v in results["extra"].items()},
            "complete": results["complete"],
            "stats": results["stats"]
        }
        print(json.dumps(output, indent=2))
    else:
        print_report(results)
    
    # Return exit code based on missing translations
    total_missing = sum(len(files) for files in results["missing"].values())
    return 1 if total_missing > 0 else 0


if __name__ == "__main__":
    exit(main())
