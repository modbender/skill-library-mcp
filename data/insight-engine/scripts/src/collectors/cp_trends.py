"""
Control Plane trends collector — fetches model promotion tracks and history.
Gracefully degrades if CP is unavailable.

Env vars:
  CP_API_URL    Base URL for control plane API (default: http://localhost:8765)
"""
from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


def collect_cp_trends(api_url: str = '', timeout: int = 5) -> dict[str, Any]:
    """Fetch trend and history data from the Hybrid Control Plane.

    Returns a dict with on_promotion_track, total_runs, recent_events.
    Returns empty dict if CP is unavailable.
    """
    base_url = api_url or os.environ.get('CP_API_URL', 'http://localhost:8765')

    try:
        r = requests.get(f'{base_url}/trends', timeout=timeout)
        r.raise_for_status()
        trends_data = r.json()

        on_promotion_track = []
        for task, models in trends_data.get('trends', {}).items():
            for model, stats in models.items():
                if stats.get('runs_to_promotion') is not None:
                    on_promotion_track.append({
                        'task': task,
                        'model': model,
                        'mean': stats['mean'],
                        'n': stats['n'],
                        'runs_to_promotion': stats['runs_to_promotion'],
                        'trend': stats['trend'],
                    })
        on_promotion_track.sort(key=lambda x: x['runs_to_promotion'])

        r2 = requests.get(f'{base_url}/history', params={'limit': 20}, timeout=timeout)
        r2.raise_for_status()
        history_data = r2.json()

        return {
            'on_promotion_track': on_promotion_track,
            'total_runs': trends_data.get('total_runs', 0),
            'recent_events': history_data.get('events', []),
            'total_history_events': history_data.get('total', 0),
        }
    except Exception as e:
        logger.warning('CP trends collection failed (graceful degradation): %s', e)
        return {}
