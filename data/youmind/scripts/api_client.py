#!/usr/bin/env python3
"""
API-first Youmind client.
Business operations use HTTP APIs only. Browser is only for auth bootstrap/refresh.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from config import STATE_FILE, YOUMIND_BASE_URL


class ApiError(RuntimeError):
    pass


class AuthError(ApiError):
    pass


def _board_id_from_url(board_url: str) -> str:
    parsed = urllib.parse.urlparse(board_url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "boards":
        return parts[1]
    raise ValueError(f"Invalid board URL: {board_url}")


class YoumindApiClient:
    def __init__(self, timezone: str = "Asia/Shanghai"):
        self.base_url = YOUMIND_BASE_URL.rstrip("/")
        self.timezone = timezone
        self._cookie_header = self._load_cookie_header()

    @staticmethod
    def board_id_from_url(board_url: str) -> str:
        return _board_id_from_url(board_url)

    def _load_cookie_header(self) -> str:
        # 1. Try dynamic CDP cookie fetching (OpenClaw browser).
        #    Cookies are always fresh from the live browser; no manual re-auth needed.
        #    On first use with no session, opens the sign-in page and waits for login.
        try:
            import sys as _sys
            import os as _os
            _sys.path.insert(0, _os.path.dirname(__file__))
            from cdp_auth import ensure_authenticated
            cookie_str = ensure_authenticated(interactive=True)
            if cookie_str:
                return cookie_str
        except Exception:
            pass

        # 2. Fall back to state.json (set by `auth_manager.py login`).
        if not STATE_FILE.exists():
            raise AuthError(
                f"Auth state not found: {STATE_FILE}\n"
                "Options:\n"
                "  • Ensure the OpenClaw browser is running (CDP port 18800) — preferred\n"
                "  • Or run: python3 scripts/run.py auth_manager.py login"
            )

        state = json.loads(STATE_FILE.read_text())
        cookies = state.get("cookies", [])
        pairs = []
        for cookie in cookies:
            domain = cookie.get("domain", "")
            if "youmind.com" not in domain:
                continue
            name = cookie.get("name")
            value = cookie.get("value")
            if name and value is not None:
                pairs.append(f"{name}={value}")

        if not pairs:
            raise AuthError("No Youmind cookies found in state.json")

        return "; ".join(pairs)

    def _headers(self, referer: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "accept": "*/*",
            "accept-language": "zh,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": self.base_url,
            "pragma": "no-cache",
            "referer": referer or f"{self.base_url}/boards",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
            ),
            "x-client-type": "youmind-skill",
            "x-time-zone": self.timezone,
            "cookie": self._cookie_header,
        }
        if extra:
            headers.update(extra)
        return headers

    def _post(self, path: str, payload: Dict[str, Any], referer: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None) -> str:
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers=self._headers(referer=referer, extra=extra_headers),
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "ignore")
            if exc.code in (401, 403):
                raise AuthError(f"HTTP {exc.code}: {body}") from exc
            raise ApiError(f"HTTP {exc.code}: {body}") from exc

    @staticmethod
    def _try_json(text: str) -> Any:
        try:
            return json.loads(text)
        except Exception:
            return text

    @staticmethod
    def parse_sse_events(text: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload:
                continue
            try:
                events.append(json.loads(payload))
            except Exception:
                events.append({"raw": payload})
        return events

    def ping_auth(self) -> bool:
        _ = self.list_boards()
        return True

    # Board APIs
    def list_boards(self) -> Any:
        return self._try_json(self._post("/api/v1/listBoards", {}))

    def find_boards(self, query: str) -> List[Dict[str, Any]]:
        query_l = query.lower()
        boards = self.list_boards()
        if not isinstance(boards, list):
            return []
        out = []
        for board in boards:
            name = str(board.get("name", "")).lower()
            bid = str(board.get("id", "")).lower()
            if query_l in name or query_l in bid:
                out.append(board)
        return out

    def get_board_detail(self, board_id: str) -> Any:
        return self._try_json(self._post("/api/v1/board/getBoardDetail", {"id": board_id}))

    def create_board(
        self,
        name: str,
        prompt: Optional[str] = None,
        description: str = "",
        icon_name: str = "Game",
        icon_color: str = "--function-red",
    ) -> Any:
        payload: Dict[str, Any] = {
            "name": name,
            "description": description,
            "icon": {"name": icon_name, "color": icon_color},
        }
        if prompt:
            payload["prompt"] = prompt
        return self._try_json(self._post("/api/v1/createBoard", payload))

    # Material APIs
    def add_link(self, board_id: str, url: str) -> Any:
        payload = {"url": url, "board_id": board_id}
        referer = f"{self.base_url}/boards/{board_id}"
        return self._try_json(self._post("/api/v1/tryCreateSnipByUrl", payload, referer=referer))

    def get_snips(self, ids: List[str]) -> Any:
        payload = {"ids": ids}
        return self._try_json(self._post("/api/v1/snip/getSnips", payload, extra_headers={"x-use-snake-case": "true"}))

    def list_picks(self, board_id: str) -> Any:
        return self._try_json(self._post("/api/v1/pick/listPicks", {"board_id": board_id}))

    def upload_file(self, board_id: str, file_path: str) -> Dict[str, Any]:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()

        signed_url = self._post("/api/v1/genSignedPutUrlIfNotExist", {"hash": digest}).strip()
        if not signed_url.startswith("http"):
            raise ApiError(f"Unexpected signed URL response: {signed_url[:200]}")

        put_headers = {
            "content-type": mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        }
        put_req = urllib.request.Request(signed_url, data=raw, method="PUT", headers=put_headers)
        with urllib.request.urlopen(put_req, timeout=120) as response:
            if response.status // 100 != 2:
                raise ApiError(f"Upload failed with status {response.status}")

        cdn_url = signed_url.split("?", 1)[0]
        # Returns file id string
        file_record_id = self._post(
            "/api/v1/createFileRecordFromCdnUrl",
            {"cdnUrl": cdn_url, "name": path.name},
        ).strip()

        # Attach file to board and create material entry.
        text_file = self._try_json(
            self._post(
                "/api/v1/createTextFile",
                {
                    "file": {"name": path.name, "hash": digest},
                    "board_id": board_id,
                },
                referer=f"{self.base_url}/boards/{board_id}",
            )
        )

        return {
            "file_path": str(path),
            "sha256": digest,
            "signed_url": signed_url,
            "cdn_url": cdn_url,
            "file_record_id": file_record_id,
            "material": text_file,
        }

    # Chat APIs
    def create_chat(
        self,
        board_id: str,
        message: str,
        message_mode: str = "agent",
        max_mode: bool = False,
    ) -> Dict[str, Any]:
        payload = {
            "origin": {"type": "board", "id": board_id},
            "board_id": board_id,
            "message": message,
            "message_mode": message_mode,
            "max_mode": max_mode,
        }
        raw = self._post("/api/v2/chatAssistant/createChat", payload, referer=f"{self.base_url}/boards/{board_id}")
        return {"raw": raw, "events": self.parse_sse_events(raw)}

    def send_message(
        self,
        chat_id: str,
        board_id: str,
        message: str,
        message_mode: str = "agent",
        max_mode: bool = False,
    ) -> Dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "message": message,
            "board_id": board_id,
            "message_mode": message_mode,
            "origin": {"type": "board", "id": board_id},
            "max_mode": max_mode,
        }
        raw = self._post("/api/v2/chatAssistant/sendMessage", payload, referer=f"{self.base_url}/boards/{board_id}")
        return {"raw": raw, "events": self.parse_sse_events(raw)}

    def list_chat_history(self, board_id: str) -> Any:
        payload = {"origin": {"type": "board", "id": board_id}}
        return self._try_json(self._post("/api/v2/chatAssistant/listChatHistory", payload, referer=f"{self.base_url}/boards/{board_id}"))

    def get_chat_detail_by_origin(self, board_id: str) -> Any:
        payload = {"type": "board", "id": board_id}
        return self._try_json(self._post("/api/v2/chatAssistant/getChatDetailByOrigin", payload, referer=f"{self.base_url}/boards/{board_id}"))

    def get_chat_detail(self, chat_id: str) -> Any:
        return self._try_json(self._post("/api/v2/chatAssistant/getChatDetail", {"chatId": chat_id}))

    def mark_chat_as_read(self, chat_id: str) -> Any:
        return self._try_json(self._post("/api/v2/chatAssistant/markChatAsRead", {"chat_id": chat_id}))
