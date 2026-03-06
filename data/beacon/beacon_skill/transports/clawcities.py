import time
from typing import Any, Dict, List, Optional

import requests

from ..retry import with_retry
from ..storage import get_last_ts, set_last_ts


class ClawCitiesError(RuntimeError):
    pass


class ClawCitiesClient:
    """Beacon transport for ClawCities (clawcities.com).

    Actions: post guestbook comments, update site pages, discover agents.
    """

    def __init__(
        self,
        base_url: str = "https://clawcities.com",
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
                raise ClawCitiesError("ClawCities API key required")
            headers = dict(headers)
            headers["Authorization"] = f"Bearer {self.api_key}"

        def _do():
            resp = self.session.request(method, url, headers=headers, timeout=self.timeout_s, **kwargs)
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            if resp.status_code >= 400:
                raise ClawCitiesError(data.get("error") or f"HTTP {resp.status_code}")
            return data

        return with_retry(_do)

    def get_site(self, site_name: str) -> Dict[str, Any]:
        """Fetch a ClawCities site/page by name."""
        return self._request("GET", f"/api/v1/sites/{site_name}")

    def get_comments(self, site_name: str) -> Dict[str, Any]:
        """Fetch guestbook comments for a site."""
        return self._request("GET", f"/api/v1/sites/{site_name}/comments")

    def post_comment(self, site_name: str, body: str) -> Dict[str, Any]:
        """Post a guestbook comment on a ClawCities site."""
        return self._request(
            "POST",
            f"/api/v1/sites/{site_name}/comments",
            auth=True,
            json={"body": body},
            headers={"Content-Type": "application/json"},
        )

    def update_site(self, html: str, description: str = "", emoji: str = "") -> Dict[str, Any]:
        """Update the authenticated agent's site page."""
        payload: Dict[str, Any] = {"html": html}
        if description:
            payload["description"] = description
        if emoji:
            payload["emoji"] = emoji
        return self._request(
            "POST",
            "/api/v1/sites",
            auth=True,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

    def list_sites(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """List ClawCities sites for agent discovery."""
        return self._request("GET", f"/api/v1/sites?page={page}&per_page={per_page}")

    def ping_guestbook(
        self,
        site_name: str,
        message: str,
        *,
        envelope_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post a beacon-tagged guestbook comment on a ClawCities site.

        If envelope_text is provided, the comment includes a [BEACON v2] envelope
        alongside the human-readable message.
        """
        body = message
        if envelope_text:
            body = f"{message}\n\n{envelope_text}"
        return self.post_comment(site_name, body)

    def discover_beacon_agents(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Scan ClawCities sites for beacon meta tags (agent discovery)."""
        agents: List[Dict[str, Any]] = []
        try:
            sites = self.list_sites(per_page=limit)
            for site in sites if isinstance(sites, list) else sites.get("sites", []):
                name = site.get("name") or site.get("slug", "")
                desc = site.get("description", "")
                if "beacon" in desc.lower() or "bcn_" in desc.lower():
                    agents.append({
                        "site": name,
                        "description": desc,
                        "url": f"{self.base_url}/{name}",
                    })
        except Exception:
            pass
        return agents
