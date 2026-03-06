# StakeWise Ethereum Staking Skill

Stake ETH on StakeWise V3 and receive osETH (liquid staking token).

## Installation

```bash
git clone https://github.com/LUKSOAgent/stakingverse-ethereum-skill.git
cd stakingverse-ethereum-skill
npm install ethers
```

## Configuration

Set environment variables:

```bash
export ETH_PRIVATE_KEY="your_private_key"
export MY_ADDRESS="your_address"
```

## Usage

### Stake ETH

```bash
node scripts/stake.mjs 0.1  # Stake 0.1 ETH
```

**Note:** StakeWise V3 requires state updates via keeper. This script automatically queries the subgraph for harvest params and calls `updateStateAndDeposit()`.

### Check Position

```bash
node scripts/position.js
```

Shows osETH shares and underlying ETH value.

### Check Vault State

```bash
node scripts/check-state.js
```

Check if state update is required before deposits.

## How It Works

StakeWise V3 uses a keeper pattern:

1. Keeper periodically updates vault state with rewards data
2. Subgraph stores harvest params (rewardsRoot, proof, etc.)
3. Depositors must include valid harvest params
4. Script auto-fetches params from subgraph

**Subgraph:** `https://graphs.stakewise.io/mainnet-a/subgraphs/name/stakewise/prod`

## Vault Details

- **Address:** `0x8A93A876912c9F03F88Bc9114847cf5b63c89f56`
- **Network:** Ethereum Mainnet
- **Token:** osETH
- **Keeper:** `0x6B5815467da09DaA7DC83Db21c9239d98Bb487b5`

## Requirements

- Ethereum wallet with ETH
- ~0.05 ETH minimum recommended

## Credits

Created by [@LUKSOAgent](https://twitter.com/LUKSOAgent)
StakeWise: https://app.stakewise.io
