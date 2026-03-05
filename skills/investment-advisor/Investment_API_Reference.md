# Investment API Reference

本文档提供投资分析相关的API详细说明，包括Finance API的使用方法以及技术指标计算公式。

## 目录

1. [Finance API基础](#finance-api基础)
2. [技术指标计算公式](#技术指标计算公式)
3. [基本面数据解读](#基本面数据解读)
4. [分析框架](#分析框架)

---

## Finance API基础

### API访问配置

```typescript
const GATEWAY_URL = process.env.GATEWAY_URL || 'https://internal-api.z.ai';
const API_PREFIX = '/external/finance';
const BASE_URL = `${GATEWAY_URL}${API_PREFIX}`;

const headers = {
  'X-Z-AI-From': 'Z'
};
```

### 核心端点

#### 1. 股票搜索
```
GET /v1/markets/search?search={keyword}
```

#### 2. 实时报价
```
GET /v1/markets/quote?ticker={symbol}&type=STOCKS
```

#### 3. 历史数据
```
GET /v1/markets/stock/history?symbol={symbol}&interval={interval}&diffandsplits=false
```

支持的间隔：
- `1m`, `5m`, `15m`, `30m`, `1h` - 短期
- `1d` - 日线
- `1wk` - 周线
- `1mo` - 月线

#### 4. 公司资料
```
GET /v1/markets/stock/modules?ticker={symbol}&module=asset-profile
```

#### 5. 财务数据
```
GET /v1/markets/stock/modules?ticker={symbol}&module=financial-data
```

#### 6. 统计数据
```
GET /v1/markets/stock/modules?ticker={symbol}&module=statistics
```

#### 7. 收益数据
```
GET /v1/markets/stock/modules?ticker={symbol}&module=earnings
```

#### 8. 资产负债表
```
GET /v1/markets/stock/modules?ticker={symbol}&module=balance-sheet
```

#### 9. 现金流量表
```
GET /v1/markets/stock/modules?ticker={symbol}&module=cashflow-statement
```

#### 10. 损益表
```
GET /v1/markets/stock/modules?ticker={symbol}&module=income-statement
```

#### 11. 机构持股
```
GET /v1/markets/stock/modules?ticker={symbol}&module=institution-ownership
```

#### 12. 分析师评级
```
GET /v1/markets/stock/modules?ticker={symbol}&module=upgrade-downgrade-history
```

#### 13. 市场新闻
```
GET /v1/markets/news?ticker={symbol}
```

---

## 技术指标计算公式

### 1. 移动平均线 (Moving Averages)

#### 简单移动平均 (SMA)
```
SMA(n) = (P1 + P2 + ... + Pn) / n

其中：
- Pn = 第n期的收盘价
- n = 周期数
```

常用周期：
- SMA5: 短期趋势
- SMA10: 短期趋势确认
- SMA20: 月线趋势
- SMA50: 中期趋势
- SMA200: 长期趋势（牛熊分界线）

#### 指数移动平均 (EMA)
```
EMA(today) = P(today) × K + EMA(yesterday) × (1 - K)
K = 2 / (n + 1)

其中：
- P(today) = 今日收盘价
- n = 周期数
- K = 平滑系数
```

EMA对近期价格赋予更大权重，反应更灵敏。

### 2. RSI (Relative Strength Index)

```
RSI = 100 - (100 / (1 + RS))
RS = 平均上涨幅度 / 平均下跌幅度

计算步骤：
1. 计算n日内上涨日的涨幅之和（U）
2. 计算n日内下跌日的跌幅之和（D）
3. 计算平均上涨和下跌：
   - 简单平均: AvgU = U/n, AvgD = D/n
   - 指数平均: AvgU = (前一日AvgU × (n-1) + 今日U) / n
4. RS = AvgU / AvgD
5. RSI = 100 - (100 / (1 + RS))
```

常用周期：14日

信号解读：
- RSI > 70: 超买
- RSI < 30: 超卖
- RSI 背离: 价格创新高但RSI未创新高 → 看跌信号

### 3. MACD (Moving Average Convergence Divergence)

```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(MACD Line, 9)
Histogram = MACD Line - Signal Line
```

信号解读：
- 金叉: MACD上穿Signal → 买入信号
- 死叉: MACD下穿Signal → 卖出信号
- 柱状图: 正值扩大表示多头加强

### 4. 布林带 (Bollinger Bands)

```
中轨 = SMA(n)
上轨 = 中轨 + K × σ
下轨 = 中轨 - K × σ

其中：
- n = 周期数（通常20）
- K = 标准差倍数（通常2）
- σ = n日价格标准差

σ = √[Σ(Pi - SMA)² / n]
```

信号解读：
- 价格突破上轨: 超买或强势突破
- 价格跌破下轨: 超卖或强势下跌
- 布林带收窄: 可能即将突破

### 5. KDJ指标

```
RSV = (C - Ln) / (Hn - Ln) × 100
K = (2/3) × K(昨日) + (1/3) × RSV
D = (2/3) × D(昨日) + (1/3) × K
J = 3 × K - 2 × D

其中：
- C = 当日收盘价
- Ln = n日内最低价
- Hn = n日内最高价
- n = 周期数（通常9）
```

信号解读：
- K > 80, D > 80: 超买
- K < 20, D < 20: 超卖
- K上穿D: 买入信号
- K下穿D: 卖出信号

### 6. CCI (Commodity Channel Index)

```
TP = (High + Low + Close) / 3
CCI = (TP - SMA(TP, n)) / (0.015 × MD)

其中：
- TP = 典型价格
- n = 周期数（通常20）
- MD = 平均绝对偏差
```

信号解读：
- CCI > 100: 超买
- CCI < -100: 超卖

### 7. ATR (Average True Range)

```
TR = max(High - Low, |High - Close昨日|, |Low - Close昨日|)
ATR = SMA(TR, n)

常用周期: 14日
```

ATR用于衡量波动性，常用于设置止损位。

### 8. OBV (On-Balance Volume)

```
如果今日收盘价 > 昨日收盘价:
  OBV = OBV昨日 + 今日成交量
如果今日收盘价 < 昨日收盘价:
  OBV = OBV昨日 - 今日成交量
如果今日收盘价 = 昨日收盘价:
  OBV = OBV昨日
```

OBV用于判断量价关系，背离信号具有重要参考价值。

### 9. VWAP (Volume Weighted Average Price)

```
VWAP = Σ(价格 × 成交量) / Σ成交量

通常用于日内交易，价格在VWAP上方为多头市场。
```

### 10. 威廉指标 (Williams %R)

```
%R = (Hn - C) / (Hn - Ln) × (-100)

其中：
- n = 周期数（通常14）
```

信号解读：
- %R > -20: 超买
- %R < -80: 超卖

---

## 基本面数据解读

### 估值指标

#### 市盈率 (P/E Ratio)
```
P/E = 股价 / 每股收益(EPS)
```
- P/E < 行业平均: 可能被低估
- P/E > 行业平均: 可能被高估
- 需结合增长率看PEG

#### PEG Ratio
```
PEG = P/E / 盈利增长率(%)
```
- PEG < 1: 低估
- PEG = 1: 合理
- PEG > 1: 高估

#### 市净率 (P/B Ratio)
```
P/B = 股价 / 每股净资产
```
适用于资产密集型行业评估。

#### 市销率 (P/S Ratio)
```
P/S = 市值 / 营业收入
```
适用于尚未盈利的成长型公司评估。

#### EV/EBITDA
```
EV = 市值 + 净债务
EV/EBITDA = EV / EBITDA
```
不受资本结构影响，适合比较不同负债水平的公司。

### 盈利能力指标

#### ROE (Return on Equity)
```
ROE = 净利润 / 股东权益 × 100%
```
- ROE > 15%: 优秀
- ROE 10-15%: 良好
- ROE < 10%: 较差

#### ROA (Return on Assets)
```
ROA = 净利润 / 总资产 × 100%
```
衡量资产利用效率。

#### 毛利率 (Gross Margin)
```
毛利率 = (营业收入 - 营业成本) / 营业收入 × 100%
```
反映产品竞争力和定价能力。

#### 净利率 (Net Margin)
```
净利率 = 净利润 / 营业收入 × 100%
```
反映最终盈利能力。

### 成长性指标

#### 营收增长率
```
营收增长率 = (本期营收 - 上期营收) / 上期营收 × 100%
```

#### EPS增长率
```
EPS增长率 = (本期EPS - 上期EPS) / 上期EPS × 100%
```

#### CAGR (复合年增长率)
```
CAGR = (终值/初值)^(1/年数) - 1
```

### 财务健康指标

#### 资产负债率
```
资产负债率 = 总负债 / 总资产 × 100%
```
- < 50%: 低风险
- 50-70%: 中等风险
- > 70%: 高风险

#### 流动比率
```
流动比率 = 流动资产 / 流动负债
```
- > 2: 流动性好
- 1-2: 正常
- < 1: 短期偿债风险

#### 速动比率
```
速动比率 = (流动资产 - 存货) / 流动负债
```
更严格的流动性测试。

#### 利息覆盖倍数
```
利息覆盖倍数 = EBIT / 利息支出
```
- > 5: 安全
- 3-5: 正常
- < 3: 风险较高

---

## 分析框架

### 技术面评分模型

```typescript
interface TechnicalScore {
  trend: number;      // 0-100, 趋势得分
  momentum: number;   // 0-100, 动量得分
  volatility: number; // 0-100, 波动性得分
  volume: number;     // 0-100, 成交量得分
}

// 权重分配
const weights = {
  trend: 0.35,
  momentum: 0.30,
  volatility: 0.20,
  volume: 0.15
};

// 总分计算
function calculateTotalScore(scores: TechnicalScore): number {
  return (
    scores.trend * weights.trend +
    scores.momentum * weights.momentum +
    scores.volatility * weights.volatility +
    scores.volume * weights.volume
  );
}
```

### 趋势评分细则

```typescript
function scoreTrend(maAnalysis: MAAnalysis): number {
  let score = 50; // 基础分

  // 均线排列
  if (maAnalysis.arrangement === 'bullish_alignment') score += 20;
  else if (maAnalysis.arrangement === 'bearish_alignment') score -= 20;

  // 价格位置
  if (maAnalysis.price > maAnalysis.sma.sma200) score += 10;
  if (maAnalysis.price > maAnalysis.sma.sma50) score += 5;

  // 均线趋势
  if (maAnalysis.sma.sma20 > maAnalysis.sma.sma50) score += 10;
  if (maAnalysis.sma.sma50 > maAnalysis.sma.sma200) score += 5;

  return Math.max(0, Math.min(100, score));
}
```

### 动量评分细则

```typescript
function scoreMomentum(rsi: RSIAnalysis, macd: MACDAnalysis): number {
  let score = 50;

  // RSI评分
  if (rsi.rsi >= 40 && rsi.rsi <= 60) score += 10; // 中性区域
  else if (rsi.rsi > 60 && rsi.rsi <= 70) score += 15; // 偏强
  else if (rsi.rsi >= 30 && rsi.rsi < 40) score -= 5; // 偏弱
  else if (rsi.rsi > 70) score -= 10; // 超买风险
  else if (rsi.rsi < 30) score += 5; // 超卖反弹机会

  // MACD评分
  if (macd.crossover === 'golden_cross') score += 20;
  else if (macd.crossover === 'death_cross') score -= 20;
  if (macd.histogram > 0 && macd.histogram > macd.prevHistogram) score += 10;
  if (macd.histogram < 0 && macd.histogram < macd.prevHistogram) score -= 10;

  return Math.max(0, Math.min(100, score));
}
```

### 基本面评分模型

```typescript
interface FundamentalScore {
  valuation: number;     // 估值得分
  profitability: number; // 盈利能力得分
  growth: number;        // 成长性得分
  financialHealth: number; // 财务健康度得分
}

// 权重分配
const fundamentalWeights = {
  valuation: 0.25,
  profitability: 0.30,
  growth: 0.25,
  financialHealth: 0.20
};
```

### 估值评分细则

```typescript
function scoreValuation(valuation: ValuationData): number {
  let score = 50;

  // P/E相对行业
  if (valuation.pe.status === 'undervalued') score += 20;
  else if (valuation.pe.status === 'overvalued') score -= 15;
  else score += 5; // 合理

  // PEG
  if (valuation.peg < 1) score += 15;
  else if (valuation.peg > 2) score -= 10;

  // P/B
  if (valuation.pb.status === 'undervalued') score += 10;
  else if (valuation.pb.status === 'overvalued') score -= 5;

  return Math.max(0, Math.min(100, score));
}
```

### 综合评分与建议映射

```typescript
function getRecommendation(totalScore: number): Recommendation {
  if (totalScore >= 80) {
    return { grade: 'A', signal: 'strong_buy', risk: 'low' };
  } else if (totalScore >= 70) {
    return { grade: 'B+', signal: 'buy', risk: 'moderate_low' };
  } else if (totalScore >= 60) {
    return { grade: 'B', signal: 'hold', risk: 'moderate' };
  } else if (totalScore >= 50) {
    return { grade: 'C', signal: 'reduce', risk: 'moderate_high' };
  } else {
    return { grade: 'D', signal: 'sell', risk: 'high' };
  }
}
```

---

## 风险评估框架

### 风险因素清单

```typescript
interface RiskFactors {
  // 技术面风险
  technical: {
    overbought: boolean;      // RSI超买
    divergence: boolean;      // 指标背离
    breakdownRisk: boolean;   // 破位风险
    highVolatility: boolean;  // 高波动
  };

  // 基本面风险
  fundamental: {
    highValuation: boolean;   // 高估值
    decliningProfit: boolean; // 利润下滑
    highDebt: boolean;        // 高负债
    cashFlowIssues: boolean;  // 现金流问题
  };

  // 市场风险
  market: {
    sectorWeakness: boolean;  // 板块弱势
    marketDowntrend: boolean; // 大盘下跌
    lowLiquidity: boolean;    // 流动性低
  };
}

function calculateRiskLevel(factors: RiskFactors): RiskLevel {
  let riskScore = 0;

  const riskWeights = {
    technical: { overbought: 10, divergence: 15, breakdownRisk: 20, highVolatility: 10 },
    fundamental: { highValuation: 15, decliningProfit: 20, highDebt: 25, cashFlowIssues: 30 },
    market: { sectorWeakness: 15, marketDowntrend: 20, lowLiquidity: 15 }
  };

  // 计算总分
  for (const category in factors) {
    for (const factor in factors[category]) {
      if (factors[category][factor]) {
        riskScore += riskWeights[category][factor];
      }
    }
  }

  // 映射风险等级
  if (riskScore <= 20) return 'low';
  if (riskScore <= 40) return 'moderate_low';
  if (riskScore <= 60) return 'moderate';
  if (riskScore <= 80) return 'moderate_high';
  return 'high';
}
```

---

## 使用示例

### 获取完整数据流程

```typescript
async function getCompleteData(symbol: string) {
  // 1. 搜索确认股票代码
  const searchResult = await fetch(
    `${BASE_URL}/v1/markets/search?search=${symbol}`
  );

  // 2. 获取实时报价
  const quote = await fetch(
    `${BASE_URL}/v1/markets/quote?ticker=${symbol}&type=STOCKS`
  );

  // 3. 获取历史数据（用于技术分析）
  const history = await fetch(
    `${BASE_URL}/v1/markets/stock/history?symbol=${symbol}&interval=1d`
  );

  // 4. 获取财务数据
  const financialData = await fetch(
    `${BASE_URL}/v1/markets/stock/modules?ticker=${symbol}&module=financial-data`
  );

  // 5. 获取统计数据
  const statistics = await fetch(
    `${BASE_URL}/v1/markets/stock/modules?ticker=${symbol}&module=statistics`
  );

  // 6. 获取收益数据
  const earnings = await fetch(
    `${BASE_URL}/v1/markets/stock/modules?ticker=${symbol}&module=earnings`
  );

  // 7. 获取资产负债表
  const balanceSheet = await fetch(
    `${BASE_URL}/v1/markets/stock/modules?ticker=${symbol}&module=balance-sheet`
  );

  // 8. 获取现金流量表
  const cashFlow = await fetch(
    `${BASE_URL}/v1/markets/stock/modules?ticker=${symbol}&module=cashflow-statement`
  );

  // 9. 获取新闻
  const news = await fetch(
    `${BASE_URL}/v1/markets/news?ticker=${symbol}`
  );

  return {
    quote,
    history,
    financialData,
    statistics,
    earnings,
    balanceSheet,
    cashFlow,
    news
  };
}
```

---

## 附录：常用参数配置

### 技术指标默认参数

| 指标 | 默认参数 | 适用场景 |
|------|---------|---------|
| SMA | 5, 10, 20, 50, 200 | 趋势判断 |
| EMA | 12, 26 | MACD计算 |
| RSI | 14 | 超买超卖 |
| MACD | 12, 26, 9 | 趋势确认 |
| 布林带 | 20, 2 | 波动区间 |
| KDJ | 9, 3, 3 | 短期信号 |
| CCI | 20 | 周期判断 |
| ATR | 14 | 波动率 |

### 评分阈值配置

| 等级 | 分数范围 | 信号 | 风险 |
|------|---------|------|------|
| A | 80-100 | 强烈买入 | 低 |
| B+ | 70-79 | 买入 | 中低 |
| B | 60-69 | 持有 | 中 |
| C | 50-59 | 减持 | 中高 |
| D | 0-49 | 卖出 | 高 |
