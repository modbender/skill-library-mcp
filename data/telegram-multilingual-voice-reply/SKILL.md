---
name: telegram-multilingual-voice-reply
description: "Smart Telegram reply workflow for OpenClaw: if the user sends text, reply with text; if the user sends a voice note/audio, transcribe locally using the installed mlx_audio (default Qwen3-ASR on Apple Silicon), then generate a meaningful reply in the same language. Send back a Telegram voice note with a caption so the user receives ONE message containing both voice+text (the caption text must match the voice content exactly). Follow the input language (Chinese→Chinese, English→English) unless the user explicitly requests a different language."
---

# Telegram Multilingual Voice Reply（多语言语音智能回复）

目标：在 Telegram 跟 OpenClaw 聊天时实现“语音优先 + 多语言跟随”的智能回复：

- **你发文字** → 默认只发**文字回复**（不触发 ASR；默认也不触发 TTS）。
- **你发语音** → 本地 STT 转写后理解语义，生成“有意义的回复”。默认用 **一条 Voice Message + caption** 发送（语音+文字同条，且内容一致）。
- **语言跟随**：你用中文我用中文；你用英文我用英文；除非你明确要求指定语言（也支持方言/口吻要求，但 TTS 受模型限制）。

## Default models

- STT 默认：`mlx-community/Qwen3-ASR-0.6B-8bit`
- （可选）Forced alignment：`mlx-community/Qwen3-ForcedAligner-0.6B-8bit`

> 需要模型清单/更多上游用法：`references/qwen3-asr-notes.md`

## How to use (agent workflow)

### A) 输入是文字（text message）

- **永不触发 ASR**。
- 默认只发文字回复。
- 只有当用户明确说“用语音回复/发语音/voice reply”时：
  - 生成回复文本 `reply_text`
  - 生成 voice note（见下方“Telegram 单条消息”）
  - 发送 **一条** Voice Message（caption=`reply_text`，且与语音内容一致）

### B) 输入是语音（voice note / audio）

- 默认必走 ASR（否则无法“智能回复”）。
- 然后根据用户意图决定是否触发 TTS：
  - 用户说“只要文字/文字回复/不要语音” → **ASR + 文字回复**（不 TTS）。
  - 否则（默认真实场景） → **ASR + 生成回复 + 单条 voice+caption**（走 TTS）。

#### 语音→转写（本地、Apple Silicon）

```bash
python3 scripts/mlx_asr.py --audio /path/to/audio.ogg --language Chinese
```

> 注：Telegram 常见是 ogg/opus。`mlx_asr.py` 已支持 CLI fallback，并会在需要时用 ffmpeg 转 wav。

#### Telegram 单条消息（语音 + 文字在同一条）

Telegram 支持给 voice note 附带 caption，使得“语音条 + 下方文字”显示为**同一条消息**（你截图里的效果）。

1) 用 `scripts/mlx_tts_voice.py` 生成 Telegram 友好的 `.ogg/opus`：

```bash
python3 scripts/mlx_tts_voice.py --text "<reply_text>" --out /tmp/reply.ogg
```

2) 用 OpenClaw `message` 工具发送（voice note + caption）：
- `asVoice: true`
- `path/filePath`: 上一步生成的 `reply.ogg`
- `caption`: **同一段 reply_text**（必须与语音内容一致）

> 说明：OpenClaw 的 `tts` 工具通常会把语音作为单独消息发送，无法保证 caption 同条承载。

## Options / overrides

- 用户说“只用文字回复/不要语音” → 只发文字。
- 用户说“只用语音回复/不要文字” → 只发语音（仍然保持内容一致）。
- 用户说“用英文/用中文回复” → 覆盖默认语言跟随策略。

## Troubleshooting

- `failed to import mlx_audio`：当前 `python3` 环境里没有安装到 `mlx_audio`。请用安装 `mlx_audio` 的同一个解释器/venv 运行。
- 音频格式问题：Telegram 常见 voice note 是 `ogg/opus`。如转写失败，优先把音频转成 wav 再试（或确保系统具备相应解码能力）。
