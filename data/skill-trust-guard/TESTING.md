# Testing Notes (latest)

已由 `TEST_REPORT.md` 统一记录最新测试结果。

关键结论：
- 安全样本（coding-agent）放行
- 中风险样本（warn-skill3）告警后可放行
- 恶意样本（malicious-skill）成功拦截（score=5）
- architect/neo4j 在线安装因 clawhub rate limit 暂未完成，待恢复后复测
