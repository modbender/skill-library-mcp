#!/usr/bin/env python3
"""queue-task: durable queue state helper (task-father layout only).

Layout:
- <WORKSPACE_DIR>/<TASKS_DIR>/<slug>/

State files:
- queue.jsonl
- progress.json
- done.jsonl
- failed.jsonl
- lock.json
"""

from __future__ import annotations
import argparse, datetime as dt, json, pathlib
from typing import Any, Dict


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_env(path: pathlib.Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        v = v.strip().strip('"').strip("'")
        out[k.strip()] = v
    return out


def read_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: pathlib.Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def resolve_dir(cfg: Dict[str, str], slug: str) -> pathlib.Path:
    ws = pathlib.Path(cfg['WORKSPACE_DIR']).expanduser().resolve()
    tasks_dir = cfg.get('TASKS_DIR', 'tasks')
    return ws / tasks_dir / slug


def ensure_task_docs_if_missing(base: pathlib.Path, slug: str) -> None:
    task_md = base / 'TASK.md'
    todos = base / 'TODOS.md'
    if not task_md.exists():
        task_md.write_text(
            '---\n'
            f'name: {slug}\n'
            'status: initialized\n'
            f'created_at: {now_iso()}\n'
            f'updated_at: {now_iso()}\n'
            '---\n\n'
            '# Purpose\nTBD\n\n'
            '# Important Decisions\n- TBD\n\n'
            '# Blockers\n- None\n\n'
            '# Capabilities\n- Skills: queue-task\n- Plugins: None\n- Tools: None\n\n'
            '# Change Log\n'
            f'- {now_iso()} — Initialized by queue-task.\n',
            encoding='utf-8',
        )
    if not todos.exists():
        todos.write_text('# TODOS\n\n- [ ] Define first queue step\n', encoding='utf-8')


def ensure_files(base: pathlib.Path, slug: str, with_task_docs: bool = False) -> Dict[str, pathlib.Path]:
    base.mkdir(parents=True, exist_ok=True)
    if with_task_docs:
        ensure_task_docs_if_missing(base, slug)
    p = {
        'queue': base / 'queue.jsonl',
        'progress': base / 'progress.json',
        'done': base / 'done.jsonl',
        'failed': base / 'failed.jsonl',
        'lock': base / 'lock.json',
    }
    for k in ('queue', 'done', 'failed'):
        if not p[k].exists():
            p[k].write_text('', encoding='utf-8')
    if not p['progress'].exists():
        write_json(p['progress'], {
            'task': slug,
            'status': 'init',
            'updatedAt': now_iso(),
            'cursor': None,
            'counts': {'processed': 0, 'done': 0, 'failed': 0, 'skipped': 0},
            'blocking_reason': None,
            'layout': 'task-folder' if (base / 'TASK.md').exists() else 'standalone',
        })
    if not p['lock'].exists():
        p['lock'].write_text('', encoding='utf-8')
    return p


def nlines(path: pathlib.Path) -> int:
    if not path.exists():
        return 0
    txt = path.read_text(encoding='utf-8').strip()
    return 0 if not txt else len(txt.splitlines())


def cmd_init(a, cfg):
    d = resolve_dir(cfg, a.slug)
    files = ensure_files(d, a.slug, with_task_docs=True)
    print(d)
    for k, v in files.items():
        print(f'{k}: {v}')


def cmd_status(a, cfg):
    d = resolve_dir(cfg, a.slug)
    files = ensure_files(d, a.slug, with_task_docs=False)
    progress = read_json(files['progress'])
    out = {
        'task': a.slug,
        'dir': str(d),
        'progress': progress,
        'queue_lines': nlines(files['queue']),
        'done_lines': nlines(files['done']),
        'failed_lines': nlines(files['failed']),
        'lock_present': bool(files['lock'].read_text(encoding='utf-8').strip()),
    }
    print(json.dumps(out, indent=2))


def cmd_clear_stale_lock(a, cfg):
    d = resolve_dir(cfg, a.slug)
    files = ensure_files(d, a.slug)
    lock = files['lock']
    if not lock.read_text(encoding='utf-8').strip():
        print('no_lock')
        return
    stale_min = int(cfg.get('LOCK_STALE_MINUTES', '20'))
    try:
        obj = read_json(lock)
        ts = obj.get('createdAt') or obj.get('ts')
        created = dt.datetime.fromisoformat(ts.replace('Z', '+00:00'))
        age = dt.datetime.now(dt.timezone.utc) - created.astimezone(dt.timezone.utc)
        if age > dt.timedelta(minutes=stale_min):
            lock.write_text('', encoding='utf-8')
            print(f'cleared_stale_lock age_seconds={int(age.total_seconds())}')
        else:
            print(f'lock_fresh age_seconds={int(age.total_seconds())}')
    except Exception:
        lock.write_text('', encoding='utf-8')
        print('cleared_unparsable_lock')


def cmd_print_template(a, cfg):
    print(f'''You are the supervisor+worker for a queue task.

Requirements:
- Process at most BATCH_SIZE={cfg.get('BATCH_SIZE','15')} items per run.
- Use queue.jsonl, progress.json, done.jsonl, failed.jsonl, lock.json.
- Idempotency: skip if already in done.
- Update progress after EACH item.
- Clear lock on exit.
- If complete, set progress.status="done".
''')


def parse_args():
    p = argparse.ArgumentParser(description='queue-task helper')
    p.add_argument('--config', default=str(pathlib.Path(__file__).resolve().parents[1] / 'config.env'))
    sub = p.add_subparsers(dest='cmd', required=True)

    for name in ('init', 'status', 'clear-stale-lock'):
        sp = sub.add_parser(name)
        sp.add_argument('slug')
    sub.add_parser('print-supervisor-template')
    return p.parse_args()


def main():
    a = parse_args()
    cfg = {
        'WORKSPACE_DIR': '/home/miles/.openclaw/workspace',
        'TASKS_DIR': 'tasks',
        'BATCH_SIZE': '15',
        'LOCK_STALE_MINUTES': '20',
    }
    cfg.update(load_env(pathlib.Path(a.config)))

    if a.cmd == 'init':
        cmd_init(a, cfg)
    elif a.cmd == 'status':
        cmd_status(a, cfg)
    elif a.cmd == 'clear-stale-lock':
        cmd_clear_stale_lock(a, cfg)
    elif a.cmd == 'print-supervisor-template':
        cmd_print_template(a, cfg)


if __name__ == '__main__':
    main()
