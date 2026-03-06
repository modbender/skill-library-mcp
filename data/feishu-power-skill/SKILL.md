---
name: feishu-power-skill
description: 飞书深度自动化 Skill。多维表格批量操作、跨表关联查询、模板化文档生成、零售运营审计、定时报告调度。触发词：飞书自动化、bitable批量、多维表格、飞书报告、跨表查询、数据快照、门店审计、运营诊断、定时报告、报告调度。
version: 1.0.0
author: ivz
license: MIT
platforms:
  - openclaw
  - claude-code
dependencies:
  - requests
  - pyyaml
---

# Feishu Power Skill

让 AI agent 像飞书重度用户一样操作飞书。不只是读写文档，而是跨文档工作流 + 多维表格自动化 + 智能报告生成 + 零售运营审计。

## 安装

```bash
# 自动安装（推荐）
bash install.sh

# 手动安装
pip install requests pyyaml
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
```

## 模块

### 1. Bitable 自动化引擎 (`bitable_engine.py`)

多维表格的瑞士军刀：批量读写、跨表 JOIN、快照备份、统计分析。

```bash
# 批量创建记录
python3 scripts/bitable_engine.py batch-create --app <app_token> --table <table_id> --data records.json

# 批量更新
python3 scripts/bitable_engine.py batch-update --app <app_token> --table <table_id> --data updates.json

# 跨表 JOIN（两张表按字段关联）
python3 scripts/bitable_engine.py join --app <app_token> --left <table1> --right <table2> --on "字段名"

# 数据快照（备份当前状态）
python3 scripts/bitable_engine.py snapshot --app <app_token> --table <table_id> --output snapshots/

# 统计摘要
python3 scripts/bitable_engine.py stats --app <app_token> --table <table_id>

# CSV 导入
python3 scripts/bitable_engine.py import-csv --app <app_token> --table <table_id> --file data.csv
```

### 2. 文档工作流引擎 (`doc_workflow.py`)

Bitable 数据 + 模板 → 飞书文档，一步到位。

```bash
# 从 Bitable 数据 + 模板 → 飞书文档
python3 scripts/doc_workflow.py generate \
  --app <app_token> --table <table_id> \
  --template templates/data_summary.md \
  --title "周报标题" \
  --group-by "分类字段" \
  --local output.md

# 纯模板渲染（不创建飞书文档）
python3 scripts/doc_workflow.py render --template templates/weekly_report.md --context data.json

# 提取 Bitable 上下文（调试用）
python3 scripts/doc_workflow.py context --app <app_token> --table <table_id>
```

模板语法：
- `{{变量}}` — 简单替换（支持中文字段名、点号路径如 `{{门店.名称}}`）
- `{{#each 列表}}...{{/each}}` — 循环
- `{{#if 条件}}...{{/if}}` — 条件
- 内置变量：`{{TODAY}}` `{{YESTERDAY}}` `{{WEEK_START}}` `{{WEEK_END}}` `{{NOW}}`

### 3. 零售运营审计引擎 (`retail_audit.py`)

YAML 配置化审计规则，门店健康评分，异常自动诊断。

```bash
# Demo 模式（50家模拟门店，快速体验）
python3 scripts/retail_audit.py demo --output report.md
python3 scripts/retail_audit.py demo --publish  # 直接发布到飞书

# 从 Bitable 真实数据审计
python3 scripts/retail_audit.py audit \
  --app <app_token> --sales-table <table_id> \
  --config configs/retail_default.yaml \
  --publish

# 查看可用行业配置
python3 scripts/retail_audit.py list-configs
```

审计规则（YAML 配置化，可按行业切换）：
- 售罄率过高/过低
- 目标达成率不足
- 负库存 / 零销售
- 库存周转过慢
- 动销率过低

内置配置：`configs/retail_default.yaml`（服装）、`configs/fmcg.yaml`（快消）。复制一份改阈值即可适配其他行业。

### 4. 定时报告生成器 (`report_generator.py`)

调度引擎：支持日/周/月频率，YAML 配置任务列表，自动跟踪执行状态。

```bash
# 运行所有到期任务
python3 scripts/report_generator.py run --schedule configs/schedule.yaml

# 运行指定任务
python3 scripts/report_generator.py run --schedule configs/schedule.yaml --job daily_audit

# 强制运行（忽略调度时间）
python3 scripts/report_generator.py run --schedule configs/schedule.yaml --job daily_audit --force

# 列出所有任务及状态
python3 scripts/report_generator.py list --schedule configs/schedule.yaml

# 单次审计报告（不需要调度配置）
python3 scripts/report_generator.py audit --demo --output report.md

# 单次模板报告
python3 scripts/report_generator.py template --app <token> --table <id> --template <path> --publish
```

调度配置示例（`configs/schedule.yaml`）：

```yaml
jobs:
  - id: daily_audit
    name: 每日门店审计
    type: audit
    enabled: true
    schedule:
      frequency: daily    # daily / weekly / monthly
      time: "09:00"
    params:
      app_token: YOUR_APP_TOKEN
      sales_table: YOUR_TABLE_ID
      config: retail_default.yaml
      publish: true
```

支持的报告类型：`audit`（审计报告）、`template`（模板报告）。

### 5. API 封装层 (`feishu_api.py`)

Token 自动管理 + Bitable / Docx / Wiki / Drive 全覆盖。其他模块的底层依赖。

也可以在 Python 中直接 import：

```python
import sys; sys.path.insert(0, "scripts")
import feishu_api as api
records = api.bitable_list_all_records(app_token, table_id)
```

## 项目结构

```
feishu-power-skill/
├── SKILL.md                 # OpenClaw 入口
├── CLAUDE.md                # Claude Code 入口
├── README.md                # GitHub README
├── install.sh               # 安装脚本
├── scripts/
│   ├── feishu_api.py        # 飞书 API 封装
│   ├── bitable_engine.py    # 多维表格引擎
│   ├── doc_workflow.py      # 文档工作流
│   ├── retail_audit.py      # 零售审计引擎
│   └── report_generator.py  # 定时报告生成器
├── templates/               # 文档模板
│   ├── weekly_report.md
│   └── data_summary.md
└── configs/                 # 配置文件
    ├── retail_default.yaml  # 服装行业审计规则
    ├── fmcg.yaml            # 快消行业审计规则
    └── schedule.yaml        # 报告调度配置
```

## 依赖

- Python 3.11+
- requests, pyyaml
- 飞书应用凭证（通过 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 环境变量）

## 测试 Bitable

`J2ehbrIvwaM4XXsjoeQckftAnNe` — 内置测试表，可用于验证功能。
