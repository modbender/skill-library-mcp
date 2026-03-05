# DataMaster Pro - 数据分析技能包

> 自动抓取、智能清洗、一键可视化、生成专业报告

## 🎯 产品定位

专为数据分析师、运营人员打造的自动化数据分析工具包。告别重复的 Excel 操作，让数据分析从小时级变成分钟级。

## ✨ 核心功能

### 1. 数据抓取 (Data Fetch)

```bash
# 网页表格抓取
node scripts/data-fetch.js --url "https://example.com/data" --selector "table.data"

# API 数据获取
node scripts/data-fetch.js --api "https://api.example.com/v1/data" --method GET

# 数据库连接
node scripts/data-fetch.js --db mysql://user:pass@host/db --query "SELECT * FROM sales"
```

支持的数据源：
- ✅ 网页表格/列表
- ✅ REST API
- ✅ MySQL / PostgreSQL / MongoDB
- ✅ CSV / JSON / Excel 文件

### 2. 数据清洗 (Data Clean)

```bash
# 自动清洗
node scripts/data-clean.js --input data.json --output clean.csv

# 使用清洗规则
node scripts/data-clean.js --input data.json --rules clean-rules.json
```

清洗功能：
- 去重（按指定列）
- 空值处理（删除/填充/插值）
- 格式标准化（日期、货币、百分比）
- 异常值检测（IQR/Z-score）
- 数据类型转换

### 3. 数据可视化 (Data Viz)

```bash
# 生成柱状图
node scripts/data-viz.js --input data.csv --type bar --output chart.png

# 生成多图
node scripts/data-viz.js --input data.csv --type line,bar,pie --output charts/
```

支持的图表类型：
- 📊 柱状图（Bar）
- 📈 折线图（Line）
- 🥧 饼图（Pie）
- 📉 面积图（Area）
- 🔵 散点图（Scatter）
- 🔥 热力图（Heatmap）
- 📉 箱线图（Box Plot）

### 4. 报告生成 (Data Report)

```bash
# 生成 Markdown 报告
node scripts/data-report.js --input data.csv --template business --output report.md

# 生成 HTML 报告
node scripts/data-report.js --input data.csv --template weekly --output report.html
```

报告模板：
- `business` - 商业分析报告
- `technical` - 技术数据报告
- `weekly` - 周报模板
- `custom` - 自定义模板

## 📦 安装

### 方式一：一键安装
```bash
install.bat
```

### 方式二：手动安装
```bash
cd data-analysis-skill
npm install
```

## 🚀 快速开始

### 完整流程示例

```bash
# 1. 抓取数据
node scripts/data-fetch.js --url "https://example.com/sales" --selector "table" --output raw.json

# 2. 清洗数据
node scripts/data-clean.js --input raw.json --output clean.csv

# 3. 生成可视化
node scripts/data-viz.js --input clean.csv --type bar,line --output charts/

# 4. 生成报告
node scripts/data-report.js --input clean.csv --template business --output report.md
```

### 一键运行
```bash
run.bat
```

## 📁 文件结构

```
data-analysis-skill/
├── SKILL.md           # 技能定义
├── README.md          # 产品说明（本文件）
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
└── examples/          # 示例文件
```

## ⚙️ 配置说明

编辑 `config.json` 进行配置：

```json
{
  "sources": [
    {
      "type": "web",
      "url": "https://example.com/data",
      "selector": "table tbody tr",
      "schedule": "0 9 * * *"
    }
  ],
  "cleaning": {
    "removeDuplicates": true,
    "fillMissing": "mean",
    "detectOutliers": true
  },
  "visualization": {
    "defaultChartType": "bar",
    "colors": ["#4CAF50", "#2196F3"],
    "width": 800,
    "height": 400
  },
  "report": {
    "template": "business",
    "includeCharts": true,
    "aiInsights": true
  }
}
```

## 🔧 高级用法

### 定时任务
```bash
# 每天早上9点抓取数据
node scripts/data-fetch.js --schedule "0 9 * * *"
```

### 批量处理
```bash
# 批量处理多个URL
node scripts/data-fetch.js --batch urls.txt
```

### 自定义清洗规则
```json
{
  "rules": [
    {"column": "price", "type": "number", "decimals": 2},
    {"column": "date", "type": "date", "format": "YYYY-MM-DD"},
    {"column": "name", "type": "string", "trim": true}
  ]
}
```

## 📊 使用案例

### 案例1：电商销售数据分析
```bash
# 抓取店铺销售数据
node scripts/data-fetch.js --api "https://shop.example.com/api/sales" --output sales.json

# 清洗并分析
node scripts/data-clean.js --input sales.json --output clean.csv
node scripts/data-report.js --input clean.csv --template business
```

### 案例2：竞品监控报告
```bash
# 抓取竞品价格
node scripts/data-fetch.js --url "https://competitor.example.com/prices" --selector ".price-table"

# 生成对比报告
node scripts/data-report.js --input prices.csv --template competitive
```

### 案例3：周报自动化
```bash
# 设置定时任务，每周一生成周报
node scripts/data-report.js --input weekly.csv --template weekly --schedule "0 9 * * 1"
```

## 🛡️ 注意事项

1. **合规使用** - 仅抓取公开、允许抓取的数据
2. **API 限制** - 注意 API 调用频率限制
3. **数据安全** - 敏感数据请使用环境变量
4. **版权问题** - 生成的报告请自行审核

## 💰 价格

| 版本 | 价格 | 功能 |
|------|------|------|
| 基础版 | ¥99 | 网页抓取 + 基础清洗 + 5种图表 |
| 进阶版 | ¥199 | API对接 + 高级清洗 + 10种图表 + 报告模板 |
| 专业版 | ¥299 | 数据库连接 + AI洞察 + 定制模板 + 1对1指导 |

## 🆘 常见问题

**Q: 支持哪些数据格式？**
A: 支持 CSV、JSON、Excel、XML 等常见格式。

**Q: 可以抓取需要登录的网站吗？**
A: 进阶版及以上支持 Cookie 认证和 Headers 设置。

**Q: 报告可以导出什么格式？**
A: 支持 Markdown、HTML、PDF 格式。

**Q: 有使用限制吗？**
A: 无限制，一次购买永久使用。

---

*开发者：AI-Company*
*版本：1.0.0*
*联系：通过ClawHub*