import re
import sys
from pathlib import Path
from typing import Set, List, Dict, Optional

def extract_wikilinks(content: str) -> List[str]:
    """Extract all [[wikilinks]] from markdown content"""
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, content)

def find_note_path(link_name: str, zettel_dir: Path) -> Optional[Path]:
    """Find the actual file path for a wikilink name"""
    # Try exact match first
    exact = zettel_dir / f"{link_name}.md"

    print('exact is:', exact)
    if exact.exists():
        return exact

    # Try case-insensitive search
    for note in zettel_dir.rglob("*.md"):
        if note.stem.lower() == link_name.lower():
            return note

    return None

def extract_tags(content: str) -> Set[str]:
    """
    Extract tags from markdown content.
    Supports: #tag, tags: [tag1, tag2], and YAML frontmatter tags.
    """
    tags = set()

    # Inline #tags
    inline_tags = re.findall(r'#([\w\-]+)', content)
    tags.update(inline_tags)

    # YAML frontmatter tags
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        # Look for tags: [...] or tags: tag1, tag2
        tags_match = re.search(r'tags:\s*\[([^\]]+)\]', fm)
        if tags_match:
            yaml_tags = [t.strip().strip('"\'') for t in tags_match.group(1).split(',')]
            tags.update(yaml_tags)
        else:
            tags_match = re.search(r'tags:\s*(.+)', fm)
            if tags_match:
                yaml_tags = [t.strip() for t in tags_match.group(1).split(',')]
                tags.update(yaml_tags)

    return tags

def extract_links_recursive(
    seed_path: Path,
    zettel_dir: Path,
    max_depth: int,
    max_links: int
) -> Dict[Path, dict]:
    """
    Recursively extract wikilinks up to max_depth levels, collecting up to max_links total.
    Returns dict: {note_path: {'level': int, 'links': [str], 'content': str}}
    """
    visited = {}
    to_process = [(seed_path, 0)]  # (path, current_depth)

    while to_process and len(visited) < max_links:
        current_path, depth = to_process.pop(0)

        if current_path in visited or depth > max_depth:
            continue

        # Read content
        try:
            content = current_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {current_path}: {e}", file=sys.stderr)
            continue

        # Extract links
        links = extract_wikilinks(content)

        visited[current_path] = {
            'level': depth,
            'links': links,
            'content': content
        }

        # Add linked notes to process queue (if we haven't hit max depth)
        if depth < max_depth and len(visited) < max_links:
            for link in links:
                linked_path = find_note_path(link, zettel_dir)
                if linked_path and linked_path not in visited:
                    to_process.append((linked_path, depth + 1))

    return visited
