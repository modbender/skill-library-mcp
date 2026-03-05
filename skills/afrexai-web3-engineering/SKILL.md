# Web3 & Blockchain Engineering

Complete methodology for evaluating, designing, building, securing, and operating blockchain-based systems. Covers smart contract development, DeFi protocol design, token economics, security auditing, and production operations.

> Zero dependencies. Framework-agnostic. Works with any blockchain, any language, any AI agent.

---

## Phase 1: Should You Use Blockchain?

### The Database Test

Before writing a single line of Solidity, answer honestly:

```yaml
blockchain_evaluation:
  problem: "[describe the core problem]"
  
  requirements:
    multiple_untrusting_parties: true/false    # >1 org needs shared truth
    no_trusted_authority: true/false            # no single party everyone trusts
    immutability_critical: true/false           # history must be tamper-proof
    censorship_resistance_needed: true/false    # no entity should block access
    value_transfer_required: true/false         # moving assets between parties
    transparency_required: true/false           # all parties need verifiable state
  
  disqualifiers:
    single_org_controls_data: true/false        # → use a database
    data_deletion_required: true/false          # → GDPR conflict, careful
    high_throughput_low_latency: true/false     # → >10K TPS? consider L2 or database
    users_cant_manage_wallets: true/false       # → account abstraction or custodial
    trusted_authority_exists: true/false        # → database with audit log
  
  score: "[count true requirements - count true disqualifiers]"
  verdict: "blockchain / hybrid / database"
```

**Decision rules:**
- Score ≤ 0 → Use PostgreSQL with audit logs
- Score 1-2 → Hybrid (anchoring/notarization on-chain, logic off-chain)
- Score 3+ → Blockchain is justified

### Platform Selection Matrix

| Platform | TPS | Finality | Gas Cost | Best For |
|----------|-----|----------|----------|----------|
| Ethereum L1 | ~30 | ~12 min | $1-50+ | Settlement, high-value DeFi |
| Arbitrum | ~4,000 | ~1 sec (soft) | $0.01-0.10 | DeFi, general dApps |
| Optimism | ~2,000 | ~2 sec (soft) | $0.01-0.15 | Public goods, governance |
| Base | ~2,000 | ~2 sec (soft) | $0.001-0.05 | Consumer apps, social |
| Polygon PoS | ~7,000 | ~2 sec | $0.001-0.01 | Gaming, mass-market |
| Solana | ~65,000 | ~400ms | $0.00025 | High-frequency, DePIN |
| Avalanche C | ~4,500 | ~1 sec | $0.01-0.10 | Enterprise, subnets |
| BNB Chain | ~2,000 | ~3 sec | $0.01-0.05 | Retail, low-cost |
| Bitcoin L1 | ~7 | ~60 min | $0.50-5+ | Store of value, settlement |
| Bitcoin L2 (Lightning) | ~1M+ | instant | <$0.01 | Micropayments, P2P |

**Selection decision tree:**
1. Store of value / settlement only? → Bitcoin
2. Micropayments / instant P2P? → Lightning Network
3. Need EVM compatibility? → Yes: continue. No: consider Solana, Cosmos
4. High-value DeFi / maximum security? → Ethereum L1
5. General dApp with low gas? → Arbitrum or Base
6. Mass-market consumer? → Base or Polygon
7. Enterprise with custom rules? → Avalanche subnets or Hyperledger

---

## Phase 2: Smart Contract Architecture

### Design Principles

1. **Minimize on-chain state** — Storage is expensive. Put data on-chain only if it needs consensus
2. **Fail loudly** — Use `require()` / `revert()` with descriptive messages, never silent failures
3. **Immutability by default** — Upgradeability adds attack surface. Only use if genuinely needed
4. **Separation of concerns** — One contract per responsibility
5. **Gas-conscious design** — Every operation costs money. Optimize hot paths

### Contract Architecture Patterns

```yaml
architecture_brief:
  project: "[name]"
  type: "DeFi / NFT / DAO / Token / Marketplace / Infrastructure"
  
  contracts:
    core:
      - name: "[MainContract]"
        responsibility: "[single clear purpose]"
        state_variables: ["list key storage"]
        external_calls: ["contracts it calls"]
    
    periphery:
      - name: "[Router/Helper]"
        responsibility: "[user-facing convenience]"
    
    libraries:
      - name: "[MathLib/SafeLib]"
        responsibility: "[shared pure functions]"
  
  upgrade_strategy: "immutable / transparent-proxy / UUPS / diamond / beacon"
  access_control: "Ownable / AccessControl / Timelock+Multisig / DAO"
```

### Upgrade Pattern Decision

| Pattern | Complexity | Gas Overhead | Storage Layout Risk | Best For |
|---------|-----------|-------------|-------------------|----------|
| Immutable | None | None | None | Simple contracts, tokens |
| Transparent Proxy | Medium | +gas per call | High | Standard upgradeable |
| UUPS | Medium | Lower than transparent | High | Gas-efficient upgradeable |
| Diamond (EIP-2535) | High | Medium | High | Large modular systems |
| Beacon | Medium | Medium | High | Many identical instances |

**Rule:** If you can avoid upgradeability, do it. If you must upgrade, use UUPS with timelock + multisig governance.

### Solidity Development Standards

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// — IMPORTS: Use named imports, pin versions —
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title VaultV1
/// @notice Single-asset vault with deposit/withdraw
/// @dev Uses SafeERC20 for all token transfers
contract VaultV1 is ReentrancyGuard {
    using SafeERC20 for IERC20;

    // — STATE: Group by slot for packing —
    IERC20 public immutable asset;       // slot 0
    uint128 public totalDeposits;        // slot 1 (packed)
    uint128 public totalShares;          // slot 1 (packed)
    
    mapping(address => uint256) public shares;

    // — EVENTS: Index searchable fields —
    event Deposited(address indexed user, uint256 amount, uint256 shares);
    event Withdrawn(address indexed user, uint256 amount, uint256 shares);

    // — ERRORS: Custom errors save gas vs strings —
    error ZeroAmount();
    error InsufficientShares(uint256 requested, uint256 available);

    constructor(IERC20 _asset) {
        asset = _asset;
    }

    /// @notice Deposit assets, receive proportional shares
    /// @param amount Asset amount to deposit
    /// @return mintedShares Shares minted to caller
    function deposit(uint256 amount) external nonReentrant returns (uint256 mintedShares) {
        if (amount == 0) revert ZeroAmount();
        
        // Calculate shares BEFORE transfer (prevent manipulation)
        mintedShares = totalDeposits == 0
            ? amount
            : (amount * totalShares) / totalDeposits;
        
        // Effects before interactions (CEI pattern)
        totalDeposits += uint128(amount);
        totalShares += uint128(mintedShares);
        shares[msg.sender] += mintedShares;
        
        // Interaction last
        asset.safeTransferFrom(msg.sender, address(this), amount);
        
        emit Deposited(msg.sender, amount, mintedShares);
    }
}
```

### Coding Standards Checklist

- [ ] NatSpec on every public/external function
- [ ] Custom errors instead of require strings (saves ~50 gas each)
- [ ] Events for every state change
- [ ] CEI pattern (Checks-Effects-Interactions) on every external call
- [ ] `nonReentrant` on functions with external calls
- [ ] `immutable` / `constant` where possible
- [ ] SafeERC20 for all token transfers
- [ ] No `tx.origin` for auth (phishing vector)
- [ ] Explicit visibility on all functions and state variables
- [ ] Storage variable packing (group smaller types together)

---

## Phase 3: Token Economics (Tokenomics)

### Token Type Decision

| Type | Standard | Use Case | Regulatory Risk |
|------|----------|----------|----------------|
| Utility token | ERC-20 | Access, governance, gas | Medium |
| Governance token | ERC-20 + voting | Protocol control | Medium |
| Security token | ERC-1400/3643 | Equity, revenue share | HIGH — requires compliance |
| NFT (unique) | ERC-721 | Collectibles, identity, access | Low-Medium |
| Semi-fungible | ERC-1155 | Gaming items, editions | Low |
| Soulbound (SBT) | ERC-5192 | Credentials, reputation | Low |
| Stablecoin | ERC-20 + peg | Payments, DeFi collateral | HIGH — regulatory scrutiny |

### Token Design Framework

```yaml
tokenomics:
  token_name: "[Name]"
  symbol: "[SYM]"
  standard: "ERC-20 / ERC-721 / ERC-1155"
  total_supply: "[fixed / capped / inflationary]"
  
  distribution:
    team: "[%] — [vesting schedule]"
    investors: "[%] — [vesting schedule]"
    community: "[%] — [distribution mechanism]"
    treasury: "[%] — [governance-controlled]"
    ecosystem: "[%] — [grants, incentives]"
    liquidity: "[%] — [DEX pairs, market making]"
  
  vesting:
    team_cliff: "12 months minimum"
    team_linear: "24-48 months after cliff"
    investor_cliff: "6-12 months"
    investor_linear: "12-36 months"
  
  value_accrual:
    mechanism: "[fee sharing / buyback-burn / staking yield / utility demand]"
    fee_structure: "[% of protocol revenue → token holders]"
    burn_mechanism: "[deflationary pressure source]"
  
  governance:
    voting_power: "1 token = 1 vote / quadratic / conviction"
    quorum: "[% of supply needed]"
    timelock: "[delay between vote and execution]"
    
  inflation_schedule:
    year_1: "[%]"
    year_2: "[%]"
    long_term: "[target %/year]"
    
  sustainability_test:
    without_new_buyers: "Does the token have utility even if price = 0?"
    revenue_source: "Where does yield come from? (real yield vs emissions)"
    death_spiral_risk: "Can selling pressure create feedback loop?"
```

### Tokenomics Red Flags

| Red Flag | Why It's Bad | Fix |
|----------|-------------|-----|
| >20% team allocation | Centralization, dump risk | Cap at 15-20%, long vesting |
| No cliff period | Immediate sell pressure | 12-month cliff minimum |
| Inflationary without utility | Token printing → zero | Emissions tied to real revenue |
| "Yield" from new deposits | Ponzi economics | Real yield from fees only |
| Governance without timelock | Admin can rug | Timelock + multisig mandatory |
| 100% unlocked at launch | Massive sell pressure | Staged unlock over 2-4 years |

---

## Phase 4: DeFi Protocol Design

### Core DeFi Primitives

| Primitive | What It Does | Key Risk | Examples |
|-----------|-------------|----------|----------|
| AMM (DEX) | Trustless token swaps | Impermanent loss | Uniswap, Curve |
| Lending | Overcollateralized loans | Liquidation cascades | Aave, Compound |
| Stablecoin | Price-stable token | Depeg risk | MakerDAO, Ethena |
| Yield aggregator | Optimize yield farming | Smart contract risk stacking | Yearn |
| Perpetuals | Leveraged derivatives | Liquidation, oracle manipulation | GMX, dYdX |
| Liquid staking | Stake + maintain liquidity | Slashing, depeg | Lido, Rocket Pool |
| Bridges | Cross-chain transfers | Bridge exploits (billions lost) | LayerZero, Wormhole |
| Restaking | Re-use staked assets | Cascading slashing | EigenLayer |

### AMM Design (Uniswap V2/V3 Pattern)

```
Constant Product: x * y = k
Price Impact: Δy = y - k/(x + Δx)
Slippage: (expected_price - actual_price) / expected_price

V3 Concentrated Liquidity:
- LPs choose price range [Pa, Pb]
- Capital efficiency: up to 4000x vs V2
- Trade-off: must actively manage positions
```

### DeFi Security Invariants

Every DeFi protocol MUST maintain these:

1. **Solvency** — Total assets ≥ total liabilities (always)
2. **No free tokens** — No path creates tokens from nothing
3. **Monotonic shares** — Depositing increases shares, withdrawing decreases
4. **Oracle freshness** — Price data is within acceptable staleness window
5. **Liquidation viability** — Undercollateralized positions can always be liquidated
6. **Access control** — Admin functions behind timelock + multisig
7. **Withdrawal guarantee** — Users can always withdraw their assets (no lock-up without consent)

---

## Phase 5: Security Auditing

### Vulnerability Taxonomy

| Category | Severity | Common Patterns |
|----------|----------|-----------------|
| Reentrancy | Critical | External call before state update |
| Oracle manipulation | Critical | Flash loan → price manipulation → profit |
| Access control | Critical | Missing auth on privileged functions |
| Integer overflow | High | Pre-0.8 math without SafeMath |
| Front-running | High | Sandwich attacks, MEV extraction |
| Flash loan attacks | High | Atomic arbitrage exploiting price feeds |
| Logic errors | High | Wrong formula, edge cases, rounding |
| Denial of service | Medium | Gas limit exploitation, stuck states |
| Centralization | Medium | Single admin key, no timelock |
| Griefing | Medium | Making others' transactions fail/expensive |

### Security Audit Checklist (100+ Points)

#### Critical (Must Pass)

- [ ] **Reentrancy protection** — All external calls follow CEI pattern OR use `nonReentrant`
- [ ] **Access control** — Every privileged function has appropriate modifier
- [ ] **Oracle security** — Price feeds have freshness checks, manipulation resistance
- [ ] **Integer safety** — Solidity ≥0.8 (built-in overflow checks) or SafeMath
- [ ] **Flash loan resistance** — Protocol functions work correctly within single transaction
- [ ] **Approval hygiene** — No unlimited approvals to untrusted contracts
- [ ] **Initialization** — Proxy contracts can only be initialized once
- [ ] **Self-destruct protection** — No `selfdestruct` in implementation contracts
- [ ] **Signature replay** — Nonces prevent signature reuse across chains/contracts

#### High Priority

- [ ] **Front-running protection** — Commit-reveal or deadline parameters on sensitive operations
- [ ] **Slippage protection** — Min output amounts on swaps/withdrawals
- [ ] **Rounding direction** — Always round in protocol's favor (against user)
- [ ] **Gas griefing** — External calls can't force excessive gas consumption
- [ ] **Token compatibility** — Handles fee-on-transfer, rebasing, and missing-return tokens
- [ ] **Withdrawal path** — Users can always exit, even if admin functions fail
- [ ] **Timelock on admin** — Governance changes have delay period
- [ ] **Key management** — Multisig for all admin functions, no single points of failure
- [ ] **Upgrade safety** — Storage layout preserved across upgrades (no slot collision)

#### Medium Priority

- [ ] **Event emission** — All state changes emit events for off-chain tracking
- [ ] **Input validation** — Zero address checks, bounds checking on parameters
- [ ] **Dust attacks** — Small deposits can't grief the accounting
- [ ] **Block timestamp** — No reliance on exact block.timestamp (manipulable ±15s)
- [ ] **Gas optimization** — No unbounded loops, batch operations have limits
- [ ] **Error messages** — Custom errors with meaningful context
- [ ] **Test coverage** — >95% line coverage, 100% on critical paths

### Common Attack Vectors with Mitigations

```
1. Reentrancy
   Attack: Call back into contract before state is updated
   Fix: CEI pattern + ReentrancyGuard
   
2. Oracle Manipulation (Flash Loan)
   Attack: Borrow → manipulate price → exploit → repay (atomic)
   Fix: TWAP oracles, Chainlink price feeds, manipulation-resistant design
   
3. Sandwich Attack (MEV)
   Attack: Front-run user's swap → inflate price → back-run to profit
   Fix: Deadline parameter, max slippage, private mempools (Flashbots)
   
4. Governance Attack
   Attack: Flash-borrow governance tokens → vote → execute
   Fix: Snapshot at proposal creation, timelock, vote escrow (ve-model)
   
5. Price Oracle Stale Data
   Attack: Use outdated price to exploit arbitrage
   Fix: Chainlink heartbeat check, staleness threshold, circuit breakers
```

### Audit Process

```yaml
audit_checklist:
  pre_audit:
    - [ ] Code freeze — no changes during audit
    - [ ] Documentation complete (spec, architecture, flow diagrams)
    - [ ] Test suite passing with >95% coverage
    - [ ] Known issues documented
    - [ ] Deployment scripts tested on testnet
    
  audit_scope:
    contracts: ["list all in-scope contracts"]
    lines_of_code: "[total Solidity LoC]"
    complexity: "low / medium / high / critical"
    prior_audits: "[list previous audit firms]"
    
  recommended_firms:
    tier_1: ["Trail of Bits", "OpenZeppelin", "Consensys Diligence"]
    tier_2: ["Spearbit", "Code4rena", "Sherlock"]
    bug_bounty: ["Immunefi (post-deployment)"]
    
  budget_guide:
    simple_token: "$5K-15K"
    defi_protocol: "$50K-200K"
    complex_system: "$200K-500K+"
    
  post_audit:
    - [ ] All critical/high findings fixed
    - [ ] Fix review by auditor
    - [ ] Audit report published (transparency)
    - [ ] Bug bounty program launched
```

---

## Phase 6: Testing Strategy

### Test Pyramid for Smart Contracts

```
                    /\
                   /  \        Mainnet Fork Tests
                  /    \       (real state, real tokens)
                 /------\
                /        \     Integration Tests
               /          \    (multi-contract interactions)
              /------------\
             /              \   Unit Tests
            /                \  (single function, isolated)
           /------------------\
          /                    \ Static Analysis
         /                      \ (Slither, Mythril, Aderyn)
        /________________________\
```

### Testing Checklist

```yaml
testing_requirements:
  static_analysis:
    tools: ["Slither", "Mythril", "Aderyn"]
    run: "On every commit (CI)"
    
  unit_tests:
    coverage_target: ">95% line, 100% critical paths"
    framework: "Foundry (preferred) or Hardhat"
    must_test:
      - All require/revert conditions
      - Boundary values (0, 1, max_uint256)
      - Access control on every privileged function
      - Math precision and rounding
      
  integration_tests:
    must_test:
      - Full user flows (deposit → earn → withdraw)
      - Multi-contract interactions
      - Upgrade paths (storage layout preservation)
      - Governance proposal → execution flow
      
  fork_tests:
    must_test:
      - Real mainnet state interactions
      - Oracle price feed behavior
      - Token compatibility (USDT, USDC, DAI, etc.)
      - Gas costs with real-world state size
      
  fuzz_tests:
    tool: "Foundry fuzz / Echidna / Medusa"
    invariants:
      - "Total supply == sum of all balances"
      - "Total assets >= total liabilities"
      - "Share price monotonically increases (yield vaults)"
      - "No function creates tokens from nothing"
      
  formal_verification:
    when: "Critical DeFi with >$10M TVL"
    tools: ["Certora", "Halmos", "KEVM"]
```

### Foundry Test Pattern

```solidity
// test/VaultV1.t.sol
contract VaultV1Test is Test {
    VaultV1 vault;
    MockERC20 token;
    address alice = makeAddr("alice");
    
    function setUp() public {
        token = new MockERC20("Test", "TST", 18);
        vault = new VaultV1(IERC20(address(token)));
        token.mint(alice, 1000e18);
        vm.prank(alice);
        token.approve(address(vault), type(uint256).max);
    }
    
    function test_deposit_mintsShares() public {
        vm.prank(alice);
        uint256 shares = vault.deposit(100e18);
        
        assertEq(shares, 100e18, "First deposit: 1:1 shares");
        assertEq(vault.shares(alice), 100e18);
        assertEq(vault.totalDeposits(), 100e18);
    }
    
    function test_deposit_revertsOnZero() public {
        vm.prank(alice);
        vm.expectRevert(VaultV1.ZeroAmount.selector);
        vault.deposit(0);
    }
    
    // Fuzz test: any deposit amount preserves invariants
    function testFuzz_deposit_invariants(uint128 amount) public {
        vm.assume(amount > 0 && amount <= token.balanceOf(alice));
        
        uint256 prevTotal = vault.totalDeposits();
        vm.prank(alice);
        vault.deposit(amount);
        
        assertEq(vault.totalDeposits(), prevTotal + amount);
        assertTrue(vault.totalShares() > 0);
    }
}
```

---

## Phase 7: Deployment & Operations

### Deployment Checklist

```yaml
pre_deployment:
  - [ ] All tests passing (unit, integration, fork, fuzz)
  - [ ] Static analysis clean (no high/critical findings)
  - [ ] Audit complete, all findings addressed
  - [ ] Deployment scripts tested on testnet (exact same flow)
  - [ ] Multisig wallets created and configured
  - [ ] Timelock contracts deployed and tested
  - [ ] Constructor arguments verified
  - [ ] Gas estimates confirmed within budget
  
deployment:
  - [ ] Deploy to mainnet from hardened machine
  - [ ] Verify source on block explorer (Etherscan)
  - [ ] Transfer ownership to multisig/timelock
  - [ ] Renounce deployer privileges
  - [ ] Test all functions with small amounts
  - [ ] Set initial parameters (fees, limits, oracles)
  
post_deployment:
  - [ ] Bug bounty program live (Immunefi)
  - [ ] Monitoring dashboards deployed
  - [ ] Alert rules configured
  - [ ] Documentation published
  - [ ] Community announcement
```

### Monitoring Dashboard

```yaml
smart_contract_monitoring:
  on_chain:
    - metric: "TVL (Total Value Locked)"
      alert: "Drop >10% in 1 hour"
      severity: "P0"
    - metric: "Unique active users (daily)"
      alert: "Drop >50% vs 7-day avg"
      severity: "P1"
    - metric: "Gas costs per transaction"
      alert: "Spike >3x average"
      severity: "P2"
    - metric: "Admin function calls"
      alert: "ANY unexpected admin call"
      severity: "P0"
    - metric: "Large withdrawals"
      alert: ">5% of TVL in single tx"
      severity: "P1"
      
  oracle:
    - metric: "Price feed freshness"
      alert: "Stale >30 minutes"
      severity: "P0"
    - metric: "Price deviation vs CEX"
      alert: ">2% deviation"
      severity: "P1"
      
  infrastructure:
    - metric: "RPC node health"
      alert: "Latency >500ms or errors"
      severity: "P1"
    - metric: "Indexer sync status"
      alert: ">100 blocks behind"
      severity: "P1"
```

### Incident Response

| Severity | Response Time | Actions |
|----------|-------------|---------|
| P0 — Active exploit | < 5 min | Pause contracts, war room, post-mortem |
| P1 — Vulnerability found | < 1 hour | Assess impact, prepare fix, notify team |
| P2 — Degraded service | < 4 hours | Investigate, fix, monitor |
| P3 — Minor issue | < 24 hours | Schedule fix in next deployment |

**P0 Emergency Protocol:**
1. Activate circuit breaker / pause contracts
2. Assess: What was exploited? What's the exposure?
3. Communicate: Alert team + trusted security researchers
4. Contain: Block exploit path if possible
5. Recover: Plan rescue transaction if funds recoverable
6. Post-mortem: Full timeline, root cause, fix, prevention

---

## Phase 8: Wallet & Key Management

### Key Hierarchy

```
Seed Phrase (BIP-39)
  └── Master Key
      ├── m/44'/60'/0'/0/0  → Ethereum Account 0
      ├── m/44'/60'/0'/0/1  → Ethereum Account 1
      ├── m/44'/0'/0'/0/0   → Bitcoin Account 0
      └── m/84'/0'/0'/0/0   → Bitcoin SegWit Account 0
```

### Wallet Security Tiers

| Tier | Type | Use Case | Security Level |
|------|------|----------|---------------|
| Hot wallet | Browser extension (MetaMask) | Daily interactions, small amounts | Low |
| Warm wallet | Mobile wallet (Rainbow, Trust) | Medium amounts, on-the-go | Medium |
| Cold wallet | Hardware (Ledger, Trezor) | Large holdings, long-term | High |
| Air-gapped | Keystone, dedicated offline | Maximum security, institutional | Very High |
| Multisig | Safe (Gnosis) | Treasury, protocol admin | Highest |

### Multisig Best Practices

```yaml
multisig_config:
  protocol_treasury:
    signers: 5
    threshold: 3  # 3-of-5
    signer_diversity:
      - Different devices/locations
      - Different key types (hardware + mobile)
      - No single point of failure
    timelock: "48 hours for >$100K"
    
  operational:
    signers: 3
    threshold: 2  # 2-of-3
    use_case: "Day-to-day parameter changes"
    timelock: "24 hours"
```

### Self-Custody Security Rules

1. **Seed phrase storage** — Metal plate (Cryptosteel/Billfodl), never digital
2. **Geographic distribution** — Copies in ≥2 physical locations
3. **Test recovery** — Verify you can restore from seed BEFORE storing value
4. **Phishing defense** — Bookmark official URLs, never click links, verify contract addresses
5. **Hardware wallet firmware** — Update only from official sources
6. **Transaction simulation** — Use Tenderly/Fire before signing large transactions
7. **Approval hygiene** — Revoke unused token approvals regularly (revoke.cash)

---

## Phase 9: Layer 2 & Scaling

### L2 Architecture Types

| Type | How It Works | Data Availability | Examples |
|------|-------------|-------------------|----------|
| Optimistic Rollup | Assume valid, challenge period | On-chain calldata | Arbitrum, Optimism, Base |
| ZK Rollup | Prove validity with ZK proof | On-chain calldata | zkSync, StarkNet, Scroll |
| Validium | ZK proof + off-chain data | Off-chain (DAC) | Immutable X |
| Plasma | Exit game mechanism | Off-chain | (largely deprecated) |
| State Channel | Off-chain with on-chain settlement | Off-chain | Lightning Network |
| Sidechain | Independent chain with bridge | Own consensus | Polygon PoS |

### Cross-Chain Bridge Security

Bridges are the #1 attack vector in crypto (>$2.5B lost).

**Bridge security checklist:**
- [ ] Multisig or decentralized validator set (not single key)
- [ ] Rate limiting on bridge transfers
- [ ] Monitoring for unusual withdrawal patterns
- [ ] Emergency pause functionality
- [ ] Regular security audits
- [ ] Insurance fund for bridge exploits

**Safer bridging approaches:**
1. Native bridges (Arbitrum/Optimism canonical) → Slow but trustless
2. LayerZero/Axelar → Decentralized messaging
3. Circle CCTP → Native USDC bridging (no wrapped tokens)
4. Avoid: New/unaudited bridges, single-key admin bridges

---

## Phase 10: Regulatory & Compliance

### Regulatory Landscape (2025)

| Jurisdiction | Framework | Token Classification | Key Requirement |
|-------------|-----------|---------------------|----------------|
| US (SEC) | Howey Test | Security vs Utility | Registration or exemption |
| US (CFTC) | CEA | Commodity (BTC, ETH) | Derivatives regulation |
| EU (MiCA) | Markets in Crypto-Assets | Utility/E-Money/ART | Licensing, reserves |
| UK (FCA) | Financial Promotions | Crypto-asset | Marketing restrictions |
| Singapore (MAS) | Payment Services Act | Digital Payment Token | Licensing |
| Japan (FSA) | FIEA/PSA | Crypto-asset | Registration |

### Compliance Checklist

```yaml
compliance:
  token_classification:
    - [ ] Legal opinion on token classification (security vs utility)
    - [ ] Howey test analysis documented
    - [ ] Jurisdictional analysis complete
    
  aml_kyc:
    - [ ] KYC/AML provider integrated (if applicable)
    - [ ] Sanctions screening (OFAC, EU, UN)
    - [ ] Transaction monitoring for suspicious activity
    - [ ] SAR (Suspicious Activity Report) filing process
    
  mca_eu:
    - [ ] Whitepaper published (if issuing tokens)
    - [ ] Notification to competent authority
    - [ ] Reserve requirements (for stablecoins)
    
  tax:
    - [ ] Tax treatment documented per jurisdiction
    - [ ] Reporting infrastructure (1099/DAC8)
    - [ ] Cost basis tracking for users
```

### Decentralization as Compliance Strategy

The more decentralized a protocol, the stronger the argument it's not a security:

| Factor | Centralized (Risky) | Decentralized (Safer) |
|--------|-------------------|---------------------|
| Development | Single company | Multiple contributor orgs |
| Governance | Admin key | Token-weighted DAO |
| Treasury | Company-controlled | Community-governed |
| Revenue | Flows to team | Flows to token holders |
| Upgrades | Admin deploys | Governance proposal + timelock |
| Front-end | Single website | Multiple alternative UIs |

---

## Phase 11: Bitcoin & Lightning Network

### Bitcoin Development

| Layer | Purpose | Key Technologies |
|-------|---------|-----------------|
| L1 (Base) | Settlement, store of value | Script, Taproot, SegWit |
| Lightning | Instant micropayments | Payment channels, HTLCs |
| Ordinals/BRC-20 | NFTs, tokens on Bitcoin | Inscription, witness data |
| Stacks/Liquid | Smart contracts on Bitcoin | Clarity, Federated sidechain |

### Lightning Network Integration

```yaml
lightning_integration:
  use_cases:
    - Micropayments (<$1)
    - Point-of-sale payments
    - Streaming payments (per-second)
    - Machine-to-machine payments
    - Tipping / donations
    
  implementation:
    self_hosted:
      options: ["LND", "CLN (Core Lightning)", "Eclair"]
      requirements: "Bitcoin full node + Lightning node"
      complexity: "High"
      
    hosted_api:
      options: ["Strike API", "Voltage", "LNbits", "BTCPay Server"]
      requirements: "API key"
      complexity: "Low-Medium"
      
    standards:
      invoices: "BOLT11 (payment request)"
      keysend: "Spontaneous payments (no invoice)"
      lnurl: "User-friendly payment flows"
      bolt12: "Reusable offers (emerging)"
```

### Bitcoin Self-Custody Best Practices

1. **UTXO management** — Consolidate during low-fee periods
2. **Address reuse** — Never reuse addresses (privacy)
3. **Coin selection** — Use coin control for privacy-sensitive transactions
4. **Fee estimation** — Use mempool.space for current fee rates
5. **Multi-sig** — 2-of-3 for significant holdings (Sparrow, Nunchuk)
6. **Verify receive addresses** — On hardware wallet screen, not just software

---

## Phase 12: Advanced Patterns

### MEV (Maximal Extractable Value)

```yaml
mev_awareness:
  what: "Value extracted by block producers reordering/inserting transactions"
  
  types:
    - sandwich_attack: "Front-run + back-run user's swap"
    - arbitrage: "Cross-DEX price differences"  
    - liquidation: "Race to liquidate undercollateralized positions"
    - jit_liquidity: "Just-in-time LP provision around large swaps"
    
  protection:
    users:
      - "Use private mempools (Flashbots Protect, MEV Blocker)"
      - "Set tight slippage limits"
      - "Use DEX aggregators with MEV protection (CoW Swap)"
      - "Submit transactions through RPC endpoints with MEV protection"
    developers:
      - "Commit-reveal schemes for sensitive operations"
      - "Batch auctions instead of continuous swaps"
      - "Deadline parameters on all swap functions"
      - "Internal oracle (TWAP) instead of spot price"
```

### Account Abstraction (ERC-4337)

```yaml
account_abstraction:
  what: "Smart contract wallets as first-class citizens"
  
  benefits:
    - Social recovery (friends can help recover account)
    - Gas sponsorship (app pays gas for users)
    - Batch transactions (multiple actions in one click)
    - Session keys (limited permissions for games/dApps)
    - Any token for gas (pay gas in USDC)
    
  implementation:
    frameworks: ["Safe{Core}", "ZeroDev", "Biconomy", "Alchemy AA"]
    bundlers: ["Pimlico", "Stackup", "Alchemy"]
    paymasters: ["Pimlico Verifying Paymaster", "Alchemy Gas Manager"]
    
  when_to_use:
    - Consumer-facing dApps (abstract wallet complexity)
    - Games (session keys, gasless)
    - B2B (multisig, spending policies)
```

### Zero-Knowledge Applications

| Application | What ZK Proves | Example |
|-------------|---------------|---------|
| Privacy transactions | "I have enough funds" without revealing amount | Tornado Cash, Zcash |
| Identity | "I'm over 18" without revealing age | Polygon ID, Worldcoin |
| Scaling (zkRollup) | "These transactions are valid" without re-executing | zkSync, StarkNet |
| Voting | "I voted" without revealing choice | MACI |
| Compliance | "I passed KYC" without sharing data | zkKYC |

### Gas Optimization Techniques

| Technique | Gas Saved | Complexity |
|-----------|-----------|-----------|
| Use `calldata` instead of `memory` for read-only params | ~60 per 32 bytes | Low |
| Pack storage variables (<256 bit types together) | ~20,000 per slot | Low |
| Use `immutable` / `constant` | ~2,100 per SLOAD avoided | Low |
| Custom errors vs require strings | ~50 per error | Low |
| Unchecked math (when overflow impossible) | ~80 per operation | Medium |
| Batch operations | Varies (amortize base cost) | Medium |
| Assembly for hot paths | 20-50% on targeted code | High |
| Minimal proxy (EIP-1167) for clones | ~90% deployment cost | Medium |

---

## Quality Rubric (0-100)

| Dimension | Weight | Score Guide |
|-----------|--------|-------------|
| Security | 25% | 0: No audit, known vulns. 50: Basic testing. 100: Full audit, bug bounty, formal verification |
| Architecture | 15% | 0: Monolithic, no separation. 50: Some patterns. 100: Clean separation, upgrade path, gas-optimized |
| Testing | 15% | 0: No tests. 50: Unit tests. 100: Full pyramid (unit/integration/fork/fuzz/invariant) |
| Tokenomics | 10% | 0: Ponzi mechanics. 50: Basic utility. 100: Sustainable value accrual, aligned incentives |
| Documentation | 10% | 0: No docs. 50: Basic README. 100: NatSpec, architecture docs, user guides |
| Operations | 10% | 0: No monitoring. 50: Basic alerts. 100: Full dashboard, incident playbooks, SLOs |
| Compliance | 10% | 0: Unaddressed. 50: Basic legal opinion. 100: Multi-jurisdictional analysis, KYC/AML |
| Decentralization | 5% | 0: Single admin key. 50: Multisig. 100: DAO governance, timelock, multiple UIs |

**Grade:** 80+ Excellent | 60-79 Good | 40-59 Needs Work | <40 Critical Risk

---

## Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Shipping without audit | Budget for audit from day 1 |
| 2 | Single admin key | Multisig + timelock always |
| 3 | Using spot price as oracle | TWAP or Chainlink |
| 4 | Ignoring MEV | Private mempool + slippage protection |
| 5 | No emergency pause | Circuit breaker on every protocol |
| 6 | Testing only happy path | Fuzz testing + invariant tests |
| 7 | Unlimited token approvals | Approve exact amounts needed |
| 8 | Ignoring gas optimization | Profile gas costs, optimize hot paths |
| 9 | No upgrade plan OR reckless upgrades | Decide upgrade strategy early |
| 10 | Building blockchain when database works | Run the Database Test first |

---

## Edge Cases

**Startup / Hackathon:**
- Use Foundry + OpenZeppelin for speed
- Deploy to Base (low gas, large ecosystem)
- Skip formal verification (do it pre-mainnet)
- Focus: working product > perfect security

**Enterprise / Institutional:**
- Hyperledger Besu or Avalanche Subnets for permissioned needs
- Formal verification for critical paths
- Multi-jurisdictional compliance from day 1
- Hardware security modules (HSMs) for key management

**High-Value DeFi (>$100M TVL):**
- Multiple independent audits (minimum 2 firms)
- Formal verification (Certora)
- $1M+ bug bounty on Immunefi
- Real-time monitoring with automatic pause triggers
- Insurance coverage (Nexus Mutual, InsurAce)

**NFT / Gaming:**
- ERC-1155 for gas efficiency (batch operations)
- Off-chain metadata (IPFS/Arweave for permanence)
- Account abstraction for onboarding (gasless minting)
- Consider L2 (Immutable X, Base, Polygon) for low gas

**Cross-Chain:**
- Start with one chain, expand after PMF
- Use canonical bridges (slow but safe) over third-party
- Implement chain-specific parameter tuning
- Monitor bridge TVL and security track record

---

## Natural Language Commands

When prompted, this skill responds to:

1. `evaluate blockchain fit` — Run the Database Test decision framework
2. `design smart contract` — Generate architecture brief + coding standards
3. `design tokenomics` — Create token economics framework with distribution
4. `audit security` — Run full security checklist against a contract
5. `plan deployment` — Generate deployment + post-deployment checklist
6. `assess DeFi protocol` — Evaluate DeFi design against security invariants
7. `optimize gas` — Review code for gas optimization opportunities
8. `review wallet security` — Generate wallet + key management recommendations
9. `evaluate L2` — Compare Layer 2 options for specific use case
10. `check compliance` — Run regulatory compliance checklist
11. `design bridge strategy` — Evaluate cross-chain approach
12. `full web3 review` — Complete assessment across all dimensions
