# YouTube Instant Article

![](https://cdn.macstories.net/friday-23-jan-2026-12-56-24-1769169413989.png)

Transform YouTube videos into beautiful Telegraph Instant View articles with embedded slides and timestamped summaries.

Best used with Clawdbot + Telegram for inline article opening.

## Features

- 🎬 **Automatic slide extraction** — Key frames from the video
- 📝 **AI-powered summaries** — GPT-5.2 generates concise, timestamped summaries
- 🖼️ **Interleaved layout** — Images paired with relevant timestamp sections
- ⚡ **Telegram Instant View** — One-tap readable articles in Telegram
- 🔗 **Reliable hosting** — Images on catbox.moe (no expiration)

## Example Output

```
📺 Watch video

[Image: Video thumbnail]

⏱️ 0:00 - Introduction and overview of the device
The reviewer introduces the new handheld gaming device...

[Image: Device closeup]

⏱️ 5:30 - Performance testing
Testing shows impressive results with modern games...

[Image: Gameplay footage]

⏱️ 12:00 - Final verdict
Overall recommendation and pricing discussion...
```

## Installation

### Prerequisites

```bash
# Install summarize CLI
brew install steipete/tap/summarize

# Install jq (JSON processor)
brew install jq
```

### Setup

1. **Get a Telegraph token:**
   ```bash
   ./scripts/setup.sh
   ```
   This creates a Telegraph account and outputs your access token.

2. **Set environment variables:**
   ```bash
   export TELEGRAPH_TOKEN="your_token_here"
   export OPENAI_API_KEY="your_openai_key"
   ```

3. **Configure summarize (optional):**
   ```bash
   mkdir -p ~/.summarize
   echo '{"model": "openai/gpt-5.2"}' > ~/.summarize/config.json
   ```

## Usage

### Basic

```bash
./scripts/generate.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

### With options

```bash
# Limit to 4 slides
./scripts/generate.sh "https://youtu.be/VIDEO_ID" --slides-max 4

# Debug mode (keeps temp files)
./scripts/generate.sh "https://youtu.be/VIDEO_ID" --debug
```

### Output

The script outputs the Telegraph article URL:
```
📹 Extracting slides...
📝 Getting summary...
📤 Uploading 4 slides...
🔨 Building article...
🌐 Publishing...

✅ Done!

https://telegra.ph/Article-Title-01-22
```

## How It Works

### Pipeline

1. **Extract video title** — Gets the actual YouTube title via summarize
2. **Extract slides** — Captures key frames at scene changes
3. **Generate summary** — GPT-5.2 creates timestamped summary
4. **Upload images** — Slides uploaded to catbox.moe
5. **Build article** — Constructs Telegraph-compatible JSON
6. **Publish** — Creates the Telegraph page via API

### Image Distribution

Images are distributed evenly across timestamp sections:
- 6 timestamps + 4 images → images at sections 1, 2, 4, 5
- Remaining timestamps get no image
- Any unused images added at the end

### Telegraph Format

The article uses this structure for Instant View compatibility:
- `<p>` — Video link, paragraphs
- `<h4>` — Timestamp headers (required for Instant View)
- `<figure><img>` — Embedded images
- `<blockquote>` — Notable quotes
- `<hr>` — Section dividers

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAPH_TOKEN` | Yes | Your Telegraph API access token |
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-5.2 |
| `SLIDES_MAX` | No | Default max slides (default: 6) |

### Summarize Config

Create `~/.summarize/config.json`:
```json
{
  "model": "openai/gpt-5.2"
}
```

## Technical Details

### Why catbox.moe?

Previous versions used freeimage.host, which had issues:
- Images sometimes returned 404
- Inconsistent availability
- SSL certificate problems

catbox.moe provides:
- No API key required
- No expiration
- Reliable CDN
- Simple upload API

### Why GPT-5.2?

We tested multiple models:

| Model | Speed | Cost | Quality |
|-------|-------|------|---------|
| gpt-5.2 | 4.5s | $0.01 | ⭐ Best |
| gpt-4o-mini | 6s | $0.0007 | Good |
| gpt-4o | 4.7s | $0.012 | Good |
| gpt-5-nano | 42s | $0.002 | Slow |
| gemini-3-flash | timeout | — | ❌ |

GPT-5.2 offers the best balance of speed and quality.

### Why zsh?

The script uses zsh instead of bash because:
- macOS bash is v3.2 (no associative arrays)
- zsh is the default shell on modern macOS
- Better array handling for image distribution

### Instant View Requirements

Telegram's Instant View requires specific formatting:
- **h4 headers** — h3 doesn't trigger Instant View
- **Proper figure tags** — Images must be in `<figure><img></figure>`
- **Processing time** — Telegram needs 1-2 minutes to generate preview

## Troubleshooting

### Script fails immediately
```bash
# Check zsh is available
which zsh

# Make script executable
chmod +x scripts/generate.sh
```

### "Failed to get summary"
```bash
# Verify OpenAI key
echo $OPENAI_API_KEY

# Test summarize directly
summarize "https://youtu.be/VIDEO_ID" --length short --plain
```

### Images not appearing
```bash
# Test catbox upload
curl -s "https://catbox.moe/user/api.php" \
  -F "reqtype=fileupload" \
  -F "fileToUpload=@test.png"
```

### No Instant View button in Telegram
- Wait 1-2 minutes after sharing the link
- Visit the Telegraph URL directly to verify content
- Try sharing the link again

## License

MIT

## Credits

- [summarize](https://github.com/steipete/summarize) — CLI for video summarization
- [Telegraph API](https://telegra.ph/api) — Article hosting
- [catbox.moe](https://catbox.moe) — Image hosting
