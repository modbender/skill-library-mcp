#!/usr/bin/env python3
"""Minimal Kan.bn TODO client for single-user task management.

Environment variables:
- KANBN_TOKEN: Bearer token for Authorization header
- KANBN_API_KEY: API key for x-api-key header
- KANBN_BASE_URL: API base URL (default: https://kan.bn/api/v1)
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _parse_bool(value):
    v = str(value).strip().lower()
    if v in {"1", "true", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


class KanbnClient:
    def __init__(self, base_url, token=None, api_key=None, timeout=30):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.api_key = api_key
        self.timeout = timeout

    def request(self, method, path, params=None, body=None):
        query = ""
        if params:
            query = "?" + urllib.parse.urlencode(params, doseq=True)

        url = f"{self.base_url}{path}{query}"
        headers = {
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        else:
            data = None

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.api_key:
            headers["x-api-key"] = self.api_key

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                payload = res.read().decode("utf-8")
                if not payload:
                    return {"ok": True}
                try:
                    return json.loads(payload)
                except json.JSONDecodeError:
                    return {"raw": payload}
        except urllib.error.HTTPError as err:
            raw = err.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"message": raw}
            return {
                "error": True,
                "status": err.code,
                "statusText": err.reason,
                "details": parsed,
            }


def _build_parser():
    parser = argparse.ArgumentParser(description="Kan.bn TODO API helper")
    parser.add_argument(
        "--base-url",
        default=os.getenv("KANBN_BASE_URL", "https://kan.bn/api/v1"),
        help="Kan.bn API base URL",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("KANBN_TOKEN"),
        help="Bearer token (or set KANBN_TOKEN)",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("KANBN_API_KEY"),
        help="x-api-key value (or set KANBN_API_KEY)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print compact JSON",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("me", help="Get current user profile")
    sub.add_parser("workspaces", help="List workspaces")

    p_workspace_get = sub.add_parser("workspace-get", help="Get workspace by public ID")
    p_workspace_get.add_argument("--workspace-id", required=True)

    p_search = sub.add_parser("search", help="Search boards/cards in a workspace")
    p_search.add_argument("--workspace-id", required=True)
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=20)

    p_boards = sub.add_parser("boards", help="List boards in a workspace")
    p_boards.add_argument("--workspace-id", required=True)
    p_boards.add_argument("--type", choices=["regular", "template"])

    p_board_create = sub.add_parser("board-create", help="Create a board")
    p_board_create.add_argument("--workspace-id", required=True)
    p_board_create.add_argument("--name", required=True)
    p_board_create.add_argument(
        "--list",
        action="append",
        dest="lists",
        default=[],
        help="Initial list name, repeatable",
    )
    p_board_create.add_argument(
        "--label",
        action="append",
        dest="labels",
        default=[],
        help="Initial label name, repeatable",
    )
    p_board_create.add_argument("--type", choices=["regular", "template"])
    p_board_create.add_argument("--source-board-id")

    p_board_get = sub.add_parser("board-get", help="Get board by public ID")
    p_board_get.add_argument("--board-id", required=True)
    p_board_get.add_argument("--member-id", action="append", default=[])
    p_board_get.add_argument("--label-id", action="append", default=[])
    p_board_get.add_argument("--list-id", action="append", default=[])
    p_board_get.add_argument(
        "--due-filter",
        action="append",
        default=[],
        choices=["overdue", "today", "tomorrow", "next-week", "next-month", "no-due-date"],
    )
    p_board_get.add_argument("--type", choices=["regular", "template"])

    p_board_update = sub.add_parser("board-update", help="Update board metadata")
    p_board_update.add_argument("--board-id", required=True)
    p_board_update.add_argument("--name")
    p_board_update.add_argument("--slug")
    p_board_update.add_argument("--visibility", choices=["public", "private"])
    p_board_update.add_argument("--favorite", type=_parse_bool)

    p_list_create = sub.add_parser("list-create", help="Create list")
    p_list_create.add_argument("--board-id", required=True)
    p_list_create.add_argument("--name", required=True)

    p_list_update = sub.add_parser("list-update", help="Update list")
    p_list_update.add_argument("--list-id", required=True)
    p_list_update.add_argument("--name")
    p_list_update.add_argument("--index", type=int)

    p_list_delete = sub.add_parser("list-delete", help="Delete list")
    p_list_delete.add_argument("--list-id", required=True)

    p_todo_create = sub.add_parser("todo-create", help="Create TODO card")
    p_todo_create.add_argument("--list-id", required=True)
    p_todo_create.add_argument("--title", required=True)
    p_todo_create.add_argument("--description", default="")
    p_todo_create.add_argument("--due-date")
    p_todo_create.add_argument("--position", choices=["start", "end"], default="end")
    p_todo_create.add_argument("--label-id", action="append", default=[])
    p_todo_create.add_argument("--member-id", action="append", default=[])

    p_todo_get = sub.add_parser("todo-get", help="Get TODO card")
    p_todo_get.add_argument("--card-id", required=True)

    p_todo_update = sub.add_parser("todo-update", help="Update TODO card fields")
    p_todo_update.add_argument("--card-id", required=True)
    p_todo_update.add_argument("--title")
    p_todo_update.add_argument("--description")
    p_todo_update.add_argument("--due-date")
    p_todo_update.add_argument("--clear-due-date", action="store_true")
    p_todo_update.add_argument("--list-id")
    p_todo_update.add_argument("--index", type=int)

    p_todo_move = sub.add_parser("todo-move", help="Change TODO status by moving to another list")
    p_todo_move.add_argument("--card-id", required=True)
    p_todo_move.add_argument("--to-list-id", required=True)
    p_todo_move.add_argument("--index", type=int)

    p_todo_delete = sub.add_parser("todo-delete", help="Delete TODO card")
    p_todo_delete.add_argument("--card-id", required=True)

    p_comment_add = sub.add_parser("comment-add", help="Add comment to TODO")
    p_comment_add.add_argument("--card-id", required=True)
    p_comment_add.add_argument("--comment", required=True)

    p_comment_update = sub.add_parser("comment-update", help="Update comment")
    p_comment_update.add_argument("--card-id", required=True)
    p_comment_update.add_argument("--comment-id", required=True)
    p_comment_update.add_argument("--comment", required=True)

    p_comment_delete = sub.add_parser("comment-delete", help="Delete comment")
    p_comment_delete.add_argument("--card-id", required=True)
    p_comment_delete.add_argument("--comment-id", required=True)

    p_checklist_add = sub.add_parser("checklist-add", help="Add checklist to TODO")
    p_checklist_add.add_argument("--card-id", required=True)
    p_checklist_add.add_argument("--name", required=True)

    p_checkitem_add = sub.add_parser("checkitem-add", help="Add checklist item")
    p_checkitem_add.add_argument("--checklist-id", required=True)
    p_checkitem_add.add_argument("--title", required=True)

    p_checkitem_update = sub.add_parser("checkitem-update", help="Update checklist item")
    p_checkitem_update.add_argument("--item-id", required=True)
    p_checkitem_update.add_argument("--title")
    p_checkitem_update.add_argument("--completed", type=_parse_bool)
    p_checkitem_update.add_argument("--index", type=int)

    p_checkitem_delete = sub.add_parser("checkitem-delete", help="Delete checklist item")
    p_checkitem_delete.add_argument("--item-id", required=True)

    p_user_update = sub.add_parser("user-update", help="Update current user profile")
    p_user_update.add_argument("--name")
    p_user_update.add_argument("--image")

    return parser


def _must_have_updates(args, fields):
    if not any(getattr(args, f) is not None and getattr(args, f) != [] for f in fields):
        raise SystemExit("No fields to update. Provide at least one update argument.")


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if not args.token and not args.api_key:
        raise SystemExit("Missing auth: set --token/--api-key or env KANBN_TOKEN/KANBN_API_KEY")

    client = KanbnClient(
        base_url=args.base_url,
        token=args.token,
        api_key=args.api_key,
        timeout=args.timeout,
    )

    if args.cmd == "me":
        out = client.request("GET", "/users/me")
    elif args.cmd == "workspaces":
        out = client.request("GET", "/workspaces")
    elif args.cmd == "workspace-get":
        out = client.request("GET", f"/workspaces/{args.workspace_id}")
    elif args.cmd == "search":
        out = client.request(
            "GET",
            f"/workspaces/{args.workspace_id}/search",
            params={"query": args.query, "limit": args.limit},
        )
    elif args.cmd == "boards":
        params = {}
        if args.type:
            params["type"] = args.type
        out = client.request("GET", f"/workspaces/{args.workspace_id}/boards", params=params)
    elif args.cmd == "board-create":
        body = {
            "name": args.name,
            "lists": args.lists if args.lists else ["TODO", "DOING", "DONE"],
            "labels": args.labels,
        }
        if args.type:
            body["type"] = args.type
        if args.source_board_id:
            body["sourceBoardPublicId"] = args.source_board_id
        out = client.request("POST", f"/workspaces/{args.workspace_id}/boards", body=body)
    elif args.cmd == "board-get":
        params = {}
        if args.member_id:
            params["members"] = args.member_id
        if args.label_id:
            params["labels"] = args.label_id
        if args.list_id:
            params["lists"] = args.list_id
        if args.due_filter:
            params["dueDateFilters"] = args.due_filter
        if args.type:
            params["type"] = args.type
        out = client.request("GET", f"/boards/{args.board_id}", params=params)
    elif args.cmd == "board-update":
        _must_have_updates(args, ["name", "slug", "visibility", "favorite"])
        body = {}
        if args.name is not None:
            body["name"] = args.name
        if args.slug is not None:
            body["slug"] = args.slug
        if args.visibility is not None:
            body["visibility"] = args.visibility
        if args.favorite is not None:
            body["favorite"] = args.favorite
        out = client.request("PUT", f"/boards/{args.board_id}", body=body)
    elif args.cmd == "list-create":
        out = client.request(
            "POST",
            "/lists",
            body={"name": args.name, "boardPublicId": args.board_id},
        )
    elif args.cmd == "list-update":
        _must_have_updates(args, ["name", "index"])
        body = {}
        if args.name is not None:
            body["name"] = args.name
        if args.index is not None:
            body["index"] = args.index
        out = client.request("PUT", f"/lists/{args.list_id}", body=body)
    elif args.cmd == "list-delete":
        out = client.request("DELETE", f"/lists/{args.list_id}")
    elif args.cmd == "todo-create":
        body = {
            "title": args.title,
            "description": args.description,
            "listPublicId": args.list_id,
            "labelPublicIds": args.label_id,
            "memberPublicIds": args.member_id,
            "position": args.position,
        }
        if args.due_date:
            body["dueDate"] = args.due_date
        out = client.request("POST", "/cards", body=body)
    elif args.cmd == "todo-get":
        out = client.request("GET", f"/cards/{args.card_id}")
    elif args.cmd == "todo-update":
        _must_have_updates(args, ["title", "description", "due_date", "list_id", "index", "clear_due_date"])
        body = {}
        if args.title is not None:
            body["title"] = args.title
        if args.description is not None:
            body["description"] = args.description
        if args.list_id is not None:
            body["listPublicId"] = args.list_id
        if args.index is not None:
            body["index"] = args.index
        if args.clear_due_date:
            body["dueDate"] = None
        elif args.due_date is not None:
            body["dueDate"] = args.due_date
        out = client.request("PUT", f"/cards/{args.card_id}", body=body)
    elif args.cmd == "todo-move":
        body = {"listPublicId": args.to_list_id}
        if args.index is not None:
            body["index"] = args.index
        out = client.request("PUT", f"/cards/{args.card_id}", body=body)
    elif args.cmd == "todo-delete":
        out = client.request("DELETE", f"/cards/{args.card_id}")
    elif args.cmd == "comment-add":
        out = client.request(
            "POST",
            f"/cards/{args.card_id}/comments",
            body={"comment": args.comment},
        )
    elif args.cmd == "comment-update":
        out = client.request(
            "PUT",
            f"/cards/{args.card_id}/comments/{args.comment_id}",
            body={"comment": args.comment},
        )
    elif args.cmd == "comment-delete":
        out = client.request("DELETE", f"/cards/{args.card_id}/comments/{args.comment_id}")
    elif args.cmd == "checklist-add":
        out = client.request(
            "POST",
            f"/cards/{args.card_id}/checklists",
            body={"name": args.name},
        )
    elif args.cmd == "checkitem-add":
        out = client.request(
            "POST",
            f"/checklists/{args.checklist_id}/items",
            body={"title": args.title},
        )
    elif args.cmd == "checkitem-update":
        _must_have_updates(args, ["title", "completed", "index"])
        body = {}
        if args.title is not None:
            body["title"] = args.title
        if args.completed is not None:
            body["completed"] = args.completed
        if args.index is not None:
            body["index"] = args.index
        out = client.request("PATCH", f"/checklists/items/{args.item_id}", body=body)
    elif args.cmd == "checkitem-delete":
        out = client.request("DELETE", f"/checklists/items/{args.item_id}")
    elif args.cmd == "user-update":
        _must_have_updates(args, ["name", "image"])
        body = {}
        if args.name is not None:
            body["name"] = args.name
        if args.image is not None:
            body["image"] = args.image
        out = client.request("PUT", "/users", body=body)
    else:
        raise SystemExit(f"Unsupported command: {args.cmd}")

    if args.raw:
        print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))

    if isinstance(out, dict) and out.get("error"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
