#!/usr/bin/env python3
"""
Plutio API CLI - Manage projects and tasks via command line
"""

import sys
import json
import argparse
import os
from pathlib import Path
import requests
from datetime import datetime
import hashlib

# Config file location
CONFIG_DIR = Path.home() / ".config" / "plutio"
TOKEN_FILE = CONFIG_DIR / "token.json"

class PlutioAPI:
    """Plutio REST API client"""
    
    BASE_URL = "https://api.plutio.com/v1.11"
    OAUTH_ENDPOINT = "https://api.plutio.com/v1.11/oauth/token"
    
    def __init__(self, subdomain: str, app_key: str, secret: str):
        self.subdomain = subdomain
        self.app_key = app_key
        self.secret = secret
        self.access_token = None
        self.token_expires_at = None
        
    def get_token(self) -> str:
        """Get or refresh access token"""
        # Try loading from cache first
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE) as f:
                    data = json.load(f)
                    # Check if token is still valid
                    if data.get("expires_at", 0) > datetime.now().timestamp():
                        if self._verify_token_match(data):
                            self.access_token = data["token"]
                            return self.access_token
            except Exception:
                pass
        
        # Request new token using OAuth 2.0 client credentials flow
        payload = {
            "client_id": self.app_key,
            "client_secret": self.secret,
            "grant_type": "client_credentials"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Business": self.subdomain
        }
        
        resp = requests.post(self.OAUTH_ENDPOINT, data=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        # Response has both accessToken and access_token
        self.access_token = data.get("access_token") or data.get("accessToken")
        expires_in = data.get("expires_in", 3600)
        expires_at = datetime.now().timestamp() + expires_in
        
        # Cache token
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump({
                "token": self.access_token,
                "expires_at": expires_at,
                "credentials_hash": self._hash_credentials()
            }, f)
        TOKEN_FILE.chmod(0o600)  # Restrict file permissions
        
        return self.access_token
    
    def _hash_credentials(self) -> str:
        """Create hash of credentials for verification"""
        cred_str = f"{self.app_key}:{self.secret}"
        return hashlib.sha256(cred_str.encode()).hexdigest()
    
    def _verify_token_match(self, token_data: dict) -> bool:
        """Verify cached token matches current credentials"""
        return token_data.get("credentials_hash") == self._hash_credentials()
    
    def _headers(self) -> dict:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Business": self.subdomain,
            "Content-Type": "application/json"
        }
    
    def list_projects(self, skip: int = 0, limit: int = 50) -> list:
        """List all projects"""
        url = f"{self.BASE_URL}/projects"
        params = {"skip": skip, "limit": limit}
        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        # API returns list directly, not wrapped in {data: [...]}
        return data if isinstance(data, list) else data.get("data", [])
    
    def get_project(self, project_id: str) -> dict:
        """Get single project"""
        url = f"{self.BASE_URL}/projects/{project_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
    
    def list_tasks(self, project_id: str, skip: int = 0, limit: int = 50, status: str = None) -> list:
        """List tasks in a project"""
        url = f"{self.BASE_URL}/tasks"
        params = {"projectId": project_id, "skip": skip, "limit": limit}
        if status:
            params["status"] = status
        
        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        # API returns list directly
        return data if isinstance(data, list) else data.get("data", [])
    
    def get_task(self, task_id: str) -> dict:
        """Get single task"""
        url = f"{self.BASE_URL}/tasks/{task_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
    
    def create_task(self, title: str, task_board_id: str = None, task_group_id: str = None, **kwargs) -> dict:
        """Create a task
        
        Args:
            title: Task title (required)
            task_board_id: Task board ID (required for task to appear in UI)
            task_group_id: Task group/column ID (required for task to appear in UI)
            **kwargs: Optional fields (status, priority, assignee_id, due_date, label_ids, custom_fields)
        """
        url = f"{self.BASE_URL}/tasks"
        payload = {"title": title}
        
        # Board and group are required for task to appear in UI
        if task_board_id:
            payload["taskBoardId"] = task_board_id
        if task_group_id:
            payload["taskGroupId"] = task_group_id
        
        # Add optional fields (only those supported by Plutio v1.11)
        # Note: 'description' field is not supported in the create endpoint
        if "status" in kwargs:
            payload["status"] = kwargs["status"]
        if "priority" in kwargs:
            payload["priority"] = kwargs["priority"]
        if "assignee_id" in kwargs:
            payload["assigneeId"] = kwargs["assignee_id"]
        if "due_date" in kwargs:
            payload["dueDate"] = kwargs["due_date"]
        if "label_ids" in kwargs:
            payload["labelIds"] = kwargs["label_ids"]
        if "custom_fields" in kwargs:
            payload["customFields"] = kwargs["custom_fields"]
        
        resp = requests.post(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
    
    def update_task(self, task_id: str, **kwargs) -> dict:
        """Update a task"""
        url = f"{self.BASE_URL}/tasks/{task_id}"
        payload = {}
        
        # Map CLI args to API fields
        field_map = {
            "title": "title",
            "description": "description",
            "status": "status",
            "priority": "priority",
            "assignee_id": "assigneeId",
            "due_date": "dueDate",
            "label_ids": "labelIds",
            "custom_fields": "customFields"
        }
        
        for cli_key, api_key in field_map.items():
            if cli_key in kwargs:
                payload[api_key] = kwargs[cli_key]
        
        resp = requests.put(url, headers=self._headers(), json=payload)
        resp.raise_for_status()
        return resp.json()
    
    def list_people(self, skip: int = 0, limit: int = 50) -> list:
        """List all people/users in workspace"""
        url = f"{self.BASE_URL}/people"
        params = {"skip": skip, "limit": limit}
        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        # API returns list directly
        return data if isinstance(data, list) else data.get("data", [])


def format_output(data, as_json=False):
    """Format output for display"""
    if as_json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_list_projects(args):
    """Command: list projects"""
    api = PlutioAPI(args.subdomain, args.app_key, args.secret)
    projects = api.list_projects(skip=args.skip, limit=args.limit)
    
    # Filter for active projects if requested
    if args.active_only:
        projects = [p for p in projects if p.get('status', {}).get('title') == 'In progress']
    
    if args.json:
        format_output(projects, as_json=True)
    else:
        if not projects:
            print("No projects found")
            return
        
        status_label = " (Active Only)" if args.active_only else ""
        print(f"\n📋 Projects{status_label}:")
        for p in projects:
            print(f"  • {p['name']} (ID: {p['_id']})")
            if p.get('description'):
                print(f"    {p['description']}")


def cmd_list_tasks(args):
    """Command: list tasks"""
    api = PlutioAPI(args.subdomain, args.app_key, args.secret)
    tasks = api.list_tasks(
        project_id=args.project_id,
        skip=args.skip,
        limit=args.limit,
        status=args.status
    )
    
    if args.json:
        format_output(tasks, as_json=True)
    else:
        if not tasks:
            print("No tasks found")
            return
        
        print(f"\n✓ Tasks ({len(tasks)}):")
        for t in tasks:
            status_emoji = "🟢" if t['status'] == 'open' else "🟡" if t['status'] == 'in_progress' else "⚫"
            priority = f"[{t.get('priority', 'medium').upper()}]" if t.get('priority') else ""
            print(f"  {status_emoji} {t['title']} {priority} (ID: {t['_id']})")
            if t.get('dueDate'):
                print(f"     Due: {t['dueDate'][:10]}")
            if t.get('assignee'):
                print(f"     Assigned to: {t['assignee'].get('name', 'Unknown')}")


def cmd_create_task(args):
    """Command: create task"""
    api = PlutioAPI(args.subdomain, args.app_key, args.secret)
    
    kwargs = {}
    if args.status:
        kwargs["status"] = args.status
    if args.priority:
        kwargs["priority"] = args.priority
    if args.assignee_id:
        kwargs["assignee_id"] = args.assignee_id
    if args.due_date:
        kwargs["due_date"] = args.due_date
    if args.label_ids:
        kwargs["label_ids"] = args.label_ids.split(",")
    if args.custom_fields:
        kwargs["custom_fields"] = json.loads(args.custom_fields)
    
    task = api.create_task(args.title, task_board_id=args.board_id, task_group_id=args.group_id, **kwargs)
    
    if args.json:
        format_output(task, as_json=True)
    else:
        print(f"\n✅ Task created!")
        print(f"   Title: {task['title']}")
        print(f"   ID: {task['_id']}")
        if task.get('dueDate'):
            print(f"   Due: {task['dueDate'][:10]}")
        if not args.board_id or not args.group_id:
            print(f"\n   ⚠️  Note: Task won't appear in Plutio UI without --board-id and --group-id")


def cmd_update_task(args):
    """Command: update task"""
    api = PlutioAPI(args.subdomain, args.app_key, args.secret)
    
    kwargs = {}
    if args.title:
        kwargs["title"] = args.title
    if args.description:
        kwargs["description"] = args.description
    if args.status:
        kwargs["status"] = args.status
    if args.priority:
        kwargs["priority"] = args.priority
    if args.assignee_id:
        kwargs["assignee_id"] = args.assignee_id
    if args.due_date:
        kwargs["due_date"] = args.due_date
    if args.custom_fields:
        kwargs["custom_fields"] = json.loads(args.custom_fields)
    
    task = api.update_task(args.task_id, **kwargs)
    
    if args.json:
        format_output(task, as_json=True)
    else:
        print(f"\n✅ Task updated!")
        print(f"   Title: {task['title']}")
        print(f"   Status: {task['status']}")


def cmd_list_people(args):
    """Command: list people"""
    api = PlutioAPI(args.subdomain, args.app_key, args.secret)
    people = api.list_people(skip=args.skip, limit=args.limit)
    
    if args.json:
        format_output(people, as_json=True)
    else:
        if not people:
            print("No people found")
            return
        
        print("\n👥 People:")
        for p in people:
            name = f"{p['name'].get('first', '')} {p['name'].get('last', '')}".strip()
            email = p.get('email', 'N/A')
            print(f"  • {name} (ID: {p['_id']}) - {email}")


def main():
    parser = argparse.ArgumentParser(
        description="Plutio API CLI - Manage projects and tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  plutio-cli.py list-projects --subdomain grewing --app-key KEY --secret SECRET
  plutio-cli.py list-tasks --project-id ID --subdomain grewing --app-key KEY --secret SECRET
  plutio-cli.py create-task --project-id ID --title "Task" --subdomain grewing --app-key KEY --secret SECRET
  plutio-cli.py update-task --task-id ID --status closed --subdomain grewing --app-key KEY --secret SECRET
        """
    )
    
    # Global arguments
    parser.add_argument("--subdomain", required=True, help="Plutio subdomain (e.g., 'grewing')")
    parser.add_argument("--app-key", required=True, help="Plutio App Key")
    parser.add_argument("--secret", required=True, help="Plutio Secret Code")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # list-projects
    sp = subparsers.add_parser("list-projects", help="List all projects")
    sp.add_argument("--skip", type=int, default=0, help="Skip N items")
    sp.add_argument("--limit", type=int, default=50, help="Limit to N items")
    sp.add_argument("--active-only", action="store_true", help="Show only 'In progress' projects")
    sp.set_defaults(func=cmd_list_projects)
    
    # list-tasks
    sp = subparsers.add_parser("list-tasks", help="List tasks in a project")
    sp.add_argument("--project-id", required=True, help="Project ID")
    sp.add_argument("--skip", type=int, default=0, help="Skip N items")
    sp.add_argument("--limit", type=int, default=50, help="Limit to N items")
    sp.add_argument("--status", help="Filter by status (e.g., 'open')")
    sp.set_defaults(func=cmd_list_tasks)
    
    # create-task
    sp = subparsers.add_parser("create-task", help="Create a new task")
    sp.add_argument("--title", required=True, help="Task title")
    sp.add_argument("--board-id", help="Task board ID (required to appear in UI)")
    sp.add_argument("--group-id", help="Task group/column ID (required to appear in UI)")
    sp.add_argument("--status", help="Task status")
    sp.add_argument("--priority", help="Priority")
    sp.add_argument("--assignee-id", help="Person ID to assign to")
    sp.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    sp.add_argument("--label-ids", help="Label IDs (comma-separated)")
    sp.add_argument("--custom-fields", help="Custom fields as JSON")
    sp.set_defaults(func=cmd_create_task)
    
    # update-task
    sp = subparsers.add_parser("update-task", help="Update an existing task")
    sp.add_argument("--task-id", required=True, help="Task ID")
    sp.add_argument("--title", help="Task title")
    sp.add_argument("--description", help="Task description")
    sp.add_argument("--status", help="Task status (open, in_progress, closed)")
    sp.add_argument("--priority", help="Priority (low, medium, high, urgent)")
    sp.add_argument("--assignee-id", help="Person ID to assign to")
    sp.add_argument("--due-date", help="Due date (YYYY-MM-DD)")
    sp.add_argument("--custom-fields", help="Custom fields as JSON")
    sp.set_defaults(func=cmd_update_task)
    
    # list-people
    sp = subparsers.add_parser("list-people", help="List all people in workspace")
    sp.add_argument("--skip", type=int, default=0, help="Skip N items")
    sp.add_argument("--limit", type=int, default=50, help="Limit to N items")
    sp.set_defaults(func=cmd_list_people)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"   {error_data.get('error', 'Unknown error')}", file=sys.stderr)
        except:
            print(f"   {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
