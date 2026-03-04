#!/usr/bin/env python3
"""Minimal Kagi API client (no external deps).

Env:
  - KAGI_API_TOKEN: required

Docs:
  - https://help.kagi.com/kagi/api/
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


class KagiError(RuntimeError):
    pass


BASE_URL = "https://kagi.com/api/v0"


def _token() -> str:
    tok = os.environ.get("KAGI_API_TOKEN") or os.environ.get("KAGI_API_KEY")
    if not tok:
        raise KagiError(
            "Missing KAGI_API_TOKEN (or KAGI_API_KEY). Create one at https://kagi.com/settings/api"
        )
    return tok.strip()


def _request(method: str, path: str, *, params: Optional[Dict[str, str]] = None, json_body: Any = None, timeout: int = 60) -> Dict[str, Any]:
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Authorization": f"Bot {_token()}",
        "Accept": "application/json",
    }

    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, method=method.upper(), headers=headers, data=data)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return json.loads(raw)
            except json.JSONDecodeError as e:
                raise KagiError(f"Non-JSON response from Kagi: {e}\n---\n{raw[:500]}")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise KagiError(f"Kagi HTTP {e.code}: {body or e.reason}")
    except urllib.error.URLError as e:
        raise KagiError(f"Kagi request failed: {e}")


def search(query: str) -> Dict[str, Any]:
    return _request("GET", "/search", params={"q": query})


def fastgpt(query: str, *, cache: bool = True, web_search: bool = True) -> Dict[str, Any]:
    # NOTE: docs say web_search is currently out of service (must be true), but we keep param for forward-compat.
    body = {"query": query, "cache": bool(cache), "web_search": bool(web_search)}
    return _request("POST", "/fastgpt", json_body=body)
