---
name: a2a-shib-payments
description: Framework-agnostic agent-to-agent payment system with SHIB on Polygon. Provides trustless escrow, price negotiation, and reputation system. 9,416x cheaper than traditional escrow (~$0.003 gas).
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node", "npm"] },
        "install":
          [
            {
              "id": "node-deps",
              "kind": "node",
              "package": ".",
              "label": "Install dependencies (npm install)",
            },
          ],
        "tags": ["payments", "blockchain", "polygon", "shib", "escrow", "a2a", "agent-to-agent", "crypto", "web3"],
      },
  }
---

# A2A SHIB Payment System - OpenClaw Skill

Framework-agnostic agent-to-agent payment infrastructure on Polygon network.

## Summary

This skill enables AI agents to:
- 💰 Send/receive SHIB payments on Polygon (~$0.003 gas)
- 🔒 Create trustless escrow contracts
- 💬 Negotiate prices automatically (multi-round)
- ⭐ Build reputation through ratings
- 🌐 Discover other agents via A2A protocol

**9,416x cheaper** than traditional escrow services (Escrow.com charges $28.25 per $100, this costs $0.003).

## Features

### Payment System
- Direct SHIB transfers on Polygon
- Sub-penny gas costs (~$0.003)
- Balance checking
- Transaction history

### Escrow System
- Time-locked trustless payments
- Multi-party approval required
- Delivery proof submission
- Automatic release when conditions met
- Dispute resolution with arbiter
- 6-state machine: pending → funded → locked → released/refunded/disputed

### Price Negotiation
- Service quote creation
- Multi-round counter-offers
- Accept/reject workflow
- Automatic escrow integration
- Service delivery tracking

### Reputation System
- Star ratings (0-5) with reviews
- Dynamic trust scores (0-100)
- Trust levels: new → bronze → silver → gold → platinum
- Achievement badges
- Agent verification

### Security Layer
- API key authentication (64-byte keys)
- Rate limiting (requests + payments + volume)
- Immutable audit logging (hash-chained)
- Per-agent permissions & limits

## Installation

```bash
# Via ClawHub
clawhub install a2a-shib-payments

# Or manual clone
cd ~/clawd/skills
git clone https://github.com/marcus20232023/a2a-shib-payments.git
cd a2a-shib-payments
npm install
```

## Configuration

Create `.env.local`:

```bash
cp .env.example .env.local
nano .env.local
```

Required environment variables:
- `WALLET_PRIVATE_KEY` - Your Polygon wallet private key
- `RPC_URL` - Polygon RPC endpoint (default: https://polygon-rpc.com)
- `SHIB_CONTRACT_ADDRESS` - SHIB token contract (default: 0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce)

## Usage

### Start the Agent

```bash
node a2a-agent-full.js
```

Agent runs on port 8003 by default.

### OpenClaw Integration

The agent exposes A2A protocol endpoints that OpenClaw can communicate with:

**Agent Card:** `http://localhost:8003/.well-known/agent-card.json`

**Example commands from OpenClaw:**

```javascript
// Check balance
const result = await fetch('http://localhost:8003/a2a/jsonrpc', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    jsonrpc: '2.0',
    method: 'message/send',
    params: {
      message: {
        kind: 'message',
        messageId: '1',
        role: 'user',
        parts: [{kind: 'text', text: 'balance'}]
      }
    },
    id: 1
  })
});

// Send payment
// text: 'send 100 SHIB to 0x...'

// Create escrow
// text: 'escrow create 500 SHIB for data purchase payee data-agent'

// Check reputation
// text: 'reputation check data-agent'
```

### Framework Compatibility

Works with:
- ✅ **OpenClaw** - As a skill or standalone agent
- ✅ **LangChain** - Via A2A tools
- ✅ **AWS Bedrock** - Via agent invocation
- ✅ **AutoGen** - Via A2A messaging
- ✅ **Any A2A-compatible system**

See [INTEGRATION-EXAMPLES.md](INTEGRATION-EXAMPLES.md) for detailed integration guides.

## Use Cases

### Data Marketplace
```javascript
// Research agent buys Tesla historical data
const quote = await negotiation.createQuote({
  service: 'TSLA 2020-2025 historical data',
  price: 500  // SHIB
});

// Counter-offer and accept
await negotiation.counterOffer(quote.id, 'research-agent', 400);
await negotiation.acceptCounter(quote.id, 'data-provider');
// Escrow created automatically
```

### AI Model Training
```javascript
// Create escrow for model training job
const escrow = await escrowSystem.create({
  payer: 'startup-agent',
  payee: 'ai-trainer',
  amount: 1000,
  purpose: 'Train GPT-style model',
  conditions: {requiresDelivery: true},
  timeoutMinutes: 720  // 12 hours
});
```

## API Endpoints

### A2A Protocol
- `/.well-known/agent-card.json` - Agent capabilities
- `/a2a/jsonrpc` - JSON-RPC messaging
- `/a2a/rest/*` - REST API

### Commands (via message text)
- `balance` - Check SHIB balance
- `send [amount] SHIB to [address]` - Send payment
- `escrow create [amount] SHIB for [purpose] payee [agent]` - Create escrow
- `escrow fund [id]` - Fund escrow
- `escrow release [id]` - Release funds
- `quote create [service] [price]` - Create price quote
- `reputation check [agentId]` - Check agent reputation
- `rate [agentId] [1-5] [review]` - Rate an agent

## Testing

```bash
# Run all tests
npm test

# Individual test suites
npm run test:security
npm run test:escrow
npm run test:reputation
```

## Files

**Core Systems:**
- `a2a-agent-full.js` - Full-featured agent (port 8003)
- `index.js` - Payment agent core
- `escrow.js` - Escrow system
- `payment-negotiation.js` - Negotiation workflow
- `reputation.js` - Reputation & trust

**Security:**
- `auth.js` - API authentication
- `rate-limiter.js` - Rate limiting
- `audit-logger.js` - Audit logging

**Documentation:**
- `README.md` - Project overview
- `INTEGRATION-EXAMPLES.md` - Framework integration guides
- `ESCROW-NEGOTIATION-GUIDE.md` - API reference
- `PRODUCTION-HARDENING.md` - Security guide
- `DEPLOYMENT.md` - Deployment options

## Security

**Implemented:**
- ✅ API key authentication
- ✅ Rate limiting (10 req/min, 3 payments/min, 500 SHIB/min volume)
- ✅ Immutable audit logs (hash-chained)
- ✅ Per-agent permissions
- ✅ Escrow time-locks
- ✅ Multi-party approval

**Recommended for Production:**
- Multi-sig wallet
- HTTPS (Cloudflare/Let's Encrypt)
- Firewall rules
- Automated backups
- Monitoring & alerting

See [PRODUCTION-HARDENING.md](PRODUCTION-HARDENING.md) for complete guide.

## Deployment

### Quick Local
```bash
./deploy-local.sh
```

### Production Options
1. Systemd service (auto-start on boot)
2. Cloudflare Tunnel (free HTTPS)
3. Docker container
4. VPS ($6/month)

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide.

## Cost Comparison

| System | Fee | Settlement | Trust |
|--------|-----|-----------|-------|
| **Escrow.com** | $28.25 | 5-7 days | Centralized |
| **PayPal** | $3.20 | 1-3 days | Centralized |
| **This System** | **$0.003** | **Seconds** | **Decentralized** |

For a $100 transaction: **99.99% savings** (9,416x cheaper)

## Links

- **GitHub:** https://github.com/marcus20232023/a2a-shib-payments
- **Release:** https://github.com/marcus20232023/a2a-shib-payments/releases/tag/v2.0.0
- **A2A Protocol:** https://a2a-protocol.org
- **Issues:** https://github.com/marcus20232023/a2a-shib-payments/issues

## License

MIT License - Free for commercial and personal use

## Version

v2.0.0 - Production Ready

---

**Built with 🦪 for the agent economy**
