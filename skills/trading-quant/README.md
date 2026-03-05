# trading-quant

量化交易数据分析工具 | Quantitative Trading Data Analysis Tool

> **Disclaimer**: 本工具仅供数据展示与分析，不构成任何投资建议。投资有风险，请谨慎决策。  
> This is an open-source tool for data analysis only. It does not provide investment advice.

## 功能 Features

- **实时行情** Real-time quotes: A股 / 美股 / 港股 / 贵金属
- **多维度评分** Multi-dimensional scoring: 技术面 + 资金面 + 基本面 + 消息面 + 情绪面
- **涨跌停异动** Limit-up/down anomalies: 涨停池、跌停池、市场情绪
- **北向资金** Northbound flow: 沪股通、深股通资金流向
- **资金流分析** Capital flow: 个股主力资金、分钟级资金流
- **全球市场概览** Global overview: 多市场指数与商品联动

## 安装 Install

```bash
clawhub install trading-quant
```

## 依赖 Dependencies

- Python 3.10+
- pandas, pandas-ta, httpx, aiohttp, pyyaml, python-dateutil
- akshare, requests (可选 optional)

安装后运行 `pip install -r requirements.txt` 安装 Python 依赖。

## 用法 Usage

```bash
# A股分析
python scripts/quant.py stock_analysis 000001 600519
python scripts/quant.py intraday_snapshot

# 全球市场
python scripts/quant.py us_stock AAPL MSFT
python scripts/quant.py hk_stock 00700
python scripts/quant.py commodity gold silver
python scripts/quant.py global_overview

# 市场数据
python scripts/quant.py market_anomaly
python scripts/quant.py market_scan
python scripts/quant.py northbound_flow
python scripts/quant.py capital_flow 000001 600519
python scripts/quant.py gold_analysis
```

## 数据源 Data Sources

| 市场 | 主源 | 降级链 |
|------|------|--------|
| A股 | 腾讯 | 新浪→东财→同花顺 |
| 美股 | 腾讯 | yfinance |
| 港股 | 腾讯 | - |
| 商品 | 新浪期货 | - |

## License

MIT
