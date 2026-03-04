# Changelog

All notable changes to the social-post skill will be documented in this file.

## [1.5.0] - 2026-02-11

### Added
- **Dynamic Twitter tier detection**: Auto-detects Basic vs Premium/Premium+ accounts
  - Automatically adjusts character limits based on account subscription tier
  - Basic/Free accounts: 280 chars (252 with buffer)
  - Premium/Premium+ accounts: 25,000 chars (22,500 with buffer)
  - Smart caching: Tier cached for 24 hours to minimize API calls
  - Graceful fallback: Defaults to Basic tier if detection fails
- **Interactive threading choice for Premium accounts**:
  - When Premium user posts > 280 but < 25k chars, shows draft as single long post first
  - Prompts: "Thread this instead? (y/n)"
  - User can choose between single long post or threaded format
  - Respects `--thread` flag to force threading (skip prompt)
  - Respects `--auto-confirm` flag to skip all prompts
- **New tier detection library**: `lib/tier-detection.sh`
  - `detect_twitter_tier()`: Detects Basic/Premium/Premium+ tier via Twitter API
  - `get_twitter_char_limit()`: Returns raw character limit for account
  - `get_twitter_char_limit_buffered()`: Returns limit with 10% safety buffer
  - `cache_tier()`: Stores tier detection result with timestamp
  - `get_cached_tier()`: Retrieves cached tier if < 24h old
- **New flags**:
  - `--refresh-tier`: Force refresh account tier cache (useful after upgrading subscription)
  - Updated `--thread`: Now explicitly forces thread mode (was implicit before)
  - Updated `--auto-confirm`: Now skips ALL prompts including threading choice
- **Tier cache file**: `~/.openclaw/workspace/memory/twitter-account-tiers.json`
  - Stores tier detection results per account
  - JSON format: `{"account": {"tier": "premium", "checkedAt": 1234567890}}`
  - Auto-expires after 24 hours

### Changed
- **Dynamic character limits**: Twitter limits now adjust per account tier automatically
- **Updated validation**: `lib/validate.sh` now uses dynamic limits from tier detection
- **Updated threading logic**: `lib/threads.sh` respects Premium account 25k limit
- **Improved draft preview**: Shows detected account tier and available character limit
- **Enhanced help text**: Documents tier detection, Premium features, and new flags

### Technical
- Twitter API v2 used for tier detection
- Tier detection uses `/users/me` endpoint with `user.fields=subscription_type`
- Fallback detection via test post attempt (checks error message for char limit)
- Cache invalidation after 24 hours or with `--refresh-tier` flag
- Multi-account aware: Each account can have different tier
- Zero breaking changes: Existing workflows continue to work

### Use Cases
- Premium users can post long-form threads without artificial character limits
- Basic users get accurate 280-char validation
- Automatic adaptation when upgrading from Basic to Premium
- Single skill supports both Basic and Premium posting workflows

## [1.4.0] - 2026-02-10

### Added
- **Auto-variation feature**: New `--vary` flag to avoid Twitter's duplicate content detection
  - Automatically introduces subtle, natural differences to text
  - Prevents "duplicate content" errors when posting similar text from multiple accounts
  - Variations include: emoji additions, punctuation changes, spacing adjustments, synonym swaps
  - Shows both original and varied text in draft preview
  - Guarantees visible variation (will always change something)
  - Works seamlessly with all existing features (images, threads, multi-account)
- **New variation library**: `lib/variation.sh` with intelligent text transformation functions
  - `vary_text()`: Applies 2-3 random variations
  - `vary_punctuation()`: Changes sentence-ending punctuation
  - `vary_emoji()`: Adds/removes emojis
  - `vary_spacing()`: Adjusts line breaks
  - `vary_wording()`: Subtle synonym swaps

### Features
- Bypass Twitter's anti-spam duplicate content blocker
- Natural, human-like text variations
- Preview variations before posting
- No manual rewriting needed

### Use Case
Solves the problem of posting the same announcement from multiple Twitter accounts (e.g., company + personal accounts) without triggering Twitter's duplicate content detection.

### Technical
- Uses bash `shuf` for randomization
- Attempts up to 10 variation tries to ensure change
- Fallback emoji injection if no variation applied
- Integrates into existing post.sh workflow

## [1.3.0] - 2026-02-10

### Added
- **Multi-account support**: Manage multiple Twitter accounts from one skill
  - New `--account <name>` flag for both `post.sh` and `reply.sh`
  - Support for custom credential prefixes in `.env` file
  - Example: `MYACCOUNT_API_KEY`, `MYACCOUNT_API_KEY_SECRET`, etc.
  - Automatic credential loading based on account name
  - Account name displayed in draft preview
- **Enhanced credential management**:
  - `get_twitter_credentials()` function in `lib/twitter.sh`
  - Dynamic credential selection based on `TWITTER_ACCOUNT` env var
  - Backward compatibility with default `X_*` credentials
- **Documentation**:
  - Multi-account setup guide in SKILL.md
  - Naming convention for custom accounts
  - Usage examples for switching between accounts
  - Updated help text with `--account` flag

### Features
- Post from multiple Twitter accounts without changing config
- Reply from any configured account
- Seamless switching via `--account` flag
- Default account fallback (X_* credentials)
- Account validation before posting

### Technical
- Environment variable-based account switching
- Prefix-based credential mapping (e.g., `oxdasx` → `OXDASX_*`)
- No breaking changes to existing single-account setups
- Works with all existing features (images, threads, replies, etc.)

## [1.2.0] - 2026-02-08

### Added
- **Reply functionality**: New `reply.sh` script to reply to tweets and casts
  - Reply to Twitter tweets with `--twitter <tweet_id>`
  - Reply to Farcaster casts with `--farcaster <cast_hash>`
  - Reply to both platforms simultaneously
  - Support for image attachments in replies
  - Link shortening in replies with `--shorten-links`
  - Character/byte validation for replies
  - Draft preview before posting replies
  - Dry-run mode for testing replies
- **Documentation**: Complete reply examples and usage in SKILL.md and README.md
- **ID extraction guide**: How to get Tweet IDs and Farcaster cast hashes from URLs

### Features
- Reply to specific tweets using tweet ID from URL
- Reply to specific casts using cast hash from URL  
- All posting features available for replies (images, link shortening, truncation)
- Proper threading support for replies
- Cost transparency for replies (same as regular posts)

### Technical
- Extended Twitter library with reply support using `in_reply_to_tweet_id`
- Extended Farcaster library with reply support using `parentCastId`
- Image upload support for both Twitter and Farcaster replies
- Reuses existing validation and link shortening libraries

## [1.1.0] - 2026-02-06

### Added
- **Draft preview**: Shows exact text, image, and target platforms before posting
- **Confirmation prompt**: Interactive "Proceed with posting? (y/n)" confirmation
- **`--yes` flag**: Skip confirmation for automated workflows
- **Balance checking script**: New `check-balance.sh` to monitor Farcaster wallet
  - Shows ETH and USDC balances on Base
  - Displays remaining casts estimate
  - Warns when balance is low (<0.1 USDC)
  - Provides BaseScan link for detailed view

### Changed
- **Updated X/Twitter API pricing documentation**:
  - ✅ Corrected to **consumption-based model** (no tiers)
  - ✅ Removed outdated subscription tier references (Basic/Pro)
  - ✅ Clarified pay-per-API-request model
  - ✅ Added official pricing link: https://developer.twitter.com/#pricing
  - ✅ Updated setup instructions to reflect billing model
- **Enhanced cost transparency**:
  - Added platform comparison table
  - Documented Farcaster costs (0.001 USDC per cast)
  - Explained x402 payment protocol
  - Included Neynar Hub payment address
  - Added cost model comparison section

### Improved
- **README.md**:
  - Quick reference table with costs and setup time
  - Step-by-step credential setup for both platforms
  - Platform comparison table (cost model, limits, billing)
  - Comprehensive troubleshooting section for credentials
  - Verification steps for testing setup
- **SKILL.md**:
  - Detailed "Setup & Credentials" section
  - Security warnings for private key handling
  - Cost breakdown for both platforms
  - Official links and references
- **Help text** in `post.sh`:
  - Added cost information
  - Added `--yes` flag documentation
  - Updated platform limits section

### Fixed
- ❌ Removed incorrect "free tier" references for X API
- ❌ Removed outdated tier pricing ($100/mo, $200/mo, $5k/mo)
- ❌ Fixed `.env` file parsing error (quoted mnemonic)
- ✅ Corrected all cost documentation to reflect current pricing models

### Documentation
- Added setup time estimates (X: 5-10 min, Farcaster: 15-20 min)
- Documented credential file locations and formats
- Added wallet funding requirements for Farcaster
- Included credential verification commands
- Enhanced troubleshooting with specific error scenarios

## [1.0.0] - 2026-02-06

### Added
- **Multi-platform posting**: Post to Twitter, Farcaster, or both simultaneously
- **Thread support**: Automatically split long text into numbered, connected threads
- **Link shortening**: Compress URLs using TinyURL to save characters
- **Image upload support**: Upload images to both platforms
  - Twitter: Direct upload via Twitter API
  - Farcaster: Upload to catbox.moe with proper embed support
- **Character/byte limit validation**: 252 chars (Twitter) / 288 bytes (Farcaster) with 10% safety buffer
- **Platform-specific posting**: `--twitter` and `--farcaster` flags
- **Auto-truncate option**: `--truncate` flag to automatically shorten text
- **Dry-run mode**: `--dry-run` flag to preview without posting
- **Comprehensive error handling**: Clear error messages and troubleshooting guidance

### Features
- Character count validation before posting
- Shows exact overflow amount when over limit
- Smart thread splitting by sentences and paragraphs
- 2-second delays between thread parts for rate limiting
- Image attachment on first post of thread
- Proper reply chains (Twitter: `in_reply_to_tweet_id`, Farcaster: `parentCastId`)
- Automatic credential loading from `.env` and Farcaster credentials file

### Documentation
- Complete SKILL.md with usage examples
- Detailed README.md with setup instructions
- Troubleshooting guide for common errors
- Credential requirements and verification steps

### Technical
- Bash scripts with modular library architecture
- Twitter OAuth 1.0a integration
- Farcaster hub integration with x402 payments
- Python dependencies: `requests`, `requests_oauthlib`
- External dependencies: `curl`, `jq`
