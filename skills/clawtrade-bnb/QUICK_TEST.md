# Quick Test Guide

## Verify Integration in 30 Seconds

```bash
cd /home/ubuntu/.openclaw/workspace/skills/yield-farming-agent
node test.live.mock.js
```

Expected output:
```
✓ [PASS] Configuration Validation
✓ [PASS] Mock Vault Data
✓ [PASS] Agent Decision
✓ [PASS] Hash Verification
✓ [PASS] Event ABI Validation
✓ [PASS] Risk Filter

Status: ✓ ALL TESTS PASSED
```

## What Was Integrated

| Component | File | Status |
|-----------|------|--------|
| Blockchain Reader | `blockchain-reader.js` | ✓ New |
| Config with ABIs | `config.deployed.json` | ✓ New |
| Mock Tests | `test.live.mock.js` | ✓ New + PASSING |
| Live Tests | `test.live.js` | ✓ New |
| Execution Guide | `LIVE_EXECUTION_GUIDE.md` | ✓ New |
| Integration Report | `INTEGRATION_MANIFEST.md` | ✓ New |
| Dependencies | `ethers@5.8.0` | ✓ Installed |

## Contract Addresses Integrated

```javascript
{
  "vault_eth_staking_001": "0x588eD88A145144F1E368D624EeFC336577a4276b",
  "vault_high_risk_001": "0x6E05a63550200e20c9C4F112E337913c32FEBdf0",
  "vault_link_oracle_001": "0x0C035842471340599966AA5A3573AC7dB34D14E4"
}
```

## Use in Code

```javascript
const BlockchainReader = require('./blockchain-reader');
const YieldFarmingAgent = require('./index');
const config = require('./config.deployed.json');

// Connect to contracts
const reader = new BlockchainReader(config.rpc);
await reader.initializeContracts(
  config.contracts.map(c => ({ ...c, abi: config.abi }))
);

// Read vault data
const vaults = await reader.getAllVaultsData(userAddress);

// Run agent
const agent = new YieldFarmingAgent(config);
const execution = agent.decide(vaults, currentAllocation);

// Verify
const valid = agent.verifyRecord(execution).valid;
```

## Next Steps

1. **Transaction Executor** - Execute actual contract calls
2. **Scheduler** - Run agent autonomously
3. **Notifications** - Alert via Telegram/Discord

See `LIVE_EXECUTION_GUIDE.md` for full details.
