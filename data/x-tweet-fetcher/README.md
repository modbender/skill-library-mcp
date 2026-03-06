# x-tweet-fetcher

Fetch tweets from X/Twitter **without login or API keys**.

An [OpenClaw](https://github.com/openclaw/openclaw) skill. Zero dependencies, zero configuration.

## What It Can Fetch

| Content | Support |
|---------|---------|
| Regular tweets | ✅ Full text + stats |
| Long tweets | ✅ Full text |
| X Articles (long-form) | ✅ Complete article |
| Quoted tweets | ✅ Included |
| Stats (likes/RT/views) | ✅ Included |

## Quick Start

```bash
# JSON output
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456"

# Human readable
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --text-only

# Pretty JSON
python3 scripts/fetch_tweet.py --url "https://x.com/user/status/123456" --pretty
```

## Requirements

- Python 3.7+
- That's it. No packages, no API keys, no login.

## How It Works

Uses [FxTwitter](https://github.com/FxEmbed/FxEmbed) public API to fetch tweet data including full article content.

## Limitations

- Cannot fetch reply threads (only reply counts are included)
  - Reply content requires browser automation (removed to maintain zero dependencies)
  - `--replies` flag documented but returns explanatory error
- Cannot fetch deleted or private tweets
- Depends on FxTwitter service availability

## License

MIT
