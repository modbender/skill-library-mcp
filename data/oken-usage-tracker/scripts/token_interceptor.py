"""Example token_interceptor.py

Normalize incoming timestamps, optionally summarize large contexts, and forward sanitized messages to token_tracker.
This is an example; integrate into your message pipeline as appropriate.
"""
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'skill-config.json'
try:
    cfg = json.loads(CONFIG_PATH.read_text())
except Exception:
    cfg = { 'timezone': 'UTC', 'log_folder': './skills/logs' }

TZ = ZoneInfo(cfg.get('timezone','UTC'))
LOG_FOLDER = Path(cfg.get('log_folder','./skills/logs'))
LOG_FOLDER.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_FOLDER / 'token_log.jsonl'

from token_tracker import log_usage  # sibling script


def normalize_timestamp(ts):
    """Return ISO timestamp in configured TZ. Accepts ISO strings with trailing Z or offsets, and naive strings.
    If parsing fails, returns current time in configured TZ."""
    if not ts:
        return datetime.now(TZ).isoformat()
    try:
        s = ts
        if s.endswith('Z'):
            s = s.replace('Z','+00:00')
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            # assume UTC for naive timestamps
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(TZ).isoformat()
    except Exception:
        return datetime.now(TZ).isoformat()


def process_message(msg):
    """Sanitize message and optionally summarize context before forwarding.
    `msg` is expected to be a dict with optional keys: 'timestamp','context','call_id','model','prompt_tokens','completion_tokens'."""
    m = dict(msg)  # shallow copy
    m['timestamp'] = normalize_timestamp(m.get('timestamp'))
    # if context is large, caller can choose to summarize before sending to model
    # Here we forward logging info only
    call_id = m.get('call_id','unknown')
    model = m.get('model','unknown')
    prompt_tokens = m.get('prompt_tokens',0)
    completion_tokens = m.get('completion_tokens',0)
    log_usage(call_id, model, prompt_tokens, completion_tokens, extra={'source':'interceptor'})
    return m


if __name__ == '__main__':
    sample = {'timestamp':'2026-02-28T14:31:53.807Z','call_id':'evt-123','model':'gpt-example','prompt_tokens':5,'completion_tokens':12}
    print(process_message(sample))
