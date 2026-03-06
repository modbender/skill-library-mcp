# Obverse Payments - OpenClaw Skill

Accept stablecoin payments (USDC/USDT) via Telegram, WhatsApp, Discord using the Obverse payment infrastructure.

## Features

- ✅ Generate payment links and QR codes
- ✅ Accept USDC/USDT on Solana and Monad
- ✅ Track payment status in real-time
- ✅ Create invoices automatically
- ✅ Check wallet balances
- ✅ Multi-platform: Telegram, WhatsApp, Discord, Signal
- ✅ Low transaction fees (0.5-1.5%)
- ✅ 24/7 automated payment processing

## Quick Start

### 1. Install the Skill

**Method A: Manual Installation**

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.openclaw/skills

# Clone or copy this skill
cp -r ./openclaw-skill ~/.openclaw/skills/obverse

# OR clone from GitHub (once published)
# git clone https://github.com/obverse/openclaw-skill ~/.openclaw/skills/obverse
```

**Method B: OpenClaw CLI** (when available on ClawHub)

```bash
openclaw skills install obverse-payments
```

### 2. Get Your API Key

1. Visit [https://obverse.cc/signup](https://obverse.cc/signup)
2. Connect your wallet (MetaMask, Phantom, etc.)
3. Choose a plan:
   - **Free**: 100 transactions/month
   - **Starter** ($29/mo): 500 transactions/month
   - **Pro** ($99/mo): 2,000 transactions/month
4. Go to Settings → API Keys
5. Generate a new API key (starts with `obv_sk_...`)

### 3. Configure OpenClaw

Edit your `~/.openclaw/openclaw.json` file:

```json
{
  "skills": {
    "entries": {
      "obverse-payments": {
        "enabled": true,
        "env": {
          "OBVERSE_API_KEY": "obv_sk_your_api_key_here"
        }
      }
    }
  }
}
```

### 4. Restart OpenClaw Gateway

```bash
openclaw gateway restart
```

### 5. Verify Installation

Check that the skill is loaded:

```bash
openclaw skills list | grep obverse
```

You should see:
```
✓ obverse-payments (enabled)
```

## Usage Examples

### Via Telegram

```
You: Create a payment link for 50 USDC

Agent: ✅ Payment link created!
       Amount: 50 USDC
       Chain: Solana
       Link: https://pay.obverse.app/xyz123

       Share this with your customer. I'll notify you when paid!
```

### Via WhatsApp

```
You: I need to accept $100 USDT on Solana

Agent: ✅ Payment link ready!
       Amount: 100 USDT
       Chain: Solana
       Link: https://pay.obverse.app/abc789

       QR Code: [image]
       Payment ID: pay_abc789
```

### Via Discord

```
You: Create invoice for John, 5 hours of work at $75/hour

Agent: ✅ Invoice created!
       Recipient: john@example.com
       Total: 375 USDC
       Due: 2026-03-01

       Invoice: https://obverse.cc/invoice/inv_xyz456
       Payment Link: https://pay.obverse.app/xyz456
```

### Check Payment Status

```
You: Check if payment pay_abc123 came through

Agent: 💰 Payment Status: COMPLETED
       Amount: 50 USDC
       Transaction: 0x742d35Cc663...
       Block: 12345678
       Confirmed at: 2026-02-11 14:30 UTC

       Funds will settle in your wallet in 2 minutes!
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| "Create payment for [amount] [currency]" | Generate payment link | "Create payment for 100 USDC" |
| "Generate QR code for [amount]" | Create QR code | "Generate QR code for 50 USDT" |
| "Create invoice for [recipient]" | Generate invoice | "Create invoice for john@email.com" |
| "Check payment [paymentId]" | Check payment status | "Check payment pay_abc123" |
| "What's my balance?" | Check wallet balance | "What's my balance?" |
| "List recent payments" | Show payment history | "List recent payments" |

## Supported Chains & Currencies

| Chain | Currencies | Network | Fees |
|-------|-----------|---------|------|
| Solana | USDC, USDT, SOL | Mainnet | low |
| Monad | USDC, USDT | Mainnet (143) | low |

Default: **Solana** (matches current backend default chain support)

## Pricing

### Transaction Fees
- **Free tier**: 1.5% per transaction
- **Starter** ($29/mo): 1% per transaction
- **Pro** ($99/mo): 0.5% per transaction
- **Enterprise**: Custom rates (0.3%+)

### Plan Limits
- **Free**: 100 txns/month, 10 API calls/min
- **Starter**: 500 txns/month, 60 API calls/min
- **Pro**: 2,000 txns/month, 300 API calls/min
- **Enterprise**: Unlimited

[View full pricing →](https://obverse.cc/pricing)

## Troubleshooting

### "Invalid API key" error

```bash
# Check your API key in openclaw.json
cat ~/.openclaw/openclaw.json | grep OBVERSE_API_KEY

# Make sure it starts with obv_sk_
# Get a new key at: https://obverse.cc/settings/api-keys
```

### "Skill not found"

```bash
# Verify the skill is installed
ls ~/.openclaw/skills/obverse

# Should show: SKILL.md, package.json, README.md

# Restart the gateway
openclaw gateway restart
```

### "curl: command not found"

```bash
# Install curl (required dependency)
# Ubuntu/Debian:
sudo apt-get install curl jq

# macOS:
brew install curl jq
```

### "Rate limit exceeded"

Your plan's API rate limit was hit. Solutions:
1. Wait 60 seconds and retry
2. Upgrade your plan at [obverse.app/pricing](https://obverse.cc/pricing)
3. Implement request batching in your workflow

### Payment link expired

Payment links expire after 24 hours for security:
1. Generate a new payment link
2. Consider using invoices for longer-term payments
3. Enable webhooks for automatic expiry notifications

## Advanced Configuration

### Custom API URL (Self-hosted)

If you're running Obverse on your own infrastructure:

```json
{
  "skills": {
    "entries": {
      "obverse-payments": {
        "enabled": true,
        "env": {
          "OBVERSE_API_KEY": "your_api_key",
          "OBVERSE_API_URL": "https://your-domain.com"
        }
      }
    }
  }
}
```

### Webhook Integration

Configure webhooks to get real-time notifications:

1. Go to [obverse.app/settings/webhooks](https://obverse.cc/settings/webhooks)
2. Add your webhook URL
3. Select events: `payment.completed`, `payment.expired`, `withdrawal.completed`
4. Your agent will receive instant notifications

### Multi-Agent Setup

To use Obverse across multiple agents:

```json
{
  "agents": {
    "sales-agent": {
      "skills": {
        "entries": {
          "obverse-payments": {
            "enabled": true,
            "env": {
              "OBVERSE_API_KEY": "obv_sk_sales_key..."
            }
          }
        }
      }
    },
    "support-agent": {
      "skills": {
        "entries": {
          "obverse-payments": {
            "enabled": true,
            "env": {
              "OBVERSE_API_KEY": "obv_sk_support_key..."
            }
          }
        }
      }
    }
  }
}
```

## API Documentation

Full API documentation is available at:
- **Swagger UI**: [obverse.onrender.com/api-docs](https://obverse.onrender.com/api-docs)
- **REST API Guide**: [obverse.onrender.com/api-docs/api](https://obverse.onrender.com/api-docs/api)
- **SDKs**: JavaScript/TypeScript, Python, Go

## Security Best Practices

1. ✅ Never commit API keys to version control
2. ✅ Use environment variables for secrets
3. ✅ Rotate API keys periodically (every 90 days)
4. ✅ Enable IP whitelisting for production
5. ✅ Monitor API usage in the dashboard
6. ✅ Set up alerts for unusual activity
7. ✅ Use separate keys for development and production

## Support

- **Documentation**: [obverse.onrender.com/api-docs](https://obverse.onrender.com/api-docs)
- **Discord**: [discord.gg/obverse](https://discord.gg/obverse)
- **Email**: obverse.ccc@gmail.com
- **Status Page**: [obverse.onrender.com](https://obverse.onrender.com)
- **GitHub Issues**: [github.com/obverse/openclaw-skill/issues](https://github.com/obverse/openclaw-skill/issues)

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## Roadmap

- [ ] One-click OAuth installation flow
- [ ] Fiat off-ramp integration (USDC → USD)
- [ ] Multi-currency support (EUR, GBP, etc.)
- [ ] Recurring subscription payments
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] More blockchain support (Ethereum, Polygon, Arbitrum)

## License

MIT License - see [LICENSE](./LICENSE) for details

## About Obverse

Obverse is a modern cryptocurrency payment platform built for the AI agent economy. We make it easy to accept stablecoin payments across multiple chains with low fees and instant settlement.

Built with:
- NestJS (Backend)
- React (Frontend)
- Turnkey (Wallet Infrastructure)
- Solana & Monad (Blockchains)
- OpenClaw (Agent Integration)

---

**Made with ❤️ by the Obverse Team**

[Website](https://obverse.cc) | [Twitter](https://twitter.com/obverse) | [Discord](https://discord.gg/obverse) | [GitHub](https://github.com/obverse)
