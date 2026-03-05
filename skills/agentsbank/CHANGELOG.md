# Changelog

All notable changes to the AgentsBank SDK are documented in this file.

## [1.0.7] - 2026-02-11

### Changed
- Cleaned up repository: removed generated `index.d.mts` build artifact
- Removed old `CHANGELOG_1.0.4.md` (consolidated into single CHANGELOG.md)
- Improved `.npmignore` to exclude non-essential files

### Dependencies
- No dependency changes

## [1.0.6] - 2026-02-11

### Added
- Comprehensive error types and handling in new `src/errors.ts`
- Enhanced type definitions for better IDE support and type safety
- Improved error messages for SDK consumers

### Changed
- Enhanced client implementation with better request handling
- Updated type definitions in `src/types.ts` for clarity and completeness
- Improved error propagation throughout SDK

### Fixed
- Better error context in API responses
- Type consistency across client methods

### Dependencies
- Updated package dependencies to latest compatible versions

## [1.0.4] - 2026-02-10

### Added
- `estimateGas` parameter validation (address format, amount value, chain type)
- `listWallets` pagination support with `limit` and `offset` parameters
- Enhanced client-side validation for all SDK methods

### Fixed
- **estimateGas**: Full parameter validation before API calls
- **signMessage**: Improved key format handling for EVM and Solana chains
- **listWallets**: Pagination support for bulk wallet listing
- Better error messages and graceful fallbacks across all chains

### Changed
- Validation happens earlier (client-side) to catch errors before API calls
- More robust key handling across Ethereum, BSC, Solana, and Bitcoin chains

## [1.0.3] - 2026-02-06

### Fixed
- Fixed missing `wallet_id` in wallet response objects

## [1.0.2] - 2026-02-06

### Added
- X-API-Key authentication support for programmatic access

## [1.0.1] - 2026-02-03

### Added
- Initial SDK release
- Multi-chain wallet support (Ethereum, BSC, Solana, Bitcoin)
- Transaction creation and monitoring
- Message signing capabilities
- Agent self-registration
- Balance and transaction history queries
