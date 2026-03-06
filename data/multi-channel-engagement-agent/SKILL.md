---
name: multi-channel-engagement-agent
description: Autonomous social media engagement across Twitter, Farcaster, and Moltbook. Fetches trending content, generates persona-driven contextual replies, and tracks state to prevent duplicates. Use when you want to engage with trending posts, reply to social media content, build audience through authentic engagement, or automate social presence across multiple platforms. Triggers on "engage on twitter", "farcaster engagement", "reply to trending", "social engagement bot", "multi-platform engagement", "autonomous social replies". Features include content filtering, mention tracking, webhook notifications, user blacklist/whitelist, analytics tracking, and quote tweet/recast support.
---

# Multi-Channel Engagement Agent

Autonomous engagement bot for **Twitter**, **Farcaster**, and **Moltbook**. Fetches trending content, generates persona-driven contextual replies, tracks replied posts to prevent duplicates.

## Quick Start

### 1. Create Config

Copy `assets/sample-config.json` to `config.json` and fill in your credentials (see Setup Guides section below).

### 2. Run Engagement

```bash
# Engage on specific platform
node scripts/engage.mjs --platform twitter
node scripts/engage.mjs --platform farcaster
node scripts/engage.mjs --platform moltbook

# Engage on all enabled platforms
node scripts/engage.mjs --all
```

## Dependencies & Setup Guides

This skill integrates multiple platforms. Setup each one:

### Farcaster Setup (required for Farcaster engagement)

**Skill:** `farcaster-agent` (https://clawhub.com/skills/farcaster-agent)

**Prerequisites:**
- Minimum **$1 ETH or USDC** on any chain (Ethereum, Optimism, Base, Arbitrum, Polygon)
- **Minimum 0.0005 ETH on Optimism** for FID registration

**Auto-setup command:**
```bash
clawhub install farcaster-agent
PRIVATE_KEY=0x... node src/auto-setup.js "Your first cast"
```

**What you'll get:**
```json
{
  "fid": 123456,
  "neynarApiKey": "...",
  "signerPrivateKey": "...",
  "custodyPrivateKey": "0x..."
}
```

**Cost breakdown:**
- FID registration: ~$0.20 (requires 0.0005 ETH + gas)
- Signer key: ~$0.05
- Bridging: ~$0.10-0.20
- **Total: ~$0.50 (budget $1 for safety)**

**Neynar API:**
- Free tier: 300 requests/minute
- Get key: https://dev.neynar.com

---

### Twitter Setup (required for Twitter engagement)

**Two options:**

**Option A: x-api (OAuth 1.0a, official)**
- Get credentials at https://developer.x.com/en/portal/dashboard
- Create Project → App
- Set permissions: **Read and Write**
- Rate limits: Tweets 50/15min, Searches 450/15min

**Option B: AISA API (alternative, good for trending)**
- AISA API endpoint: `https://api.aisa.one/apis/v1/twitter/tweet/advanced_search`
- Get API key at https://aisa.one
- Searches via AISA are fast and reliable for trending
- Config: add `aisaTwitterApiKey` to twitter platform

**Recommendation:** Use AISA for trending discovery, x-api for posting (replies)

---

### Moltbook Setup (required for Moltbook engagement)

**API Base:** `https://www.moltbook.com/api/v1` (note: use `www`)

**Get API key:**
1. Register at https://www.moltbook.com
2. Get token from account settings
3. Verify: https://www.moltbook.com/api/v1/posts

**⚠️ CRITICAL:** Only send API key to `www.moltbook.com`, never to other domains

**Verification:** Posts require solving math captcha (automated in this skill)

---

### Summary Config

All credentials go into `config.json`:
```json
{
  "platforms": {
    "twitter": { "oauth": {...} },
    "farcaster": { "neynarApiKey": "...", "fid": 123, ... },
    "moltbook": { "apiKey": "..." }
  }
}
```

---

## Core Workflow

### Step 1: Load Configuration
- Read `config.json` for platform credentials
- Load persona settings (tone, values, style)
- Load state from `engagement-state.json` (replied posts)

### Step 2: Fetch Trending
**Twitter (OAuth 1.0a via x-api approach):**
```javascript
// Uses twitter-api-v2 with OAuth 1.0a
const client = new TwitterApi({
  appKey: config.twitter.oauth.consumerKey,
  appSecret: config.twitter.oauth.consumerSecret,
  accessToken: config.twitter.oauth.accessToken,
  accessSecret: config.twitter.oauth.accessTokenSecret
});
const trending = await client.v2.search('crypto OR web3 OR base', { max_results: 10 });
```

**Farcaster (Neynar API):**
```javascript
const response = await fetch('https://api.neynar.com/v2/farcaster/feed/trending?limit=5', {
  headers: { 'x-api-key': config.farcaster.neynarApiKey }
});
```

**Moltbook:**
```javascript
const response = await fetch('https://www.moltbook.com/api/v1/posts/trending', {
  headers: { 'Authorization': `Bearer ${config.moltbook.apiKey}` }
});
```

### Step 3: Filter Already Replied
- Load `engagement-state.json`
- Filter out posts with IDs in `repliedPosts[platform]`
- Select random unreplied post from remaining

### Step 4: Generate Contextual Reply
Based on persona config, analyze post content and generate reply:

**Reply Generation Rules:**
1. **Read the post carefully** - understand topic, tone, intent
2. **Match persona** - use configured tone, values, signature emoji
3. **Add specific value** - technical insight, question, or genuine reaction
4. **Avoid generic praise** - no "Great post!", "Love this!"
5. **Keep it natural** - crypto slang if persona dictates, short sentences

**Tone Balance (configurable):**
- Educational: technical insights, explanations, resources
- Community Vibes: celebration, encouragement, connection
- Humor: wit, self-aware jokes, memes (when appropriate)

### Step 5: Post Reply

**Twitter:**
```javascript
await client.v2.reply(replyText, originalTweetId);
```

**Farcaster (via farcaster-agent pattern):**
```javascript
// Uses post-cast.js with PARENT_FID + PARENT_HASH
const result = await postCast({
  privateKey: config.farcaster.custodyPrivateKey,
  signerPrivateKey: config.farcaster.signerPrivateKey,
  fid: config.farcaster.fid,
  text: replyText,
  parentFid: originalCast.author.fid,
  parentHash: originalCast.hash
});
```

**Moltbook:**
```javascript
await fetch('https://www.moltbook.com/api/v1/comments', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${config.moltbook.apiKey}` },
  body: JSON.stringify({ postId, content: replyText })
});
```

### Step 6: Update State
```json
{
  "lastUpdated": "2026-02-12T11:00:00Z",
  "repliedPosts": {
    "twitter": ["1234567890", "0987654321"],
    "farcaster": ["0xabc123...", "0xdef456..."],
    "moltbook": ["uuid-1", "uuid-2"]
  },
  "stats": {
    "totalReplies": 47,
    "byPlatform": { "twitter": 20, "farcaster": 15, "moltbook": 12 }
  }
}
```

## Persona Configuration Guide

See [references/persona-config.md](references/persona-config.md) for detailed persona setup.

**Quick Examples:**

```json
// Crypto-native builder
{
  "tone": "crypto-native, technical, supportive",
  "signatureEmoji": "🦞",
  "values": ["shipping", "community", "open-source"],
  "phrases": ["ships > talks", "ser", "wagmi", "based"]
}

// Professional analyst
{
  "tone": "professional, analytical, educational",
  "signatureEmoji": "📊",
  "values": ["accuracy", "depth", "clarity"],
  "phrases": ["data suggests", "worth noting", "key insight"]
}
```

## Platform-Specific Notes

See [references/platform-apis.md](references/platform-apis.md) for API details.

**Twitter:** OAuth 1.0a required. Rate limits: 50 tweets/15min, 300 tweets/3hr.

**Farcaster:** Neynar API + x402 payments (0.001 USDC/call). Requires FID + signer key.

**Moltbook:** API key auth. Verification captcha for posts/comments.

## Reply Quality Guidelines

See [references/reply-strategies.md](references/reply-strategies.md) for detailed strategies.

**Golden Rules:**
1. **Specific > Generic** - If you can't add specific value, stay silent
2. **Quality > Quantity** - One thoughtful reply beats five generic ones
3. **Authentic > Performative** - Sound human, not bot
4. **Value > Visibility** - Help the community, don't just farm engagement

**What Works:**
✅ Technical questions showing understanding
✅ Specific insights from experience
✅ Genuine celebration with substance
✅ Helpful resources and connections

**What Fails:**
❌ Generic praise ("Love this!", "Great post!")
❌ Corporate speak ("excited to announce")
❌ Surface-level comments
❌ Forced humor

## Cron Integration

To run automatically, create a cron job:

```json
{
  "name": "Multi-Channel Engagement - Every 6h",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run multi-channel-engagement-agent: engage on all platforms",
    "model": "haiku"
  }
}
```

## Advanced Features

### Content Filters
Skip spam, scams, and low-quality content automatically.

```json
"filters": {
  "skipKeywords": ["airdrop", "free money", "send dm", "check bio"],
  "minEngagement": { "likes": 5, "replies": 2 },
  "skipBots": true,
  "languageFilter": ["en", "es"]
}
```

### Mention Tracking
Reply to mentions of your account, not just trending.

```bash
node scripts/engage.mjs --mentions --platform=twitter
```

### Webhook Notifications
Send engagement results to Telegram or Discord.

```json
"webhooks": {
  "telegram": {
    "enabled": true,
    "botToken": "YOUR_BOT_TOKEN",
    "chatId": "YOUR_CHAT_ID"
  },
  "discord": {
    "enabled": false,
    "webhookUrl": "https://discord.com/api/webhooks/..."
  }
}
```

### User Blacklist/Whitelist
Skip bots, prioritize builders.

```json
"users": {
  "blacklist": ["spambot123", "scammer456"],
  "whitelist": ["jessepollak", "vitalik"],
  "prioritizeVerified": true
}
```

### Analytics Tracking
Track engagement stats over time in `analytics.json`.

```json
{
  "daily": {
    "2026-02-12": {
      "replies": 4,
      "platforms": { "twitter": 2, "farcaster": 2 },
      "engagement": { "likes": 15, "replies": 3 }
    }
  },
  "allTime": {
    "totalReplies": 247,
    "avgEngagement": 4.2
  }
}
```

### Quote Support
Quote tweets/recasts instead of direct replies.

```bash
node scripts/engage.mjs --quote --platform=twitter
node scripts/engage.mjs --quote --platform=farcaster
```

## Troubleshooting

**"Already replied to all trending"** - All top posts already engaged. Wait for new trending content.

**Twitter rate limit** - Wait 15 minutes. Consider reducing frequency.

**Farcaster "unknown fid"** - Hub not synced. Wait 30-60 seconds.

**Moltbook verification failed** - Solve the math captcha in verification response.

## Files

- `scripts/engage.mjs` - Main engagement script
- `scripts/fetch-trending.mjs` - Fetch trending by platform
- `scripts/generate-reply.mjs` - Persona-driven reply generation
- `scripts/post-reply.mjs` - Post reply to platform
- `references/persona-config.md` - Persona configuration guide
- `references/platform-apis.md` - Platform API documentation
- `references/reply-strategies.md` - Reply quality strategies
