# Changelog

## [1.1.0] - 2026-02-12
### Changed
- Backend architecture now uses shared runtime services (`voice_runtime.py`) across API and local loop.
- API startup now owns runtime initialization through lifespan hooks.
- Added baseline API test scaffolding under `tests/`.

## [1.0.2] - 2026-02-12
### Changed
- Converted the skill to client-only operation; removed service startup from `SKILL.md`.
- Removed `scripts/start.sh` from the skill package path.
- Updated skill instructions to require a separately managed backend at `http://localhost:8000`.
- Cleaned `client.py` by removing dead multipart/experimental code.

## [1.0.0] - 2026-01-28
### Added
- Initial release of the Voice Agent Skill.
- Client script (`client.py`) with `transcribe`, `synthesize`, and `health` commands.
- Zero-dependency architecture using standard library `urllib`.
- Dockerized backend support (`ai-voice-backend` image).

### Changed
- Refactored `client.py` to remove live audio tools (`speak`/`listen`) in favor of a pure file-based file I/O interface for better compatibility with messaging platforms (WhatsApp/Telegram).
