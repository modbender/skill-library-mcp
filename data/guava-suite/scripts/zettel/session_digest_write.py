#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, pathlib, datetime as dt, re, subprocess

ROOT = pathlib.Path(os.environ.get('OPENCLAW_WORKSPACE', os.path.expanduser('~/.openclaw/workspace')))
SESSIONS_DIR = pathlib.Path('/Users/ishikawaryuuta/.openclaw/agents/main/sessions')
NOTES_DIR = ROOT / 'memory' / 'notes'
STATE_PATH = ROOT / 'projects' / 'zettel-memory-openclaw' / 'state' / 'digest_state.json'
LOCK_PATH = ROOT / 'projects' / 'zettel-memory-openclaw' / 'state' / 'digest.lock'
LINK_SCRIPT = ROOT / 'projects' / 'zettel-memory-openclaw' / 'scripts' / 'link_notes.py'
MIN_INTERVAL_SEC = 10 * 60


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            st = json.loads(STATE_PATH.read_text(encoding='utf-8'))
            if 'last_ts_ms' not in st:
                st['last_ts_ms'] = 0
            return st
        except Exception:
            pass
    # 初回は直近12時間のみ対象にして過去ログ爆取り込みを防ぐ
    return {'last_ts_ms': int((dt.datetime.now(dt.timezone.utc).timestamp() - 12*3600) * 1000), 'last_hash': ''}


def save_state(st: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding='utf-8')


def acquire_lock() -> bool:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = LOCK_PATH.open('x')
        fd.write(str(dt.datetime.now(dt.timezone.utc).timestamp()))
        fd.close()
        return True
    except FileExistsError:
        return False


def release_lock():
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get('type') == 'text':
                t = c.get('text')
                if isinstance(t, str):
                    parts.append(t)
        return '\n'.join(parts)
    return ''


def to_ms(ts) -> int:
    if ts is None:
        return 0
    if isinstance(ts, (int, float)):
        return int(ts)
    if isinstance(ts, str):
        s = ts.strip()
        if s.isdigit():
            return int(s)
        try:
            if s.endswith('Z'):
                s = s[:-1] + '+00:00'
            return int(dt.datetime.fromisoformat(s).timestamp() * 1000)
        except Exception:
            return 0
    return 0


def iter_new_messages(last_ts_ms: int):
    files = sorted([p for p in SESSIONS_DIR.glob('*.jsonl') if '.deleted.' not in p.name], key=lambda p: p.stat().st_mtime)
    for fp in files:
        try:
            with fp.open(encoding='utf-8') as f:
                for line in f:
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    if o.get('type') != 'message':
                        continue
                    ts_raw = ((o.get('message') or {}).get('timestamp') or o.get('timestamp'))
                    ts_ms = to_ms(ts_raw)
                    if ts_ms <= last_ts_ms:
                        continue
                    role = ((o.get('message') or {}).get('role') or '').lower()
                    text = extract_text((o.get('message') or {}).get('content'))
                    if not text.strip():
                        continue
                    yield ts_ms, role, text.strip(), fp.name
        except Exception:
            continue


def suggest_tags(text: str) -> list[str]:
    words = re.findall(r'[A-Za-z][A-Za-z0-9_-]{3,}', text.lower())
    # Expanded stop words: common English + URL fragments + generic terms
    stop = {
        'that', 'this', 'with', 'from', 'your', 'about', 'have', 'will',
        'just', 'then', 'when', 'what', 'where', 'which', 'been', 'were',
        'they', 'them', 'their', 'there', 'these', 'those', 'than', 'each',
        'some', 'more', 'most', 'only', 'into', 'over', 'also', 'after',
        'before', 'between', 'under', 'again', 'does', 'done', 'could',
        'would', 'should', 'being', 'other', 'every', 'here', 'very',
        # Platform / generic terms (not useful as tags)
        'openclaw', 'session', 'message', 'https', 'http', 'true', 'false',
        'null', 'none', 'json', 'string', 'label', 'content', 'metadata',
        'untrusted', 'conversation', 'sender', 'guild', 'channel',
        'reply', 'current', 'info', 'data', 'type', 'user', 'assistant',
        'generic', 'auto', 'digest',
    }
    freq = {}
    for w in words:
        if w in stop:
            continue
        # Skip URL-like fragments (e.g. n---, com, org)
        if re.match(r'^[a-z]-{2,}', w) or len(w) <= 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:4]
    tags = [f'kw-{w}' for w, _ in top]
    base = ['auto-digest', 'session-summary']
    return base + tags


def fmt_ms(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).isoformat()


def make_note(entries: list[tuple[int,str,str,str]]):
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    zid = f"zettel-{now.strftime('%Y%m%d-%H%M%S')}-{now.microsecond:06d}"

    user_msgs = [t for _,r,t,_ in entries if r == 'user']
    assistant_msgs = [t for _,r,t,_ in entries if r == 'assistant']
    merged = '\n'.join([t for _,_,t,_ in entries])
    tags = suggest_tags(merged)

    title = f"Auto digest {now.astimezone().strftime('%m/%d %H:%M')}"
    body_lines = [
        '## Auto session digest (LLMなし・直接集約)',
        f'- window: {fmt_ms(entries[0][0])} -> {fmt_ms(entries[-1][0])}',
        f'- messages: total={len(entries)}, user={len(user_msgs)}, assistant={len(assistant_msgs)}',
        '',
        '## Recent highlights (raw extract)',
    ]
    for ts_ms, role, text, src in entries[-10:]:
        snippet = text.replace('\n', ' ')[:220]
        body_lines.append(f'- [{fmt_ms(ts_ms)}] ({role}) {snippet}')

    content = f"""---
id: {zid}
title: {title}
tags: [{', '.join(tags)}]
entities: [OpenClaw, SessionDigest]
source: auto/session-log
created_at: {now.isoformat()}
updated_at: {now.isoformat()}
supersedes: null
links: []
confidence: 0.60
---

{chr(10).join(body_lines)}
"""
    out = NOTES_DIR / f"{zid}-auto-session-digest.md"
    out.write_text(content, encoding='utf-8')
    return out


def main() -> int:
    if not acquire_lock():
        print('Another digest process is running; skip')
        return 0
    try:
        st = load_state()

        # cooldown guard
        last_run_at = st.get('last_run_at')
        if isinstance(last_run_at, str):
            try:
                t = last_run_at
                if t.endswith('Z'):
                    t = t[:-1] + '+00:00'
                elapsed = dt.datetime.now(dt.timezone.utc).timestamp() - dt.datetime.fromisoformat(t).timestamp()
                if elapsed < MIN_INTERVAL_SEC:
                    print('Cooldown active; skip')
                    return 0
            except Exception:
                pass

        entries = list(iter_new_messages(int(st.get('last_ts_ms', 0))))
        if not entries:
            print('No new messages; skip')
            return 0

        fingerprint = hashlib.sha256(('\n'.join(f"{a}|{b}|{c[:200]}|{d}" for a,b,c,d in entries)).encode()).hexdigest()
        if fingerprint == st.get('last_hash'):
            print('Same digest fingerprint; skip')
            return 0

        note_path = make_note(entries)
        subprocess.run(['python3', str(LINK_SCRIPT)], check=False)

        st['last_ts_ms'] = max(ts for ts,_,_,_ in entries)
        st['last_hash'] = fingerprint
        st['last_run_at'] = iso_now()
        st['last_note'] = str(note_path)
        save_state(st)

        print(f'Wrote {note_path}')
        return 0
    finally:
        release_lock()


if __name__ == '__main__':
    code = main()
    # Chain: also run Antigravity walkthrough digest
    antigravity_script = pathlib.Path(__file__).parent / 'antigravity_digest.py'
    if antigravity_script.exists():
        subprocess.run(['python3', str(antigravity_script)], check=False)
    # Chain: integrity check (daily health check)
    integrity_script = ROOT / 'scripts' / 'integrity_check.py'
    if integrity_script.exists():
        subprocess.run(['python3', str(integrity_script)], check=False)
    raise SystemExit(code)

