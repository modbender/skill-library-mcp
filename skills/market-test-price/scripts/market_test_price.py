"""
OKX DEX Market Price API Client
===============================
Production-ready Python client for the OKX DEX Market Price API (v6).

Usage:
    from dex_market_price import OKXDexMarketPriceClient

    client = OKXDexMarketPriceClient(
        api_key=os.environ["OKX_ACCESS_KEY"],
        secret_key=os.environ["OKX_SECRET_KEY"],
        passphrase=os.environ["OKX_PASSPHRASE"],
    )
    results = client.get_prices([
        {"chainIndex": "1", "tokenContractAddress": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
    ])
    for r in results:
        print(r.price, r.time)

Environment variables:
    OKX_ACCESS_KEY    - API key
    OKX_SECRET_KEY    - Secret key for HMAC signing
    OKX_PASSPHRASE    - Account passphrase
"""

import os
import json
import hmac
import hashlib
import base64
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

try:
    import requests
except ImportError:
    raise ImportError("Please install requests: pip install requests")


BASE_URL = "https://web3.okx.com"
PRICE_PATH = "/api/v6/dex/market/price"
MAX_BATCH_SIZE = 100


@dataclass
class PriceResult:
    chain_index: str
    token_contract_address: str
    time: str
    price: str

    @classmethod
    def from_api(cls, data: dict) -> "PriceResult":
        return cls(
            chain_index=data.get("chainIndex", ""),
            token_contract_address=data.get("tokenContractAddress", ""),
            time=data.get("time", "0"),
            price=data.get("price", "0"),
        )


class OKXDexMarketPriceClient:
    """Client for the OKX DEX Market Price API (batch token price)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        passphrase: Optional[str] = None,
        timeout: int = 30,
    ):
        # strip() 避免从文件/终端粘贴时带入换行导致 401
        self.api_key = (api_key or os.environ.get("OKX_ACCESS_KEY", "")).strip()
        self.secret_key = (secret_key or os.environ.get("OKX_SECRET_KEY", "")).strip()
        self.passphrase = (passphrase or os.environ.get("OKX_PASSPHRASE", "")).strip()
        self.timeout = timeout
        self.session = requests.Session()

        if not all([self.api_key, self.secret_key, self.passphrase]):
            raise ValueError(
                "Missing credentials. Set OKX_ACCESS_KEY, OKX_SECRET_KEY, "
                "OKX_PASSPHRASE env vars or pass them to the constructor."
            )

    def _sign(self, timestamp: str, method: str, request_path: str, body: str) -> str:
        """Generate HMAC-SHA256 signature (POST: prehash includes body)."""
        prehash = timestamp + method + request_path + body
        mac = hmac.new(
            self.secret_key.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(mac.digest()).decode("utf-8")

    def _headers(self, body: str) -> dict:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        if os.environ.get("OKX_DEBUG"):
            prehash = timestamp + "POST" + PRICE_PATH + body
            print("[OKX_DEBUG] timestamp:", timestamp, "| prehash length:", len(prehash), "| body:", body[:80] + "..." if len(body) > 80 else body)
        signature = self._sign(timestamp, "POST", PRICE_PATH, body)
        return {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-TIMESTAMP": timestamp,
        }

    @staticmethod
    def _validate_item(chain_index: str, token_contract_address: str) -> None:
        """Basic address format validation."""
        if chain_index == "501":  # Solana
            if not re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", token_contract_address):
                raise ValueError(f"Invalid Solana address: {token_contract_address}")
        else:
            if not re.match(r"^0x[0-9a-f]{40}$", token_contract_address):
                raise ValueError(f"Invalid EVM address (lowercase hex): {token_contract_address}")

    def get_prices(
        self,
        token_param_list: list[dict],
    ) -> list[PriceResult]:
        """
        Batch fetch token prices.

        Args:
            token_param_list: List of {"chainIndex": str, "tokenContractAddress": str}, 1–100 items.

        Returns:
            List of PriceResult (chainIndex, tokenContractAddress, time, price).

        Raises:
            ValueError: Invalid params or batch size.
            Exception: API error.
        """
        if not token_param_list or len(token_param_list) > MAX_BATCH_SIZE:
            raise ValueError(
                f"token_param_list must have 1–{MAX_BATCH_SIZE} items, got {len(token_param_list)}"
            )

        for item in token_param_list:
            ci = item.get("chainIndex")
            addr = item.get("tokenContractAddress")
            if not ci or not addr:
                raise ValueError("Each item must have chainIndex and tokenContractAddress")
            self._validate_item(ci, addr)

        # 与签名一致：无空格、key 按字母序，和 OKX 服务端期望一致
        body = json.dumps(token_param_list, separators=(",", ":"), sort_keys=True)

        headers = self._headers(body)
        url = BASE_URL + PRICE_PATH
        resp = self.session.post(url, headers=headers, data=body, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "0":
            raise Exception(
                f"OKX API error (code {data.get('code')}): {data.get('msg', 'Unknown error')}"
            )

        raw_list = data.get("data") or []
        return [PriceResult.from_api(item) for item in raw_list]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OKX DEX Market Price CLI")
    parser.add_argument("--chain", default="1", help="Chain index (default: 1 = Ethereum)")
    parser.add_argument("--token", required=True, help="Token contract address")
    args = parser.parse_args()

    client = OKXDexMarketPriceClient()
    results = client.get_prices([
        {"chainIndex": args.chain, "tokenContractAddress": args.token},
    ])
    for r in results:
        print(f"price={r.price} time={r.time} chainIndex={r.chain_index} token={r.token_contract_address}")
