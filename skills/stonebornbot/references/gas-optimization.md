# Gas Optimization Guide

## EIP-1559 Gas Settings

```json
"gas": {
  "maxFeePerGas": "0.5",          // Max total fee in gwei
  "maxPriorityFeePerGas": "0.05", // Tip to miners/validators in gwei
  "gasLimit": 60000                // Gas units. Increase for complex mints.
}
```

### Setting Gas for Different Scenarios

| Scenario | maxFee | priority | Notes |
|----------|--------|----------|-------|
| Low competition | 0.3-1 | 0.01-0.1 | Free mints, quiet period |
| Medium competition | 1-5 | 0.1-1 | Popular mint, moderate demand |
| High competition | 5-50 | 1-10 | Hyped mint, many bots |
| War mode | 50-150 | 10-30 | Extreme competition |

### Gas Limit by Contract Type

- Simple ERC721: 50,000-80,000
- ERC721A (batch): 60,000-120,000
- Archetype mints: 80,000-150,000
- Complex logic: 150,000-300,000

**Tip**: Use Etherscan's gas tracker or check recent similar mints for guidance.

## War Mode

```json
"warMode": {
  "enabled": true,
  "autoAdjust": true,
  "maxFeeCapGwei": "5",
  "maxPriorityCapGwei": "2",
  "triggerCondition": "gasAboveMax"
}
```

When enabled and `autoAdjust` is true:
1. Bot checks current network gas before sending
2. If gas exceeds your `maxFeePerGas`, it escalates up to the cap values
3. Keeps you competitive without setting a static high gas price

**triggerCondition**: `"gasAboveMax"` — escalate only when base fee exceeds your maxFee setting.
