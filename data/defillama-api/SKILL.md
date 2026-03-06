---
name: defillama-api
description: 使用 DefiLlama API/SDK 获取 TVL、stablecoins、coins 价格、yields、volumes、fees、perps、unlocks、bridges、ETFs、narratives、token liquidity、main page、DAT、meta 等数据的 CLI 技能；当需要用命令行调用 DefiLlama 数据时使用。
homepage: https://defillama.com/
metadata:
  {
    "openclaw":
      {
        "emoji": "🦙",
        "requires": { "bins": ["uv"], "env": [] },
        "optionalEnv": ["DEFILLAMA_API_KEY"],
        "install":
          [
            {
              "id": "uv-brew",
              "kind": "brew",
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
          ],
      },
  }
---

# DefiLlama API

只允许通过 `src/run.py` 调用，禁止直接运行 `src/scripts/` 下的脚本。

## 安装

```bash
cd {baseDir}
```

## 环境变量

- `DEFILLAMA_API_KEY`：可选，Pro API key。若未提供，Pro 端点会提示 `API PLAN REQUIRED`。

## 使用方式（必须通过 run.py）

### TVL

```bash
uv run {baseDir}/src/run.py tvl protocols
uv run {baseDir}/src/run.py tvl protocol --protocol aave
uv run {baseDir}/src/run.py tvl tvl --protocol uniswap
uv run {baseDir}/src/run.py tvl chains
uv run {baseDir}/src/run.py tvl historical-chain-tvl --chain Ethereum
```

### Stablecoins

```bash
uv run {baseDir}/src/run.py stablecoins list --include-prices
uv run {baseDir}/src/run.py stablecoins charts-all
uv run {baseDir}/src/run.py stablecoins charts-chain --chain Ethereum
uv run {baseDir}/src/run.py stablecoins detail --asset 1
uv run {baseDir}/src/run.py stablecoins dominance --chain Ethereum --stablecoin-id 1
```

### Coins（价格与链上数据）

```bash
uv run {baseDir}/src/run.py coins current --coins coingecko:ethereum,ethereum:0x0000000000000000000000000000000000000000
uv run {baseDir}/src/run.py coins historical --timestamp 1704067200 --coins coingecko:ethereum
uv run {baseDir}/src/run.py coins chart --coins coingecko:ethereum --period 7d
```

### Yields（Pro）

```bash
uv run {baseDir}/src/run.py yields pools
uv run {baseDir}/src/run.py yields pool-chart --pool <pool_id>
```

### Volumes

```bash
uv run {baseDir}/src/run.py volumes dex-overview
uv run {baseDir}/src/run.py volumes options-overview --data-type dailyPremiumVolume
```

### Fees

```bash
uv run {baseDir}/src/run.py fees overview
uv run {baseDir}/src/run.py fees summary --protocol uniswap
```

### Perps

```bash
uv run {baseDir}/src/run.py perps open-interest
uv run {baseDir}/src/run.py perps derivatives-overview
```

### Unlocks（Pro）

```bash
uv run {baseDir}/src/run.py unlocks all
uv run {baseDir}/src/run.py unlocks protocol --protocol hyperliquid
```

### Main Page（Pro）

```bash
uv run {baseDir}/src/run.py main-page categories
uv run {baseDir}/src/run.py main-page raises
```

### Token Liquidity（Pro）

```bash
uv run {baseDir}/src/run.py token-liquidity historical --token usdt
```

### ETFs（Pro）

```bash
uv run {baseDir}/src/run.py etfs overview
uv run {baseDir}/src/run.py etfs history
```

### Narratives（Pro）

```bash
uv run {baseDir}/src/run.py narratives fdv-performance --period 30
```

### Bridges（Pro）

```bash
uv run {baseDir}/src/run.py bridges list --include-chains
uv run {baseDir}/src/run.py bridges transactions --id 1 --limit 50
```

### Meta / DAT（Pro）

```bash
uv run {baseDir}/src/run.py meta usage
uv run {baseDir}/src/run.py dat institutions
```

## 备注

- Coin 需要使用 `chain:address` 或 `coingecko:slug` 格式，例如 `coingecko:ethereum`。
- Pro 端点需要 `DEFILLAMA_API_KEY` 或 `--api-key`。

## 常见错误

- `rate limited`：放缓速率或提供 API plan key。
- `API PLAN REQUIRED`：升级订阅或设置 `DEFILLAMA_API_KEY`。
