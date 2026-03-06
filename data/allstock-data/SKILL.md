---
name: allstock-data
description: Stock market data query skill for China A-shares, Hong Kong, and US markets. Uses Tencent Finance HTTP API by default (lightweight, no install needed), with optional adata SDK for more comprehensive data. Supports real-time quotes, K-line history, order book analysis, and more.
---

# Stock Data Query

Two data sources are supported. **Tencent Finance HTTP API is used by default:**

1. **Tencent Finance HTTP API (Default)** — Lightweight, no installation, no proxy required
2. **adata SDK (Optional)** — More comprehensive data, requires installation and possibly a proxy

---

## 1. Tencent Finance HTTP API (Default)

### 1.1 China A-Share Real-Time Quotes

**Endpoint:**
```
http://qt.gtimg.cn/q=<stock_code>
```

**Stock Code Format:**

| Market | Code Prefix | Example |
|--------|-------------|---------|
| Shanghai Main Board | sh600xxx | sh600519 (Moutai) |
| STAR Market | sh688xxx | sh688111 |
| Shenzhen Main Board | sz000xxx | sz000001 (Ping An Bank) |
| ChiNext (GEM) | sz300xxx | sz300033 |
| ETF | sz159xxx | sz159919 |

**Index Codes:**

| Index | Code |
|-------|------|
| SSE Composite (Shanghai) | sh000001 |
| SZSE Component (Shenzhen) | sz399001 |
| ChiNext Index | sz399006 |
| STAR 50 | sz399987 |
| CSI 300 | sh000300 |

**Examples:**
```bash
# Single stock
curl -s "http://qt.gtimg.cn/q=sh600519"

# Multiple stocks
curl -s "http://qt.gtimg.cn/q=sh600519,sh000001,sz399001"
```

**Response Fields:**
```
v_sh600519="1~贵州茅台~600519~1460.00~1466.21~1466.99~14146~6374~7772~..."
          ~  Name    ~ Code  ~  Open  ~  High  ~   Low  ~ Volume
```

| Index | Field |
|-------|-------|
| 0 | Market code |
| 1 | Stock name |
| 2 | Stock code |
| 3 | Current price |
| 4 | Open price |
| 5 | Low price |
| 6 | High price |
| 30 | Price change |
| 31 | Change % |

---

### 1.2 Hong Kong Stock Real-Time Quotes

**Endpoint:**
```
http://qt.gtimg.cn/q=hk<stock_code>
```

**Examples:**
```bash
# Tencent Holdings
curl -s "http://qt.gtimg.cn/q=hk00700"

# Alibaba
curl -s "http://qt.gtimg.cn/q=hk09988"
```

---

### 1.3 US Stock Real-Time Quotes

**Endpoint:**
```
http://qt.gtimg.cn/q=us<ticker>
```

**Examples:**
```bash
# Apple
curl -s "http://qt.gtimg.cn/q=usAAPL"

# Tesla
curl -s "http://qt.gtimg.cn/q=usTSLA"

# NVIDIA
curl -s "http://qt.gtimg.cn/q=usNVDA"
```

---

### 1.4 K-Line Historical Data

**Endpoint:**
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get
```

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `_var` | Variable name, e.g. `kline_dayqfq` |
| `param` | stock_code, kline_type, start_date, end_date, count, adjust_type |

**K-Line Types:** `day` / `week` / `month`

**Adjustment Types:** `qfqa` (forward-adjusted) / `qfq` (backward-adjusted) / empty (unadjusted)

**Examples:**
```bash
# Moutai daily K-line (last 10 days, forward-adjusted)
curl -s "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sh600519,day,,,10,qfqa"

# Ping An Bank weekly K-line (last 5 weeks)
curl -s "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_weekqfq&param=sz000001,week,,,5,qfqa"

# ChiNext Index monthly K-line (last 3 months)
curl -s "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_monthqfq&param=sz399006,month,,,3,qfqa"
```

**Response Format:**
```json
{"day": [["2026-02-27", "1466.99", "1461.19", "1476.21", "1456.01", "13534"], ...]}
                Date       Open      Close      High       Low      Volume
```

---

### 1.5 Order Book Analysis

**Endpoint:**
```
http://qt.gtimg.cn/q=s_pk<stock_code>
```

**Example:**
```bash
curl -s "http://qt.gtimg.cn/q=s_pksh600519"
```

**Returns:** Buy/sell volume ratios (internal vs external trades)

---

## 2. adata SDK (Optional)

adata is an open-source A-share quantitative data library providing more comprehensive data. Requires installation and possibly a proxy.

### Installation

```bash
pip install adata
```

### Proxy Setup (if needed)

```python
import adata
adata.proxy(is_proxy=True, ip='your-proxy-ip:port')
```

### Feature List

| Feature | Description |
|---------|-------------|
| Stock Basic Info | All A-share codes, share capital, SW industry classification |
| K-Line Data | Daily/Weekly/Monthly, forward/backward adjustment |
| Real-Time Quotes | Batch real-time pricing |
| Level-2 Order Book | Bid/ask depth data |
| Capital Flow | Individual stock capital flow analysis |
| Concept Sectors | Thematic sector data |
| Index Data | Major index quotes |
| ETF | ETF quotes |

### Usage Examples

```python
import adata

# Get all A-share stock codes
df = adata.stock.info.all_code()

# Get K-line data
df = adata.stock.market.get_market(
    stock_code='000001',
    k_type=1,           # 1=daily, 2=weekly, 3=monthly
    start_date='2024-01-01',
    adjust_type=1        # 0=unadjusted, 1=forward, 2=backward
)

# Real-time quotes
df = adata.stock.market.list_market_current(
    code_list=['000001', '600519']
)
```

---

## 3. Use Case Guide

| Scenario | Recommended Source |
|----------|--------------------|
| Quick single stock price check | Tencent Finance API |
| K-line historical data | Tencent Finance API |
| Batch quote queries | Tencent Finance API |
| Capital flow data | adata SDK |
| Full financial statements | adata SDK |
| Concept/sector analysis | adata SDK |
| Level-2 order book | Tencent Finance API or adata SDK |

---

## 4. Important Notes

1. **Encoding**: Tencent Finance API returns GBK-encoded text — decode accordingly
2. **Change %**: Use the API's built-in field (index 31) — do not calculate manually
3. **Data Delay**: Real-time data may have up to 15-minute delay
4. **Request Rate**: Avoid high-frequency requests — use batch queries when possible
5. **Error Handling**: Invalid stock codes return `v_pv_none_match="1"`
