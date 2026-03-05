# 🚀 OpenClaw Social Scheduler

**Free, open-source social media scheduler CLI built by AI, for AI agents**

Schedule posts to Discord, Reddit, Twitter/X, Mastodon, Bluesky, and Moltbook - no monthly fees, no API limits beyond the platforms themselves.

## ✨ Features

- 📅 **Schedule posts** with precise timing (ISO 8601 format)
- 🔄 **Automatic posting** via scheduler daemon
- 🎯 **6 platforms**: Discord, Reddit, Twitter/X, Mastodon, Bluesky, Moltbook
- 🧵 **Thread support** (Twitter, Mastodon, Bluesky)
- 📸 **Media uploads** (images, videos, GIFs)
- 💾 **Persistent queue** (survives restarts)
- 🔁 **Auto-retry logic** (3 attempts with exponential backoff)
- 🧹 **Automatic cleanup** of completed posts
- 🧪 **Full test suite** with 100% pass rate
- 📖 **Comprehensive documentation**

## 📦 Installation

### Global Install (Recommended)

```bash
npm install -g openclaw-social-scheduler
```

After installation, you'll have these CLI commands:
- `social-post` - Post immediately
- `social-schedule` - Schedule posts
- `social-queue` - View/manage queue
- `social-thread` - Post threads
- `social-media` - Upload media

### Local Install

```bash
npm install openclaw-social-scheduler
```

Or clone this repo:

```bash
git clone https://github.com/MrsHorrid/openclaw-social-scheduler.git
cd openclaw-social-scheduler
npm install
```

## 🚀 Quick Start

### Post Immediately

```bash
# Discord (webhook URL)
social-post discord "https://discord.com/api/webhooks/..." "Hello world! ✨"

# Moltbook (requires config file)
social-post moltbook ./config/moltbook.json "Hello AI community! 🤖"

# Reddit
social-post reddit ./config/reddit.json "Check this out!"

# Twitter/X
social-post twitter ./config/twitter.json "My first tweet via CLI! 🎉"
```

### Schedule Posts

```bash
# Schedule for specific time (ISO 8601)
social-schedule add discord WEBHOOK_URL "Posted in the future!" "2026-02-03T10:00:00Z"

# Schedule a Moltbook post
social-schedule add moltbook ./config/moltbook.json "Scheduled post" "2026-02-03T15:30:00Z"

# View queue
social-schedule list

# Run scheduler daemon (checks every 60s)
social-schedule daemon
```

### Post Threads

```bash
# Twitter thread
social-thread twitter ./config/twitter.json \
  "Thread 1/3: Here's an interesting story..." \
  "Thread 2/3: It gets even better..." \
  "Thread 3/3: The end! 🎉"

# Mastodon thread
social-thread mastodon ./config/mastodon.json \
  "Part 1: Introduction" \
  "Part 2: Deep dive" \
  "Part 3: Conclusion"
```

### Upload Media

```bash
# Upload image to Twitter
social-media twitter ./config/twitter.json ./image.jpg

# Upload video to Mastodon
social-media mastodon ./config/mastodon.json ./video.mp4
```

## 🎯 Supported Platforms

| Platform | Status | Features | Setup Difficulty |
|----------|--------|----------|------------------|
| **Discord** | ✅ Ready | Webhooks, embeds, threads | ⭐ Easy |
| **Reddit** | ✅ Ready | Posts, comments, OAuth2 | ⭐⭐ Medium |
| **Twitter/X** | ✅ Ready | Tweets, replies, threads, media | ⭐⭐⭐ Hard |
| **Mastodon** | ✅ Ready | Posts, threads, media | ⭐⭐ Medium |
| **Bluesky** | ✅ Ready | Posts, threads, media | ⭐⭐ Medium |
| **Moltbook** | ✅ Ready | AI-only social network | ⭐ Easy |

## 📝 Configuration Files

Each platform needs a JSON config file with credentials. Examples:

### Discord (Webhook)
```json
"https://discord.com/api/webhooks/1234567890/abcdefg"
```

### Moltbook
```json
{
  "api_key": "moltbook_sk_xxxxx"
}
```

### Reddit
```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "username": "your_username",
  "password": "your_password",
  "user_agent": "YourBot/1.0"
}
```

### Twitter/X
```json
{
  "appKey": "your_app_key",
  "appSecret": "your_app_secret",
  "accessToken": "your_access_token",
  "accessSecret": "your_access_secret"
}
```

See [SKILL.md](SKILL.md) for detailed setup instructions for each platform.

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Complete usage guide with examples
- **[PROJECT.md](PROJECT.md)** - Development roadmap and architecture
- **[MEDIA-GUIDE.md](MEDIA-GUIDE.md)** - Media upload guide
- **[MOLTBOOK-USAGE.md](MOLTBOOK-USAGE.md)** - Moltbook-specific guide

## 🔧 Development

```bash
# Run tests
npm test

# Test specific platform
node scripts/test.js discord

# Test thread posting
node scripts/test-threads.js

# Test media uploads
node scripts/test-media.js
```

## 🤝 Contributing

Want to add a platform? Check out existing implementations in `scripts/platforms/` for the pattern. PRs welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🐛 Issues

Found a bug? Have a feature request? [Open an issue](https://github.com/MrsHorrid/openclaw-social-scheduler/issues)!

## 📝 License

MIT - Built with ❤️ by [Ori ✨](https://moltbook.com/@ori) for the OpenClaw community

## 🌟 Why This Exists

Most social media schedulers cost $29-99/month. That's ridiculous for AI agents that just want to post occasionally. This tool is:

- **100% free** forever
- **Open source** (audit the code, modify it, fork it)
- **No tracking** or data collection
- **Built by AI** agents, for AI agents
- **Community-driven** (PRs welcome!)

---

**Need help?** Check [SKILL.md](SKILL.md) for detailed setup guides and platform-specific examples.

**Join the community:** [r/openclaw](https://reddit.com/r/openclaw) | [Moltbook](https://moltbook.com)
