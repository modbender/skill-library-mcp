# Wallet Management

All wallet commands run from the `jinn-node/` directory. Most require `OPERATE_PASSWORD` and `RPC_URL` in `.env`.

## Check Status

```bash
yarn wallet:info
```

Shows wallet addresses, ETH/OLAS balances, and staking status. No flags — uses `.env` values.

## Backup

```bash
yarn wallet:backup
yarn wallet:backup --output my-backup.tar.gz
```

Creates a timestamped `.tar.gz` of the `.operate` directory. Does not require `OPERATE_PASSWORD`.

## Export Keys

```bash
yarn wallet:export-keys
```

Displays the BIP-39 mnemonic for the master wallet. **Ask the user to confirm before running** — this shows sensitive key material.

## Withdraw Funds

Preview first, then execute:
```bash
yarn wallet:withdraw --to <address> --dry-run
yarn wallet:withdraw --to <address>
```

| Flag | Default | Description |
|------|---------|-------------|
| `--to` | (required) | Destination address |
| `--asset` | `all` | `ETH`, `OLAS`, or `all` |
| `--dry-run` | off | Preview without executing |

Keeps 0.001 ETH in the Safe for future gas.

## Unstake

```bash
yarn wallet:unstake --dry-run
yarn wallet:unstake
```

| Flag | Default | Description |
|------|---------|-------------|
| `--service-id` | (from config) | Service ID to unstake |
| `--dry-run` | off | Preview without executing |

**72-hour staking cooldown**: OLAS requires minimum 72 hours staked before unstake is allowed. Will fail if cooldown has not elapsed.

## Emergency Recovery

Terminates the service and withdraws all funds. **Always preview first.**

```bash
yarn wallet:recover --to <address> --dry-run
yarn wallet:recover --to <address>
```

| Flag | Default | Description |
|------|---------|-------------|
| `--to` | (required) | Destination address for all funds |
| `--dry-run` | off | Preview without executing |
| `--skip-terminate` | off | Skip termination (if already unstaked) |

**WARNING**: Recovery terminates the service. You must re-run `yarn setup` to re-stake.
