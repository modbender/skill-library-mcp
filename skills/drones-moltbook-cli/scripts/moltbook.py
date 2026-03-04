#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path('/opt/moltbook-cli/.env')
STATE_PATH = Path('/opt/moltbook-cli/state.json')


def load_env():
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())


def load_state():
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def api_base():
    base = os.environ.get('MOLTBOOK_API', 'https://www.moltbook.com/api/v1').strip()
    return base.rstrip('/')


def auth_header():
    key = os.environ.get('MOLTBOOK_KEY', '').strip()
    if not key:
        raise SystemExit('MOLTBOOK_KEY not set. Put it in /opt/moltbook-cli/.env')
    return {'Authorization': f'Bearer {key}'}


def request(method, path, body=None):
    url = api_base() + path
    data = None
    headers = auth_header()
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        payload = e.read().decode('utf-8', errors='ignore')
        raise SystemExit(f'HTTP {e.code}: {payload}')


def truncate(text: str, max_len: int = 120) -> str:
    text = (text or '').strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + '…'


def store_last_feed(posts):
    state = load_state()
    state['last_feed'] = [
        {
            'id': p.get('id'),
            'title': p.get('title'),
            'url': p.get('url') or p.get('permalink') or p.get('post_url'),
            'author': (p.get('author') or {}).get('name'),
            'submolt': (p.get('submolt') or {}).get('name') if isinstance(p.get('submolt'), dict) else p.get('submolt')
        }
        for p in posts
    ]
    save_state(state)


def resolve_post_ref(ref):
    ref = str(ref).strip()
    if ref.isdigit():
        state = load_state()
        last_feed = state.get('last_feed', [])
        idx = int(ref)
        if 1 <= idx <= len(last_feed):
            return last_feed[idx - 1]['id'], last_feed[idx - 1]
    return ref, None


def cmd_feed(args):
    sort = args.sort
    limit = args.limit
    submolt = args.submolt
    params = {'sort': sort, 'limit': limit}
    if submolt:
        params['submolt'] = submolt
    query = urllib.parse.urlencode(params)
    res = request('GET', f'/posts?{query}')
    posts = res.get('posts', [])
    if not posts:
        print('No posts')
        return
    store_last_feed(posts)
    for idx, p in enumerate(posts, start=1):
        title = truncate(p.get('title', ''), 120)
        author = p.get('author', {}).get('name', 'unknown')
        comments = p.get('comment_count', 0)
        upvotes = p.get('upvotes', 0)
        post_id = p.get('id', '')
        print(f"{idx}. {title}")
        print(f"   ↑ {upvotes}  •  {comments} comments  •  by {author}")
        print(f"   id: {post_id}")
        if idx < len(posts):
            print()


def cmd_find(args):
    keyword = args.keyword
    limit = args.limit
    res = request('GET', f'/posts?sort=new&limit={limit}')
    pattern = re.compile(re.escape(keyword), re.I)
    for p in res.get('posts', []):
        title = p.get('title') or ''
        content = p.get('content') or ''
        if pattern.search(title) or pattern.search(content):
            print(json.dumps({
                'id': p.get('id'),
                'title': title,
                'author': p.get('author', {}).get('name'),
                'upvotes': p.get('upvotes', 0),
            }, ensure_ascii=False))


def cmd_show(args):
    post_id, cached = resolve_post_ref(args.post_id)
    res = request('GET', f"/posts/{post_id}")
    post = res.get('post') or res
    if not isinstance(post, dict):
        print(json.dumps(res, ensure_ascii=False))
        return
    title = post.get('title') or (cached.get('title') if cached else '')
    author = (post.get('author') or {}).get('name') or (cached.get('author') if cached else 'unknown')
    url = post.get('url') or post.get('permalink') or post.get('post_url') or (cached.get('url') if cached else None)
    print(f"Title: {title}")
    print(f"Author: {author}")
    if url:
        print(f"URL: {url}")
    print(f"ID: {post.get('id', post_id)}")


def cmd_open(args):
    post_id, cached = resolve_post_ref(args.post_id)
    res = request('GET', f"/posts/{post_id}")
    post = res.get('post') or res
    if isinstance(post, dict):
        url = post.get('url') or post.get('permalink') or post.get('post_url') or (cached.get('url') if cached else None)
        if url:
            print(url)
            return
    print(f"No URL found. Post ID: {post_id}")


def cmd_comments(args):
    post_id, _ = resolve_post_ref(args.post_id)
    sort = args.sort
    limit = args.limit
    res = request('GET', f"/posts/{post_id}/comments?sort={urllib.parse.quote(sort)}&limit={limit}")
    comments = res.get('comments', [])
    if not comments:
        print('No comments')
        return
    for idx, c in enumerate(comments, start=1):
        author = (c.get('author') or {}).get('name', 'unknown')
        cid = c.get('id', '')
        content = truncate(c.get('content', ''), 160)
        print(f"{idx}. {author}: {content}")
        print(f"   id: {cid}")
        if idx < len(comments):
            print()


def cmd_mine(args):
    limit = args.limit
    res = request('GET', '/agents/me')
    agent = res.get('agent') or res.get('profile') or {}
    name = agent.get('name')
    recent = agent.get('recentPosts') or res.get('recentPosts')
    posts = []
    if isinstance(recent, list) and recent:
        posts = recent[:limit]
    else:
        res2 = request('GET', f'/posts?sort=new&limit={limit}')
        for p in res2.get('posts', []):
            author = (p.get('author') or {}).get('name')
            if name and author == name:
                posts.append(p)
    if not posts:
        print('No posts')
        return
    store_last_feed(posts)
    for idx, p in enumerate(posts, start=1):
        title = truncate(p.get('title', ''), 120)
        post_id = p.get('id', '')
        print(f"{idx}. {title}")
        print(f"   id: {post_id}")
        if idx < len(posts):
            print()


def cmd_like(args):
    res = request('POST', f"/posts/{args.post_id}/upvote")
    print(res.get('message') or res.get('error') or 'ok')


def cmd_post(args):
    body = {'title': args.title, 'content': args.content, 'submolt': args.submolt}
    res = request('POST', '/posts', body)
    print(json.dumps(res, ensure_ascii=False))


def cmd_comment(args):
    body = {'content': args.text}
    res = request('POST', f"/posts/{args.post_id}/comments", body)
    print(json.dumps(res, ensure_ascii=False))


def cmd_reply(args):
    body = {'content': args.text, 'parent_id': args.parent_id}
    res = request('POST', f"/posts/{args.post_id}/comments", body)
    print(json.dumps(res, ensure_ascii=False))


def cmd_delete(args):
    res = request('DELETE', f"/posts/{args.post_id}")
    print(json.dumps(res, ensure_ascii=False))


def cmd_follow(args):
    res = request('POST', f"/agents/{args.name}/follow")
    print(json.dumps(res, ensure_ascii=False))


def cmd_unfollow(args):
    res = request('DELETE', f"/agents/{args.name}/follow")
    print(json.dumps(res, ensure_ascii=False))


def openclaw_generate(prompt):
    agent = os.environ.get('OPENCLAW_AGENT', 'main').strip()
    cmd = ['openclaw', 'agent', '--agent', agent, '--message', prompt, '--json', '--timeout', '120']
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(proc.stdout)
    payloads = data.get('result', {}).get('payloads', [])
    if not payloads:
        raise SystemExit('OpenClaw returned no payloads')
    return payloads[0].get('text', '').strip()


def cmd_respond(args):
    keyword = args.keyword
    limit = args.limit
    res = request('GET', f'/posts?sort=new&limit={limit}')
    pattern = re.compile(re.escape(keyword), re.I)
    matched = []
    for p in res.get('posts', []):
        title = p.get('title') or ''
        content = p.get('content') or ''
        if pattern.search(title) or pattern.search(content):
            matched.append(p)
    if not matched:
        print('No matching posts')
        return

    post = matched[0]
    prompt = (
        'Write a concise, friendly comment (1-3 sentences) relevant to this Moltbook post. '
        'Do not include hashtags or links.\n\n'
        f"Title: {post.get('title','')}\n"
        f"Content: {post.get('content','')}\n"
    )
    comment_text = openclaw_generate(prompt)

    if args.dry_run:
        print('DRY RUN')
        print(f"Post id: {post.get('id')}")
        print(comment_text)
        return

    body = {'content': comment_text}
    res = request('POST', f"/posts/{post.get('id')}/comments", body)
    print(json.dumps(res, ensure_ascii=False))


def build_parser():
    p = argparse.ArgumentParser(description='Moltbook CLI')
    sub = p.add_subparsers(dest='cmd', required=True)

    feed = sub.add_parser('feed', help='Show feed')
    feed.add_argument('sort', nargs='?', default='hot')
    feed.add_argument('limit', nargs='?', type=int, default=10)
    feed.add_argument('--submolt', dest='submolt', default=None)
    feed.set_defaults(func=cmd_feed)

    find = sub.add_parser('find', help='Find posts by keyword (local search)')
    find.add_argument('keyword')
    find.add_argument('limit', nargs='?', type=int, default=50)
    find.set_defaults(func=cmd_find)

    show = sub.add_parser('show', help='Show post details by id or last feed index')
    show.add_argument('post_id')
    show.set_defaults(func=cmd_show)

    open_cmd = sub.add_parser('open', help='Print post URL by id or last feed index')
    open_cmd.add_argument('post_id')
    open_cmd.set_defaults(func=cmd_open)

    comments = sub.add_parser('comments', help='List comments for a post')
    comments.add_argument('post_id')
    comments.add_argument('sort', nargs='?', default='top')
    comments.add_argument('limit', nargs='?', type=int, default=20)
    comments.set_defaults(func=cmd_comments)

    mine = sub.add_parser('mine', help='List your recent posts')
    mine.add_argument('limit', nargs='?', type=int, default=10)
    mine.set_defaults(func=cmd_mine)

    like = sub.add_parser('like', help='Upvote a post')
    like.add_argument('post_id')
    like.set_defaults(func=cmd_like)

    post = sub.add_parser('post', help='Create a post')
    post.add_argument('title')
    post.add_argument('content')
    post.add_argument('submolt', nargs='?', default='general')
    post.set_defaults(func=cmd_post)

    comment = sub.add_parser('comment', help='Comment on a post')
    comment.add_argument('post_id')
    comment.add_argument('text')
    comment.set_defaults(func=cmd_comment)

    reply = sub.add_parser('reply', help='Reply to a comment')
    reply.add_argument('post_id')
    reply.add_argument('parent_id')
    reply.add_argument('text')
    reply.set_defaults(func=cmd_reply)

    delete = sub.add_parser('delete', help='Delete a post')
    delete.add_argument('post_id')
    delete.set_defaults(func=cmd_delete)

    follow = sub.add_parser('follow', help='Follow a molty by name')
    follow.add_argument('name')
    follow.set_defaults(func=cmd_follow)

    unfollow = sub.add_parser('unfollow', help='Unfollow a molty by name')
    unfollow.add_argument('name')
    unfollow.set_defaults(func=cmd_unfollow)

    respond = sub.add_parser('respond', help='Find by keyword and comment using OpenClaw')
    respond.add_argument('keyword')
    respond.add_argument('limit', nargs='?', type=int, default=30)
    respond.add_argument('--post', dest='dry_run', action='store_false', help='Actually post comment')
    respond.set_defaults(func=cmd_respond, dry_run=True)

    return p


def main():
    load_env()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
