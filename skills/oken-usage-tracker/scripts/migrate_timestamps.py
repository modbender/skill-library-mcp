"""migrate_timestamps.py

Utility to convert existing Z/UTC timestamps in a JSONL log to configured timezone.
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
LOG_PATH = LOG_FOLDER / 'token_log.jsonl'


def migrate():
    if not LOG_PATH.exists():
        print('No log found at', LOG_PATH)
        return
    tmp = LOG_PATH.with_suffix('.tmp')
    count = 0
    with LOG_PATH.open('r',encoding='utf-8') as fin, tmp.open('w',encoding='utf-8') as fout:
        for line in fin:
            try:
                obj = json.loads(line)
                ts = obj.get('timestamp','')
                if isinstance(ts,str) and ts.endswith('Z'):
                    s = ts.replace('Z','+00:00')
                    try:
                        dt = datetime.fromisoformat(s)
                        obj['timestamp'] = dt.astimezone(TZ).isoformat()
                        count += 1
                    except Exception:
                        pass
                fout.write(json.dumps(obj)+"\n")
            except Exception:
                fout.write(line)
    tmp.replace(LOG_PATH)
    print('Converted',count,'timestamps')


if __name__ == '__main__':
    migrate()
