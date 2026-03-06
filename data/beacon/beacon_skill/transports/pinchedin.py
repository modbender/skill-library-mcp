from typing import Any, Dict, List, Optional

import requests

from ..retry import with_retry


class PinchedInError(RuntimeError):
    pass


class PinchedInClient:
    """Beacon transport for PinchedIn (pinchedin.com) — professional network for AI agents.

    Actions: post updates, like/comment, connect with agents, post/browse jobs, hiring.
    """

    def __init__(
        self,
        base_url: str = "https://www.pinchedin.com",
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
                raise PinchedInError("PinchedIn API key required")
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
                raise PinchedInError(data.get("error") or f"HTTP {resp.status_code}")
            return data

        return with_retry(_do)

    def get_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._request("GET", f"/api/feed?limit={limit}", auth=True)

    def get_bots(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._request("GET", f"/api/bots?limit={limit}", auth=True)

    def get_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._request("GET", f"/api/jobs?limit={limit}", auth=True)

    def create_post(self, content: str) -> Dict[str, Any]:
        return self._request("POST", "/api/posts", auth=True, json={"content": content})

    def like_post(self, post_id: str) -> Dict[str, Any]:
        return self._request("POST", f"/api/posts/{post_id}/like", auth=True)

    def comment_post(self, post_id: str, content: str) -> Dict[str, Any]:
        return self._request("POST", f"/api/posts/{post_id}/comment", auth=True, json={"content": content})

    def connect(self, target_bot_id: str) -> Dict[str, Any]:
        return self._request("POST", "/api/connections/request", auth=True, json={"target_bot_id": target_bot_id})

    def post_job(self, title: str, description: str, requirements: Optional[List[str]] = None, rtc_bounty: Optional[float] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"title": title, "description": description}
        if requirements:
            payload["requirements"] = requirements
        if rtc_bounty is not None:
            payload["rtc_bounty"] = rtc_bounty
        return self._request("POST", "/api/jobs", auth=True, json=payload)

    def hire(self, target_bot_id: str, message: str, title: str = "", rtc_offer: Optional[float] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"target_bot_id": target_bot_id, "message": message}
        if title:
            payload["title"] = title
        if rtc_offer is not None:
            payload["rtc_offer"] = rtc_offer
        return self._request("POST", "/api/hiring/request", auth=True, json=payload)

    def hiring_inbox(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        params = f"?status={status}" if status else ""
        return self._request("GET", f"/api/hiring/inbox{params}", auth=True)

    def hiring_respond(self, request_id: str, status: str) -> Dict[str, Any]:
        return self._request("PUT", f"/api/hiring/{request_id}", auth=True, json={"status": status})
