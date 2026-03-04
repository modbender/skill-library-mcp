# 且慢MCP工具完整清单

盈米且慢MCP提供72个专业金融工具，分为五大核心能力模块。

> 官方文档：https://qieman.com/mcp/tools  
> 使用指南：https://yingmi.feishu.cn/docx/PRPRds5SBo2MITxHJL2cMPminEf

## 工具调用方式

```bash
mcporter call qieman-mcp.<工具名> --args '<JSON参数>' --output json
```

---

## 一、金融数据模块

### 1.1 基金数据 - 基本信息

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `BatchGetFundsDetail` | 批量获取基金详细信息 | 查询易方达蓝筹精选基金详情 |
| `BatchGetFundNavHistory` | 批量获取基金历史净值 | 查询基金过去一年净值变化 |
| `BatchGetFundTradeRules` | 批量获取基金交易规则 | 查询申购确认日期、到账时间 |
| `BatchGetFundTradeLimit` | 批量获取基金交易限制 | 查询最低购买金额、定投起点 |
| `BatchGetFundsSplitHistory` | 批量获取基金拆分记录 | 查询基金历史拆分情况 |
| `BatchGetFundsDividendRecord` | 批量获取基金分红记录 | 查询基金历史分红情况 |
| `GuessFundCode` | 基金代码模糊匹配 | 根据基金名称匹配代码 |
| `GetFundBenchmarkInfo` | 获取基金业绩基准 | 查询基金的业绩比较基准 |

**示例：查询基金详情**
```bash
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes":["005827"]}' \
  --output json
```

### 1.2 基金数据 - 业绩表现

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetBatchFundPerformance` | 批量获取基金业绩表现 | 对比多只基金的收益和风险指标 |

**返回指标包括：**
- 阶段收益率（近一周/月/季/年/成立来）
- 风险指标（最大回撤、波动率、夏普比率）
- 同类排名

### 1.3 基金数据 - 持仓明细

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `BatchGetFundsHolding` | 批量获取基金持仓 | 查询基金的十大重仓股和重仓债 |
| `GetFundAssetClassAnalysis` | 获取基金大类资产分布 | 分析基金底层资产类型占比 |
| `GetFundIndustryAllocation` | 获取基金行业配置比例 | 查询基金在各行业的配置权重 |
| `GetFundIndustryConcentration` | 获取基金行业集中度 | 分析基金前5大行业持仓占比 |
| `getQdFundAreaAllocation` | 获取QDII基金地区配置 | 查询QDII基金的海外资产分布 |
| `getBondAllocationByFundCode` | 获取债基券种配置 | 查询债券型基金的券种风格 |
| `getStockAllocationAndMetricsByFundCode` | 获取权益基金估值指标 | 查询持仓股票的PE、ROE等 |

### 1.4 基金数据 - 持仓特征

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `fund-sector-preference` | 获取基金板块偏好 | 分析基金更偏好科技还是消费板块 |
| `fund-equity-position` | 获取基金权益仓位 | 查询基金的长期权益仓位水平 |
| `getFundTurnoverRate` | 获取基金换手率 | 判断基金经理的调仓频率 |
| `getFundIndustryPreference` | 获取基金行业偏好 | 分析基金的行业配置倾向 |

### 1.5 基金数据 - 能力评价

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `fund-recovery-ability` | 获取基金回撤修复能力 | 判断基金解套速度是否够快 |

### 1.6 基金数据 - 风险指标

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `AnalyzeFundRisk` | 基金风险分析 | 获取基金风险评分和风险来源 |
| `getBondIndicator` | 债基风险指标查询 | 查询债基的久期、杠杆、集中度 |
| `getFundDiveCount` | 获取债基异动次数 | 查询基金净值跳水次数 |
| `getBondFundCreditRatingLevel` | 获取债基信用评级 | 查询债券型基金的债券信用评级 |

### 1.7 基金数据 - 业绩归因

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `getFundIndustryReturns` | 获取基金行业收益归因 | 分析各行业对基金收益的贡献 |
| `getFundBrinsonIndicator` | 获取基金Brinson归因 | 拆解超额收益来源（配置/选股） |
| `getFundCampisiIndicator` | 获取基金Campisi归因 | 拆解债券收益来源 |
| `getMarketTimingIndicator` | 获取基金择时指标 | 分析基金经理的择时能力 |

### 1.8 基金数据 - 公告信息

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetFundAnnouncements` | 查询基金公告列表 | 获取基金季报、年报等公告 |
| `GetAnnouncementcontents` | 获取公告详细内容 | 解读基金季报中的市场观点 |

### 1.9 策略数据

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetStrategyDetails` | 获取策略详情 | 详细介绍且慢投顾策略 |
| `BatchGetStrategiesComposition` | 批量获取策略持仓 | 查询策略的最新持仓基金 |
| `BatchGetPoTradeComposition` | 获取策略交易成分 | 查询策略当前可买入的成分基金 |
| `GetStrategyBenchmark` | 获取策略业绩基准 | 查询策略的比较基准 |
| `GetStrategyRiskInfo` | 获取策略风险信息 | 查询策略风险等级和建议持有时间 |
| `BatchGetStrategyRiskInfo` | 批量获取策略风险信息 | 对比多个策略的风险等级 |
| `GetStrategyAssetClassAnalysis` | 获取策略资产分布 | 分析策略穿透后的大类资产占比 |
| `GetPortfolioNavHistory` | 获取策略历史净值 | 查询策略净值走势 |

---

## 二、投研服务模块

### 2.1 基金研究 - 基金筛选

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `SearchFunds` | 基金搜索 | 搜索名称包含"红利"的基金 |
| `GetPopularFund` | 获取热门基金 | 查看近期访问量最高的基金 |
| `filterBondFundByCreditRating` | 按信用评级筛选债基 | 筛选AAA级以上的债券基金 |
| `filterBondFundByBondType` | 按券种风格筛选债基 | 筛选国债风格债券基金 |
| `filterStockFundByStockTurnover` | 按换手率筛选股票基金 | 筛选高换手率的股票基金 |
| `getBondFundWithAlertRecord` | 查询净值异动债基 | 查询近期发生净値跳水的基金 |
| `GetFundRelatedStrategies` | 按重仓基金筛选策略 | 查找重仓某基金的投顾策略 |

**示例：搜索红利基金**
```bash
mcporter call qieman-mcp.SearchFunds \
  --args '{"keyword":"红利","limit":10,"sortBy":"oneYearReturn"}' \
  --output json
```

### 2.2 基金研究 - 基金评价

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetFundDiagnosis` | 基金诊断 | 全面分析基金的风险与机会 |

### 2.3 投前分析 - 组合模拟

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetFundsCorrelation` | 基金相关性分析 | 检查组合中基金是否高度相关 |
| `GetFundsBackTest` | 组合回测分析 | 评估投资组合的历史表现 |
| `MonteCarloSimulate` | 蒙特卡洛模拟 | 预测组合未来收益分布 |

**示例：组合回测**
```bash
mcporter call qieman-mcp.GetFundsBackTest \
  --args '{"fundCodes":["005094","320007","001003"],"weights":[0.5,0.3,0.2]}' \
  --output json
```

### 2.4 投后分析 - 持仓分析

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetAssetAllocation` | 资产配置分析 | 分析组合的大类资产分布 |
| `DiagnoseFundPortfolio` | 账户诊断 | 全面诊断基金组合的健康度 |

### 2.5 投后分析 - 风险分析

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `AnalyzePortfolioRisk` | 投后风险分析 | 评估组合整体风险水平 |

### 2.6 市场分析

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetLatestQuotations` | 市场温度计 | 查询当日市场温度和行情解读 |

---

## 三、投顾服务模块

### 3.1 投资规划

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetAssetAllocationPlan` | 获取资产配置方案 | 制定预期收益8%的配置方案 |
| `GetCompositeModel` | 获取基金投资方案 | 将资产配置方案转化为具体基金 |
| `AnalyzeInvestmentPerformance` | 投资方案表现分析 | 分析投资方案是否符合预期 |
| `StrategySearchByKeyword` | 策略关键词搜索 | 搜索名称包含"成长"的策略 |

**示例：获取资产配置方案**
```bash
mcporter call qieman-mcp.GetAssetAllocationPlan \
  --args '{"expectedAnnualReturn":0.08,"investmentPeriod":3}' \
  --output json
```

### 3.2 家庭&财务分析

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `AnalyzeFamilyMembers` | 家庭结构分析 | 分析家庭生命周期阶段 |
| `AnalyzeAssetLiability` | 资产负债分析 | 计算资产负债率、净资产等 |
| `AnalyzeIncomeExpense` | 收入支出分析 | 计算结余率、收支占比 |
| `AnalyzeFinancialIndicators` | 财务指标分析 | 评估7大财务健康指标 |
| `AnalyzeCashFlow` | 现金流分析 | 制定详细的财务规划 |

**示例：资产负债分析**
```bash
mcporter call qieman-mcp.AnalyzeAssetLiability \
  --args '{"totalAsset":5000000,"totalLiability":2000000,"monthlyIncome":30000,"monthlyExpense":10000}' \
  --output json
```

---

## 四、投顾内容模块

### 4.1 公开内容

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `SearchFinancialNews` | 财经资讯搜索 | 查询央行降息相关新闻 |
| `SearchHotTopic` | 热点话题榜单 | 了解当前市场热点 |
| `searchRealtimeAiAnalysis` | 实时资讯AI解读 | 获取AI对市场动态的解读 |

**示例：搜索财经资讯**
```bash
mcporter call qieman-mcp.SearchFinancialNews \
  --args '{"keyword":"降息","startDate":"2025-01-01","limit":10}' \
  --output json
```

### 4.2 盈米内容

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `searchInvestAdvisorContent` | 搜索投顾内容 | 获取盈米最新的市场观点 |
| `SearchManagerViewpoint` | 基金经理观点 | 查询基金经理对行业的看法 |

**示例：基金经理观点**
```bash
mcporter call qieman-mcp.SearchManagerViewpoint \
  --args '{"industry":"科技","limit":5}' \
  --output json
```

---

## 五、通用服务模块

### 5.1 常用工具

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GetCurrentTime` | 获取当前时间 | 查询当前日期时间 |
| `GetTxnDayRange` | 交易日查询 | 查询未来10个交易日 |
| `RenderEchart` | ECharts图表渲染 | 生成可视化图表 |
| `RenderHtmlToPdf` | HTML转PDF | 生成可打印的投资报告 |

**示例：交易日查询**
```bash
mcporter call qieman-mcp.GetTxnDayRange \
  --args '{"centerDate":"2025-03-01","days":10,"direction":"forward"}' \
  --output json
```

### 5.2 金融工具

| 工具名 | 功能 | 示例场景 |
|--------|------|----------|
| `GuessFundCode` | 基金代码模糊匹配 | 根据名称查找基金代码 |

---

## 工具分类索引

### 按使用场景分类

#### 查询基金信息
- `BatchGetFundsDetail` - 基金详情
- `BatchGetFundNavHistory` - 历史净值
- `GetBatchFundPerformance` - 业绩表现
- `BatchGetFundsHolding` - 持仓明细
- `GetFundDiagnosis` - 基金诊断
- `SearchFunds` - 基金搜索

#### 分析投资组合
- `GetFundsCorrelation` - 相关性分析
- `GetFundsBackTest` - 回测分析
- `DiagnoseFundPortfolio` - 组合诊断
- `GetAssetAllocation` - 资产配置分析
- `AnalyzePortfolioRisk` - 风险分析

#### 制定投资规划
- `GetAssetAllocationPlan` - 资产配置方案
- `GetCompositeModel` - 基金投资方案
- `MonteCarloSimulate` - 收益模拟
- `AnalyzeInvestmentPerformance` - 方案分析

#### 财务健康分析
- `AnalyzeFamilyMembers` - 家庭结构
- `AnalyzeAssetLiability` - 资产负债
- `AnalyzeIncomeExpense` - 收支分析
- `AnalyzeCashFlow` - 现金流规划
- `AnalyzeFinancialIndicators` - 财务指标

#### 市场研究
- `GetLatestQuotations` - 市场温度
- `SearchHotTopic` - 热点话题
- `SearchFinancialNews` - 财经资讯
- `SearchManagerViewpoint` - 基金经理观点
- `searchInvestAdvisorContent` - 投顾内容

#### 生成报告
- `RenderEchart` - 图表渲染
- `RenderHtmlToPdf` - PDF生成

### 按基金类型分类

#### 股票型/混合型基金
- `getStockAllocationAndMetricsByFundCode` - 估值指标（PE、ROE等）
- `GetFundIndustryAllocation` - 行业配置
- `getFundTurnoverRate` - 换手率

#### 债券型基金
- `getBondAllocationByFundCode` - 券种配置
- `getBondIndicator` - 风险指标（久期、杠杆）
- `getBondFundCreditRatingLevel` - 信用评级
- `filterBondFundByCreditRating` - 信用筛选
- `getFundDiveCount` - 异动监控

#### QDII基金
- `getQdFundAreaAllocation` - 地区配置

---

## 调用限制

- 单次批量查询最多10只基金
- 建议使用 `--output json` 参数获取结构化数据
- 部分工具支持分页查询，使用 `limit` 和 `offset` 参数

## 错误处理

常见错误码：
- `400` - 参数错误，检查JSON格式
- `401` - API Key无效或过期
- `429` - 请求频率过高
- `500` - 服务端错误

---

> 文档更新日期：2025-03-01  
> 工具数量：72个  
> 官方文档：https://qieman.com/mcp/tools