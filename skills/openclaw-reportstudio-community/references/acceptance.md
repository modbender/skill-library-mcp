# 验收清单（OpenClaw skill：openclaw-reportstudio-community）

目标：确保 skill 在“自然语言触发”的情况下，稳定地产出 **xlsx + pdf + pptx**，并且遵守社区版安全边界。

## A. 前置检查

- ReportStudio 本体可运行（在同机 python 环境中可 import / 可执行）。
- 输入文件为 CSV 或 XLSX，路径可读。

建议先在命令行确认一次：

```bash
python -m reportstudio.cli.main --help
```

## B. 自然语言触发（核心验收）

用一段自然语言指令（含文件路径 + 产物要求），例如：

- “用 `./data.xlsx` 生成月报，输出到 `./artifacts`，要 xlsx+pdf+pptx。”
- “用 `sales.csv` 做周报，趋势按 week，拆解维度用 region，指标用 revenue。”

验收点：
1) agent 能自动抽取关键参数：file/prompt/out-dir/formats/grain/dim/measure/topn/time-range
2) 最终运行 ReportStudio 后，返回的 JSON 至少包含：
   - `artifacts[]`（path 存在）
   - `warnings[]`
   - `tables.trend[]` 与 `tables.breakdowns[]`（当 schema 支持时）
   - `meta.kpis`、`meta.grain`

## C. 导出物验收

- XLSX：存在 `Summary/Trend/Breakdowns` sheet
- PPTX：5 张 slide（封面/KPI/趋势/拆解/风险建议）
- PDF：包含 cover + KPI + trend + breakdown + warnings/actions 等结构页面（近似 6 页）

## D. 大数据治理验收

构造 >= 6001 行的日粒度趋势数据，运行后必须满足：
- `warnings` 包含趋势截断提示：
  - `Trend table: exported first 5000 rows (truncated from N).`
- XLSX Trend sheet 顶部包含 NOTE（明确截断）

## E. 安全边界验收

- 输入源文件不被修改（mtime/sha 不变）
- 不做外网请求也可运行
- 不导出 raw 明细 dump（XLSX 只含聚合）

## F. 常见失败模式

- 没有 date 列：趋势/环比会跳过，warnings 必须明确说明
- 没有 numeric 列：KPI/拆解会跳过，warnings 必须明确说明
- previous=0 / total change=0：delta/share 计算会跳过并 warnings
