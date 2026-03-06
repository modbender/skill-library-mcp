# PostgreSQL 常用命令参考

## 连接数据库

```bash
# 基本连接
psql -U username -d database_name -h host -p port

# 使用环境变量
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=mydb
export PGUSER=postgres
export PGPASSWORD=your_password

# 连接后常用命令
\c database_name    # 切换数据库
\du                 # 列出所有用户
\l                  # 列出所有数据库
\d                  # 列出当前数据库所有表
\d table_name       # 查看表结构
\dt                 # 只列出表
\di                 # 列出索引
\dv                 # 列出视图
\df                 # 列出函数
\x                  # 切换扩展显示模式
\q                  # 退出
```

## 数据库操作

```sql
-- 创建数据库
CREATE DATABASE dbname;

-- 删除数据库
DROP DATABASE dbname;

-- 创建用户
CREATE USER username WITH PASSWORD 'password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE dbname TO username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO username;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO username;
```

## 表操作

```sql
-- 创建表
CREATE TABLE table_name (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加列
ALTER TABLE table_name ADD COLUMN column_name datatype;

-- 删除列
ALTER TABLE table_name DROP COLUMN column_name;

-- 修改列类型
ALTER TABLE table_name ALTER COLUMN column_name TYPE new_type;

-- 添加约束
ALTER TABLE table_name ADD CONSTRAINT constraint_name PRIMARY KEY (column);
ALTER TABLE table_name ADD CONSTRAINT constraint_name FOREIGN KEY (column) REFERENCES other_table(column);

-- 删除表
DROP TABLE table_name;

-- 重命名表
ALTER TABLE old_name RENAME TO new_name;
```

## 数据操作

```sql
-- 插入数据
INSERT INTO table_name (col1, col2) VALUES ('value1', 'value2');
INSERT INTO table_name (col1, col2) VALUES 
    ('value1', 'value2'),
    ('value3', 'value4');

-- 更新数据
UPDATE table_name SET column = 'new_value' WHERE condition;

-- 删除数据
DELETE FROM table_name WHERE condition;

-- 查询数据
SELECT * FROM table_name;
SELECT col1, col2 FROM table_name WHERE condition ORDER BY col1 DESC LIMIT 10;
SELECT col1, COUNT(*) FROM table_name GROUP BY col1 HAVING COUNT(*) > 1;
```

## 索引操作

```sql
-- 创建索引
CREATE INDEX idx_name ON table_name (column);
CREATE INDEX idx_name ON table_name (column1, column2);
CREATE UNIQUE INDEX idx_name ON table_name (column);

-- 删除索引
DROP INDEX idx_name;

-- 查看查询计划
EXPLAIN ANALYZE SELECT * FROM table_name WHERE condition;
```

## 备份与恢复

```bash
# 备份整个数据库（自定义格式）
pg_dump -Fc -U username -d dbname -f backup_file.backup

# 备份整个数据库（SQL格式）
pg_dump -U username -d dbname -f backup_file.sql

# 备份指定表
pg_dump -t table_name -U username -d dbname -f table_backup.sql

# 恢复
pg_restore -U username -d dbname -c backup_file.backup

# 导入SQL
psql -U username -d dbname -f backup_file.sql
```

## 用户与权限

```sql
-- 创建角色
CREATE ROLE role_name WITH LOGIN PASSWORD 'password';

-- 角色授权
GRANT SELECT ON table_name TO role_name;
GRANT ALL ON table_name TO role_name;

-- 撤销权限
REVOKE SELECT ON table_name FROM role_name;

-- 查看权限
\dp table_name
```

## 事务控制

```sql
-- 开始事务
BEGIN;

-- 提交
COMMIT;

-- 回滚
ROLLBACK;

-- 保存点
SAVEPOINT savepoint_name;
ROLLBACK TO SAVEPOINT savepoint_name;
```

## 性能监控

```sql
-- 查看当前连接
SELECT * FROM pg_stat_activity;

-- 查看表大小
SELECT pg_size_pretty(pg_total_relation_size('table_name'));
SELECT pg_size_pretty(pg_relation_size('table_name'));

-- 查看索引使用情况
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- 查看慢查询
SELECT query, calls, mean_time, total_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- 启用 pg_stat_statements
CREATE EXTENSION pg_stat_statements;
```

## 常用数据类型

| 类型 | 说明 |
|------|------|
| SERIAL | 自增整数 |
| VARCHAR(n) | 可变长度字符串 |
| TEXT | 无限长度字符串 |
| INTEGER | 4字节整数 |
| BIGINT | 8字节整数 |
| DECIMAL(p,s) | 精确小数 |
| BOOLEAN | 布尔值 |
| DATE | 日期 |
| TIMESTAMP | 日期时间 |
| JSON/JSONB | JSON数据 |
| ARRAY | 数组 |

## 常用函数

```sql
-- 字符串函数
SELECT UPPER('hello');
SELECT LOWER('HELLO');
SELECT LENGTH('hello');
SELECT SUBSTRING('hello', 1, 3);
SELECT TRIM('  hello  ');
SELECT CONCAT('a', 'b');

-- 日期函数
SELECT CURRENT_DATE;
SELECT CURRENT_TIMESTAMP;
SELECT EXTRACT(YEAR FROM date_column);
SELECT date_column + INTERVAL '1 day';

-- 聚合函数
SELECT COUNT(*), SUM(column), AVG(column), MAX(column), MIN(column) FROM table_name;
```
