#!/usr/bin/env python3
"""Slack Message Reader — Neatly prints thread replies or channel history.

Usage:
  # Read thread
  slack-thread.sh https://your-workspace.slack.com/archives/C0123456789/p1234567890123456
  slack-thread.sh C0123456789 1234567890.123456

  # Read channel history
  slack-thread.sh https://your-workspace.slack.com/archives/C0123456789
  slack-thread.sh C0123456789
  slack-thread.sh C0123456789 --limit 30

  # Channel history with thread replies
  slack-thread.sh C0123456789 --with-threads
  slack-thread.sh C0123456789 --with-threads --thread-limit 5
"""

import json, sys, re, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

CONFIG_FILE = Path.home() / ".openclaw" / "openclaw.json"


def load_token():
    with open(CONFIG_FILE) as f:
        return json.load(f)["channels"]["slack"]["botToken"]


def slack_api(method, params, token):
    url = f"https://slack.com/api/{method}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def parse_slack_link(link):
    """Parse Slack link → (channel, ts or None)
    Thread: https://...slack.com/archives/CHANNEL/pTIMESTAMP
    Channel: https://...slack.com/archives/CHANNEL
    """
    # Thread link
    m = re.search(r'/archives/([^/]+)/p(\d+)', link)
    if m:
        channel = m.group(1)
        raw_ts = m.group(2)
        ts = f"{raw_ts[:10]}.{raw_ts[10:]}"
        return channel, ts

    # Channel link (no ts)
    m = re.search(r'/archives/([^/?]+)', link)
    if m:
        return m.group(1), None

    return None, None


def resolve_users(user_ids, token):
    """Map user IDs to display names"""
    cache = {}
    for uid in set(user_ids):
        if uid in cache or not uid:
            continue
        data = slack_api("users.info", {"user": uid}, token)
        if data.get("ok"):
            u = data["user"]
            cache[uid] = u.get("real_name") or u.get("name", uid)
        else:
            cache[uid] = uid
    return cache


def fetch_thread(channel, ts, token, limit=200):
    """Fetch all thread messages with pagination"""
    all_messages = []
    cursor = None
    while True:
        params = {"channel": channel, "ts": ts, "limit": min(limit, 200)}
        if cursor:
            params["cursor"] = cursor
        data = slack_api("conversations.replies", params, token)
        if not data.get("ok"):
            print(f"API error: {data.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)
        all_messages.extend(data.get("messages", []))
        cursor = data.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            break
    return all_messages


def fetch_channel(channel, token, limit=50):
    """Fetch channel history with pagination"""
    all_messages = []
    cursor = None
    remaining = limit
    while remaining > 0:
        batch = min(remaining, 200)
        params = {"channel": channel, "limit": batch}
        if cursor:
            params["cursor"] = cursor
        data = slack_api("conversations.history", params, token)
        if not data.get("ok"):
            print(f"API error: {data.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)
        msgs = data.get("messages", [])
        all_messages.extend(msgs)
        remaining -= len(msgs)
        cursor = data.get("response_metadata", {}).get("next_cursor", "")
        if not cursor or not msgs:
            break
    return all_messages


def collect_user_ids(messages):
    """Collect all user IDs from messages (senders + reactors)"""
    ids = []
    for m in messages:
        if m.get("user"):
            ids.append(m["user"])
        for r in m.get("reactions", []):
            ids.extend(r.get("users", []))
    return ids


def replace_mentions(text, user_map):
    """Replace <@U1234> with @name"""
    for uid, name in user_map.items():
        text = text.replace(f"<@{uid}>", f"@{name}")
    return text


def format_ts(ts_val):
    """Convert timestamp to ISO 8601 (seconds)"""
    dt = datetime.fromtimestamp(float(ts_val))
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def format_reactions(msg, user_map):
    """Format emoji reactions as [:thumbsup: John,Jane]"""
    reactions = msg.get("reactions", [])
    if not reactions:
        return ""
    parts = []
    for r in reactions:
        names = [user_map.get(uid, uid) for uid in r.get("users", [])]
        parts.append(f":{r['name']}: {','.join(names)}")
    return " [" + " | ".join(parts) + "]"


def format_files(msg):
    """Format attachments/images as 📎 filename (type)"""
    files = msg.get("files", [])
    if not files:
        return ""
    parts = []
    for f in files:
        name = f.get("name", f.get("title", "unknown"))
        mimetype = f.get("mimetype", "")
        parts.append(f"📎 {name} ({mimetype})" if mimetype else f"📎 {name}")
    return " " + " ".join(parts)


def format_msg_line(msg, user_map, prefix=""):
    """Format a single message line"""
    user = user_map.get(msg.get("user", "?"), msg.get("user", "?"))
    text = replace_mentions(msg.get("text", "").replace("\n", " ↵ "), user_map)
    ts_str = format_ts(msg.get("ts", 0))
    reactions = format_reactions(msg, user_map)
    files = format_files(msg)
    return f"{prefix}[{ts_str}] {user}: {text}{files}{reactions}"


def format_thread(messages, user_map):
    """Format thread output"""
    lines = []
    for i, msg in enumerate(messages):
        if i == 0:
            reply_count = msg.get("reply_count", 0)
            user = user_map.get(msg.get("user", "?"), msg.get("user", "?"))
            text = replace_mentions(msg.get("text", "").replace("\n", " ↵ "), user_map)
            ts_str = format_ts(msg.get("ts", 0))
            reactions = format_reactions(msg, user_map)
            files = format_files(msg)
            lines.append(f"📌 [{ts_str}] {user}: {text[:200]}{files}{reactions}")
            lines.append(f"   ({reply_count} replies)")
            lines.append("---")
        else:
            lines.append(format_msg_line(msg, user_map))
    return "\n".join(lines)


def format_channel(messages, user_map, thread_replies=None):
    """Format channel history output (reversed from newest-first to chronological)
    thread_replies: dict of {thread_ts: [reply_messages]} (optional)
    """
    messages = list(reversed(messages))
    lines = []
    for msg in messages:
        reply_count = msg.get("reply_count", 0)
        reply_tag = f" 💬{reply_count}" if reply_count else ""
        line = format_msg_line(msg, user_map)
        lines.append(f"{line}{reply_tag}")

        # Inline thread replies (only on parent messages, avoid broadcast duplicates)
        thread_ts = msg.get("thread_ts")
        is_parent = thread_ts and thread_ts == msg.get("ts")
        if thread_replies and is_parent and thread_ts in thread_replies:
            replies = thread_replies[thread_ts]
            total = len(replies)
            for i, reply in enumerate(replies):
                prefix = "  └ " if i == total - 1 else "  ├ "
                lines.append(format_msg_line(reply, user_map, prefix))

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage:", file=sys.stderr)
        print("  Thread: slack-thread.sh <slack-thread-link>", file=sys.stderr)
        print("  Thread: slack-thread.sh <channel-id> <thread-ts>", file=sys.stderr)
        print("  Channel: slack-thread.sh <slack-channel-link>", file=sys.stderr)
        print("  Channel: slack-thread.sh <channel-id> [--limit N]", file=sys.stderr)
        sys.exit(1)

    # Parse flags
    limit = 50
    with_threads = False
    thread_limit = 0  # 0 = all

    args = list(sys.argv[1:])

    # --with-threads
    if "--with-threads" in args:
        with_threads = True
        args.remove("--with-threads")

    # --thread-limit N
    if "--thread-limit" in args:
        idx = args.index("--thread-limit")
        if idx + 1 < len(args):
            thread_limit = int(args[idx + 1])
            args = args[:idx] + args[idx + 2:]
        else:
            args = args[:idx]

    # --limit N
    if "--limit" in args:
        idx = args.index("--limit")
        if idx + 1 < len(args):
            limit = int(args[idx + 1])
            args = args[:idx] + args[idx + 2:]
        else:
            args = args[:idx]

    # Treat a standalone numeric 3rd argument as limit
    if len(args) >= 3 and args[2].isdigit():
        limit = int(args[2])
        args = args[:2]

    channel = None
    ts = None

    if args[0].startswith("http"):
        channel, ts = parse_slack_link(args[0])
        if not channel:
            print(f"Failed to parse link: {args[0]}", file=sys.stderr)
            sys.exit(1)
        # Limit may follow the link
        if len(args) >= 2 and args[1].isdigit():
            limit = int(args[1])
    else:
        channel = args[0]
        if len(args) >= 2 and not args[1].startswith("-"):
            ts = args[1]

    token = load_token()

    if ts:
        # Thread mode
        messages = fetch_thread(channel, ts, token, limit)
        if not messages:
            print("(No thread replies)")
            return
        user_ids = collect_user_ids(messages)
        user_map = resolve_users(user_ids, token)
        print(format_thread(messages, user_map))
    else:
        # Channel history mode
        messages = fetch_channel(channel, token, limit)
        if not messages:
            print("(No messages)")
            return

        # Fetch thread replies
        thread_replies = {}
        if with_threads:
            threaded = [m for m in messages if m.get("reply_count", 0) > 0]
            for m in threaded:
                t_ts = m["thread_ts"]
                replies = fetch_thread(channel, t_ts, token, limit=200)
                # Exclude the parent message, keep only replies
                replies = [r for r in replies if r.get("ts") != t_ts]
                if thread_limit > 0:
                    replies = replies[:thread_limit]
                if replies:
                    thread_replies[t_ts] = replies

        # Resolve users including those in thread replies
        all_msgs = list(messages)
        for replies in thread_replies.values():
            all_msgs.extend(replies)
        all_user_ids = collect_user_ids(all_msgs)
        user_map = resolve_users(all_user_ids, token)

        thread_info = f", {len(thread_replies)} threads included" if thread_replies else ""
        print(f"📢 Channel history ({len(messages)} messages, latest {limit}{thread_info})")
        print("---")
        print(format_channel(messages, user_map, thread_replies))


if __name__ == "__main__":
    main()
