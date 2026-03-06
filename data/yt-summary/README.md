# 📺 YouTube Summary

**Drop a YouTube link in chat → get an instant, structured summary.**

An [OpenClaw](https://openclaw.com) skill that extracts video transcripts via [TranscriptAPI.com](https://transcriptapi.com) and generates concise summaries with key points and notable quotes. Supports custom prompts — just add your instructions after the URL.

## ✨ Features

- **Any YouTube URL** — `youtube.com/watch`, `youtu.be`, `/shorts/`, `/live/`, `m.youtube.com`
- **Custom prompts** — "focus on the technical details", "list action items", "explain like I'm 5"
- **Long video support** — handles videos of any length with smart truncation for very long transcripts
- **Telegram-optimized** — output fits Telegram's formatting and character limits

## 🚀 Quick Example

You:
> https://www.youtube.com/watch?v=dQw4w9WgXcQ summarize the key arguments

Giskard:
> 📺 **Never Gonna Give You Up** — Rick Astley (3min)
>
> **TL;DR:** Rick makes an impassioned case for commitment and loyalty...
>
> **Key Points:**
> • Never going to give you up
> • Never going to let you down
> ...

## 📦 Setup

### Prerequisites

- Python 3.10+
- A [TranscriptAPI.com](https://transcriptapi.com) account ($5/mo for 1,000 transcripts)

### 1. Get a TranscriptAPI key

Sign up at [transcriptapi.com](https://transcriptapi.com) and copy your API key.

### 2. Provide the API key (choose one method)

**Option A — Environment variable (simplest):**
```bash
export TRANSCRIPT_API_KEY="your-key-here"
```

**Option B — `pass` password store (most secure):**
```bash
pass insert transcriptapi/api-key
```

The script reads `--api-key-file` first (used by the `pass` workflow), then falls back to the `TRANSCRIPT_API_KEY` environment variable.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

That's it. Drop a YouTube link in chat and the skill kicks in automatically.

## 🔧 Why TranscriptAPI?

YouTube aggressively blocks transcript requests from datacenter IP ranges. If your OpenClaw instance runs on a VPS (Hetzner, DigitalOcean, AWS, Linode, etc.), direct transcript fetching will fail for most videos.

[TranscriptAPI.com](https://transcriptapi.com) proxies requests through residential IPs, making transcript extraction reliable from any host. At $5/mo for 1,000 transcripts, it's a simple and cost-effective solution.

## 🎨 Custom Prompt Examples

| You type | You get |
|---|---|
| `<url>` | Default structured summary with TL;DR + key points |
| `<url> focus on the technical details` | Technical deep-dive |
| `<url> list all action items` | Actionable takeaways |
| `<url> what are the main arguments for and against?` | Balanced pro/con analysis |
| `<url> explain like I'm 5` | Simplified summary |
| `<url> auf Deutsch zusammenfassen` | Summary in German |

## 🔍 Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Invalid API key` | TranscriptAPI key is wrong or expired | Check your key |
| `No transcript available` | Video has no captions | Nothing to do — video has no transcript |
| `Video not found` | Bad URL or private video | Double-check the URL |
| `Rate limited` | Too many requests | Wait a moment, try again |
| `No API key provided` | Neither env var nor `--api-key-file` set | Set `TRANSCRIPT_API_KEY` or use `pass` |

## 📁 Files

```
youtube-summary/
├── SKILL.md              # Agent instructions (how the AI uses this skill)
├── README.md             # This file (for humans)
├── requirements.txt      # Python dependencies
├── scripts/
│   ├── extract.py        # Transcript extraction + metadata
│   ├── utils.py          # URL parsing, token counting, text helpers
│   └── prompts.py        # Summary prompt templates (reference)
└── LICENSE               # MIT
```

## 📄 License

MIT — see [LICENSE](LICENSE).
