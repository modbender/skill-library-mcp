#!/usr/bin/env python3
"""AI-powered ClickUp task management for OpenClaw agents."""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE_URL = "https://api.clickup.com/api/v2"


def get_api_key():
    key = os.environ.get("CLICKUP_API_KEY")
    if not key:
        print("Error: CLICKUP_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(endpoint, method="GET", data=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    if params:
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers={
        "Authorization": get_api_key(),
        "Content-Type": "application/json",
    }, method=method)
    try:
        with urlopen(req) as resp:
            text = resp.read().decode()
            return json.loads(text) if text.strip() else {}
    except HTTPError as e:
        err = e.read().decode() if e.fp else ""
        print(f"API Error {e.code}: {err}", file=sys.stderr)
        sys.exit(1)


def llm_request(prompt, system="You are a project management expert."):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("Error: OPENROUTER_API_KEY required for AI features", file=sys.stderr)
        sys.exit(1)
    data = json.dumps({
        "model": "anthropic/claude-haiku-4.5",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "max_tokens": 2000,
    }).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=data, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    })
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())["choices"][0]["message"]["content"]
    except HTTPError as e:
        print(f"LLM Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def cmd_workspaces(args):
    data = api_request("/team")
    for t in data.get("teams", []):
        print(f"  {t['name']} | ID: {t['id']} | Members: {len(t.get('members', []))}")


def cmd_spaces(args):
    data = api_request(f"/team/{args.team_id}/space")
    for s in data.get("spaces", []):
        print(f"  {s['name']} | ID: {s['id']} | Private: {s.get('private', False)}")


def cmd_folders(args):
    data = api_request(f"/space/{args.space_id}/folder")
    for f in data.get("folders", []):
        lists = len(f.get("lists", []))
        print(f"  {f['name']} | ID: {f['id']} | Lists: {lists}")


def cmd_lists(args):
    data = api_request(f"/folder/{args.folder_id}/list")
    for l in data.get("lists", []):
        print(f"  {l['name']} | ID: {l['id']} | Tasks: {l.get('task_count', '?')}")


def cmd_folderless_lists(args):
    data = api_request(f"/space/{args.space_id}/list")
    for l in data.get("lists", []):
        print(f"  {l['name']} | ID: {l['id']} | Tasks: {l.get('task_count', '?')}")


def cmd_tasks(args):
    params = {"subtasks": "true"} if args.subtasks else {}
    if args.status:
        params["statuses[]"] = args.status
    if args.assignee:
        params["assignees[]"] = args.assignee
    data = api_request(f"/list/{args.list_id}/task", params=params)
    tasks = data.get("tasks", [])
    if not tasks:
        print("  No tasks found.")
        return
    for t in tasks:
        priority = t.get("priority", {})
        p_name = priority.get("priority", "none") if priority else "none"
        assignees = ", ".join(a.get("username", "?") for a in t.get("assignees", []))
        due = t.get("due_date")
        due_str = ""
        if due:
            from datetime import datetime
            due_str = f" | Due: {datetime.fromtimestamp(int(due)/1000).strftime('%Y-%m-%d')}"
        print(f"  [{t.get('status',{}).get('status','?')}] {t['name']} | ID: {t['id']} | P: {p_name}{due_str} | {assignees}")


def cmd_get_task(args):
    data = api_request(f"/task/{args.task_id}")
    print(json.dumps(data, indent=2))


def cmd_create_task(args):
    body = {"name": args.name}
    if args.description:
        body["description"] = args.description
    if args.priority:
        body["priority"] = args.priority
    if args.due:
        from datetime import datetime
        body["due_date"] = int(datetime.strptime(args.due, "%Y-%m-%d").timestamp() * 1000)
    if args.assignee:
        body["assignees"] = [args.assignee]
    result = api_request(f"/list/{args.list_id}/task", method="POST", data=body)
    print(f"  Task created: {result.get('name','?')} | ID: {result.get('id','?')}")


def cmd_update_task(args):
    body = {}
    if args.name:
        body["name"] = args.name
    if args.status:
        body["status"] = args.status
    if args.priority:
        body["priority"] = args.priority
    if args.due:
        from datetime import datetime
        body["due_date"] = int(datetime.strptime(args.due, "%Y-%m-%d").timestamp() * 1000)
    if args.assignee:
        body["assignees"] = {"add": [args.assignee]}
    result = api_request(f"/task/{args.task_id}", method="PUT", data=body)
    print(f"  Task updated: {result.get('name','?')}")


def cmd_delete_task(args):
    api_request(f"/task/{args.task_id}", method="DELETE")
    print(f"  Task {args.task_id} deleted.")


def cmd_comment(args):
    result = api_request(f"/task/{args.task_id}/comment", method="POST", data={"comment_text": args.text})
    print(f"  Comment added: {result.get('id', 'OK')}")


def cmd_start_timer(args):
    result = api_request(f"/task/{args.task_id}/time", method="POST", data={"start": True})
    print(f"  Timer started on {args.task_id}")


def cmd_stop_timer(args):
    result = api_request(f"/team/{args.team_id}/time_entries/running", method="GET")
    running = result.get("data", [])
    if not running:
        print("  No running timers.")
        return
    for entry in running:
        api_request(f"/team/{args.team_id}/time_entries/stop", method="POST")
        print(f"  Timer stopped: {entry.get('task',{}).get('name','?')} ({entry.get('duration','?')}ms)")


def cmd_log_time(args):
    body = {"duration": args.duration}
    if args.description:
        body["description"] = args.description
    result = api_request(f"/task/{args.task_id}/time", method="POST", data=body)
    print(f"  Time logged: {args.duration}ms on {args.task_id}")


def cmd_prioritize(args):
    data = api_request(f"/list/{args.list_id}/task")
    tasks = data.get("tasks", [])
    if not tasks:
        print("  No tasks to prioritize.")
        return

    task_info = []
    for t in tasks:
        due = t.get("due_date")
        task_info.append({
            "id": t["id"], "name": t["name"], "status": t.get("status", {}).get("status", "?"),
            "priority": t.get("priority", {}).get("priority", "none") if t.get("priority") else "none",
            "due_date": due, "assignees": [a.get("username") for a in t.get("assignees", [])],
        })

    prompt = f"""Score these tasks by urgency × importance (0-100). Consider:
- Due dates (closer = more urgent)
- Current priority level
- Status (blocked items need attention)
- Task name/context

Return a ranked list with scores and brief reasoning.

Tasks:
{json.dumps(task_info, indent=2)}"""

    result = llm_request(prompt)
    print("  AI TASK PRIORITIZATION")
    print(f"  {'='*50}")
    print(result)


def cmd_standup(args):
    data = api_request(f"/list/{args.list_id}/task")
    tasks = data.get("tasks", [])
    if not tasks:
        print("  No tasks for standup.")
        return

    task_info = [{"name": t["name"], "status": t.get("status", {}).get("status", "?"),
                  "assignees": [a.get("username") for a in t.get("assignees", [])]}
                 for t in tasks]

    prompt = f"""Generate a daily standup summary from these tasks. Group into:
1. ✅ Done (completed/closed tasks)
2. 🔄 In Progress (active tasks)
3. 🚫 Blocked (blocked/on hold tasks)
4. 📋 To Do (not started)

Keep it concise, bullet points. Include assignees.

Tasks:
{json.dumps(task_info, indent=2)}"""

    result = llm_request(prompt)
    print("  DAILY STANDUP")
    print(f"  {'='*50}")
    print(result)


def main():
    parser = argparse.ArgumentParser(description="ClickUp Pro API")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("workspaces")

    p = sub.add_parser("spaces"); p.add_argument("team_id")
    p = sub.add_parser("folders"); p.add_argument("space_id")
    p = sub.add_parser("lists"); p.add_argument("folder_id")
    p = sub.add_parser("folderless-lists"); p.add_argument("space_id")

    p = sub.add_parser("tasks"); p.add_argument("list_id")
    p.add_argument("--status"); p.add_argument("--assignee"); p.add_argument("--subtasks", action="store_true")

    p = sub.add_parser("get-task"); p.add_argument("task_id")

    p = sub.add_parser("create-task"); p.add_argument("list_id")
    p.add_argument("--name", required=True); p.add_argument("--description")
    p.add_argument("--priority", type=int); p.add_argument("--due"); p.add_argument("--assignee")

    p = sub.add_parser("update-task"); p.add_argument("task_id")
    p.add_argument("--name"); p.add_argument("--status"); p.add_argument("--priority", type=int)
    p.add_argument("--due"); p.add_argument("--assignee")

    p = sub.add_parser("delete-task"); p.add_argument("task_id")

    p = sub.add_parser("comment"); p.add_argument("task_id"); p.add_argument("--text", required=True)

    p = sub.add_parser("start-timer"); p.add_argument("task_id")
    p = sub.add_parser("stop-timer"); p.add_argument("team_id")
    p = sub.add_parser("log-time"); p.add_argument("task_id")
    p.add_argument("--duration", type=int, required=True); p.add_argument("--description")

    p = sub.add_parser("prioritize"); p.add_argument("list_id")
    p = sub.add_parser("standup"); p.add_argument("list_id")

    args = parser.parse_args()
    cmds = {
        "workspaces": cmd_workspaces, "spaces": cmd_spaces, "folders": cmd_folders,
        "lists": cmd_lists, "folderless-lists": cmd_folderless_lists, "tasks": cmd_tasks,
        "get-task": cmd_get_task, "create-task": cmd_create_task, "update-task": cmd_update_task,
        "delete-task": cmd_delete_task, "comment": cmd_comment, "start-timer": cmd_start_timer,
        "stop-timer": cmd_stop_timer, "log-time": cmd_log_time, "prioritize": cmd_prioritize,
        "standup": cmd_standup,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
