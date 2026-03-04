# Social Post

> Post and reply to X/Twitter and Farcaster from one command.

[![Version](https://img.shields.io/badge/version-1.4.0-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-orange.svg)](https://openclaw.ai)

**Multi-platform social posting and replying with automatic validation, image uploads, threads, and cost transparency.**

**Repository:** [github.com/teeclaw/social-post](https://github.com/teeclaw/social-post)

## Features

✅ **Multi-account support** - Manage multiple Twitter accounts from one skill  
✅ **Auto-variation** - Avoid Twitter's duplicate content detection with `--vary` flag  
✅ **Multi-platform posting** - X/Twitter, Farcaster, or both simultaneously  
✅ **Reply support** - Reply to specific tweets and casts with text and images  
✅ **Draft preview** - See exactly what will be posted before confirmation  
✅ **Cost transparency** - Clear pricing for both platforms documented  
✅ **Thread support** - Auto-split long posts into numbered threads  
✅ **Image uploads** - Attach images to posts and replies on both platforms  
✅ **Link shortening** - Compress URLs to save characters  
✅ **Character validation** - Validates limits before posting (252 chars / 288 bytes)  
✅ **Balance monitoring** - Check Farcaster wallet balance anytime  
✅ **Auto-truncate** - Optional automatic text shortening  
✅ **Dry-run mode** - Test without actually posting  

## Table of Contents

- [Features](#features)
- [Quick Reference](#quick-reference)
- [Required Credentials](#required-credentials)
  - [X/Twitter Setup](#xtwitter-setup-)
  - [Farcaster Setup](#farcaster-setup-)
- [Platform Comparison](#platform-comparison)
- [Verify Setup](#verify-setup)
- [Quick Start](#quick-start)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## Quick Reference

| Platform | Cost | Credentials Location | Setup Time |
|----------|------|---------------------|------------|
| **X/Twitter** | Pay-per-use (consumption-based) | `~/.openclaw/.env` | 5-10 min |
| **Farcaster** | 0.001 USDC/cast | `~/.openclaw/farcaster-credentials.json` | 15-20 min |

**Before first use:**
1. Set up credentials for your platforms (see below)
2. For X/Twitter: Enable API access (consumption-based billing)
3. For Farcaster: Fund custody wallet with USDC on Base
4. Test with `--dry-run` flag
5. Start posting! 🚀

**Cost Model Comparison:**

| Platform | Model | Details |
|----------|-------|---------|
| **X/Twitter** | Consumption-based | Pay per API request. No tiers, no subscriptions. |
| **Farcaster** | Pay-per-cast | 0.001 USDC per cast. Pre-fund wallet on Base. |

**X/Twitter:**
- ✅ Pay per API request (post, read, etc.)
- ✅ No subscription tiers (eliminated)
- ✅ No monthly minimums
- ✅ Credit card billing through X Developer Portal
- 📊 See official pricing: https://developer.twitter.com/#pricing

**Farcaster:**
- ✅ Fixed cost: 0.001 USDC per cast
- ✅ Pre-fund wallet with USDC on Base chain
- ✅ Deducted instantly per cast

### Required Credentials

#### **X/Twitter Setup** 🐦

**Step 1: Get Developer Access**
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Apply for Developer Access
3. Wait for approval (1-2 days)
4. **Enable consumption-based billing**
   - Set up payment method (credit card)
   - No subscription tiers - pay only for what you use
   - Charged automatically per API request

**Step 2: Create App & Generate Keys**
1. Create a new App in Developer Portal
2. Set permissions to "Read and Write"
3. Generate Consumer Key/Secret and Access Token/Secret

**Step 3: Add to .env file**
Location: `/home/phan_harry/.openclaw/.env`
```bash
X_CONSUMER_KEY=your_consumer_key
X_CONSUMER_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
X_USERNAME=your_username  # Optional but recommended
X_USER_ID=your_user_id    # Optional but recommended
```

**💰 X/Twitter Costs:**
- **100% Consumption-based pricing** - NO subscription tiers
- **Pay per API request** - charged for each call you make
- No monthly fees, no minimums, no tier upgrades
- Billing is automatic based on actual usage
- Uses **OAuth 1.0a** authentication
- Requires X Developer account with approved API access + payment method
- See official pricing: https://developer.twitter.com/#pricing

**Important:** X API eliminated subscription tiers. It's now purely pay-per-use.

#### **Farcaster Setup** 🟣

**Step 1: Create Farcaster Account**

Option A - Use farcaster-agent skill (recommended):
```bash
# See /skills/farcaster-agent/SKILL.md for full guide
# This will automatically:
# - Register your FID
# - Add signer key
# - Save credentials to ~/.openclaw/farcaster-credentials.json
```

Option B - Use existing account:
- Export your custody wallet private key
- Export your signer private key
- Create credentials JSON manually

**Step 2: Verify Credentials File**

Location: `/home/phan_harry/.openclaw/farcaster-credentials.json`
```json
{
  "fid": "2684290",
  "custodyAddress": "0xB329...",
  "custodyPrivateKey": "0x601f1ea...",
  "signerPublicKey": "0x120986...",
  "signerPrivateKey": "0x0c8fe1a...",
  "createdAt": "2026-02-06T04:29:00.000Z"
}
```

**Step 3: Fund Custody Wallet (REQUIRED)**
```bash
# Check current balance
scripts/check-balance.sh

# Send USDC to custody address on Base chain
# Minimum: 0.1 USDC (~100 casts)
# Recommended: 1-5 USDC (1000-5000 casts)
```

**💰 Farcaster Costs:**
- **0.001 USDC per cast** (via x402 payment protocol)
- Deducted from custody wallet on **Base chain**
- Uses Neynar Hub API (`hub-api.neynar.com`)
- Payment to: `0xA6a8736f18f383f1cc2d938576933E5eA7Df01A1`

**Monitor Balance:**
```bash
# Quick check with script
scripts/check-balance.sh

# Or view on BaseScan
# https://basescan.org/address/<your_custody_address>
```

**Dependencies:**
- `python3` with `requests` and `requests_oauthlib` (for Twitter)
- `jq` (for JSON parsing)
- `curl` (for image uploads)

### Verify Setup

**1. Check credentials exist:**
```bash
# Check X/Twitter credentials
grep "^X_CONSUMER_KEY" ~/.openclaw/.env

# Check Farcaster credentials
ls -la ~/.openclaw/farcaster-credentials.json
```

**2. Check Farcaster wallet balance:**
```bash
scripts/check-balance.sh
# Should show:
# 💎 ETH Balance: X.XXX ETH
# 💵 USDC Balance: X.XXX USDC
# 📢 Casts Remaining: ~XXX
```

**3. Test with dry-run (doesn't actually post):**
```bash
scripts/post.sh --dry-run "Test message"

# Should show:
# ✅ Twitter: X/252 characters
# ✅ Farcaster: X/288 bytes
# === Draft Preview ===
# Would post to Twitter
# Would post to Farcaster
```

**4. Test single platform:**
```bash
# Test Twitter only
scripts/post.sh --twitter --dry-run "Twitter test"

# Test Farcaster only
scripts/post.sh --farcaster --dry-run "Farcaster test"
```

**Ready to post!** 🚀

### Quick Start

#### Posting

```bash
# Post to both platforms
scripts/post.sh "gm! Building onchain 🦞"

# Twitter only
scripts/post.sh --twitter "Twitter announcement"

# Farcaster only  
scripts/post.sh --farcaster "Farcaster thoughts"

# With image (both platforms)
scripts/post.sh --image ~/photo.jpg "Check this out!"

# Long text as thread
scripts/post.sh --thread "Very long announcement that exceeds character limits..."

# Shorten URLs to save characters
scripts/post.sh --shorten-links "Check out this cool site: https://very-long-url.com/path/to/page"

# Combine features
scripts/post.sh --thread --shorten-links --image ~/pic.jpg "Long text with links and image..."
```

#### Replying ✨ NEW

```bash
# Reply to Twitter tweet (get ID from URL: twitter.com/user/status/[ID])
scripts/reply.sh --twitter 1234567890123456789 "Great point!"

# Reply to Farcaster cast (get hash from URL: farcaster.xyz/~/conversations/[HASH])
scripts/reply.sh --farcaster 0xa1b2c3d4e5f6... "Interesting perspective!"

# Reply with image
scripts/reply.sh --twitter 123456789 --image ~/chart.png "Here's the data"

# Reply to both platforms (if you have IDs on both)
scripts/reply.sh --twitter 123456 --farcaster 0xabc... "Great discussion!"

# Shorten links in reply
scripts/reply.sh --twitter 123456 --shorten-links "More info: https://example.com/long-url"

# Quick reply without confirmation
scripts/reply.sh --twitter 123456 --yes "Quick acknowledgment"
```

### Features

✅ Post to Twitter, Farcaster, or both  
✅ **Reply to tweets and casts** - respond to specific posts on both platforms  
✅ Automatic character/byte limit validation  
✅ Image upload support (for posts and replies)  
✅ **Thread support** - split long text into numbered posts  
✅ **Link shortening** - compress URLs to save characters  
✅ Auto-truncate option  
✅ Dry-run mode  

### Platform Comparison

| Feature | X/Twitter | Farcaster |
|---------|-----------|-----------|
| **Cost model** | Consumption-based | Pay-per-cast |
| **Cost per post** | Charged per API request | 0.001 USDC |
| **Monthly fee** | None (pay-as-you-go) | None |
| **Payment method** | X API billing (credit card) | Custody wallet (Base) |
| **Character limit** | 252 chars* | 288 bytes* |
| **Rate limit** | Based on account | No limit (if funded) |
| **Image hosting** | Twitter API | catbox.moe |
| **API type** | OAuth 1.0a | Neynar Hub (x402) |

*With 10% safety buffer

### Platform Limits

- **Twitter:** 252 characters (280 with 10% buffer)
- **Farcaster:** 288 bytes (320 with 10% buffer)

### Image Hosting

- **Twitter:** Direct upload via Twitter API
- **Farcaster:** Uploaded to catbox.moe (free, no account needed)

### Troubleshooting

#### Credential Issues

**"X_CONSUMER_KEY not found" or Twitter auth errors:**
1. Check `.env` file exists: `ls -la ~/.openclaw/.env`
2. Verify credentials are set:
   ```bash
   grep "^X_" ~/.openclaw/.env
   ```
3. Ensure no extra spaces or quotes around values
4. Check file permissions: `chmod 600 ~/.openclaw/.env`
5. Test Python OAuth library:
   ```bash
   python3 -c "import requests_oauthlib"
   ```

**"Error: Farcaster credentials not found"**
1. Check file exists: `ls -la ~/.openclaw/farcaster-credentials.json`
2. Verify JSON is valid:
   ```bash
   jq . ~/.openclaw/farcaster-credentials.json
   ```
3. Ensure all required fields present:
   - `fid`, `custodyAddress`, `custodyPrivateKey`
   - `signerPublicKey`, `signerPrivateKey`
4. Set up Farcaster account using farcaster-agent skill

**"Insufficient USDC balance" or Farcaster post fails:**
1. Check wallet balance:
   ```bash
   scripts/check-balance.sh
   ```
2. If balance is low, send USDC to custody address on Base
3. Minimum: 0.1 USDC for ~100 casts
4. View on BaseScan to verify transaction

**"Invalid private key" or "signer error":**
1. Ensure private keys have `0x` prefix
2. Check custody key is Ethereum wallet format (64 hex chars)
3. Check signer key is Ed25519 format
4. Re-export keys if corrupted

#### Other Issues

**"Error: Twitter post script not found"**
- Ensure `/home/phan_harry/.openclaw/workspace/scripts/twitter-post.sh` exists
- Check script is executable: `chmod +x scripts/*.sh`

**"Error: Image not found"**
- Verify image path is correct
- Use absolute paths: `/full/path/to/image.jpg`
- Check file permissions and format (jpg, png, gif)

**Character limit exceeded:**
- Use `--truncate` flag to auto-shorten
- Use `--thread` to split into multiple posts
- Use `--shorten-links` to compress URLs
- Check byte count for emojis (count more on Farcaster)

**Rate limit errors (Twitter):**
- Rate limits based on account and usage
- Wait and retry later
- Check X Developer Portal for current limits

## Documentation

- **[SKILL.md](SKILL.md)** - Complete technical documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[X API Pricing](https://developer.twitter.com/#pricing)** - Official X API pricing
- **[Neynar Hub API](https://hub-api.neynar.com)** - Farcaster hub documentation

## Links

- **X Developer Portal:** https://developer.twitter.com/en/portal/dashboard
- **Farcaster Developer Docs:** https://docs.farcaster.xyz
- **OpenClaw:** https://openclaw.ai
- **ClawHub:** https://clawhub.com

## License

MIT © 0xdas

---

**Version 1.2.0** | Built for [OpenClaw](https://openclaw.ai) 🦞
