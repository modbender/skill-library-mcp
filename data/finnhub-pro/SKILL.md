---
name: finnhub
description: 使用 Finnhub 获取美股/全球股票的实时报价、公司档案、新闻、分析师推荐、内部人交易、盈利日历和基本面财务数据。适用场景：查股价、查公司信息、看最新新闻、了解内部人是否在买卖、查看近期财报日期。免费层60次/分钟。
---

# Finnhub 金融数据技能

使用 Finnhub API 获取美股及全球市场数据。

## API Key

已保存：`YOUR_FINNHUB_API_KEY`（环境变量 `FINNHUB_API_KEY` 或脚本内硬编码）

## 使用方法

通过 Python 脚本调用：

```bash
python3 /Users/dtbllsj/.openclaw/workspace/skills/finnhub/scripts/finnhub_cli.py <command> [args] [--json] [--limit N]
```

或更简洁（在代理中直接用 exec 工具运行）：

```
PYTHON=/Users/dtbllsj/.pyenv/versions/3.12.12/bin/python3
SCRIPT=/Users/dtbllsj/.openclaw/workspace/skills/finnhub/scripts/finnhub_cli.py
```

## 免费层支持的命令

### 实时报价
```bash
python3 $SCRIPT quote AAPL
python3 $SCRIPT quote NVDA
python3 $SCRIPT quote TSLA --json   # 返回原始JSON
```

### 公司��案
```bash
python3 $SCRIPT profile AAPL
python3 $SCRIPT profile BABA
```

### 公司新闻（最近7天）
```bash
python3 $SCRIPT news NVDA
python3 $SCRIPT news AAPL --from 2026-02-01 --to 2026-02-21 --limit 5
```

### 分析师推荐趋势
```bash
python3 $SCRIPT recommend NVDA
python3 $SCRIPT recommend TSLA
```

### 内部人交易记录（最近90天）
```bash
python3 $SCRIPT insiders AAPL
python3 $SCRIPT insiders NVDA --from 2026-01-01 --to 2026-02-21
```

### 盈利日历（未来30天）
```bash
python3 $SCRIPT earnings             # 所有股票
python3 $SCRIPT earnings NVDA        # 指定股票
python3 $SCRIPT earnings --from 2026-02-21 --to 2026-03-07 --limit 30
```

### 基本面财务指标
```bash
python3 $SCRIPT financials AAPL
python3 $SCRIPT financials NVDA --json   # 全部指标JSON
```

### 市场状态
```bash
python3 $SCRIPT market          # 默认美国市场
python3 $SCRIPT market NYSE
python3 $SCRIPT market NASDAQ
```

### 同行公司
```bash
python3 $SCRIPT peers AAPL
python3 $SCRIPT peers NVDA
```

### 股票代码搜索
```bash
python3 $SCRIPT search "apple"
python3 $SCRIPT search "nvidia"
```

## 不可用功能（付费层）

- `stock_candles` - K线数据（需付费）
- `price_target` - 分析师目标价（需付费）
- `news_sentiment` - 新闻情绪��析（需付费）
- `stock_candles` - 历史价格（需付费）

## 限制

- 免费层：60次/分钟请求限额
- 错误码 403 = 需要付费升级
- 错误码 429 = 触发限速

## Python 直接调用

```python
import finnhub
client = finnhub.Client(api_key="YOUR_FINNHUB_API_KEY")

# 实时报价
quote = client.quote("AAPL")

# 内部人交易
insiders = client.stock_insider_transactions("AAPL", "2026-01-01", "2026-02-21")

# 盈利日历
earnings = client.earnings_calendar(_from="2026-02-21", to="2026-03-07", symbol="", international=False)

# 基本面
financials = client.company_basic_financials("AAPL", "all")
```
