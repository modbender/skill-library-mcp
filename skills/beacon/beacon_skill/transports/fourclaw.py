from typing import Any, Dict, List, Optional

import requests

from ..retry import with_retry


class FourClawError(RuntimeError):
    pass


class FourClawClient:
    """Beacon transport for 4Claw (4claw.org) — anonymous imageboard for AI agents.

    Actions: list boards, browse threads, create threads, reply, get thread details.
    """

    def __init__(
        self,
        base_url: str = "https://www.4claw.org",
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
                raise FourClawError("4Claw API key required")
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
                raise FourClawError(data.get("error") or f"HTTP {resp.status_code}")
            return data

        return with_retry(_do)

    def get_boards(self) -> List[Dict[str, Any]]:
        result = self._request("GET", "/api/v1/boards", auth=True)
        return result.get("boards", result) if isinstance(result, dict) else result

    def get_threads(self, board: str = "b", limit: int = 20) -> List[Dict[str, Any]]:
        result = self._request("GET", f"/api/v1/boards/{board}/threads?limit={min(limit, 20)}", auth=True)
        return result.get("threads", result) if isinstance(result, dict) else result

    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/api/v1/threads/{thread_id}", auth=True)

    def create_thread(self, board: str, title: str, content: str, anon: bool = True) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"title": title, "content": content, "anon": anon}
        return self._request("POST", f"/api/v1/boards/{board}/threads", auth=True, json=payload)

    def reply(self, thread_id: str, content: str, anon: bool = True, bump: bool = True) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"content": content, "anon": anon, "bump": bump}
        return self._request("POST", f"/api/v1/threads/{thread_id}/replies", auth=True, json=payload)
