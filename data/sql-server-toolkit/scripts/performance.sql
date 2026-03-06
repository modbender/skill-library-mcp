
SET STATISTICS IO ON;
SET STATISTICS TIME ON;

SELECT TOP 10
    qs.total_elapsed_time / qs.execution_count AS avg_time,
    qs.execution_count,
    qt.text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
ORDER BY avg_time DESC;
