#!/usr/bin/env python3
"""Minimal Alpha Vantage client with throttle-aware retries."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict


BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageError(RuntimeError):
    pass


class AlphaVantageClient:
    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 20.0,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        backoff_cap: float = 20.0,
    ) -> None:
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            raise AlphaVantageError(
                "Missing API key. Set ALPHAVANTAGE_API_KEY or pass --apikey."
            )
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap

    def query(self, function: str, **params: str) -> Dict[str, Any]:
        query_params = {"function": function, "apikey": self.api_key, **params}
        url = f"{BASE_URL}?{urllib.parse.urlencode(query_params)}"

        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                    status = getattr(resp, "status", 200)
                    body = resp.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                status = exc.code
                body = exc.read().decode("utf-8", errors="replace")
                if self._should_retry_http(status) and attempt < self.max_retries:
                    self._sleep_with_backoff(attempt)
                    continue
                raise AlphaVantageError(f"HTTP {status}: {body[:300]}") from exc
            except urllib.error.URLError as exc:
                if attempt < self.max_retries:
                    self._sleep_with_backoff(attempt)
                    continue
                raise AlphaVantageError(f"Network error: {exc}") from exc

            if status < 200 or status >= 300:
                if self._should_retry_http(status) and attempt < self.max_retries:
                    self._sleep_with_backoff(attempt)
                    continue
                raise AlphaVantageError(f"HTTP {status}: {body[:300]}")

            try:
                payload: Dict[str, Any] = json.loads(body)
            except json.JSONDecodeError as exc:
                raise AlphaVantageError("Non-JSON response from Alpha Vantage") from exc

            # "Note" commonly indicates throttling/temporary quota exceedance.
            if "Note" in payload:
                if attempt < self.max_retries:
                    self._sleep_with_backoff(attempt)
                    continue
                raise AlphaVantageError(payload["Note"])

            if "Error Message" in payload:
                raise AlphaVantageError(payload["Error Message"])

            return payload

        raise AlphaVantageError("Request failed after retries")

    @staticmethod
    def _should_retry_http(status: int) -> bool:
        return status in {408, 425, 429, 500, 502, 503, 504}

    def _sleep_with_backoff(self, attempt: int) -> None:
        raw = min(self.backoff_cap, self.backoff_base * (2**attempt))
        jitter = random.uniform(0, raw * 0.25)
        time.sleep(raw + jitter)


def _parse_params(raw_params: list[str]) -> Dict[str, str]:
    params: Dict[str, str] = {}
    for item in raw_params:
        if "=" not in item:
            raise AlphaVantageError(f"Invalid param '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise AlphaVantageError(f"Invalid param '{item}'. Empty key.")
        params[key] = value.strip()
    return params


def main() -> int:
    parser = argparse.ArgumentParser(description="Alpha Vantage API client")
    parser.add_argument("--function", required=True, help="Alpha Vantage function name")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Query parameter in key=value form (repeatable)",
    )
    parser.add_argument("--apikey", help="API key (default: ALPHAVANTAGE_API_KEY)")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON output (no indentation)",
    )
    args = parser.parse_args()

    try:
        params = _parse_params(args.param)
        client = AlphaVantageClient(
            api_key=args.apikey,
            timeout=args.timeout,
            max_retries=args.retries,
        )
        payload = client.query(args.function, **params)
    except AlphaVantageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.compact:
        print(json.dumps(payload, separators=(",", ":"), sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
