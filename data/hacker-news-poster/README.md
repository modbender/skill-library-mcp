# hacker-news-poster

Post, comment, and interact on Hacker News from the command line. Built for AI agents on OpenClaw, works standalone too.

## Install

```bash
# As an OpenClaw skill
clawhub install hacker-news-poster

# Or just grab the script
curl -O https://raw.githubusercontent.com/frostai-lab/hacker-news-poster/main/scripts/hn.py
```

Requires Python 3.10+. No dependencies.

## Setup

Set `HN_USERNAME` and `HN_PASSWORD` in your environment.

## Usage

```bash
# Login (once per session)
python3 scripts/hn.py login

# Submit a link
python3 scripts/hn.py submit --title "Show HN: My Tool" --url "https://example.com"

# Submit a text post
python3 scripts/hn.py submit --title "Ask HN: Question?" --text "body here"

# Comment on a thread
python3 scripts/hn.py comment --parent 12345678 --text "your comment"

# Edit a comment (within HN's ~2hr edit window)
python3 scripts/hn.py edit --id 12345678 --text "updated text"

# Update profile bio
python3 scripts/hn.py profile --username youruser --about "your bio"
```

All commands output JSON on success, errors go to stderr.

## Notes

- HN rate-limits submissions and comments. If you hit a limit, wait a few minutes.
- Pair with the read-only [hacker-news](https://clawhub.com/skills/hacker-news) skill for browsing/searching.

## License

MIT
