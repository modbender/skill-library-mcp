# Garden Temp Market (GTM) 🌡️

A daily over/under prediction market for garden temperature, built for Netclawd's SensorNet on Base.

**"Will today's 18:00 UTC temperature be HIGHER than yesterday's?"**

## Overview

- **Betting**: Users bet ETH on HIGHER or LOWER
- **Settlement**: Daily at 18:00 UTC based on SensorNet readings
- **Payouts**: Winners split 98% of pot (2% house fee on new bets only)
- **Ties**: Pot rolls over to next day
- **One-sided markets**: Everyone gets refunded

Built by **potdealer x Ollie** for **Netclawd's SensorNet**

## Trust Model ⚠️

This contract uses a **TRUSTED KEEPER** model. The keeper (Ollie/Bankr wallet) reads temperature data from Net Protocol off-chain and submits it to the contract.

The keeper has full authority to determine the temperature value. Users must trust the keeper to submit accurate readings.

Why? SensorNet stores readings as Net Protocol messages, not direct contract storage. There's no on-chain `getTemperature()` to call.

## Contract Addresses

| Contract | Address |
|----------|---------|
| DailyTempMarket | `0xA3F09E6792351e95d1fd9d966447504B5668daF6` |
| SensorNet | `0xf873D168e2cD9bAC70140eDD6Cae704Ed05AdEe0` |
| Keeper (Ollie) | `0x750b7133318c7d24afaae36eadc27f6d6a2cc60d` |
| Treasury | `0x750b7133318c7d24afaae36eadc27f6d6a2cc60d` |

## Deployment

### Prerequisites

1. Install [Foundry](https://book.getfoundry.sh/getting-started/installation)
2. Copy `.env.example` to `.env` and fill in:
   - `PRIVATE_KEY` - Deployer wallet private key
   - `BASESCAN_API_KEY` - For contract verification

### Deploy to Base Mainnet

```bash
# Load environment variables
source .env

# Deploy and verify
forge script script/Deploy.s.sol:DeployDailyTempMarket \
  --rpc-url base \
  --broadcast \
  --verify
```

### Update Initial Temperature

Before deploying, update `INITIAL_TEMP` in `script/Deploy.s.sol` to the latest SensorNet reading:

```solidity
int256 constant INITIAL_TEMP = 1210; // Update this!
```

Temperature format: 2 decimal places (e.g., 1210 = 12.10°C)

## How It Works

### Daily Cycle

```
00:00 UTC ─────────────────────────── 12:00 UTC ──────── 18:00 UTC
           Betting Window Open         Betting            Settlement
           (18 hours)                  Closes             Keeper calls
                                       (6h buffer)        settle(temp)
```

### Betting

```solidity
// Bet that today's temp will be HIGHER
market.betHigher{value: 0.01 ether}();

// Bet that today's temp will be LOWER or equal
market.betLower{value: 0.01 ether}();
```

Minimum bet: 0.001 ETH (configurable by owner)
Max bettors per side: 200 (gas protection)

### Settlement

At 18:00 UTC daily, the keeper:
1. Reads the latest temperature from Net Protocol (SensorNet)
2. Calls `settle(todayTemp)` on the contract
3. Winners receive proportional payouts

### Temperature Format

- `int256` with 2 decimal places
- Example: `1210` = 12.10°C
- Valid range: -50.00°C to 60.00°C (-5000 to 6000)

## Security

- ✅ ReentrancyGuard on settlement
- ✅ Max 200 bettors per side (gas DoS protection)
- ✅ House fee only on new bets (no double-fee on rollover)
- ✅ Temperature bounds checking
- ✅ Direct ETH transfers rejected
- ✅ Audited by ChatGPT and Grok (experimental audits)

## Testing

```bash
forge test
```

36 tests covering betting, settlement, payouts, edge cases, and security.

## License

MIT
