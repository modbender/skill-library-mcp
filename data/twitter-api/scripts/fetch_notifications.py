import asyncio
import json
import os
from pathlib import Path

from twitter_api.twitter import Twitter

BASE = Path(__file__).parent
ENV_PATH = BASE / '.env'
OUT_PATH = BASE / 'notifications_raw.json'

def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, val = line.split('=', 1)
        os.environ.setdefault(key.strip(), val.strip())


async def main():
    load_env(ENV_PATH)
    auth = os.environ.get('GANCLAW_X_PRIMARY_AUTH_TOKEN')
    ct0 = os.environ.get('GANCLAW_X_PRIMARY_CT0')
    if not auth or not ct0:
        raise SystemExit('Missing auth env vars')
    twitter = Twitter(auth, ct0)
    data = await twitter.user.get_notifications()
    if data is None:
        raise SystemExit('No data (auth failure?)')
    OUT_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps({'saved': str(OUT_PATH), 'notifications': len(data.get('globalObjects', {}).get('tweets', {}))}))


if __name__ == '__main__':
    asyncio.run(main())
