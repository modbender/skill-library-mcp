#!/usr/bin/env python3
"""Manage Slack channel bookmarks (add, list, edit, remove).

Note: Slack API only supports link bookmarks. Folders are UI-only and cannot be
created via the API.

Usage:
    python3 slack_bookmark.py add --channel C123ABC --title "Design Docs" --link "https://example.com"
    python3 slack_bookmark.py list --channel C123ABC
    python3 slack_bookmark.py edit --channel C123ABC --bookmark-id Bk123 --title "New Title"
    python3 slack_bookmark.py remove --channel C123ABC --bookmark-id Bk123
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")


def get_bot_token():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    token = config.get("channels", {}).get("slack", {}).get("botToken")
    if not token:
        print("Error: No botToken found in", CONFIG_PATH, file=sys.stderr)
        sys.exit(1)
    return token


def slack_api(token, method, params):
    """POST to Slack API with application/x-www-form-urlencoded."""
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {token}"}
    body = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} from {method}: {error_body}", file=sys.stderr)
        sys.exit(1)


def cmd_add(args):
    token = get_bot_token()
    if not args.link:
        print("Error: --link is required (Slack API only supports link bookmarks, not folders)", file=sys.stderr)
        sys.exit(1)
    params = {
        "channel_id": args.channel,
        "title": args.title,
        "type": "link",
        "link": args.link,
    }
    if args.emoji:
        params["emoji"] = args.emoji

    resp = slack_api(token, "bookmarks.add", params)
    if not resp.get("ok"):
        print(f"Error: bookmarks.add failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    bookmark = resp.get("bookmark", {})
    print(json.dumps({
        "ok": True,
        "bookmark_id": bookmark.get("id"),
        "title": bookmark.get("title"),
        "type": bookmark.get("type"),
        "link": bookmark.get("link"),
        "channel": args.channel,
    }, indent=2))


def cmd_list(args):
    token = get_bot_token()
    resp = slack_api(token, "bookmarks.list", {"channel_id": args.channel})
    if not resp.get("ok"):
        print(f"Error: bookmarks.list failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    bookmarks = resp.get("bookmarks", [])
    result = []
    for b in bookmarks:
        entry = {
            "id": b.get("id"),
            "title": b.get("title"),
            "type": b.get("type"),
            "link": b.get("link", ""),
        }
        if b.get("emoji"):
            entry["emoji"] = b["emoji"]
        result.append(entry)
    print(json.dumps({"ok": True, "bookmarks": result}, indent=2))


def cmd_edit(args):
    token = get_bot_token()
    params = {
        "channel_id": args.channel,
        "bookmark_id": args.bookmark_id,
    }
    if args.title:
        params["title"] = args.title
    if args.link:
        params["link"] = args.link
    if args.emoji:
        params["emoji"] = args.emoji

    resp = slack_api(token, "bookmarks.edit", params)
    if not resp.get("ok"):
        print(f"Error: bookmarks.edit failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    bookmark = resp.get("bookmark", {})
    print(json.dumps({
        "ok": True,
        "bookmark_id": bookmark.get("id"),
        "title": bookmark.get("title"),
    }, indent=2))


def cmd_remove(args):
    token = get_bot_token()
    resp = slack_api(token, "bookmarks.remove", {
        "channel_id": args.channel,
        "bookmark_id": args.bookmark_id,
    })
    if not resp.get("ok"):
        print(f"Error: bookmarks.remove failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"ok": True, "removed": args.bookmark_id}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Manage Slack channel bookmarks")
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a link bookmark")
    p_add.add_argument("--channel", required=True, help="Channel ID")
    p_add.add_argument("--title", required=True, help="Bookmark title")
    p_add.add_argument("--link", required=True, help="URL for the bookmark")
    p_add.add_argument("--emoji", help="Emoji icon (e.g. :link:)")

    # list
    p_list = sub.add_parser("list", help="List bookmarks in a channel")
    p_list.add_argument("--channel", required=True, help="Channel ID")

    # edit
    p_edit = sub.add_parser("edit", help="Edit a bookmark")
    p_edit.add_argument("--channel", required=True, help="Channel ID")
    p_edit.add_argument("--bookmark-id", required=True, help="Bookmark ID to edit")
    p_edit.add_argument("--title", help="New title")
    p_edit.add_argument("--link", help="New URL")
    p_edit.add_argument("--emoji", help="New emoji")

    # remove
    p_remove = sub.add_parser("remove", help="Remove a bookmark")
    p_remove.add_argument("--channel", required=True, help="Channel ID")
    p_remove.add_argument("--bookmark-id", required=True, help="Bookmark ID to remove")

    args = parser.parse_args()
    {"add": cmd_add, "list": cmd_list, "edit": cmd_edit, "remove": cmd_remove}[args.command](args)


if __name__ == "__main__":
    main()
