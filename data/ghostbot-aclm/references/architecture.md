# GhostBot ACLM Architecture

## System Overview

GhostBot is a 3-layer system for automated concentrated liquidity management on Uniswap v4.

### Layer 1: Off-chain Bot Engine (TypeScript)
- **MarketAnalyzer**: Rolling 24h tick history, computes annualized volatility and trend (bullish/bearish/neutral)
- **RangeOptimizer**: Calculates optimal tick range using `halfWidth = kFactor * volatility`, applies trend bias (20% shift)
- **FeeOptimizer**: Dynamic fee 0.01%-1.00% based on volatility and volume
- **DecisionAggregator**: Confidence gating (>=70), 60s rate limit between oracle writes
- **Heartbeat**: Every 60 seconds

### Layer 2: On-chain Oracle (OpenClawOracle.sol)
- Stores rebalance signals in circular buffer (max 32 per pool)
- Stores fee recommendations (1 per pool, overwritten)
- Signal TTL: 5 minutes
- Access control: only authorized bot can write, only linked hook can read
- Validates: confidence 0-100, no future timestamps, staleness check

### Layer 3: On-chain Hook (OpenClawACLMHook.sol)
- Inherits `BaseCustomAccounting` — hook owns all liquidity, users get ERC6909 shares
- **beforeSwap**: Reads oracle fee recommendation, applies if confidence >= 70 and change > 10%
- **afterSwap**: Updates PoolStats (volume EMA, volatility), checks limit orders (max 10/swap), emits RebalanceRequested events
- **rebalancePosition**: Owner-callable, removes old liquidity, computes new range, adds liquidity, tracks surplus
- **Limit Orders**: Stop-loss, take-profit, trailing stop; tokens escrowed as ERC-6909 claims; atomic execution during swaps

## Data Flow

```
Market Data → MarketAnalyzer → RangeOptimizer → DecisionAggregator → Oracle.postRebalanceSignal()
                             → FeeOptimizer   →                    → Oracle.postFeeRecommendation()

Swap tx → Hook.beforeSwap() → Oracle.getDynamicFee() → poolManager.updateDynamicLPFee()
       → Hook.afterSwap()  → Update PoolStats
                            → Execute matching limit orders
                            → Emit RebalanceRequested if positions out of range

Bot detects event → Hook.rebalancePosition() → Remove old liquidity → Add new liquidity
```

## Security Features

- Confidence-gated signals (threshold: 70/100)
- Signal TTL expiry (5 minutes)
- Rebalance cooldown (default 1 hour, configurable)
- Per-swap execution caps (5 rebalances, 10 orders)
- Fee change hysteresis (>10% delta required)
- Reentrancy guard on order execution
- Pausable emergency stop
- Surplus tracking (no funds lost during rebalance)

## Contract Sizes

- OpenClawACLMHook: 24,366 bytes (210B under 24,576 limit)
- OpenClawOracle: 3,228 bytes
- Compiler: Solc 0.8.26, EVM Cancun, via_ir=true, optimizer_runs=200
