# Changelog

All notable changes to the Ringez Phone Calling API.

## [1.0.7] - 2026-02-09

### Added
- **Idempotency Support** — Prevent duplicate calls using `idempotency_key` parameter
  - 5-minute deduplication window
  - Returns existing call details if duplicate detected
  - Recommended format: `<session_id>_<timestamp>_<random>`

### Improved
- Documentation reorganized for better readability
- Added clear use case examples
- Improved SEO structure with better headings

---

## [1.0.6] - 2026-02-09

### Added
- "Support the Service" section explaining the indie creator context
- Friendly, honest messaging about recharging
- Sample conversation flows for low balance scenarios
- AI agent tone guidelines (grateful, honest, brief)

### Changed
- Clarified that 5 free minutes are for testing
- Improved "Handling Low Balance" section with human-friendly approach

---

## [1.0.5] - 2026-02-09

### Added
- Clear separation between AI Skill and Website responsibilities
- Complete API examples for managing active calls:
  - Check call status
  - End/hang up calls
  - DTMF tones for IVR navigation
  - Hold/unhold functionality
- Call history with pagination
- Low balance handling guidance

### Changed
- Marked wallet operations as web-only (PCI compliance)

---

## [1.0.4] - 2026-02-09

### Added
- Three complete usage scenarios with step-by-step examples
- Mode selection quick reference table
- Example chat flows

---

## [1.0.3] - 2026-02-09

### Changed
- Default mode changed from `direct` to `bridge` for safety
- Smart fallback: if no bridge number, uses direct mode automatically

---

## [1.0.0] - 2026-02-06

### Initial Release
- International phone calling to 200+ countries
- Email signup with OTP verification
- 5 free minutes for testing
- PayPal (USD) and UPI (INR) payments
- Bridge and direct calling modes
- Session-based authentication
