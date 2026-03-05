---
name: daily-market-insight
description: "每日市场洞察报告生成系统。使用多Agent协作：新闻采集→分析→市场趋势预测→飞书文档报告。每天10:00自动运行。"
metadata:
  openclaw:
    emoji: "📊"
    schedule: "0 10 * * *"
    requires: ["web_search", "web_fetch", "feishu_doc"]
---

# 每日市场洞察 - 多Agent系统

## 工作流程

当触发此技能时，按以下步骤执行：

### Step 1: 新闻采集 🔍

使用 `web_search` 搜索以下领域的最新新闻：

**宏观经济（重点）:**
- query: "中国经济 宏观政策 今日"
- query: "美联储 利率决议 最新"
- query: "央行 货币政策 降准降息"

**科技行业（重点）:**
- query: "人工智能 AI 行业动态 今日"
- query: "半导体芯片 行业新闻 最新"
- query: "新能源汽车 行业动态"

**其他领域:**
- query: "地缘政治 国际形势 最新"
- query: "大宗商品 原油 黄金 行情"

每类搜索取前3-5条，使用 `web_fetch` 获取详细内容。

### Step 2: 新闻分析 📊

将采集的新闻整理成结构化数据，调用 **opencode sisyphus** 进行分析：

```bash
opencode run --agent sisyphus "分析以下财经新闻..."
```

要求输出：
- 每条新闻的核心要点
- 市场情感判断（正面/中性/负面）
- 影响程度评估（高/中/低）
- 相关板块/市场

### Step 3: 市场趋势预测 🔮

基于新闻分析结果，调用 **opencode sisyphus** 进行预测：

针对 A股、港股、美股 分别分析：
- 短期趋势（1-2周）
- 中期趋势（1-3月）
- 重点关注的板块
- 风险提示
- 投资建议

### Step 4: 报告生成 📝

生成完整的 Markdown 报告，包含：
- 日期标题
- 新闻分析摘要
- 市场趋势预测
- 数据表格（如有）

### Step 5: 推送到飞书 📤

1. 使用 `feishu_doc` 创建新文档，标题：「每日市场洞察 - YYYY-MM-DD」
2. 将报告内容写入文档
3. 在当前飞书群发送消息：「✅ 今日市场洞察报告已生成！」

---

## 数据存储

- 本地报告：`~/.openclaw/workspace/projects/daily-market-insight/data/`
- 日志：`~/.openclaw/workspace/projects/daily-market-insight/logs/`

## 注意事项

1. opencode 需要 git 目录才能运行，先在目标目录执行 `git init`
2. 新闻采集使用免费渠道，数量有限制
3. 分析结果仅供参考，不构成投资建议
