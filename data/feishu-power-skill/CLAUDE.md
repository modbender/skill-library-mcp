# Feishu Power Skill

飞书深度自动化工具集。多维表格批量操作、跨表关联、模板化文档生成、零售运营审计。

## 环境变量（必须）

```bash
export FEISHU_APP_ID=cli_xxx
export FEISHU_APP_SECRET=xxx
```

## 脚本位置

所有脚本在 `scripts/` 目录下，相对于本文件所在目录。

## 能力一览

### 1. Bitable 自动化（bitable_engine.py）

```bash
# 批量创建
python3 scripts/bitable_engine.py batch-create --app <app_token> --table <table_id> --data records.json

# 跨表 JOIN
python3 scripts/bitable_engine.py join --app <app_token> --left <table1> --right <table2> --on "字段名"

# 统计摘要
python3 scripts/bitable_engine.py stats --app <app_token> --table <table_id>

# 数据快照
python3 scripts/bitable_engine.py snapshot --app <app_token> --table <table_id> --output snapshots/
```

### 2. 文档工作流（doc_workflow.py）

```bash
# Bitable 数据 → 模板渲染 → 飞书文档（一步到位）
python3 scripts/doc_workflow.py generate \
  --app <app_token> --table <table_id> \
  --template templates/data_summary.md \
  --title "报告标题" --group-by "分类字段"

# 纯模板渲染（不创建飞书文档）
python3 scripts/doc_workflow.py render --template templates/weekly_report.md --context data.json

# 提取 Bitable 上下文（调试）
python3 scripts/doc_workflow.py context --app <app_token> --table <table_id>
```

模板语法：`{{变量}}` `{{#each list}}...{{/each}}` `{{#if flag}}...{{/if}}` `{{TODAY}}` `{{NOW}}`

### 3. 零售运营审计（retail_audit.py）

```bash
# Demo（50家模拟门店）
python3 scripts/retail_audit.py demo --output report.md

# 真实数据审计 + 发布飞书
python3 scripts/retail_audit.py audit \
  --app <app_token> --sales-table <table_id> \
  --config configs/retail_default.yaml --publish

# 查看可用行业配置
python3 scripts/retail_audit.py list-configs
```

审计规则 YAML 配置化，内置：`configs/retail_default.yaml`（服装）、`configs/fmcg.yaml`（快消）

### 4. API 封装层（feishu_api.py）

底层依赖，其他模块自动调用。Token 自动缓存刷新，覆盖 Bitable/Docx/Wiki/Drive 全部 API。

也可以在 Python 中直接 import：

```python
import sys; sys.path.insert(0, "scripts")
import feishu_api as api
records = api.bitable_list_all_records(app_token, table_id)
```

### 5. 定时报告（report_generator.py）

```bash
# 运行所有到期任务
python3 scripts/report_generator.py run --schedule configs/schedule.yaml

# 运行指定任务（强制）
python3 scripts/report_generator.py run --schedule configs/schedule.yaml --job daily_audit --force

# 列出任务状态
python3 scripts/report_generator.py list --schedule configs/schedule.yaml

# 单次审计报告
python3 scripts/report_generator.py audit --demo --output report.md

# 单次模板报告
python3 scripts/report_generator.py template --app <token> --table <id> --template <path> --publish
```

调度配置：`configs/schedule.yaml`，支持 daily/weekly/monthly 频率。

## 依赖

```bash
pip install requests pyyaml
```
