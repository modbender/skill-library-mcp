---
name: alpha-vantage
description: >-
  Alpha Vantage 金融数据 API。支持股票、外汇、加密货币的实时和历史数据。
  免费 API key: demo (限流)，建议申请自己的免费 key。
requirements:
  - Node.js
  - 网络连接
  - (可选) Alpha Vantage API key from https://www.alphavantage.co/support/#api-key
examples:
  - "查询苹果股票: alpha quote AAPL"
  - "查询日K线: alpha daily AAPL"
  - "查询外汇汇率: alpha forex USD/JPY"
  - "查询加密货币: alpha crypto BTC/USD"
  - "设置 API key: alpha apikey YOUR_KEY"
---

# Alpha Vantage Skill

Alpha Vantage 提供股票、外汇、加密货币等金融数据接口。

## 快速开始

### 设置 API Key (推荐)

```bash
# 使用自己的 API key (免费申请: https://www.alphavantage.co/support/#api-key)
node alpha.js apikey YOUR_API_KEY

# 或使用演示 key (限流)
node alpha.js quote AAPL
```

### 查询实时报价

```bash
# 股票报价
node alpha.js quote AAPL

# 带 API key
ALPHA_KEY=your_key node alpha.js quote AAPL
```

### 获取历史 K 线

```bash
# 日K线
node alpha.js daily AAPL

# 周K线
node alpha.js weekly IBM

# 月K线
node alpha.js monthly MSFT
```

### 外汇汇率

```bash
# 美元兑日元
node alpha.js forex USD/JPY

# 欧元兑美元
node alpha.js forex EUR/USD
```

### 加密货币

```bash
# 比特币兑美元
node alpha.js crypto BTC/USD

# 以太坊兑比特币
node alpha.js crypto ETH/BTC
```

## 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| quote | 实时报价 | `alpha quote AAPL` |
| daily | 日K线 | `alpha daily AAPL` |
| weekly | 周K线 | `alpha weekly AAPL` |
| monthly | 月K线 | `alpha monthly AAPL` |
| forex | 汇率 | `alpha forex USD/JPY` |
| crypto | 加密货币 | `alpha crypto BTC/USD` |
| apikey | 设置 API key | `alpha apikey YOUR_KEY` |

## 注意事项

1. **免费 API 限流** - 每分钟 5 次请求，每天 500 次
2. **演示 key** - 使用 `demo` key 可能有严格限流
3. **数据延迟** - 免费版数据可能有 15 分钟延迟
4. **申请免费 key** - https://www.alphavantage.co/support/#api-key