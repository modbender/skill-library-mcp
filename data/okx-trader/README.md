# OKX Trader Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-okx--trader-blue)](https://clawhub.ai/esojourn/okx-trader)

Professional automated grid trading system for OKX, designed for OpenClaw.

## Trading Logic

The bot implements a **Dynamic Symmetric Grid** strategy:

1.  **Maintenance:** Every 5 minutes, the bot compares current market price against planned grid levels. If a level is missing an order, it places a new limit order.
2.  **Rescale:** If the price moves beyond the `trailingPercent` threshold of the current range, the bot cancels all orders and re-centers the grid around the new price.
3.  **Profit Taking:** Sell orders are only placed if they meet the `minProfitGap` requirement relative to the average position cost (for Micro grid).

## Account Snapshots

`scripts/snapshot.js` records daily account state (balances, prices, 24h trading summary) and compares equity changes against the previous day. Data is saved to `okx_data/snapshots/YYYY-MM-DD.json`.

## Configuration

Files should be placed in `/root/.openclaw/workspace/okx_data/`:

### `config.json`
```json
{
  "apiKey": "YOUR_API_KEY",
  "secretKey": "YOUR_SECRET_KEY",
  "passphrase": "YOUR_PASSPHRASE",
  "isSimulation": true
}
```

### `grid_settings.json`
Supports multiple named configurations (e.g., `main`, `micro`, `eth_micro`) for different instruments and strategies.

## Environment Variables

- `OKX_API_KEY`
- `OKX_SECRET_KEY`
- `OKX_PASSPHRASE`
- `OKX_IS_SIMULATION` (default: false)

## Disclaimer

This software is for educational purposes only. Do not trade money you cannot afford to lose.

---

# OKX Trader Skill (中文说明)

专为 OpenClaw 设计的 OKX 专业自动化网格交易系统。

## 交易逻辑

机器人执行**动态对称网格**策略：

1.  **定期维护:** 每5分钟，机器人对比当前市价与计划网格水位。如果某个水位缺失订单，则下达新的限价单。
2.  **自动移动:** 如果价格超出当前区间设定的偏移阈值，机器人将取消所有订单，并以新价格为中心重置网格。
3.  **止盈保护:** （针对小网格）卖单仅在满足相对于持仓均价的最小利润间隔时才会下达。

## 账户快照

`scripts/snapshot.js` 每日记录账户状态（余额、价格、24h 交易汇总），并与前一天对比权益变化。数据保存至 `okx_data/snapshots/YYYY-MM-DD.json`。

## 配置说明

文件应存放在 `/root/.openclaw/workspace/okx_data/` 目录下：

### `config.json`
见上方英文示例。

### `grid_settings.json`
支持多个命名配置（如 `main`、`micro`、`eth_micro`），可用于不同交易对和策略。

## 环境变量

见上方英文列表。

## 免责声明

本软件仅用于教学目的。请勿使用你无法承受损失的资金进行交易。
