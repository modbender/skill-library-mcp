# Changelog

## 1.0.2 (2026-02-15)

### Security
- Move daemon socket and PID file from `/tmp/` to `~/.her-voice/` — prevents local symlink attacks and unauthorized access
- Set restrictive permissions on config directory (`0700`), config file (`0600`), socket (`0600`), and PID file (`0600`)
- Add max message size limit (1MB) to daemon protocol — prevents memory exhaustion via oversized requests
- Add chunk size validation (100MB) on both client and visualizer — prevents allocation bombs from malicious responses
- Validate `os.execv` target paths — ensure resolved Python is a real interpreter inside a valid venv (`pyvenv.cfg` check)
- Refuse to follow symlinks for socket and PID file paths in daemon startup
- Escape regex metacharacters in visualizer binary path before passing to `pgrep`
- Replace `strcpy` with bounded `strlcpy` in Swift socket code — prevents potential buffer overflow
- Bound stdin read to 10MB in `speak.py`
- Read daemon socket path from config in Swift visualizer instead of hardcoding `/tmp/`
- Add 30s client timeout on daemon connections — prevents connection starvation from hung clients
- Add 500MB total audio memory cap in Swift visualizer — prevents unbounded allocation from rogue responses
- Add `atexit` cleanup for temp files in `speak.py` — prevents temp file leaks on unexpected exit
- Handle corrupt PID files gracefully — prevents crashes on malformed data

### Code Quality
- Centralize language-to-Kokoro code mapping (`LANG_MAP`) in `config.py` — eliminates triple duplication across Python files
- Add type hints to all Python function signatures
- Replace fragile `enumerate` + tuple unpacking with direct iteration in PyTorch generator handling
- Use `copy.deepcopy` instead of `json.loads(json.dumps(...))` for config deep copy
- Narrow `except Exception` to specific exceptions in `resolve_pytorch_voice` — log warning instead of silent fallback
- Guard `pgrep` PID parsing against `ValueError` from unexpected output
- Extract PID file reading into `_read_pid` helper with consistent error handling
- Fix misleading "Trying apt install" message in `check_espeak` on Linux
- Sync Swift language map with canonical `LANG_MAP` (add `zh`, `ko` entries)

### Documentation
- Explain `SKILL_DIR` placeholder used in code examples
- Add uninstall instructions
- Explicitly state Windows is not supported
- Explain voice quality rating scale
- Add PyTorch-specific errors to troubleshooting table
- Clarify `daemon.auto_start` is advisory-only — the daemon never self-starts

## 1.0.1 (2026-02-15)
- Rewrote and condensed documentation in SKILL.md for improved clarity and focus.
- Simplified the description to highlight key use cases and features.
- Core functionality and configuration details remain unchanged.
- No new features or breaking changes introduced in this version.

## 1.0.0 (2026-02-15)
- Initial release
- Streaming TTS via Kokoro 82M — MLX (Apple Silicon) + PyTorch (everywhere else)
- Real-time audio visualizer (60fps, native macOS, Cocoa + AVFoundation)
- Persist mode: visualizer stays on screen, drag-and-drop audio playback
- ⌘V paste-to-speak: streams directly from TTS daemon with full visualizer animation
- TTS daemon for persistent model warmth (~1s faster per call, optional)
- Smart setup wizard with cross-platform detection
- Configurable: voice, speed, visualizer, notification sound, daemon
- Voice blending support (mix multiple Kokoro voices)
- Default blend: 60% af_heart + 40% af_sky @ 1.05x speed
- Window position remembered between sessions
- User name pronunciation config for non-English names
