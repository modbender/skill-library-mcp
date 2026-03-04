import logging
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

log = logging.getLogger(__name__)


class GoogleAPI:
    def __init__(self, token_path):
        self.token_path = token_path
        self.service = self._build_service()

    def _build_service(self):
        if not os.path.exists(self.token_path):
            return None
        try:
            creds = Credentials.from_authorized_user_file(self.token_path)
            if creds.expired and creds.refresh_token:
                log.info("Refreshing Google token")
                creds.refresh(Request())
                with open(self.token_path, "w") as f:
                    f.write(creds.to_json())
            return build("tasks", "v1", credentials=creds)
        except Exception as e:
            log.error("Google service init failed: %s", e)
            return None

    def is_authenticated(self):
        return self.service is not None

    # ── Task Lists ──

    def get_lists(self):
        try:
            return self.service.tasklists().list(maxResults=100).execute().get("items", [])
        except Exception as e:
            log.error("get_lists: %s", e)
            return []

    def create_list(self, title):
        try:
            return self.service.tasklists().insert(body={"title": title}).execute()
        except Exception as e:
            log.error("create_list '%s': %s", title, e)
            return None

    def update_list(self, list_id, title):
        try:
            return self.service.tasklists().update(
                tasklist=list_id, body={"title": title, "id": list_id}
            ).execute()
        except Exception as e:
            log.error("update_list: %s", e)
            return None

    def delete_list(self, list_id):
        try:
            self.service.tasklists().delete(tasklist=list_id).execute()
            return True
        except Exception as e:
            log.error("delete_list %s: %s", list_id, e)
            return False

    # ── Tasks ──

    def get_tasks(self, list_id, show_completed=False):
        """Fetch all tasks with pagination."""
        all_tasks = []
        page_token = None
        try:
            while True:
                params = {
                    "tasklist": list_id,
                    "maxResults": 100,
                    "showCompleted": show_completed,
                    "showHidden": show_completed,
                }
                if page_token:
                    params["pageToken"] = page_token
                result = self.service.tasks().list(**params).execute()
                all_tasks.extend(result.get("items", []))
                page_token = result.get("nextPageToken")
                if not page_token:
                    break
        except Exception as e:
            log.error("get_tasks list=%s: %s", list_id, e)
        return all_tasks

    def create_task(self, list_id, title, notes="", due_date=None):
        try:
            body = {"title": title}
            if notes:
                body["notes"] = notes
            if due_date:
                body["due"] = due_date
            return self.service.tasks().insert(tasklist=list_id, body=body).execute()
        except Exception as e:
            log.error("create_task '%s': %s", title, e)
            return None

    def update_task(self, list_id, task_id, **fields):
        """Update task fields (title, notes, due, status, etc.).

        Pass due=None to clear the due date.
        Pass status='completed' or status='needsAction' to change completion.
        """
        try:
            task = self.service.tasks().get(tasklist=list_id, task=task_id).execute()
            changed = False
            for key, value in fields.items():
                if task.get(key) != value:
                    task[key] = value
                    changed = True
            if changed:
                return self.service.tasks().update(
                    tasklist=list_id, task=task_id, body=task
                ).execute()
            return task
        except Exception as e:
            log.error("update_task %s: %s", task_id, e)
            return None

    def delete_task(self, list_id, task_id):
        try:
            self.service.tasks().delete(tasklist=list_id, task=task_id).execute()
            return True
        except Exception as e:
            log.error("delete_task %s: %s", task_id, e)
            return False
