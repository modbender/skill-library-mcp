# Changelog

All notable changes to openclaw-cost-optimizer will be documented in this file.

## [1.0.0] - 2026-02-26

### Added
- 初始版本发布
- Session logs 分析功能
- Token 使用统计（按模型、会话、时间维度）
- 高消耗场景识别：
  - 长对话检测（>50k tokens）
  - 频繁 Cron 任务（>10次/天）
  - 大 Context 会话（平均>30k tokens）
  - 昂贵模型使用
- 优化建议生成：
  - 模型降级策略
  - Context 压缩方案
  - Cron 频率调整
  - 本地模型使用建议
- 成本报告生成（Markdown 格式）
- 快速成本查看命令
- 预计节省金额计算
- 纯 Node.js 实现，无外部依赖

### Features
- `analyze` 命令：生成完整分析报告
- `quick` 命令：快速查看今日成本
- 支持自定义分析天数
- 自动保存报告到 memory 目录
- 优先级排序的优化建议（高/中/低）

### Security
- ✅ 纯本地运行
- ✅ 无网络请求
- ✅ 无外部依赖
- ✅ 不执行子进程
- ✅ 只读分析，不修改配置
- ✅ 数据不离开本机
