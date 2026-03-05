---
name: finance-agent
description: Record company expenses and generate summary tables. Data is persisted to a CSV file on Google Drive. Supports adding expenses (date, category, amount, description), generating expense tables (CSV, Markdown), and exporting reports.
version: 1.0.0
metadata:
  openclaw:
    emoji: "💰"
    requires:
      env:
        - GDRIVE_CREDENTIALS
      bins:
        - python3
    primaryEnv: GDRIVE_CREDENTIALS
    install:
      - kind: uv
        package: pandas
        bins: []
      - kind: uv
        package: tabulate
        bins: []
---

# finance-agent

**finance-agent** 是一个用于记录公司开销并生成汇总表格的 Agent 技能。所有数据持久化到 Google Drive 的 CSV 文件中，确保数据安全可靠。

## 使用场景

当用户需要以下操作时，请调用本技能：

- 记录一笔新的公司开销（如差旅、餐饮、办公用品等）
- 查看所有开销记录的汇总表格
- 导出开销报告为 CSV 或 Markdown 格式
- 追踪特定类别的开销

## 操作说明

### 添加开销记录

调用 `add_expense` 方法，传入以下参数：

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `date` | `str` | 开销日期，格式为 `YYYY-MM-DD` | `"2026-02-28"` |
| `category` | `str` | 开销类别 | `"Travel"`, `"Meals"`, `"Office Supplies"` |
| `amount` | `float` | 开销金额 | `250.75` |
| `description` | `str` | 开销描述 | `"Flight to client meeting"` |

```python
from finance_agent import FinanceAgent

agent = FinanceAgent()
agent.add_expense('2026-02-28', 'Travel', 250.75, 'Flight to client meeting')
```

### 生成开销汇总表格

调用 `generate_expense_table` 方法，通过 `output_format` 参数指定输出格式：

| 格式 | 说明 |
|------|------|
| `"dataframe"` | 返回 Pandas DataFrame 对象（默认） |
| `"csv"` | 返回 CSV 格式字符串 |
| `"markdown"` | 返回 Markdown 格式表格字符串 |

```python
# 生成 Markdown 格式报告
markdown_table = agent.generate_expense_table(output_format='markdown')
print(markdown_table)

# 生成 CSV 格式报告
csv_data = agent.generate_expense_table(output_format='csv')
```

### 导出报告

调用 `export_report` 方法，将报告保存到指定路径：

```python
agent.export_report(output_path='expense_report.csv', output_format='csv')
```

## 数据持久化

本技能使用 CSV 文件进行数据持久化。默认情况下，数据保存在 `expense_report.csv` 文件中。

若需将数据同步到 Google Drive，请确保已正确配置 `GDRIVE_CREDENTIALS` 环境变量，并使用 Google Drive API 将 CSV 文件上传到指定目录。

## 环境变量

| 变量名 | 说明 |
|--------|------|
| `GDRIVE_CREDENTIALS` | Google Drive API 凭据文件路径（JSON 格式） |

## 文件结构

```
finance-agent/
├── SKILL.md                # 本文件，技能说明文档
├── finance_agent.py        # 技能主逻辑实现
└── expense_report.csv      # 开销数据持久化文件（示例数据）
```

## 示例输出

以下是 Markdown 格式的开销汇总表格示例：

| Date       | Category        | Amount | Description                    |
|------------|-----------------|--------|--------------------------------|
| 2026-02-27 | Office Supplies | 55.0   | Printer paper and ink          |
| 2026-02-26 | Travel          | 250.75 | Flight to client meeting       |
| 2026-02-25 | Meals           | 45.5   | Lunch with a potential partner |
