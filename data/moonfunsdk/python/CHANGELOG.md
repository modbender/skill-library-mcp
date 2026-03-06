# Changelog

All notable changes to MoonfunSDK will be documented in this file.

## [1.0.6] - Current

### Changed
- Token tag classification set to "Ai Agent"
- Improved categorization for AI-generated tokens

## [1.0.5] - 2024

### Added
- Enhanced authentication mechanism
- Improved security for platform interactions

### Changed
- Optimized login flow for better reliability
- Session management improvements

## [1.0.4] - 2024

### Added
- Support for selling tokens with low liquidity
- Fallback to min_received=0 when getAmountOut fails

### Changed
- Trading functions marked as experimental
- Complete alignment with bsc_meme_creator for buy & sell operations

### Fixed
- Critical fix for selling new tokens with low liquidity

## [1.0.3] - 2024

### Added
- Support for buying new tokens (holders=0)
- Fallback to min_received=0 when getAmountOut fails in buy_token()

### Changed
- Trading functionality marked with experimental warning

### Known Issues
- Price estimation may fail on new/low-liquidity tokens

## [1.0.2] - 2024

### Changed
- Simplified initialization (only private key required)
- Enhanced transaction reliability
- Dynamic gas estimation with safety buffer

### Improved
- Compatibility with various RPC endpoints
- Error messages and exception handling

## [1.0.1] - 2024

### Changed
- Internal optimizations
- Enhanced platform integration

## [1.0.0] - 2024

### Added
- Initial release
- Token creation with AI-generated images
- Basic trading functionality (buy/sell)
- Balance queries
- Platform integration with MoonnFun
- BSC blockchain support
- Comprehensive error handling

### Security
- Local private key management
- Cryptographic signature authentication
- Balance-gated API access
