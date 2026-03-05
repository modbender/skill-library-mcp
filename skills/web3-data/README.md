# web3-data-skill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill for exploring Web3 on-chain data using [Chainbase](https://chainbase.com) APIs.

## Features

- **Token Holders** — Query top holders of any ERC20 token with balance and USD value
- **Address Labels** — Look up wallet address tags (exchange, KOL, contract deployer, etc.)
- **Token Data** — Price, metadata, transfer history
- **NFT Data** — Metadata, owners, floor price, trending collections, rarity
- **Wallet Analytics** — Balances, transaction history, DeFi portfolios, ENS domains
- **SQL Queries** — When fixed APIs don't cover your needs, write custom SQL to query any on-chain data

Supports Ethereum, BSC, Polygon, Arbitrum, Optimism, Base, Avalanche, zkSync, and more.

## Install

```bash
claude install-skill /path/to/web3-data-skill
```

Or install from GitHub:

```bash
claude install-skill https://github.com/lxcong/web3-data-skill
```

## Usage

Once installed, just ask Claude Code about any Web3 data in natural language:

```
> USDT 的 top holders 是谁？
> 查一下 vitalik 的地址标签
> ETH 上 USDC 最近 24 小时的转账记录
> 查询 Bored Ape 的地板价
> 用 SQL 查一下以太坊最近 10 个区块
```

## API Key

The skill uses Chainbase's `demo` API key by default. If you hit rate limits, register at [console.chainbase.com](https://console.chainbase.com) and set your key:

```bash
export CHAINBASE_API_KEY=your_api_key
```

## Structure

```
├── SKILL.md                    # Skill definition and routing logic
├── scripts/
│   └── chainbase.sh            # API wrapper script (auto-handles SQL async polling)
└── references/
    └── api-endpoints.md        # Complete API endpoint reference (38 endpoints)
```

## License

MIT
