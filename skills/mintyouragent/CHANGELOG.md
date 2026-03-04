# Changelog

All notable changes to MintYourAgent are documented here.

## [3.5.0] - 2026-02-24

### Added
- **Poker**: Heads-up Texas Hold'em with real SOL stakes via on-chain escrow
- **Soul/Link**: Extract agent personality (SOUL.md) and link identity to mintyouragent.com
- **Native Launches**: Bundled create + buy transactions via pump.fun (atomic, like the webapp)
- **Balance Validation**: Pre-launch check ensures sufficient SOL before spending
- **Preflight Checks**: Server-side rate limit validation before launch transactions

### Fixed
- **install.sh**: Corrected GitHub URL (was pointing to wrong repo)
- **uninstall.sh**: Now references correct data directory (~/.mintyouragent/)
- **SKILL.md**: Fixed misleading "Free" messaging — launches cost 0.01 SOL platform fee
- **Version alignment**: pyproject.toml and Dockerfile now match SKILL.md version

### Changed
- Version bump from 3.0.0 to 3.5.0 across all package files
- Comparison table in SKILL.md updated to remove inaccurate "Free" row

## [3.0.0] - 2026-02-09

### Added
- **New Commands**: tokens, history, backup, verify, status, trending, leaderboard, stats, airdrop, transfer, sign
- **Command Aliases**: l=launch, w=wallet, s=setup, c=config, h=history, t=tokens, b=backup
- **.env File Support**: Auto-loads from current dir or ~/.mintyouragent/
- **Network Selection**: --network mainnet/devnet/testnet
- **All Output Formats**: --format text/json/csv/table
- **QR Code Support**: Optional with `pip install qrcode`
- **Clipboard Support**: Optional with `pip install pyperclip`
- **Progress Bars**: With ETA estimation
- **"Did You Mean?"**: Typo suggestions for commands
- **Full Help**: --help-all shows complete reference
- **Preview Mode**: --preview shows what would be launched
- **Backup System**: Automatic backups before destructive operations
- **Wallet Integrity**: Checksum verification on load
- **Correlation IDs**: For request tracing in logs

### Changed
- Input sanitization on all user inputs
- Path safety validation (no traversal, no symlinks)
- Windows compatibility (optional fcntl)
- BOM handling for file encoding
- Error messages now suggest fixes

### Security
- All 200 audit issues addressed
- Secure key import via stdin
- Memory clearing after key use
- File locking to prevent race conditions
- Secure deletion (overwrite before unlink)

## [2.3.0] - 2026-02-09

### Added
- All CLI flags: --json, --format, --quiet, --debug, --timestamps
- Path overrides: --config-file, --wallet-file, --log-file
- Network options: --api-url, --rpc-url, --proxy, --user-agent
- Behavior: --timeout, --retry-count, --priority-fee, --skip-balance-check

### Security
- Input sanitization
- Path traversal protection
- Symlink protection
- Config schema validation

## [2.2.0] - 2026-02-09

### Added
- Audit logging to ~/.mintyouragent/audit.log
- Retry logic with exponential backoff
- Graceful signal handling (SIGINT/SIGTERM)
- Real money confirmation prompts
- Exit code enum for consistent errors
- Type hints throughout
- Threaded spinner

### Security
- Key import via stdin (not visible in ps aux)
- Memory clearing with ctypes.memset
- Secure file deletion
- File locking with fcntl
- Wallet checksums for integrity
- Sanitized error messages

## [2.1.0] - 2026-02-09

### Added
- Secure local signing (prepare→sign→submit)
- AI initial buy decision (--ai-initial-buy)
- First-launch tips (--tips)
- Transaction verification before signing

### Security
- Private keys never leave machine
- Blockhash validation
- Signer verification
- Moved sensitive files to ~/.mintyouragent/

## [2.0.0] - 2026-02-08

### Added
- Pure Python implementation
- No bash/jq/solana-cli dependencies
- Cross-platform (Windows, Mac, Linux)
- Dry run mode

### Changed
- Complete rewrite from shell scripts

## [1.0.0] - 2026-02-07

### Added
- Initial release
- Basic token launching
- Wallet management
