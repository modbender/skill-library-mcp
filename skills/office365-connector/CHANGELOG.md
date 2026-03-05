# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-02-09

### Added - Multi-Account Support

**New Features:**
- Multi-account configuration system
- Per-account authentication and token management
- Account switching via `--account=<name>` flag
- Default account selection
- Legacy single-account import tool
- Comprehensive multi-account documentation

**New Files:**
- `accounts.js` - Account management CLI
- `MULTI-ACCOUNT.md` - Complete usage guide
- `CREDITS.md` - Attribution and acknowledgments
- `CHANGELOG.md` - This file

**Enhanced Files:**
- `auth.js` - Now supports multiple accounts with `--account=` flag
- `email.js` - Multi-account email operations
- `calendar.js` - Multi-account calendar operations
- `send-email.js` - Send from specific accounts
- `cancel-event.js` - Cancel events from specific accounts

### Changed

- Token storage moved from single file to per-account files in `~/.openclaw/auth/office365/`
- Account configuration stored in `~/.openclaw/auth/office365-accounts.json`
- All CLI scripts now accept `--account=<name>` parameter

### Maintained

- Full backward compatibility with v1.0.0
- Environment variable fallback (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
- All original functionality preserved
- No breaking changes for existing single-account users

### Migration

Existing users can:
1. Continue using without changes (environment variables still work)
2. Import existing setup: `node accounts.js import-legacy`
3. Add additional accounts: `node accounts.js add <name> ...`

## [1.0.0] - Original Release

Original Office 365 Connector skill with single-account support.

**Features:**
- OAuth 2.0 Device Code Flow authentication
- Email operations (read, search, send, reply)
- Calendar operations (read events, cancel)
- Contact operations (read, search)
- Automatic token refresh
- Azure App Registration setup guide
