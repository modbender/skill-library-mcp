# Changelog

All notable changes to PCClaw will be documented in this file.

## [2.0.0] - 2026-02-12

### Added
- `win-scheduler` skill — Windows Task Scheduler automation. Create one-time, daily, weekly, logon, and startup tasks. Manage, enable/disable, trigger, export, and delete scheduled tasks. Organizes PCClaw tasks in a dedicated `\PCClaw\` folder. Zero external dependencies (built-in ScheduledTasks PowerShell module).

### Changed
- Bumped version to 2.0.0 (16 total skills: 14 Windows-native + 2 cross-platform)
- Installer now deploys 16 skills

## [1.9.0] - 2026-02-12

### Added
- `win-browser` skill — Browser integration for Edge and Chrome. Read and search bookmarks (JSON), browsing history and downloads (SQLite via winsqlite3.dll), get active tab titles, open URLs. Supports multiple browser profiles. Zero external dependencies.

### Changed
- Bumped version to 1.9.0
- Installer now deploys 15 skills (added win-browser)

## [1.8.0] - 2026-02-12

### Added
- `win-ai-local` skill — Local AI inference via Ollama REST API. Generate text, chat, embeddings, manage models — all on-device with no cloud dependency. Includes AI hardware detection (NPU, GPU, DirectML, WinML). Recommended models table for AIPC hardware (8-32 GB RAM). Requires Ollama installed.

### Changed
- Bumped version to 1.8.0

## [1.7.0] - 2026-02-12

### Added
- `win-sysinfo` skill — System diagnostics: CPU, RAM, battery, GPU, NPU, network, running processes, startup programs, OS info. Uses WMI (Get-CimInstance) with zero external dependencies. Includes NPU/AI accelerator detection for AIPC hardware.

### Changed
- Bumped version to 1.7.0

## [1.6.0] - 2026-02-12

### Added
- `win-files` skill — Search, browse, and manage files and folders. File search by name or content, recent files, folder size breakdown, disk info, create/copy/move/delete operations. Zero external dependencies (built-in PowerShell cmdlets).
- `sticky-notes` skill — Read, search, create, update, and export Windows Sticky Notes. Accesses the local SQLite database via `winsqlite3.dll` P/Invoke with full UTF-8 support. Zero external dependencies.

### Changed
- Bumped version to 1.6.0

## [1.5.1] - 2026-02-12

### Added
- `win-tts` skill — Text-to-speech using Windows built-in SAPI 5 speech engine. Speak text aloud or save to WAV. Supports voice selection, speed/volume control, SSML for prosody, and multilingual output (English + Chinese). Zero external dependencies.

### Changed
- Bumped version to 1.5.1

## [1.5.0] - 2026-02-09

### Added
- `win-whisper` skill — Record audio and transcribe speech to text using Whisper, running fully local. Uses whisper.cpp v1.8.3 with OpenBLAS acceleration. Supports WAV/MP3/FLAC/OGG, auto language detection, translation to English, SRT subtitle output, Voice Activity Detection, and real-time streaming transcription. Includes zero-dependency audio recording via Windows Multimedia API (winmm.dll). Optional Intel GPU/NPU acceleration via OpenVINO.

### Changed
- Bumped version to 1.5.0

## [1.4.0] - 2026-02-09

### Added
- `win-ocr` skill — Extract text from images and screenshots using Windows built-in OCR (Windows.Media.Ocr WinRT API). Supports multilingual recognition (English, Traditional Chinese, and any installed language pack). Includes word-level bounding boxes for click targeting. Fully offline, zero external dependencies.

### Changed
- Bumped version to 1.4.0

## [1.3.0] - 2026-02-09

### Added
- `win-ui-auto` skill — Windows UI automation: inspect UI element trees, click, double-click, right-click, type text, send hotkeys, focus/move/resize/minimize/maximize/close windows, launch/quit apps, scroll. The Windows counterpart to Peekaboo (macOS). Uses .NET UI Automation + Win32 APIs with zero external dependencies.

### Changed
- Bumped version to 1.3.0

## [1.2.0] - 2026-02-09

### Added
- `win-screenshot` skill — Screen capture (full screen, region, specific window) + window listing via .NET System.Drawing (zero dependencies)
- `win-clipboard` skill — Clipboard read/write for text, images, and file lists via .NET Windows.Forms (zero dependencies)

### Changed
- Bumped version to 1.2.0

## [1.1.0] - 2026-02-09

### Added
- **Skills pack** — PCClaw is now an installer + skills bundle
- `win-notify` skill — Native Windows toast notifications via PowerShell/WinRT (zero dependencies)
- `winget` skill — Windows Package Manager integration (search, install, upgrade, export)
- `ms-todo` skill — Microsoft To Do via Graph API (cross-platform counterpart to `apple-reminders`)
- `google-tasks` skill — Google Tasks via `gog` CLI or REST API (cross-platform)
- `.gitignore` — Exclude macOS `.DS_Store` files
- `CHANGELOG.md` — This file

### Changed
- Rebranded from "OpenClaw Installer" to **PCClaw** — reflecting the expanded scope beyond just installation
- Updated README with skills documentation and PCClaw identity

## [1.0.1] - 2026-02-06

### Fixed
- PowerShell window no longer closes instantly on error or completion ([PR #1](https://github.com/IrisGoLab/pcclaw/pull/1) by @TonySincerely)
- Synced `web/i.ps1` with `quick-install.ps1` after PR merge

## [1.0.0] - 2026-02-04

### Added
- Initial release
- One-command Windows installer (`irm openclaw.irisgo.xyz/i | iex`)
- Interactive provider selection (Anthropic, OpenAI, Gemini, GLM, OpenAI-compatible)
- Automatic prerequisites installation (Node.js, Git via winget)
- OpenClaw installation and LLM configuration
- Moltbook agent registration and first post
- Landing page at `openclaw.irisgo.xyz`
- BYOK (Bring Your Own Key) — API keys stay local
