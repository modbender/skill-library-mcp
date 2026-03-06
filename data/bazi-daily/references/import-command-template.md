# Import Command Template

先在 skill 根目录生成 SQL：

```bash
python scripts/import_bazi_calendar.py \
  --input assets/bazi_daily_calendar_2026.xlsx \
  --output assets/bazi_daily_calendar_2026.sql \
  --table bazi_daily_calendar
```

## OpenClaw 内置表导入（模板）

将 `<OPENCLAW_DB_EXEC>` 替换为你环境中的数据库执行命令。

```bash
<OPENCLAW_DB_EXEC> < assets/bazi_daily_calendar_2026.sql
```

常见等价形式：

```bash
cat assets/bazi_daily_calendar_2026.sql | <OPENCLAW_DB_EXEC>
```

## SQLite 回退模板（本地验证）

如果你的 OpenClaw 内置表底层是 SQLite，可先用本地方式验数：

```bash
sqlite3 /path/to/openclaw.db < assets/bazi_daily_calendar_2026.sql
```

验数示例：

```bash
sqlite3 /path/to/openclaw.db \
  "SELECT COUNT(*) FROM bazi_daily_calendar; \
   SELECT MIN(date), MAX(date) FROM bazi_daily_calendar;"
```

## 上线后抽样校验

```sql
SELECT date, flow_year, flow_month, flow_day
FROM bazi_daily_calendar
WHERE date IN ('2026-03-03', '2026-06-01', '2026-12-31');
```
