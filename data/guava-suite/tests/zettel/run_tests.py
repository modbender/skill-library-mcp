#!/usr/bin/env python3
from __future__ import annotations
import pathlib, re, subprocess, sys, datetime as dt, tempfile, os, json

ROOT = pathlib.Path('/Users/ishikawaryuuta/.openclaw/workspace')
PROJ = ROOT / 'projects' / 'zettel-memory-openclaw'
SCRIPTS = PROJ / 'scripts'
NOTES = ROOT / 'memory' / 'notes'
OUTPUT = PROJ / 'output'

REQ_KEYS = {
    'id:', 'title:', 'tags:', 'entities:', 'source:', 'created_at:', 'updated_at:', 'supersedes:', 'links:', 'confidence:'
}


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, text=True, capture_output=True)
    out = (p.stdout or '') + (p.stderr or '')
    return p.returncode, out


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
            fm[k.strip()+':'] = v.strip()
    return fm


def test_id_uniqueness() -> tuple[bool, str]:
    before = note_files()
    c1, o1 = run([
        'python3', str(SCRIPTS / 'new_note.py'),
        '--title', 'TEST ID uniqueness A',
        '--body', 'id uniqueness test',
        '--tags', 'test,id', '--entities', 'Test', '--source', 'test-suite'
    ])
    c2, o2 = run([
        'python3', str(SCRIPTS / 'new_note.py'),
        '--title', 'TEST ID uniqueness B',
        '--body', 'id uniqueness test',
        '--tags', 'test,id', '--entities', 'Test', '--source', 'test-suite'
    ])
    after = note_files()
    new = sorted(after - before)
    if c1 != 0 or c2 != 0 or len(new) < 2:
        return False, f'creation failed\n{o1}\n{o2}'

    ids = []
    for p in new:
        txt = p.read_text(encoding='utf-8', errors='ignore')
        fm = parse_frontmatter(txt)
        ids.append(fm.get('id:', ''))
    ok = len(set(ids)) == len(ids) and all(re.match(r'zettel-\d{8}-\d{6}(?:-\d{6})?', i or '') for i in ids)
    return ok, f'new_ids={ids}'


def test_frontmatter_validation() -> tuple[bool, str]:
    bad = []
    for p in note_files():
        txt = p.read_text(encoding='utf-8', errors='ignore')
        fm = parse_frontmatter(txt)
        missing = sorted(k for k in REQ_KEYS if k not in fm)
        if missing:
            bad.append((p.name, missing))
            continue
        if not fm['links:'].startswith('[') or not fm['links:'].endswith(']'):
            bad.append((p.name, ['links not list-like']))
    if bad:
        return False, str(bad[:5])
    return True, f'checked={len(note_files())}'


def test_smoke_e2e() -> tuple[bool, str]:
    title = f"TEST smoke {dt.datetime.now().strftime('%H%M%S')}"
    c1, o1 = run([
        'python3', str(SCRIPTS / 'new_note.py'),
        '--title', title,
        '--body', 'openclaw smoke e2e test memory search graph',
        '--tags', 'test,smoke,openclaw', '--entities', 'OpenClaw,Test', '--source', 'test-suite'
    ])
    c2, o2 = run(['python3', str(SCRIPTS / 'link_notes.py')])
    c3, o3 = run(['python3', str(SCRIPTS / 'search_expand.py'), '--query', 'openclaw', '--top', '3', '--mode', 'auto'])
    c4, o4 = run(['python3', str(SCRIPTS / 'weekly_curate.py')])

    ok = (c1 == c2 == c3 == c4 == 0) and ('Seed notes' in o3) and any(OUTPUT.glob('weekly-curation-*.md'))
    details = '\n'.join([
        f'new_note: {c1}', f'link_notes: {c2}', f'search_expand: {c3}', f'weekly_curate: {c4}',
        f"search_expand_out_head: {(o3[:240]).replace(chr(10), ' | ')}"
    ])
    return ok, details


def test_retrieval_golden_set() -> tuple[bool, str]:
    checks = [
        ('openclaw', 'zettel-20260215-164924'),
        ('identity', 'identity-continuity-anchor'),
    ]
    msgs = []
    for q, expected in checks:
        c, out = run(['python3', str(SCRIPTS / 'search_expand.py'), '--query', q, '--top', '5', '--mode', 'local'])
        ok = (c == 0) and ('Seed notes' in out) and (expected in out)
        msgs.append(f'{q}=>{"PASS" if ok else "FAIL"}')
        if not ok:
            return False, f'{q} failed. out_head={(out[:280]).replace(chr(10), " | ")}'
    return True, ', '.join(msgs)


def test_auto_fallback_when_memory_search_unavailable() -> tuple[bool, str]:
    c, out = run([
        'python3', str(SCRIPTS / 'search_expand.py'),
        '--query', 'openclaw', '--top', '3', '--mode', 'auto', '--openclaw-bin', '/nonexistent/openclaw'
    ])
    ok = (c == 0) and ('# Mode: local' in out) and ('Seed notes' in out)
    return ok, (out[:280]).replace('\n', ' | ')


def test_supersedes_integrity() -> tuple[bool, str]:
    id_to_sup = {}
    for p in note_files():
        fm = parse_frontmatter(p.read_text(encoding='utf-8', errors='ignore'))
        nid = fm.get('id:', '').strip()
        sup = fm.get('supersedes:', '').strip()
        if nid:
            id_to_sup[nid] = None if sup in ('', 'null', 'None') else sup

    # all supersedes targets must exist
    missing = [f'{nid}->{sup}' for nid, sup in id_to_sup.items() if sup and sup not in id_to_sup]
    if missing:
        return False, f'missing targets: {missing[:5]}'

    # cycle detection in supersedes chains
    for nid in id_to_sup:
        seen = set()
        cur = nid
        while cur is not None:
            if cur in seen:
                return False, f'cycle detected at {nid}'
            seen.add(cur)
            cur = id_to_sup.get(cur)
    return True, f'checked_nodes={len(id_to_sup)}'


def test_memory_json_shape_resilience() -> tuple[bool, str]:
    # pick an existing note path for mocked memory_search response
    notes = sorted(note_files())
    if not notes:
        return False, 'no notes found for mock test'
    target = notes[0].as_posix()

    payload = {
        'results': [
            {'path': target, 'text': 'mock result primary shape'},
            {'content': 'fallback snippet mentioning zettel-20260215-164924'},
        ]
    }

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.sh') as f:
        script_path = f.name
        f.write('#!/bin/sh\n')
        f.write("cat <<'EOF'\n")
        f.write(json.dumps(payload))
        f.write('\nEOF\n')
    os.chmod(script_path, 0o755)

    try:
        c, out = run([
            'python3', str(SCRIPTS / 'search_expand.py'),
            '--query', 'mock-query', '--top', '3', '--mode', 'memory', '--openclaw-bin', script_path
        ])
    finally:
        pathlib.Path(script_path).unlink(missing_ok=True)

    ok = (c == 0) and ('# Mode: memory_search' in out) and ('Seed notes' in out)
    return ok, (out[:280]).replace('\n', ' | ')


def test_property_based_hypothesis() -> tuple[bool, str]:
    vpy = PROJ / '.venv' / 'bin' / 'python'
    if not vpy.exists():
        return False, 'venv python not found. create .venv first'
    c, out = run([str(vpy), str(PROJ / 'tests' / 'p2_property_tests.py')])
    return (c == 0), (out[:300]).replace('\n', ' | ')


def cleanup_test_notes():
    for p in note_files():
        txt = p.read_text(encoding='utf-8', errors='ignore')
        if 'source: test-suite' in txt or 'title: TEST ' in txt:
            p.unlink(missing_ok=True)


def main() -> int:
    NOTES.mkdir(parents=True, exist_ok=True)
    tests = [
        ('P0-ID-uniqueness', test_id_uniqueness),
        ('P0-frontmatter-validation', test_frontmatter_validation),
        ('P0-smoke-e2e', test_smoke_e2e),
        ('P1-retrieval-golden-set', test_retrieval_golden_set),
        ('P1-auto-fallback', test_auto_fallback_when_memory_search_unavailable),
        ('P1-supersedes-integrity', test_supersedes_integrity),
        ('P2-memory-json-shape-resilience', test_memory_json_shape_resilience),
        ('P2-property-based-hypothesis', test_property_based_hypothesis),
    ]
    failed = []
    print('# zettel-memory-openclaw test run')
    try:
        for name, fn in tests:
            ok, msg = fn()
            status = 'PASS' if ok else 'FAIL'
            print(f'- {name}: {status}')
            print(f'  {msg}')
            if not ok:
                failed.append((name, msg))
    finally:
        cleanup_test_notes()
        run(['python3', str(SCRIPTS / 'link_notes.py')])

    if failed:
        print('\nFAILED TESTS:')
        for n, m in failed:
            print(f'* {n}: {m}')
        return 1
    print('\nALL TESTS PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
