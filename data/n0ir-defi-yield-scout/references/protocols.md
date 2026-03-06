# Protocol Reference — n0ir Whitelisted Protocols

Detailed metadata for each protocol supported by the DeFi Yield Scout.

---

## Morpho (morpho-v1)

- **Chains:** Base, Arbitrum
- **Vault Standard:** ERC-4626
- **Audits:** Spearbit, Trail of Bits, Cantina
- **How it works:** Non-custodial lending protocol with immutable markets. Curated vaults allocate across multiple Morpho markets, managed by risk curators (e.g., Gauntlet, Steakhouse, Re7).
- **Risk notes:** Individual markets are immutable once deployed — no governance risk on market params. Curator risk exists at the vault level (allocation decisions). High code maturity.
- **USDC vaults:** Multiple curated vaults with different risk/return profiles (e.g., Steakhouse USDC, Gauntlet USDC).

## Euler v2 (euler-v2)

- **Chains:** Base, Arbitrum
- **Vault Standard:** ERC-4626
- **Audits:** Spearbit, Certora (formal verification), Trail of Bits
- **How it works:** Modular lending protocol. v2 is a complete rewrite after the v1 exploit ($197M, March 2023 — funds recovered). Vaults are composable and can reference each other.
- **Risk notes:** Formal verification via Certora adds assurance. Governor-managed vaults have admin risk. The v1 exploit was a reentrancy bug — v2 architecture eliminates that class of vulnerability.
- **USDC vaults:** Core lending vaults and specialized strategy vaults.

## Lazy Summer Protocol (lazy-summer-protocol)

- **Chains:** Base
- **Vault Standard:** ERC-4626
- **Audits:** Community audited
- **How it works:** Yield aggregator native to Base. Allocates deposits across underlying lending protocols to optimize returns. Previously known as Summer.fi deployment on Base.
- **Risk notes:** Aggregator risk — exposed to all underlying protocols. Newer protocol with lower battle-testing. Smart contract risk is additive (aggregator + underlying).
- **USDC vaults:** Aggregated USDC vault that rebalances across Base lending markets.

## Silo v2 (silo-v2)

- **Chains:** Base, Arbitrum
- **Vault Standard:** Custom (isolated markets)
- **Audits:** ABDK, Quantstamp
- **How it works:** Isolated lending markets — each pair is its own silo. Risk from one market cannot cascade to others. This is the key differentiator vs shared-pool models.
- **Risk notes:** Isolation model limits systemic risk but means liquidity is fragmented. Oracle risk per-market. Newer v2 with improved capital efficiency.
- **USDC vaults:** Per-pair lending positions (e.g., USDC-ETH silo, USDC-ARB silo).

## Moonwell (moonwell-lending)

- **Chains:** Base
- **Vault Standard:** cToken (Compound-style)
- **Audits:** Halborn, Code4rena
- **How it works:** Fork of Compound v2, originally on Moonbeam, expanded to Base. Governance-managed interest rate curves and collateral factors.
- **Risk notes:** Well-audited codebase (Compound fork). Governance can adjust parameters. WELL token rewards may inflate APY temporarily.
- **USDC vaults:** Direct supply market (mUSDC token).

## Compound v3 (compound-v3)

- **Chains:** Base, Arbitrum
- **Vault Standard:** Comet (single-borrowable-asset)
- **Audits:** OpenZeppelin, Trail of Bits, ChainSecurity
- **How it works:** Single-borrowable-asset model. Each Comet market supports one asset to borrow (e.g., USDC) with multiple collateral types. Simplified from v2.
- **Risk notes:** Most battle-tested DeFi lending code. COMP rewards supplement base APY but are subject to governance allocation. Minimal admin surface.
- **USDC vaults:** USDC Comet markets on Base and Arbitrum.

## Aave v3 (aave-v3)

- **Chains:** Base, Arbitrum
- **Vault Standard:** aToken (rebasing)
- **Audits:** SigmaPrime, Trail of Bits, Certora
- **How it works:** Largest DeFi lending protocol. Efficiency mode (E-mode) for correlated assets. Isolation mode for new/risky collateral. GHO stablecoin integration on mainnet.
- **Risk notes:** Highest TVL = most battle-tested. Complex governance (Aave DAO). Oracle dependency on Chainlink. aTokens rebase on transfer — some integrations may not handle this.
- **USDC vaults:** Direct supply markets. aUSDC token is rebasing.

## Harvest Finance (harvest-finance)

- **Chains:** Base, Arbitrum
- **Vault Standard:** Custom (fToken)
- **Audits:** Haechi, PeckShield
- **How it works:** Yield aggregator that auto-compounds rewards from underlying protocols. fTokens represent vault shares. Strategies are upgradeable by governance.
- **Risk notes:** Aggregator risk. Was exploited in October 2020 ($34M flash loan manipulation) — has since hardened. Strategy upgadeability is a governance trust assumption. iFARM staking adds another layer.
- **USDC vaults:** USDC auto-compounding vaults on both chains.

## 40 Acres (40-acres)

- **Chains:** Base
- **Vault Standard:** ERC-4626
- **Audits:** Community audited
- **How it works:** Newer lending/yield protocol on Base. Targets underserved DeFi segments.
- **Risk notes:** Low TVL = higher smart contract risk. Limited track record. Community audited (no major firm audit publicly available). Use with smaller allocations.
- **USDC vaults:** USDC lending pools on Base.

## Wasabi Protocol (wasabi-protocol)

- **Chains:** Arbitrum
- **Vault Standard:** Custom
- **Audits:** Community audited
- **How it works:** Options and perpetuals protocol. Yield for USDC depositors comes from options premiums and trading fees.
- **Risk notes:** Options protocols have counterparty/settlement risk. Yield is less predictable than lending. Lower TVL.
- **USDC vaults:** USDC liquidity pools backing options/perps.

## Yo Protocol (yo-protocol)

- **Chains:** Base
- **Vault Standard:** Custom
- **Audits:** Community audited
- **How it works:** Newer DeFi protocol on Base. Emerging yield source.
- **Risk notes:** Very new. Low TVL. No major firm audit. High smart contract risk. Treat as experimental allocation only.
- **USDC vaults:** USDC pools on Base.

---

## Chain Context

### Base
- **USDC address:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (native Circle USDC)
- **Gas costs:** Very low ($0.01–$0.10 per tx). Same-chain vault switches are cheap.
- **Bridge:** Standard Base bridge or third-party bridges (Across, Stargate) for cross-chain.

### Arbitrum
- **USDC address (native):** `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`
- **USDC.e address (bridged):** `0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8`
- **Gas costs:** Low ($0.05–$0.30 per tx). Higher than Base but still L2-cheap.
- **Bridge:** Arbitrum native bridge (7-day withdrawal) or fast bridges (Across, Stargate, Hop).

### Cross-Chain Considerations
- Bridging Base <-> Arbitrum typically costs $2–$15 depending on bridge and amount.
- Bridge time: 1–20 minutes for fast bridges, 7 days for native Arbitrum bridge.
- The breakeven tool estimates 3% cost for cross-chain moves (conservative, includes slippage + bridge fees for larger amounts).
- For amounts < $1,000, cross-chain moves are rarely worth it unless the APY difference is very large (>5 pp).
