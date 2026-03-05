# Changelog

All notable changes to the Rug Checker skill are documented here.

## [0.1.3] — 2026-02-16

### Added

- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+:
  - Compact first response with key risk drivers
  - Component-style quick actions for follow-up analysis
  - Fallback numbered actions when components are unavailable

### Changed

- README: added "OpenClaw Discord v2 Ready" compatibility section.
- `SKILL.md` metadata tags now include `discord` and `discord-v2`.

## [0.1.2] — 2026-02-15

### Fixed

- **P0 CRITICAL: Name resolution picks wrong token** — `detect-token.sh` no longer auto-picks the highest-liquidity DexScreener result when given a name. Instead, it returns a `candidates` array (up to 5, de-duped by address) and requires the agent to present them to the user for confirmation. SKILL.md updated with candidate workflow instructions. A rug checker that checks the wrong token is worse than no rug checker.
- **P0 HIGH: Holder stats show nonsense for blue chips** — Rugcheck returns `totalHolders=0` and `topHolders=[]` for many established tokens (e.g., BONK). The report now renders "N/A" instead of "0" for holder count, and the holder concentration check shows `❓ ?/10 NO DATA` when holder data is unavailable.
- **P0 HIGH: Rate limiter math bug** — `cf_rate_wait()` sliding window was broken: `wait_time = 60 - (now - window_start) + 1` always evaluated to ~1s because `window_start = now - 60`. Reimplemented as a proper sliding window that finds the OLDEST timestamp in the window and sleeps until it expires.
- **P0 MEDIUM: SKILL.md missing YAML front matter** — Added standard YAML front matter (name, description, version, author, tags, permissions) for ClawHub and AgentSkills compatibility.

### Improved

- **P1: Composite scoring excludes missing data** — Checks with `data_available=false` now use `weight=0` in the composite calculation, so missing data doesn't inflate or deflate scores. Only real data contributes.
- **P1: format-report.sh fallbacks** — Replaced `source common.sh || true` with proper fallback functions (`format_usd`, `format_number`, `format_pct`, `CF_DISCLAIMER`) so the report renderer works even if common.sh fails.
- **User-Agent bumped** to `CacheForge-DeFi-Stack/0.1.2`.

## [0.1.1] — 2026-02-15

### Fixed

- **CRITICAL: Rugged override** — Tokens with `rugged=true` from Rugcheck.xyz now force composite score ≥85 and tier CRITICAL regardless of weighted average. A confirmed rug can never score SAFE.
- **HIGH: `bc` dependency check** — Added `bc` to `cf_check_deps()` alongside `curl` and `jq`. Missing `bc` now prints install instructions and exits instead of silently defaulting all comparisons to 0.
- **MEDIUM: JSON-RPC param safety** — `solana_mint_info()` and `solana_token_supply()` now use `jq -n --arg` to build RPC params instead of bash string interpolation.
- **MEDIUM: "Should I buy" trigger removed** — Removed from SKILL.md activation triggers. Added redirect guidance for buy-intent queries. Replaced "looks solid" SAFE commentary with neutral language. Strengthened NOT FINANCIAL ADVICE disclaimer.
- **MEDIUM: Data unavailable indicator** — Checks with no data now show `❓` indicator with `?/10` and "NO DATA" label instead of misleading `🟠 5/10`. Added `data_available` boolean to check JSON output.
- **MEDIUM: `format_usd()` fixed** — Replaced broken sed-based implementation with the working suffix-based formatter ($1.2B, $3.4M, $56.7K, $12.34).
- **MEDIUM: README example complete** — Updated example report to show all 10 checks (added Liquidity Depth and Transfer Fee).

### Improved

- **Rate limiter locking** — `cf_rate_wait()` now uses `flock` advisory locking to prevent concurrent write corruption.
- **Temp file cleanup** — Added `cf_mktemp()` with EXIT trap to clean up temp files on unexpected termination.
- **DRY consolidation** — `fmt_usd()` in format-report.sh now delegates to `format_usd()` in common.sh.
- **Dynamic box header** — Report header box now auto-sizes to fit long token names instead of overflowing at 62 chars.
- **Name resolution warning** — `detect-token.sh` now emits a warning when resolving tokens by name, with a `name_resolution_warning` field in JSON output.
- **SOLANA_RPC_URL trust boundary** — Documented in SECURITY.md as a known trust boundary.
- **Tagline accuracy** — Changed "Just truth" to "Just data" in README.
- **ClawHub URLs** — Removed unverified clawhub.dev URLs and `clawhub install` commands; marked as "coming soon".
- **User-Agent updated** to 0.1.1.

## [0.1.0] — 2026-02-15

### Added

- **10-point risk analysis engine** (`analyze-risk.sh`)
  - Mint Authority check (weight 2.0)
  - Freeze Authority check (weight 1.5)
  - Holder Concentration analysis (weight 1.5)
  - LP Lock Status detection (weight 2.0)
  - Token Age assessment (weight 1.0)
  - Liquidity Depth analysis (weight 1.0)
  - Rugcheck.xyz automated flag ingestion (weight 1.0)
  - Insider network detection (weight 1.5)
  - Transfer fee / hidden tax detection (weight 1.0)
  - Jupiter verification status (weight 0.5)

- **Token resolution** (`detect-token.sh`)
  - Resolve by Solana address (direct lookup)
  - Resolve by name/symbol (DexScreener search → highest liquidity match)
  - Fallback to Solana RPC when DexScreener has no data

- **Visual report card** (`format-report.sh`)
  - Unicode box-drawing header
  - Market overview table
  - Per-check risk bars with emoji indicators
  - 50-character composite score bar
  - Data source availability matrix
  - Direct links to DexScreener, Rugcheck, Solscan, Birdeye
  - Automated disclaimer

- **Shared library** (`common.sh`)
  - DexScreener API wrappers (search, token, pairs)
  - Rugcheck.xyz API wrappers (full report)
  - Solana RPC wrappers (mint info, token supply)
  - Token-bucket rate limiting per domain
  - HTTP retry with exponential backoff
  - Number/USD/percentage formatting helpers
  - Solana address validation

- **Documentation**
  - Agent-facing skill definition (SKILL.md)
  - Human-facing README with example output
  - Security model documentation (SECURITY.md)
  - Test plan with real commands (TESTING.md)
  - MIT license

### Data Sources

- Rugcheck.xyz API (no auth required)
- DexScreener API (no auth required, 300 req/min)
- Solana mainnet RPC (no auth required)

### Known Limitations

- Solana only (no EVM chain support)
- Rugcheck has data gaps for some stablecoins (USDC, USDT)
- Jupiter verification data from Rugcheck may lag
- Public Solana RPC has aggressive rate limits on `getTokenLargestAccounts`
