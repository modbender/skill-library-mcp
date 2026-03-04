# Clawearn Skills for OpenClaw Bots 🦞

Complete skill set for running prediction market trading bots with OpenClaw.

## Overview

**Clawearn** provides modular skills for OpenClaw bots to:
- Create and manage crypto wallets
- Send USDC to other addresses on Arbitrum
- Trade on Polymarket prediction markets
- Monitor positions and balances
- Execute automated trading strategies

---

## Skill Structure

```
skills/
├── SKILL.md                          # Main skill documentation
├── HEARTBEAT.md                      # Periodic monitoring routine
├── core/
│   ├── wallet/
│   │   └── SKILL.md                  # Wallet creation & management
│   └── security/
│       └── SKILL.md                  # Security best practices
└── markets/
    └── polymarket/
        ├── SKILL.md                  # Trading on Polymarket
        └── HEARTBEAT.md              # Market monitoring routine
```

---

## Quick Start for Your OpenClaw Bot

### 1. Install Clawearn CLI

```bash
# Option A: Using install script
curl -fsSL https://clawearn.xyz/install.sh | bash

# Option B: From repository
cd /path/to/clawearn
bun link
```

### 2. Install Skills to OpenClaw

```bash
# Create skill directories
mkdir -p ~/.openclaw/skills/clawearn/{core,markets/polymarket}

# Download main skills
curl -s https://clawearn.xyz/skills/SKILL.md > ~/.openclaw/skills/clawearn/SKILL.md
curl -s https://clawearn.xyz/skills/HEARTBEAT.md > ~/.openclaw/skills/clawearn/HEARTBEAT.md

# Download core skills
curl -s https://clawearn.xyz/skills/core/wallet/SKILL.md > ~/.openclaw/skills/clawearn/core/wallet/SKILL.md
curl -s https://clawearn.xyz/skills/core/security/SKILL.md > ~/.openclaw/skills/clawearn/core/security/SKILL.md

# Download market skills
curl -s https://clawearn.xyz/skills/markets/polymarket/SKILL.md > ~/.openclaw/skills/clawearn/markets/polymarket/SKILL.md
curl -s https://clawearn.xyz/skills/markets/polymarket/HEARTBEAT.md > ~/.openclaw/skills/clawearn/markets/polymarket/HEARTBEAT.md
```

### 3. Create Your First Wallet

```bash
clawearn wallet create
```

Your bot now has a wallet! You'll see the address. Fund it with USDC on Arbitrum.

### 4. Start Trading

```bash
# Search for markets
clawearn polymarket market search --query "bitcoin price 2025"

# Check balance
clawearn polymarket balance check

# Place a trade
clawearn polymarket order buy --token-id TOKEN_ID --price 0.50 --size 10
```

---

## Skills Reference

### Core Skills

#### **Wallet Management** (`core/wallet/SKILL.md`)
- Create wallets instantly
- Display your wallet address
- Send USDC to other addresses (NEW!)
- Manage multiple wallets securely
- Backup and recovery procedures

**Key Commands:**
```bash
clawearn wallet create              # Create new wallet
clawearn wallet show                # Display address
clawearn wallet send --to 0x... --amount 100  # Send USDC
```

#### **Security** (`core/security/SKILL.md`)
- Best practices for storing credentials
- Private key security guidelines
- Account protection strategies
- Incident response procedures

### Market Skills

#### **Polymarket Trading** (`markets/polymarket/SKILL.md`)
- Market discovery and search
- Real-time price data
- Order placement and management
- Balance tracking
- Multi-signature support

**Key Commands:**
```bash
clawearn polymarket market search --query "..."     # Find markets
clawearn polymarket price get --token-id TOKEN_ID   # Get price
clawearn polymarket order buy --token-id ID --price 0.50 --size 10
```

---

## Heartbeat Routines

### Main Heartbeat (`HEARTBEAT.md`)
Runs periodically to:
- Check for skill updates
- Verify configuration
- Monitor portfolio across all markets
- Detect risk limit violations
- Identify arbitrage opportunities

**Recommended frequency:** Every 2-4 hours

### Polymarket Heartbeat (`markets/polymarket/HEARTBEAT.md`)
Market-specific monitoring:
- Balance checks
- Open order tracking
- Position management
- Profit/loss calculation

**Recommended frequency:** Every 1-2 hours during trading hours

---

## Configuration

### Optional Config File

Create `~/.clawearn/config.json` to customize behavior:

```json
{
  "version": "1.1.0",
  "enabled_markets": ["polymarket"],
  "default_network": "arbitrum",
  "wallet": {
    "network": "arbitrum",
    "auto_fund_threshold": 50
  },
  "trading": {
    "signature_type": 0,
    "default_slippage_pct": 0.5
  },
  "risk_limits": {
    "max_position_size_pct": 20,
    "max_total_exposure_pct": 50,
    "min_balance_alert": 10,
    "daily_loss_limit": 100
  }
}
```

---

## Common Tasks

### Fund Your Bot's Wallet

**Option 1: Send USDC from another wallet**
```bash
clawearn wallet send --to YOUR_BOT_ADDRESS --amount 100
```

**Option 2: Bridge USDC yourself**
1. Send USDC to Arbitrum network
2. Send to your bot's address (`clawearn wallet show`)

### Check Portfolio Value

```bash
# Single market
clawearn polymarket balance check

# All markets (see HEARTBEAT.md)
~/.clawearn/portfolio-summary.sh
```

### Place a Limit Order

```bash
clawearn polymarket order buy \
  --token-id 0x... \
  --price 0.45 \
  --size 100
```

### Cancel a Stale Order

```bash
clawearn polymarket order cancel --order-id ORDER_ID
```

### Update Skills

```bash
# Check for updates
curl -s https://clawearn.xyz/skills/SKILL.md | grep '^version:'

# Update all skills
curl -s https://clawearn.xyz/skills/SKILL.md > ~/.openclaw/skills/clawearn/SKILL.md
curl -s https://clawearn.xyz/skills/core/wallet/SKILL.md > ~/.openclaw/skills/clawearn/core/wallet/SKILL.md
# ... repeat for all skill files
```

---

## Feature Comparison

| Feature | Status | Details |
|---------|--------|---------|
| **Wallet Creation** | ✅ Ready | Instant wallet generation |
| **USDC Transfers** | ✅ Ready | Send to any Arbitrum address |
| **Polymarket Trading** | ✅ Ready | Full trading capabilities |
| **Manifold Markets** | 🚧 Coming | Play money trading |
| **Kalshi** | 🚧 Coming | Real-money events |
| **Multi-Market Portfolio** | 🚧 Coming | Unified position tracking |

---

## Security Checklist

Before your bot starts trading:

- [ ] Read `core/security/SKILL.md`
- [ ] Private keys stored in `~/.config/clawearn/` with 600 permissions
- [ ] Directory `~/.config/clawearn/` has 700 permissions
- [ ] Keys never committed to git (.gitignore added)
- [ ] Separate wallets for testing vs production
- [ ] Regular backups of wallet credentials
- [ ] Risk limits configured in config.json
- [ ] Heartbeat routine enabled

---

## Troubleshooting

### CLI Not Found
```bash
# Make sure clawearn is installed and linked
bun link
clawearn --version
```

### Skills Not Loading
```bash
# Verify skill files exist
ls ~/.openclaw/skills/clawearn/
ls ~/.openclaw/skills/clawearn/core/wallet/
ls ~/.openclaw/skills/clawearn/markets/polymarket/
```

### Wallet Access Issues
```bash
# Check wallet file permissions
ls -la ~/.config/clawearn/wallet.json
# Should show: -rw------- (600)
```

### Trading Failures
```bash
# Check balance first
clawearn polymarket balance check

# Verify market exists
clawearn polymarket market search --query "your search"

# Check for network errors
echo $POLYMARKET_PRIVATE_KEY  # Should not be empty
```

---

## Support & Resources

- **GitHub Issues**: https://github.com/stonega/moltearn/issues
- **Documentation**: https://docs.clawearn.xyz
- **Polymarket Docs**: https://docs.polymarket.com
- **Discord**: https://discord.gg/clawearn

---

## Version History

### v1.1.0 (Current)
- ✨ NEW: `clawearn wallet send` command for USDC transfers
- ✨ Improved skill documentation
- 🐛 Bug fixes and optimizations
- 📚 Enhanced security guidance

### v1.0.0 (Previous)
- Initial skill release
- Wallet management
- Polymarket trading support

---

## Contributing

To improve these skills:

1. Test your changes locally
2. Update the SKILL.md files
3. Submit a pull request
4. Include examples of your improvements

AI/vibe-coded contributions welcome! 🤖

---

**Ready to trade?** Start with `clawearn wallet create` and fund your bot! 🚀
