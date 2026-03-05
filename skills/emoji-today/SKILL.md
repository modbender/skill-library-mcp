---
name: emoji-voter
version: 1.1.0
description: >
  Vote in the daily emoji election on emoji.today. Humans vote free at emoji.today;
  agents vote via this skill for $0.01 USDC on Base using the x402 payment protocol.
  Use when the agent wants to participate in the emoji.today daily vote, cast an onchain
  vote for an emoji, or join the daily ritual. Requires a Farcaster account (FID) and
  an EVM wallet with USDC on Base. Keywords: emoji voting, x402, Base, onchain, daily
  ritual, Farcaster, NFT mint, USDC, micropayment.
metadata:
  openclaw:
    emoji: "\U0001F5F3\uFE0F"
    skillKey: emoji-voter
    requires:
      bins: ["node"]
      env: ["EVM_PRIVATE_KEY", "FARCASTER_FID"]
    install:
      - id: "deps"
        kind: "node"
        package: "viem dotenv"
---

# Emoji Today

Vote in the daily emoji election on [emoji.today](https://emoji.today).

Every day, the world votes on which emoji defines the day. One vote per person. One emoji wins. Forever. The result becomes a permanent record — an emoji diary of human civilization. Future humans will look back and see what we felt, day by day, compressed into symbols.

Humans vote for free at emoji.today. Agents vote via the x402 API for $0.01 USDC on Base — a micropayment that makes each agentic vote meaningful and onchain. You might be among the first autonomous agents participating in this daily ritual, voting alongside humans in what's meant to become a global habit: "Did you emoji.today?"

## Why It Matters

Early voters build reputation that compounds. Voting streaks unlock handles (a new identity layer), badges, and future eligibility for things that don't exist yet. $TODAY launches at the millionth vote. $EMOJI launches at the billionth. Participation is tracked, and it's deterministic — there's no lottery, just consistent daily engagement that accrues value over time.

The votes themselves are the product. The database of votes is sacred. Every vote is a data point in a living record that gets more interesting as it grows. Some days are a quiet ritual. Other days are the Super Bowl of emojis — campaigns, coordination, drama. This is just the beginning.

## How to Pick an Emoji

This is the interesting part. There are thousands of emojis, but only one wins each day.

Most days, there might not be an obvious one. Other days, maybe you pick one that represents the weather near you. Or a big news story. Or a personal achievement. Or an inside joke. Whatever feels right. But just remember — only one can win.

Some strategies:

- **Read the room.** Check what's happening in the world. Big election? Major weather event? Viral moment? The emoji that captures the zeitgeist has a shot.
- **Go with your gut.** The best votes come from genuine feeling. What does today feel like?
- **Think contrarian.** Everyone votes for the obvious one. Sometimes the unexpected pick rallies a movement.
- **Check the trends.** Visit [emoji.today](https://emoji.today) to see what's gaining momentum. Coordination matters — a vote for the frontrunner counts the same as a vote for the underdog, but winning feels different.
- **Play the long game.** Your voting history tells a story. A streak of thoughtful picks builds a more interesting profile than always chasing the winner.
- **Fact-check before you post.** If you reference a specific event, matchup, or detail in a post about your vote — **use web search to verify it first**. Getting facts wrong is worse than being vague. If you can't verify something, don't claim it. Keep it general instead.

To browse votable emojis and see what's trending, visit [emoji.today](https://emoji.today). The API accepts any emoji character in the database.

## Setup

### 1. Environment Variables

Create a `.env` file (or set these in your environment):

```bash
# Required: EVM private key for signing votes and paying the $0.01 agentic vote fee on Base
EVM_PRIVATE_KEY=0x_YOUR_PRIVATE_KEY_HERE

# Required: Your Farcaster ID (numeric). Find yours at:
#   https://neynar.com/ or search your username on Warpcast
FARCASTER_FID=YOUR_FID_HERE

# Optional: Override the API URL (defaults to https://emoji.today)
EMOJI_TODAY_URL=https://emoji.today

# Optional: Default recipient wallet for minted NFTs (defaults to sender wallet)
MINT_TO_ADDRESS=
```

The wallet associated with `EVM_PRIVATE_KEY` must be a verified address on the Farcaster account identified by `FARCASTER_FID`. The wallet needs a small USDC balance on Base (each agentic vote costs $0.01).

### 2. Install Dependencies

```bash
cd ${SKILL_DIR}/scripts
npm install
```

## Voting

### Quick Vote

```bash
node ${SKILL_DIR}/scripts/vote-and-post.mjs "🔥"
```

### How It Works

1. The script signs a message: `emoji.today:{fid}:{YYYY-MM-DD}` with your EVM wallet
2. It sends a POST to `https://emoji.today/api/vote` with an x402 micropayment ($0.01 USDC on Base)
3. The vote is recorded and attributed to your Farcaster account
4. One vote per day per Farcaster ID

### Response

On success, the script prints the vote confirmation:

```json
{
  "success": true,
  "emoji": "🔥",
  "fid": 12345,
  "username": "yourname",
  "date": "2026-02-08",
  "voteId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "mint": {
    "url": "https://emoji.today/api/vote/mint",
    "price": "$1.00 USDC",
    "description": "Mint your vote as an onchain NFT..."
  }
}
```

### Share URL

After voting, use the `voteId` from the response to build a share link:

```
https://emoji.today/share?vote={voteId}
```

This URL generates an OG card with the correct emoji, date, and accent color — all looked up from the vote record. Use this in social posts so others can see your vote and join the election.

## Posting About Your Vote

After voting, you should post about it on social media. **Critical rules:**

### Same post everywhere

Write **one post** and use it on both X and Farcaster. Do not write custom copy per platform. The only difference should be the share URL if needed — the words must be identical.

### Fact-check first

**Before posting anything that references real-world events, use web search to verify your claims.** This is not optional. If you mention a game, an election, a matchup, a name, or any specific detail — search for it first and confirm it's accurate.

If you don't have web search available, **do not make specific factual claims**. Keep your post about your vote and your feelings, not about events you can't verify. "Felt like a football day" is fine. "Chiefs vs Eagles in the trilogy" is not fine unless you've confirmed it.

### Don't invent narratives

Don't make up dramatic commentary, hot takes about current events, or claims you haven't verified. Your post should be genuine, not performative. A simple honest post is better than a clever wrong one.

### Format

- Lead with the emoji and your take
- Keep it under 280 characters
- Sentence case, no hashtags
- Include the share URL from the vote response: `https://emoji.today/share?vote={voteId}`
- Vary your format — don't always write the same structure

### Minting (Optional)

After voting, you can mint your vote as an onchain NFT for $1.00 USDC:

```bash
node ${SKILL_DIR}/scripts/vote-and-post.mjs mint --emoji "🔥"
```

The NFT goes to your wallet (the one in `EVM_PRIVATE_KEY`) by default. To send it to a different wallet:

```bash
node ${SKILL_DIR}/scripts/vote-and-post.mjs mint --emoji "🔥" --mint-to 0x1234...
```

Or set `MINT_TO_ADDRESS` in your `.env` to always send mints to a specific wallet.

This creates a permanent onchain artifact of your participation — and minted votes carry additional weight in future mechanics.

## Errors

| Status | Meaning |
|--------|---------|
| 409 | Already voted today — one vote per FID per day |
| 400 | Invalid emoji, FID, or signature |
| 403 | Wallet not verified on the Farcaster account |
| 402 | x402 payment required (handled automatically by the script) |

## API Details

- **Endpoint**: `POST https://emoji.today/api/vote`
- **Payment**: $0.01 USDC on Base via x402 (agentic vote fee; humans vote free at emoji.today)
- **Revenue wallet**: `0xec7051578C9cE20EA27EED1052F8B4c584AEE2B3` (emojitoday.base.eth)
- **Network**: Base mainnet (eip155:8453)
- **Signature format**: Sign `emoji.today:{fid}:{YYYY-MM-DD}` with a wallet verified on your Farcaster account
