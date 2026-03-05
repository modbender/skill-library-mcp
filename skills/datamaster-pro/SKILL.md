---
name: data-analysis-skill
description: 数据分析技能包 - 自动抓取、清洗、可视化、生成报告。适合数据分析师、运营人员，告别 Excel 手工操作。
version: 1.0.0
author: AI-Company
tags: [data, analysis, visualization, report, automation, 数据分析, 可视化]
license: MIT
---

# 数据分析技能包 DataMaster Pro

## 一句话介绍
自动抓取数据、智能清洗、一键可视化、生成专业报告。

## 解决什么问题？
- 数据分散：多个来源手动复制粘贴 → 一键抓取聚合
- 清洗耗时：Excel 公式搞半天 → 自动识别并清洗
- 图表难看：不会做可视化 → 一键生成专业图表
- 报告难写：不会写分析 → AI 自动生成洞察

## 功能清单
- 🌐 数据抓取：网页爬取、API 对接、数据库连接
- 🧹 数据清洗：去重、补缺、格式化、异常检测
- 📊 可视化：折线图、柱状图、饼图、热力图、散点图
- 📝 报告生成：自动生成数据分析报告（Markdown/HTML/PDF）
- 🔄 定时任务：支持定时抓取和分析

## 快速开始

### 安装
```bash
# 进入技能包目录
cd data-analysis-skill
npm install
```

### 使用命令

```bash
# 网页数据抓取
/data-fetch <URL> --selector "table.data"

# API 数据获取
/data-api <API_URL> --method GET --output data.json

# 数据清洗
/data-clean data.json --rules clean-rules.json

# 生成可视化图表
/data-viz data.csv --type bar --title "销售趋势"

# 完整分析报告
/data-report data.csv --template business --output report.md
```

### 配置示例
```json
{
  "sources": [
    {
      "type": "web",
      "url": "https://example.com/data",
      "selector": "table tbody tr",
      "schedule": "0 9 * * *"
    },
    {
      "type": "api",
      "url": "https://api.example.com/v1/data",
      "headers": {
        "Authorization": "Bearer TOKEN"
      }
    }
  ],
  "cleaning": {
    "removeDuplicates": true,
    "fillMissing": "mean",
    "normalizeColumns": ["price", "quantity"]
  },
  "visualization": {
    "defaultChartType": "bar",
    "colors": ["#4CAF50", "#2196F3", "#FF9800"],
    "width": 800,
    "height": 400
  }
}
```

## 文件结构
```
data-analysis-skill/
├── SKILL.md           # 技能定义（本文件）
├── README.md          # 产品说明
├── TUTORIAL.md        # 傻瓜式教程
├── install.bat        # 一键安装
├── run.bat            # 一键运行
├── config.json        # 配置示例
├── package.json       # 依赖管理
├── scripts/           # 核心代码
│   ├── data-fetch.js  # 数据抓取
│   ├── data-clean.js  # 数据清洗
│   ├── data-viz.js    # 可视化生成
│   └── data-report.js # 报告生成
├── templates/         # 报告模板
│   ├── business.md    # 商业报告模板
│   ├── technical.md   # 技术报告模板
│   └── weekly.md      # 周报模板
└── examples/          # 示例文件
    ├── sample-data.csv
    └── sample-report.md
```

## 核心脚本说明

### data-fetch.js - 数据抓取
支持三种数据源：
- **网页抓取**：CSS 选择器提取表格/列表数据
- **API 请求**：GET/POST 请求，支持认证
- **数据库**：MySQL/PostgreSQL/MongoDB 连接

### data-clean.js - 数据清洗
- 去重、去空值
- 格式标准化（日期、数字、文本）
- 异常值检测与处理
- 数据类型转换

### data-viz.js - 可视化
- 自动推荐最佳图表类型
- 支持自定义样式
- 输出 SVG/PNG/HTML

### data-report.js - 报告生成
- AI 驱动的数据洞察
- 多种模板可选
- 支持导出 Markdown/HTML/PDF

## 适用人群
- 数据分析师
- 运营人员
- 市场研究员
- 产品经理
- 财务人员

## 价格
- 基础版：¥99（网页抓取+基础清洗+5种图表）
- 进阶版：¥199（API对接+高级清洗+10种图表+报告模板）
- 专业版：¥299（数据库连接+AI洞察+定制模板+1对1指导）

---

*开发者：AI-Company*
*联系：通过ClawHub*