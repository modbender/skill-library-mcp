---
name: voice-message
version: 1.0.4
description: Send voice messages across chat channels (Telegram, Discord, Feishu/Lark, Signal, WhatsApp, and others) using edge-tts for text-to-speech and ffmpeg for audio conversion. IMPORTANT - Feishu/Lark does NOT support asVoice=true via the message tool; you MUST use this skill to send voice messages on Feishu, otherwise it will send a file attachment instead of a voice bubble. | 通过 edge-tts 文字转语音和 ffmpeg 音频转换，在各聊天渠道（Telegram、Discord、飞书、Signal、WhatsApp 等）发送语音消息。飞书不支持 message 工具的 asVoice=true，必须使用本 skill 才能发送语音气泡而非文件附件。
metadata:
  openclaw:
    emoji: "🎤"
---

# Voice Message

Send text as voice messages to any chat channel.

## Prerequisites

- `edge-tts` — Microsoft Edge TTS (`pip install edge-tts`)
- `ffmpeg` / `ffprobe` — audio conversion and duration detection

## Default Voices

- Chinese: `zh-CN-XiaoxiaoNeural`
- English: `en-US-JennyNeural`
- Other languages: see [references/voices.md](references/voices.md)

## Step 1: Generate Voice File

Use `scripts/gen_voice.sh` to convert text to an ogg/opus file:

```bash
scripts/gen_voice.sh "你好" /tmp/voice.ogg
scripts/gen_voice.sh "Hello" /tmp/voice.ogg en-US-JennyNeural
```

Arguments: `<text> <output.ogg> [voice]`
- If voice is omitted, defaults to `zh-CN-XiaoxiaoNeural`.

## Step 2: Send by Channel

### Generic (Telegram, Signal, WhatsApp, etc.)

Use the message tool directly:

```
action=send, asVoice=true, filePath=/tmp/voice.ogg
```

This works for most channels. Telegram confirmed working.

### Feishu/Lark

⚠️ Feishu does NOT support `asVoice=true` via the message tool. You must use the dedicated script.

Use `scripts/send_feishu_voice.sh`:

```bash
scripts/send_feishu_voice.sh /tmp/voice.ogg <receive_id> <tenant_access_token> [receive_id_type]
```

- `receive_id_type`: `open_id` (default), `chat_id`, `user_id`, `union_id`, `email`
- The script handles upload (as opus with duration) and sends as audio message type to produce a voice bubble.
- To get `tenant_access_token`, use the Feishu tenant token API with your app credentials.

### Discord

Discord voice messages require a waveform and special flags.

1. Generate ogg with `scripts/gen_voice.sh`
2. Generate waveform: `python3 scripts/gen_waveform.py /tmp/voice.ogg`
   - Outputs JSON: `{"duration_secs": 4.2, "waveform": "base64..."}`
3. Send via Discord API with `flags: 8192` (IS_VOICE_MESSAGE) and the waveform/duration in attachments metadata.
   - Missing waveform/duration causes error 50161.

### Fallback

If `asVoice=true` does not produce a voice bubble on a channel:
1. Try sending via the platform's native API
2. If native API unavailable, send as audio file attachment
