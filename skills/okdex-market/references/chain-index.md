# 支持的区块链列表 (chainIndex)

## 主流区块链

| chainIndex | 区块链名称 | 原生代币 |
|------------|-----------|----------|
| 0 | Bitcoin | BTC |
| 1 | Ethereum | ETH |
| 10 | Optimism | ETH |
| 25 | Cronos | CRO |
| 56 | BNB Smart Chain (BSC) | BNB |
| 66 | OKX Chain (OKC) | OKT |
| 100 | Gnosis | xDAI |
| 128 | HECO | HT |
| 137 | Polygon | MATIC |
| 250 | Fantom | FTM |
| 288 | Boba Network | ETH |
| 321 | KCC | KCS |
| 324 | zkSync Era | ETH |
| 501 | Solana | SOL |
| 1030 | Conflux eSpace | CFX |
| 1088 | Metis | METIS |
| 1101 | Polygon zkEVM | ETH |
| 1284 | Moonbeam | GLMR |
| 1285 | Moonriver | MOVR |
| 2222 | Kava | KAVA |
| 5000 | Mantle | MNT |
| 8453 | Base | ETH |
| 42161 | Arbitrum One | ETH |
| 42220 | Celo | CELO |
| 43114 | Avalanche C-Chain | AVAX |
| 59144 | Linea | ETH |
| 81457 | Blast | ETH |
| 534352 | Scroll | ETH |
| 7565164 | Solana (SPL) | SOL |

## Bitcoin 生态

| chainIndex | 类型 | 说明 |
|------------|------|------|
| 0 | BTC 原生 | Bitcoin 原生代币 |
| 0 | BRC-20 | 格式: `btc-brc20-{ticker}` |
| 0 | ARC-20 | 格式: `btc-arc20-{inscriptionId}` |
| 0 | Runes | 格式: `btc-runesMain-{runeId}` |
| 0 | SRC-20 | Stamps 协议代币 |

## 代币地址格式

### EVM 链 (Ethereum, BSC, Polygon 等)
- 格式: `0x` + 40 位十六进制字符
- 示例: `0xdac17f958d2ee523a2206206994597c13d831ec7` (USDT)
- **注意**: 地址必须使用小写

### Solana
- 格式: Base58 编码的公钥
- 示例: `5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp`

### Bitcoin 铭文代币
- BRC-20: `btc-brc20-ordi`
- ARC-20: `btc-arc20-00009b954c9f1358de9c089f95ec420132e4106a89c8fbb3cfda198ae1e5f9d5i0`
- Runes: `btc-runesMain-840000:2`

## 查询原生代币价格

要查询链的原生代币价格，将 `tokenContractAddress` 设为空字符串 `""`：

```json
{
  "chainIndex": "1",
  "tokenContractAddress": ""  // 查询 ETH 价格
}
```

## 常用代币地址

### Ethereum (chainIndex: 1)
| 代币 | 地址 |
|------|------|
| USDT | 0xdac17f958d2ee523a2206206994597c13d831ec7 |
| USDC | 0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 |
| WETH | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 |
| WBTC | 0x2260fac5e5542a773aa44fbcfedf7c193bc2c599 |
| DAI | 0x6b175474e89094c44da98b954eedeac495271d0f |

### BSC (chainIndex: 56)
| 代币 | 地址 |
|------|------|
| USDT | 0x55d398326f99059ff775485246999027b3197955 |
| USDC | 0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d |
| WBNB | 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c |

### Solana (chainIndex: 501)
| 代币 | 地址 |
|------|------|
| USDC | EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v |
| USDT | Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB |
