from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class BarkResponse:
    ok: bool
    status_code: int
    data: dict[str, Any] | None
    error: str | None


class BarkClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def push_json(self, payload: dict[str, Any], timeout_s: float = 10.0) -> BarkResponse:
        url = self._resolve_url(payload)
        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = Request(url, data=body_bytes, method="POST")
        req.add_header("Content-Type", "application/json; charset=utf-8")
        try:
            with urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                data = self._safe_json(raw)
                ok = 200 <= int(resp.status) < 300
                return BarkResponse(ok=ok, status_code=int(resp.status), data=data, error=None if ok else raw)
        except HTTPError as e:
            raw = ""
            try:
                raw = e.read().decode("utf-8", errors="replace")
            except Exception:
                raw = str(e)
            return BarkResponse(ok=False, status_code=int(getattr(e, "code", 0) or 0), data=self._safe_json(raw), error=raw)
        except URLError as e:
            return BarkResponse(ok=False, status_code=0, data=None, error=str(e))
        except Exception as e:
            return BarkResponse(ok=False, status_code=0, data=None, error=str(e))

    def _resolve_url(self, payload: dict[str, Any]) -> str:
        if payload.get("_use_push_path") is True:
            payload.pop("_use_push_path", None)
            if self._base_url.endswith("/push"):
                return self._base_url
            return f"{self._base_url}/push"
        payload.pop("_use_push_path", None)
        return self._base_url

    def _safe_json(self, raw: str) -> dict[str, Any] | None:
        raw = (raw or "").strip()
        if not raw:
            return None
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
            return {"data": data}
        except Exception:
            return None
