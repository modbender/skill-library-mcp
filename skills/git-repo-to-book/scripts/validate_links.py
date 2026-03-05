#!/usr/bin/env python3
"""Validate all internal links and image references in a book project.

Usage:
    python3 validate_links.py [--book-dir /path/to/book]

Checks:
    - Image references (![...](path)) point to existing files
    - Internal markdown links ([...](path.md)) point to existing files  
    - No orphaned diagram directories (diagrams with no chapter reference)

Exit code: 0 = all valid, 1 = broken links found
"""
import os, re, sys
from pathlib import Path

def find_refs(md_file):
    refs = []
    with open(md_file, 'r', encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', line):
                refs.append({'file': str(md_file), 'line': lineno, 'type': 'image', 'path': m.group(2)})
            for m in re.finditer(r'(?<!!)\[([^\]]*)\]\(([^)]*\.md(?:#[^)]*)?)\)', line):
                refs.append({'file': str(md_file), 'line': lineno, 'type': 'link', 'path': m.group(2).split('#')[0]})
    return refs

def main():
    book_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    print(f"Validating links in: {book_dir}\n")
    
    md_files = sorted(list(book_dir.rglob('chapters/*.md')) + list(book_dir.rglob('book/*.md')))
    broken = []
    
    for md_file in md_files:
        for ref in find_refs(md_file):
            resolved = (md_file.parent / ref['path']).resolve()
            if not resolved.exists():
                broken.append(ref)
                parent = resolved.parent
                if parent.exists():
                    candidates = [f.name for f in parent.glob(f'*{resolved.suffix}')][:3]
                    if candidates:
                        ref['suggestions'] = candidates
    
    if broken:
        print(f"❌ {len(broken)} broken link(s):\n")
        for b in broken:
            print(f"  {Path(b['file']).name}:{b['line']}  {b['type']}: {b['path']}")
            if 'suggestions' in b:
                print(f"    → did you mean: {', '.join(b['suggestions'])}")
    else:
        print("✅ All links valid")
    
    # Check orphaned diagrams
    diag_dir = book_dir / 'diagrams'
    if diag_dir.exists():
        referenced = set()
        for md in md_files:
            content = md.read_text()
            for m in re.finditer(r'diagrams/([\w-]+)/', content):
                referenced.add(m.group(1))
        orphans = [d.name for d in sorted(diag_dir.iterdir()) if d.is_dir() and d.name not in referenced]
        if orphans:
            print(f"\n⚠️  {len(orphans)} orphaned diagram dir(s): {', '.join(orphans)}")
    
    print(f"\nScanned {len(md_files)} files.")
    sys.exit(1 if broken else 0)

if __name__ == '__main__':
    main()
