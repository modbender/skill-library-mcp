# YouTube AI Videos 🎬

Fetch latest AI-related videos from YouTube channels with keyword filtering using YouTube Data API v3.

![Skill Version](https://img.shields.io/badge/version-1.0.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-yellow)

## ⚠️ Requirement

**This skill requires a YouTube Data API v3 key to function.** The YouTube RSS feeds have been disabled, so this skill exclusively uses the YouTube Data API v3.

## ✨ Features

- 🔍 **Keyword Filtering** — Only videos matching your keywords
- 📅 **Age Filter** — Configurable maximum video age (default: 3 days)
- 🎯 **Channel Selection** — Curated AI-focused YouTube channels
- 🔐 **Secure API Key** — Multiple storage options (env var, secrets file)
- 🏷️ **Keyword Highlighting** — Matches are highlighted in output
- 📊 **Configurable** — Channels, keywords, max videos, age limits
- 🚀 **Fast** — Uses YouTube Data API v3 for efficient fetching

## 📋 What it Does

This skill fetches recent videos from your favorite AI-focused YouTube channels using the YouTube Data API v3 and filters them by keywords like "OpenClaw", "LLM", "Agent", "Claude Code", etc.

Perfect for staying up-to-date with the latest AI developments, agent tools, and coding assistants!

## 🚀 Installation

### Option 1: Install via ClawHub (Recommended)

```bash
clawhub install youtube-ai-videos
```

### Option 2: Manual Installation

1. Clone or download this skill to your OpenClaw workspace:
```bash
git clone https://github.com/your-username/youtube-ai-videos.git ~/.openclaw/workspace/youtube-ai-videos
```

2. Ensure Python 3.8+ is installed:
```bash
python3 --version
```

## ⚙️ Configuration

### Step 1: Get YouTube Data API Key (REQUIRED!)

This skill **requires** a YouTube Data API v3 key. Without it, the skill will not work.

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or use existing
3. Navigate to "APIs & Services" → "Library"
4. Search for "YouTube Data API v3" and enable it
5. Go to "APIs & Services" → "Credentials"
6. Create "API Key"
7. **Important:** Restrict key to "YouTube Data API v3" only

### Step 2: Configure API Key (Secure Options)

Choose one of these methods (ordered by priority):

#### Option A: Secrets File (Recommended ✅)

Store your API key securely:

```bash
echo "YOUR_YOUTUBE_API_KEY" > ~/.openclaw/secrets/youtube_api_key.txt
chmod 600 ~/.openclaw/secrets/youtube_api_key.txt
```

#### Option B: Environment Variable

```bash
export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"
```

For permanent usage, add to your shell profile (~/.zshrc or ~/.bashrc):

```bash
echo 'export YOUTUBE_API_KEY="YOUR_YOUTUBE_API_KEY"' >> ~/.zshrc
source ~/.zshrc
```

#### Option C: Config File (Fallback ⚠️)

Edit `config.json` and replace the placeholder:

```json
{
  "youtubeApiKey": "YOUR_YOUTUBE_API_KEY"
}
```

**⚠️ Security Warning:** The API key in `config.json` is visible in plain text. Use options A or B instead!

### Step 3: Configure Channels and Keywords

Edit `config.json` to customize:

```json
{
  "channels": [
    "@IchBinFabian",
    "@EverlastAI",
    "@BetterStack",
    "@ChristophMagnussen"
  ],
  "keywords": [
    "OpenClaw",
    "LLM",
    "Agent",
    "Claude Code",
    "RAG"
  ],
  "maxVideos": 15,
  "maxAgeDays": 3
}
```

**Settings Explained:**

| Setting | Description | Default |
|---------|-------------|----------|
| `channels` | YouTube channel handles (@handle) or IDs | 13 AI channels |
| `keywords` | Keywords to filter videos by | AI/LLM related |
| `maxVideos` | Maximum number of videos to return | 15 |
| `maxAgeDays` | Maximum age of videos in days | 3 |
| `youtubeApiKey` | Fallback API key (use secrets instead) | `YOUR_API_KEY_HERE` |

## 🎯 Usage

### Command Line

Run the fetcher:

```bash
~/.openclaw/workspace/youtube-ai-videos/scripts/fetch_youtube_ai_videos.py
```

Or use the alias (if configured):

```bash
youtube-ai
```

### Output Format

```
🎬 Fetching AI videos (last 3 days)
Keywords: openclaw, llm, agent, claude code, opencode, rag
Channels: 13

Fetching from @IchBinFabian...
Fetching from @EverlastAI...
...

1. [7m ago] [Codex App Live: KI-**Agent**en direkt auf deinen Code ansetzen!](https://www.youtube.com/watch?v=...)
   by @IchBinFabian

2. [1h ago] [An **LLM** in Just 200 Lines of Python?! (microGPT)](https://www.youtube.com/watch?v=...)
   by @Better Stack

✅ Found 15 videos (from 13 channels)
```

## 🔧 Advanced Configuration

### Adding More Channels

Find YouTube channel handle or ID:

1. Go to channel page
2. Look at URL: `youtube.com/@CHANNELNAME` or `youtube.com/channel/CHANNEL_ID`
3. Add to `config.json`:
   - Handle format: `"@ChannelName"`
   - ID format: `"UC..."`
   - URL format: `"https://www.youtube.com/CHANNELNAME"`

### Custom Keywords

Add any keywords you want to track:

```json
"keywords": [
  "OpenClaw",
  "LLM",
  "GPT",
  "Claude",
  "AI Coding",
  "RAG",
  "Vector Database"
]
```

### Adjust Time Range

Change the maximum age of videos:

```json
"maxAgeDays": 7  // Show videos from last week
```

Or show only today's videos:

```json
"maxAgeDays": 1  // Show only today's videos
```

## 📊 API Quota

The YouTube Data API v3 free tier includes:

- **10,000 quota units per day**
- **Channel list API** costs 1 unit per request
- **Video search API** costs 100 units per request
- **Video details API** costs 1 unit per request

**Typical Usage:**
- Fetching from 13 channels ≈ 13 units
- Fetching video details ≈ 1-3 units
- **Daily usage ≈ 20-50 units** (well within limits!)

## 🛠️ Troubleshooting

### API Key Not Found

```
❌ YouTube Data API key is required!
```

**Solution:** Make sure your API key is set via:
- Secrets file: `~/.openclaw/secrets/youtube_api_key.txt`
- Environment variable: `export YOUTUBE_API_KEY="..."`
- Config file (fallback): `config.json`

### No Matching Videos

```
❌ No matching videos found.
```

**Possible causes:**
1. No videos matching your keywords in time range
2. Channels have no recent uploads
3. Keywords are too specific
4. `maxAgeDays` is too short

**Solutions:**
- Increase `maxAgeDays` (try 7 or 14)
- Add more keywords
- Add more channels
- Check if channels are posting content

### Rate Limit Errors

```
Error: quotaExceeded
```

**Solution:** YouTube API quota is 10,000 units/day. If you hit this limit:
1. Wait until tomorrow for quota to reset
2. Reduce number of channels
3. Increase `maxAgeDays` to reduce refresh frequency

## 📦 Skill Structure

```
youtube-ai-videos/
├── SKILL.md                 # Core skill documentation
├── config.json              # Configuration (channels, keywords, settings)
├── README.md               # This file
└── scripts/
    ├── fetch_youtube_ai_videos.py  # Main fetcher script
    └── find_channel_id.py        # Channel ID finder utility
```

## 📞 Support

- **OpenClaw Docs:** https://docs.openclaw.ai
- **ClawHub:** https://clawhub.com
- **Community:** https://discord.com/invite/clawd

## 📜 License

MIT License - feel free to use, modify, and distribute!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add more AI-focused channels
- Improve filtering logic
- Add more output formats
- Fix bugs

## 🙏 Credits

- Built for OpenClaw users
- Uses YouTube Data API v3
- Inspired by the need for automated AI news aggregation

---

Made with ❤️ by the OpenClaw community
