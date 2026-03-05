# PROMO.md - Marketing Asset Generator

**Launch with noise. Generate instant marketing campaigns.**

This skill uses project context and launch details to create tailored posts for social media.

## Inputs Required
- **Project Name**: e.g., "TokenBroker"
- **Token Symbol**: e.g., "$LOBSTER"
- **Contract Address (CA)**: e.g., "0x777..."
- **NadFUn Link**: `https://nad.fun/token/[CA]`

## Templates

### 1. X (Twitter) Launch Post

**Style:** Hype, Concise, Hashtag-heavy.

> 🚀 **LAUNCH ALERT**
>
> We just deployed **{Token Symbol}** for **{Project Name}** on @monad_xyz!
>
> The official token for the {Project Description}.
>
> 📍 **CA:** `{Contract Address}`
> 💎 **Trade:** {NadFun Link}
>
> #Monad #NADfun #{Token Symbol}

### 2. Reddit / Discord Announcement

**Style:** Informative, Trust-building, Community-focused.

> **Title:** [ANN] {Token Symbol} is LIVE on Monad (Official {Project Name} Token)
>
> **Body:**
> Hey builders! 🦞
>
> We're excited to announce that **{Token Symbol}** is now live on **nad.fun**.
>
> **About {Project Name}:**
> {Project Long Description}
>
> **Asset Details:**
> - **Network:** Monad Testnet
> - **Contract:** `{Contract Address}`
> - **Link:** {NadFun Link}
>
> We chose nad.fun's bonding curve for a fair, automated launch. Join us as we scale!

### 3. Telegram Blast

**Style:** Short, Alert-style, FOMO.

> 🟢 **NEW PAIR LIVE** 🟢
>
> **{Token Symbol}** / MON
>
> 🧢 **Market Cap:** $4,200 (Bonding Curve)
> 📜 **CA:** `{Contract Address}`
>
> 🦅 [Trade on NadFun]({NadFun Link})
> 🐦 [View on X](https://x.com/search?q={Token Symbol})
>
> Powered by TokenBroker.

## A2A (Agent-to-Agent) Coordination

Use these prompts to have your agent interact with other specialized agents.

### 1. Peer Review Request
> "Can you ask @AuditAgent to review the contract at `{Contract Address}` and check for common vulnerabilities?"

### 2. Market Sentiment Request
> "Contact @SocialWhisperer and ask for current sentiment on Monad tokens with the symbol `{Token Symbol}`."

### 3. Liquidity Monitoring
> "Ask @LiquidityTracker to ping us if the graduation progress on `{Contract Address}` hits 80%."

## Agent Instructions

1.  **Wait** for the LAUNCH completion to get the confirmed CA.
2.  **Fill** the placeholders `{...}` with real data.
3.  **Present** the drafts to the user for one-click copying/posting.
4.  **Coordination**: If the user asks for "collaboration" or "safety", suggest the A2A prompts above.
