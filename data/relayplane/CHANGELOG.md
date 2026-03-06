# RelayPlane Skill Changelog

## v2.1.0 (2026-02-09)

### New Features
- **Doctor command:** `/relayplane doctor` diagnoses configuration and connectivity issues
- **Proxy management:** `/relayplane proxy [start|stop|status]` to control the proxy
- **Model aliases table:** `/relayplane models` now shows full alias reference
- **Dual CLI support:** Uses `relayplane` or `relayplane-proxy` CLIs as available

### Improvements
- Updated model aliases to reflect current routing (rp:best → Claude Sonnet 4)
- Better error messages with actionable guidance
- Help text includes all new commands
- Added comprehensive test suite (13 tests)

### Bug Fixes
- Fixed CLI detection for both `relayplane` and `relayplane-proxy`
- Improved HTTP fallback error handling
- Timeout handling for slow proxy responses

### Compatibility
- Requires `@relayplane/cli` v1.1.1+ for `doctor` command
- Works with `@relayplane/proxy` v1.1.2+
- Backwards compatible with v2.0.0 installations

---

## v2.0.0 (2026-02-08)

### Breaking Changes
- `/relayplane switch` command removed (use dashboard instead)
- Requires `@relayplane/proxy` v0.2.1+

### New Features
- **Telemetry control:** `/relayplane telemetry [on|off|status]`
- **Dashboard command:** `/relayplane dashboard` shows cloud dashboard link
- **CLI-first:** Uses `relayplane-proxy` CLI when available, falls back to HTTP
- **Better stats:** Improved formatting, supports both old and new data formats

### Upgrade Path
Existing installs will auto-upgrade. The skill now:
1. Checks for `relayplane-proxy` CLI first
2. Falls back to HTTP endpoints if CLI unavailable
3. Works with both old proxy versions and new

### Migration Notes
- Run `npm install -g @relayplane/proxy` to get latest CLI
- `/relayplane switch` now redirects to dashboard
- Telemetry settings persistent across restarts
