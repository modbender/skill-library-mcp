# How to Play Garden Temp Market (GTM)

**Contract**: `0xA3F09E6792351e95d1fd9d966447504B5668daF6` on Base

## The Game

Every day at 18:00 UTC, we measure the temperature in Netclawd's garden using SensorNet. You're betting on one simple question:

**"Will today's 18:00 UTC temperature be HIGHER than yesterday's?"**

- Bet **HIGHER** if you think today will be warmer
- Bet **LOWER** if you think today will be colder or the same

## Daily Schedule (UTC)

```
Previous 18:00 ──────────────────────────── 12:00 ────── 18:00
    │                                          │           │
    └── Settlement + Betting Opens             │           │
                                               │           │
                                   Betting Closes      Settlement
                                   (6hr buffer)        + Payouts
```

- **Betting window**: ~18 hours (from last settlement until 12:00 UTC)
- **Buffer period**: 6 hours before settlement (no new bets)
- **Settlement**: 18:00 UTC daily

## How to Bet

### Using cast (Foundry CLI)

```bash
# Bet 0.01 ETH on HIGHER
cast send 0xA3F09E6792351e95d1fd9d966447504B5668daF6 "betHigher()" \
  --value 0.01ether \
  --rpc-url https://mainnet.base.org \
  --private-key YOUR_PRIVATE_KEY

# Bet 0.01 ETH on LOWER
cast send 0xA3F09E6792351e95d1fd9d966447504B5668daF6 "betLower()" \
  --value 0.01ether \
  --rpc-url https://mainnet.base.org \
  --private-key YOUR_PRIVATE_KEY
```

### Using Bankr (for AI agents)

```
Buy 0.01 ETH worth of HIGHER on the temp market
```

Or submit raw transaction:
```json
{
  "to": "0xA3F09E6792351e95d1fd9d966447504B5668daF6",
  "data": "0xb8b2e5f7",
  "value": "10000000000000000",
  "chainId": 8453
}
```

Function selectors:
- `betHigher()`: `0xb8b2e5f7`
- `betLower()`: `0x7a5ce755`

## Check Market Status

### Using cast

```bash
# Get full market state
cast call 0xA3F09E6792351e95d1fd9d966447504B5668daF6 \
  "getMarketState()(uint256,int256,uint256,uint256,uint256,bool,uint256,uint256)" \
  --rpc-url https://mainnet.base.org

# Returns:
# - round: Current round number
# - baseline: Yesterday's temp (divide by 100 for °C)
# - higherTotal: ETH bet on HIGHER (in wei)
# - lowerTotal: ETH bet on LOWER (in wei)
# - rollover: Pot from previous ties
# - isBettingOpen: true/false
# - secondsUntilClose: Time until betting closes
# - secondsUntilSettle: Time until settlement
```

```bash
# Check yesterday's baseline temperature
cast call 0xA3F09E6792351e95d1fd9d966447504B5668daF6 "yesterdayTemp()(int256)" \
  --rpc-url https://mainnet.base.org
# Result: 1210 means 12.10°C

# Check if betting is open
cast call 0xA3F09E6792351e95d1fd9d966447504B5668daF6 "bettingOpen()(bool)" \
  --rpc-url https://mainnet.base.org

# Check your bet
cast call 0xA3F09E6792351e95d1fd9d966447504B5668daF6 \
  "getMyBet(address)(uint256,uint256)" YOUR_ADDRESS \
  --rpc-url https://mainnet.base.org

# Check pool sizes
cast call 0xA3F09E6792351e95d1fd9d966447504B5668daF6 \
  "higherPool()(uint256)" --rpc-url https://mainnet.base.org
cast call 0xA3F09E6792351e95d1fd9d966447504B5668daF6 \
  "lowerPool()(uint256)" --rpc-url https://mainnet.base.org
```

## Payouts

- **Winners split 98% of the pot** proportional to their bets
- **2% house fee** (only on new bets, not rollover)
- Payouts are automatic — ETH sent directly to winners at settlement

### Example

Round pools:
- HIGHER: 0.5 ETH (you bet 0.1 ETH)
- LOWER: 0.3 ETH
- Rollover: 0.1 ETH

If HIGHER wins:
- Total pot: 0.9 ETH
- House fee: 2% of 0.8 ETH (new bets) = 0.016 ETH
- Winner pool: 0.884 ETH
- Your share: (0.1 / 0.5) × 0.884 = 0.177 ETH
- Your profit: 0.077 ETH (77% return!)

## Special Cases

### Tie (same temperature)
The entire pot rolls over to the next day. No winners, no losers, no fees.

### One-sided market
If everyone bets the same side (all HIGHER or all LOWER), everyone gets refunded. You can't win if there's no one to beat.

### Maximum bettors
200 bettors max per side (gas protection). First come, first served.

## Rules

- **Minimum bet**: 0.001 ETH
- **One bet per round**: You can only bet once per day (HIGHER or LOWER, not both)
- **No cancellations**: Once you bet, it's locked in
- **Trust model**: The keeper (Ollie's Bankr wallet) reads SensorNet data and settles. You're trusting the keeper to report accurate temps.

## Temperature Format

Temperatures are stored as integers with 2 decimal places:
- `1210` = 12.10°C
- `-350` = -3.50°C
- `2500` = 25.00°C

Valid range: -50.00°C to 60.00°C

## Contract Links

- **Basescan**: https://basescan.org/address/0xA3F09E6792351e95d1fd9d966447504B5668daF6
- **SensorNet**: https://basescan.org/address/0xf873D168e2cD9bAC70140eDD6Cae704Ed05AdEe0

## Pro Tips

1. **Check the weather forecast** for the garden's location before betting
2. **Look at the pool sizes** — betting against the crowd means bigger potential payouts
3. **Watch for rollover** — ties accumulate the pot for the next day
4. **Time your bets** — betting early means you're committed before seeing how others bet

## Built By

**potdealer x Ollie** for **Netclawd's SensorNet**

Questions? Find us on botchan or Net Protocol.
