#!/usr/bin/env python3
"""
Monday.com API — calls api.monday.com directly via GraphQL.
No third-party proxy.
"""
import argparse
import json
import os
import sys
import urllib.request

BASE_URL = "https://api.monday.com/v2"
API_VERSION = "2024-04"


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_token():
    token = os.environ.get("MONDAY_API_TOKEN")
    if not token:
        print("Error: MONDAY_API_TOKEN not set.", file=sys.stderr)
        print("Get your token at: Profile picture → Developers → API token", file=sys.stderr)
        sys.exit(1)
    return token


def gql(query, variables=None):
    token = get_token()
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("Authorization", token)
    req.add_header("Content-Type", "application/json")
    req.add_header("API-Version", API_VERSION)

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if "errors" in result:
                print(f"GraphQL errors: {result['errors']}", file=sys.stderr)
                sys.exit(1)
            return result.get("data", {})
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_me(args):
    data = gql("query { me { id name email account { name plan { max_users } } } }")
    me = data.get("me", {})
    print(f"Name:    {me.get('name')}")
    print(f"Email:   {me.get('email')}")
    account = me.get("account", {})
    print(f"Account: {account.get('name')}")


def cmd_list_boards(args):
    query = """
    query ($limit: Int!, $page: Int!) {
      boards(limit: $limit, page: $page, order_by: created_at) {
        id name description board_kind state items_count
      }
    }
    """
    data = gql(query, {"limit": args.limit, "page": args.page})
    boards = data.get("boards", [])
    print(f"# {len(boards)} boards\n")
    for b in boards:
        print(f"{b['id']}\t{b['name']}\t{b.get('items_count', 0)} items\t{b.get('board_kind')}")


def cmd_get_board(args):
    query = """
    query ($id: ID!) {
      boards(ids: [$id]) {
        id name description state items_count
        columns { id title type }
        groups { id title }
      }
    }
    """
    data = gql(query, {"id": args.board_id})
    boards = data.get("boards", [])
    if not boards:
        print("Board not found.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(boards[0], indent=2))


def cmd_list_items(args):
    query = """
    query ($board_id: ID!, $limit: Int!) {
      boards(ids: [$board_id]) {
        items_page(limit: $limit) {
          items {
            id name state
            column_values { id text }
          }
        }
      }
    }
    """
    data = gql(query, {"board_id": args.board_id, "limit": args.limit})
    boards = data.get("boards", [])
    if not boards:
        print("Board not found.", file=sys.stderr)
        sys.exit(1)
    items = boards[0].get("items_page", {}).get("items", [])
    print(f"# {len(items)} items\n")
    for item in items:
        col_values = {cv["id"]: cv["text"] for cv in item.get("column_values", []) if cv.get("text")}
        print(f"{item['id']}\t{item['name']}")
        for k, v in col_values.items():
            print(f"  {k}: {v}")
        print()


def cmd_list_workspaces(args):
    query = "query { workspaces { id name kind description } }"
    data = gql(query)
    workspaces = data.get("workspaces", [])
    print(f"# {len(workspaces)} workspaces\n")
    for w in workspaces:
        print(f"{w['id']}\t{w['name']}\t{w.get('kind')}")


def cmd_list_users(args):
    query = """
    query ($limit: Int!) {
      users(limit: $limit) {
        id name email enabled
      }
    }
    """
    data = gql(query, {"limit": args.limit})
    users = data.get("users", [])
    print(f"# {len(users)} users\n")
    for u in users:
        status = "active" if u.get("enabled") else "disabled"
        print(f"{u['id']}\t{u['name']}\t{u.get('email')}\t{status}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Monday.com CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("me", help="Get your account info")

    p = sub.add_parser("list-boards", help="List all boards")
    p.add_argument("--limit", type=int, default=25)
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("get-board", help="Get board details, columns, and groups")
    p.add_argument("board_id", help="Board ID")

    p = sub.add_parser("list-items", help="List items on a board")
    p.add_argument("board_id", help="Board ID")
    p.add_argument("--limit", type=int, default=25)

    sub.add_parser("list-workspaces", help="List workspaces")

    p = sub.add_parser("list-users", help="List account users")
    p.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()
    {
        "me": cmd_me,
        "list-boards": cmd_list_boards,
        "get-board": cmd_get_board,
        "list-items": cmd_list_items,
        "list-workspaces": cmd_list_workspaces,
        "list-users": cmd_list_users,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
