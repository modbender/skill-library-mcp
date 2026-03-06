# Installation — Twitter/X Reader Skill

## Prerequisites

- **bash** (v4+ recommended)
- **curl** — HTTP client
- **jq** — JSON processor
- **gdate** (optional, macOS) — `brew install coreutils` for better timestamp formatting

## Install

1. Copy the `twitter-reader/` directory into your OpenClaw skills folder:

   ```bash
   cp -r twitter-reader/ ~/.openclaw/workspace/skills/twitter-reader/
   ```

2. Make scripts executable:

   ```bash
   chmod +x skills/twitter-reader/scripts/*.sh
   ```

3. Verify dependencies:

   ```bash
   command -v curl jq bash
   ```

4. Test with a sample tweet:

   ```bash
   ./skills/twitter-reader/scripts/read_tweet.sh "https://x.com/OpenAI/status/1234567890"
   ```

## File Structure

```
skills/twitter-reader/
├── SKILL.md                    # Skill documentation for agents
├── README.md                   # Public-facing documentation
├── INSTALLATION.md             # This file
├── LICENSE                     # MIT license
├── test_skill.sh               # Test script
└── scripts/
    ├── read_tweet.sh           # Primary FxTwitter API script
    ├── read_thread.sh          # Thread reader (follows reply chain)
    └── read_tweet_nitter.sh    # Nitter fallback (best-effort)
```

## Usage

```bash
# Read a single tweet
./scripts/read_tweet.sh "https://x.com/user/status/123456789"

# Read a thread
./scripts/read_thread.sh "https://x.com/user/status/123456789"

# Nitter fallback (most instances are defunct — best-effort only)
./scripts/read_tweet_nitter.sh "https://x.com/user/status/123456789"
```

## Troubleshooting

- **jq not found** — Install via `brew install jq` (macOS) or `apt install jq` (Linux)
- **Nitter failures** — Expected; most public instances are down. Use FxTwitter (default).
- **Timestamp formatting** — Install GNU date (`brew install coreutils`) for human-readable timestamps on macOS.
