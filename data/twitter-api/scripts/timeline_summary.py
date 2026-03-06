import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Ensure we can import local twitter_api package
import sys
BASE_DIR = Path(__file__).parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from twitter_api.twitter import Twitter

ENV_PATH = BASE_DIR / '.env'
RAW_PATH = BASE_DIR / 'timeline_raw.json'
SUMMARY_PATH = BASE_DIR / 'timeline_summary.txt'


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()
        os.environ.setdefault(key, value)


def format_tweet(t: dict, idx: int) -> str:
    user = t.get('user', {})
    metrics = t.get('metrics', {})
    text = (t.get('text', '') or '').replace('\n', ' ')
    lines = [
        f"{idx}. @{user.get('username','?')} — {user.get('display_name','')}",
        f"   Text: {text[:160]}{'…' if len(text) > 160 else ''}",
        f"   Likes {metrics.get('likes',0)}, RTs {metrics.get('retweets',0)}, Replies {metrics.get('replies',0)}, Quotes {metrics.get('quotes',0)}",
    ]
    if t.get('hashtags'):
        lines.append(f"   Hashtags: {' '.join(t['hashtags'][:5])}")
    if t.get('urls'):
        lines.append(f"   URLs: {t['urls'][0]}")
    lines.append(f"   Created: {t.get('created_at','')}")
    if t.get('is_promoted'):
        lines.append("   [PROMOTED]")
    return '\n'.join(lines)


def summarize(tweets: list) -> str:
    if not tweets:
        return "No tweets returned."
    top = tweets[:10]
    summary_blocks = [format_tweet(t, i+1) for i, t in enumerate(top)]
    return '\n\n'.join(summary_blocks)


def main():
    load_env_file(ENV_PATH)
    auth = os.environ.get('GANCLAW_X_PRIMARY_AUTH_TOKEN')
    ct0 = os.environ.get('GANCLAW_X_PRIMARY_CT0')
    if not auth or not ct0:
        raise SystemExit("Missing GANCLAW_X_PRIMARY_AUTH_TOKEN or GANCLAW_X_PRIMARY_CT0 in .env or environment")

    twitter = Twitter(auth, ct0)

    async def fetch():
        return await twitter.timeline.get_home_timeline_data(count=20)

    tweets = asyncio.run(fetch())

    RAW_PATH.write_text(json.dumps(tweets, indent=2, ensure_ascii=False), encoding='utf-8')
    SUMMARY_PATH.write_text(summarize(tweets), encoding='utf-8')

    print(json.dumps({
        'fetched': len(tweets),
        'raw_path': str(RAW_PATH),
        'summary_path': str(SUMMARY_PATH),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }))


if __name__ == '__main__':
    main()
