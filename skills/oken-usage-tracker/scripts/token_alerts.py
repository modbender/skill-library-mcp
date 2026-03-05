"""token_alerts.py

Example alerting script. Reads token_log.jsonl and prints entries over a threshold.
Replace printing with webhook/telegram calls as needed.
"""
import json
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parents[1] / 'skills' / 'logs' / 'token_log.jsonl'


def check_threshold(threshold=1000):
    if not LOG_PATH.exists():
        print('No log file at', LOG_PATH)
        return []
    matches = []
    with LOG_PATH.open('r',encoding='utf-8') as f:
        for line in f:
            try:
                j = json.loads(line)
                if j.get('total_tokens',0) >= threshold:
                    matches.append(j)
            except Exception:
                continue
    return matches


if __name__ == '__main__':
    hits = check_threshold(500)
    for h in hits:
        print('Alert:', h)
