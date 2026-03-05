# PCClaw — OpenClaw for Windows

14 Windows-native AI agent skills + 2 cross-platform + one-command PowerShell installer.

## What it does

OpenClaw's skill ecosystem was built for macOS. PCClaw fills the gap with native Windows skills that use built-in .NET, WinRT, WMI, and Win32 APIs — most require zero external dependencies.

## Skills

### Windows-Native (14)

| Skill | What it does |
|-------|-------------|
| win-notify | Toast notifications via WinRT API |
| winget | Search, install, upgrade software |
| win-screenshot | Full screen, region, or window capture |
| win-clipboard | Read/write text, images, file lists |
| win-ui-auto | UI automation — inspect, click, type, manage windows |
| win-ocr | Multilingual offline OCR (built-in Windows) |
| win-whisper | Speech-to-text, GPU/NPU accelerated |
| win-tts | Text-to-speech via SAPI 5, multilingual |
| win-files | File search, browse, disk info |
| sticky-notes | Read, search, create Windows Sticky Notes |
| win-sysinfo | CPU, RAM, GPU, NPU, battery, network via WMI |
| win-ai-local | Local LLM inference + model management (Ollama) |
| win-browser | Edge/Chrome bookmarks, history, downloads |
| win-scheduler | Create and manage Windows Task Scheduler tasks |

### Cross-Platform (2)

| Skill | What it does | macOS counterpart |
|-------|-------------|-------------------|
| ms-todo | Microsoft To Do via Graph API | apple-reminders |
| google-tasks | Google Tasks via REST API | apple-reminders |

## Install

```powershell
irm openclaw.irisgo.xyz/i | iex
```

The installer handles Node.js, Git, OpenClaw, skills, LLM configuration, and Moltbook registration.

Or install skills manually:

```powershell
Copy-Item -Recurse .\skills\* "$env:USERPROFILE\.openclaw\skills\"
```

## Supported LLM Providers

- Anthropic (Claude) — default
- OpenAI (GPT)
- Google (Gemini)
- GLM (Zhipu AI)
- OpenAI Compatible (Ollama, LM Studio, vLLM)

BYOK — your API key stays on your machine.

## Requirements

- Windows 10/11
- PowerShell 5.1+
- LLM API key (any provider) or local LLM

## Links

- Website: https://openclaw.irisgo.xyz
- GitHub: https://github.com/IrisGoLab/PCClaw
- Community: https://irisgo.slack.com

## Author

Built by [IrisGo.AI](https://irisgo.ai) — open source, MIT licensed.
