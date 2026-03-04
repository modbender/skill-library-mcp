"""token_tracker.py

Minimal token logging helper. Append per-call token usage to a JSONL file.
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / 'skill-config.json'
try:
    cfg = json.loads(CONFIG_PATH.read_text())
except Exception:
    cfg = { 'timezone': 'UTC', 'log_folder': './skills/logs' }

TZ = ZoneInfo(cfg.get('timezone','UTC'))
LOG_FOLDER = Path(cfg.get('log_folder','./skills/logs'))
LOG_FOLDER.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_FOLDER / 'token_log.jsonl'


def now_iso():
    return datetime.now(TZ).isoformat()


def log_usage(call_id, model, prompt_tokens, completion_tokens, extra=None):
    entry = {
        'call_id': call_id,
        'model': model,
        'prompt_tokens': int(prompt_tokens),
        'completion_tokens': int(completion_tokens),
        'total_tokens': int(prompt_tokens) + int(completion_tokens),
        'timestamp': now_iso(),
    }
    if extra:
        entry['extra'] = extra
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    # simple demo
    log_usage('demo-1','gpt-example',10,20,{'note':'demo'})
    print('Wrote demo entry to', LOG_PATH)
