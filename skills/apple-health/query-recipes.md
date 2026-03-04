# Query Recipes — Apple Health MCP

Use these patterns after `health_schema` confirms table names.

## 1) Resting Heart Rate Last 30 Days

```sql
SELECT date_trunc('day', startDate) AS day,
       AVG(CAST(value AS DOUBLE)) AS avg_rhr
FROM hkquantitytypeidentifierrestingheartrate
WHERE startDate >= now() - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

## 2) Sleep Duration Last 14 Days

```sql
SELECT date_trunc('day', startDate) AS day,
       SUM(date_diff('minute', startDate, endDate)) / 60.0 AS sleep_hours
FROM hkcategorytypeidentifiersleepanalysis
WHERE startDate >= now() - INTERVAL 14 DAY
GROUP BY 1
ORDER BY 1;
```

## 3) Workouts Per Week (12 Weeks)

```sql
SELECT date_trunc('week', startDate) AS week,
       COUNT(*) AS workouts
FROM hkworkoutactivitytype
WHERE startDate >= now() - INTERVAL 84 DAY
GROUP BY 1
ORDER BY 1;
```

## Reporting Guardrails

- Always show the exact date window used.
- Always keep units visible (bpm, hours, counts).
- If table names differ, map from `health_schema` output and retry.
