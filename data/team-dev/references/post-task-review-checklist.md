# Post-task Review Checklist

用于主 Agent 在 SubAgent 声称完成后进行强制验收。

## 1) 基础信息

- Task ID:
- Branch:
- SubAgent:
- Completion marker (e.g. `TASK_X_DONE`):
- Review date (absolute):

## 2) DoD 逐条核对

- [ ] 功能项已实现（逐条对照任务 prompt）
- [ ] 约束项未违反（例如不改原始数据、不提前做后置任务）
- [ ] 交付项完整（文档/命令/输出字段）

## 3) 真实验证（非 mock）

- [ ] 执行了至少 1 条真实链路验证命令
- [ ] 验证命令可复现（命令已记录）
- [ ] 关键输出已记录（日志/报告路径）

## 4) 指标门禁

- [ ] 指标字段齐全（按任务要求）
- [ ] 指标达到阈值（按 VERSION 文档 Go/No-Go）
- [ ] 无法达标时已明确阻断原因

## 5) 依赖与时序

- [ ] 前置任务已达标
- [ ] 后置任务尚未提前派发（如要求串行）

## 6) 合并决策

- [ ] PASS：允许合并（记录 commit）
- [ ] FAIL：禁止合并并派发 fixup

## 7) 固化记录

- [ ] 已写入 docs（VERSION/REVIEW/VALIDATION）
- [ ] 已更新任务状态与下一步行动

