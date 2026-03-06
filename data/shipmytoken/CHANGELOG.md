# Changelog

All notable changes to Ship My Token will be documented in this file.

## [1.5.1] - 2026-02-22

### Added
- Social share template in post-launch output with ready-to-copy tweet
- Revenue framing in welcome message (passive SOL earnings from trading fees)

## [1.5.0] - 2026-02-17

### Added
- README with install instructions and feature overview

### Fixed
- Version check showing false update notice when local version is newer than GitHub release
- Version comparison now uses proper semver (only notifies when remote > local)

### Changed
- Restructured SKILL.md for better rendering and readability
- Update notification now shows the `npx skills` install method

## [1.4.0] - 2026-02-10

### Added
- Default `pump` suffix on mint addresses — tokens now match pump.fun's native address format automatically
- Uses `solana-keygen grind --ends-with pump` (exact case); falls back silently to random address if not installed
- `--skip-pump-suffix` flag to opt out and use a random mint address

## [1.3.0] - 2026-02-09

### Added
- Vanity address support: `--vanity-prefix` and `--vanity-suffix` flags for custom token mint addresses
- Uses `solana-keygen grind` (Solana CLI) — fast, cross-platform, case-insensitive
- Base58 validation, 5-char max, 2-minute timeout with clear error messages

## [1.2.0] - 2026-02-09

### Added
- "What's next" section after successful token launch guiding users to fee claiming, portfolio, fee sharing, and launching another token

### Fixed
- Claimable fees showing 0 for tokens with fee sharing configured — now sums per-token distributable fees via getMinimumDistributableFee
- Bonding curve progress overstated by ~54% due to hardcoded SOL constants — now uses on-chain token reserves from PumpFun Global state
- Earnings queries ("how much did I earn") triggering on-chain fee claims instead of showing read-only portfolio

## [1.1.1] - 2026-02-09

### Changed
- Agent no longer refuses token launches based on content — Pump.fun is permissionless and handles its own moderation

## [1.1.0] - 2026-02-09

### Added
- Automatic daily portfolio recaps with 24h debounce — works via heartbeat (OpenClaw), cron, or on user interaction as fallback
- Setup flow now configures the platform's scheduling mechanism during onboarding (HEARTBEAT.md, cron, or fallback)

### Changed
- Post-launch output no longer shows default fee sharing split — only shown if user customized the split or if it failed

## [1.0.2] - 2026-02-09

### Fixed
- Stats and fee claiming broken by pump-sdk v1.27.0 API change. The SDK split into offline (`PumpSdk`) and online (`OnlinePumpSdk`) classes — updated stats, fees, and launch scripts to use the correct classes.
- Launch with `--initial-buy` was also broken (calling `fetchGlobal`/`fetchFeeConfig` on the offline SDK).
- Pinned `@pump-fun/pump-sdk` and `@pump-fun/pump-swap-sdk` to `^1.27.0` / `^1.13.0` to prevent future silent breakage from `latest`.

## [1.0.1] - 2025-02-09

### Fixed
- Fee sharing configuration failing on every token launch (error 6013: NotEnoughRemainingAccounts). The `createFeeSharingConfig` initializes the creator as the sole shareholder, so `updateFeeShares` needs the creator passed as a current shareholder.

## [1.0.0] - 2025-02-08

### Added
- Token launch on Pumpfun via chat (name, symbol, image, optional metadata)
- Automatic fee sharing: 90% creator / 10% Ship My Token
- Fee claiming for accumulated creator trading fees
- Fee sharing updates with custom splits (up to 10 shareholders)
- Portfolio view with token status, price, and bonding curve progress
- Daily recap reports
- Secure wallet creation and backup (stored in `~/.shipmytoken/`)
- Post-install onboarding flow with guided setup
- Universal Agent Skills spec compatibility (Claude Code, Cursor, Windsurf, OpenClaw)
- Version check on setup to notify users of available updates

### Fixed
- Fee claim crash when fee sharing is not configured
- Minimum SOL requirement corrected from 0.005 to 0.01 SOL
- SKILL.md frontmatter parsing issue with colons in description
