"""
Provisioning gateway client (recommended for production).

Instead of calling the image-provider provisioning API directly (which requires a highly
privileged admin secret), call YOUR backend (e.g. Vercel) which keeps that secret
server-side.

Expected gateway behavior:
- Accepts POST JSON:
  { "provider": "...", "provider_user_id": "...", "create_api_key": true }
- Returns JSON (schema depends on upstream), typically including:
  api_key and/or wallet_address (top-level or nested under "data")

Deploy this route in your backend (e.g. Vercel function):
- /api/sociclaw/provision
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .http_retry import request_with_retry
from .validators import validate_provider, validate_provider_user_id


@dataclass(frozen=True)
class ProvisionResult:
    provider: str
    provider_user_id: str
    api_key: Optional[str]
    wallet_address: Optional[str]
    raw: Dict[str, Any]


class SociClawProvisioningGatewayClient:
    def __init__(
        self,
        *,
        url: str,
        internal_token: Optional[str] = None,
        timeout_seconds: int = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not url or not url.strip():
            raise ValueError("url is required")
        self.url = url.strip()
        self.internal_token = internal_token.strip() if internal_token else None
        self.timeout_seconds = int(timeout_seconds)
        self.max_retries = 3
        self.backoff_base_seconds = 0.5
        self.session = session or requests.Session()

    def provision(
        self,
        *,
        provider: str,
        provider_user_id: str,
        create_api_key: bool = True,
    ) -> ProvisionResult:
        provider = validate_provider(provider)
        provider_user_id = validate_provider_user_id(provider_user_id)

        payload = {
            "provider": provider,
            "provider_user_id": str(provider_user_id),
            "create_api_key": bool(create_api_key),
        }

        headers = {"Content-Type": "application/json"}
        if self.internal_token:
            headers["Authorization"] = f"Bearer {self.internal_token}"

        resp = request_with_retry(
            session=self.session,
            method="POST",
            url=self.url,
            headers=headers,
            json=payload,
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )
        resp.raise_for_status()
        data = resp.json()

        nested = data.get("data") if isinstance(data.get("data"), dict) else {}
        # Contract order:
        # 1) data.api_key
        # 2) api_key
        # 3) data.image_api_key
        # 4) image_api_key
        api_key = (
            nested.get("api_key")
            or data.get("api_key")
            or nested.get("image_api_key")
            or data.get("image_api_key")
        )
        if not api_key:
            for container in (data, nested):
                for k, v in container.items():
                    if k.endswith("_api_key") and v:
                        api_key = v
                        break
                if api_key:
                    break
        wallet_address = (
            data.get("wallet_address")
            or data.get("wallet")
            or (data.get("data") or {}).get("wallet_address")
            or (data.get("data") or {}).get("wallet")
        )

        return ProvisionResult(
            provider=provider,
            provider_user_id=str(provider_user_id),
            api_key=str(api_key) if api_key else None,
            wallet_address=str(wallet_address) if wallet_address else None,
            raw=data,
        )
