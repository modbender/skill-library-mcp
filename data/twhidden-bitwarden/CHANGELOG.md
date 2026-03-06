# Changelog

## v1.0.5 (2026-02-18)

### Changed
- **Fixed title/branding** — Display name is now "Bitwarden / Vaultwarden" (removed "TWhidden" from title)
- **Addressed security concerns** — Added security manifest header to bw.sh, improved documentation
- **Added ClawHub link** to GitHub README

## v1.0.4 (2026-02-18)

### Changed
- **Rewrote registration to pure bash + openssl** — removed Python dependency entirely
  - Key derivation (PBKDF2, HKDF) now uses `openssl kdf` commands
  - AES-256-CBC encryption uses `openssl enc`
  - HMAC-SHA256 uses `openssl dgst`
  - HTTP registration uses `curl` instead of Python `requests`
  - JSON parsing uses `grep` instead of Python `json`
- Removed `python3`, `cryptography`, and `requests` from required dependencies
- Added `openssl` (3.x+) and `curl` as required binaries

### Why
The Python dependency was unnecessary overhead for a bash-native skill. The new implementation uses only standard Unix tools (openssl, curl, xxd, base64) and is more portable and lightweight.

## v1.0.3

- Initial ClawHub release
- Bitwarden/Vaultwarden CLI wrapper with registration, login, CRUD operations
