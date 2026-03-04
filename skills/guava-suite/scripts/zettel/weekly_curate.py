#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt
import pathlib

ROOT = pathlib.Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
NOTES_DIR = ROOT / 'memory' / 'notes'
OUT_DIR = ROOT / 'projects' / 'zettel-memory-openclaw' / 'output'
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    notes = sorted([p for p in NOTES_DIR.glob('zettel-*.md')], key=lambda p: p.stat().st_mtime, reverse=True)
    top = notes[:30]

    today = dt.datetime.now().strftime('%Y-%m-%d')
    out = OUT_DIR / f'weekly-curation-{today}.md'

    lines = [
        f'# Weekly Curation Draft ({today})',
        '',
        f'Total notes: {len(notes)}',
        f'Included in draft: {len(top)}',
        '',
        '## Candidate notes (recent first)',
        ''
    ]

    for p in top:
        title = 'untitled'
        txt = p.read_text(encoding='utf-8', errors='ignore')
        for line in txt.splitlines():
            if line.startswith('title: '):
                title = line.split('title: ', 1)[1]
                break
        lines.append(f'- [{title}]({p.as_posix()})')

    lines += [
        '',
        '## Next Step (manual)',
        '- Pick 5-10 durable notes and merge into MEMORY.md or archive note.',
        '- Mark superseded notes with `supersedes` when rewriting.',
    ]

    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
