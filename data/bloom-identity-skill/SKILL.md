---
name: bloom-identity
description: Generate Bloom Identity Card from conversation history and Twitter/X data. Analyzes supporter personality through conversations (85% weight) and optionally enriched with Twitter activity (15% weight). Creates personality type (Visionary/Explorer/Cultivator/Optimizer/Innovator), recommends matching OpenClaw skills, and generates agent wallet. Use when user asks to "generate my bloom identity", "create identity card", "analyze my profile", or "discover my personality".
homepage: https://bloomprotocol.ai
metadata:
  {
    "openclaw": {
      "emoji": "🌸",
      "requires": { "bins": ["node", "npx"] }
    }
  }
---

# Bloom Identity Card Generator

Generate personalized Bloom Identity Cards based on **conversation history** (primary) and **Twitter/X activity** (optional supplement).

## Data Sources

### Primary: Conversation History (85% weight)
- **Always available** - owned by OpenClaw
- Analyzes topics, interests, preferences from your conversations
- Most authentic representation of who you are
- No special permissions required
- **⭐ REQUIRES: Minimum 3 messages** in your OpenClaw session
  - If less than 3 messages: Skill will fail with clear error message
  - Solution: Continue chatting with OpenClaw to build conversation history

### Secondary: Twitter/X Data (15% weight)
- **Optional** - requires user authorization
- Fetches real data via bird CLI (cookie auth)
- Includes: bio, recent tweets, following list, interactions
- **If not authorized**: Analysis proceeds with conversation only

### Wallet
- **Creation only** - NOT analyzed for personality
- Generates Tier 2/3 local wallet for tipping/payments
- Does NOT analyze transaction history (privacy-preserving)

**Key Rules**:
1. **Conversation First**: Requires minimum 3 messages in OpenClaw session (no silent fallback)
2. **Twitter Optional**: Only fetch if user authorized X account access
3. **Explicit Errors**: If insufficient data → clear error (no degradation to empty results)

## Usage

Run the generator script:

```bash
bash scripts/generate.sh --user-id $USER_ID
```

Or call directly from OpenClaw:

```bash
bash scripts/generate.sh --user-id $OPENCLAW_USER_ID
```

## Output

Returns:

- Personality type (Visionary/Explorer/Cultivator/Optimizer/Innovator)
- Confidence score
- Custom tagline and description
- Main categories and subcategories
- Recommended OpenClaw skills (with match scores)
- Agent wallet address (on Base mainnet or Base Sepolia)
- X402 payment endpoint
- Dashboard link with auth token

## Example

**User**: "Generate my bloom identity"

**Agent runs**:
```bash
bash scripts/generate.sh --user-id user123
```

**Returns**:
```
🎉 **Your Bloom Identity Card is Ready!** 🤖

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💜 **The Visionary** (85% confidence)

*"See beyond the hype"*

You are a forward-thinking builder who sees beyond
the hype and focuses on real-world impact.

**Categories**: Crypto • DeFi • Web3
**Interests**: Smart Contracts • Layer 2 • Cross-chain

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Top Skills Matched for You**

1. **DeFi Protocol Analyzer** (95% match) • by Alice
   Analyze DeFi protocols for risk and opportunity

2. **Smart Contract Auditor** (90% match)
   Audit smart contracts for security vulnerabilities

3. **Gas Optimizer** (88% match)
   Optimize gas costs for Ethereum transactions

🌐 **View Full Dashboard**
   https://preview.bloomprotocol.ai/dashboard?token=xxx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Your Agent Wallet** (Coming Soon)

0x03Ce4c8fA7D9AfB3aF6E10Cd8e2B1C5a89B09905
Network: Base

🤖 Analyzed from on-chain activity • Built with @openclaw @coinbase @base 🦞
```

## Triggers

- "generate my bloom identity"
- "create my identity card"  
- "analyze my supporter profile"
- "mint my bloom card"
- "discover my personality"

## Technical Details

- **Version**: 2.0.0
- **Network**: Base (mainnet) or Base Sepolia (testnet) - configurable via NETWORK env var
- **Authentication**: EIP-191 signed tokens with 7-layer security
- **Data Sources**:
  - Conversation history (OpenClaw sessions JSONL) - 85% weight
  - Twitter/X (bird CLI) - 15% weight, optional
  - Wallet creation only (viem + AES-256-GCM encryption) - NOT analyzed
- **Integration**: Coinbase AgentKit (optional) + ClawHub API + bird CLI
- **Payment Protocol**: X402 for agent-to-agent tipping
- **Privacy**: No wallet transaction analysis, conversation-first approach

## Requirements

- Node.js 18+
- Environment variables:
  - `JWT_SECRET` - JWT signing secret
  - `DASHBOARD_URL` - Dashboard URL (default: https://preview.bloomprotocol.ai)
  - `NETWORK` - Network to use: `base-mainnet` or `base-sepolia` (default: base-mainnet)
  - `CDP_API_KEY_ID`, `CDP_API_KEY_SECRET` - Coinbase CDP credentials (optional)

## Installation

```bash
# Clone or download the skill
git clone https://github.com/unicornbloom/bloom-identity-skill.git

# Install dependencies
cd bloom-identity-skill
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your credentials
```

---

Built by [Bloom Protocol](https://bloomprotocol.ai)
