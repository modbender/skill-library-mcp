from typing import Any, Dict, List, Optional

import requests

from ..retry import with_retry


class ClawTasksError(RuntimeError):
    pass


class ClawTasksClient:
    """Beacon transport for ClawTasks (clawtasks.com) — bounty & task marketplace for AI agents.

    Actions: browse bounties, get bounty details, create bounties.
    """

    def __init__(
        self,
        base_url: str = "https://clawtasks.com",
        api_key: Optional[str] = None,
        timeout_s: int = 20,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Beacon/1.0.0 (Elyan Labs)"})

    def _request(self, method: str, path: str, auth: bool = False, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        if auth:
            if not self.api_key:
                raise ClawTasksError("ClawTasks API key required")
            headers = dict(headers)
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["Content-Type"] = "application/json"

        def _do():
            resp = self.session.request(method, url, headers=headers, timeout=self.timeout_s, **kwargs)
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            if resp.status_code >= 400:
                raise ClawTasksError(data.get("error") or f"HTTP {resp.status_code}")
            return data

        return with_retry(_do)

    def get_bounties(self, status: str = "open", limit: int = 20) -> List[Dict[str, Any]]:
        result = self._request("GET", f"/api/bounties?status={status}&limit={limit}", auth=True)
        return result.get("bounties", result) if isinstance(result, dict) else result

    def get_bounty(self, bounty_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/bounties/{bounty_id}", auth=True)

    def create_bounty(self, title: str, description: str, tags: Optional[List[str]] = None, deadline_hours: int = 168) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"title": title, "description": description, "deadline_hours": deadline_hours}
        if tags:
            payload["tags"] = tags
        return self._request("POST", "/api/bounties", auth=True, json=payload)
