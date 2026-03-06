#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def safe_filename(name: str) -> str:
    name = (name or 'Untitled').strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name or 'Untitled'


def q(v: str) -> str:
    return str(v or '').replace('"', "'").strip()


def ms_to_iso(ms):
    try:
      return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).isoformat()
    except Exception:
      return ''


def sender_to_heading(sender_type: str) -> str:
    s = (sender_type or '').strip().lower()
    if s == 'user':
        return 'User'
    if s == 'agent':
        return 'Grok'
    return sender_type or 'Unknown'


def extract_tweet_urls(text: str):
    if not text:
        return []
    urls = re.findall(r'https?://x\.com/[^\s)]+/status/\d+', text, flags=re.I)
    out, seen = [], set()
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def build_markdown(conv: dict, include_reasoning: bool, separator: str) -> str:
    title = conv.get('title') or conv.get('id') or 'Untitled'
    url = conv.get('URL') or ''
    items = conv.get('items') or []

    # API list is newest-first for this endpoint; reverse for conversation flow
    ordered = list(reversed(items))

    created = ''
    if ordered:
        created = ms_to_iso(ordered[0].get('created_at_ms'))

    tweet_urls = []
    for it in items:
        tweet_urls.extend(extract_tweet_urls((it.get('message') or '') + '\n' + (it.get('thinking_trace') or '')))
    tweet_urls = list(dict.fromkeys(tweet_urls))

    lines = []
    lines.append('---')
    lines.append(f'URL: "{q(url)}"')
    lines.append(f'created: "{q(created)}"')
    if tweet_urls:
        joined_tweets = ', '.join(tweet_urls)
        lines.append(f'source_tweets: "{q(joined_tweets)}"')
    lines.append('---')
    lines.append(f'# {title}')
    lines.append('')

    for i, item in enumerate(ordered):
        heading = sender_to_heading(item.get('sender_type'))
        message = (item.get('message') or '').strip()
        lines.append(f'## {heading}')
        lines.append('')
        lines.append(message if message else '_empty message_')
        lines.append('')

        if include_reasoning and heading == 'Grok':
            reasoning = (item.get('thinking_trace') or '').strip()
            if reasoning:
                lines.append('### Reasoning')
                lines.append('')
                lines.append('```text')
                lines.append(reasoning)
                lines.append('```')
                lines.append('')

        if i < len(ordered) - 1:
            lines.append(separator)
            lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main():
    ap = argparse.ArgumentParser(description='Convert grok-network-capture JSON to Obsidian Markdown files')
    ap.add_argument('--input', required=True, help='Path to grok-network-capture-*.json')
    ap.add_argument('--out', default='.', help='Output folder (default: current directory)')
    ap.add_argument('--include-reasoning', action='store_true', help='Include thinking_trace blocks')
    ap.add_argument('--separator', default='---', help='Turn separator line')
    ap.add_argument('--overwrite', action='store_true', help='Overwrite existing files with same title')
    args = ap.parse_args()

    src = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(src.read_text(encoding='utf-8'))
    conversations = data.get('conversations') or []

    written = 0
    skipped = 0

    for conv in conversations:
        if conv.get('error') == 'not_captured':
            skipped += 1
            continue

        title = conv.get('title') or conv.get('id') or 'Untitled'
        content = build_markdown(conv, include_reasoning=args.include_reasoning, separator=args.separator)
        base = safe_filename(title)

        target = out_dir / f'{base}.md'
        if target.exists() and not args.overwrite:
            n = 2
            while True:
                alt = out_dir / f'{base} {n}.md'
                if not alt.exists():
                    target = alt
                    break
                n += 1

        target.write_text(content, encoding='utf-8')
        written += 1

    print(json.dumps({
        'input': str(src),
        'output': str(out_dir),
        'written': written,
        'skipped_not_captured': skipped,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
