# Bazi Calendar Schema

## Data Source File

- 默认文件：`assets/bazi_daily_calendar_2026.xlsx`
- 用途：作为 `bazi_daily_calendar` 内置表的 2026 年导入源
- 建议：部署前先完成一次全量导入，之后按日增量补齐
- SQL 产物：`assets/bazi_daily_calendar_2026.sql`（由导入脚本生成）
- 导入脚本：`scripts/import_bazi_calendar.py`

## Import Mapping

将 Excel 列映射为内置表字段（若原始表头不同，按语义映射）：

- 日期列 -> `date`（统一转换为 `YYYY-MM-DD`）
- 流年列 -> `flow_year`
- 流月列 -> `flow_month`
- 流日列 -> `flow_day`

导入约束：

- `date` 唯一，不允许重复日期记录
- 空值行在导入前过滤
- 导入后至少抽样校验首日、月切换日、年末三类日期

脚本生成示例：

```bash
python scripts/import_bazi_calendar.py \
  --input assets/bazi_daily_calendar_2026.xlsx \
  --output assets/bazi_daily_calendar_2026.sql \
  --table bazi_daily_calendar
```

使用本技能时，日历流运数据表至少应包含以下字段：

- `table_name`：`bazi_daily_calendar`（OpenClaw 内置表，逻辑名）
- `date`：公历日期，格式 `YYYY-MM-DD`（主键或唯一键）
- `flow_year`：当日对应流年（示例：`乙巳`）
- `flow_month`：当日对应流月（示例：`丁卯`）
- `flow_day`：当日对应流日（示例：`辛亥`）

可选增强字段：

- `term`：节气
- `notes`：人工备注
- `source`：数据来源
- `updated_at`：更新时间

## Query Contract

输入：
- 用户本地日期 `today_local`（`YYYY-MM-DD`）

输出：
- `flow_year`
- `flow_month`
- `flow_day`

查询无结果时：
- 返回空结果并触发上层“缺失数据”分支，不允许回填或猜测。

## Canonical Query Example

```sql
SELECT flow_year, flow_month, flow_day
FROM bazi_daily_calendar
WHERE date = :today_local
LIMIT 1;
```

## Constraints

- 必须按用户本地时区计算 `today_local` 后再查询。
- 若 `user_timezone` 缺失，回退 `Asia/Shanghai` 并打日志 `timezone_fallback=true`。
- 查询未命中时只返回空，不允许推断补写。
- 每次运势分析前必须执行一次 `date=today_local` 的查询；未查询不得输出分析结论。
