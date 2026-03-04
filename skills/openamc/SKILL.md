---
name: openamc
description:  OpenAMC 本地 MCP 命令调用技能。通过标准化 CLI 接口，允许 AI Agent 主动向本地 MCP Server 发送查询指令以获取全球金融数据。覆盖 A股/港股（AKShare）、美股（yfinance）、宏观经济（FRED/IMF/EconDB）、美国国会（Congress）及衍生品、外汇、大宗商品市场。
---

# OpenAMC Financial Intelligence  MCP Connector

OpenAMC 是一个轻量级金融数据查询连接器技能。本技能仅提供本地 MCP Server 命令调用能力，不包含自动交易执行、持续监控或本地系统控制逻辑。这是一个基于 OpenAMC Platform 的全能金融分析技能包。通过 `mcporter` (命令为 `mcp`) 调用本地 MCP Server，查询跨市场、全资产类别的金融数据。

## 核心要求

- **mcporter**: 确保 `mcp` 命令已全局可用。
- **OpenAMC MCP Server**: 建议运行于 `http://127.0.0.1:8001`。
- **数据源**: 集成了 AKShare, yfinance, FRED, FMP, SEC, Congress.gov, IMF, EconDB 等。

## 场景调用指南 (When to Use)

AI Agent 在遇到以下任务时应主动调用本技能：

- **中国市场分析**: 当用户提到金融市场行情、 A 股（6位数字代码）、港股、中国基金、或要求查看中国公司新闻/主营业务时，查看上市公司的行情时。
- **外汇交易**: 涉及外汇市场货币对而行情，汇率报价、货币对分析（如 EUR/USD, USD/JPY）。
- **全球股票研究**: 需要查看美股（如 AAPL, TSLA）的实时报价、财务指标或分析师评级时。
- **宏观趋势研判与固定收益查询**: 当涉及 GDP、CPI、失业率、美联储利率、国债收益率曲线等宏观经济指标时。
- **政策与合规监控**: 当需要查询美国国会法案动态、SEC 监管文件（10-K, 10-Q）时。
- **多资产比价**: 需要查询黄金、原油（大宗商品）、比特币（加密货币）或汇率走势时。

## 核心指令集

### 1. 股票行情与历史 (Equity Price & History)
支持全球主流交易所。对于 A 股和港股，推荐显式指定 `akshare` 驱动。

```bash
# 获取 A股 茅台历史 K 线 (AKShare)
mcp call openamc equity_price_historical --args '{"symbol": "600519", "provider": "akshare", "interval": "1d", "start_date": "2025-01-01"}'

# 获取美股 NVDA 实时报价 (yfinance)
mcp call openamc equity_price_quote --args '{"symbol": "NVDA", "provider": "yfinance"}'

# 获取港股 06823 历史数据 (AKShare)
mcp call openamc equity_price_historical --args '{"symbol": "06823", "provider": "akshare"}'
```

### 2.中国市场深度研究 (AKShare Specialized)
利用 AKShare 插件特有的深度数据函数。

```bash
# A股 公司主营业务分析 (主营构成)
mcp call openamc akshare_business_analysis --args '{"symbol": "600519", "provider": "akshare"}'

# A股 ETF 持仓查询 (输入 ETF 代码)
mcp call openamc akshare_etf_holdings --args '{"symbol": "510300", "provider": "akshare"}'

# A股 个股新闻舆情
mcp call openamc news_company --args '{"symbol": "000002", "provider": "akshare"}'
```
### 3. 宏观经济 (Economy)
连接 FRED, IMF 和 EconDB，支持 GDP、CPI、失业率等指标查询。

```bash
# 获取全球失业率数据 (EconDB)
mcp call openamc economy_unemployment --args '{"provider": "econdb"}'

# 获取 FRED 源的经济指标
mcp call openamc economy_indicators --args '{"symbol": "GDP", "provider": "fred"}'

# 获取 IMF 经济展望工具
mcp call openamc imf_utils_general --args '{"provider": "imf"}'
```
### 4. 政策、监管与固定收益 (Policy and Fixed Income)
连接 监管, SEC文件，支持 国债收益率等固定收益指标查询。

```bash
# 追踪美国第 119 届国会最新法案
mcp call openamc uscongress_bills --args '{"congress": 119, "provider": "congress_gov"}'

# 获取 SEC 申报文件 (10-K/10-Q)
mcp call openamc regulators_sec_filings --args '{"symbol": "TSLA", "provider": "sec"}'

# 获取国债收益率曲线
mcp call openamc fixedincome_government_treasury_rates --args '{"provider": "federal_reserve"}'

# 查美联储实际利率 (FEDFUNDS)
mcp call openamc economy_fred_series --args '{"symbol": "FEDFUNDS", "provider": "fred", "start_date": "2026-01-01"}'

# 查美联储政策利率目标上限 (DFEDTARU)
mcp call openamc economy_fred_series --args '{"symbol": "DFEDTARU", "provider": "fred", "start_date": "2026-01-01"}'

# 获取的是美联储官方公布的有效隔夜利率
mcp call openamc fixedincome_rate_effr --args '{"provider": "federal_reserve", "start_date": "2026-01-01"}'
```
### 5. 外汇市场 (Forex Market)
针对有外汇交易背景的用户，提供全球主流货币对（Major Pairs）及交叉盘的深度行情与趋势分析。

- **实时汇率报价**: `currency_price_historical` (支持多种频率选择)
- **货币对搜索**: 可结合 `yfinance` 搜索特定汇率对。

```bash
# 获取 欧元/美元 (EURUSD) 历史行情
mcp call openamc currency_price_historical --args '{"symbol": "EURUSD=X", "provider": "yfinance", "interval": "1d"}'

# 获取 英镑/美元 (GBPUSD) 历史行情
mcp call openamc currency_price_historical --args '{"symbol": "GBPUSD=X", "provider": "yfinance", "start_date": "2026-02-01"}'

# 获取 美元/日元 (USDJPY)
mcp call openamc currency_price_historical --args '{"symbol": "USDJPY=X", "provider": "yfinance"}'
```

### 6. 多资产类别 (Commodity, Crypto, Forex, Derivatives)
支持商品，加密货币，外汇，衍生品等多资产类别的数据查询。

```bash
# 大宗商品历史价格 (如黄金 GC=F)
mcp call openamc commodity_price_historical --args '{"symbol": "GC=F", "provider": "yfinance"}'

# 数字货币行情 (BTC-USD)
mcp call openamc crypto_price_historical --args '{"symbol": "BTC-USD", "provider": "yfinance"}'

# 外汇对行情 (EURUSD=X)
mcp call openamc currency_price_historical --args '{"symbol": "EURUSD=X", "provider": "yfinance"}'

# 获取期权链数据
mcp call openamc derivatives_options_chains --args '{"symbol": "AAPL", "provider": "yfinance"}'
```

## 证券代码与驱动规范 (Symbol Format)

| 资产类型        | 示例代码              | 推荐 Provider        |
|---------------|----------------------|----------------------|
| A股 (沪深)     | 600519, 000002       | akshare              |
| 港股           | 06823                | akshare              |
| 美股           | AAPL, NVDA           | yfinance / fmp       |
| 加密货币       | BTC-USD              | yfinance             |
| 大宗商品       | GC=F, CL=F           | yfinance             |
| 外汇 (Forex) | EURUSD=X, GBPUSD=X, USDCNY=X | yfinance |
---

## 工具发现与自检 (Meta Tools)

AI Agent 可通过以下指令动态发现 193 个函数的具体用法：

**查看全部分类：**
```bash
mcp call openamc available_categories
```

## 工具发现与自检 (Meta Tools)
AI Agent 可通过以下指令动态发现 193 个函数的具体用法：
```bash
#查看全部分类
mcp call openamc available_categories

# 查看特定分类下的工具
mcp call openamc available_tools --args '{"category": "equity"}
```
## 故障排除 (Troubleshooting)

- **A股报价报错：**  
  若 `equity_price_quote` 提示关键字段错误，请使用 `equity_price_historical` 替代。

- **返回空结果：**  
  检查 `provider` 是否与 `symbol` 匹配（如 A股不能使用 `yfinance`）。

- **超时限制：**  
  大批量数据请求时，请在命令末尾增加：  --timeout 60000


