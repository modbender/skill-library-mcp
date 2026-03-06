from __future__ import annotations
"""
Langfuse OTEL collector — fetches traces, observations, and scores via REST API.
Returns structured dicts; no interpretation.

Env vars:
  LANGFUSE_PUBLIC_KEY   Langfuse public key
  LANGFUSE_SECRET_KEY   Langfuse secret key
  LANGFUSE_BASE_URL     Langfuse server URL (default: http://localhost:3100)

Note: some self-hosted Langfuse versions don't support fromTimestamp query params —
we fetch recent items and filter client-side by timestamp.
"""
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional


def _auth(public_key: str = '', secret_key: str = '') -> tuple:
    pk = public_key or os.environ.get('LANGFUSE_PUBLIC_KEY', '')
    sk = secret_key or os.environ.get('LANGFUSE_SECRET_KEY', '')
    return (pk, sk)


def _since_ts(days_back: int) -> float:
    return (datetime.now(timezone.utc) - timedelta(days=days_back)).timestamp()


def _parse_ts(s: Optional[str]) -> float:
    if not s:
        return 0.0
    try:
        s = s.replace('Z', '+00:00')
        return datetime.fromisoformat(s).timestamp()
    except Exception:
        return 0.0


def fetch_traces(days_back: int = 1, base_url: str = 'http://localhost:3100',
                 limit: int = 100, public_key: str = '', secret_key: str = '') -> list[dict]:
    resp = requests.get(
        f'{base_url}/api/public/traces',
        auth=_auth(public_key, secret_key),
        params={'limit': limit},
        timeout=15
    )
    resp.raise_for_status()
    cutoff = _since_ts(days_back)
    return [
        t for t in resp.json().get('data', [])
        if _parse_ts(t.get('timestamp') or t.get('createdAt')) >= cutoff
    ]


def fetch_observations(days_back: int = 1, base_url: str = 'http://localhost:3100',
                       limit: int = 100, public_key: str = '', secret_key: str = '') -> list[dict]:
    resp = requests.get(
        f'{base_url}/api/public/observations',
        auth=_auth(public_key, secret_key),
        params={'limit': limit, 'type': 'GENERATION'},
        timeout=15
    )
    resp.raise_for_status()
    cutoff = _since_ts(days_back)
    return [
        o for o in resp.json().get('data', [])
        if _parse_ts(o.get('startTime') or o.get('createdAt')) >= cutoff
    ]


def fetch_scores(days_back: int = 1, base_url: str = 'http://localhost:3100',
                 limit: int = 100, public_key: str = '', secret_key: str = '') -> list[dict]:
    resp = requests.get(
        f'{base_url}/api/public/scores',
        auth=_auth(public_key, secret_key),
        params={'limit': limit},
        timeout=15
    )
    resp.raise_for_status()
    cutoff = _since_ts(days_back)
    return [
        s for s in resp.json().get('data', [])
        if _parse_ts(s.get('timestamp') or s.get('createdAt')) >= cutoff
    ]


def build_experiment_summary(days_back: int = 7, base_url: str = 'http://localhost:3100',
                              public_key: str = '', secret_key: str = '') -> dict:
    """Aggregate experiment data: per-model score distributions, run counts, latency stats."""
    obs = fetch_observations(days_back=days_back, base_url=base_url,
                             public_key=public_key, secret_key=secret_key)
    scores = fetch_scores(days_back=days_back, base_url=base_url,
                          public_key=public_key, secret_key=secret_key)

    by_model: dict[str, list] = {}
    for o in obs:
        model = o.get('model', 'unknown')
        by_model.setdefault(model, []).append(o)

    model_stats = {}
    for model, runs in by_model.items():
        latencies = [r['latency'] for r in runs if r.get('latency') is not None]
        prompt_tokens = [r.get('promptTokens', 0) or 0 for r in runs]
        completion_tokens = [r.get('completionTokens', 0) or 0 for r in runs]
        model_stats[model] = {
            'run_count': len(runs),
            'latency_ms': _describe(latencies),
            'prompt_tokens': _describe(prompt_tokens),
            'completion_tokens': _describe(completion_tokens),
        }

    score_groups: dict[str, list] = {}
    for s in scores:
        name = s.get('name', 'unknown')
        score_groups.setdefault(name, []).append(s.get('value'))

    return {
        'period_days': days_back,
        'total_observations': len(obs),
        'total_scores': len(scores),
        'model_stats': model_stats,
        'score_stats': {name: _describe(vals) for name, vals in score_groups.items()},
    }


def _describe(values: list) -> dict:
    vals = [v for v in values if v is not None]
    if not vals:
        return {'count': 0, 'note': 'no data'}
    vals_sorted = sorted(vals)
    n = len(vals_sorted)
    mean = sum(vals_sorted) / n
    variance = sum((x - mean) ** 2 for x in vals_sorted) / n if n > 1 else 0
    return {
        'count': n,
        'mean': round(mean, 4),
        'median': _percentile(vals_sorted, 50),
        'p95': _percentile(vals_sorted, 95),
        'p99': _percentile(vals_sorted, 99),
        'std': round(variance ** 0.5, 4),
        'min': round(vals_sorted[0], 4),
        'max': round(vals_sorted[-1], 4),
    }


def _percentile(sorted_vals: list, p: int) -> float:
    if not sorted_vals:
        return 0.0
    idx = (p / 100) * (len(sorted_vals) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    return round(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo), 4)
