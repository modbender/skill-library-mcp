#!/usr/bin/env python3
"""Remember The Milk CLI — manage tasks via the RTM REST API.

Requires env vars RTM_API_KEY and RTM_SHARED_SECRET.
Auth token persists at ~/.rtm_token after first `auth` run.
All network calls use a 15-second timeout. Stdlib only (no pip deps).
"""

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REST_URL = "https://api.rememberthemilk.com/services/rest/"
AUTH_URL = "https://www.rememberthemilk.com/services/auth/"
TOKEN_PATH = Path.home() / ".rtm_token"
TIMEOUT = 15
MAX_RETRIES = 2
RETRY_DELAY = 2


def get_config():
    api_key = os.environ.get("RTM_API_KEY")
    shared_secret = os.environ.get("RTM_SHARED_SECRET")
    if not api_key or not shared_secret:
        print("Error: RTM_API_KEY and RTM_SHARED_SECRET env vars required.", file=sys.stderr)
        sys.exit(1)
    return api_key, shared_secret


def sign(params, shared_secret):
    sorted_params = sorted(params.items())
    raw = shared_secret + "".join(k + v for k, v in sorted_params)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def api_call(method, shared_secret, api_key, token=None, use_post=False, **kwargs):
    """Make an RTM API call with automatic retry on timeout/transient errors."""
    params = {"method": method, "api_key": api_key, "format": "json"}
    if token:
        params["auth_token"] = token
    params.update(kwargs)
    params["api_sig"] = sign(params, shared_secret)

    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            if use_post:
                body = urllib.parse.urlencode(params).encode("utf-8")
                req = urllib.request.Request(REST_URL, data=body, method="POST")
                req.add_header("Content-Type", "application/x-www-form-urlencoded")
                with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                    data = json.loads(resp.read().decode())
            else:
                url = REST_URL + "?" + urllib.parse.urlencode(params)
                with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
                    data = json.loads(resp.read().decode())

            rsp = data.get("rsp", data)
            if rsp.get("stat") != "ok":
                err = rsp.get("err", {})
                print(f"API error: {err.get('msg', rsp)}", file=sys.stderr)
                sys.exit(1)
            return rsp

        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            print(f"Network error after {MAX_RETRIES + 1} attempts: {e}", file=sys.stderr)
            sys.exit(1)


def load_token():
    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text().strip()
    print("Not authenticated. Run: rtm.py auth", file=sys.stderr)
    sys.exit(1)


def get_timeline(shared_secret, api_key, token):
    rsp = api_call("rtm.timelines.create", shared_secret, api_key, token)
    return rsp["timeline"]


def _normalize_list(obj):
    """Ensure obj is a list (RTM returns dict for single items)."""
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        return obj
    return []


def _print_task(tl, ts, t, show_notes=True):
    """Print a single task with optional notes."""
    due = t.get("due", "")
    due_str = f" (due: {due})" if due else ""
    priority = t.get("priority", "N")
    pri_str = f" [P{priority}]" if priority != "N" else ""
    completed = t.get("completed", "")
    status = " ✓" if completed else ""
    tags = ts.get("tags", {})
    tag_list = tags.get("tag", []) if isinstance(tags, dict) else []
    if isinstance(tag_list, str):
        tag_list = [tag_list]
    tag_str = f" #{' #'.join(tag_list)}" if tag_list else ""
    print(f"  {ts['name']}{pri_str}{due_str}{tag_str}{status}")
    print(f"    list={tl['id']} series={ts['id']} task={t['id']}")
    if show_notes:
        notes_obj = ts.get("notes", {})
        if isinstance(notes_obj, list):
            notes_obj = notes_obj[0] if notes_obj else {}
        notes = _normalize_list(notes_obj.get("note", []) if isinstance(notes_obj, dict) else [])
        for n in notes:
            body = n.get("$t", "")
            note_title = n.get("title", "")
            note_id = n.get("id", "")
            id_str = f" (note_id={note_id})" if note_id else ""
            if note_title:
                print(f"    📝 {note_title}{id_str}")
                if body:
                    print(f"    {body}")
            elif body:
                print(f"    📝 {body}{id_str}")


def _iter_tasks(rsp):
    """Yield (task_list, taskseries, task) tuples from an RTM tasks response."""
    tasks = rsp.get("tasks", {})
    task_lists = _normalize_list(tasks.get("list", []))
    for tl in task_lists:
        series = _normalize_list(tl.get("taskseries", []))
        for ts in series:
            task_entries = _normalize_list(ts.get("task", []))
            for t in task_entries:
                yield tl, ts, t


# --- Commands ---

def cmd_auth(args):
    api_key, shared_secret = get_config()
    rsp = api_call("rtm.auth.getFrob", shared_secret, api_key)
    frob = rsp["frob"]
    auth_params = {"api_key": api_key, "perms": "delete", "frob": frob}
    auth_params["api_sig"] = sign(auth_params, shared_secret)
    url = AUTH_URL + "?" + urllib.parse.urlencode(auth_params)
    print(f"Open this URL and authorize the app:\n\n  {url}\n")
    input("Press Enter after authorizing...")
    rsp = api_call("rtm.auth.getToken", shared_secret, api_key, frob=frob)
    token = rsp["auth"]["token"]
    username = rsp["auth"]["user"]["username"]
    TOKEN_PATH.write_text(token)
    print(f"Authenticated as {username}! Token saved to {TOKEN_PATH}")


def cmd_lists(args):
    api_key, shared_secret = get_config()
    token = load_token()
    rsp = api_call("rtm.lists.getList", shared_secret, api_key, token)
    for lst in rsp["lists"]["list"]:
        if lst.get("archived", "0") == "1" and not args.all:
            continue
        archived = " [archived]" if lst.get("archived", "0") == "1" else ""
        print(f"  {lst['id']:>10}  {lst['name']}{archived}")


def cmd_tasks(args):
    api_key, shared_secret = get_config()
    token = load_token()
    kwargs = {}
    if args.list:
        kwargs["list_id"] = args.list
    if args.filter:
        kwargs["filter"] = args.filter
    else:
        kwargs["filter"] = "status:incomplete"
    rsp = api_call("rtm.tasks.getList", shared_secret, api_key, token, **kwargs)
    count = 0
    for tl, ts, t in _iter_tasks(rsp):
        _print_task(tl, ts, t, show_notes=not args.no_notes)
        count += 1
    if count == 0:
        print("  No tasks found.")
    elif not args.no_notes:
        print(f"\n  {count} task(s)")


def cmd_add(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    kwargs = {"timeline": timeline, "name": args.name}
    if args.list:
        kwargs["list_id"] = args.list
    if args.parse:
        kwargs["parse"] = "1"
    rsp = api_call("rtm.tasks.add", shared_secret, api_key, token, **kwargs)
    ts = rsp["list"]["taskseries"]
    if isinstance(ts, list):
        ts = ts[0]
    task = ts["task"]
    if isinstance(task, list):
        task = task[0]
    print(f"Added: {ts['name']} (list={rsp['list']['id']} series={ts['id']} task={task['id']})")


def cmd_complete(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    api_call("rtm.tasks.complete", shared_secret, api_key, token,
             timeline=timeline, list_id=args.list_id,
             taskseries_id=args.taskseries_id, task_id=args.task_id)
    print("Task completed.")


def cmd_delete(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    api_call("rtm.tasks.delete", shared_secret, api_key, token,
             timeline=timeline, list_id=args.list_id,
             taskseries_id=args.taskseries_id, task_id=args.task_id)
    print("Task deleted.")


def cmd_set_priority(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    api_call("rtm.tasks.setPriority", shared_secret, api_key, token,
             timeline=timeline, list_id=args.list_id,
             taskseries_id=args.taskseries_id, task_id=args.task_id,
             priority=args.priority)
    print(f"Priority set to {args.priority}.")


def cmd_set_due(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    kwargs = {"timeline": timeline, "list_id": args.list_id,
              "taskseries_id": args.taskseries_id, "task_id": args.task_id,
              "due": args.due, "parse": "1"}
    if args.has_due_time:
        kwargs["has_due_time"] = "1"
    api_call("rtm.tasks.setDueDate", shared_secret, api_key, token, **kwargs)
    print(f"Due date set to: {args.due}")


def cmd_move(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    api_call("rtm.tasks.moveTo", shared_secret, api_key, token,
             timeline=timeline, from_list_id=args.from_list,
             to_list_id=args.to_list,
             taskseries_id=args.taskseries_id, task_id=args.task_id)
    print(f"Task moved from list {args.from_list} to {args.to_list}.")


def cmd_add_tags(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    api_call("rtm.tasks.addTags", shared_secret, api_key, token,
             timeline=timeline, list_id=args.list_id,
             taskseries_id=args.taskseries_id, task_id=args.task_id,
             tags=args.tags)
    print(f"Tags added: {args.tags}")


def cmd_notes_add(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    rsp = api_call("rtm.tasks.notes.add", shared_secret, api_key, token,
                   use_post=True, timeline=timeline, list_id=args.list_id,
                   taskseries_id=args.taskseries_id, task_id=args.task_id,
                   note_title=args.title, note_text=args.text)
    note = rsp.get("note", {})
    print(f"Note added (id={note.get('id', '?')})")


def cmd_notes_delete(args):
    api_key, shared_secret = get_config()
    token = load_token()
    timeline = get_timeline(shared_secret, api_key, token)
    api_call("rtm.tasks.notes.delete", shared_secret, api_key, token,
             timeline=timeline, note_id=args.note_id)
    print("Note deleted.")


def cmd_search(args):
    api_key, shared_secret = get_config()
    token = load_token()
    rsp = api_call("rtm.tasks.getList", shared_secret, api_key, token, filter=args.query)
    count = 0
    for tl, ts, t in _iter_tasks(rsp):
        _print_task(tl, ts, t, show_notes=True)
        count += 1
    if count == 0:
        print("  No tasks found.")
    else:
        print(f"\n  {count} task(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Remember The Milk CLI — manage tasks, lists, and notes via the RTM API.",
        epilog="Env vars: RTM_API_KEY, RTM_SHARED_SECRET (required). Auth token: ~/.rtm_token")
    sub = parser.add_subparsers(dest="command", required=True)

    # Auth
    sub.add_parser("auth", help="Authenticate with RTM (interactive, opens browser URL)")

    # Lists
    p_lists = sub.add_parser("lists", help="Show all lists")
    p_lists.add_argument("--all", action="store_true", help="Include archived lists")

    # Tasks
    p_tasks = sub.add_parser("tasks", help="Show tasks (default: incomplete)")
    p_tasks.add_argument("--list", help="Filter by list ID")
    p_tasks.add_argument("--filter", help="RTM filter query (overrides default incomplete filter)")
    p_tasks.add_argument("--no-notes", action="store_true", help="Hide notes in output")

    # Add
    p_add = sub.add_parser("add", help="Add a task")
    p_add.add_argument("name", help="Task name (use --parse for Smart Add syntax)")
    p_add.add_argument("--list", help="List ID (default: Inbox)")
    p_add.add_argument("--parse", action="store_true",
                       help="Enable Smart Add (e.g. 'Buy milk ^tomorrow #shopping !1')")

    # Complete
    p_complete = sub.add_parser("complete", help="Mark a task complete")
    p_complete.add_argument("list_id")
    p_complete.add_argument("taskseries_id")
    p_complete.add_argument("task_id")

    # Delete
    p_delete = sub.add_parser("delete", help="Delete a task permanently")
    p_delete.add_argument("list_id")
    p_delete.add_argument("taskseries_id")
    p_delete.add_argument("task_id")

    # Set priority
    p_pri = sub.add_parser("set-priority", help="Set task priority (1=high, 2=medium, 3=low, N=none)")
    p_pri.add_argument("list_id")
    p_pri.add_argument("taskseries_id")
    p_pri.add_argument("task_id")
    p_pri.add_argument("priority", choices=["1", "2", "3", "N"])

    # Set due date
    p_due = sub.add_parser("set-due", help="Set task due date (natural language supported)")
    p_due.add_argument("list_id")
    p_due.add_argument("taskseries_id")
    p_due.add_argument("task_id")
    p_due.add_argument("due", help="Due date (e.g. 'tomorrow', '2025-03-15', 'next friday')")
    p_due.add_argument("--has-due-time", action="store_true", help="Include time in due date")

    # Move
    p_move = sub.add_parser("move", help="Move a task between lists")
    p_move.add_argument("from_list", help="Source list ID")
    p_move.add_argument("to_list", help="Destination list ID")
    p_move.add_argument("taskseries_id")
    p_move.add_argument("task_id")

    # Add tags
    p_tags = sub.add_parser("add-tags", help="Add tags to a task")
    p_tags.add_argument("list_id")
    p_tags.add_argument("taskseries_id")
    p_tags.add_argument("task_id")
    p_tags.add_argument("tags", help="Comma-separated tags")

    # Search
    p_search = sub.add_parser("search", help="Search tasks using RTM filter syntax")
    p_search.add_argument("query", help="RTM filter (e.g. 'tag:work AND priority:1')")

    # Notes
    p_notes_add = sub.add_parser("notes-add", help="Add a note to a task")
    p_notes_add.add_argument("list_id")
    p_notes_add.add_argument("taskseries_id")
    p_notes_add.add_argument("task_id")
    p_notes_add.add_argument("text", help="Note body text")
    p_notes_add.add_argument("--title", default="", help="Note title")

    p_notes_del = sub.add_parser("notes-delete", help="Delete a note by ID")
    p_notes_del.add_argument("note_id")

    args = parser.parse_args()
    cmds = {
        "auth": cmd_auth, "lists": cmd_lists, "tasks": cmd_tasks,
        "add": cmd_add, "complete": cmd_complete, "delete": cmd_delete,
        "set-priority": cmd_set_priority, "set-due": cmd_set_due,
        "move": cmd_move, "add-tags": cmd_add_tags,
        "search": cmd_search,
        "notes-add": cmd_notes_add, "notes-delete": cmd_notes_delete,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
