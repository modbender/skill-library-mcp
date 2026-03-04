# Installation & Authentication

## Install the CLI

```bash
npm install -g video-understand
```

Verify installation:
```bash
video-understand --version
```

**Requires Node.js 18 or later.**

## Authentication

`video-understand` supports two providers. You only need to set up the one(s) you plan to use.

---

### Gemini (Google)

Get an API key from https://aistudio.google.com/apikey.

**Option A: Environment variable (recommended)**
```bash
export GEMINI_API_KEY="your-key-here"
```

**Option B: CLI login**
```bash
video-understand login --key YOUR_GEMINI_API_KEY
# Auto-detected as gemini. Saved to ~/.video-understand/config.json.
```

---

### Kimi (Moonshot AI)

Get an API key from https://platform.moonshot.ai.

**Option A: Environment variable (recommended)**
```bash
export MOONSHOT_API_KEY="your-key-here"
```

**Option B: CLI login**
```bash
video-understand login --key YOUR_KIMI_API_KEY
# Auto-detected as kimi. Saved to ~/.video-understand/config.json.
```

**YouTube videos support (optional):**

Kimi can analyze YouTube videos, but requires `yt-dlp` to download the video first.

Install via your platform's package manager (recommended):
```bash
# Windows
winget install yt-dlp

# macOS
brew install yt-dlp

# Linux (Debian/Ubuntu)
sudo apt install yt-dlp

# Cross-platform (uv)
uv tool install yt-dlp
```

---

### Switch default provider

```bash
video-understand config set-provider kimi
video-understand config set-provider gemini
```

### Verify authentication

```bash
video-understand config
```

Shows the active provider, masked API key, and whether it came from an env var or config file.

---

## Troubleshooting

**"API key not found"**
- Ensure the relevant env var is set (`GEMINI_API_KEY` or `MOONSHOT_API_KEY`), or run `video-understand login --key YOUR_API_KEY`

**"Could not detect provider from key format"**
- Use `--provider` explicitly: `video-understand login --provider gemini --key YOUR_API_KEY`

**"yt-dlp is required to download YouTube videos"**
- Required when using Kimi with YouTube videos. See the yt-dlp install instructions above.

**"File processing timed out"**
- Large video files (>500MB) may take longer on Gemini. Try a shorter clip

**"Unsupported video format"**
- Supported: MP4, MPEG, MOV, AVI, FLV, MPG, WebM, WMV, 3GPP, MKV

**Permission denied on install**
- Use `sudo npm install -g video-understand` or fix npm permissions
