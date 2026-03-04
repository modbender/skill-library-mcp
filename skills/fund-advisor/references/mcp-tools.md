# qieman-mcp 工具文档

## 概述

qieman-mcp 是基金投资工具包，提供基金、内容、投研、投顾等专业领域能力。

通过 mcporter CLI 调用：

```bash
mcporter call qieman-mcp.<tool_name> --args '<json_args>' --output json
```

> **完整工具清单**：72个工具详见 [mcp-tools-full.md](./mcp-tools-full.md)

## 常用工具

### BatchGetFundsDetail

批量获取基金详细信息

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCodes | string[] | 是 | 基金代码数组，最多10个 |

**返回：**

```json
[
  {
    "fundCode": "004137",
    "data": {
      "summary": {
        "fundCode": "004137",
        "fundName": "华夏全球精选",
        "fundInvestType": "QDII",
        "risk5Level": 4,
        "nav": "1.234",
        "navDate": "2024年01月15日",
        "netAsset": "12.34亿",
        "setupDate": 1234567890000,
        "yearlyRoe": "2.34%",
        "oneYearReturn": "12.34%",
        "setupDayReturn": "123.45%"
      },
      "managers": [
        {
          "fundManagerName": "张三"
        }
      ],
      "assetPortfolios": [
        {"name": "股票", "ratio": "90.00%"},
        {"name": "债券", "ratio": "5.00%"},
        {"name": "现金", "ratio": "5.00%"}
      ]
    }
  }
]
```

**示例：**

```bash
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes": ["004137", "000001"]}' \
  --output json
```

### BatchGetFundsHolding

批量获取基金持仓情况

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCodes | string[] | 是 | 基金代码数组，最多10个 |
| fundReportDate | int | 否 | 报告日期，格式如 20240630 |

**返回：**

```json
[
  {
    "fundCode": "004137",
    "data": {
      "fundCode": "004137",
      "reportDate": "2024年06月30日",
      "stockInvestRatio": "90.00%",
      "bondInvestRatio": "5.00%",
      "stockInvests": [
        {
          "code": "AAPL",
          "name": "苹果公司",
          "ratio": "5.00%",
          "amount": "0.50亿"
        }
      ],
      "bondInvests": [
        {
          "code": "123456",
          "name": "国债",
          "ratio": "2.00%",
          "amount": "0.20亿"
        }
      ]
    }
  }
]
```

**示例：**

```bash
mcporter call qieman-mcp.BatchGetFundsHolding \
  --args '{"fundCodes": ["004137"]}' \
  --output json
```

### SearchFunds

基金搜索

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| fundType | string | 否 | 基金类型 |
| sortBy | string | 否 | 排序字段 |
| limit | int | 否 | 返回数量 |

**示例：**

```bash
mcporter call qieman-mcp.SearchFunds \
  --args '{"keyword": "红利", "limit": 10}' \
  --output json
```

### GetFundDiagnosis

基金诊断

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCode | string | 是 | 基金代码 |

**示例：**

```bash
mcporter call qieman-mcp.GetFundDiagnosis \
  --args '{"fundCode": "005827"}' \
  --output json
```

### GetFundsCorrelation

基金相关性分析

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCodes | string[] | 是 | 基金代码数组 |

**示例：**

```bash
mcporter call qieman-mcp.GetFundsCorrelation \
  --args '{"fundCodes": ["005827", "000001"]}' \
  --output json
```

### GetFundsBackTest

组合回测分析

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| fundCodes | string[] | 是 | 基金代码数组 |
| weights | number[] | 否 | 权重数组 |

**示例：**

```bash
mcporter call qieman-mcp.GetFundsBackTest \
  --args '{"fundCodes": ["005094", "320007"], "weights": [0.5, 0.5]}' \
  --output json
```

### DiagnoseFundPortfolio

账户诊断

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| holdings | array | 是 | 持仓列表，包含fundCode和amount或weight |

**示例：**

```bash
mcporter call qieman-mcp.DiagnoseFundPortfolio \
  --args '{"holdings": [{"fundCode": "005094", "weight": 0.47}, {"fundCode": "320007", "weight": 0.23}]}' \
  --output json
```

### GetAssetAllocationPlan

获取资产配置方案

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| expectedAnnualReturn | number | 否 | 预期年化收益率 |
| expectedMaxDrawdown | number | 否 | 预期最大回撤 |
| investmentPeriod | number | 否 | 投资期限(年) |

**示例：**

```bash
mcporter call qieman-mcp.GetAssetAllocationPlan \
  --args '{"expectedAnnualReturn": 0.08, "investmentPeriod": 3}' \
  --output json
```

### AnalyzeAssetLiability

资产负债分析

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| totalAsset | number | 是 | 总资产 |
| totalLiability | number | 是 | 总负债 |

**示例：**

```bash
mcporter call qieman-mcp.AnalyzeAssetLiability \
  --args '{"totalAsset": 5000000, "totalLiability": 2000000}' \
  --output json
```

## 调用限制

- 单次最多查询 10 只基金
- 超过限制需分批处理