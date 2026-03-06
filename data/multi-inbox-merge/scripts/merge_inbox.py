#!/usr/bin/env python3
import argparse
import csv
import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timezone, timedelta

URGENT_WORDS = ["urgent", "asap", "today", "blocked", "紧急", "尽快", "今天"]


def parse_ts(s):
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None

    # 支持毫秒时间戳
    if s.isdigit():
        try:
            v = int(s)
            if v > 10**12:
                return datetime.fromtimestamp(v / 1000, tz=timezone.utc)
            return datetime.fromtimestamp(v, tz=timezone.utc)
        except Exception:
            return None

    try:
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        return datetime.fromisoformat(s)
    except Exception:
        return None


def read_csv(path):
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 兼容常见结构：list / {messages:[...]} / {data:[...]}
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get('messages'), list):
            return data['messages']
        if isinstance(data.get('data'), list):
            return data['data']
    return []


def normalize_phone(s):
    if not s:
        return ''
    digits = ''.join(ch for ch in str(s) if ch.isdigit() or ch == '+')
    return digits


def normalize_contact(row):
    email = (row.get('email') or row.get('contact_key') or '').strip().lower()
    if '@' in email:
        return email
    phone = normalize_phone(row.get('phone') or row.get('contact_key') or row.get('sender_mobile') or row.get('staff_mobile') or '')
    if phone:
        return phone
    return (row.get('user_id') or row.get('sender') or row.get('sender_staff_id') or row.get('conversation_id') or 'unknown').strip().lower()


def normalize_row(row, source_hint='unknown'):
    source = (row.get('source') or source_hint or 'unknown').strip().lower()
    text = (row.get('text') or row.get('content') or row.get('msg_content') or '').strip()
    ts_raw = row.get('timestamp') or row.get('time') or row.get('created_at') or row.get('msg_time') or row.get('send_time') or ''
    ts = parse_ts(ts_raw)
    sender = (row.get('sender') or row.get('from') or row.get('sender_nick') or row.get('sender_name') or '').strip()
    direction = (row.get('direction') or '').strip().lower()

    # 钉钉常见方向兜底
    if not direction:
        is_from_me = str(row.get('is_from_me') or '').lower()
        if is_from_me in ('1', 'true', 'yes'):
            direction = 'outbound'
        elif is_from_me in ('0', 'false', 'no'):
            direction = 'inbound'

    thread_id = (row.get('thread_id') or row.get('conversation_id') or row.get('chat_id') or '').strip()

    return {
        'source': source,
        'contact_key': normalize_contact(row),
        'sender': sender,
        'timestamp': ts.isoformat() if ts else '',
        'text': text,
        'thread_id': thread_id,
        'direction': direction,
    }


def load_rows(fp):
    ext = os.path.splitext(fp)[1].lower()
    if ext == '.csv':
        return read_csv(fp)
    if ext == '.json':
        return read_json(fp)
    return []


def urgency_score(messages):
    score = 0
    if not messages:
        return score
    latest = messages[-1]
    latest_text = (latest.get('text') or '').lower()
    if any(w in latest_text for w in URGENT_WORDS):
        score += 3

    ts = parse_ts(latest.get('timestamp', ''))
    if ts and ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if latest.get('direction') == 'inbound' and ts:
        if datetime.now(timezone.utc) - ts > timedelta(hours=24):
            score += 2

    now = datetime.now(timezone.utc)
    inbound_recent = 0
    for m in messages:
        mts = parse_ts(m.get('timestamp', ''))
        if not mts:
            continue
        if mts.tzinfo is None:
            mts = mts.replace(tzinfo=timezone.utc)
        if m.get('direction') == 'inbound' and now - mts <= timedelta(hours=48):
            inbound_recent += 1
    if inbound_recent >= 3:
        score += 1

    return score


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', nargs='+', required=True, help='输入文件（支持 CSV/JSON，可用通配符）')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    files = []
    for p in args.inputs:
        files.extend(glob.glob(p))
    files = sorted(set(files))

    merged = []
    for fp in files:
        source_hint = os.path.basename(fp).split('.')[0].lower()
        for r in load_rows(fp):
            if not isinstance(r, dict):
                continue
            nr = normalize_row(r, source_hint)
            if nr['contact_key'] and nr['text']:
                merged.append(nr)

    seen = set()
    dedup = []
    for r in merged:
        key = (r['source'], r['contact_key'], r['timestamp'], r['text'])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)

    dedup.sort(key=lambda x: (x['contact_key'], x['timestamp']))

    threads = defaultdict(list)
    for r in dedup:
        threads[r['contact_key']].append(r)

    thread_rows = []
    followups = []
    for ck, msgs in threads.items():
        latest = msgs[-1]
        score = urgency_score(msgs)
        thread_rows.append({
            'contact_key': ck,
            'message_count': len(msgs),
            'latest_timestamp': latest.get('timestamp', ''),
            'latest_source': latest.get('source', ''),
            'latest_sender': latest.get('sender', ''),
            'urgency_score': score,
        })
        followups.append({
            'contact_key': ck,
            'urgency_score': score,
            'latest_timestamp': latest.get('timestamp', ''),
            'suggested_next_action': '立即回复并确认下一步' if score >= 3 else '常规跟进',
        })

    followups.sort(key=lambda r: (-int(r['urgency_score']), r['latest_timestamp']))

    os.makedirs(args.out, exist_ok=True)
    write_csv(os.path.join(args.out, 'merged_messages.csv'), dedup,
              ['source', 'contact_key', 'sender', 'timestamp', 'text', 'thread_id', 'direction'])
    write_csv(os.path.join(args.out, 'threads_summary.csv'), thread_rows,
              ['contact_key', 'message_count', 'latest_timestamp', 'latest_source', 'latest_sender', 'urgency_score'])
    write_csv(os.path.join(args.out, 'followup_queue.csv'), followups,
              ['contact_key', 'urgency_score', 'latest_timestamp', 'suggested_next_action'])

    summary_path = os.path.join(args.out, 'summary.md')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write('# 多平台私信合并汇总\n\n')
        f.write(f'- 输入文件数: {len(files)}\n')
        f.write(f'- 去重后消息数: {len(dedup)}\n')
        f.write(f'- 会话线程数: {len(threads)}\n\n')
        f.write('## 紧急度最高的线程（Top10）\n')
        for r in sorted(followups, key=lambda x: int(x['urgency_score']), reverse=True)[:10]:
            f.write(f"- {r['contact_key']}: 分数={r['urgency_score']}（{r['suggested_next_action']}）\n")

    print(f'完成，输出目录: {args.out}')


if __name__ == '__main__':
    main()
