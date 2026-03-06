"""dedupe_log.py

Remove duplicate entries from token_log.jsonl based on call_id.
"""
import json
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / 'skills' / 'logs' / 'token_log.jsonl'


def dedupe():
    if not LOG_PATH.exists():
        print('No log at', LOG_PATH)
        return
    seen = set()
    tmp = LOG_PATH.with_suffix('.dedupe')
    with LOG_PATH.open('r',encoding='utf-8') as fin, tmp.open('w',encoding='utf-8') as fout:
        for line in fin:
            try:
                j = json.loads(line)
                cid = j.get('call_id')
                key = cid if cid else line
                if key in seen:
                    continue
                seen.add(key)
                fout.write(json.dumps(j)+"\n")
            except Exception:
                fout.write(line)
    tmp.replace(LOG_PATH)
    print('Dedupe complete. Kept', len(seen), 'entries')


if __name__ == '__main__':
    dedupe()
