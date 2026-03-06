# PRISM OS — Architecture & Build Roadmap

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OPENCLAW AGENTS                              │
│  Finance Agent │ Spirit │ CLAWSHI │ YieldClaw │ Bankr │ AntiHunter  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                        PRISM OS SDK                                 │
│                   new PrismOS({ apiKey })                           │
│                                                                     │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────────────┐  │
│  │ assets   │ market   │ dex      │ cex      │ defi              │  │
│  ├──────────┼──────────┼──────────┼──────────┼───────────────────┤  │
│  │predict.  │ signals  │portfolio │ risk     │ execute           │  │
│  └──────────┴──────────┴──────────┴──────────┴───────────────────┘  │
│                                                                     │
│              ┌───────────────────────────────────┐                 │
│              │    CANONICAL ASSET RESOLVER        │                 │
│              │  "ETH" → prism:ethereum:eth        │                 │
│              │  Universal ID across all tools     │                 │
│              └───────────────────────────────────┘                 │
│                                                                     │
│              ┌───────────────────────────────────┐                 │
│              │    HTTP CLIENT                     │                 │
│              │  Auth │ Cache │ Retry │ Mock mode  │                 │
│              └───────────────────────────────────┘                 │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                     PRISM API GATEWAY                               │
│                                                                     │
│  CoinGecko │ CMC │ FMP │ DeFiLlama │ Uniswap │ Jupiter │ Polymarket │
│  Binance   │ Bybit │ OKX │ Hyperliquid │ Kalshi │ Manifold          │
│  Etherscan │ Solscan │ GoPlus │ De.Fi │ Tenderly                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow: Agent Trade Execution

```
Agent asks: "Buy $1000 of ETH on Base"

   │
   ▼
[1] assets.resolve("ETH", { chain: "base" })
    → "prism:ethereum:eth" (canonical ID, stable forever)
   │
   ▼
[2] risk.getTokenScore("prism:ethereum:eth")
    → score: 2/100 ✅ (proceed)
   │
   ▼
[3] dex.getQuote({ from: "USDC", to: "ETH", amount: "1000", chain: "base" })
    → quote: 0.3087 ETH, slippage: 0.1%, gas: $0.08
   │
   ▼
[4] risk.simulateTx(quoteTx, "base")
    → success: true, no MEV risk ✅
   │
   ▼
[5] dex.executeSwap(quote, signer)
    → txHash: 0x..., filled: 0.3087 ETH
   │
   ▼
[6] risk.watchAsset("ETH", { priceChangeThreshold: 0.05 })
    → watchId: watch_xyz, active ✅
```

## Canonical Asset Schema

Every single tool input and output uses PRISM-IDs. This is the lock-in.

```typescript
// PRISM-ID format: "prism:{primaryChain}:{symbol}"
// Examples:
"prism:ethereum:eth"     // Ethereum
"prism:solana:sol"       // Solana  
"prism:ethereum:usdc"    // USDC (primary chain = ethereum)
"prism:ethereum:weth"    // Wrapped ETH
"prism:solana:bonk"      // BONK

// The resolver handles ALL of these → same canonical ID:
resolve("ETH")           → "prism:ethereum:eth"
resolve("ethereum")      → "prism:ethereum:eth"
resolve("0xEeee...EEeE") → "prism:ethereum:eth"
resolve("Ether")         → "prism:ethereum:eth"
resolve("1027")          // CMC ID → "prism:ethereum:eth"
```

## Build Roadmap

### Phase 1 — Tier 1: Day 1 Essentials (Week 1-2)
Ship the minimum that makes PRISM useful to builders immediately.

- [ ] `assets.resolve` + canonical registry (100 top assets)
- [ ] `market.getPrice` + `getPriceMulti` (CoinGecko integration)
- [ ] `dex.getQuote` (Jupiter for Solana, 1inch for EVM)
- [ ] `dex.simulateSwap` (Tenderly for EVM, simulation API for Solana)
- [ ] `predictions.getMarkets` (Polymarket API)
- [ ] `risk.getTokenScore` (GoPlus + De.Fi aggregation)
- [ ] Auth (API key via Bearer token)
- [ ] Mock mode (all tools work without real API keys for dev)
- [ ] NPM publish: `@prismapi/sdk`

**Milestone:** A developer can `npm install @prismapi/sdk` and get prices, quotes, and prediction market data with one API key.

---

### Phase 2 — Tier 2: Sticky Features (Week 3-5)
What makes agents actually *want* to stay on PRISM.

- [ ] `portfolio.getMultiChainBalances` (Moralis/Alchemy)
- [ ] `portfolio.getPnL` (full realized + unrealized)
- [ ] `signals.getWhaleActivity` (Nansen/on-chain indexing)
- [ ] `signals.getSentiment` (Santiment or LunarCrush integration)
- [ ] `execute.arbitrage` (cross-venue price difference detection)
- [ ] `execute.dca` + `execute.twap` (algorithmic orders)
- [ ] `defi.getYields` (DeFiLlama integration)
- [ ] `execute.agentTreasuryManage` (Bankr/Juno use case)
- [ ] Webhooks + real-time alerts (risk monitoring)
- [ ] Expand canonical registry to 1000 assets

**Milestone:** Agents can track portfolios, get yield opps, run arb strategies, and receive real-time alerts.

---

### Phase 3 — Tier 3: The Moat (Week 6-10)
What makes PRISM irreplaceable.

- [ ] `execute.batch` (DAG-based atomic multi-step execution)
- [ ] `execute.conditional` (event-driven automation)
- [ ] `risk.simulateTx` (full Tenderly state simulation)
- [ ] `risk.checkAgentInjection` (security for agent pipelines)
- [ ] `execute.multiAgentCoord` (Virtual ACP compatibility)
- [ ] `execute.integrateX402` (Bankr micropayment layer)
- [ ] `risk.getAgentReputation` (ERC-8004 identity)
- [ ] `market.getAIScore` (ML scoring model, Kavout-style)
- [ ] `predictions.getMultiAgentConsensus` (fleet coordination)
- [ ] Cloud Hub Skill (one-click PRISM OS for no-code agents)
- [ ] Python SDK (`pip install prism-os`)
- [ ] Canonical registry: 10,000+ assets, self-healing via external APIs

**Milestone:** PRISM OS is the default financial OS for every agent in the OpenClaw ecosystem. New agents start with PRISM, not individual API integrations.

---

## OpenClaw Integration Pattern

```typescript
// In OpenClaw agent definition:
import { PrismOS } from '@prismapi/sdk'

export const agentConfig = {
  name: 'YieldClaw',
  tools: await new PrismOS({ apiKey: process.env.PRISM_KEY })
    .getToolManifest()  // Auto-registers all 44 tools
    .tools
    .filter(t => ['market', 'defi', 'execute'].includes(t.module))
}
```

## OpenClaw Agent → PRISM Module Mapping

| Agent | Primary Modules |
|-------|----------------|
| Finance Agent | market, portfolio, signals, execute |
| Spirit | market, signals, predictions |
| CLAWSHI | predictions, execute (agentBet) |
| YieldClaw | defi, assets (getRelatedYields), execute |
| Bankr | execute (x402), portfolio, defi |
| AntiHunter | assets (getUnlockSchedule), risk, signals |
| Juno | execute (treasury), portfolio, risk |
| TradeBoba | dex (agentLPEnter), defi, signals |

## Extension Points

Adding a new data source (e.g. Nansen for whale tracking):
1. Create `/src/providers/nansen.ts` implementing the provider interface
2. Register in `/src/providers/registry.ts`
3. Wire into relevant module (e.g. `signals.getWhaleActivity`)
4. PRISM-IDs stay stable — no agent code changes needed

Adding a new module (e.g. NFTs):
1. Create `/src/modules/nfts/index.ts`
2. Add to `PrismOS` constructor
3. Add to `getToolManifest()`
4. All existing agents unaffected
