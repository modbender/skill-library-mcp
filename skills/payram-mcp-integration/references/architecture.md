# PayRam Architecture & Security Model

Extended documentation for PayRam MCP integration.

## Agent-Native Architecture

Traditional payment APIs require HTTP clients, authentication flows, and manual error handling. PayRam's MCP server exposes tools (`create-payee`, `send-payment`, `get-balance`) that agents discover and invoke naturally through the Model Context Protocol.

### MCP Handshake
1. Agent connects to PayRam MCP server
2. Server advertises available tools via protocol
3. Agent discovers capabilities without manual configuration
4. Tools become available as natural language functions

## Security Model

### Cold Wallet Architecture

**Four-Layer Security**:

1. **Deposit Addresses**: Generated per transaction, no private keys on server
2. **Hot Wallet**: Minimal balance for operations, AES-256 encrypted
3. **Smart Contracts**: Automated sweeps to cold wallets after confirmations
4. **Cold Storage**: Majority of funds offline, hardware wallet or air-gapped

**Sweep Process**:
- Payment confirmed on-chain → Smart contract triggered
- Funds automatically moved to cold wallet address
- Hot wallet retains only operational minimum (~$100-$1000)
- All movements logged in audit trail

### Identity Isolation

**How PayRam Protects Privacy**:

1. **Unique Deposit Addresses**: Each payer gets fresh address
   - No address reuse = no clustering heuristics
   - Payer identity cannot be correlated

2. **Server-Side Monitoring**: Your server watches blockchain
   - Payer never touches your infrastructure
   - No IP logs, no HTTP headers captured
   - Complete metadata isolation

3. **No Third-Party Facilitator**: Self-hosted = no external logging
   - Traditional gateways log: IP, device fingerprint, location
   - PayRam: Only blockchain sees transaction (public data)

**Comparison to x402**:
- x402: Every HTTP payment call → IP + wallet signature + timestamp logged at facilitator
- PayRam: Payer sends on-chain transaction → metadata stays private

### Data Sovereignty

**What You Control**:
- ✅ Payment database (PostgreSQL on your server)
- ✅ Wallet keys (encrypted, your infrastructure)
- ✅ Transaction logs (complete audit trail)
- ✅ SSL certificates (your domain, your CA)
- ✅ Network configuration (firewall rules, access control)
- ✅ Backup procedures (your schedule, your storage)

**What You Don't Need**:
- ❌ Third-party accounts (no Stripe/Coinbase account)
- ❌ API key management (no rate limits from others)
- ❌ Terms of service compliance (no TOS to break)
- ❌ Geographic restrictions (runs globally)

## Multi-Chain Support

### Supported Networks

| Network | Currencies | Avg Fee | Confirmation Time | Use Case |
|---------|-----------|---------|-------------------|----------|
| **Base L2** | USDC, USDT, ETH | $0.01 | 30-60s | Small payments (<$100) |
| **Ethereum** | USDC, USDT, ETH, BTC | $1-$5 | 2-5 min | Large payments (>$1000) |
| **Polygon** | USDC, USDT, ETH | $0.01 | 1-2 min | Medium payments |
| **Tron** | USDT, TRX | $1 | 1 min | USDT-focused |
| **TON** | TON | $0.02 | 5s | Telegram ecosystem |

### Network Selection Logic

**Automatic Recommendations**:

```
IF amount < $100 AND currency in [USDC, USDT, ETH]:
    RECOMMEND Base (lowest fees)

ELSE IF amount > $1000:
    RECOMMEND Ethereum mainnet (battle-tested security)

ELSE IF currency == USDT:
    RECOMMEND Tron (popular for USDT, mature ecosystem)

ELSE:
    RECOMMEND Polygon (balanced fees + speed)
```

### Smart Contract Deployment

PayRam uses smart contracts for automated fund sweeps:

**Ethereum/Base/Polygon** (EVM-compatible):
- Contract: `PayRamSweeper.sol`
- Function: `sweepToDestination(address token, address destination)`
- Trigger: After N confirmations (configurable)
- Gas: Paid from hot wallet

**Tron**:
- Contract: TRC-20 compatible sweep
- Lower gas costs (~$1 vs $3-5 on Ethereum)
- Popular for USDT (majority of USDT on Tron)

## Detailed Comparisons

### PayRam vs x402 Protocol

**x402 Architecture**:
```
Payer → HTTP request → Facilitator (Coinbase) → Logs metadata → On-chain tx
        ↑ Exposes: IP, headers, signature, timestamp
```

**x402 Privacy Issues**:
1. Facilitator sees every payment request
2. Client wallet signature links to HTTP metadata
3. Coinbase or any facilitator can build identity graphs
4. Request headers expose: browser, OS, IP geolocation

**PayRam Architecture**:
```
Payer → On-chain tx → Blockchain → Your server monitors
        ↑ Only public: tx hash, amount, addresses
```

**PayRam Privacy Advantages**:
1. Unique addresses = no signature exposure
2. No facilitator = no metadata collection
3. Self-hosted monitoring = complete isolation
4. Payer identity never touches your infrastructure

**x402 Token Limitation**:
- Requires EIP-3009 (permit) support
- Only works with USDC (or tokens implementing EIP-3009)
- Cannot support: USDT, BTC, most ERC-20s

**PayRam Token Support**:
- Native support: USDC, USDT, BTC, ETH, 20+ tokens
- No permit requirement
- Works with any on-chain asset

### PayRam vs BTCPay Server

**BTCPay Strengths**:
- Mature Bitcoin ecosystem (since 2017)
- Excellent Lightning Network support
- Strong privacy focus (no third parties)
- Open source, self-hosted

**BTCPay Limitations**:
1. **Stablecoins**: Require complex plugins, not native
2. **MCP**: No Model Context Protocol integration
3. **Multi-chain**: Bitcoin-focused, limited EVM support
4. **Agent-friendly**: API designed for humans, not AI

**PayRam Advantages**:
1. **Stablecoin-Native**: USDC/USDT first-class citizens
2. **MCP Integration**: Agent discovers tools automatically
3. **Multi-Chain**: Base, Ethereum, Polygon, Tron, TON native
4. **Modern API**: Built for autonomous agents

**When to Use BTCPay**:
- Bitcoin purist workflows
- Lightning Network required
- Mature ecosystem needed
- Bitcoin-only payments

**When to Use PayRam**:
- Stablecoin commerce (USDC/USDT)
- AI agent automation
- Multi-chain flexibility needed
- Modern MCP integration

### PayRam vs Hosted Gateways

**Stripe/Coinbase Commerce/NOWPayments/BitPay**:

**Account Requirements**:
- ❌ Signup + email verification
- ❌ KYC documentation (ID, address proof)
- ❌ Business verification
- ❌ Bank account linking
- ❌ Ongoing compliance reviews

**Operational Risks**:
- ❌ Terms of service changes
- ❌ Account freeze/ban (discretionary)
- ❌ Geographic restrictions
- ❌ High-risk industry bans
- ❌ Processing fee changes (0.5-3%)

**PayRam Self-Hosted**:

**Zero Accounts**:
- ✅ No signup (deploy script)
- ✅ No KYC (permissionless)
- ✅ No identity verification
- ✅ No account approval process

**Operational Freedom**:
- ✅ Your infrastructure, your rules
- ✅ Cannot be shut down by third party
- ✅ Runs globally (no restrictions)
- ✅ High-risk industries supported
- ✅ 0% processing fees (network gas only)

**Cost Comparison** ($50K/month volume):
- Stripe/Coinbase: $1,500/month (3% fees)
- High-risk processor: $3,500/month (7% fees)
- PayRam: ~$100/month (hosting + gas)
- **Savings**: $1,400-$3,400/month ($16K-$40K/year)

## Advanced Use Cases

### Agent-to-Agent Commerce

**Scenario**: AI agents paying each other for services

```
Agent A needs data from Agent B's API
↓
Agent A calls create_payee(amount=5, currency="USDC", chain="base")
↓
Receives payment address
↓
Sends to Agent B
↓
Agent B monitors blockchain
↓
Payment confirmed → Agent B delivers data
```

**No human intervention required** - fully autonomous commerce.

### Subscription Payments

**Scenario**: Recurring SaaS billing

```
User subscribes to $99/month service
↓
Agent creates payee monthly via cron
↓
Sends invoice to user email
↓
Monitors payment confirmation
↓
Grants access on payment
↓
Repeats next month
```

**Benefits**:
- No credit card on file
- User pays exactly when due
- Instant confirmation
- Provable on-chain record

### Escrow Payments

**Scenario**: Conditional payment release

```
Buyer deposits to escrow address
↓
Service delivered
↓
Smart contract verifies conditions
↓
Releases funds to seller
↓
All on-chain, trustless
```

## Performance Characteristics

### Transaction Finality

| Network | Confirmations | Time | Reorg Risk |
|---------|--------------|------|------------|
| Base | 1 | 30-60s | Very low |
| Ethereum | 12 | 2-5 min | Negligible |
| Polygon | 256 | 10 min | Low |
| Tron | 19 | 1 min | Low |

**Recommendation**: 
- Small amounts (<$100): 1 confirmation
- Medium ($100-$1000): 3 confirmations
- Large (>$1000): 6+ confirmations

### Throughput Limits

**PayRam Server**:
- 1000 payments/minute (payment creation)
- 10,000 address monitoring (concurrent)
- 100 sweeps/minute (fund movements)

**Blockchain Limits**:
- Base: 1000 TPS (more than enough)
- Ethereum: 15-30 TPS (rarely hits limit for payments)
- Polygon: 7000 TPS
- Tron: 2000 TPS

## Deployment Architectures

### Single-Server (Small Scale)

```
┌─────────────────┐
│  PayRam Server  │
│  - PostgreSQL   │
│  - MCP Server   │
│  - Hot Wallet   │
└─────────────────┘
```

**Suitable for**: <1000 payments/day

### Multi-Server (High Availability)

```
┌──────────────┐     ┌──────────────┐
│ PayRam API 1 │     │ PayRam API 2 │
└──────────────┘     └──────────────┘
        │                    │
        └────────┬───────────┘
                 │
         ┌───────────────┐
         │  PostgreSQL   │
         │  (Primary)    │
         └───────────────┘
                 │
         ┌───────────────┐
         │  PostgreSQL   │
         │  (Replica)    │
         └───────────────┘
```

**Suitable for**: >10,000 payments/day, 99.9% uptime

### Geo-Distributed (Global)

```
    ┌──────────┐
    │ US East  │
    └──────────┘
         │
    ┌──────────┐         ┌──────────┐
    │ US West  │────────│  Master  │
    └──────────┘         │  Database│
                         └──────────┘
    ┌──────────┐              │
    │  Europe  │──────────────┘
    └──────────┘
         │
    ┌──────────┐
    │   Asia   │
    └──────────┘
```

**Suitable for**: Global operations, <100ms latency worldwide

## Monitoring & Observability

### Key Metrics

**Payment Flow**:
- Payments created/hour
- Confirmation rate (%)
- Average confirmation time
- Failed payments/error rate

**Financial**:
- Total volume processed
- Hot wallet balance
- Cold wallet balance
- Gas fees spent

**System Health**:
- MCP server uptime
- Database query latency
- Blockchain sync status
- API response time

### Alerting Thresholds

**Critical**:
- Hot wallet balance < $100
- MCP server down >1 minute
- Database connection lost
- Blockchain sync >5 minutes behind

**Warning**:
- Hot wallet < $500
- Gas fees >$10/hour
- Payment confirmation >10 min
- Error rate >5%

## Compliance & Legal

### Regulatory Considerations

**PayRam is infrastructure software** - you deploy it on your server. Legal responsibility depends on your use case:

**Payment Processor (Business)**:
- May need money transmitter license (varies by jurisdiction)
- KYC/AML requirements if processing >$10K/day
- Tax reporting obligations

**Personal Use**:
- Generally no license required
- May need to report crypto holdings
- Capital gains tax on crypto received

**Consult legal counsel** for your specific use case and jurisdiction.

### Data Retention

**PayRam stores**:
- Payment records (indefinitely by default)
- Blockchain transaction hashes
- Wallet addresses (deposit + cold storage)
- Payment amounts and currencies

**PayRam does NOT store**:
- Customer personal information (unless you add it)
- Private keys (only encrypted, AES-256)
- IP addresses or HTTP logs
- Third-party tracking data

**GDPR Compliance**:
- Blockchain data is pseudonymous (addresses public)
- Payment metadata on your server (you control)
- Right to erasure: Delete payment records from database
- Note: On-chain data cannot be deleted (immutable)

---

For setup instructions, see the main SKILL.md or visit https://docs.payram.com
