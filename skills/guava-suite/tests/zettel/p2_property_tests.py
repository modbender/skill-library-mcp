#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, subprocess, sys
from hypothesis import given, settings, strategies as st

ROOT = pathlib.Path('/Users/ishikawaryuuta/.openclaw/workspace')
SCRIPTS = ROOT / 'projects' / 'zettel-memory-openclaw' / 'scripts'
NOTES = ROOT / 'memory' / 'notes'


def note_files() -> set[pathlib.Path]:
    return set(NOTES.glob('zettel-*.md'))


def parse_frontmatter(txt: str) -> dict[str, str]:
    lines = txt.splitlines()
    if len(lines) < 3 or lines[0].strip() != '---':
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == '---':
            break
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


TITLE = st.text(
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc'), blacklist_characters='\n\r\t\x00'),
    min_size=3,
    max_size=60,
)
BODY = st.text(
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc'), blacklist_characters='\n\r\t\x00'),
    min_size=10,
    max_size=200,
)
TAG = st.from_regex(r'[a-z0-9][a-z0-9_-]{0,11}', fullmatch=True)


@given(title=TITLE, body=BODY, tags=st.lists(TAG, min_size=0, max_size=4), entities=st.lists(TAG, min_size=0, max_size=4))
@settings(max_examples=20, deadline=None)
def test_new_note_property(title, body, tags, entities):
    before = note_files()
    c, out = run([
        'python3', str(SCRIPTS / 'new_note.py'),
        f'--title={title}',
        f'--body={body}',
        f"--tags={','.join(tags)}",
        f"--entities={','.join(entities)}",
        '--source', 'test-suite',
        '--confidence', '0.7',
    ])
    assert c == 0, out
    after = note_files()
    created = list(after - before)
    assert len(created) == 1, f'created={len(created)} out={out}'

    txt = created[0].read_text(encoding='utf-8', errors='ignore')
    fm = parse_frontmatter(txt)

    assert re.match(r'^zettel-\d{8}-\d{6}(?:-\d{6})?$', fm.get('id', ''))
    for key in ['title', 'tags', 'entities', 'source', 'created_at', 'updated_at', 'supersedes', 'links', 'confidence']:
        assert key in fm, f'missing {key}'
    assert fm['links'].startswith('[') and fm['links'].endswith(']')


def cleanup():
    for p in note_files():
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if 'source: test-suite' in txt:
            p.unlink(missing_ok=True)


if __name__ == '__main__':
    try:
        test_new_note_property()
        print('P2 property tests PASS')
        rc = 0
    except AssertionError as e:
        print(f'P2 property tests FAIL: {e}')
        rc = 1
    finally:
        cleanup()
        run(['python3', str(SCRIPTS / 'link_notes.py')])
    sys.exit(rc)
