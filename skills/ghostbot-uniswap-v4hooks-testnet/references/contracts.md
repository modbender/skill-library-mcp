# Deployed Contracts Reference

## Network: Ethereum Sepolia (Chain ID: 11155111)

### OpenClawACLMHook
- **Address**: `0xbD2802B7215530894d5696ab8450115f56b1fAC0`
- **Etherscan**: https://sepolia.etherscan.io/address/0xbD2802B7215530894d5696ab8450115f56b1fAC0
- **Type**: Uniswap v4 Hook (BaseCustomAccounting)
- **Permissions**: BEFORE_INITIALIZE, AFTER_INITIALIZE, BEFORE_ADD_LIQUIDITY, BEFORE_REMOVE_LIQUIDITY, BEFORE_SWAP, AFTER_SWAP

### OpenClawOracle
- **Address**: `0x300Fa0Af86201A410bEBD511Ca7FB81548a0f027`
- **Etherscan**: https://sepolia.etherscan.io/address/0x300Fa0Af86201A410bEBD511Ca7FB81548a0f027
- **Type**: Signal bridge (rebalance signals + fee recommendations)

### Uniswap v4 PoolManager (Sepolia)
- **Address**: `0xE03A1074c86CFeDd5C142C4F04F1a1536e203543`

### Test Tokens
- **GBB (currency0)**: `0x07B55AfA83169093276898f789A27a4e2d511F36` — has public `mint(address, uint256)`
- **GBA (currency1)**: `0xB960eD7FC078037608615a0b62a1a0295493f26E` — has public `mint(address, uint256)`

### Pool Configuration
- **Fee**: DYNAMIC_FEE_FLAG (`0x800000`)
- **Tick Spacing**: 60
- **Initial Price**: tick 0 (1:1 ratio)
- **sqrtPriceX96**: `79228162514264337593543950336`

## Key Function Signatures

### Hook (write)
- `addLiquidity(AddLiquidityParams)` — payable, adds position
- `removeLiquidity(RemoveLiquidityParams)` — removes position liquidity
- `rebalancePosition(uint256 positionId, int24 newTickLower, int24 newTickUpper)` — onlyOwner
- `placeLimitOrder(PoolKey, bool zeroForOne, int24 triggerTick, uint128 amountIn, uint128 amountOutMin, OrderType, uint256 linkedPositionId)` — returns orderId
- `cancelLimitOrder(uint256 orderId)` — returns escrowed tokens
- `claimFilledOrder(uint256 orderId)` — claims executed order output

### Hook (read)
- `getUserPositions(address)` → uint256[]
- `getPosition(uint256 positionId)` → Position struct
- `getPoolStats(bytes32 poolId)` → PoolStats struct
- `getUserLimitOrders(address)` → uint256[]
- `getLimitOrder(uint256 orderId)` → LimitOrder struct
- `poolKey()` → PoolKey struct
- `positionCounter()` / `orderCounter()` → uint256

### Oracle (write — bot only)
- `postRebalanceSignal(bytes32 poolId, RebalanceSignal)` — onlyBot
- `postFeeRecommendation(bytes32 poolId, FeeRecommendation)` — onlyBot

### Oracle (read)
- `getPositionsNeedingRebalance(bytes32 poolId)` → RebalanceSignal[]
- `getDynamicFee(bytes32 poolId)` → (uint24 fee, uint8 confidence)
- `getOptimalRange(bytes32 poolId, uint256 positionId)` → (int24, int24, uint8)
