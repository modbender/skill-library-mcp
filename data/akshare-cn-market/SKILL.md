---
name: akshare-cn-market
description: 中国A股行情与宏观经济数据工具，基于 AKShare 库。支持个股K线、大盘指数、财务摘要、GDP/CPI/PMI/M2货币供应、中美国债收益率等。
---

# AKShare 中国市场数据

## 安装依赖

```bash
pip install akshare pandas
# 验证
python3 -c "import akshare; print(akshare.__version__)"
```

## 脚本用法

### 股票行情（scripts/stock.py）

```bash
# 个股历史K线（默认最近10条日线，前复权）
python3 scripts/stock.py hist 000001
python3 scripts/stock.py hist 600519 --n 20 --start 20240101

# 大盘指数K线（新浪源）
python3 scripts/stock.py index sh000001      # 上证综指
python3 scripts/stock.py index sh000300      # 沪深300
python3 scripts/stock.py index sz399001      # 深证成指
python3 scripts/stock.py index sh000016 --n 5   # 上证50，最近5条

# 个股财务摘要（近5年）
python3 scripts/stock.py financial 000001
python3 scripts/stock.py financial 600519
```

### 宏观数据（scripts/macro.py）

```bash
# GDP 季度数据（默认最近8季度）
python3 scripts/macro.py gdp
python3 scripts/macro.py gdp --n 4

# CPI 月度数据（默认最近12个月）
python3 scripts/macro.py cpi

# PMI（制造业 + 非制造业，默认最近12个月）
python3 scripts/macro.py pmi

# 货币供应量 M0/M1/M2（默认最近12个月）
python3 scripts/macro.py money

# 中美国债收益率（默认最近10个交易日）
python3 scripts/macro.py bond --n 5
```

### 交易日历（scripts/trade_cal.py）

```bash
# 判断今天是否为交易日
python3 scripts/trade_cal.py check today

# 判断指定日期
python3 scripts/trade_cal.py check 2026-03-01

# 当天或之后最近的交易日
python3 scripts/trade_cal.py next today
python3 scripts/trade_cal.py next 2026-02-01

# 当天或之前最近的交易日（获取最近一个收盘日）
python3 scripts/trade_cal.py prev today

# 列出区间内所有交易日
python3 scripts/trade_cal.py range 2026-03-02 2026-03-06
```

数据来源：新浪财经，覆盖 1990-12-19 至 2026-12-31。

## 在 Agent 中直接调用

```python
import akshare as ak

# A股个股K线
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", adjust="qfq")

# 大盘指数（新浪源，不受东方财富代理限制）
df = ak.stock_zh_index_daily(symbol="sh000001")

# 宏观：GDP / CPI / PMI / 货币供应
df = ak.macro_china_gdp()
df = ak.macro_china_cpi()
df = ak.macro_china_pmi()
df = ak.macro_china_money_supply()

# 中美国债收益率
df = ak.bond_zh_us_rate()

# 交易日判断（覆盖至2026年底）
from scripts.trade_cal import is_trade_day, next_trade_day, prev_trade_day
if not is_trade_day("2026-03-02"):
    print("非交易日，跳过")
last_close = prev_trade_day("2026-03-02")  # 最近一个收盘日

# 个股财务摘要（同花顺）
df = ak.stock_financial_abstract_ths(symbol="000001", indicator="按年度")
```

## 返回格式

所有脚本输出均为 JSON 数组（每条记录一个对象）。

## 常用指数代码

| 代码 | 指数 |
|------|------|
| sh000001 | 上证综指 |
| sz399001 | 深证成指 |
| sh000300 | 沪深300 |
| sh000016 | 上证50 |
| sh000905 | 中证500 |

## 注意事项

- **数据来源**：公开财经网站，仅供研究参考
- **网络要求**：宏观数据 + 新浪源指数在大多数环境可用；东方财富实时行情在部分代理环境下可能超时
- **数据延迟**：实时/日线数据可能有15分钟～1日延迟
- **投资风险**：数据仅供参考，投资决策请自行判断
