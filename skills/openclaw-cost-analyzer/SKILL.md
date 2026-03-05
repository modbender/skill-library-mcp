---
name: openclaw-cost-optimizer
description: 分析 OpenClaw 的 token 使用和成本，识别高消耗场景（长对话、频繁 cron、大 context），给出具体优化建议（模型降级、context 压缩、cron 频率调整）。纯 Node.js，无外部依赖。输出清晰的成本报告。
version: 1.0.0
author: OpenClaw Community
security:
  verified: true
  scripts_no_network: true
  scripts_no_code_execution: true
  scripts_no_subprocess: true
  scripts_data_local_only: true
---

# OpenClaw Cost Optimizer

专为 OpenClaw 用户设计的成本分析和优化工具。通过分析 session logs，识别高消耗场景，给出可执行的优化建议。

## 核心功能

### 1. 成本分析
- 读取 session logs，统计 token 使用和成本
- 按模型、会话、时间维度分析
- 识别高成本会话和异常消耗

### 2. 场景识别
- **长对话检测**: 超过 50k tokens 的会话
- **频繁 Cron**: 每天超过 10 次的定时任务
- **大 Context**: 平均输入超过 30k tokens
- **昂贵模型**: 使用高成本模型处理简单任务

### 3. 优化建议
- 模型降级策略（Opus → Sonnet → DeepSeek）
- Context 压缩方案
- Cron 频率调整
- 本地模型使用建议
- 预计节省金额

## 快速开始

### 生成完整分析报告（推荐）

```bash
node scripts/cost_analyzer.js analyze
```

默认分析最近 7 天，生成详细报告保存到 `~/.openclaw/workspace/memory/cost-analysis-report.md`

**指定天数**:
```bash
node scripts/cost_analyzer.js analyze 30  # 分析最近 30 天
```

### 快速查看今日成本

```bash
node scripts/cost_analyzer.js quick
```

输出示例:
```
📊 今日成本快览:
  总成本: $2.45
  会话数: 12
  平均: $0.204/会话
```

## 报告示例

```markdown
# OpenClaw 成本分析报告

生成时间: 2026-02-26 15:30:00

## 📊 总览

- 总会话数: 45
- 总输入 tokens: 1,234,567
- 总输出 tokens: 456,789
- 总成本: $15.67
- 平均每会话: $0.348

## 🤖 模型使用统计

### claude-opus-4-6
- 会话数: 30
- 输入: 890,123 tokens
- 输出: 345,678 tokens
- 成本: $12.34

### claude-sonnet-4-20250514
- 会话数: 15
- 输入: 344,444 tokens
- 输出: 111,111 tokens
- 成本: $3.33

## 💰 高成本会话 (Top 5)

- Session: a1b2c3d4...
  - 模型: claude-opus-4-6
  - Tokens: 125,000
  - 成本: $3.45
  - 消息数: 25

## 💡 优化建议

### 1. 🔴 模型降级：yunyi-claude/claude-opus-4-6

**问题**: 该模型成本较高 ($45/M tokens)，已使用 30 次会话

**建议**: 对于简单任务使用 Sonnet 或 DeepSeek，复杂任务才用 Opus

**预计节省**: $9.87

**操作**: `openclaw models set yunyi-claude/claude-sonnet-4-20250514`

### 2. 🟡 长对话检测

**问题**: 发现 3 个长对话，最长 125,000 tokens

**建议**: 超过 50k tokens 时开启新会话，避免 context 累积

**预计节省**: $1.04

**操作**: 手动开启新会话或设置 context 限制

### 3. 🔴 Context 过大

**问题**: 平均每次会话输入 27,435 tokens，可能加载了过多文件

**建议**: 优化 AGENTS.md、SOUL.md，移除不必要的内容；使用 lazy loading

**预计节省**: $6.27

**操作**: 参考 openclaw-token-optimizer skill 的 context_optimizer

**总预计节省**: $17.18
```

## 优化策略详解

### 策略 1: 模型分级使用

根据任务复杂度选择模型:

| 任务类型 | 推荐模型 | 成本 |
|---------|---------|------|
| 简单查询、文件读取 | local/qwen2.5:7b | 免费 |
| 日常对话、代码编写 | claude-sonnet-4 | $3/M |
| 复杂推理、架构设计 | claude-opus-4-6 | $45/M |
| 备用/降级 | deepseek-chat | $0.02/M |

**操作**:
```bash
# 临时切换
openclaw models set yunyi-claude/claude-sonnet-4-20250514

# 设置 fallback
openclaw models fallbacks add deepseek/deepseek-chat
```

### 策略 2: Context 优化

**问题**: 默认加载所有 context 文件（SOUL.md, AGENTS.md, TOOLS.md, MEMORY.md, docs/**/*.md），可能 50k+ tokens

**解决方案**:

1. **精简 AGENTS.md**
   - 移除冗余说明
   - 合并重复规则
   - 使用简洁语言

2. **Lazy Loading**
   - 简单任务只加载 SOUL.md + IDENTITY.md
   - 复杂任务按需加载相关文档
   - 参考 `openclaw-token-optimizer` 的 context_optimizer

3. **定期清理**
   ```bash
   # 清理旧 memory logs
   find ~/.openclaw/workspace/memory -name "2026-*.md" -mtime +30 -delete
   ```

### 策略 3: Cron 优化

**识别高频 Cron**:
```bash
openclaw cron list
```

**优化方案**:
- 非关键任务降低频率（每小时 → 每 4 小时）
- 使用更便宜的模型执行 cron
- 合并多个小任务为一个批处理

**示例**:
```bash
# 修改 cron 频率
openclaw cron edit <job-id>

# 为 cron 指定模型
openclaw cron add --model local/qwen2.5:7b "0 */4 * * *" "检查系统状态"
```

### 策略 4: 会话管理

**长对话问题**: Context 累积导致每次请求都携带完整历史

**解决方案**:
- 超过 50k tokens 时主动开启新会话
- 使用 `/new` 命令清空 context
- 重要信息保存到 MEMORY.md，不依赖会话历史

### 策略 5: 启用本地模型

**适用场景**:
- 文件读取、简单查询
- 开发测试
- 离线工作

**设置**:
```bash
# 确保 Ollama 运行
ollama serve

# 拉取模型
ollama pull qwen2.5:7b

# 切换到本地模型
openclaw models set local/qwen2.5:7b
```

## 成本基准

基于实际使用数据的成本参考:

| 使用模式 | 每日会话数 | 平均 tokens/会话 | 每日成本 | 每月成本 |
|---------|-----------|----------------|---------|---------|
| 轻度使用 | 5-10 | 20k | $0.50-1.00 | $15-30 |
| 中度使用 | 20-30 | 30k | $2.00-4.00 | $60-120 |
| 重度使用 | 50+ | 40k | $8.00-15.00 | $240-450 |
| 优化后 | 50+ | 15k | $3.00-6.00 | $90-180 |

**优化目标**: 重度使用场景下节省 50-60% 成本

## 集成到工作流

### 每日成本检查（推荐）

添加 cron 任务，每天生成报告:

```bash
openclaw cron add "0 9 * * *" "node ~/.openclaw/workspace/skills/openclaw-cost-optimizer/scripts/cost_analyzer.js quick"
```

### 每周深度分析

```bash
openclaw cron add "0 10 * * 1" "node ~/.openclaw/workspace/skills/openclaw-cost-optimizer/scripts/cost_analyzer.js analyze 7"
```

### 成本告警

在 AGENTS.md 中添加规则:

```markdown
## 成本监控
- 每日成本超过 $5 → 立即告警
- 单次会话超过 $1 → 记录并分析
- 每周生成成本报告
```

## 与其他 Skills 配合

### openclaw-token-optimizer
- 本 skill 专注**成本分析和报告**
- token-optimizer 提供**底层优化工具**（context_optimizer, model_router）
- 配合使用效果最佳

### openclaw-doctor
- doctor 检查系统健康
- cost-optimizer 检查成本健康
- 一起使用确保系统稳定且经济

## 技术细节

### 数据来源
- Session logs: `~/.openclaw/agents/main/agent/sessions/*.jsonl`
- 分析最近 N 天的日志（默认 7 天）
- 提取 inputTokens, outputTokens, model, sessionId

### 成本计算
基于各模型官方定价:
```javascript
modelCosts: {
  'yunyi-claude/claude-opus-4-6': { input: 15, output: 75 },
  'yunyi-claude/claude-sonnet-4-20250514': { input: 3, output: 15 },
  'deepseek/deepseek-chat': { input: 0.014, output: 0.028 },
  'local/qwen2.5:7b': { input: 0, output: 0 }
}
```

### 阈值配置
```javascript
thresholds: {
  longConversation: 50000,      // tokens
  highContextSession: 30000,    // tokens
  frequentCron: 10,             // 每天次数
  expensiveModel: 10            // USD per 1M tokens
}
```

可在脚本中修改以适应个人需求。

## 安全性

✅ **纯本地运行**
- 无网络请求
- 无外部依赖
- 不执行子进程
- 数据不离开本机

✅ **只读分析**
- 只读取 session logs
- 不修改任何配置
- 不执行任何操作
- 建议需手动执行

## 故障排查

### 问题: 未找到 session logs

**原因**: logs 目录不存在或路径错误

**解决**:
```bash
ls ~/.openclaw/agents/main/agent/sessions/
```

如果目录不存在，说明还没有会话记录。

### 问题: 成本计算不准确

**原因**: 模型定价可能更新

**解决**: 编辑 `scripts/cost_analyzer.js`，更新 `modelCosts` 对象。

### 问题: 报告为空

**原因**: 指定天数内没有日志

**解决**: 增加分析天数
```bash
node scripts/cost_analyzer.js analyze 30
```

## 更新日志

### v1.0.0 (2026-02-26)
- 初始版本
- 支持 session logs 分析
- 识别 5 大高消耗场景
- 生成优化建议和成本报告
- 纯 Node.js 实现，无外部依赖

## 贡献

欢迎提交 Issue 和 PR:
- 新的优化策略
- 更准确的成本计算
- 更多模型支持
- 报告格式改进

## 许可

MIT License

---

**让 OpenClaw 更经济，让 AI 更可持续！** 💰✨
