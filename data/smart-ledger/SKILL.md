---
name: smart-ledger
version: 1.0.0
description: >
  智能收支追踪器 — 通过自然语言快速记账，自动分类，生成日/周/月报告和趋势分析。
  支持中文自然语言输入("今天午饭花了35元")，数据本地JSON存储保护隐私。
  适用于个人财务管理、预算追踪和消费分析场景。
emoji: 💰
category: finance
tags:
  - finance
  - expense-tracker
  - budget
  - chinese
  - natural-language
requires:
  python: ">=3.9"
os:
  - macos
  - linux
  - windows
author: dyby99
license: MIT
---

# Smart Expense Tracker - 智能收支追踪器

通过自然语言快速记账，自动生成财务报告的智能工具。

## 功能特性

- 📝 **自然语言记账**: "今天午饭花了35元"、"收到工资8000"
- 🏷️ **智能自动分类**: 自动识别餐饮、交通、购物等分类
- 📊 **多维度报告**: 日报、周报、月报、趋势分析
- 🔒 **本地数据存储**: JSON文件存储，保护隐私
- 🌐 **中英文支持**: 支持中英文自然语言输入
- ⚠️ **消费异常检测**: 自动识别异常消费模式

## 快速开始

### 添加收支记录

```bash
# 记录支出
python scripts/expense-tracker.py add "今天午饭花了35元"
python scripts/expense-tracker.py add "昨天打车去公司28块"
python scripts/expense-tracker.py add "买衣服花了299元"

# 记录收入
python scripts/expense-tracker.py add "今天发工资8000元"
python scripts/expense-tracker.py add "收到红包200"
```

### 查看记录

```bash
# 列出最近7天记录
python scripts/expense-tracker.py list

# 列出最近30天记录
python scripts/expense-tracker.py list 30

# 只显示支出
python scripts/expense-tracker.py list 7 expense
```

### 生成报告

```bash
# 日报
python scripts/report-generator.py daily
python scripts/report-generator.py daily 2024-01-15

# 周报
python scripts/report-generator.py weekly
python scripts/report-generator.py weekly 1  # 上周

# 月报
python scripts/report-generator.py monthly
python scripts/report-generator.py monthly 1  # 上月

# 趋势分析
python scripts/report-generator.py trend 30
```

### 查看统计

```bash
# 最近30天收支摘要
python scripts/expense-tracker.py summary

# 最近90天摘要
python scripts/expense-tracker.py summary 90

# 查看分类列表
python scripts/expense-tracker.py categories
```

## 项目结构

```
smart-ledger/
├── SKILL.md                      # 本文件
├── scripts/
│   ├── expense-tracker.py       # 核心记账逻辑
│   └── report-generator.py      # 报告生成器
└── assets/
    └── categories.json          # 分类配置
```

## 数据存储

- **路径**: `~/.openclaw/workspace/data/expenses/expenses.json`
- **格式**: JSON
- **隐私**: 纯本地存储，不上传云端

数据结构:
```json
{
  "expenses": [
    {
      "id": "a1b2c3d4",
      "date": "2024-01-15",
      "type": "expense",
      "amount": 35.00,
      "category": "餐饮",
      "note": "午饭",
      "raw_text": "今天午饭花了35元",
      "created_at": "2024-01-15T12:30:00"
    }
  ],
  "categories": {
    "income": ["工资", "奖金", "投资", ...],
    "expense": ["餐饮", "交通", "购物", ...]
  }
}
```

## 自然语言支持示例

### 时间表达
- "今天..." - 今天
- "昨天..." - 昨天
- "前天..." - 前天
- "2024-01-15..." - 指定日期

### 金额表达
- "花了35元"
- "花了35块"
- "35元"
- "收入5000"

### 自动分类关键词

| 分类 | 触发关键词 |
|------|-----------|
| 餐饮 | 吃饭、午饭、晚饭、外卖、奶茶、咖啡、火锅 |
| 交通 | 地铁、公交、打车、滴滴、加油、停车、高铁 |
| 购物 | 购物、买衣服、鞋子、包包、化妆品、淘宝、京东 |
| 娱乐 | 电影、游戏、充值、会员、旅游、KTV |
| 居住 | 房租、房贷、水电、物业费、装修 |
| 工资 | 工资、薪水、发工资 |
| 奖金 | 奖金、年终奖、分红 |

## 分类配置

分类配置存储在 `assets/categories.json`，包含:

- **收入分类**: 工资、奖金、投资、兼职、红包、退款、其他收入
- **支出分类**: 餐饮、交通、购物、娱乐、居住、医疗、教育、通讯、人情、其他支出
- **预算预警**: 每个分类可设置预算阈值
- **关键词映射**: 自定义分类识别关键词

### 自定义分类

编辑 `assets/categories.json` 添加自定义分类和关键词。

## 报告类型

### 日报
- 当日收支总览
- 分类明细
- 交易记录列表

### 周报
- 本周收支总览
- 日均支出
- 每日明细
- TOP支出分类

### 月报
- 月度收支总览
- 预算执行情况
- 周度趋势
- 分类统计
- 日均支出

### 趋势分析
- 消费趋势（上升/下降/稳定）
- 异常消费检测（超过均值2倍）
- 环比变化分析
- 消费建议

## 高级用法

### 删除记录

```bash
# 删除指定ID的记录
python scripts/expense-tracker.py delete a1b2c3d4
```

### JSON格式输出

```bash
# 报告输出JSON格式（便于程序处理）
python scripts/report-generator.py monthly 0 json
```

### 批量导入

可通过直接编辑 `expenses.json` 文件实现批量导入。

## 使用建议

1. **每日记账**: 养成每天记录的习惯，可以在每天晚上花2分钟回顾当天支出
2. **及时分类**: 如果自动分类不准确，可以在备注中添加更具体的关键词
3. **定期复盘**: 每周查看周报，每月查看月报，了解自己的消费模式
4. **设置预算**: 在 `categories.json` 中为各分类设置预算预警值

## 故障排除

### 无法识别金额
- 确保金额格式正确，如 "35元"、"35块"
- 尝试明确表达："花了35元"

### 分类不准确
- 在描述中添加更多关键词，如 "淘宝买衣服" 会比 "买衣服" 更准确
- 可在 `categories.json` 中添加自定义关键词

### 数据文件损坏
- 数据文件是纯JSON，可用文本编辑器修复
- 建议定期备份 `~/.openclaw/workspace/data/expenses/expenses.json`

## 扩展开发

### 添加新的自动分类规则

编辑 `scripts/expense-tracker.py` 中的 `KEYWORD_MAPPING` 字典:

```python
KEYWORD_MAPPING = {
    # 现有规则...
    "新关键词": "目标分类",
    " another keyword": "Category Name"
}
```

### 集成其他工具

`expense-tracker.py` 可作为模块导入:

```python
from scripts.expense_tracker import ExpenseTracker

tracker = ExpenseTracker()
record = tracker.add("今天买书花了50元")
print(record)
```

## 技术规格

- **Python版本**: 3.9+
- **依赖**: 无外部依赖，仅使用标准库
- **编码**: UTF-8
- **数据格式**: JSON

## 许可证

MIT License
