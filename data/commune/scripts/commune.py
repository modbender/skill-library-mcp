#!/usr/bin/env python3
"""
Commune CLI — Agent-native email operations.
Usage: python scripts/commune.py <command> [options]

Commands:
  test              Verify API connection
  create-inbox      Create a new agent inbox
  list-inboxes      List all inboxes
  list-threads      List email threads in an inbox
  read-thread       Read all messages in a thread
  search            Semantic search across threads
  send              Send or reply to an email
  tag               Add tags to a thread
  untag             Remove tags from a thread
  status            Set thread triage status
  stats             Get deliverability stats
  help              Show this help
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Credential loading
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    """Load API key from env var or credentials.json."""
    key = os.environ.get("COMMUNE_API_KEY")
    if key:
        return key

    # Look for credentials.json relative to skill root
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "credentials.json"),
        os.path.expanduser("~/.config/commune/credentials.json"),
        "credentials.json",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            return data.get("api_key", "")

    print("ERROR: No API key found.")
    print("  Set COMMUNE_API_KEY environment variable, or create credentials.json:")
    print('  { "api_key": "comm_..." }')
    sys.exit(1)


def get_client():
    """Return an authenticated CommuneClient."""
    try:
        from commune import CommuneClient
    except ImportError:
        print("ERROR: commune-mail not installed. Run: pip install commune-mail")
        sys.exit(1)
    return CommuneClient(api_key=load_api_key())


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_json(obj):
    """Pretty-print a dict or list."""
    if hasattr(obj, "__dict__"):
        obj = obj.__dict__
    print(json.dumps(obj, indent=2, default=str))


def print_threads(result):
    """Print a ThreadList in a readable format."""
    threads = result.data if hasattr(result, "data") else result
    if not threads:
        print("No threads found.")
        return
    for t in threads:
        tid = getattr(t, "thread_id", "?")
        subject = getattr(t, "subject", "(no subject)")
        count = getattr(t, "message_count", "?")
        last = getattr(t, "last_message_at", "?")
        direction = getattr(t, "last_direction", "?")
        snippet = getattr(t, "snippet", "") or ""
        print(f"  [{direction}] {subject}")
        print(f"   thread_id : {tid}")
        print(f"   messages  : {count}  |  last: {last}")
        if snippet:
            print(f"   preview   : {snippet[:120]}")
        print()
    if hasattr(result, "has_more") and result.has_more:
        print(f"  → More results. Next cursor: {result.next_cursor}")


def print_messages(messages):
    """Print messages in a thread chronologically."""
    if not messages:
        print("No messages found.")
        return
    for i, msg in enumerate(messages, 1):
        direction = getattr(msg, "direction", "?")
        sender = "?"
        participants = getattr(msg, "participants", [])
        for p in participants:
            role = getattr(p, "role", None)
            if role == "sender":
                sender = getattr(p, "identity", "?")
                break
        content = getattr(msg, "content", "") or ""
        meta = getattr(msg, "metadata", None)
        subject = getattr(meta, "subject", "") if meta else ""
        created = getattr(meta, "created_at", "") if meta else ""
        print(f"  [{i}] {direction.upper()} — {sender}")
        if subject:
            print(f"       Subject : {subject}")
        if created:
            print(f"       Date    : {created}")
        print(f"       {content[:500]}")
        if len(content) > 500:
            print(f"       ... ({len(content)} chars total)")
        print()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_test(args, client):
    """Verify API connection by listing domains."""
    print("Testing Commune API connection...")
    try:
        domains = client.domains.list()
        print(f"✅ Connected. {len(domains)} domain(s) in account.")
        for d in domains:
            print(f"   • {getattr(d, 'name', d)} — {getattr(d, 'status', '')}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)


def cmd_create_inbox(args, client):
    """Create a new inbox."""
    inbox = client.inboxes.create(
        local_part=args.local_part,
        domain_id=args.domain_id or None,
        name=args.name or None,
    )
    print(f"✅ Inbox created: {inbox.address}")
    print(f"   inbox_id : {inbox.id}")
    print(f"   address  : {inbox.address}")
    print()
    print("Save these to /workspace/memory/commune-config.json:")
    config = {"inbox_id": inbox.id, "address": inbox.address}
    print(json.dumps(config, indent=2))


def cmd_list_inboxes(args, client):
    """List all inboxes."""
    inboxes = client.inboxes.list(domain_id=args.domain_id or None)
    if not inboxes:
        print("No inboxes found.")
        return
    for inbox in inboxes:
        print(f"  {getattr(inbox, 'address', '?')}  (id: {getattr(inbox, 'id', '?')})")


def cmd_list_threads(args, client):
    """List threads in an inbox."""
    result = client.threads.list(
        inbox_id=args.inbox_id or None,
        domain_id=args.domain_id or None,
        limit=args.limit,
        cursor=args.cursor or None,
        order=args.order,
    )
    print_threads(result)


def cmd_read_thread(args, client):
    """Read all messages in a thread."""
    messages = client.threads.messages(
        args.thread_id,
        limit=args.limit,
        order=args.order,
    )
    print(f"Thread: {args.thread_id}")
    print("-" * 60)
    print_messages(messages)


def cmd_search(args, client):
    """Semantic search across threads."""
    result = client.threads.search(
        query=args.query,
        inbox_id=args.inbox_id or None,
        domain_id=args.domain_id or None,
        limit=args.limit,
    )
    threads = result.data if hasattr(result, "data") else (result or [])
    if not threads:
        print(f"No results for: {args.query!r}")
        return
    print(f"Search results for: {args.query!r}")
    print()
    print_threads(result)


def cmd_send(args, client):
    """Send an email or reply in a thread."""
    result = client.messages.send(
        to=args.to,
        subject=args.subject,
        text=args.body or None,
        html=args.html or None,
        inbox_id=args.inbox_id or None,
        thread_id=args.thread_id or None,
        cc=args.cc or None,
        reply_to=args.reply_to or None,
    )
    print("✅ Email sent.")
    if hasattr(result, "message_id"):
        print(f"   message_id : {result.message_id}")
    if hasattr(result, "thread_id"):
        print(f"   thread_id  : {result.thread_id}")


def cmd_tag(args, client):
    """Add tags to a thread."""
    # The MCP uses tag_thread; the Python SDK may expose this via a different path.
    # We call the REST API directly if the SDK doesn't expose it.
    try:
        # Try SDK method first (if available)
        client.threads.tag(args.thread_id, tags=args.tags)
        print(f"✅ Tagged thread {args.thread_id} with: {args.tags}")
    except AttributeError:
        # Fall back to direct HTTP
        import urllib.request
        api_key = load_api_key()
        url = f"https://api.commune.email/v1/threads/{args.thread_id}/tags"
        body = json.dumps({"tags": args.tags}).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            resp.read()
        print(f"✅ Tagged thread {args.thread_id} with: {args.tags}")


def cmd_status(args, client):
    """Set thread triage status."""
    valid = {"open", "needs_reply", "waiting", "closed"}
    if args.status not in valid:
        print(f"ERROR: status must be one of: {', '.join(sorted(valid))}")
        sys.exit(1)
    try:
        client.threads.set_status(args.thread_id, status=args.status)
        print(f"✅ Thread {args.thread_id} status → {args.status}")
    except AttributeError:
        import urllib.request
        api_key = load_api_key()
        url = f"https://api.commune.email/v1/threads/{args.thread_id}/status"
        body = json.dumps({"status": args.status}).encode()
        req = urllib.request.Request(url, data=body, method="PATCH")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req) as resp:
            resp.read()
        print(f"✅ Thread {args.thread_id} status → {args.status}")


def cmd_stats(args, client):
    """Get deliverability stats."""
    try:
        stats = client.deliverability.stats(
            inbox_id=args.inbox_id or None,
            domain_id=args.domain_id or None,
            period=args.period,
        )
        print_json(stats)
    except AttributeError:
        import urllib.request
        api_key = load_api_key()
        params = f"period={args.period}"
        if args.inbox_id:
            params += f"&inbox_id={args.inbox_id}"
        url = f"https://api.commune.email/v1/delivery/metrics?{params}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {api_key}")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        print_json(data)


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="commune",
        description="Commune CLI — agent-native email",
    )
    sub = parser.add_subparsers(dest="command")

    # test
    sub.add_parser("test", help="Verify API connection")

    # create-inbox
    p = sub.add_parser("create-inbox", help="Create a new inbox")
    p.add_argument("--local-part", required=True, help="Part before @, e.g. 'support'")
    p.add_argument("--domain-id", help="Domain ID (auto-resolved if omitted)")
    p.add_argument("--name", help="Display name")

    # list-inboxes
    p = sub.add_parser("list-inboxes", help="List all inboxes")
    p.add_argument("--domain-id", help="Filter by domain")

    # list-threads
    p = sub.add_parser("list-threads", help="List email threads")
    p.add_argument("--inbox-id", help="Inbox ID")
    p.add_argument("--domain-id", help="Domain ID")
    p.add_argument("--limit", type=int, default=20, help="Number of results (default: 20)")
    p.add_argument("--cursor", help="Pagination cursor")
    p.add_argument("--order", default="desc", choices=["desc", "asc"], help="Sort order")

    # read-thread
    p = sub.add_parser("read-thread", help="Read all messages in a thread")
    p.add_argument("--thread-id", required=True, help="Thread ID")
    p.add_argument("--limit", type=int, default=50, help="Max messages (default: 50)")
    p.add_argument("--order", default="asc", choices=["asc", "desc"], help="Sort order")

    # search
    p = sub.add_parser("search", help="Semantic search across threads")
    p.add_argument("--query", required=True, help="Natural language search query")
    p.add_argument("--inbox-id", help="Inbox ID")
    p.add_argument("--domain-id", help="Domain ID")
    p.add_argument("--limit", type=int, default=10, help="Number of results (default: 10)")

    # send
    p = sub.add_parser("send", help="Send an email or reply in a thread")
    p.add_argument("--to", required=True, help="Recipient email address")
    p.add_argument("--subject", required=True, help="Subject line")
    p.add_argument("--body", help="Plain text body")
    p.add_argument("--html", help="HTML body")
    p.add_argument("--inbox-id", help="Send from this inbox")
    p.add_argument("--thread-id", help="Reply in this thread")
    p.add_argument("--cc", help="CC addresses (comma-separated)")
    p.add_argument("--reply-to", help="Reply-to address")

    # tag
    p = sub.add_parser("tag", help="Add tags to a thread")
    p.add_argument("--thread-id", required=True, help="Thread ID")
    p.add_argument("--tags", required=True, help="Comma-separated tags, e.g. 'urgent,vip'")

    # status
    p = sub.add_parser("status", help="Set thread triage status")
    p.add_argument("--thread-id", required=True, help="Thread ID")
    p.add_argument(
        "--status",
        required=True,
        choices=["open", "needs_reply", "waiting", "closed"],
        help="New status",
    )

    # stats
    p = sub.add_parser("stats", help="Get deliverability stats")
    p.add_argument("--inbox-id", help="Inbox ID")
    p.add_argument("--domain-id", help="Domain ID")
    p.add_argument("--period", default="7d", choices=["24h", "7d", "30d"], help="Time period")

    args = parser.parse_args()

    if not args.command or args.command == "help":
        parser.print_help()
        return

    client = get_client()

    dispatch = {
        "test": cmd_test,
        "create-inbox": cmd_create_inbox,
        "list-inboxes": cmd_list_inboxes,
        "list-threads": cmd_list_threads,
        "read-thread": cmd_read_thread,
        "search": cmd_search,
        "send": cmd_send,
        "tag": cmd_tag,
        "status": cmd_status,
        "stats": cmd_stats,
    }

    handler = dispatch.get(args.command)
    if not handler:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

    handler(args, client)


if __name__ == "__main__":
    main()
