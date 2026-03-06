# Changelog - Pet-Me-Master

## [2.1.0] - 2026-02-28

### ✅ Verified Working
- **Fully autonomous petting system** tested and confirmed operational
- Auto-detection of ready gotchis via blockchain checks
- Instant Telegram notifications when gotchis ready
- 1-hour grace period with auto-pet fallback
- Dynamic scheduling based on actual pet times

### Improved
- Enhanced auto-pet fallback with better state management
- Dynamic check scheduling (adjusts to actual pet time)
- Improved notification delivery (instant Telegram via bot API)
- Better error handling and process management

### Added
- `schedule-dynamic-check.sh` - Smart scheduling based on cooldown
- Background process management for fallback execution
- State persistence between cycles

### Testing
- Confirmed working through multiple cycles (Feb 22-28, 2026)
- Auto-pet successfully executed when user unavailable
- Manual petting properly detected and fallback cancelled

---

## [2.0.2] - 2026-02-22

### Fixed
- Reminder notification timing
- State file persistence
- Cron scheduling conflicts

---

## [2.0.0] - 2026-02-22

### Added
- Bankr wallet integration for gasless petting
- Multi-gotchi batch petting support
- Auto-reminder system with fallback

---

## [1.0.0] - 2026-02-13

### Initial Release
- Basic gotchi petting via Foundry cast
- Manual execution only
