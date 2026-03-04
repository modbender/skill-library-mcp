# x-extract

Extract tweet content from x.com URLs without requiring Twitter/X API credentials.

## Description

Browser-based tweet extraction tool that captures tweet text, author information, media, and engagement metrics from public x.com/twitter.com URLs using OpenClaw's browser automation.

## Usage

Trigger phrases:
- "extract tweet [URL]"
- "get tweet content from [URL]"
- "download x.com link [URL]"
- Any x.com/*/status/* or twitter.com/*/status/* URL

## Features

- ✅ No API credentials required
- ✅ Extract text, author, timestamp, media URLs
- ✅ Capture engagement metrics (likes, retweets, replies)
- ✅ Thread detection and extraction
- ✅ Optional media download
- ✅ Structured markdown output

## Requirements

- OpenClaw with browser tool enabled
- Profile: `openclaw` (or any browser profile)

## Limitations

- Cannot access protected/private tweets
- Cannot access login-required content (age-restricted, controversial)
- May be affected by X.com layout changes
- Subject to X.com rate limiting

## Documentation

See [SKILL.md](SKILL.md) for detailed workflow and technical documentation.

## Version

1.0.0 (2026-02-16)
