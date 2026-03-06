#!/usr/bin/env python3
"""Create, edit, delete, and manage Slack canvases.

Usage:
    python3 slack_canvas.py create --title "Sprint Notes" --markdown "## Goals\\n- Ship feature X"
    python3 slack_canvas.py edit --canvas-id F123 --operation insert_at_end --markdown "New content"
    python3 slack_canvas.py edit --canvas-id F123 --section-id S123 --operation replace --markdown "Updated"
    python3 slack_canvas.py delete --canvas-id F123
    python3 slack_canvas.py sections --canvas-id F123
    python3 slack_canvas.py access --canvas-id F123 --channel C123 --level edit
"""

import argparse
import json
import os
import sys
import urllib.request
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


def slack_api(token, method, data):
    url = f"https://slack.com/api/{method}"
    body = json.dumps(data).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error: HTTP {e.code} from {method}: {error_body}", file=sys.stderr)
        sys.exit(1)


def doc_content(markdown_text):
    """Build a document_content object from markdown text."""
    return {"type": "markdown", "markdown": markdown_text}


def cmd_create(args, token):
    data = {"title": args.title, "document_content": doc_content(args.markdown)}
    resp = slack_api(token, "canvases.create", data)
    if not resp.get("ok"):
        print(f"Error: canvases.create failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "canvas_id": resp.get("canvas_id", "")}, indent=2))


def cmd_edit(args, token):
    change = {
        "operation": args.operation,
        "document_content": doc_content(args.markdown),
    }
    if args.section_id:
        change["section_id"] = args.section_id

    data = {"canvas_id": args.canvas_id, "changes": [change]}
    resp = slack_api(token, "canvases.edit", data)
    if not resp.get("ok"):
        print(f"Error: canvases.edit failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "canvas_id": args.canvas_id, "operation": args.operation}, indent=2))


def cmd_delete(args, token):
    resp = slack_api(token, "canvases.delete", {"canvas_id": args.canvas_id})
    if not resp.get("ok"):
        print(f"Error: canvases.delete failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "deleted": args.canvas_id}, indent=2))


def cmd_sections(args, token):
    criteria = {}
    if args.contains:
        criteria["contains_text"] = args.contains
    if args.section_types:
        criteria["section_types"] = args.section_types.split(",")
    if not criteria:
        # Default: search for any_header to get all sections
        criteria["section_types"] = ["any_header"]

    data = {"canvas_id": args.canvas_id, "criteria": criteria}
    resp = slack_api(token, "canvases.sections.lookup", data)
    if not resp.get("ok"):
        print(f"Error: canvases.sections.lookup failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(resp, indent=2))


def cmd_access(args, token):
    data = {
        "canvas_id": args.canvas_id,
        "access_level": args.level,
    }
    if args.channel:
        data["channel_ids"] = [args.channel]
    if args.user:
        data["user_ids"] = [args.user]

    resp = slack_api(token, "canvases.access.set", data)
    if not resp.get("ok"):
        print(f"Error: canvases.access.set failed: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"ok": True, "canvas_id": args.canvas_id, "access_level": args.level}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Manage Slack canvases")
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="Create a new canvas")
    p_create.add_argument("--title", required=True, help="Canvas title")
    p_create.add_argument("--markdown", required=True, help="Markdown content")

    # edit
    p_edit = sub.add_parser("edit", help="Edit an existing canvas")
    p_edit.add_argument("--canvas-id", required=True, help="Canvas ID (e.g. F07ABCD1234)")
    p_edit.add_argument("--operation", required=True,
                        choices=["insert_at_start", "insert_at_end", "insert_after", "replace", "delete"],
                        help="Edit operation")
    p_edit.add_argument("--markdown", required=True, help="Markdown content for the operation")
    p_edit.add_argument("--section-id", help="Section ID (required for replace, delete, insert_after)")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a canvas")
    p_delete.add_argument("--canvas-id", required=True, help="Canvas ID")

    # sections
    p_sections = sub.add_parser("sections", help="Look up canvas sections")
    p_sections.add_argument("--canvas-id", required=True, help="Canvas ID")
    p_sections.add_argument("--contains", help="Search for sections containing this text")
    p_sections.add_argument("--section-types", help="Comma-separated types: any_header,h1,h2,h3")

    # access
    p_access = sub.add_parser("access", help="Set canvas access permissions")
    p_access.add_argument("--canvas-id", required=True, help="Canvas ID")
    p_access.add_argument("--level", required=True, choices=["read", "write"], help="Access level")
    p_access.add_argument("--channel", help="Channel ID to grant access")
    p_access.add_argument("--user", help="User ID to grant access")

    args = parser.parse_args()
    token = get_bot_token()

    commands = {
        "create": cmd_create,
        "edit": cmd_edit,
        "delete": cmd_delete,
        "sections": cmd_sections,
        "access": cmd_access,
    }
    commands[args.command](args, token)


if __name__ == "__main__":
    main()
