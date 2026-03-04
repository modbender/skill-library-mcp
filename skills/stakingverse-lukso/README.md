# Stakingverse LUKSO Staking Skill

Stake LYX on Stakingverse and earn ~8% APY with liquid staking (sLYX).

## Installation

```bash
git clone https://github.com/LUKSOAgent/stakingverse-lukso-skill.git
cd stakingverse-lukso-skill
npm install ethers
```

## Configuration

Set environment variables:

```bash
export STAKING_PRIVATE_KEY="your_controller_private_key"
export MY_UP="your_universal_profile_address"
export CONTROLLER="your_controller_address"
```

## Usage

### Stake LYX

```bash
node scripts/stake.js 10  # Stake 10 LYX
```

Returns sLYX tokens immediately (1:1 ratio).

### Check Balance

```bash
node scripts/balance.js
```

Shows sLYX balance and underlying LYX value.

### Request Unstake

```bash
node scripts/unstake-request.js 5  # Request withdrawal of 5 sLYX
```

This burns sLYX and creates a withdrawal request.

### Claim LYX

```bash
node scripts/claim.js
```

Claims unstaked LYX after oracle processes the withdrawal.

## How It Works

**Staking:** Direct deposit via UP → KeyManager → Vault. Instant sLYX minting.

**Unstaking:** Two-step process
1. Request withdrawal (burns sLYX)
2. Oracle processes request (can take time)
3. Claim LYX

## Vault Details

- **Address:** `0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04`
- **Network:** LUKSO Mainnet
- **Token:** sLYX (LSP7)
- **APY:** ~8% (variable)

## Requirements

- Universal Profile on LUKSO
- Controller with staking permissions
- LYX for gas

## Credits

Created by [@LUKSOAgent](https://twitter.com/LUKSOAgent)
Stakingverse: https://app.stakingverse.io
