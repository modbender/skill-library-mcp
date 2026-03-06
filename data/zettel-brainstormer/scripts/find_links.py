#!/usr/bin/env python3
"""
Find Links script for zettel-brainstormer.
Extracts paths of wikilinked docs and tag-similar docs.
Writes JSON list of file paths: ["/path/to/doc1.md", "/path/to/doc2.md", ...]

Usage: find_links.py --input note.md --output paths.json
"""
import sys, json, argparse
from pathlib import Path
from typing import Set, List, Dict

from config_manager import ConfigManager
from obsidian_utils import extract_links_recursive, extract_tags

def simple_read(path):
    try:
        return Path(path).read_text(encoding='utf-8')
    except Exception:
        return ""

def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2), encoding='utf-8')

def find_tag_similar_docs(
    seed_tags: Set[str],
    zettel_dir: Path,
    seed_path: Path,
    max_similar: int = 5
) -> List[str]:
    """
    Find notes with overlapping tags.
    Returns list of paths: ['/path/to/doc1.md']
    """
    similar = []

    for note_path in zettel_dir.rglob("*.md"):
        if note_path.resolve() == seed_path.resolve():
            continue

        try:
            content = note_path.read_text(encoding='utf-8')
            note_tags = extract_tags(content)
            overlap = len(seed_tags & note_tags)

            if overlap > 0:
                similar.append({
                    'path': str(note_path.resolve()),
                    'overlap': overlap
                })
        except Exception as e:
            continue

    # Sort by overlap descending, take top max_similar
    similar.sort(key=lambda x: x['overlap'], reverse=True)
    return [s['path'] for s in similar[:max_similar]]

def find_links(args):
    # Load configuration
    config = ConfigManager.load()
    if args.zettel_dir:
        zettel_dir = Path(args.zettel_dir).expanduser()
    else:
        zettel_dir_str = config.get('zettel_dir')
        if not zettel_dir_str:
             print("Error: zettel_dir not configured.", file=sys.stderr)
             sys.exit(1)
        zettel_dir = Path(zettel_dir_str).expanduser()

    link_depth = config.get('link_depth', 2)
    max_links = config.get('max_links', 10)

    seed_path = Path(args.input).expanduser().resolve()
    if not seed_path.exists():
        print(f"Error: Input note not found: {seed_path}", file=sys.stderr)
        sys.exit(1)

    text = simple_read(seed_path)

    # Extract wikilinked documents
    linked_paths = set()
    if zettel_dir.exists():
        # extract_links_recursive returns dict {path: {level, content}}
        raw_linked_docs = extract_links_recursive(seed_path, zettel_dir, link_depth, max_links)
        for path in raw_linked_docs.keys():
             linked_paths.add(str(path))
        print(f"Extracted {len(linked_paths)} linked documents (depth={link_depth}, max={max_links})", file=sys.stderr)
    else:
        print(f"Warning: Zettelkasten directory not found: {zettel_dir}", file=sys.stderr)

    # Extract tag-similar documents
    tag_similar_paths = []
    if zettel_dir.exists():
        seed_tags = extract_tags(text)
        if seed_tags:
            tag_similar_paths = find_tag_similar_docs(seed_tags, zettel_dir, seed_path, max_similar=5)
            print(f"Found {len(tag_similar_paths)} tag-similar documents (seed tags: {sorted(seed_tags)})", file=sys.stderr)

    # Combine all paths, keeping seed note out (it's implicit context)
    all_paths = set(linked_paths)
    for p in tag_similar_paths:
        all_paths.add(p)

    # Ensure seed path is not in the list (if it somehow got linked)
    if str(seed_path) in all_paths:
        all_paths.remove(str(seed_path))

    # Output as JSON list
    output_list = list(all_paths)
    write_json(args.output, output_list)
    print(f'Wrote {len(output_list)} paths to {args.output}', file=sys.stderr)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True, help='Input note path')
    p.add_argument('--output', required=True, help='Output JSON path')
    p.add_argument('--zettel-dir', help='Override Zettelkasten directory')

    args = p.parse_args()

    find_links(args)