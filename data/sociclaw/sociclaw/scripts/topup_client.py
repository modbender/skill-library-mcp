"""
SociClaw Credits topup client (txHash flow).

Flow:
- start: request deposit address + exact amount
- claim: submit txHash
- status: poll current session status
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Dict, Optional

import requests

from .http_retry import request_with_retry
from .validators import validate_tx_hash


@dataclass(frozen=True)
class TopupStartResult:
    session_id: str
    deposit_address: str
    amount_usdc_exact: str
    raw: Dict[str, Any]


class TopupClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: Optional[str] = None,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("Topup API key is required")

        url = (base_url or os.getenv("SOCICLAW_IMAGE_API_BASE_URL") or "").strip().rstrip("/")
        if not url:
            raise ValueError("Topup base_url is required (or set SOCICLAW_IMAGE_API_BASE_URL)")

        self.base_url = url
        self.api_key = api_key.strip()
        self.timeout_seconds = int(timeout_seconds)
        self.max_retries = int(max_retries)
        self.backoff_base_seconds = 0.5
        self.session = session or requests.Session()

    def start_topup(self, *, expected_amount_usd: float, chain: str = "base", token_symbol: str = "USDC") -> TopupStartResult:
        payload = {
            "expectedAmountUsd": float(expected_amount_usd),
            "chain": chain,
            "tokenSymbol": token_symbol,
        }
        data = self._post("/api/v1?path=account/topup/start", payload)

        session_id = str(data.get("sessionId") or data.get("session_id") or "")
        deposit_address = str(data.get("depositAddress") or data.get("deposit_address") or "")
        amount_usdc_exact = str(data.get("amountUsdcExact") or data.get("amount_usdc_exact") or "")
        if not session_id or not deposit_address or not amount_usdc_exact:
            raise RuntimeError(f"Invalid topup/start response: {data}")

        return TopupStartResult(
            session_id=session_id,
            deposit_address=deposit_address,
            amount_usdc_exact=amount_usdc_exact,
            raw=data,
        )

    def claim_topup(self, *, session_id: str, tx_hash: str) -> Dict[str, Any]:
        payload = {"sessionId": str(session_id).strip(), "txHash": validate_tx_hash(tx_hash)}
        return self._post("/api/v1?path=account/topup/claim", payload)

    def status_topup(self, *, session_id: str) -> Dict[str, Any]:
        path = f"/api/v1?path=account/topup/status&sessionId={requests.utils.quote(str(session_id), safe='')}"
        return self._get(path)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = request_with_retry(
            session=self.session,
            method="POST",
            url=f"{self.base_url}{path}",
            headers=self._headers(),
            json=payload,
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str) -> Dict[str, Any]:
        resp = request_with_retry(
            session=self.session,
            method="GET",
            url=f"{self.base_url}{path}",
            headers=self._headers(),
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
            backoff_base_seconds=self.backoff_base_seconds,
        )
        resp.raise_for_status()
        return resp.json()
