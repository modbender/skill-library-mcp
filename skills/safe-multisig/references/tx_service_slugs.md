# Safe Transaction Service — Chain Slugs

Use these slugs with `--chain <slug>` in all scripts.

The `--chain` parameter accepts human-readable names which are mapped internally
to the correct EIP-3770 short names used by the Safe Transaction Service API.

## Supported Chains

| --chain slug    | EIP-3770 | Chain ID | Network              |
|-----------------|----------|----------|----------------------|
| mainnet         | eth      | 1        | Ethereum Mainnet     |
| base            | base     | 8453     | Base                 |
| optimism        | oeth     | 10       | Optimism             |
| arbitrum        | arb1     | 42161    | Arbitrum One         |
| polygon         | matic    | 137      | Polygon              |
| gnosis          | gno      | 100      | Gnosis Chain         |
| bsc             | bnb      | 56       | BNB Smart Chain      |
| avalanche       | avax     | 43114    | Avalanche C-Chain    |
| sepolia         | sep      | 11155111 | Sepolia Testnet      |
| base-sepolia    | basesep  | 84532    | Base Sepolia Testnet |

## URL Format

The transaction service URL is constructed as:
```
https://safe-transaction-{eip3770_short_name}.safe.global/api/
```

Example for Base:
```
https://safe-transaction-base.safe.global/api/v1/about/
```

## Aliases

Some chains support multiple slug names:
- `ethereum` → same as `mainnet`
- `op-mainnet` → same as `optimism`
- `arbitrum-one` → same as `arbitrum`
