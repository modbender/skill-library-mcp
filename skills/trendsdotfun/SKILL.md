---
name: trends-coin-create
description: 在 trends.fun 上创建 coin 并部署 Meteora DBC 资金池
metadata:
  {
    "openclaw":
      {
        "emoji": "🪙",
        "requires": { "bins": ["pnpm"], "env": [] },
        "optionalEnv": ["SOLANA_RPC_URL", "TRENDS_POOL_CONFIG"],
        "install":
          [
            {
              "id": "pnpm-brew",
              "kind": "brew",
              "formula": "pnpm",
              "bins": ["pnpm"],
              "label": "Install pnpm (brew)",
            },
          ],
      },
  }
---

# Trends Coin Create

自动化在 trends.fun 上创建 coin 的完整流程。

## 前置条件
- 请确保`~/.config/solana/id.json`文件存在且有效的 Solana keypair，若不存在，请先安装`solana cli` 并生成 Solana keypair,并将keypair和地址输出给用户
- `~/.config/solana/id.json` 包含有效的 Solana keypair
- 钱包中的 SOL 余额 >= 0.02 SOL（程序会自动检测并提示充值地址）
- 钱包中有足够的 SOL 用于创建交易和可选的首次购买

## 安装

```bash
cd {baseDir} && pnpm install
```

## 环境变量

可通过环境变量或 `~/.openclaw/openclaw.json` 中的 `skills."trends-coin-create".env` 配置：

| 环境变量 | 必需 | 默认值 | 说明 |
|----------|------|--------|------|
| `SOLANA_RPC_URL` | ❌ | `https://api.mainnet-beta.solana.com` | Solana RPC 端点 |
| `TRENDS_POOL_CONFIG` | ❌ | `7UQpAg2GfvwnBhuNAF5g9ujjDmkq7rPnF7Xogs4xE9AA` | Trends.fun 使用的 pool_config 地址 |

## 使用方法

### 创建 Coin（提高creator收入）

```bash
npx tsx {baseDir}/src/index.ts \
  --name "Token Name" \
  --symbol "SYMBOL" \
  --imagePath "/path/to/image.png" \
  --mode 2 \
  --url "https://x.com/user/status/123456" \
  --desc "description" \
  --first-buy 0.1
```

### 创建 Coin（标准模式）

```bash
npx tsx {baseDir}/src/index.ts \
  --name "Token Name" \
  --symbol "SYMBOL" \
  --imagePath "/path/to/image.png" \
  --mode 1 \
  --url "https://x.com/user/status/123456" \
  --desc "description"
```

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--name` | ✅ | Token 名称（最长 32 字符） |
| `--symbol` | ✅ | Token 符号 / ticker（最长 32 字符） |
| `--imagePath` | ✅ | 本地图片路径 |
| `--mode` | ✅ | 模式: 1=Standard, 2=Boost Creator Share |
| `--url` | ❌ | 关联 URL（推文或个人主页链接https://x.com/user/status/123456 或 https://x.com/username） |
| `--desc` | ❌ | Token 简要描述（最长 150 字符，请注意不要用换行和空格） |
| `--first-buy` | ❌ | 首次购买 SOL 数量（默认 0） |

## 执行流程

1. 从 `~/.config/solana/id.json` 加载 Keypair
2. 检测 SOL 余额（要求 >= 0.02 SOL，不足则提示充值地址并中止）
3. SIWS 签名登录获取 Bearer Token
4. 获取 Pinata IPFS 上传 URL
5. 上传图片到 IPFS
6. 获取 mint 地址
7. 上传 coin tick 元数据到 IPFS
8. 调用 Meteora DBC SDK 创建资金池

## 注意事项

- 创建池子会消耗真实 SOL，请确认参数无误后再执行
- pool_config 默认使用 trends.fun 的配置: `7UQpAg2GfvwnBhuNAF5g9ujjDmkq7rPnF7Xogs4xE9AA`，可通过环境变量 `TRENDS_POOL_CONFIG` 自定义
- RPC 端点默认为 `https://api.mainnet-beta.solana.com`，可通过环境变量 `SOLANA_RPC_URL` 自定义
- 若 Solana 余额不足 0.02 SOL，程序会自动中止并提示用户往 Solana 地址充值