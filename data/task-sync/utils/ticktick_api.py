import json
import logging
import os

import requests

log = logging.getLogger(__name__)


class TickTickAPI:
    def __init__(self, token_path, api_base):
        self.api_base = api_base
        self.token = self._load_token(token_path)

    def _load_token(self, path):
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                return json.load(f).get("access_token")
        except (json.JSONDecodeError, IOError) as e:
            log.error("Failed to load TickTick token: %s", e)
            return None

    def is_authenticated(self):
        return self.token is not None

    def _request(self, endpoint, method="GET", data=None):
        if not self.token:
            return None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        url = f"{self.api_base}{endpoint}"
        try:
            resp = requests.request(
                method, url, headers=headers,
                json=data if data else None, timeout=30,
            )
            if resp.ok:
                return resp.json() if resp.content else {}
            log.error("TickTick %s %s -> %d: %s", method, endpoint, resp.status_code, resp.text[:200])
            return None
        except requests.RequestException as e:
            log.error("TickTick request error: %s", e)
            return None

    # ── Projects ──

    def get_projects(self):
        return self._request("/project") or []

    def create_project(self, name):
        return self._request("/project", "POST", {"name": name})

    # ── Tasks ──

    def get_tasks(self, project_id):
        data = self._request(f"/project/{project_id}/data")
        if data and "tasks" in data:
            return data["tasks"]
        return []

    def get_task(self, project_id, task_id):
        """Get a single task by ID. Returns task dict or None if deleted/not found."""
        return self._request(f"/project/{project_id}/task/{task_id}")

    def create_task(self, project_id, title, content="", due_date=None):
        body = {"title": title, "projectId": project_id}
        if content:
            body["content"] = content
        if due_date:
            body["dueDate"] = due_date
        return self._request("/task", "POST", body)

    def update_task(self, task):
        """Update a task. Pass the full task object."""
        return self._request(f"/task/{task['id']}", "POST", task)

    def complete_task(self, project_id, task_id):
        return self._request(f"/project/{project_id}/task/{task_id}/complete", "POST")

    def delete_task(self, project_id, task_id):
        return self._request(f"/project/{project_id}/task/{task_id}", "DELETE")
