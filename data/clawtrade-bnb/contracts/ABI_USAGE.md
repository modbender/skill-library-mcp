# YieldVault ABI Usage

## Import ABI

### JavaScript
```javascript
const YieldVaultABI = require('./abi/YieldVault.json');
// or
const { YieldVaultABI } = require('./abi/YieldVault.js');
```

### TypeScript
```typescript
import YieldVaultABI from './abi/YieldVault.json';
```

## Contract Events

### ExecutionRecorded
Emitted on every action (deposit, withdraw, harvest, compound)
```solidity
event ExecutionRecorded(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 amount,
    uint256 shares,
    uint256 timestamp
);
```

### ActionExecuted
Emitted with success/failure status
```solidity
event ActionExecuted(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 indexed amount,
    bool success,
    string message
);
```

## Contract Functions

| Function | Input | Output | Action |
|----------|-------|--------|--------|
| deposit() | uint256 amount | uint256 shares | Deposit tokens and receive shares |
| withdraw() | uint256 shares | uint256 amount | Burn shares and receive tokens |
| harvest() | - | uint256 yield | Claim yield without reinvesting |
| compound() | - | uint256 newShares | Reinvest yield as new shares |
| getShareBalance() | address user | uint256 | Get user's share balance |
| getTotalAssets() | - | uint256 | Get total vault assets |
| getTotalShares() | - | uint256 | Get total shares issued |
| getVaultInfo() | - | (id, token, assets, shares) | Get vault metadata (compatible with mockdata.json) |

## Agent Integration

Use events to track vault activity:

```javascript
contract.on('ExecutionRecorded', (vaultId, action, user, amount, shares) => {
  console.log(`[${vaultId}] ${action} by ${user}: ${amount} amount, ${shares} shares`);
});

contract.on('ActionExecuted', (vaultId, action, user, amount, success, message) => {
  console.log(`Action ${action} - Success: ${success}, Message: ${message}`);
});
```

## Data Compatibility

The contract is compatible with mockdata.json structure:

```json
{
  "vault_id": "vault_bnb_lp_001",
  "token": "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312",
  "shares": 1000000000000000000,
  "amount": 500000000000000000
}
```

Generated: $(date)
