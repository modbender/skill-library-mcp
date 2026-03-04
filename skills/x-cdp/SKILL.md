---
name: x-cdp
description: >
  Automate X (Twitter) via Chromium CDP: post tweets, reply, quote-retweet, publish articles.
  Uses real browser sessions with existing login, no API keys needed.
  Trigger: user asks to post on X/Twitter, reply to a tweet, quote retweet, or publish an X article.
---

# X CDP Skill — Browser Automation for X (Twitter)

## First-Time Setup

Run the setup wizard. It checks everything and auto-fixes what it can:

```bash
node scripts/setup.js [--port 18802] [--profile ~/chromium-profiles/x-cdp]
```

The wizard does 4 things:
1. **Finds Chromium/Chrome** on your system (or tells you how to install it)
2. **Checks puppeteer-core** (auto-installs to /tmp/node_modules if missing)
3. **Launches Chromium** with CDP enabled on the specified port
4. **Verifies X login** (tells you to log in manually if needed)

### Manual setup (if you prefer)

**Install Chromium** (recommended over Chrome for version stability):
```bash
# macOS
brew install --cask chromium

# Linux
sudo apt install chromium-browser
```

**Install puppeteer-core**:
```bash
cd /tmp && npm init -y && npm install puppeteer-core
```

**Launch Chromium with CDP**:
```bash
chromium --remote-debugging-port=18802 --user-data-dir=~/chromium-profiles/x-cdp --no-first-run
```

**Log in to X**: Open `x.com` in the Chromium window and log in once. The session persists in the profile directory.

### Why Chromium, not Chrome?

Chrome auto-updates silently. One update can change DOM selectors and break all automation overnight. Chromium lets you pin a known-good version. That said, Chrome works fine too if you don't mind occasional breakage.

## Architecture

All scripts connect to a running Chromium instance via CDP (Chrome DevTools Protocol).
This is **not** API-based. It drives the real browser UI, identical to a human clicking.

### Multi-account isolation

Each X account gets its own Chromium instance with a separate port and profile:

- Port 18800, profile `chromium-profiles/main`: @your_main_account
- Port 18801, profile `chromium-profiles/second`: @your_second_account
- Port 18802, profile `chromium-profiles/third`: @your_third_account

Launch multiple instances for multi-account use. All scripts accept `--port` to target a specific account.

## Commands

### Post a tweet
```bash
NODE_PATH=/tmp/node_modules node scripts/post-tweet.js "Hello world" [--image /path/to/img.png] [--port 18802] [--dry-run]
```

### Reply to a tweet
```bash
NODE_PATH=/tmp/node_modules node scripts/reply-tweet.js <tweet_url> "Nice post!" [--image /path/to/img.png] [--port 18802] [--dry-run]
```

### Quote retweet
```bash
NODE_PATH=/tmp/node_modules node scripts/quote-tweet.js <tweet_url> "My thoughts" [--port 18802] [--dry-run]
```

### Publish an article (X Premium)
```bash
NODE_PATH=/tmp/node_modules node scripts/post-article.js --title "Title" --body "Body text" [--body-file /path/to/content.md] [--cover /path/to/cover.jpg] [--port 18800] [--dry-run]
```

All scripts support `--dry-run` to fill content without sending. A screenshot is saved to `/tmp/`.

## Agent Integration

When the user asks to interact with X:

### Pre-flight check
Before running any script, verify the environment:
1. Check if Chromium is running on the target port: `curl -s http://localhost:<port>/json/version`
2. If not running, run `node scripts/setup.js --port <port>` to launch and configure
3. If setup fails, report the specific step that failed

### Compose flow
1. User provides intent (e.g., "reply to this tweet saying thanks")
2. Agent drafts the text, shows it to user for approval
3. On confirmation, run the script via `exec`
4. Report success/failure

### Error recovery
If a script fails with "not found" errors, X may have changed its DOM. Check and update:
- `references/selectors.md` for the latest selectors
- `scripts/lib/cdp-utils.js` SELECTORS object

## Risk Notes

- **Rate limiting**: Space out actions. No more than ~10 tweets/hour.
- **Detection**: CDP automation looks like real browser usage. Much harder to detect than API abuse.
- **Account safety**: Human-like delays are built into all scripts. Avoid bulk operations.
- **vs API tools (bird etc.)**: API wrappers get DMCA'd or break on API changes. CDP works as long as the website works.
