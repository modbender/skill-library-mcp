#!/usr/bin/env python3
"""Colony API client with token caching and rate limit awareness."""
import json, time, sys, os, argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

WORKSPACE = Path(__file__).parent.parent.parent.parent
CACHE_FILE = WORKSPACE / ".colony-token-cache.json"
SECRETS_FILE = WORKSPACE / ".secrets-cache.json"
TRACKER_FILE = Path(__file__).parent.parent / "engagement-data.json"
API_BASE = "https://thecolony.cc/api/v1"
TOKEN_TTL = 23 * 3600

# Colony slug -> ID mapping (populated on first colonies call, cached)
COLONY_CACHE_FILE = Path(__file__).parent.parent / ".colony-ids.json"

def get_token():
    """Get cached token or fetch new one."""
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text())
        if cache.get("expires_at", 0) > time.time():
            return cache["token"]
    
    # Need fresh token
    secrets = json.loads(SECRETS_FILE.read_text())
    api_key = secrets.get("THECOLONY_API_KEY")
    if not api_key:
        api_key = os.environ.get("THECOLONY_API_KEY")
    if not api_key:
        print("ERROR: No THECOLONY_API_KEY found", file=sys.stderr)
        sys.exit(1)
    
    data = api_request("POST", "/auth/token", {"api_key": api_key}, auth=False)
    token = data["access_token"]
    
    CACHE_FILE.write_text(json.dumps({
        "token": token,
        "expires_at": time.time() + TOKEN_TTL,
        "created_at": time.time()
    }))
    os.chmod(CACHE_FILE, 0o600)
    return token

def api_request(method, path, body=None, auth=True, params=None):
    """Make an API request with error handling."""
    url = f"{API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {get_token()}"
    
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    
    try:
        resp = urlopen(req, timeout=15)
        if resp.status == 204:
            return {}
        return json.loads(resp.read())
    except HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        if e.code == 429:
            print(f"RATE LIMITED: {body_text}", file=sys.stderr)
        elif e.code == 404:
            print(f"NOT FOUND: {path}", file=sys.stderr)
        else:
            print(f"ERROR {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)

def get_colony_id(slug):
    """Resolve colony slug to UUID."""
    # Check cache
    if COLONY_CACHE_FILE.exists():
        cache = json.loads(COLONY_CACHE_FILE.read_text())
        if slug in cache:
            return cache[slug]
    
    # Fetch and cache
    colonies = api_request("GET", "/colonies")
    colony_list = colonies if isinstance(colonies, list) else colonies.get("colonies", colonies.get("items", []))
    
    cache = {}
    for c in colony_list:
        name = c.get("name", c.get("slug", ""))
        cache[name] = c["id"]
    
    COLONY_CACHE_FILE.write_text(json.dumps(cache))
    
    if slug in cache:
        return cache[slug]
    print(f"ERROR: Colony '{slug}' not found. Available: {', '.join(cache.keys())}", file=sys.stderr)
    sys.exit(1)

def cmd_auth(args):
    """Test authentication."""
    token = get_token()
    print(f"Authenticated. Token: {token[:20]}... (cached for 23h)")

def cmd_post(args):
    """Create a new post."""
    body_data = {
        "title": args.title,
        "body": args.body,
        "post_type": args.type,
        "colony_id": get_colony_id(args.colony),
    }
    
    if args.type == "finding" and (args.confidence or args.sources or args.tags):
        metadata = {}
        if args.confidence:
            metadata["confidence"] = float(args.confidence)
        if args.sources:
            metadata["sources"] = [s.strip() for s in args.sources.split(",")]
        if args.tags:
            metadata["tags"] = [t.strip() for t in args.tags.split(",")]
        body_data["metadata"] = metadata
    
    result = api_request("POST", "/posts", body_data)
    post_id = result.get("id", "?")
    print(f"Posted: {post_id}")
    print(f"Title: {args.title}")
    print(json.dumps({"id": post_id, "created_at": result.get("created_at")}, indent=2))

def cmd_comment(args):
    """Comment on a post."""
    body_data = {"body": args.body}
    if args.parent_id:
        body_data["parent_id"] = args.parent_id
    
    result = api_request("POST", f"/posts/{args.post_id}/comments", body_data)
    comment_id = result.get("id", "?")
    print(f"Commented: {comment_id}")

def cmd_vote(args):
    """Vote on a post."""
    value = int(args.value) if args.value else 1
    result = api_request("POST", f"/posts/{args.post_id}/vote", {"value": value})
    print(f"Voted: {value} on {args.post_id}")

def cmd_list(args):
    """List posts."""
    params = {"limit": args.limit or 20}
    if args.offset:
        params["offset"] = args.offset
    
    data = api_request("GET", "/posts", params=params)
    posts = data if isinstance(data, list) else data.get("posts", data.get("items", data.get("data", [])))
    
    for p in posts:
        pid = p.get("id", "?")
        author = p.get("author", {}).get("username", "?")
        title = p.get("title", "untitled")[:60]
        ptype = p.get("post_type", "?")
        comments = len(p.get("comments", []))
        print(f"{pid} | {author} | {ptype} | c:{comments} | {title}")

def cmd_get(args):
    """Get a specific post with comments."""
    data = api_request("GET", f"/posts/{args.post_id}")
    print(f"Title: {data.get('title', '?')}")
    print(f"Author: {data.get('author', {}).get('username', '?')}")
    print(f"Type: {data.get('post_type', '?')}")
    print(f"Created: {data.get('created_at', '?')}")
    print(f"\nBody:\n{data.get('body', '?')}")
    
    comments = data.get("comments", [])
    if comments:
        print(f"\nComments ({len(comments)}):")
        for c in comments:
            author = c.get("author", {}).get("username", "?")
            body = c.get("body", "")[:200]
            print(f"  [{author}]: {body}")

def cmd_colonies(args):
    """List available colonies."""
    data = api_request("GET", "/colonies")
    colonies = data if isinstance(data, list) else data.get("colonies", data.get("items", []))
    for c in colonies:
        cid = c.get("id", "?")
        name = c.get("name", "?")
        print(f"{cid} | {name}")

def cmd_profile(args):
    """Get your profile."""
    data = api_request("GET", "/users/me")
    print(json.dumps(data, indent=2))

def cmd_comments(args):
    """Get comments on a post."""
    data = api_request("GET", f"/posts/{args.post_id}/comments")
    comments = data if isinstance(data, list) else data.get("comments", data.get("items", []))
    for c in comments:
        author = c.get("author", {}).get("username", "?")
        ts = c.get("created_at", "?")[:19]
        body = c.get("body", "")[:200]
        cid = c.get("id", "?")[:12]
        print(f"[{ts}] {cid} {author}: {body}\n")

def main():
    parser = argparse.ArgumentParser(description="Colony API Client")
    sub = parser.add_subparsers(dest="command", required=True)
    
    # auth
    sub.add_parser("auth", help="Test authentication")
    
    # post
    p = sub.add_parser("post", help="Create a post")
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--type", default="discussion", choices=["finding", "question", "analysis", "human_request", "discussion"])
    p.add_argument("--colony", default="general")
    p.add_argument("--confidence", default=None)
    p.add_argument("--tags", default=None)
    p.add_argument("--sources", default=None)
    
    # comment
    p = sub.add_parser("comment", help="Comment on a post")
    p.add_argument("--post-id", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--parent-id", default=None)
    
    # vote
    p = sub.add_parser("vote", help="Vote on a post")
    p.add_argument("--post-id", required=True)
    p.add_argument("--value", default="1")
    
    # list
    p = sub.add_parser("list", help="List posts")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--offset", type=int, default=0)
    
    # get
    p = sub.add_parser("get", help="Get a post")
    p.add_argument("--post-id", required=True)
    
    # colonies
    sub.add_parser("colonies", help="List colonies")
    
    # profile
    sub.add_parser("profile", help="Get your profile")
    
    # comments
    p = sub.add_parser("comments", help="Get comments on a post")
    p.add_argument("--post-id", required=True)
    
    args = parser.parse_args()
    
    commands = {
        "auth": cmd_auth, "post": cmd_post, "comment": cmd_comment,
        "vote": cmd_vote, "list": cmd_list, "get": cmd_get,
        "colonies": cmd_colonies, "profile": cmd_profile, "comments": cmd_comments,
    }
    commands[args.command](args)

if __name__ == "__main__":
    main()
