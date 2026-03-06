---
name: x-alpha-scout
description: "X/Twitter alpha scanner for crypto and NFTs. Use when: (1) user
  wants daily alpha reports, (2) analyzing a specific token/NFT/project from X
  sentiment. GitHub: github.com/hammad-btc/alpha-scout-skill"
---


# X Alpha Scout

Your agent's X/Twitter alpha scanner. Two things: daily reports and on-demand analysis.

## Prerequisites

**Environment variables:**
```bash
export X_AUTH_TOKEN="your_twitter_auth_token"
export X_CT0="your_twitter_ct0_cookie"
```

**Verify:**
```bash
bird whoami --auth-token "$X_AUTH_TOKEN" --ct0 "$X_CT0"
```

---

## Feature 1: Daily Alpha Report (Auto at 00:00 UTC)

**User says:** "Run my daily alpha" or "Get today's report"

**What you do:**

```bash
# Scan for overnight alpha
bird search "(buying OR bought OR aping OR loading up) (ticker OR token OR \$)" -n 25
bird search "(minting OR mint OR free mint) NFT" -n 20
bird search "(just launched OR stealth launch) token" -n 15
bird search "(gem OR undervalued OR 100x) crypto" --min-likes 10 -n 15
```

**Generate report in this exact format:**

```markdown
# 🦅 Alpha Report — Feb 10, 2026

### 1. Good Morning
[Simple greeting]

### 2. Crypto Market Update
- BTC: $[price] ([+/-]% 24h)
- ETH: $[price] ([+/-]% 24h)
- SOL: $[price] ([+/-]% 24h)
- Fear & Greed Index: [value] ([Extreme Fear/Fear/Neutral/Greed/Extreme Greed])

### 3. News of the Day
- [Major Web3 announcement](https://x.com/...) — Brief summary
- [Regulation/news affecting market](https://x.com/...) — Brief summary
- [Any market-moving world news](https://x.com/...) — Brief summary

### 4. Crypto Twitter (CT)
- Main narrative: [What's the hot topic today?]
- Key trends: [New meta, drama, or shifts]
- Notable accounts: [Who's driving conversation]

### 5. NFTs Market Update
**ETH Eco:** [2-3 sentence paragraph on top ETH ecosystem updates — NFTs, tokens, protocols. Skip if nothing significant.]

**Bitcoin Eco:** [2-3 sentence paragraph on top Bitcoin/Ordinals market. Skip if nothing significant.]

**Sol Eco:** [2-3 sentence paragraph on top Solana ecosystem — NFTs, DeFi, memes. Skip if nothing significant.]

**Notable Mints:**
- Minting Today: [@account1](https://x.com/account1) [@account2](https://x.com/account2) [@account3](https://x.com/account3) (only good, hyped drops — embed X profile links)
- Upcoming Mints: [@account4](https://x.com/account4) [@account5](https://x.com/account5) (worth keeping an eye on — embed X profile links)

If none worth mentioning, say "No major mints detected."

### 6. Alpha from Reputable Figures:
- Top calls: [What are reputable accounts buying/minting? Include @username]
- High-conviction signals: [Who's aping what with size/proof — include @username]
- WL opportunities: [Any good drops they mentioned — include @username]
- Emerging narratives: [New meta or trend being discussed — include @username]
- Notable exits/warnings: [Who's selling or warning about what — include @username]

### 7. Extra / Warnings
- [Any red flags or opportunities noticed]
- [Personal observations]

---
*Report time: 00:00 UTC | NFA/DYOR*
```

**Deliver:** Send to user via their preferred channel (Discord, Telegram, etc.)

---

## Feature 2: On-Demand Analysis

**User says:** "What do you think of $PEPEAI?" or "Analyze FomoBears NFT"

**What you do:**

```bash
# Deep scan this specific asset
bird search "$PEPEAI" -n 30
bird search "$PEPEAI (gem OR scam OR rug OR buy)" -n 20
```

**Analyze gathered tweets:**

1. **Count sentiment:** Bullish vs Bearish vs Neutral
2. **Identify high-conviction posts:** Position sizes, wallet proofs, detailed threads
3. **Check high-rep accounts:** Are known good callers in or out?
4. **Look for red flags:** Contract issues, copycat names, anon team

**Deliver analysis in this exact format:**

```
📊 CT Sentiments:
[4-5 line summary based on top 20-30 recent tweets about the asset. What are people saying? Any patterns? Hype or concern? Specific details about the project/token/NFT]
📈 Overall: [Bullish/Bearish/Neutral] (assessment at end of CT Sentiments section)

🐋 Takes of High-Rep Accounts:
[@Influencer1: "quote or summary of their take" — Bullish]
[@Influencer2: "quote or summary of their take" — Bearish]
[Or: No noticeable activity detected from high-rep accounts — Bearish]

⚠️ Red Flags:
[Any contract issues, anon team, copycat name, LP not locked, etc. Or: None detected]

📊 Score: XX/100

✅ Verdict: [High/Medium/Low confidence — Bullish/Neutral/Bearish]

⚡ NFA / DYOR
```

**How to gather data:**

```bash
# Get general sentiment tweets
bird search "$TICKER" -n 30

# Get high-rep account takes specifically
bird search "$TICKER (from:DegenKing OR from:AlphaKing OR from:CryptoGem)" -n 20
# Add more KOLs as needed
```

**Scoring guide:**
- **90-100:** Strong bullish consensus, high-reps bullish, no red flags
- **70-89:** Moderate bullish, some high-reps in, minor concerns
- **50-69:** Mixed/neutral, no clear direction or high-reps silent
- **30-49:** Bearish signals, some red flags or high-reps warning
- **0-29:** Strong bearish, multiple red flags, avoid

---

## Signal Scoring Guide

**CT Sentiment Score (0-100):**
- **80-100:** Strong bullish consensus, high-rep accounts in, no red flags
- **50-79:** Mixed or moderate sentiment, do more research
- **<50:** Bearish consensus or multiple red flags detected

**What to look for:**
- **Bullish:** "gem", "undervalued", "loading up", "next 100x"
- **Bearish:** "rug", "scam", "avoid", "dumping"
- **High-conviction:** Specific numbers ("bought $5k"), wallet screenshots, detailed threads
- **Red flags:** Contract unverified, LP not locked, copycat name, team completely anon

---

## Quick Commands

| Task | Command |
|------|---------|
| Daily report | Run scans for last 24h, compile top calls |
| Analyze asset | `bird search "$TICKER" -n 30` |
| Check specific caller | `bird search "from:username" -n 20` |
| Find mints | `bird search "free mint OR minting now NFT" -n 15` |

---

## Example Sessions

**User:** "Get my alpha report"

**You:** Run the 4 daily scans → compile top calls → format report → deliver

---

**User:** "What about $MOONSHOT?"

**You:** Search "$MOONSHOT" (30 tweets) → analyze sentiment → check for red flags → deliver analysis with score + verdict + NFA

---

**User:** "Is @DegenKing reliable?"

**You:** Search "from:DegenKing" → review their recent calls → give qualitative assessment: "Known for high-conviction calls, recent streak looks solid" or "Mixed bag lately, verify before following"

---

*Built for the agent economy. NFA. DYOR.* 🦅
