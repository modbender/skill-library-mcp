# Changelog

## v2.2.0 - 2026-03-03

- **Security**: Fixed webhook template injection vulnerability (PR #2 by @heavygee):
  - Added JSON-aware template rendering with proper escaping to prevent injection attacks.
  - Added `validate_host_port()` function to reject dangerous characters in host/port values.
  - Applied validation across all HTTP request construction points.
- **Breaking**: Renamed work directory from `custom/work` to `custom/restart-guard-work` for better clarity.
  - Update your config file paths if using custom locations.
- Added comprehensive security tests for template injection and URL validation.
- Improved error handling for invalid host/port configurations.

## v2.1.1 - 2026-02-28

- Hardened command execution in `postcheck.py` and guardian diagnostics:
  - removed shell-wrapper fallback and enforce strict non-shell parsing.
  - reject shell metacharacters in verify/diagnostics command strings.
- Improved trigger-failure resilience in `restart.py`:
  - keep guardian running when restart trigger fails (fallback recovery + delivery still proceed).
  - add immediate failure event back to origin session on trigger failure.
  - resolve `lsof` via explicit binary discovery to avoid PATH-related failures.
- Improved test portability:
  - replaced machine-specific absolute script paths with repo-relative paths.
- Added repository hygiene files:
  - `LICENSE` (MIT) and `.gitignore` (`__pycache__`, Python cache artifacts).
- Added unit tests for restart runtime helpers (`lsof` resolution, trigger failure reporting).
- Docs: added explicit `suspicious` rationale and security boundary notes (external notification necessity, no extra port binding, strict anti-injection stance).

## v2.1.0 - 2026-02-27

- Reworked restart flow to strict state machine with invariant:
  - `down_detected && start_attempted && up_healthy`
- Added origin-session proactive ACK contract (`restart_guard.result.v1`) and structured delivery metadata.
- Added disaster delivery route with retry budget:
  - `origin session -> agent:main:main -> discovered external channels`
- Added diagnostics bundle generation for failure paths:
  - concise external summary + local detailed diagnostics files.
- Added zero-config auto entry (`scripts/auto_restart.py`) and channel discovery (`scripts/discover_channels.py`).
- Fixed config parsing robustness and backward compatibility mappings for legacy fields.
- Updated docs to bilingual format (`README.md`, `SKILL.md`) and added implementation spec.
- Added unit tests for parser, state machine, delivery fallback, channel discovery, and origin selection.
