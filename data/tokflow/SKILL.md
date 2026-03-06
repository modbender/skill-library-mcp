---
name: tokflow
version: "0.5.0"
description: Token 消耗监控与优化分析工具。查询 LLM 模型用量、费用、各渠道余额、提问方式分析与优化建议。当用户询问 token 消耗、模型费用、优化建议、渠道余额、提问方式优化等问题时使用此技能。
---

# TokFlow - Token 消耗监控与优化

TokFlow 是一个本地运行的 LLM Token 消耗监控和优化平台，自动追踪 OpenClaw 中所有付费模型的使用情况，并支持**提问方式监控与优化**（v0.5.0）。

## 能力概述

- 查询总览数据（今日/本月 Token 消耗、费用、活跃模型数）
- 查看所有模型和付费渠道的详细统计
- 获取各渠道实时余额（DeepSeek、硅基流动等）
- 获取智能优化建议（模型替换、缓存优化、调用模式优化、**提问方式优化**）
- **提问方式分析**：提问轮次、平均提问长度、长度分布、预估节省
- 生成优化报告

## 使用方法

所有查询通过调用 TokFlow 的本地 API（`http://localhost:8001/api`）完成。

### 1. 查询总览

```bash
scripts/tokflow_query.py dashboard
```

返回：今日 Token 消耗、本月消耗、活跃模型数、本月费用、模型分布。

### 2. 查询所有模型

```bash
scripts/tokflow_query.py models
```

返回：所有已配置的付费模型列表，含消耗量、费用、效率评分、使用状态。

### 3. 查询渠道统计

```bash
scripts/tokflow_query.py providers
```

返回：按付费渠道分组的汇总数据（minimax / deepseek / siliconflow 等各自独立统计）。

### 4. 查询单个模型详情

```bash
scripts/tokflow_query.py model-detail <model_id> [--days 7]
```

返回：指定模型的每日趋势、调用时段分布、P95 统计等详细数据。

### 5. 查询渠道余额

```bash
scripts/tokflow_query.py balance
```

返回：各付费渠道的实时账户余额（从各平台 API 实时查询）。

### 6. 获取优化建议

```bash
scripts/tokflow_query.py suggestions
```

返回：待处理的优化建议列表，包含预估节省金额。

### 7. 生成新的优化建议

```bash
scripts/tokflow_query.py generate
```

触发优化引擎重新分析，生成最新的优化建议。

### 8. 消耗分析

```bash
scripts/tokflow_query.py analysis [--days 30]
```

返回：费用趋势、模型费用对比、环比变化、异常检测。

### 9. 提问方式统计（v0.5.0）

```bash
scripts/tokflow_query.py prompt-stats [--days 30]
```

返回：提问轮次、平均/中位提问长度、长度分桶、总费用、预估可节省金额。

## 应答格式

脚本输出 JSON 格式数据。请将数据解读为自然语言回答用户的问题。例如：

- 用户问"我这个月花了多少钱" → 调用 `dashboard`，读取 `month_cost.value`
- 用户问"哪个模型最费钱" → 调用 `models`，按 `total_cost` 排序
- 用户问"有什么优化建议" → 调用 `suggestions`
- 用户问"各渠道还剩多少钱" → 调用 `balance`

## 注意

- TokFlow 服务必须在本地 8001 端口运行
- 数据来源是 OpenClaw 本地 JSONL 会话文件，实时同步
- 费用数据直接取自 OpenClaw 原始计算值，精度到 6 位小数
