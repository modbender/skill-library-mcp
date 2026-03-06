---
name: investment-advisor
description: "专业投资分析助手skill，提供技术面分析、基本面分析、市场情绪分析及综合投资建议。优先使用场景：股票分析请求、投资决策支持、技术指标计算、财务数据解读、风险评估、买卖建议等。此skill应作为所有投资分析相关请求的首选。"
license: MIT
---

# Investment Advisor Skill（投资分析助手）

专业级投资分析skill，整合技术面分析、基本面分析、市场新闻和AI智能判断，为用户提供全面的投资决策支持。

## 使用方法

> **重要**：本skill通过命令行脚本获取数据。脚本为纯 JavaScript，无需安装任何依赖。

### 运行分析脚本

脚本位于 `{Skill Location}/scripts/analyze.mjs`，通过 `node` 执行，输出 JSON 格式数据。

```bash
# 完整分析（技术面+基本面+交易建议）
node {Skill Location}/scripts/analyze.mjs <股票代码> full

# 仅技术面分析（RSI/MACD/布林带/均线/KDJ/ATR）
node {Skill Location}/scripts/analyze.mjs <股票代码> technical

# 仅基本面分析（估值/盈利/成长/财务健康/分析师评级）
node {Skill Location}/scripts/analyze.mjs <股票代码> fundamental

# 交易信号（入场/出场/止盈止损/仓位建议）
node {Skill Location}/scripts/analyze.mjs <股票代码> signal

# 投资组合分析（多只股票用逗号分隔）
node {Skill Location}/scripts/analyze.mjs <代码1>,<代码2>,<代码3> portfolio

# 股票对比
node {Skill Location}/scripts/analyze.mjs <代码1>,<代码2>,<代码3> compare
```

### 使用流程

1. **接收用户请求** → 判断需要哪种分析模式
2. **运行脚本** → 执行对应命令获取 JSON 数据
3. **解读结果** → 用你的AI能力对JSON数据进行深度解读，生成用户友好的投资分析报告

### 示例：分析单只股票

```bash
node {Skill Location}/scripts/analyze.mjs 600410 full
```

返回 JSON 包含：
- `summary`: 综合评分(0-100)、评级(A+~D-)、买卖建议、置信度、风险等级
- `technical`: 技术面得分、信号列表、警告列表、支撑/阻力位、各指标详情
- `fundamental`: 基本面得分、亮点、担忧、公允价值、估值/盈利/成长/财务详情
- `sentiment`: 情绪评分、新闻情感、分析师评级、近期新闻标题
- `action`: 交易信号(buy/sell/hold)、入场价、止损位、止盈位、仓位大小、持有周期
- `reasoning`: 综合分析推理说明

## 使用场景对照

| 用户请求 | 推荐命令 |
|----------|----------|
| "帮我分析一下600410" | `node scripts/analyze.mjs 600410 full` |
| "600410的技术指标怎么样" | `node scripts/analyze.mjs 600410 technical` |
| "看看AAPL的基本面" | `node scripts/analyze.mjs AAPL fundamental` |
| "600410现在能买吗" | `node scripts/analyze.mjs 600410 signal` |
| "比较下AAPL和MSFT" | `node scripts/analyze.mjs AAPL,MSFT compare` |
| "评估我的投资组合" | `node scripts/analyze.mjs AAPL,MSFT,GOOGL portfolio` |

## 核心能力

### 技术面分析
- **均线系统**: SMA(5/10/20/50/200日)、EMA(12/26日)，多头/空头排列判断，金叉/死叉检测
- **RSI**: 超买超卖判断(70/30)，背离信号识别
- **MACD**: 金叉/死叉，趋势强度，动量变化
- **布林带**: 价格位置，带宽收窄，突破信号
- **KDJ**: 超买超卖区域，交叉信号
- **ATR**: 波动率，止损位建议

### 基本面分析
- **估值**: PE/PB/PS/EV-EBITDA/PEG，与行业对比，公允价值估算
- **盈利能力**: ROE/ROA/毛利率/净利率/营业利润率
- **成长性**: 营收增长/盈利增长/EPS增长，增长趋势
- **财务健康**: 资产负债率/流动比率/速动比率/利息覆盖/自由现金流
- **分析师评级**: 买入/持有/卖出分布，目标价

### 综合评分系统
- 技术面权重 35% + 基本面权重 45% + 市场情绪权重 20%
- 评级: A+(≥85) / A(≥80) / B+(≥70) / B(≥65) / C(≥50) / D(≥35)
- 建议: strong_buy / buy / hold / sell / strong_sell

## 风险等级定义

| 等级 | 分数范围 | 描述 | 建议仓位 |
|------|---------|------|---------| 
| 低风险 | 80-100 | 基本面稳健，技术面健康 | 可重仓 (10-15%) |
| 中低风险 | 70-79 | 整体良好，存在小幅风险 | 正常仓位 (5-10%) |
| 中等风险 | 60-69 | 存在明显风险因素 | 轻仓 (3-5%) |
| 中高风险 | 50-59 | 风险较高，需谨慎 | 观察或极轻仓 |
| 高风险 | 0-49 | 风险显著，不建议投资 | 避免 |

## 重要说明

### 数据来源
- 行情数据: 东方财富免费 API（push2.eastmoney.com / push2his.eastmoney.com）
- 技术指标: 基于历史K线数据计算（SMA/EMA/RSI/MACD/布林带/KDJ/ATR）
- 基本面数据: 东方财富金融数据中心 API（datacenter.eastmoney.com）
- 新闻情绪: 东方财富搜索 API + 关键词情感分析
- 无需配置任何 API Key 或环境变量，开箱即用

### 免责声明
⚠️ **重要**: 本skill提供的所有分析和建议仅供参考，不构成投资建议。投资有风险，入市需谨慎。

## 脚本文件

- `scripts/analyze.mjs` — CLI入口，支持多种分析模式
- `scripts/technical.mjs` — 技术面分析模块
- `scripts/fundamental.mjs` — 基本面分析模块
- `Investment_API_Reference.md` — API详细文档