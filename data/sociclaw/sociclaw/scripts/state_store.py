"""
Tiny local state store for SociClaw (MVP).

Why:
- We need somewhere to keep per-user provisioned credentials returned by the
  configured image provider
  (API key, wallet address) without hardcoding them into env vars.
- OpenClaw will likely provide a proper config store; for now we keep it simple.

Security:
- This file may contain API keys. It defaults to `.tmp/` which is gitignored.
- Do not commit state files or print full keys to logs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_state_path() -> Path:
    # repo_root/sociclaw/scripts/state_store.py -> repo_root
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / ".tmp" / "sociclaw_state.json"


def user_key(*, provider: str, provider_user_id: str) -> str:
    return f"{provider}:{provider_user_id}"


@dataclass
class UserState:
    provider: str
    provider_user_id: str
    image_api_key: Optional[str] = None
    wallet_address: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class StateStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or default_state_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, UserState]:
        if not self.path.exists():
            return {}

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        users = raw.get("users", {})
        out: Dict[str, UserState] = {}
        for k, v in users.items():
            payload = dict(v)
            # Backward compatibility: migrate any legacy `*_api_key` field on read.
            if "image_api_key" not in payload:
                for key_name, value in payload.items():
                    if key_name.endswith("_api_key") and value:
                        payload["image_api_key"] = value
                        break
            for key_name in list(payload.keys()):
                if key_name.endswith("_api_key") and key_name != "image_api_key":
                    payload.pop(key_name, None)
            out[k] = UserState(**payload)
        return out

    def save(self, users: Dict[str, UserState]) -> None:
        payload = {
            "version": 1,
            "updated_at": _utc_now_iso(),
            "users": {k: asdict(v) for k, v in users.items()},
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def upsert_user(
        self,
        *,
        provider: str,
        provider_user_id: str,
        image_api_key: Optional[str] = None,
        wallet_address: Optional[str] = None,
    ) -> UserState:
        key = user_key(provider=provider, provider_user_id=str(provider_user_id))
        users = self.load()

        now = _utc_now_iso()
        existing = users.get(key)
        if existing is None:
            existing = UserState(
                provider=provider,
                provider_user_id=str(provider_user_id),
                created_at=now,
            )

        if image_api_key is not None:
            existing.image_api_key = image_api_key
        if wallet_address is not None:
            existing.wallet_address = wallet_address

        existing.updated_at = now
        users[key] = existing
        self.save(users)
        return existing

    def get_user(self, *, provider: str, provider_user_id: str) -> Optional[UserState]:
        key = user_key(provider=provider, provider_user_id=str(provider_user_id))
        return self.load().get(key)
