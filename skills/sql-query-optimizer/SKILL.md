# SQL Query Optimizer

分析并优化 SQL 查询，提升数据库性能。

## 功能

- 查询性能分析
- 索引建议
- 执行计划解读
- SQL 优化建议

## 触发词

- "SQL优化"
- "查询优化"
- "sql optimization"
- "慢查询"

## 检测问题

```sql
-- 检测 SELECT * 问题
SELECT * FROM users WHERE id = 1;

-- 检测缺少 LIMIT
SELECT name FROM users;

-- 检测前导通配符
SELECT * FROM users WHERE name LIKE '%john%';
```

## 优化建议

1. 避免 SELECT *，只查询需要的列
2. 添加 WHERE 条件和 LIMIT
3. 避免 LIKE 前导通配符
4. 使用索引列
5. 避免嵌套子查询
6. 使用 EXPLAIN 分析执行计划

## 输出示例

```json
{
  "original": "SELECT * FROM users WHERE name LIKE '%john%'",
  "suggestions": [
    "避免使用 SELECT *，只查询需要的列",
    "避免 LIKE 前导通配符",
    "添加 LIMIT 限制返回数量"
  ],
  "optimized": "SELECT id, name FROM users WHERE name LIKE '%john%' LIMIT 100"
}
```
