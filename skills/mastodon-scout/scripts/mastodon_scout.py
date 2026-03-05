#!/usr/bin/env python3
"""Mastodon Scout — read-only Mastodon API client. stdlib only, no pip required."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def strip_html(html):
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = (text
            .replace('&amp;', '&')
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&quot;', '"')
            .replace('&#39;', "'")
            .replace('&nbsp;', ' '))
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def fmt_time(ts):
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        diff = datetime.now(timezone.utc) - dt
        secs = diff.total_seconds()
        if secs < 3600:
            return f"{int(secs / 60)}m ago"
        if secs < 86400:
            return f"{int(secs / 3600)}h ago"
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return ts


def fmt_post(i, status):
    reblog = status.get('reblog')
    if reblog:
        # Boosted post: show original author's content, note who boosted it
        booster = status.get('account', {}).get('acct', '?')
        src = reblog
        prefix = f"[{i}] 🔁 @{booster} boosted"
    else:
        src = status
        prefix = f"[{i}]"

    acct = src.get('account', {}).get('acct', '?')
    display = src.get('account', {}).get('display_name', '').strip()
    name = f"{display} (@{acct})" if display else f"@{acct}"
    content = strip_html(src.get('content', ''))
    ts = fmt_time(src.get('created_at', ''))
    r = src.get('replies_count', 0)
    rb = src.get('reblogs_count', 0)
    fav = src.get('favourites_count', 0)
    url = src.get('url', '')
    return f"{prefix}\n{name} · {ts}\n{content}\n↩ {r}  🔁 {rb}  ⭐ {fav}\n{url}"


HTTP_ERRORS = {
    401: 'Mastodon API error: 401 Unauthorized — check MASTODON_TOKEN',
    403: 'Mastodon API error: 403 Forbidden',
    422: 'Mastodon API error: 422 Unprocessable Entity',
    429: 'Mastodon API error: 429 Rate Limited — try again later',
}


def api_get(url, token):
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')


def check(status, body):
    if status != 200:
        print(HTTP_ERRORS.get(status, f'Mastodon API error: {status}'), file=sys.stderr)
        sys.exit(1)


def print_posts(posts):
    for i, post in enumerate(posts, 1):
        print(fmt_post(i, post))
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['home', 'user-tweets', 'mentions', 'search'])
    parser.add_argument('query', nargs='?')
    parser.add_argument('--instance', default=os.environ.get('MASTODON_INSTANCE', 'https://mastodon.social'))
    parser.add_argument('--limit', type=int, default=int(os.environ.get('LIMIT', '20')))
    parser.add_argument('--json', action='store_true', dest='raw_json')
    args = parser.parse_args()

    token = os.environ.get('MASTODON_TOKEN', '')
    if not token:
        print('Error: MASTODON_TOKEN is not set', file=sys.stderr)
        sys.exit(1)

    base = args.instance.rstrip('/')

    if args.command == 'home':
        status, body = api_get(f'{base}/api/v1/timelines/home?limit={args.limit}', token)
        check(status, body)
        if args.raw_json:
            print(body)
        else:
            print_posts(json.loads(body))

    elif args.command == 'user-tweets':
        status, body = api_get(f'{base}/api/v1/accounts/verify_credentials', token)
        check(status, body)
        acct_id = json.loads(body)['id']
        status, body = api_get(f'{base}/api/v1/accounts/{acct_id}/statuses?limit={args.limit}', token)
        check(status, body)
        if args.raw_json:
            print(body)
        else:
            print_posts(json.loads(body))

    elif args.command == 'mentions':
        status, body = api_get(f'{base}/api/v1/notifications?limit={args.limit}&types[]=mention', token)
        check(status, body)
        if args.raw_json:
            print(body)
            return
        for i, notif in enumerate(json.loads(body), 1):
            post = notif.get('status', {})
            post['account'] = notif.get('account', {})
            print(fmt_post(i, post))
            print()

    elif args.command == 'search':
        if not args.query:
            print('Error: search requires a query argument', file=sys.stderr)
            sys.exit(1)
        q = urllib.parse.quote(args.query)
        status, body = api_get(f'{base}/api/v2/search?q={q}&type=statuses&limit={args.limit}', token)
        check(status, body)
        if args.raw_json:
            print(body)
        else:
            print_posts(json.loads(body).get('statuses', []))


if __name__ == '__main__':
    main()
