# OpenClaw Cost Optimizer

专为 OpenClaw 用户设计的成本分析和优化工具。

## 功能

- 📊 分析 session logs，统计 token 使用和成本
- 🔍 识别高消耗场景（长对话、频繁 cron、大 context）
- 💡 给出具体优化建议（模型降级、context 压缩、cron 频率调整）
- 📈 生成清晰的成本报告
- 🚀 纯 Node.js，无外部依赖

## 快速开始

```bash
# 生成完整分析报告（默认最近 7 天）
node scripts/cost_analyzer.js analyze

# 分析最近 30 天
node scripts/cost_analyzer.js analyze 30

# 快速查看今日成本
node scripts/cost_analyzer.js quick
```

## 报告内容

- 总览：会话数、token 使用、总成本
- 模型统计：各模型的使用情况和成本
- 高成本会话：Top 5 最贵的会话
- 优化建议：可执行的优化方案和预计节省

## 优化策略

1. **模型分级使用**：简单任务用 Sonnet/本地模型，复杂任务才用 Opus
2. **Context 优化**：精简 AGENTS.md，使用 lazy loading
3. **Cron 优化**：降低非关键任务频率
4. **会话管理**：超过 50k tokens 开启新会话
5. **本地模型**：文件读取等简单任务使用 Ollama

## 成本基准

| 使用模式 | 每日会话数 | 每日成本 | 每月成本 |
|---------|-----------|---------|---------|
| 轻度使用 | 5-10 | $0.50-1.00 | $15-30 |
| 中度使用 | 20-30 | $2.00-4.00 | $60-120 |
| 重度使用 | 50+ | $8.00-15.00 | $240-450 |
| 优化后 | 50+ | $3.00-6.00 | $90-180 |

**优化目标**：节省 50-60% 成本

## 集成到工作流

```bash
# 每日成本检查
openclaw cron add "0 9 * * *" "node ~/.openclaw/workspace/skills/openclaw-cost-optimizer/scripts/cost_analyzer.js quick"

# 每周深度分析
openclaw cron add "0 10 * * 1" "node ~/.openclaw/workspace/skills/openclaw-cost-optimizer/scripts/cost_analyzer.js analyze 7"
```

## 安全性

✅ 纯本地运行，无网络请求  
✅ 无外部依赖  
✅ 只读分析，不修改配置  
✅ 数据不离开本机

## 许可

MIT License
