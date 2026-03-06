#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, datetime as dt

ROOT = pathlib.Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
NOTES_DIR = ROOT / 'memory' / 'notes'
INDEX = NOTES_DIR / 'index.md'


def read_text(p: pathlib.Path) -> str:
    return p.read_text(encoding='utf-8')


def keywords(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    stop = {'the','and','for','with','that','this','from','into','your','have','are'}
    return {w for w in words if w not in stop}


def extract_id(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith('id: '):
            return line.split('id: ', 1)[1].strip()
    return fallback


def update_links(path: pathlib.Path, all_notes: list[pathlib.Path], threshold=3):
    src = read_text(path)
    src_kw = keywords(src)
    linked = []
    for other in all_notes:
        if other == path:
            continue
        other_txt = read_text(other)
        ov = len(src_kw & keywords(other_txt))
        if ov >= threshold:
            linked.append((other, ov, other_txt))
    linked.sort(key=lambda x: x[1], reverse=True)

    # replace links line in frontmatter
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('links:'):
            ids = [extract_id(txt, p.stem) for p, _, txt in linked[:8]]
            lines[i] = f"links: [{', '.join(ids)}]"
            break
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def build_index(notes: list[pathlib.Path]):
    rows = ['# Zettel Index', '', f'Updated: {dt.datetime.now().isoformat()}', '']
    for n in sorted(notes, key=lambda p: p.stat().st_mtime, reverse=True):
        txt = read_text(n)
        title = 'untitled'
        for line in txt.splitlines():
            if line.startswith('title: '):
                title = line.split('title: ',1)[1]
                break
        rows.append(f"- [{title}](./{n.name})")
    INDEX.write_text('\n'.join(rows) + '\n', encoding='utf-8')


def main():
    notes = [p for p in NOTES_DIR.glob('*.md') if p.name != 'index.md']
    for n in notes:
        update_links(n, notes)
    build_index(notes)
    print(f'updated {len(notes)} notes and index')


if __name__ == '__main__':
    main()
