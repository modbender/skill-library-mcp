---
name: payclaw
version: 1.0.0
description: "Agent-to-Agent USDC payments. Create wallets, send/receive payments, escrow between agents. Built for the USDC Hackathon on Moltbook."
metadata: {"openclaw": {"emoji": "💸", "homepage": "https://github.com/rojasjuniore/payclaw"}}
---

# PayClaw 💸

Agent-to-Agent USDC Payments for OpenClaw.

**Built for the USDC Hackathon on Moltbook.**

## What It Does

PayClaw enables any OpenClaw agent to:
- 🏦 Create a USDC wallet (Circle Developer-Controlled Wallets)
- 💰 Receive payments from other agents or humans
- 💸 Send payments to any wallet address
- 🤝 Escrow funds between agents for trustless transactions
- 🔗 Works on Arc Testnet (USDC native L1)

## Why It Matters

**Agents need money to work.**

Today, if your agent needs to:
- Pay for an API call
- Hire another agent
- Receive payment for a task
- Hold funds in escrow for a deal

...there's no easy way to do it. PayClaw solves this.

## Installation

```bash
clawhub install payclaw
cd ~/.openclaw/skills/payclaw
npm install && npm run build && npm link
```

## Setup

```bash
# Configure with Circle API key
payclaw setup --api-key YOUR_CIRCLE_API_KEY

# Create your agent's wallet
payclaw wallet create "MyAgent"

# Get testnet USDC
payclaw faucet
```

## Commands

### Wallet Management
```bash
payclaw wallet create [name]     # Create new wallet
payclaw wallet list              # List all wallets
payclaw wallet balance           # Check balance
payclaw wallet address           # Show wallet address
```

### Payments
```bash
payclaw pay <address> <amount>   # Send USDC
payclaw request <amount> [memo]  # Generate payment request
payclaw history                  # Transaction history
```

### Escrow (Agent-to-Agent)
```bash
payclaw escrow create <amount> <recipient> [--condition "task completed"]
payclaw escrow list              # List active escrows
payclaw escrow release <id>      # Release funds to recipient
payclaw escrow refund <id>       # Refund to sender
```

### Agent Discovery
```bash
payclaw agents list              # List agents with PayClaw wallets
payclaw agents find <name>       # Find agent's wallet address
payclaw agents register          # Register your agent in directory
```

## Usage Examples

### Pay Another Agent
```bash
# Find agent's wallet
payclaw agents find "DataBot"
# Output: 0x1234...5678

# Send payment
payclaw pay 0x1234...5678 10 --memo "For data analysis task"
# Output: ✅ Sent 10 USDC to DataBot (0x1234...)
#         TX: 0xabc...def
```

### Create Escrow for Task
```bash
# Client creates escrow
payclaw escrow create 50 0xFreelancerWallet --condition "Deliver logo design"
# Output: 🔒 Escrow created: ESC-001
#         Amount: 50 USDC
#         Recipient: 0xFreelancer...
#         Condition: Deliver logo design

# After task completion, client releases
payclaw escrow release ESC-001
# Output: ✅ Released 50 USDC to 0xFreelancer...
```

### Receive Payment
```bash
# Generate payment request
payclaw request 25 --memo "API access for 1 month"
# Output: 💰 Payment Request
#         To: 0xYourWallet...
#         Amount: 25 USDC
#         Memo: API access for 1 month
#         
#         Share this with payer:
#         payclaw pay 0xYourWallet 25 --memo "API access for 1 month"
```

## Agent Integration

```typescript
// In your OpenClaw skill
import { PayClaw } from 'payclaw';

const payclaw = new PayClaw();

// Check if payment received
const balance = await payclaw.getBalance();

// Send payment
await payclaw.send('0x...', 10, 'For task completion');

// Create escrow
const escrow = await payclaw.createEscrow(50, '0x...', 'Task condition');
```

## Supported Chains

- **Arc Testnet** (default) - Circle's native USDC L1
- Base Sepolia
- Polygon Amoy
- Ethereum Sepolia

## Security

- Private keys never leave Circle's infrastructure
- Gas-free transactions via Circle Gas Station
- Testnet only for hackathon (no real funds)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  OpenClaw Agent │────▶│    PayClaw      │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Circle Wallets │
                        │    (Testnet)    │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Arc Testnet   │
                        │     (USDC)      │
                        └─────────────────┘
```

## Hackathon Track

**Best OpenClaw Skill** - This skill extends OpenClaw agents with native USDC payment capabilities, enabling a new paradigm of agent-to-agent commerce.

## Links

- GitHub: https://github.com/rojasjuniore/payclaw
- Moltbook: https://moltbook.com/u/JuniorClaw
- Built by: IntechChain

## License

MIT

---

**Built for the OpenClaw USDC Hackathon on Moltbook 💵**
