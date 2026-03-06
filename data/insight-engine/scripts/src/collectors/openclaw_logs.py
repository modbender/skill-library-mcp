from __future__ import annotations
"""
OpenClaw/gateway log collector — parses daily log files and memory markdown files.
Extracts model calls, token counts. No interpretation.

Env vars:
  OPENCLAW_LOG_DIR    Directory with daily log files (default: /tmp/openclaw)
  OPENCLAW_MEMORY_DIR Directory with daily memory .md files (default: ~/.openclaw/memory)
"""
import glob
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Optional

_MODEL_RE = re.compile(r'model["\s:=]+([a-z0-9\-/_\.]+)', re.IGNORECASE)
_TOKEN_RE = re.compile(
    r'tokens?["\s:=]+\{?"?input"?["\s:=]+(\d+)[,\s]+"?output"?["\s:=]+(\d+)',
    re.IGNORECASE
)
_COST_RE = re.compile(r'cost["\s:=]+([0-9.]+)', re.IGNORECASE)
_SESSION_RE = re.compile(r'session["\s:=]+([a-z0-9\-]+)', re.IGNORECASE)


def parse_gateway_log(log_path: str, date_filter: Optional[date] = None) -> list[dict]:
    """Parse a gateway log file into structured events."""
    events = []
    if not os.path.exists(log_path):
        return events
    with open(log_path, 'r', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = _try_json_parse(line) or _try_regex_parse(line)
            if event:
                if date_filter is None or event.get('date') == str(date_filter):
                    events.append(event)
    return events


def parse_daily_log(log_dir: Optional[str] = None, target_date: Optional[date] = None) -> list[dict]:
    """Parse the daily log file for a given date."""
    if target_date is None:
        target_date = date.today()
    if log_dir is None:
        log_dir = os.environ.get('OPENCLAW_LOG_DIR', '/tmp/openclaw')
    pattern = os.path.join(log_dir, f'openclaw-{target_date}.log')
    files = glob.glob(pattern)
    if not files:
        return []
    return parse_gateway_log(files[0])


def read_memory_file(memory_dir: Optional[str] = None, target_date: Optional[date] = None) -> Optional[str]:
    """Read the daily memory markdown file."""
    if target_date is None:
        target_date = date.today()
    if memory_dir is None:
        memory_dir = os.environ.get(
            'OPENCLAW_MEMORY_DIR',
            os.path.join(os.path.expanduser('~'), '.openclaw', 'memory')
        )
    path = Path(memory_dir) / f'{target_date}.md'
    if path.exists():
        return path.read_text(errors='replace')
    return None


def aggregate_log_events(events: list[dict]) -> dict:
    """Aggregate log events into summary statistics. Pure Python — no LLM."""
    if not events:
        return {'total_events': 0, 'note': 'no log events found for period'}

    by_model: dict[str, dict] = {}
    total_input = total_output = 0
    total_cost = 0.0

    for e in events:
        model = e.get('model', 'unknown')
        inp = e.get('input_tokens', 0) or 0
        out = e.get('output_tokens', 0) or 0
        cost = e.get('cost', 0.0) or 0.0
        if model not in by_model:
            by_model[model] = {'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cost': 0.0}
        by_model[model]['calls'] += 1
        by_model[model]['input_tokens'] += inp
        by_model[model]['output_tokens'] += out
        by_model[model]['cost'] += cost
        total_input += inp
        total_output += out
        total_cost += cost

    return {
        'total_events': len(events),
        'total_input_tokens': total_input,
        'total_output_tokens': total_output,
        'total_tokens': total_input + total_output,
        'total_cost_usd': round(total_cost, 6),
        'by_model': by_model,
    }


def _try_json_parse(line: str) -> Optional[dict]:
    try:
        data = json.loads(line)
        if not isinstance(data, dict):
            return None
        from datetime import datetime
        event: dict = {
            'raw': line,
            'model': data.get('model'),
            'input_tokens': data.get('input_tokens') or data.get('usage', {}).get('input_tokens'),
            'output_tokens': data.get('output_tokens') or data.get('usage', {}).get('output_tokens'),
            'cost': data.get('cost'),
            'session': data.get('session_id') or data.get('session'),
        }
        if ts := data.get('timestamp') or data.get('time'):
            try:
                dt = datetime.fromisoformat(str(ts)[:26])
                event['timestamp'] = dt.isoformat()
                event['date'] = str(dt.date())
            except Exception:
                pass
        return event if event.get('model') else None
    except Exception:
        return None


def _try_regex_parse(line: str) -> Optional[dict]:
    event: dict = {'raw': line}
    if m := _MODEL_RE.search(line):
        event['model'] = m.group(1)
    if m := _TOKEN_RE.search(line):
        event['input_tokens'] = int(m.group(1))
        event['output_tokens'] = int(m.group(2))
    if m := _COST_RE.search(line):
        event['cost'] = float(m.group(1))
    if m := _SESSION_RE.search(line):
        event['session'] = m.group(1)
    return event if event.get('model') else None
