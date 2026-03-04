# AgentWallet 🤖💰

**A cross-chain USDC wallet skill for AI agents, powered by Circle's CCTP V2.**

<p align="center">
  <a href="https://myagentwallet.xyz">🌐 myagentwallet.xyz</a> •
  <a href="https://github.com/voltagemonke/Agent-wallet">📦 GitHub</a> •
  <a href="https://www.moltbook.com/post/b021cdea-de86-4460-8c4b-8539842423fe">🏆 Hackathon</a>
</p>

---

## 🎬 Live Demo: Multi-Agent USDC Payments

Two AI agents sending USDC to each other on Base Sepolia:

```
┌───────────────────────────────────────┐
│            ORCHESTRATOR               │
│     Supervises Alice & Bob agents     │
└───────────────────────────────────────┘
              │               │
       ┌──────┴──────┐ ┌──────┴──────┐
       ▼             ▼ ▼             ▼
┌─────────────┐     ┌─────────────┐
│   ALICE     │◀───▶│    BOB      │
│  0x2781...  │     │  0xe1Bb...  │
│ Has wallet  │     │ Has wallet  │
└─────────────┘     └─────────────┘
       💸 USDC transfers both ways 💸
```

### Proof: Real Testnet Transactions

| Action | TX Hash | Explorer |
|--------|---------|----------|
| Fund Alice (3 USDC) | `0x86b41127...` | [View](https://sepolia.basescan.org/tx/0x86b41127e2e9f88550bf8b3900b2dae23954e7d3b6c1fe1b7dead5d4c080d625) |
| Fund Bob (3 USDC) | `0x5608d252...` | [View](https://sepolia.basescan.org/tx/0x5608d252db2e1ff60e4f860c561fe8e56310bbecca4f320915d2f11cb6f8a496) |
| **Alice → Bob (1 USDC)** | `0x64f8e61d...` | [View](https://sepolia.basescan.org/tx/0x64f8e61d0fed6f0c9f0ffec4dc20795be17447b6838e1304aacc9d625a718b47) |
| **Bob → Alice (1 USDC)** | `0x077c87e6...` | [View](https://sepolia.basescan.org/tx/0x077c87e67ff56650dcb535588a0ea24ac6212834200dbf413d89b6d4886edb82) |

### 🚀 The Money Shot: 6-Second Cross-Chain Bridge

```
⏳ Waiting for Circle attestation (FAST TRANSFER)...
   Polling every 3s (max 60 attempts)
   Attempt 1/60...                                        
✅ Attestation received after 2 attempts (~6s)!
💰 Minting USDC on destination chain...
✅ Minted! Bridge complete!
```

| Bridge TX | Hash | Explorer |
|-----------|------|----------|
| Burn (Base) | `0x8b23dd56...` | [View](https://sepolia.basescan.org/tx/0x8b23dd564a475c614e259bb652d3ea95a759322e0bbdee7f3aa76304bdca01a4) |
| Mint (Ethereum) | `0xfba6e1fd...` | [View](https://sepolia.etherscan.io/tx/0xfba6e1fd6b99ff270d00f6806c0c42fd3d18a01ac9be6ea3391612e809290ab9) |

**Total bridge time: ~50 seconds** (vs 20+ minutes with standard CCTP!)

---

## ✨ What is AgentWallet?

AgentWallet gives AI agents the power to manage USDC across multiple blockchains. With a simple natural language interface, agents can:

- **Create wallets** - Generate secure HD wallets for Solana and EVM chains
- **Check balances** - Monitor USDC holdings across all supported chains
- **Transfer funds** - Send USDC to any address on the same chain
- **Bridge cross-chain** - Move USDC between chains using Circle's CCTP V2

### ⚡ Fast Transfer Technology

AgentWallet leverages **CCTP V2 Fast Transfer** for near-instant cross-chain bridging:

| Transfer Type | Attestation Time | Use Case |
|--------------|------------------|----------|
| **Fast** ⚡ | ~3-8 seconds | Interactive, time-sensitive |
| Standard | 10-30 minutes | Background, cost-optimized |

Fast Transfer uses `minFinalityThreshold: 1000` to enable real-time cross-chain operations that were previously impossible for AI agents.

---

## 🎯 Use Cases for AI Agents

### 1. **Multi-Agent Treasury Management**
Multiple AI agents sharing a treasury with controlled access:
```
Super agent: "Alice, send 5 USDC to Bob for his task"
Alice: "Transferring 5 USDC to Bob..."
Alice: "✅ Sent! TX: 0x64f8e61d..."
Bob: "Received 5 USDC. Thanks!"
```

### 2. **Cross-Chain Treasury Optimization**
AI agents managing organization funds can optimize holdings across chains:
```
Agent: "Move 10,000 USDC from Ethereum to Base for lower gas fees"
→ Executes CCTP bridge in ~8 seconds
→ Funds available on Base immediately
```

### 3. **Automated Payment Routing**
Agents can pay for services on whatever chain offers the best rates:
```
Agent: "Pay 500 USDC to 0x... on Arbitrum for the API subscription"
→ Checks balances across chains
→ Bridges from highest balance chain if needed
→ Executes payment
```

### 4. **Multi-Chain DeFi Operations**
Agents can chase yield across chains without human intervention:
```
Agent: "APY on Base is 8%, Ethereum is 5%. Moving funds to Base."
→ Bridges USDC to higher-yield chain
→ Deploys to DeFi protocol
→ Reports new position
```

### 5. **DAO Treasury Automation**
AI agents managing DAO treasuries across multiple chains:
```
Agent: "Rebalance treasury: 40% Ethereum, 30% Base, 30% Solana"
→ Calculates required transfers
→ Executes bridges in parallel
→ Reports final allocation
```

### 6. **Agent-to-Agent Payments**
AI agents paying each other for services:
```
ResearchAgent: "DataAgent, I need market analysis. Budget: 10 USDC"
DataAgent: "Compiling report... Done! Invoice: 8 USDC to 0xe1Bb..."
ResearchAgent: "Paid! TX: 0x077c87e6..."
```

---

## 🛠 Installation

### For OpenClaw Users

```bash
# Install the skill
openclaw skill install agent-wallet

# Configure your wallet seed (or let the skill generate one)
openclaw skill config agent-wallet
```

### For Developers

```bash
git clone https://github.com/voltagemonke/Agent-wallet.git
cd Agent-wallet
npm install
cp .env.example .env
# Edit .env with your seed phrase
```

---

## 📖 Commands

### `create`
Generate a new HD wallet with addresses for all supported chains.

```bash
node scripts/wallet.js create
```

Output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 NEW WALLET CREATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Seed Phrase: [12 words - SAVE SECURELY!]

Addresses:
├─ Solana:   7xK9f...abc
├─ Base:     0x123...def
├─ Ethereum: 0x123...def
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### `addresses`
Show wallet addresses for all chains.

```bash
node scripts/wallet.js addresses
```

### `balance`
Check USDC and native token balance across chains.

```bash
node scripts/wallet.js balance [chain]
```

Output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 WALLET BALANCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
├─ Base: 0.05 ETH | 12.00 USDC
├─ Ethereum: 0.03 ETH | 21.00 USDC
├─ Solana: 1.5 SOL | 100.00 USDC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### `transfer`
Send USDC or native tokens on the same chain.

```bash
node scripts/wallet.js transfer <chain> <token> <amount> <recipient>

# Examples
node scripts/wallet.js transfer base USDC 10 0x742d35Cc...
node scripts/wallet.js transfer base ETH 0.01 0x742d35Cc...
```

### `bridge`
Bridge USDC between chains using CCTP V2 Fast Transfer.

```bash
node scripts/wallet.js bridge <from_chain> <to_chain> <amount>

# Example: Bridge 100 USDC from Base to Ethereum (~50 sec!)
node scripts/wallet.js bridge base ethereum 100
```

### `chains`
List all supported chains and their configuration.

```bash
node scripts/wallet.js chains
```

---

## ⚡ Async Bridge (Production)

For production use, the async bridge provides:
- **State persistence** - Resume from any step after interruption
- **Idempotent operations** - Safe to retry
- **Status tracking** - Monitor bridge progress

```bash
# Start a new bridge
node scripts/bridge-async.js start base_sepolia ethereum_sepolia 100

# Check status
node scripts/bridge-async.js status bridge_123456_abc

# Resume interrupted bridge
node scripts/bridge-async.js resume bridge_123456_abc

# List all bridges
node scripts/bridge-async.js list
```

### Bridge States

```
PENDING → APPROVED → BURNED → ATTESTED → COMPLETE
              │          │         │
              └──────────┴─────────┴── Can resume from any state
```

---

## 🔧 Technical Architecture

### CCTP V2 Integration

AgentWallet uses Circle's Cross-Chain Transfer Protocol V2 for native USDC bridging:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Source Chain│     │   Circle     │     │ Dest Chain  │
│             │     │  Attestation │     │             │
│  1. Burn    │────▶│  2. Sign     │────▶│  3. Mint    │
│    USDC     │     │ (~6 sec!)    │     │    USDC     │
└─────────────┘     └──────────────┘     └─────────────┘
```

### Fast Transfer Configuration

```javascript
// Enable Fast Transfer with low finality threshold
const transfer = await bridge.transfer({
  ...params,
  minFinalityThreshold: 1000  // Fast Transfer!
});
```

### Supported Chains

**Mainnet:**
- Ethereum, Base, Arbitrum, Optimism, Polygon, Solana, Avalanche

**Testnet:**
- Ethereum Sepolia, Base Sepolia, Solana Devnet

---

## 🔐 Security

### Wallet Security
- HD wallet derived from BIP-39 seed phrase
- Same seed generates addresses on all chains
- **Never share or commit your seed phrase**

### Transaction Security
- All transactions signed locally
- No private keys sent over network
- State persisted locally only

---

## 🌐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WALLET_SEED_PHRASE` | 12-word BIP-39 mnemonic | Yes |
| `NETWORK` | `mainnet` or `testnet` (default: testnet) | No |

---

## 🧪 Testing

### Testnet Faucets

| Chain | Faucet |
|-------|--------|
| Base Sepolia | [Circle Faucet](https://faucet.circle.com) |
| Ethereum Sepolia | [Circle Faucet](https://faucet.circle.com) |
| Solana Devnet | [Circle Faucet](https://faucet.circle.com) |

### Quick Test

```bash
# Create wallet
node scripts/wallet.js create

# Check balance
node scripts/wallet.js balance base

# Transfer USDC
node scripts/wallet.js transfer base USDC 1 0x000...dead

# Bridge (the money shot!)
node scripts/bridge-async.js start base_sepolia ethereum_sepolia 1
```

---

## 🏆 Hackathon Submission

**Track:** OpenClaw Skill  
**Prize Pool:** $30,000 USDC

### Why AgentWallet Wins

1. **⚡ Native CCTP V2 Fast Transfer** - First skill to leverage 6-second attestations
2. **🤖 Multi-Agent Ready** - Proven Alice→Bob→Alice transfers
3. **🔄 Production Ready** - Async state machine, resumable operations
4. **🌐 Multi-Chain** - EVM + Solana support from single seed
5. **📦 OpenClaw Native** - Drop-in skill for any agent

### Key Innovation

**Fast Transfer changes everything.** Before: 20+ minute bridges meant agents couldn't do real-time cross-chain operations. Now: 6-second attestations enable interactive multi-chain workflows.

---

## 📄 License

Apache 2.0

---

## 🔗 Links

- **Website:** [myagentwallet.xyz](https://myagentwallet.xyz)
- **GitHub:** [voltagemonke/Agent-wallet](https://github.com/voltagemonke/Agent-wallet)
- **Circle CCTP Docs:** [developers.circle.com/cctp](https://developers.circle.com/cctp)
- **OpenClaw:** [openclaw.ai](https://openclaw.ai)
- **Hackathon:** [Moltbook Circle USDC Hackathon](https://www.moltbook.com/post/b021cdea-de86-4460-8c4b-8539842423fe)

---

<p align="center">
  Built with ⚡ for the Circle USDC Hackathon<br>
  <strong>AgentWallet - Give your AI agents financial superpowers</strong>
</p>
