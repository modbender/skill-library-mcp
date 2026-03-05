# X/Twitter Data Fetcher (Apify)

Fetch X/Twitter data from anywhere using Apify actors.

## Features

- **Tweet Search** - Search tweets by keywords, hashtags, mentions
- **User Profiles** - Get tweets from specific users, bio, stats
- **Tweet Details** - Get a specific tweet and its replies by URL
- **Local caching** - Repeat requests are FREE (1h for searches, 24h for profiles)
- **Cache management** - `--cache-stats`, `--clear-cache`, `--no-cache`
- JSON or human-readable summary output
- Simple Python script, no SDK needed

## Free Tier

Apify offers **$5/month free credits** - no credit card required!

[Sign up here](https://apify.com/)

## Quick Start

```bash
# 1. Set your API token
export APIFY_API_TOKEN="apify_api_YOUR_TOKEN"

# 2. Search tweets
python3 scripts/fetch_tweets.py --search "artificial intelligence"

# 3. Get user's tweets
python3 scripts/fetch_tweets.py --user "OpenAI"

# 4. Get specific tweet
python3 scripts/fetch_tweets.py --url "https://x.com/user/status/123"
```

## Documentation

See [SKILL.md](SKILL.md) for full documentation, setup instructions, and usage examples.

## Links

- [Apify Free Tier](https://apify.com/pricing) - $5/month free
- [Get API Key](https://console.apify.com/account/integrations)
- [Twitter Scraper Actor](https://apify.com/quacker/twitter-scraper)

## Requirements

- Python 3.6+
- `requests` library (`pip install requests`)
- Apify API token (free)

## Legal Notice

This skill accesses publicly available data via Apify. Users are responsible for compliance with local data protection laws (GDPR etc.) and X/Twitter's Terms of Service.

## License

MIT
