---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5f99537637ec8a7284fc6db453befbf1
    PropagateID: 5f99537637ec8a7284fc6db453befbf1
    ReservedCode1: 30450220459a060a3cd402aa1efd0cedaa919091eac38669a1a684f23a3d11e0bbeefab40221009d2ccb1970d6f6ae56965fa89c64a5ce991462be3af54aa3d944f723b80579d9
    ReservedCode2: 3045022072c8a10b604befe2a48fdea3a89439bc7ff3b660ddfa39531dcf9376f3bf2691022100e64cbce383db99fd25a2ea80b7484bbb9e579a3627ad9fc3d5daab163557d93e
description: 多智能体A股深度研究框架。当用户要求分析A股上市公司、产业链研究、个股深度报告、行业比较、投资价值评估时激活。支持：单只股票全面分析（财务/新闻/情绪/技术/风险）、多智能体辩论（看涨vs看跌）、产业链上下游拆解、事实核查、Dashboard部署。数据来源：akshare（A股/港股）、yfinance（美股）、网络搜索（研报/新闻）。适合A股投资者、量化研究员、产业链分析师。
name: astock-multiagent-research
---

# 多智能体A股研究框架

## 快速启动

**单只股票分析**：
```
用户: "帮我研究 600519 茅台" / "分析润泽科技300442" / "中际旭创值得买吗"
```
→ 触发完整6步工作流（见下）

**产业链分析**：
```
用户: "分析AI算力产业链" / "商业航天产业链哪个环节最值得关注"
```
→ 读取 `references/industry-chain.md`，触发产业链专项框架

**快速概览**（仅基本面+新闻）：
```
用户: "给我简单看下000977浪潮信息最近怎样"
```
→ 仅启动 fundamentals_analyst + news_analyst 两个子智能体

---

## 工作流（完整6步）

### Step 1：多维并行数据收集

同时启动4个子智能体（使用 `sessions_spawn`）：

| 子智能体 | 任务 | 参考提示词 |
|---------|------|-----------|
| `fundamentals_analyst` | 财务报表深度分析、估值、机构预测 | `references/agent-prompts.md#fundamentals` |
| `news_analyst` | 公司动态、行业新闻、政策 | `references/agent-prompts.md#news` |
| `sentiment_analyst` | 市场情绪、研报评级变化 | `references/agent-prompts.md#sentiment` |
| `technical_analyst` | 价格走势、成交量、关键位 | `references/agent-prompts.md#technical` |

### Step 2：观点碰撞

基于Step1报告，并行启动：
- `bullish_researcher`：挖掘增长潜力、竞争优势、价值低估
- `bearish_researcher`：识别风险、业绩隐忧、估值泡沫

### Step 3：风险评估
- `risk_manager`：综合投资风险评估（行业/财务/流动性/政策）

### Step 4：事实核查
- `fact_checker`：对关键数据和说法二次验证

### Step 5：综合报告
按 `references/report-template.md` 格式输出完整研究报告

### Step 6：Dashboard部署
将报告渲染为交互式HTML Dashboard，使用 `deploy` 工具部署，返回可访问链接

---

## 数据获取（Python/akshare）

运行 `scripts/fetch_stock_data.py <股票代码>` 获取基础数据包。

```python
# 手动调用示例
import akshare as ak

# 公司基本信息（A股）
info = ak.stock_individual_info_em(symbol="300442")

# 三大财务报表
balance = ak.stock_balance_sheet_by_report_em(symbol="300442")
income = ak.stock_profit_sheet_by_report_em(symbol="300442")
cashflow = ak.stock_cash_flow_sheet_by_report_em(symbol="300442")

# 财务指标（ROE/毛利率等）
indicator = ak.stock_financial_analysis_indicator(symbol="300442")

# 机构持仓
fund_hold = ak.stock_report_fund_hold(symbol="300442")

# 美股
import yfinance as yf
ticker = yf.Ticker("AAPL")
info = ticker.info
```

子代码格式：沪市6开头用"6xxxxx"，深市/创业板用"0xxxxx"/"3xxxxx"，北交所用"8xxxxx"。

---

## 输出规范

详见 `references/report-template.md`。核心结构：
- 研究摘要（公司定位、行业地位、当前估值）
- 财务分析表格（营收/净利润/毛利率/ROE，含同比和行业对比）
- 估值分析（PE/PB/PS历史分位）
- 机构观点（评级分布、目标价区间）
- 核心竞争力 vs 风险因素
- 综合评级：🟢高 / 🟡中等 / 🔴低

---

## 注意事项

- akshare股票代码不含市场前缀（用"300442"而非"sz300442"）
- 数据来源声明：akshare/东方财富/同花顺/公司公告
- 免责声明必须包含在每份报告末尾
- 产业链分析见 `references/industry-chain.md`
