---
name: minimax-to-telegram
description: |
  Generate images, audio, video using MiniMax MCP and send to Telegram. 
  Use when user wants to create media with MiniMax and deliver it via Telegram.
---

# Setup (Prerequisites)

## 1. Install mcporter

```bash
# 如果未有 npm/npx
npm install -g mcporter
```

或者用 npx 直接跑：
```bash
npx mcporter --help
```

## 2. Set MiniMax API Key

响 terminal 度 set 環境變數：

```bash
export MINIMAX_API_KEY="your-api-key-here"
```

或者响 `~/.mcporter/config.json` 入面 set：

```json
{
  "env": {
    "MINIMAX_API_KEY": "your-api-key-here",
    "MINIMAX_RESOURCE_MODE": "url"
  }
}
```

## 3. Add MiniMax MCP Server

```bash
mcporter mcp add minimax-mcp
```

---

# MiniMax MCP Skill

Use `mcporter` to call MiniMax MCP server tools.

## Prerequisites

- mcporter CLI installed
- MiniMax MCP server configured in mcporter

## Available Tools

| Tool | Description |
|------|-------------|
| text_to_image | Generate images from text prompts |
| text_to_audio | Convert text to speech (TTS) |
| generate_video | Generate videos from text prompts |
| image_to_video | Generate videos from images |
| music_generation | Generate music from prompt + lyrics |
| voice_clone | Clone voice from audio file |
| voice_design | Generate voice from description |
| list_voices | List available voice IDs |
| play_audio | Play audio file |

## Basic Usage

### Image Generation

```bash
mcporter call minimax-mcp.text_to_image prompt:"your prompt" aspectRatio:"4:3"
```

### Audio Generation (TTS)

```bash
mcporter call minimax-mcp.text_to_audio text:"Hello world" voiceId:"male-qn-qingse"
```

### Video Generation

```bash
mcporter call minimax-mcp.generate_video prompt:"your video description"
```

## Sending to Telegram

**IMPORTANT**: When MiniMax returns a URL, it includes a query string with authentication token. You MUST use the FULL URL including all query parameters.

**Correct** (full URL with token):
```
<MINIMAX_OUTPUT_URL>?Expires=xxx&OSSAccessKeyId=xxx&Signature=xxx
```

**Incorrect** (URL without token):
```
<MINIMAX_OUTPUT_URL>
```

### Sending Image to Telegram

1. Call text_to_image and capture the FULL URL (including query string)
2. Send directly to Telegram using message tool with media parameter:

```python
message(
  action="send",
  channel="telegram",
  target="<chat_id>",
  media="<full_url_with_token>",
  message="Your caption"
)
```

### Sending Audio to Telegram

Same approach - use FULL URL with token:

```python
message(
  action="send",
  channel="telegram",
  target="<chat_id>",
  media="<full_url_with_token>",
  message="Your caption"
)
```

**IMPORTANT**: When sending audio, ALWAYS include the text content as the message caption below the audio!

Example:
```python
# Generate audio
audio_url = "<MINIMAX_AUDIO_URL>?Expires=xxx&Signature=xxx"
text_content = "呢段係你想既文字內容..."

# Send with both audio and text
message(
  action="send",
  channel="telegram",
  target="<chat_id>",
  media=audio_url,
  message=text_content  # Always include the text!
)
```

## Common Parameters

### text_to_image
- prompt: Text description of desired image
- aspectRatio: "1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"
- n: Number of images (1-9)
- model: Model to use (default: "image-01")

### text_to_audio
- text: Text to convert to speech
- voiceId: Voice ID (e.g., "male-qn-qingse", "female-shaonv")
- speed: Speech speed (0.5-2)
- emotion: "happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"
- format: "mp3", "wav", "pcm", "flac"
- languageBoost: Enhance recognition for specific languages/dialects
  - Cantonese: "Chinese,Yue" or "Chinese"
  - Mandarin: "Chinese" or "Chinese,Mandarin"
  - English: "English"
  - **Always include this when generating Cantonese audio!**

### generate_video
- prompt: Video description
- model: "T2V-01", "T2V-01-Director", "I2V-01", "I2V-01-Director", "I2V-01-live", "MiniMax-Hailuo-02"
- duration: 6 or 10 (for MiniMax-Hailuo-02)
- resolution: "768P", "1080P"

## Optimization & Troubleshooting

- **Timeout Management:** Video generation can take significant time (up to 20-30 minutes for high-quality 10s clips). Always pass a large `--timeout` value (e.g., `--timeout 1800000`) to `mcporter` to prevent early termination.
- **Gateway Turn Limit:** Most OpenClaw profiles have a 10-minute turn timeout (600000ms). To avoid being killed by the gateway, ALWAYS run `generate_video` with `background: true` or inside a background process.
- **Model Choice:** Use `MiniMax-Hailuo-02` for higher quality 10-second videos.

## Error Handling

If you get 403 Forbidden when sending to Telegram:
- Make sure you're using the FULL URL with query string
- The token (Signature) expires - regenerate if needed

## Notes

- MiniMax MCP must be configured with MINIMAX_RESOURCE_MODE=url in mcporter config
- Generated media URLs include authentication tokens that expire
- Always use the complete URL returned by MCP calls

## Cantonese (廣東話) Tips

When generating Cantonese audio:
- Use voice ID from Cantonese category (e.g., "Cantonese_PlayfulMan", "Cantonese_CuteGirl")
- **Always add**: `languageBoost:"Chinese,Yue"` or `languageBoost:"Chinese"`
- Example:
  ```bash
  mcporter call minimax-mcp.text_to_audio text:"新年快樂" voiceId:"Cantonese_PlayfulMan" languageBoost:"Chinese,Yue"
  ```
