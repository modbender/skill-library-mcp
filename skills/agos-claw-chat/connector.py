#!/usr/bin/env python3
"""
AITalk OpenClaw connector skill runtime.

Usage:
  python connector.py --api-base https://chat-api.agos.fun --match-code AGOS-XXXX-YYYY

The connector performs:
- register-with-code
- periodic heartbeat
- long-poll request claim
- local response execution
- complete callback with usage
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests


VERSION = "0.1.0"


@dataclass
class ConnectorSession:
    session_token: str
    provider_id: str
    connector_session_id: str
    heartbeat_interval_sec: int
    expires_at: datetime


class AITalkConnector:
    def __init__(
        self,
        api_base: str,
        connector_id: str,
        state_file: Path,
        timeout_sec: int,
        agent_cmd: Optional[str] = None,
    ):
        self.api_base = api_base.rstrip("/")
        self.connector_id = connector_id
        self.state_file = state_file
        self.timeout_sec = timeout_sec
        self.agent_cmd = agent_cmd
        self.http = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self.api_base}{path}"

    def _parse_expiry(self, raw: str) -> datetime:
        value = raw.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def _load_session(self) -> Optional[ConnectorSession]:
        if not self.state_file.exists():
            return None
        data = json.loads(self.state_file.read_text("utf-8"))
        if "session_token" not in data:
            return None
        return ConnectorSession(
            session_token=data["session_token"],
            provider_id=data.get("provider_id", ""),
            connector_session_id=data.get("connector_session_id", ""),
            heartbeat_interval_sec=int(data.get("heartbeat_interval_sec", 30)),
            expires_at=self._parse_expiry(data["expires_at"]),
        )

    def _save_session(self, session: ConnectorSession) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_token": session.session_token,
            "provider_id": session.provider_id,
            "connector_session_id": session.connector_session_id,
            "heartbeat_interval_sec": session.heartbeat_interval_sec,
            "expires_at": session.expires_at.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.state_file.write_text(json.dumps(payload, indent=2), "utf-8")

    def register_with_code(self, match_code: str) -> ConnectorSession:
        resp = self.http.post(
            self._url("/api/v2/openclaw/connectors/register-with-code"),
            json={
                "match_code": match_code,
                "connector_id": self.connector_id,
                "client_version": VERSION,
                "capabilities": {"mode": "polling", "runtime": "python"},
            },
            timeout=self.timeout_sec,
        )
        resp.raise_for_status()
        body = resp.json()
        session = ConnectorSession(
            session_token=body["session_token"],
            provider_id=body["provider_id"],
            connector_session_id=body["connector_session_id"],
            heartbeat_interval_sec=int(body.get("heartbeat_interval_sec", 30)),
            expires_at=self._parse_expiry(body["expires_at"]),
        )
        self._save_session(session)
        return session

    def refresh_session(self, session: ConnectorSession) -> ConnectorSession:
        resp = self.http.post(
            self._url("/api/v2/openclaw/connectors/refresh-session"),
            headers={"Authorization": f"Bearer {session.session_token}"},
            json={"ttl_hours": 24},
            timeout=self.timeout_sec,
        )
        resp.raise_for_status()
        body = resp.json()
        refreshed = ConnectorSession(
            session_token=body["session_token"],
            provider_id=body["provider_id"],
            connector_session_id=body["connector_session_id"],
            heartbeat_interval_sec=int(body.get("heartbeat_interval_sec", 30)),
            expires_at=self._parse_expiry(body["expires_at"]),
        )
        self._save_session(refreshed)
        return refreshed

    def heartbeat(self, session: ConnectorSession, status: str = "online") -> None:
        resp = self.http.post(
            self._url("/api/v2/openclaw/connectors/heartbeat"),
            headers={"Authorization": f"Bearer {session.session_token}"},
            json={"status": status},
            timeout=self.timeout_sec,
        )
        resp.raise_for_status()

    def claim_next(self, session: ConnectorSession, max_wait_seconds: int = 20) -> Optional[Dict[str, Any]]:
        resp = self.http.post(
            self._url("/api/v2/openclaw/connectors/requests/next"),
            headers={"Authorization": f"Bearer {session.session_token}"},
            json={"max_wait_seconds": max_wait_seconds},
            timeout=max(self.timeout_sec, max_wait_seconds + 5),
        )
        resp.raise_for_status()
        body = resp.json()
        return body.get("request")

    def complete(
        self,
        session: ConnectorSession,
        request_id: str,
        status: str,
        output_text: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost_usd: float,
        error_message: Optional[str] = None,
    ) -> None:
        payload = {
            "status": status,
            "output_text": output_text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
            "error_message": error_message,
        }
        resp = self.http.post(
            self._url(f"/api/v2/openclaw/connectors/requests/{request_id}/complete"),
            headers={"Authorization": f"Bearer {session.session_token}"},
            json=payload,
            timeout=self.timeout_sec,
        )
        resp.raise_for_status()

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    def _run_local_agent(self, message: str, request_payload: Dict[str, Any]) -> str:
        if not self.agent_cmd:
            return f"[AITalk Connector] {message}"

        env = os.environ.copy()
        env["OPENCLAW_MESSAGE"] = message
        env["OPENCLAW_PAYLOAD"] = json.dumps(request_payload)
        proc = subprocess.run(
            self.agent_cmd,
            shell=True,
            env=env,
            capture_output=True,
            text=True,
            timeout=90,
        )
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            raise RuntimeError(stderr or f"agent command failed with code {proc.returncode}")
        output = (proc.stdout or "").strip()
        return output or "[AITalk Connector] empty response"

    def run_loop(self, initial_session: ConnectorSession) -> None:
        session = initial_session
        print(f"[openclaw-skill] connected provider={session.provider_id} connector={self.connector_id}")
        next_heartbeat_at = 0.0

        while True:
            now = datetime.now(timezone.utc)
            if session.expires_at - now < timedelta(minutes=30):
                try:
                    session = self.refresh_session(session)
                    print("[openclaw-skill] session refreshed")
                except Exception as exc:
                    print(f"[openclaw-skill] refresh failed: {exc}")

            t = time.time()
            if t >= next_heartbeat_at:
                try:
                    self.heartbeat(session, status="online")
                except Exception as exc:
                    print(f"[openclaw-skill] heartbeat failed: {exc}")
                next_heartbeat_at = t + max(10, session.heartbeat_interval_sec)

            try:
                req = self.claim_next(session, max_wait_seconds=20)
            except Exception as exc:
                print(f"[openclaw-skill] claim-next failed: {exc}")
                time.sleep(3)
                continue

            if not req:
                continue

            request_id = req.get("request_id")
            payload = req.get("payload") or {}
            message = str(payload.get("message") or "")
            if not request_id:
                continue

            try:
                output = self._run_local_agent(message, payload)
                prompt_tokens = self._estimate_tokens(message)
                completion_tokens = self._estimate_tokens(output)
                total_tokens = prompt_tokens + completion_tokens
                self.complete(
                    session=session,
                    request_id=request_id,
                    status="success",
                    output_text=output,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost_usd=0.0,
                )
            except Exception as exc:
                err = str(exc)
                print(f"[openclaw-skill] request {request_id} failed: {err}")
                try:
                    self.complete(
                        session=session,
                        request_id=request_id,
                        status="failed",
                        output_text="",
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        cost_usd=0.0,
                        error_message=err,
                    )
                except Exception as inner_exc:
                    print(f"[openclaw-skill] complete failed: {inner_exc}")


def resolve_default_connector_id() -> str:
    hostname = socket.gethostname().split(".")[0]
    return f"agos-{hostname}-{uuid.uuid4().hex[:6]}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AITalk OpenClaw connector skill")
    parser.add_argument("--api-base", default=os.getenv("AITALK_API_BASE", "https://chat-api.agos.fun"))
    parser.add_argument("--match-code", default=os.getenv("AITALK_MATCH_CODE"))
    parser.add_argument("--connector-id", default=os.getenv("AITALK_CONNECTOR_ID", resolve_default_connector_id()))
    parser.add_argument(
        "--state-file",
        default=os.getenv("AITALK_STATE_FILE", str(Path.home() / ".aitalk" / "openclaw_connector_state.json")),
    )
    parser.add_argument("--timeout-sec", type=int, default=int(os.getenv("AITALK_HTTP_TIMEOUT", "20")))
    parser.add_argument(
        "--agent-cmd",
        default=os.getenv("AITALK_AGENT_CMD"),
        help="Optional command for local OpenClaw execution. OPENCLAW_MESSAGE env will be injected.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    connector = AITalkConnector(
        api_base=args.api_base,
        connector_id=args.connector_id,
        state_file=Path(args.state_file),
        timeout_sec=max(5, args.timeout_sec),
        agent_cmd=args.agent_cmd,
    )

    session = connector._load_session()
    if session is None:
        match_code = args.match_code
        if not match_code:
            match_code = input("Enter AITalk match code: ").strip()
        if not match_code:
            print("Missing match code")
            return 2
        try:
            session = connector.register_with_code(match_code)
            print("[openclaw-skill] register success")
        except Exception as exc:
            print(f"register failed: {exc}")
            return 1

    try:
        connector.run_loop(session)
    except KeyboardInterrupt:
        print("\n[openclaw-skill] stopped")
        return 0
    except Exception as exc:
        print(f"[openclaw-skill] fatal error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
