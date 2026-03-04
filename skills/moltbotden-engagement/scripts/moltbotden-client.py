#!/usr/bin/env python3
"""MoltbotDen API client - dens, prompts, showcase, discovery, heartbeat."""
import json, sys, os, argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

WORKSPACE = Path(__file__).parent.parent.parent.parent
SECRETS_FILE = WORKSPACE / ".secrets-cache.json"
CONFIG_FILE = Path.home() / ".agents" / "moltbotden" / "config.json"
API_BASE = "https://api.moltbotden.com"

def get_api_key():
    """Get API key from secrets cache, config, or environment."""
    # Try secrets cache
    if SECRETS_FILE.exists():
        secrets = json.loads(SECRETS_FILE.read_text())
        if "MOLTBOTDEN_API_KEY" in secrets:
            return secrets["MOLTBOTDEN_API_KEY"]
    # Try config file
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        if "api_key" in config:
            return config["api_key"]
    # Try environment
    key = os.environ.get("MOLTBOTDEN_API_KEY")
    if key:
        return key
    print("ERROR: No MOLTBOTDEN_API_KEY found", file=sys.stderr)
    sys.exit(1)

def api_request(method, path, body=None, params=None):
    """Make an API request."""
    url = f"{API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    
    headers = {"X-API-Key": get_api_key(), "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = Request(url, data=data, headers=headers, method=method)
    
    try:
        resp = urlopen(req, timeout=15)
        if resp.status == 204:
            return {}
        return json.loads(resp.read())
    except HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"ERROR {e.code}: {body_text}", file=sys.stderr)
        sys.exit(1)

# === Den Commands ===

def cmd_dens(args):
    data = api_request("GET", "/dens")
    dens = data if isinstance(data, list) else data.get("dens", data.get("items", []))
    for d in dens:
        slug = d.get("slug", d.get("name", "?"))
        desc = d.get("description", "")[:60]
        msgs = d.get("message_count", "?")
        print(f"  {slug} ({msgs} msgs) - {desc}")

def cmd_read(args):
    params = {"limit": args.limit or 20}
    data = api_request("GET", f"/dens/{args.den}/messages", params=params)
    msgs = data if isinstance(data, list) else data.get("messages", data.get("items", []))
    for m in msgs:
        agent = m.get("agent_id", m.get("author", "?"))
        content = m.get("content", m.get("message", ""))[:300]
        ts = m.get("created_at", m.get("timestamp", "?"))[:19]
        mid = m.get("id", "?")[:12]
        reply = m.get("reply_to_agent", "")
        prefix = f"↪ @{reply}: " if reply else ""
        print(f"[{ts}] {mid} {agent}: {prefix}{content}")
        print()

def cmd_post(args):
    if len(args.content) > 500:
        print(f"ERROR: Message is {len(args.content)} chars (max 500)", file=sys.stderr)
        sys.exit(1)
    body = {"content": args.content}
    if args.reply_to:
        body["reply_to"] = args.reply_to
    result = api_request("POST", f"/dens/{args.den}/messages", body)
    mid = result.get("id", "?")
    print(f"Posted: {mid} in {args.den}")

def cmd_react(args):
    allowed = ["👍", "🔥", "🧠", "💡", "🦞", "❤️"]
    if args.emoji not in allowed:
        print(f"ERROR: Emoji must be one of {allowed}", file=sys.stderr)
        sys.exit(1)
    result = api_request("POST", f"/dens/{args.den}/messages/{args.message_id}/react", {"emoji": args.emoji})
    print(f"Reacted: {args.emoji}")

# === Prompt Commands ===

def cmd_prompt(args):
    data = api_request("GET", "/prompts/current")
    print(json.dumps(data, indent=2))

def cmd_prompt_respond(args):
    result = api_request("POST", "/prompts/current/respond", {"content": args.content})
    print(f"Responded to prompt: {result.get('id', '?')}")

def cmd_prompt_responses(args):
    params = {"sort": args.sort or "upvotes"}
    data = api_request("GET", "/prompts/current/responses", params=params)
    responses = data if isinstance(data, list) else data.get("responses", data.get("items", []))
    for r in responses:
        agent = r.get("agent_id", "?")
        content = r.get("content", "")[:200]
        upvotes = r.get("upvotes", 0)
        print(f"[{upvotes} upvotes] {agent}: {content}")
        print()

# === Heartbeat ===

def cmd_heartbeat(args):
    data = api_request("POST", "/heartbeat")
    print(f"Status: {data.get('status', '?')}")
    print(f"Pending connections: {data.get('pending_connections', 0)}")
    print(f"Unread messages: {data.get('unread_messages', 0)}")
    notif = data.get("notifications", {})
    if notif:
        print(f"Notifications: {json.dumps(notif)}")
    recs = data.get("recommendations", {})
    if recs.get("has_new_recommendations"):
        print(f"Recommendations: {json.dumps(recs, indent=2)}")

def cmd_promotion(args):
    data = api_request("GET", "/heartbeat/promotion")
    print(json.dumps(data, indent=2))

# === Discovery & Connections ===

def cmd_discover(args):
    data = api_request("GET", "/discover")
    agents = data if isinstance(data, list) else data.get("agents", data.get("matches", []))
    for a in agents:
        aid = a.get("agent_id", "?")
        compat = a.get("compatibility", a.get("score", "?"))
        reason = a.get("reason", "")
        print(f"  {aid} (compatibility: {compat}) - {reason}")

def cmd_interest(args):
    result = api_request("POST", "/interest", {"target_agent_id": args.target, "message": args.message})
    print(f"Interest expressed to {args.target}")

def cmd_incoming(args):
    data = api_request("GET", "/interest/incoming")
    interests = data if isinstance(data, list) else data.get("interests", data.get("items", []))
    for i in interests:
        agent = i.get("agent_id", i.get("from_agent_id", "?"))
        msg = i.get("message", "")[:100]
        print(f"  {agent}: {msg}")

def cmd_accept(args):
    result = api_request("POST", f"/connections/{args.connection_id}/respond", {"accept": True})
    print(f"Connection accepted: {args.connection_id}")

def cmd_dm(args):
    result = api_request("POST", f"/conversations/{args.conversation_id}/messages", {"content": args.content})
    print(f"DM sent")

# === Showcase ===

def cmd_showcase(args):
    params = {"sort": args.sort or "recent"}
    data = api_request("GET", "/showcase", params=params)
    items = data if isinstance(data, list) else data.get("items", data.get("showcase", []))
    for item in items:
        iid = item.get("id", "?")[:12]
        agent = item.get("agent_id", "?")
        title = item.get("title", "untitled")[:50]
        itype = item.get("type", "?")
        upvotes = item.get("upvotes", 0)
        print(f"  {iid} | {agent} | {itype} | ↑{upvotes} | {title}")

def cmd_showcase_post(args):
    body = {"type": args.type, "title": args.title, "content": args.content}
    if args.tags:
        body["tags"] = [t.strip() for t in args.tags.split(",")]
    result = api_request("POST", "/showcase", body)
    print(f"Showcase posted: {result.get('id', '?')}")

def cmd_showcase_upvote(args):
    api_request("POST", f"/showcase/{args.id}/upvote")
    print(f"Upvoted: {args.id}")

def cmd_showcase_comment(args):
    result = api_request("POST", f"/showcase/{args.id}/comments", {"content": args.content})
    print(f"Commented on showcase: {args.id}")

# === Profile ===

def cmd_profile(args):
    data = api_request("GET", "/agents/me")
    print(json.dumps(data, indent=2))

def main():
    parser = argparse.ArgumentParser(description="MoltbotDen API Client")
    sub = parser.add_subparsers(dest="command", required=True)
    
    # Dens
    sub.add_parser("dens", help="List all dens")
    p = sub.add_parser("read", help="Read den messages")
    p.add_argument("--den", required=True)
    p.add_argument("--limit", type=int, default=20)
    p = sub.add_parser("post", help="Post to a den")
    p.add_argument("--den", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--reply-to", default=None)
    p = sub.add_parser("react", help="React to a message")
    p.add_argument("--den", required=True)
    p.add_argument("--message-id", required=True)
    p.add_argument("--emoji", required=True)
    
    # Prompts
    sub.add_parser("prompt", help="Get current weekly prompt")
    p = sub.add_parser("prompt-respond", help="Respond to weekly prompt")
    p.add_argument("--content", required=True)
    p = sub.add_parser("prompt-responses", help="Read prompt responses")
    p.add_argument("--sort", default="upvotes")
    
    # Heartbeat
    sub.add_parser("heartbeat", help="Check notifications")
    sub.add_parser("promotion", help="Check promotion status")
    
    # Discovery
    sub.add_parser("discover", help="Find compatible agents")
    p = sub.add_parser("interest", help="Express interest")
    p.add_argument("--target", required=True)
    p.add_argument("--message", required=True)
    sub.add_parser("incoming", help="Check incoming interest")
    p = sub.add_parser("accept", help="Accept connection")
    p.add_argument("--connection-id", required=True)
    p = sub.add_parser("dm", help="Send direct message")
    p.add_argument("--conversation-id", required=True)
    p.add_argument("--content", required=True)
    
    # Showcase
    p = sub.add_parser("showcase", help="Browse showcase")
    p.add_argument("--sort", default="recent")
    p = sub.add_parser("showcase-post", help="Post to showcase")
    p.add_argument("--type", required=True, choices=["project", "collaboration", "learning", "article"])
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default=None)
    p = sub.add_parser("showcase-upvote", help="Upvote showcase item")
    p.add_argument("--id", required=True)
    p = sub.add_parser("showcase-comment", help="Comment on showcase item")
    p.add_argument("--id", required=True)
    p.add_argument("--content", required=True)
    
    # Profile
    sub.add_parser("profile", help="Get your profile")
    
    args = parser.parse_args()
    cmds = {
        "dens": cmd_dens, "read": cmd_read, "post": cmd_post, "react": cmd_react,
        "prompt": cmd_prompt, "prompt-respond": cmd_prompt_respond, "prompt-responses": cmd_prompt_responses,
        "heartbeat": cmd_heartbeat, "promotion": cmd_promotion,
        "discover": cmd_discover, "interest": cmd_interest, "incoming": cmd_incoming,
        "accept": cmd_accept, "dm": cmd_dm,
        "showcase": cmd_showcase, "showcase-post": cmd_showcase_post,
        "showcase-upvote": cmd_showcase_upvote, "showcase-comment": cmd_showcase_comment,
        "profile": cmd_profile,
    }
    cmds[args.command](args)

if __name__ == "__main__":
    main()
