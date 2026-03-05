---
name: clankerkit
description: Autonomous wallet operations for AI agents on Monad — swap, stake, deploy wallets, trade memecoins, and manage spending policies via natural language.
license: MIT
metadata:
  openclaw:
    requires:
      env:
        - AGENT_WALLET_ADDRESS
        - POLICY_ENGINE_ADDRESS
        - AGENT_PRIVATE_KEY
        - OWNER_ADDRESS
      primaryEnv: AGENT_PRIVATE_KEY
---

# ClankerKit - Autonomous Wallet for AI Agents on Monad

ClankerKit gives your AI agent autonomous financial capabilities on Monad blockchain. Deploy a smart contract wallet, set spending policies, swap tokens via Kuru DEX, stake MON, trade memecoins with strategies, and execute cross-chain swaps.

## Quick Start

```bash
# Install the skill
claw skill install clankerkit
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AGENT_WALLET_ADDRESS` | Yes | Deployed AgentWallet contract address |
| `POLICY_ENGINE_ADDRESS` | Yes | Deployed PolicyEngine contract address |
| `AGENT_PRIVATE_KEY` | Yes | Agent's private key (with 0x prefix) |
| `OWNER_ADDRESS` | Yes | Human owner address |
| `MONAD_RPC_URL` | No | Monad RPC URL (default: testnet) |
| `MONAD_NETWORK` | No | `testnet` or `mainnet` (default: testnet) |
| `ZEROX_API_KEY` | No | 0x Swap API key (only for `zerox_swap`) |

## Tools (32 total)

### Wallet Management

#### `get_wallet_info`
Get wallet address, owner, agent, MON balance, and policy state.

#### `get_token_balance`
Get ERC-20 token balance of the agent wallet.
- **token**: Token symbol (WMON, USDC, CHOG, DAK, YAKI) or contract address

#### `send_tokens`
Send native MON tokens from the wallet.
- **to**: Recipient address
- **amount**: Amount in human-readable form (e.g. "0.5")

#### `send_token`
Send ERC-20 tokens from the wallet.
- **token**: Token contract address
- **to**: Recipient address
- **amount**: Amount in human-readable form

#### `execute_transaction`
Execute an arbitrary contract call via the wallet.
- **target**: Target contract address
- **value**: Native MON to send (wei, default "0")
- **data**: Encoded calldata (hex)

#### `ensure_gas`
Ensure the agent EOA has enough MON for gas fees. If the EOA balance is below the minimum threshold, automatically sends MON from the AgentWallet contract to the EOA. Users only need to fund the wallet contract — the agent tops up its own gas from there.
- **minBalance**: Minimum acceptable EOA balance in MON (human-readable, default "0.01")
- **topUpAmount**: Amount of MON to send to EOA if below minimum (human-readable, default "0.05")

### Policy & Security

#### `get_policy`
View current spending limits (daily/weekly), usage, and allowlists.

#### `create_policy`
Create a spending policy. Must be called once before guarded transactions work.
- **dailyLimit**: Max MON per day (human-readable, e.g. "1.0")
- **weeklyLimit**: Max MON per week (defaults to 7x daily)
- **allowedTokens**: Optional ERC-20 address allowlist
- **allowedContracts**: Optional contract address allowlist
- **requireApprovalAbove**: MON threshold for owner approval

#### `update_daily_limit`
Update the daily spending limit.
- **newLimit**: New limit in human-readable MON

### Token Swaps (Kuru DEX)

#### `swap_tokens`
Swap tokens on Monad via Kuru Flow aggregator. Accepts symbols (MON, USDC, WMON, CHOG, DAK, AUSD, WETH, WBTC) or contract addresses.
- **tokenIn**: Source token (symbol or address)
- **tokenOut**: Destination token (symbol or address)
- **amount**: Human-readable amount (e.g. "0.01")
- **slippage**: Slippage in bps (default: 50 = 0.5%)

#### `get_swap_quote`
Get a swap quote without executing.
- **tokenIn**, **tokenOut**, **amount**: Same as `swap_tokens`

### Staking

#### `stake_mon`
Stake MON with a validator to earn rewards.
- **amount**: MON to stake (human-readable)
- **validatorId**: Validator ID (optional, uses default)

#### `unstake_mon`
Begin unstaking MON from a validator.
- **amount**: MON to unstake (human-readable)
- **validatorId**: Validator ID (optional)
- **withdrawId**: Withdrawal ID (default: 0)

#### `withdraw_stake`
Withdraw unstaked MON after the 1-epoch delay.
- **validatorId**, **withdrawId**: Optional

#### `claim_staking_rewards`
Claim accumulated staking rewards.
- **validatorId**: Optional

#### `compound_rewards`
Re-stake accumulated rewards.
- **validatorId**: Optional

#### `get_staking_info`
Get delegation info (staked amount, unclaimed rewards).
- **validatorId**: Optional

### Kuru CLOB Orderbook Trading

#### `get_kuru_markets`
List known Kuru CLOB orderbook markets on Monad mainnet.

#### `get_order_book`
Fetch live L2 order book (bids/asks) for a Kuru CLOB market.
- **marketAddress**: Orderbook contract address

#### `get_market_price`
Get best bid, ask, and mid price for a Kuru CLOB market.
- **marketAddress**: Orderbook contract address

#### `kuru_market_order`
Place a market (IOC) order on a Kuru CLOB market. Agent EOA must hold tokens.
- **marketAddress**: Orderbook contract address
- **amount**: Human-readable float
- **isBuy**: true for buy, false for sell
- **minAmountOut**: Minimum output (default: 0)
- **slippageBps**: Slippage in bps (default: 100)

#### `kuru_limit_order`
Place a limit (GTC) order on a Kuru CLOB market.
- **marketAddress**: Orderbook contract address
- **price**: Price in quote asset (float)
- **size**: Size in base asset (float)
- **isBuy**: true for bid, false for ask
- **postOnly**: Reject if it crosses spread (default: false)

#### `cancel_kuru_orders`
Cancel open orders on a Kuru CLOB market.
- **marketAddress**: Orderbook contract address
- **orderIds**: Array of order ID strings

### Memecoin Trading

#### `get_meme_tokens`
Get live price metrics for all known Monad memecoins (DAK, CHOG, YAKI). Uses CLOB orderbooks with Kuru Flow fallback.

#### `get_token_price`
Get live price for a specific token by symbol or contract address.
- **token**: Symbol (DAK, CHOG, YAKI) or contract address

#### `smart_trade`
Evaluate or execute an autonomous trading strategy.
- **token**: Token symbol
- **strategyType**: `dca`, `momentum`, `scalp`, or `hodl`
- **budgetMon**: Total budget in MON
- **stopLoss**: Stop-loss fraction (default: 0.1 = -10%)
- **takeProfit**: Take-profit fraction (default: 0.3 = +30%)
- **dcaIntervals**: Number of DCA buys (default: 5)
- **momentumThreshold**: Min 24h change for momentum (default: 0.05)
- **autoExecute**: Execute trades or dry-run (default: false)

### Cross-Chain Swaps

#### `kyber_swap`
Swap on Ethereum/Polygon/Arbitrum/Optimism/Base/BSC/Avalanche via KyberSwap. No API key needed. Uses agent EOA (not wallet contract).
- **chain**: Target chain name
- **tokenIn**, **tokenOut**: Token addresses on target chain
- **amountIn**: Amount in smallest unit (wei)
- **slippageBps**: Slippage (default: 50)
- **recipient**: Recipient address (default: agent EOA)

#### `zerox_swap`
Swap via 0x Swap API v2. Requires `ZEROX_API_KEY`.
- **chain**, **tokenIn**, **tokenOut**, **amountIn**, **slippageBps**: Same as `kyber_swap`

### Payments & Identity

#### `pay_for_service`
Pay for an x402-enabled API endpoint.
- **endpoint**: API endpoint URL
- **amount**: Payment in USDC

#### `register_agent`
Register on ERC-8004 identity registry.
- **name**: Agent name
- **description**: Agent description

### Deployment

#### `deploy_policy_engine`
Deploy a new PolicyEngine contract. The deployer becomes the owner. No parameters needed.

#### `deploy_agent_wallet`
Deploy a new AgentWallet contract. Optionally deploys PolicyEngine too.
- **owner**: Address that owns the wallet
- **agent**: Agent EOA address allowed to call execute()
- **policyEngine**: Optional existing PolicyEngine address

## Security Features

- **Spending Limits**: Daily and weekly caps on agent spending
- **Token Allowlists**: Restrict which tokens the agent can transfer
- **Contract Whitelists**: Only allow calls to approved contracts
- **Approval Thresholds**: Require human approval above certain amounts
- **Emergency Controls**: Owner can pause or withdraw funds anytime
- **Access Control**: PolicyEngine recordExecution() only callable by the wallet contract

## Example Session

```
User: Check my gas and fund up if needed

Agent: [calls ensure_gas]
EOA already has sufficient gas balance. EOA: 0.221 MON, Wallet: 0.075 MON.

User: Set a daily limit of 2 MON

Agent: [calls create_policy with dailyLimit="2.0"]
Policy created: 2 MON daily, 14 MON weekly.

User: Swap 0.1 MON for CHOG

Agent: [calls swap_tokens with tokenIn="MON", tokenOut="CHOG", amount="0.1"]
Swapped 0.1 MON -> 2.71 CHOG via Kuru Flow.

User: What's my portfolio?

Agent: [calls get_wallet_info, get_meme_tokens, get_staking_info]
Wallet: 1.9 MON
CHOG: 2.71 (worth ~0.1 MON)
Staked: 0.5 MON with validator #1
```

## License

MIT
