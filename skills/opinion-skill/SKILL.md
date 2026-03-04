# Opinion CLOB Skills

基于 bun 运行时的 Opinion 预测市场交易工具集。

## 仓库源

https://github.com/Yuandiaodiaodiao/opinion-skill

如果本地没有 scripts 目录，先克隆仓库：
```bash
git clone https://github.com/Yuandiaodiaodiao/opinion-skill.git /root/opinionskills
```

## 环境检查

```bash
ls /root/opinionskills/scripts/config.ts 2>/dev/null && echo "scripts ready" || { echo "scripts missing, cloning..."; git clone https://github.com/Yuandiaodiaodiao/opinion-skill.git /root/opinionskills; }
```

> 所有命令均需在 `/root/opinionskills/` 目录下执行。bun 可直接执行 .ts 文件，无需 bun install。

## 前置条件

1. 安装 bun:
   ```bash
   command -v bun >/dev/null 2>&1 && echo "bun $(bun --version)" || { curl -fsSL https://bun.sh/install | bash && source ~/.bashrc; }
   ```
2. 创建 `.env` 文件:
   ```
   PRIVATE_KEY=0x_your_eoa_private_key
   MULTI_SIG_ADDRESS=0x_your_opinion_builtin_wallet_address
   API_KEY=your_opinion_api_key
   ```

## 网站前置步骤

1. 前往 Opinion 平台注册账户
2. 平台会自动创建内置钱包 (Gnosis Safe 多签钱包, BSC 链)
3. Enable Trading (链上授权, 需要 BNB gas)
4. 充值 USDT 到内置钱包

## 入门流程

1. 填写 `.env`
2. `bun run scripts/enable-trading.ts` — 一次性链上授权
3. `bun run scripts/balances.ts` — 确认余额
4. 开始交易

## 数据来源说明

- **数据查询** (市场/价格/订单簿/持仓等): 使用 API `http://newopinion.predictscanapi.xyz:10001`
- **交易操作** (下单/取消/余额): 使用 `@opinion-labs/opinion-clob-sdk`
- **tokenId = assetId**: 两者是同一概念，可互换使用

## 环境变量与权限分级

数据查询脚本（search、markets、market-detail、price、orderbook、positions、trades、top-markets）**不需要任何环境变量，也不需要 bun install**，克隆仓库后即可直接运行。

交易操作脚本（buy、sell、cancel、orders、balances、enable-trading）**必须先 `bun install` 安装 SDK 依赖，并配置 `.env`**。如果用户尝试执行交易操作但未配置环境变量，脚本会报错提示缺少 PRIVATE_KEY / MULTI_SIG_ADDRESS / API_KEY。

执行交易操作前，先确认 `.env` 是否已配置：
```bash
test -f /root/opinionskills/.env && grep -q "PRIVATE_KEY=0x" /root/opinionskills/.env && echo "Trading credentials configured" || echo "WARNING: .env not configured — only market data queries are available. To trade, create /root/opinionskills/.env with PRIVATE_KEY, MULTI_SIG_ADDRESS, and API_KEY."
```

如果用户要求下单但 `.env` 未配置，不要执行交易脚本，而是提示用户先配置环境变量。

## 命令速查

```bash
# 数据查询 (API)
bun run scripts/search.ts <keyword> [--limit <n>]                                    # 搜索市场
bun run scripts/markets.ts [--limit <n>] [--offset <n>] [--json]                     # 浏览市场/事件列表
bun run scripts/market-detail.ts <marketId> [--json]                                 # 市场详情
bun run scripts/price.ts <assetId> [<assetId2> ...] [--json]                         # 查询价格
bun run scripts/orderbook.ts <assetId> [--json]                                      # 查看订单簿
bun run scripts/positions.ts <address> [--limit <n>] [--json]                        # 查看持仓
bun run scripts/trades.ts <assetId> [--limit <n>] [--filter all|taker|maker] [--json] # 成交记录
bun run scripts/top-markets.ts [--tag volume|txn] [--window 1h|4h|24h] [--json]      # 热门市场

# 交易操作 (SDK)
bun run scripts/enable-trading.ts                                                     # 启用交易 (一次性)
bun run scripts/balances.ts [--json]                                                  # 查看余额
bun run scripts/buy.ts --market <ID> --token <TOKEN_ID> --price <P> --amount <AMT> [--type market|limit]
bun run scripts/sell.ts --market <ID> --token <TOKEN_ID> --price <P> --shares <N> [--type market|limit]
bun run scripts/orders.ts [--market <ID>] [--status open] [--json]                   # 查看订单
bun run scripts/cancel.ts --order <ORDER_ID>                                          # 取消单个订单
bun run scripts/cancel.ts --all [--market <MARKET_ID>]                                # 取消全部订单
```

## 脚本用法详解

### 1. 搜索市场 — `search.ts <keyword> [--limit <n>]`

搜索 Opinion 市场，返回匹配的市场列表及其 tokenId。

| 参数 | 说明 |
|------|------|
| `<keyword>` | 搜索关键词 (必填) |
| `--limit <n>` | 返回数量 (默认 10) |

输出: 市场标题、marketId、yesTokenId、noTokenId、所属 Event。

### 2. 浏览市场 — `markets.ts [options]`

浏览所有市场和事件 (WrapEvent 统一格式)。

| 参数 | 说明 |
|------|------|
| `--limit <n>` | 返回数量 (默认 20, 最大 1000) |
| `--offset <n>` | 跳过前 n 条 (分页) |
| `--json` | 输出原始 JSON |

### 3. 市场详情 — `market-detail.ts <marketId> [--json]`

获取单个市场的完整信息，包括 tokenId、状态、规则、子市场等。

### 4. 查询价格 — `price.ts <assetId> [<assetId2> ...] [--json]`

单个 assetId 返回 lastPrice/bestBid/bestAsk/mid (从 orderbook 计算)。
多个 assetId 使用 batchprice 接口，返回 price 和 source。

### 5. 查看订单簿 — `orderbook.ts <assetId> [--json]`

获取完整 bids + asks，计算 spread 和中间价。显示前 10 档。

### 6. 查看持仓 — `positions.ts <address> [--limit <n>] [--json]`

查询指定地址的持仓。自动批量查询市场信息，显示 YES/NO 方向。
`<address>` 为 maker 地址 (内置钱包地址)。

### 7. 成交记录 — `trades.ts <assetId> [--limit <n>] [--filter all|taker|maker] [--json]`

按 assetId 查询成交记录 (taker 交易)。

| 参数 | 说明 |
|------|------|
| `<assetId>` | Asset/Token ID (必填) |
| `--limit <n>` | 返回数量 (默认 100, 最大 1000) |
| `--filter all\|taker\|maker` | 筛选类型 (默认 taker) |
| `--json` | 输出原始 JSON |

### 8. 热门市场 — `top-markets.ts [options]`

| 参数 | 说明 |
|------|------|
| `--tag volume\|txn` | 排序方式 (默认 volume) |
| `--window 1h\|4h\|24h` | 时间窗口 (默认 24h) |
| `--json` | 输出原始 JSON |

### 9. 启用交易 — `enable-trading.ts`

一次性链上授权操作。批准 ERC20 代币用于 CTF Exchange 和 ConditionalTokens 合约。
需要 BNB gas。执行一次即可，SDK 内部有缓存 (默认 3600s)。

### 10. 查看余额 — `balances.ts [--json]`

通过 SDK 查询内置钱包余额。

### 11. 买入 — `buy.ts`

| 参数 | 说明 |
|------|------|
| `--market <ID>` | 市场 ID (必填) |
| `--token <TOKEN_ID>` | tokenId/assetId (必填) |
| `--price <P>` | 价格 0-1 (限价单必填, 市价单设 0) |
| `--amount <AMT>` | USDT 金额 (必填) |
| `--type market\|limit` | 订单类型 (默认 limit) |

示例:
- 限价买入: `bun run scripts/buy.ts --market 123 --token 0xabc... --price 0.45 --amount 10`
- 市价买入: `bun run scripts/buy.ts --market 123 --token 0xabc... --price 0 --amount 10 --type market`

### 12. 卖出 — `sell.ts`

| 参数 | 说明 |
|------|------|
| `--market <ID>` | 市场 ID (必填) |
| `--token <TOKEN_ID>` | tokenId/assetId (必填) |
| `--price <P>` | 价格 0-1 (限价单必填, 市价单设 0) |
| `--shares <N>` | 卖出的 token 数量 (必填) |
| `--type market\|limit` | 订单类型 (默认 limit) |

### 13. 查看订单 — `orders.ts [options]`

| 参数 | 说明 |
|------|------|
| `--market <ID>` | 按市场过滤 |
| `--status open` | 仅显示活跃订单 |
| `--json` | 输出原始 JSON |

### 14. 取消订单 — `cancel.ts`

- `--order <ORDER_ID>` — 取消单个订单
- `--all [--market <MARKET_ID>]` — 取消全部 (可按市场过滤)

## 常用工作流

### 查找市场并下单

1. `bun run scripts/search.ts bitcoin` — 搜索市场
2. 记下 marketId 和 yesTokenId/noTokenId
3. `bun run scripts/orderbook.ts <tokenId>` — 查看盘口
4. `bun run scripts/buy.ts --market <ID> --token <tokenId> --price 0.45 --amount 10` — 下单

### 查看持仓和管理订单

1. `bun run scripts/positions.ts <address>` — 查看持仓
2. `bun run scripts/orders.ts --status open` — 查看活跃订单
3. `bun run scripts/cancel.ts --order <ID>` — 取消订单

## 订单类型

| 类型 | 说明 |
|------|------|
| LIMIT (默认) | 限价单, 挂单等待成交。price 为 0-1 之间的值 |
| MARKET | 市价单, 立即成交。price 设为 "0" |

## 价格说明

- 价格范围: 0 到 1 (exclusive), 如 0.5 = 50 cents
- 买入 (BUY): 用 USDT 购买 outcome token, 提供 `makerAmountInQuoteToken` (USDT 金额)
- 卖出 (SELL): 卖出 outcome token 换 USDT, 提供 `makerAmountInBaseToken` (token 数量)

## 市场结构

- **Binary Market**: 有 yesTokenId 和 noTokenId, 二选一
- **Categorical Market**: 有 childMarkets 数组, 每个子市场有自己的 yesTokenId/noTokenId
- **statusEnum**: "Activated" = 活跃可交易, "Resolved" = 已结算

## 链信息

- 主链: BSC (chainId 56)
- 需要 BNB 用于 gas (enableTrading, split, merge, redeem)
- 下单和取消订单不需要 gas (EIP-712 签名)

## 错误处理

SDK API 返回格式: `{ errno: number, errmsg: string, result: T }`
- `errno === 0` 表示成功
- 非零 errno 不会抛异常，需检查 errno 值

常见错误:
- `BalanceNotEnough` — 余额不足, 充值 USDT
- `InsufficientGasBalance` — BNB 不足, 充值 BNB
- `InvalidParamError` — 参数错误, 检查 marketId/tokenId/price
