"""
OKX DEX Aggregator Quote Client
================================
A production-ready Python client for the OKX DEX Aggregator Quote API (v6).

Usage:
    from okx_dex_quote import OKXDexQuoteClient

    client = OKXDexQuoteClient(
        api_key=os.environ["OKX_ACCESS_KEY"],
        secret_key=os.environ["OKX_SECRET_KEY"],
        passphrase=os.environ["OKX_PASSPHRASE"],
    )

    result = client.get_quote(
        chain_index="1",
        from_token="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        to_token="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        human_amount=1.0,
        from_decimals=18,
    )
    print(result.summary())

Environment variables:
    OKX_ACCESS_KEY    - API key
    OKX_SECRET_KEY    - Secret key for HMAC signing
    OKX_PASSPHRASE    - Account passphrase
"""

import os
import hmac
import hashlib
import base64
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    raise ImportError("Please install requests: pip install requests")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://web3.okx.com"
QUOTE_PATH = "/api/v6/dex/aggregator/quote"

NATIVE_TOKEN = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

CHAIN_NAMES = {
    "1": "Ethereum",
    "56": "BSC",
    "137": "Polygon",
    "42161": "Arbitrum",
    "10": "Optimism",
    "43114": "Avalanche",
    "8453": "Base",
    "501": "Solana",
    "130": "Unichain",
}

# Chains that support exactOut mode
EXACT_OUT_CHAINS = {"1", "8453", "56", "42161"}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TokenInfo:
    symbol: str
    address: str
    decimal: int
    unit_price: Optional[str]
    is_honeypot: bool
    tax_rate: float

    @classmethod
    def from_api(cls, data: dict) -> "TokenInfo":
        return cls(
            symbol=data.get("tokenSymbol", "UNKNOWN"),
            address=data.get("tokenContractAddress", ""),
            decimal=int(data.get("decimal", "18")),
            unit_price=data.get("tokenUnitPrice"),
            is_honeypot=data.get("isHoneyPot", False),
            tax_rate=float(data.get("taxRate", "0")),
        )


@dataclass
class DexRoute:
    dex_name: str
    percent: str
    from_symbol: str
    to_symbol: str

    @classmethod
    def from_api(cls, data: dict) -> "DexRoute":
        return cls(
            dex_name=data.get("dexProtocol", {}).get("dexName", "Unknown"),
            percent=data.get("dexProtocol", {}).get("percent", "0"),
            from_symbol=data.get("fromToken", {}).get("tokenSymbol", "?"),
            to_symbol=data.get("toToken", {}).get("tokenSymbol", "?"),
        )


@dataclass
class QuoteResult:
    chain_index: str
    from_token: TokenInfo
    to_token: TokenInfo
    from_amount_raw: str
    to_amount_raw: str
    trade_fee_usd: str
    estimate_gas: str
    price_impact_percent: Optional[str]
    routes: list[DexRoute] = field(default_factory=list)
    swap_mode: str = "exactIn"
    raw_response: dict = field(default_factory=dict, repr=False)

    @property
    def from_amount_human(self) -> float:
        return int(self.from_amount_raw) / (10 ** self.from_token.decimal)

    @property
    def to_amount_human(self) -> float:
        return int(self.to_amount_raw) / (10 ** self.to_token.decimal)

    @property
    def exchange_rate(self) -> float:
        if self.from_amount_human == 0:
            return 0.0
        return self.to_amount_human / self.from_amount_human

    @property
    def has_honeypot_risk(self) -> bool:
        return self.from_token.is_honeypot or self.to_token.is_honeypot

    @property
    def has_tax(self) -> bool:
        return self.from_token.tax_rate > 0 or self.to_token.tax_rate > 0

    def summary(self) -> str:
        lines = []
        chain_name = CHAIN_NAMES.get(self.chain_index, f"Chain {self.chain_index}")
        lines.append(f"=== OKX DEX Quote ({chain_name}) ===")
        lines.append(f"Swap: {self.from_amount_human:,.6f} {self.from_token.symbol} -> "
                      f"{self.to_amount_human:,.6f} {self.to_token.symbol}")
        lines.append(f"Rate: 1 {self.from_token.symbol} = {self.exchange_rate:,.6f} {self.to_token.symbol}")
        lines.append(f"Mode: {self.swap_mode}")

        if self.price_impact_percent:
            impact = float(self.price_impact_percent)
            warning = " ⚠️ HIGH IMPACT" if impact < -3 else ""
            lines.append(f"Price Impact: {self.price_impact_percent}%{warning}")
        else:
            lines.append("Price Impact: N/A (could not calculate)")

        lines.append(f"Gas Fee (USD): ${self.trade_fee_usd}")

        if self.has_honeypot_risk:
            lines.append("🚨 HONEYPOT WARNING: One or more tokens flagged as potential scam!")

        if self.has_tax:
            if self.from_token.tax_rate > 0:
                lines.append(f"Sell Tax ({self.from_token.symbol}): {self.from_token.tax_rate * 100:.2f}%")
            if self.to_token.tax_rate > 0:
                lines.append(f"Buy Tax ({self.to_token.symbol}): {self.to_token.tax_rate * 100:.2f}%")

        if self.routes:
            lines.append("Routing:")
            for r in self.routes:
                lines.append(f"  {r.percent}% {r.from_symbol} -> {r.to_symbol} via {r.dex_name}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class OKXDexQuoteClient:
    """Client for the OKX DEX Aggregator Quote API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        passphrase: Optional[str] = None,
        timeout: int = 30,
    ):
        self.api_key = api_key or os.environ.get("OKX_ACCESS_KEY", "")
        self.secret_key = secret_key or os.environ.get("OKX_SECRET_KEY", "")
        self.passphrase = passphrase or os.environ.get("OKX_PASSPHRASE", "")
        self.timeout = timeout
        self.session = requests.Session()

        if not all([self.api_key, self.secret_key, self.passphrase]):
            raise ValueError(
                "Missing credentials. Set OKX_ACCESS_KEY, OKX_SECRET_KEY, "
                "OKX_PASSPHRASE env vars or pass them to the constructor."
            )

    def _sign(self, timestamp: str, method: str, request_path: str) -> str:
        """Generate HMAC-SHA256 signature."""
        prehash = timestamp + method + request_path
        mac = hmac.new(
            self.secret_key.encode("utf-8"),
            prehash.encode("utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(mac.digest()).decode("utf-8")

    def _headers(self, request_path: str) -> dict:
        """Build authenticated headers."""
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )[:-3] + "Z"
        signature = self._sign(timestamp, "GET", request_path)
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-TIMESTAMP": timestamp,
        }

    @staticmethod
    def _validate_address(address: str, chain_index: str) -> None:
        """Basic address format validation."""
        if chain_index == "501":  # Solana uses base58
            if not re.match(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$", address):
                if address != NATIVE_TOKEN:
                    raise ValueError(f"Invalid Solana address: {address}")
        else:  # EVM chains use hex
            if not re.match(r"^0x[0-9a-fA-F]{40}$", address):
                raise ValueError(f"Invalid EVM address: {address}")

    @staticmethod
    def to_raw_amount(human_amount: float, decimals: int) -> str:
        """Convert human-readable amount to raw amount string.

        Uses integer math to avoid floating-point precision issues.
        """
        # Handle decimal amounts by splitting on '.'
        amount_str = f"{human_amount:.{decimals}f}"
        if "." in amount_str:
            integer_part, decimal_part = amount_str.split(".")
            decimal_part = decimal_part[:decimals].ljust(decimals, "0")
            raw = int(integer_part) * (10 ** decimals) + int(decimal_part)
        else:
            raw = int(amount_str) * (10 ** decimals)
        return str(raw)

    def get_quote(
        self,
        chain_index: str,
        from_token: str,
        to_token: str,
        human_amount: Optional[float] = None,
        raw_amount: Optional[str] = None,
        from_decimals: int = 18,
        swap_mode: str = "exactIn",
        dex_ids: Optional[str] = None,
        direct_route: Optional[bool] = None,
        price_impact_protection: Optional[str] = None,
        fee_percent: Optional[str] = None,
    ) -> QuoteResult:
        """Fetch a swap quote from OKX DEX Aggregator.

        Args:
            chain_index: Chain ID (e.g., "1" for Ethereum).
            from_token: Sell token contract address.
            to_token: Buy token contract address.
            human_amount: Amount in human-readable form (e.g., 1.5 for 1.5 ETH).
                         Requires from_decimals to be set correctly.
            raw_amount: Amount already in raw units (overrides human_amount).
            from_decimals: Decimal places for the from_token (default 18).
            swap_mode: "exactIn" or "exactOut".
            dex_ids: Comma-separated DEX IDs to restrict routing.
            direct_route: Force single-pool routing (Solana only).
            price_impact_protection: Max allowed price impact percent (0-100).
            fee_percent: Commission fee percentage for integrators.

        Returns:
            QuoteResult with parsed quote data.

        Raises:
            ValueError: Invalid parameters.
            Exception: API error.
        """
        # Validate inputs
        if swap_mode == "exactOut" and chain_index not in EXACT_OUT_CHAINS:
            raise ValueError(
                f"exactOut not supported on chain {chain_index}. "
                f"Supported: {', '.join(EXACT_OUT_CHAINS)}"
            )

        self._validate_address(from_token, chain_index)
        self._validate_address(to_token, chain_index)

        # Determine amount
        if raw_amount:
            amount = raw_amount
        elif human_amount is not None:
            amount = self.to_raw_amount(human_amount, from_decimals)
        else:
            raise ValueError("Provide either human_amount or raw_amount")

        # Build query parameters
        params = {
            "chainIndex": chain_index,
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "amount": amount,
            "swapMode": swap_mode,
        }

        if dex_ids:
            params["dexIds"] = dex_ids
        if direct_route is not None:
            params["directRoute"] = str(direct_route).lower()
        if price_impact_protection:
            params["priceImpactProtectionPercent"] = price_impact_protection
        if fee_percent:
            params["feePercent"] = fee_percent

        query_string = urlencode(params)
        request_path = f"{QUOTE_PATH}?{query_string}"

        # Make request
        headers = self._headers(request_path)
        url = f"{BASE_URL}{request_path}"

        resp = self.session.get(url, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != "0":
            raise Exception(f"OKX API error (code {data.get('code')}): {data.get('msg', 'Unknown error')}")

        if not data.get("data"):
            raise Exception("OKX API returned empty data — no quote available for this pair/amount.")

        quote_data = data["data"][0]

        # Parse response
        routes = [DexRoute.from_api(r) for r in quote_data.get("dexRouterList", [])]

        return QuoteResult(
            chain_index=quote_data.get("chainIndex", chain_index),
            from_token=TokenInfo.from_api(quote_data.get("fromToken", {})),
            to_token=TokenInfo.from_api(quote_data.get("toToken", {})),
            from_amount_raw=quote_data.get("fromTokenAmount", amount),
            to_amount_raw=quote_data.get("toTokenAmount", "0"),
            trade_fee_usd=quote_data.get("tradeFee", "0"),
            estimate_gas=quote_data.get("estimateGasFee", "0"),
            price_impact_percent=quote_data.get("priceImpactPercent"),
            routes=routes,
            swap_mode=quote_data.get("swapMode", swap_mode),
            raw_response=quote_data,
        )


# ---------------------------------------------------------------------------
# CLI usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OKX DEX Quote CLI")
    parser.add_argument("--chain", default="1", help="Chain index (default: 1 = Ethereum)")
    parser.add_argument("--from", dest="from_token", required=True, help="From token address")
    parser.add_argument("--to", dest="to_token", required=True, help="To token address")
    parser.add_argument("--amount", type=float, required=True, help="Human-readable amount")
    parser.add_argument("--decimals", type=int, default=18, help="From token decimals (default: 18)")
    parser.add_argument("--mode", default="exactIn", choices=["exactIn", "exactOut"])

    args = parser.parse_args()

    client = OKXDexQuoteClient()
    result = client.get_quote(
        chain_index=args.chain,
        from_token=args.from_token,
        to_token=args.to_token,
        human_amount=args.amount,
        from_decimals=args.decimals,
        swap_mode=args.mode,
    )
    print(result.summary())
