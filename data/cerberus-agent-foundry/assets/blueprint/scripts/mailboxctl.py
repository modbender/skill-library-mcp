#!/usr/bin/env python3
import argparse, hashlib, os, re
from datetime import datetime
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAILBOX = os.path.join(ROOT, 'control-plane', 'mailbox')
ARCHIVE = os.path.join(ROOT, 'control-plane', 'mailbox', 'archive')
EVENTS = os.path.join(ROOT, 'control-plane', 'logs', 'events.jsonl')

STATUS_FLOW = {
    'UNREAD': {'ACK', 'REJECTED'},
    'ACK': {'RESOLVED', 'REJECTED'},
    'RESOLVED': set(),
    'REJECTED': set(),
}


def now_iso():
    return datetime.now().astimezone().isoformat()


def ensure_dirs():
    os.makedirs(MAILBOX, exist_ok=True)
    os.makedirs(ARCHIVE, exist_ok=True)


def parse_message(path):
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', txt, re.S)
    if not m:
        raise SystemExit(f'invalid message format: {path}')
    header_raw, body = m.group(1), m.group(2)
    header = yaml.safe_load(header_raw) or {}
    return header, body


def render_message(header, body):
    y = yaml.safe_dump(header, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{y}\n---\n{body if body.endswith(chr(10)) else body + chr(10)}"


def checksum_for(header, body):
    h = dict(header)
    h.pop('checksum', None)
    payload = yaml.safe_dump(h, sort_keys=True, allow_unicode=True) + "\n" + body
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def event(line):
    import json
    with open(EVENTS, 'a', encoding='utf-8') as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def next_msg_id():
    existing = [x for x in os.listdir(MAILBOX) if x.startswith('MSG-') and x.endswith('.md')]
    nums = []
    for n in existing:
        try:
            nums.append(int(n.split('-')[1].split('.')[0]))
        except Exception:
            pass
    i = max(nums) + 1 if nums else 1
    return f"MSG-{i:04d}"


def message_path(message_id):
    return os.path.join(MAILBOX, f"{message_id}.md")


def required_header(h):
    required = [
        'message_id','correlation_id','task_id','sender','receiver',
        'version','timestamp','status','retry_count','checksum'
    ]
    missing = [k for k in required if k not in h]
    if missing:
        raise SystemExit(f'missing header fields: {missing}')


def cmd_send(a):
    ensure_dirs()
    mid = a.message_id or next_msg_id()
    path = message_path(mid)
    if os.path.exists(path):
        raise SystemExit(f'message exists: {mid}')
    header = {
        'message_id': mid,
        'correlation_id': a.correlation_id,
        'task_id': a.task_id,
        'sender': a.sender,
        'receiver': a.receiver,
        'version': '1.0',
        'timestamp': now_iso(),
        'status': 'UNREAD',
        'retry_count': int(a.retry_count),
        'checksum': ''
    }
    body = f"# Message\n\n{a.body}\n"
    header['checksum'] = checksum_for(header, body)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(render_message(header, body))
    event({'ts': now_iso(), 'type': 'mail_send', 'message_id': mid, 'task_id': a.task_id, 'sender': a.sender, 'receiver': a.receiver})
    print(path)


def cmd_show(a):
    p = message_path(a.message_id)
    h, b = parse_message(p)
    required_header(h)
    chk = checksum_for(h, b)
    ok = (chk == h.get('checksum'))
    print(yaml.safe_dump({'header': h, 'checksum_ok': ok}, sort_keys=False, allow_unicode=True).strip())


def cmd_status(a):
    p = message_path(a.message_id)
    h, b = parse_message(p)
    required_header(h)
    cur = h.get('status')
    nxt = a.to
    if nxt not in STATUS_FLOW.get(cur, set()):
        raise SystemExit(f'invalid status transition: {cur}->{nxt}')

    actor = a.actor
    # Receiver can ACK/RESOLVED/REJECTED for their message; Team Lead can arbitrate any
    if actor != 'team-lead' and actor != h.get('receiver'):
        raise SystemExit('only receiver or team-lead can update status')

    h['status'] = nxt
    h['timestamp'] = now_iso()
    if a.increment_retry:
        h['retry_count'] = int(h.get('retry_count', 0)) + 1
    if a.note:
        b = b + f"\n## Response ({actor})\n\n{a.note}\n"
    h['checksum'] = checksum_for(h, b)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(render_message(h, b))
    event({'ts': now_iso(), 'type': 'mail_status', 'message_id': h['message_id'], 'task_id': h['task_id'], 'from': cur, 'to': nxt, 'actor': actor})
    print(f"{h['message_id']}: {cur} -> {nxt}")


def cmd_list(_):
    ensure_dirs()
    files = sorted([f for f in os.listdir(MAILBOX) if f.endswith('.md')])
    for fn in files:
        h, _ = parse_message(os.path.join(MAILBOX, fn))
        print(f"{h.get('message_id')}\t{h.get('status')}\t{h.get('sender')}\t{h.get('receiver')}\t{h.get('task_id')}")


def cmd_gc(a):
    ensure_dirs()
    if a.actor != 'team-lead':
        raise SystemExit('only team-lead can run mailbox GC')

    statuses = set([x.strip() for x in a.statuses.split(',') if x.strip()])
    moved = 0
    files = sorted([f for f in os.listdir(MAILBOX) if f.endswith('.md')])
    for fn in files:
        src = os.path.join(MAILBOX, fn)
        h, _ = parse_message(src)
        st = h.get('status')
        if st in statuses:
            dst = os.path.join(ARCHIVE, fn)
            os.replace(src, dst)
            moved += 1
            event({'ts': now_iso(), 'type': 'mail_gc', 'message_id': h.get('message_id'), 'task_id': h.get('task_id'), 'status': st, 'actor': a.actor})
    print(f'moved={moved} statuses={sorted(list(statuses))}')


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(required=True)

    s = sp.add_parser('send')
    s.add_argument('--task-id', required=True)
    s.add_argument('--sender', required=True)
    s.add_argument('--receiver', required=True)
    s.add_argument('--correlation-id', required=True)
    s.add_argument('--body', required=True)
    s.add_argument('--retry-count', default=0)
    s.add_argument('--message-id')
    s.set_defaults(func=cmd_send)

    sh = sp.add_parser('show')
    sh.add_argument('--message-id', required=True)
    sh.set_defaults(func=cmd_show)

    st = sp.add_parser('status')
    st.add_argument('--message-id', required=True)
    st.add_argument('--to', required=True, choices=['ACK','RESOLVED','REJECTED'])
    st.add_argument('--actor', required=True)
    st.add_argument('--note')
    st.add_argument('--increment-retry', action='store_true')
    st.set_defaults(func=cmd_status)

    ls = sp.add_parser('list')
    ls.set_defaults(func=cmd_list)

    gc = sp.add_parser('gc')
    gc.add_argument('--actor', required=True)
    gc.add_argument('--statuses', default='RESOLVED,REJECTED')
    gc.set_defaults(func=cmd_gc)

    a = ap.parse_args()
    a.func(a)


if __name__ == '__main__':
    main()
