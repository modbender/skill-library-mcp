"""
Twitter API HTTP client (cookie-based auth: auth_token + ct0).
Used by twitter_api.api and twitter_api.twitter.
"""

import json
from typing import Any, Dict, Optional

import aiohttp

from ..utils.constants import PROFILE_HEADERS


def _build_params_from_json(json_data: Dict[str, Any]) -> Dict[str, str]:
    """Turn GraphQL-style payload (variables, features, queryId) into query params."""
    params = {}
    for key, value in json_data.items():
        if value is not None:
            params[key] = json.dumps(value) if not isinstance(value, str) else value
    return params


class TwitterAPIClient:
    """
    Async HTTP client for Twitter/X API with cookie-based auth.
    Supports get/post with json_data (GraphQL) or form data.
    Optional proxy_url (e.g. http://host:port) for requests.
    """

    def __init__(
        self,
        auth_token: str,
        ct0: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy_url: Optional[str] = None,
    ):
        self.auth_token = auth_token
        self.ct0 = ct0 or ""
        self.proxy_url = (proxy_url or "").strip() or None
        self.headers = dict(headers or PROFILE_HEADERS)
        self.headers["cookie"] = f"auth_token={auth_token}; ct0={self.ct0}"
        if self.ct0:
            self.headers["x-csrf-token"] = self.ct0

    async def fetch_csrf_token(self) -> Optional[str]:
        """Return current ct0 (caller may refresh by loading x.com in browser)."""
        return self.ct0 or None

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """GET request. json_data is serialized to query params (Twitter GraphQL style)."""
        qparams = dict(params) if params else {}
        if json_data:
            qparams.update(_build_params_from_json(json_data))
        if data:
            qparams.update(data)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, headers=self.headers, params=qparams or None, proxy=self.proxy_url
            ) as resp:
                if resp.status != 200:
                    return None
                try:
                    return await resp.json()
                except Exception:
                    return None

    async def post(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """POST request. json_data sent as JSON body; data as form."""
        qparams = dict(params) if params else None
        async with aiohttp.ClientSession() as session:
            if json_data is not None:
                async with session.post(
                    url, headers=self.headers, params=qparams, json=json_data, proxy=self.proxy_url
                ) as resp:
                    if resp.status != 200:
                        return None
                    try:
                        return await resp.json()
                    except Exception:
                        return None
            elif data is not None:
                async with session.post(
                    url, headers=self.headers, params=qparams, data=data, proxy=self.proxy_url
                ) as resp:
                    if resp.status != 200:
                        return None
                    try:
                        return await resp.json()
                    except Exception:
                        return None
            else:
                async with session.post(
                    url, headers=self.headers, params=qparams, proxy=self.proxy_url
                ) as resp:
                    if resp.status != 200:
                        return None
                    try:
                        return await resp.json()
                    except Exception:
                        return None


async def _demo_fetch_csrf(auth_token: str, ct0: Optional[str]) -> None:
    """Test fetch_csrf_token with primary creds."""
    client = TwitterAPIClient(auth_token, ct0=ct0 or "")
    token = await client.fetch_csrf_token()
    print("fetch_csrf_token() =>", repr(token))
    if token:
        print("(ct0 length:", len(token), ")")


if __name__ == "__main__":
    import asyncio
    import os
    # Load .env from cwd
    cwd = os.path.abspath(os.getcwd())
    for path in [os.path.join(cwd, ".env"), os.path.join(cwd, "social_ops", ".env")]:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break
    auth = os.environ.get("GANCLAW_X_PRIMARY_AUTH_TOKEN") or os.environ.get("PICLAW_TWITTER_AUTH_TOKEN") or ""
    ct0 = os.environ.get("GANCLAW_X_PRIMARY_CT0") or os.environ.get("PICLAW_TWITTER_CT0") or ""
    if not auth or not ct0:
        print("Set GANCLAW_X_PRIMARY_AUTH_TOKEN and GANCLAW_X_PRIMARY_CT0 (e.g. in .env)")
        raise SystemExit(1)
    asyncio.run(_demo_fetch_csrf(auth, ct0))
