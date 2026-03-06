"""Per-API rate limiting for FinClaw."""

import time
import threading

_locks = {}
_call_times = {}
_global_lock = threading.Lock()

RATE_LIMITS = {
    "finnhub": 60, "alpha_vantage": 5, "fmp": 250,
    "fred": 120, "binance": 1200, "exchangerate": 60,
    "yfinance": 30, "coingecko": 10,
}


def wait_if_needed(api_name: str):
    limit = RATE_LIMITS.get(api_name, 60)
    window = 60.0
    with _global_lock:
        if api_name not in _locks:
            _locks[api_name] = threading.Lock()
            _call_times[api_name] = []
    with _locks[api_name]:
        now = time.time()
        _call_times[api_name] = [t for t in _call_times[api_name] if now - t < window]
        if len(_call_times[api_name]) >= limit:
            oldest = _call_times[api_name][0]
            sleep_time = window - (now - oldest) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
        _call_times[api_name].append(time.time())
