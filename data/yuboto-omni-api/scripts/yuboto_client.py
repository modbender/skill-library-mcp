#!/usr/bin/env python3
"""Minimal Yuboto Omni API client (v2 endpoints).

Focuses on production-critical flows:
- Send message
- Delivery lookup (DLR)
- Cost check
- User balance
- Cancel message

Auth: API key via Authorization header.
Swagger indicates: Authorization: Basic <apiKey>
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import requests


class YubotoApiError(Exception):
    def __init__(self, status_code: int, message: str, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


@dataclass
class YubotoConfig:
    api_key: str
    base_url: str = "https://api.yuboto.com"
    timeout: int = 30


class YubotoClient:
    def __init__(self, config: YubotoConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self._build_auth_header(config.api_key),
        })

    @staticmethod
    def _build_auth_header(api_key: str) -> str:
        k = (api_key or "").strip()
        if not k:
            raise ValueError("api_key is required")
        # Accept either raw key or already-prefixed header value.
        if k.lower().startswith("basic "):
            return k
        return f"Basic {k}"

    def _url(self, path: str) -> str:
        return self.config.base_url.rstrip("/") + path

    def _request(self, method: str, path: str, *, params: Optional[Dict[str, Any]] = None, json_body: Optional[Dict[str, Any]] = None) -> Any:
        try:
            r = self.session.request(
                method=method,
                url=self._url(path),
                params=params,
                json=json_body,
                timeout=self.config.timeout,
            )
        except requests.RequestException as e:
            raise YubotoApiError(-1, f"Network error: {e}") from e

        # Parse response payload when possible.
        payload: Any = None
        if r.text:
            try:
                payload = r.json()
            except Exception:
                payload = r.text

        if r.status_code >= 400:
            msg = f"HTTP {r.status_code} for {method} {path}"
            if isinstance(payload, dict):
                # Common ASP.NET ProblemDetails keys
                detail = payload.get("detail") or payload.get("title") or payload.get("message")
                if detail:
                    msg += f": {detail}"
            raise YubotoApiError(r.status_code, msg, payload=payload)

        return payload

    # -------- core account --------
    def user_balance(self) -> Dict[str, Any]:
        return self._request("GET", "/v2/Account/UserBalance")

    def cost(self, *, channel: str, iso2: Optional[str] = None, phonenumber: Optional[str] = None) -> Dict[str, Any]:
        ch = (channel or "").strip()
        body: Dict[str, Any] = {"channel": ch}
        if iso2:
            body["iso2"] = iso2
        if phonenumber:
            body["phonenumber"] = phonenumber
        return self._request("POST", "/v2/Account/Cost", json_body=body)

    # -------- messaging --------
    def send_message(
        self,
        *,
        contacts: List[str],
        sms_text: Optional[str] = None,
        sms_sender: Optional[str] = None,
        viber_text: Optional[str] = None,
        viber_sender: Optional[str] = None,
        dlr: bool = True,
        callback_url: Optional[str] = None,
        date_and_time_to_send: Optional[str] = None,
        option1: Optional[str] = None,
        option2: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not contacts:
            raise ValueError("contacts cannot be empty")

        contact_objs = []
        for c in contacts:
            cc = (c or "").strip()
            if not cc:
                continue
            contact_objs.append({"phonenumber": cc})

        body: Dict[str, Any] = {
            "contacts": contact_objs,
            "dlr": dlr,
        }

        if callback_url:
            body["callbackUrl"] = callback_url
        if date_and_time_to_send:
            body["dateAndTimeToSend"] = date_and_time_to_send
        if option1:
            body["option1"] = option1
        if option2:
            body["option2"] = option2

        if sms_text:
            sender = sms_sender or "Yuboto"
            body["sms"] = {"sender": sender, "text": sms_text}
        if viber_text:
            sender = viber_sender or sms_sender or "Yuboto"
            body["viber"] = {"sender": sender, "viberMessageType": "Text", "text": viber_text}

        if not (body.get("sms") or body.get("viber") or (extra and any(k in extra for k in ["email", "sms", "viber"]))):
            raise ValueError("At least one channel payload is required (sms_text/viber_text or extra payload)")

        if extra:
            body.update(extra)

        try:
            return self._request("POST", "/v2/Messages/Send", json_body=body)
        except YubotoApiError as e:
            # Some backends may be configured to expect a wrapper object name.
            if e.status_code == 400 and isinstance(e.payload, dict):
                errs = (e.payload.get("errors") or {})
                if "sendMessageRequest" in errs:
                    wrapped = {"sendMessageRequest": body}
                    return self._request("POST", "/v2/Messages/Send", json_body=wrapped)
            raise

    def dlr(self, message_id: str) -> Any:
        return self._request("GET", f"/v2/Messages/Dlr/{message_id}")

    def dlr_by_phonenumber(self, message_id: str) -> Any:
        return self._request("GET", f"/v2/Messages/DlrPhonenumber/{message_id}")

    def cancel_message(self, message_id: str) -> Any:
        return self._request("GET", f"/v2/Messages/Cancel/{message_id}")


if __name__ == "__main__":
    # quick local sanity only
    print("YubotoClient module loaded")
