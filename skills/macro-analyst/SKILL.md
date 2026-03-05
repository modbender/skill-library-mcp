---
name: macro-analyst
description: 宏观经济分析工具集 - 基于AKShare的GDP/CPI/PMI/利率/汇率数据
keywords:
  - 宏观
  - GDP
  - CPI
  - PMI
  - 利率
  - 汇率
---

# Macro Analyst — 宏观经济分析

## 数据获取

### 中国宏观
```bash
PYTHON=python3.12
SCRIPT=skills/akshare-finance/scripts/macro_data.py

# GDP (季度)
$PYTHON $SCRIPT gdp

# CPI (月度)
$PYTHON $SCRIPT cpi

# PMI (月度)
$PYTHON $SCRIPT pmi

# M2货币供应 (月度)
$PYTHON $SCRIPT m2
```

### 个股财报 (行业聚合分析用)
```bash
$PYTHON skills/akshare-finance/scripts/earnings.py report 600519
$PYTHON skills/akshare-finance/scripts/earnings.py earnings
$PYTHON skills/akshare-finance/scripts/earnings.py industry
```

### 全球市场
```bash
# 全球市场概览 (via quant.py)
$PYTHON workspace-trading/skills/trading-quant/scripts/quant.py global_overview
```

### 汇率
```python
# 使用 akshare 直接调用
import akshare as ak
ak.currency_boc_sina()  # 中国银行汇率
```

## 分析框架

### 宏观日报流程
1. 获取 global_overview → 全球市场概况
2. 获取 GDP/CPI/PMI → 经济趋势判断
3. 检查 earnings → 季度业绩预告趋势
4. 综合分析 → 宏观展望

### 宏观周报流程
1. 本周全球市场回顾 (global_overview)
2. 宏观数据对比 (GDP/CPI/PMI 趋势)
3. 行业轮动分析 (industry)
4. 下周展望与风险提示

## 与其他 Agent 的协作
- 个股深度分析 → 交给 trading
- AI 行业趋势 → 交给 ainews
- Macro 关注: 政策影响、经济周期、行业估值
