# 𝕏 X-CLI

**X/Twitter toolkit for AI agents — No API key. No developer account. Just cookies.**

An open-source [OpenClaw](https://openclaw.ai) skill that gives AI agents full X/Twitter access. Read tweets, search, post, interact, manage lists, upload media, send DMs — all from the command line.

Powered by [twikit](https://github.com/d60/twikit).

---

## ⚡ Why X-CLI?

| Feature | X-CLI | Twitter API v2 | Bird CLI |
|---------|-------|---------------|----------|
| **Cost** | Free | $100+/mo | Free |
| **API Key** | Not needed | Required | Not needed |
| **Auth** | Cookie-based | OAuth 2.0 | Cookie-based |
| **Status** | ✅ Active | ✅ Active | ⚠️ Deprecated |
| **Server/VPS** | ✅ Works | ✅ Works | ⚠️ Needs browser |
| **Proxy** | ✅ Built-in | N/A | ❌ No |
| **Language** | Python | Any | Node.js |

---

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/ignsoftwarellc/x-cli.git
cd x-cli

# Install dependencies
pip install -r scripts/requirements.txt

# Create your config
cp config.example.json config.json
```

### 🤖 Or Let Your AI Agent Do It

If you're using an AI agent (OpenClaw, Claude Code, etc.), just say:

> "Install x-cli from https://github.com/ignsoftwarellc/x-cli — my X username is **your_username**, password is **your_password**."

Your agent will clone, install, configure, and authenticate automatically.

---

## 🔐 Authentication

X-CLI uses your browser cookies to authenticate — no API keys needed.

### Option 1: Login with credentials
```bash
python scripts/x_auth.py login --username your_user --password your_pass
# Cookies are saved automatically
```

### Option 2: Use existing cookies
If you already have a `cookies.json` file (e.g. from a browser export), place it in the project root.

### Option 3: Set credentials in config.json
```json
{
  "x_username": "your_username",
  "x_email": "your_email@example.com",
  "x_password": "your_password",
  "cookies_file": "cookies.json",
  "proxy": null,
  "language": "en-US"
}
```

### Verify your auth
```bash
python scripts/x_auth.py check
# ✅ Cookies: cookies.json (found)
# ✅ Authenticated as @your_username

python scripts/x_auth.py whoami
# @your_username (Your Name)
# Followers: 1234 | Following: 567
```

---

## 📖 All Commands

### 📰 Reading (`x_read.py`)

Read tweets, timelines, threads, mentions, replies, and more.

```bash
# Read a single tweet (URL or ID)
python scripts/x_read.py tweet https://x.com/elonmusk/status/123456

# Read a user's latest tweets
python scripts/x_read.py user jack --count 5

# Read your home timeline (Following tab)
python scripts/x_read.py timeline --count 20

# Read your For You timeline
python scripts/x_read.py foryou --count 20

# Read a full thread
python scripts/x_read.py thread https://x.com/user/status/123456

# Read replies to a tweet
python scripts/x_read.py replies https://x.com/user/status/123456 --count 10

# Read your mentions (people who replied to you)
python scripts/x_read.py mentions --count 10

# Read a user's highlighted tweets
python scripts/x_read.py highlights elonmusk --count 5

# Search for users
python scripts/x_read.py search-user "space engineer" --count 10
```

### 🔎 Searching (`x_search.py`)

Search tweets using X's advanced search syntax.

```bash
# Basic search
python scripts/x_search.py "artificial intelligence" --count 10

# From a specific user
python scripts/x_search.py "from:jack AI" --count 5

# With minimum likes
python scripts/x_search.py "#OpenSource min_faves:100"

# In a specific language
python scripts/x_search.py "yapay zeka lang:tr" --count 10
```

### ✏️ Posting (`x_post.py`)

Post tweets, reply, and quote.

```bash
# Post a tweet
python scripts/x_post.py tweet "Hello from X-CLI! 🚀"

# Preview without actually posting
python scripts/x_post.py tweet "Draft tweet" --dry-run

# Post with media (upload first, then attach)
python scripts/x_extra.py upload photo.jpg    # Returns media ID
python scripts/x_post.py tweet "Check this out!" --media abc123

# Reply to a tweet
python scripts/x_post.py reply https://x.com/user/status/123 "Great analysis!"

# Quote tweet
python scripts/x_post.py quote https://x.com/user/status/123 "Adding context..."
```

### 💬 Interactions (`x_interact.py`)

Like, retweet, bookmark, follow, and more.

```bash
# Like / Unlike
python scripts/x_interact.py like https://x.com/user/status/123
python scripts/x_interact.py unlike https://x.com/user/status/123

# Retweet / Undo retweet
python scripts/x_interact.py retweet https://x.com/user/status/123
python scripts/x_interact.py unretweet https://x.com/user/status/123

# Bookmark / Remove bookmark
python scripts/x_interact.py bookmark https://x.com/user/status/123
python scripts/x_interact.py unbookmark https://x.com/user/status/123

# Follow / Unfollow
python scripts/x_interact.py follow elonmusk
python scripts/x_interact.py unfollow elonmusk

# Mute / Unmute
python scripts/x_interact.py mute spambot
python scripts/x_interact.py unmute spambot

# Block / Unblock
python scripts/x_interact.py block annoying_user
python scripts/x_interact.py unblock annoying_user

# Delete your own tweet
python scripts/x_interact.py delete https://x.com/you/status/123
```

### 📩 Direct Messages (`x_dm.py`)

Send and read DMs.

```bash
# Send a DM
python scripts/x_dm.py send elonmusk "Hey, great tweet!"

# Read your DM inbox
python scripts/x_dm.py inbox --count 10
```

### 🧰 Extra Features (`x_extra.py`)

Trends, bookmarks, notifications, user info, media, lists, polls.

```bash
# Trending topics
python scripts/x_extra.py trends
python scripts/x_extra.py trends --category news        # news, sports, entertainment, for-you

# List your bookmarked tweets
python scripts/x_extra.py bookmarks --count 10

# Read notifications
python scripts/x_extra.py notifications --count 10

# User profile info
python scripts/x_extra.py user-info elonmusk

# List a user's followers / following
python scripts/x_extra.py followers elonmusk --count 20
python scripts/x_extra.py following elonmusk --count 20

# Upload media (image, video, gif)
python scripts/x_extra.py upload path/to/image.jpg

# Schedule a tweet (unix timestamp)
python scripts/x_extra.py schedule 1740000000 "Scheduled tweet!"

# Create a poll
python scripts/x_extra.py poll "Option A" "Option B" "Option C" --duration 1440

# Lists: create, manage, read
python scripts/x_extra.py list-create "Tech News" --private
python scripts/x_extra.py list-add 12345 jack
python scripts/x_extra.py list-remove 12345 jack
python scripts/x_extra.py list-tweets 12345 --count 20
```

---

## 📊 JSON Output

Every command supports `--json` for structured output, perfect for piping to other tools:

```bash
python scripts/x_read.py user jack --count 3 --json
```

```json
{
  "id": "123",
  "user": "jack",
  "text": "Exciting new update coming soon!",
  "favorite_count": 500,
  "media": [{"url": "https://pbs.twimg.com/media/abc.jpg", "type": "photo", "alt_text": null}],
  "reply_to": null
}
```

---

## 👁️ Media & Vision Support

Tweets containing images, videos, or GIFs automatically include media URLs in the output:

```
@NASA (NASA)
Perseverance rover captures new Mars panorama 🔴
❤️ 5200  🔁 1800  🔗 https://x.com/NASA/status/123
🖼️ https://pbs.twimg.com/media/abc123.jpg
```

An AI agent can:
1. See the media URL in the tweet output
2. Fetch the image using `web_fetch`
3. Analyze it with **vision** (charts, infographics, screenshots)
4. Respond contextually based on what it sees

### Reply Context

Replies include the original tweet ID so the agent knows *what* was replied to:

```
@user (User Name)
Amazing photo!
❤️ 12  🔁 2  🔗 https://x.com/user/status/789
↩️ Reply to: https://x.com/i/status/456
```

The agent reads the original tweet, understands context, and writes a relevant reply.

---

## 🌐 Proxy Support (Optional)

If you're running on a VPS or datacenter IP, a residential proxy is recommended:

```json
{
  "proxy": "http://username:password@host:port"
}
```

Without proxy, X-CLI connects directly — proxy is **not required**.

---

## 🧩 OpenClaw Integration

### As a global skill
```bash
cp -r x-cli ~/.openclaw/skills/x-cli
```

### As a workspace skill
```bash
cp -r x-cli ~/.openclaw/workspace/skills/x-cli
```

The agent uses `exec` tool to run commands:
```
Agent: "Let me check trending topics"
→ exec: python scripts/x_extra.py trends
→ Agent reads output and responds
```

---

## 📋 Full Command Summary

| Script | Commands |
|--------|----------|
| `x_read.py` | `tweet`, `user`, `timeline`, `foryou`, `thread`, `replies`, `mentions`, `highlights`, `search-user` |
| `x_search.py` | Search with advanced syntax |
| `x_post.py` | `tweet`, `reply`, `quote` (+ `--media`, `--dry-run`) |
| `x_interact.py` | `like`, `unlike`, `retweet`, `unretweet`, `bookmark`, `unbookmark`, `follow`, `unfollow`, `delete`, `mute`, `unmute`, `block`, `unblock` |
| `x_dm.py` | `send`, `inbox` |
| `x_extra.py` | `trends`, `bookmarks`, `notifications`, `user-info`, `followers`, `following`, `upload`, `schedule`, `poll`, `list-create`, `list-add`, `list-remove`, `list-tweets` |
| `x_auth.py` | `check`, `whoami`, `login` |

**Total: 40+ commands across 7 scripts.**

---

## ⚠️ Disclaimer

X-CLI uses X/Twitter's private web GraphQL endpoints via twikit. This is **not** an official API. X can change things anytime — expect potential breakage without notice. Use responsibly.

---

## 📄 Requirements

- Python ≥ 3.10
- twikit ≥ 2.0.0

## 📜 License

MIT — Free to use, modify, and distribute.

## 🙏 Credits

- [twikit](https://github.com/d60/twikit) — Python X/Twitter API wrapper
- [OpenClaw](https://openclaw.ai) — AI agent platform
- [IGN Software](https://github.com/ignsoftwarellc) — Built by IGN Software LLC
