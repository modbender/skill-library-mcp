---
name: windows-tts
description: 在 Windows 11 上"直接发声"的 TTS（从 WSL2/TUI 调用 powershell.exe + System.Speech）。适用于用户说"说出来/读出来/语音播报/用TTS"，或反馈"没声音/tts 生成的 mp3 是空的/播不出来"，以及需要中文语音但 OpenClaw 内置 tts 不可用时。
---

# Windows TTS (WSL2)

Use Windows built-in TTS via `powershell.exe` so audio plays through the **Windows 默认输出设备**（无需 WSLg/PulseAudio）。

## 什么时候用这个 skill（触发提示）

当用户出现以下表达时，优先用本 skill，而不是 OpenClaw 内置 `tts`（后者可能生成空 mp3 或在某些环境无声）：
- "说出来 / 读出来 / 念一下 / 语音播报 / 用 TTS"
- "还没声音 / 没声音 / 播不出来"
- "中文语音"且希望**直接从电脑扬声器播放**

> 注意：本 skill 是"直接播放"，不会返回音频文件路径。

## Quick start（直接说出来）

Run from WSL:

```bash
bash {baseDir}/scripts/say.sh "你好，我是你的助手。"
```

## List installed voices

```bash
bash {baseDir}/scripts/list_voices.sh
```

## Speak with a specific voice

```bash
bash {baseDir}/scripts/say.sh --voice "VOICE_NAME" "你好，我以后会用这个声音说话。"
```

## Notes

- If you embed PowerShell directly in bash, remember: **escape `$`** or use outer single quotes; otherwise bash expands `$s` and breaks the command.
- If the user reports errors like `=New-Object` or `TypeName:` prompts, prefer the provided scripts instead of ad-hoc quoting.
