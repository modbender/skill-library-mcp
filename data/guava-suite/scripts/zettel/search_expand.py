#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, json, pathlib, re, subprocess

ROOT = pathlib.Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
NOTES_DIR = ROOT / 'memory' / 'notes'
DEFAULT_OPENCLAW_BIN = '/opt/homebrew/bin/openclaw'


def parse_links(note_text: str) -> list[str]:
    for line in note_text.splitlines():
        if line.startswith('links:'):
            inside = line.split('[',1)[-1].rsplit(']',1)[0].strip()
            if not inside:
                return []
            return [x.strip() for x in inside.split(',') if x.strip()]
    return []


def id_from_filename(p: pathlib.Path) -> str:
    m = re.match(r'(zettel-\d{8}-\d{6}(?:-\d{6})?)', p.name)
    return m.group(1) if m else p.stem


def build_id_map() -> dict[str, pathlib.Path]:
    mp = {}
    for p in NOTES_DIR.glob('zettel-*.md'):
        mp[id_from_filename(p)] = p
    return mp


def try_parse_json(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        return None


def run_memory_search(query: str, k: int, openclaw_bin: str):
    cmd = [
        openclaw_bin, 'tools', 'call', 'memory_search',
        json.dumps({'query': query, 'maxResults': k})
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return try_parse_json(out)
    except Exception:
        return None


def extract_seed_from_memory_result(memory_result, idmap: dict[str, pathlib.Path]) -> list[tuple[int, str, pathlib.Path]]:
    if not isinstance(memory_result, dict):
        return []
    snippets = memory_result.get('results') or memory_result.get('snippets') or []
    seeds = []
    for i, s in enumerate(snippets):
        text = ''
        path = ''
        if isinstance(s, dict):
            text = (s.get('text') or s.get('content') or '').lower()
            path = (s.get('path') or '')
        candidate = None

        # 1) direct path hit
        if path:
            for nid, fp in idmap.items():
                if fp.as_posix() == path or fp.name == pathlib.Path(path).name:
                    candidate = (nid, fp)
                    break

        # 2) id in snippet text
        if candidate is None and text:
            m = re.search(r'zettel-\d{8}-\d{6}(?:-\d{6})?', text)
            if m and m.group(0) in idmap:
                nid = m.group(0)
                candidate = (nid, idmap[nid])

        if candidate is not None:
            nid, fp = candidate
            score = max(1, 100 - i)  # keep order from memory_search
            seeds.append((score, nid, fp))

    # dedupe by id, keep best score
    best = {}
    for score, nid, fp in seeds:
        if nid not in best or score > best[nid][0]:
            best[nid] = (score, fp)
    out = [(score, nid, fp) for nid, (score, fp) in best.items()]
    out.sort(reverse=True)
    return out


def local_seed_search(query: str, idmap: dict[str, pathlib.Path], top: int):
    scored = []
    q = query.lower()
    for nid, fp in idmap.items():
        txt = fp.read_text(encoding='utf-8', errors='ignore').lower()
        s = txt.count(q)
        if s > 0:
            scored.append((s, nid, fp))
    scored.sort(reverse=True)
    return scored[:top]


def main():
    p = argparse.ArgumentParser(description='Expand zettel neighbors by 1-hop links')
    p.add_argument('--query', required=True)
    p.add_argument('--top', type=int, default=5)
    p.add_argument('--mode', choices=['auto', 'memory', 'local'], default='auto')
    p.add_argument('--openclaw-bin', default=DEFAULT_OPENCLAW_BIN)
    args = p.parse_args()

    idmap = build_id_map()

    seeds = []
    mode_used = 'local'
    if args.mode in ('auto', 'memory'):
        mem = run_memory_search(args.query, max(args.top, 8), args.openclaw_bin)
        seeds = extract_seed_from_memory_result(mem, idmap)
        if seeds:
            mode_used = 'memory_search'

    if (not seeds) and args.mode in ('auto', 'local'):
        seeds = local_seed_search(args.query, idmap, args.top)
        mode_used = 'local'

    seeds = seeds[:args.top]

    print(f'# Query: {args.query}')
    print(f'# Mode: {mode_used}')
    if not seeds:
        print('No direct zettel hits. (Tip: create notes first with new_note.py)')
        return

    print('\n## Seed notes')
    for s, nid, fp in seeds:
        print(f'- {nid} ({fp.name}) score={s}')

    print('\n## 1-hop linked notes')
    seen = set(nid for _, nid, _ in seeds)
    for _, nid, fp in seeds:
        links = parse_links(fp.read_text(encoding='utf-8', errors='ignore'))
        for lid in links:
            if lid in idmap and lid not in seen:
                seen.add(lid)
                print(f'- {lid} ({idmap[lid].name}) via {nid}')


if __name__ == '__main__':
    main()
