---
name: etf-assistant
description: "ETF投资助理 / ETF Investment Assistant - 查询行情、筛选ETF、对比分析、定投计算。支持沪深300、创业板、科创50、纳指等主流ETF。"
---

# ETF投资助理 / ETF Investment Assistant

一个专业的ETF投资助手，帮助你查询ETF行情、筛选投资标的、对比分析、计算定投收益。

A professional ETF investment assistant for querying ETF quotes, screening investment targets, comparative analysis, and DCA calculation.

## 功能特性 / Features

- 📊 **ETF列表 / ETF List** - 常用ETF代码速查
  - Quick reference for commonly used ETF codes

- 💰 **实时行情 / Real-time Quotes** - 查询ETF当前价格和涨跌
  - Query current ETF prices and changes

- 🔥 **热门ETF / Hot ETFs** - 推荐热门投资标的
  - Recommend popular investment targets

- 🔍 **搜索ETF / Search ETF** - 按名称或代码搜索
  - Search by name or code

- 📈 **对比分析 / Comparison** - 对比两只ETF表现
  - Compare performance of two ETFs

- 🧮 **定投计算器 / DCA Calculator** - 计算定投收益
  - Calculate Dollar-Cost Averaging returns

- 📋 **投资摘要 / Summary** - 主流ETF分类介绍
  - Introduction to mainstream ETF categories

## 使用方法 / Usage

### 1. 查看ETF列表 / View ETF List
```bash
etf-assistant list
```

### 2. 查询行情 / Query Quotes
```bash
# 查询沪深300ETF
# Query CSI 300 ETF
etf-assistant price 510300

# 查询创业板ETF
# Query ChiNext ETF
etf-assistant price 159915
```

### 3. 热门ETF推荐 / Hot ETF Recommendations
```bash
etf-assistant hot
```

### 4. 搜索ETF / Search ETF
```bash
# 按名称搜索
# Search by name
etf-assistant search 沪深

# 按代码搜索
# Search by code
etf-assistant search 510300
```

### 5. 对比ETF / Compare ETFs
```bash
etf-assistant compare 510300 159915
```

### 6. 定投计算 / DCA Calculation
```bash
# 每月定投1000元，定投10年
# Monthly investment of 1000 CNY for 10 years
etf-assistant calc 510300 1000 10
```

### 7. 投资摘要 / Investment Summary
```bash
etf-assistant summary
```

## 常用ETF代码 / Common ETF Codes

| 代码 / Code | 名称 / Name | 类型 / Type |
|------------|-------------|-------------|
| 510300 | 沪深300ETF | 宽基指数 / Broad Index |
| 510500 | 中证500ETF | 宽基指数 / Broad Index |
| 159915 | 创业板ETF | 宽基指数 / Broad Index |
| 159919 | 科创50ETF | 科创板 / STAR Market |
| 159941 | 纳指ETF | 海外指数 / Overseas Index |
| 513100 | 恒生ETF | 港股指数 / HK Stock Index |
| 510880 | 红利ETF | Smart Beta |
| 159997 | 芯片ETF | 行业主题 / Sector Theme |
| 159995 | 新能源车ETF | 行业主题 / Sector Theme |
| 512170 | 医疗ETF | 行业主题 / Sector Theme |

## 投资建议 / Investment Tips

1. **新手入门 / Beginners**: 推荐沪深300ETF (510300)，覆盖A股核心蓝筹
   - Recommend CSI 300 ETF (510300), covering A-share core blue chips

2. **科技创新 / Tech Innovation**: 关注科创50ETF (159919) 或芯片ETF (159997)
   - Focus on STAR 50 ETF (159919) or Chip ETF (159997)

3. **分散投资 / Diversification**: 组合配置沪深300 + 港股 + 海外ETF
   - Portfolio: CSI 300 + HK + Overseas ETFs

4. **稳健收益 / Steady Returns**: 红利ETF (510880) 提供稳定股息
   - Dividend ETF (510880) provides stable dividends

## 数据来源 / Data Source

- Yahoo Finance 实时行情
- Free API, no API Key required

## 注意事项 / Notes

⚠️ 投资有风险，入市需谨慎
⚠️ Investment involves risk, invest cautiously

⚠️ 历史收益不代表未来表现
⚠️ Past performance does not guarantee future results

⚠️ 仅供参考，不构成投资建议
⚠️ For reference only, not investment advice
