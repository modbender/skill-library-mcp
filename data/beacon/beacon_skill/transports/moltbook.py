import time
from typing import Any, Dict, Optional

import requests

from ..retry import with_retry
from ..storage import get_last_ts, set_last_ts


class MoltbookError(RuntimeError):
    pass


class MoltbookClient:
    def __init__(
        self,
        base_url: str = "https://www.moltbook.com",
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
                raise MoltbookError("Moltbook API key required")
            headers = dict(headers)
            headers["Authorization"] = f"Bearer {self.api_key}"

        def _do():
            resp = self.session.request(method, url, headers=headers, timeout=self.timeout_s, **kwargs)
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            if resp.status_code >= 400:
                raise MoltbookError(data.get("error") or f"HTTP {resp.status_code}")
            return data

        return with_retry(_do)

    def upvote(self, post_id: int) -> Dict[str, Any]:
        return self._request("POST", f"/api/v1/posts/{int(post_id)}/upvote", auth=True)

    def create_post(self, submolt: str, title: str, content: str, *, force: bool = False) -> Dict[str, Any]:
        """Create a Moltbook post with a local IP-rate-limit guard (30 min default).

        This does not bypass Moltbook's server-side rate limit; it helps avoid
        accidental tight loops that can get accounts suspended.
        """
        guard_key = "moltbook_post"
        last_ts = get_last_ts(guard_key)
        if not force and last_ts is not None and (time.time() - last_ts) < 1800:
            raise MoltbookError("Local guard: Moltbook posting is limited to 1 per 30 minutes (use --force to override).")
        resp = self._request(
            "POST",
            "/api/v1/posts",
            auth=True,
            json={"submolt": submolt, "title": title, "content": content},
            headers={"Content-Type": "application/json"},
        )
        set_last_ts(guard_key)
        return resp

