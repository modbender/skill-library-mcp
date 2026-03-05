# PCClaw — OpenClaw for Windows

<p align="center">
  <img src="web/pcclaw-logo.png" alt="PCClaw" width="160">
</p>

<p align="center">
  <strong>OpenClaw Skills are macOS-only. Until now.</strong><br>
  14 Windows-native skills + 2 cross-platform skills + one-command installer.
</p>

<p align="center">
  <a href="https://openclaw.irisgo.xyz">Website</a> &bull;
  <a href="https://join.slack.com/t/irisgo-community/shared_invite/zt-3i3qm7sds-A4WIKXk4rQHgG1FUg1i0Og">Community Slack</a> &bull;
  <a href="https://irisgo.ai">IrisGo.AI</a>
</p>

---

**v2.0.0** | A community project by [IrisGo.AI](https://irisgo.ai)

## The Skills Gap

[OpenClaw](https://openclaw.ai) has a rich skill ecosystem — but it was built for macOS. Windows users got left behind.

PCClaw fills the gap:

```
                    macOS (built-in)          Windows (PCClaw)
  ─────────────────────────────────────────────────────────────
  Notes             apple-notes, bear-notes   sticky-notes
  Tasks             apple-reminders           ms-todo, google-tasks
  File Search       —                         win-files
  System Info       —                         win-sysinfo (WMI)
  Local AI          —                         win-ai-local (Ollama)
  Notifications     osascript                 win-notify (WinRT)
  Screen Capture    peekaboo                  win-screenshot
  Clipboard         pbcopy / pbpaste          win-clipboard
  Packages          homebrew                  winget
  OCR               —                         win-ocr (built-in)
  UI Automation     —                         win-ui-auto (.NET)
  Speech-to-Text    —                         win-whisper (GPU/NPU)
  Text-to-Speech    say                       win-tts (SAPI 5)
  Browser           —                         win-browser (Edge/Chrome)
  Scheduler         —                         win-scheduler (Task Scheduler)
  Messages          imsg                      — (coming soon)
```

## Quick Start

```powershell
irm openclaw.irisgo.xyz/i | iex
```

That's it. The installer handles Node.js, Git, OpenClaw, skills, and [Moltbook](https://moltbook.com) registration.

### One-liner with Parameters

```powershell
# Anthropic (default)
.\install.ps1 -ApiKey "sk-ant-your-key" -AgentName "my_agent"

# OpenAI
.\install.ps1 -ApiKey "sk-your-key" -AgentName "my_agent" -Provider "openai"

# GLM (Zhipu AI)
.\install.ps1 -ApiKey "your-glm-key" -AgentName "my_agent" -Provider "glm"

# Local LLM (Ollama, LM Studio, etc.)
.\install.ps1 -ApiKey "any" -AgentName "my_agent" -Provider "openai-compatible" -BaseUrl "http://localhost:11434/v1"
```

## Supported Providers

| Provider | Models |
|----------|--------|
| Anthropic | Claude (default) |
| OpenAI | GPT |
| Google Gemini | Gemini |
| GLM | Zhipu AI |
| OpenAI Compatible | Ollama, LM Studio, vLLM, etc. |

**BYOK** — Your API key stays on your machine. We never collect or transmit it.

---

## Skills

### Windows-Native (14)

| Skill | What it does | Dependencies |
|-------|-------------|--------------|
| [`win-notify`](skills/win-notify/SKILL.md) | Toast notifications via WinRT API | None (built-in) |
| [`winget`](skills/winget/SKILL.md) | Search, install, upgrade software | winget (pre-installed) |
| [`win-screenshot`](skills/win-screenshot/SKILL.md) | Full screen, region, or window capture | None (built-in .NET) |
| [`win-clipboard`](skills/win-clipboard/SKILL.md) | Read/write text, images, file lists | None (built-in .NET) |
| [`win-ui-auto`](skills/win-ui-auto/SKILL.md) | Inspect, click, type, manage windows | None (built-in .NET + Win32) |
| [`win-ocr`](skills/win-ocr/SKILL.md) | Extract text from images — multilingual, offline | None (built-in Windows OCR) |
| [`win-whisper`](skills/win-whisper/SKILL.md) | Speech-to-text — local, GPU/NPU accelerated | whisper.cpp (one-time download) |
| [`win-tts`](skills/win-tts/SKILL.md) | Text-to-speech — speak aloud or save to WAV, multilingual | None (built-in .NET) |
| [`win-files`](skills/win-files/SKILL.md) | Search, browse, manage files and folders, disk info | None (built-in PowerShell) |
| [`sticky-notes`](skills/sticky-notes/SKILL.md) | Read, search, create Windows Sticky Notes | None (built-in winsqlite3) |
| [`win-sysinfo`](skills/win-sysinfo/SKILL.md) | CPU, RAM, battery, GPU, NPU, network, processes | None (built-in WMI) |
| [`win-ai-local`](skills/win-ai-local/SKILL.md) | Local LLM inference, model management, AI hardware detection | [Ollama](https://ollama.com) |
| [`win-browser`](skills/win-browser/SKILL.md) | Bookmarks, history, downloads from Edge/Chrome, open URLs | None (built-in winsqlite3) |
| [`win-scheduler`](skills/win-scheduler/SKILL.md) | Create, manage, schedule automated tasks and reminders | None (built-in ScheduledTasks) |

### Cross-Platform (2)

| Skill | What it does | macOS counterpart |
|-------|-------------|-------------------|
| [`ms-todo`](skills/ms-todo/SKILL.md) | Microsoft To Do via Graph API | `apple-reminders` |
| [`google-tasks`](skills/google-tasks/SKILL.md) | Google Tasks via REST API | `apple-reminders` |

### Install Skills

```powershell
Copy-Item -Recurse .\skills\* "$env:USERPROFILE\.openclaw\skills\"
```

Skills load automatically on the next OpenClaw session.

---

## What the Installer Does

1. **Checks prerequisites** — Installs Node.js and Git if needed (via winget)
2. **Installs OpenClaw** — `npm install -g openclaw@latest`
3. **Configures your LLM** — Sets up API key for your chosen provider
4. **Registers on Moltbook** — Creates your AI agent profile and posts first message
5. **Launches onboard wizard** — Gets you started immediately

## Requirements

- Windows 10/11 (PowerShell 5.1+)
- Internet connection
- LLM API key (any supported provider) — or a local LLM

---

## After Installation

1. **Claim your agent** — Visit the claim URL shown after installation
2. **Run OpenClaw** — Just type `openclaw` in terminal
3. **Install PCClaw skills** — Copy skills to `~/.openclaw/skills/`
4. **Share your profile** — Show off on social media!

## Troubleshooting

**"Node.js not found after installation"** — Close and reopen your terminal, then run the installer again.

**"winget not available"** — Install Node.js manually from https://nodejs.org, then run the installer again.

**"Moltbook registration failed"** — Your agent name might be taken, or the API might be temporarily down. Try a different name.

**"OpenClaw won't start"** — Make sure your API key is valid and has sufficient credits.

## Files Created

```
%USERPROFILE%\
├── .openclaw\
│   ├── config.json     # OpenClaw configuration
│   └── skills\         # PCClaw skills (after install)
└── .config\
    └── moltbook\
        └── credentials.json
```

## Uninstall

```powershell
npm uninstall -g openclaw
Remove-Item -Recurse "$env:USERPROFILE\.openclaw"
Remove-Item -Recurse "$env:USERPROFILE\.config\moltbook"
```

---

## Contributing

We welcome new Windows skills! See [CHANGELOG.md](CHANGELOG.md) for version history.

1. Create a folder under `skills/<skill-name>/`
2. Add a `SKILL.md` following [OpenClaw's skill format](https://openclaw.ai)
3. Test locally by copying to `~/.openclaw/skills/`
4. Open a PR

## Links

- [PCClaw Website](https://openclaw.irisgo.xyz)
- [OpenClaw Official](https://openclaw.ai)
- [Moltbook](https://moltbook.com)
- [IrisGo.AI](https://irisgo.ai)
- [Community Slack](https://join.slack.com/t/irisgo-community/shared_invite/zt-3i3qm7sds-A4WIKXk4rQHgG1FUg1i0Og)

## License

MIT

---

*PCClaw is a community project by [IrisGo.AI](https://irisgo.ai). Not officially affiliated with OpenClaw.*
