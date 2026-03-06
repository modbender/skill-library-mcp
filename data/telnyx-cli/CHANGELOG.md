# Changelog

## [1.1.0] - 2026-02-13

### Added
- Companion Skills coordination layer for account lifecycle management
  - Pre-flight checklist: CLI installed → API key exists → key valid
  - Auto-handoff to **telnyx-bot-signup** for account creation, signin, and key refresh
  - Auto-handoff to **telnyx-freemium-upgrade** when freemium restrictions are hit
  - Upgrade cache awareness (`~/.telnyx/upgrade.json`) to avoid redundant handoffs
  - Fallback messages when companion skills are not installed
- Full lifecycle flow: install → auth → operate → upgrade → retry

## [1.0.0] - 2025-05-15

### Added
- Initial release
- Telnyx CLI integration for Clawdbot
- Messaging commands (send, list, get)
- Phone number management (list, search, buy, release)
- Call log viewing
- Webhook management and debugger
- Account info and balance queries
- Output format support (table, JSON, CSV)
- Bulk messaging and webhook monitoring examples
