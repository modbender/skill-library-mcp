---
name: roundtable
version: 1.1.0
description: |
  Multi-perspective decision analysis. Use when the user asks for roundtable,
  or when facing important decisions that need multiple viewpoints.
  Dynamically selects relevant roles based on the task.
  
  ⚠️ 直接在主 session 执行，不要 spawn subagent。
  Roundtable 是 prompt 技巧，不需要隔离环境。
---

# Roundtable: Multi-Perspective Decision Analysis

## ⚠️ 执行方式

**直接在主 session 执行，不要用 sessions_spawn。**

原因：
1. Roundtable 是 prompt 技巧，不是长任务
2. 主 Agent 需要保持对话控制
3. 避免 subagent announce 路由问题
4. 更快（省去 spawn 开销）

## When to Use

**触发词（任一）：**
- roundtable / roundtable this
- 圆桌 / 圆桌会议 / 圆桌讨论
- 帮我跑一个 roundtable

**场景：**
- Important decisions that benefit from multiple viewpoints
- Before high-risk operations (trading, public posts, major changes)

## Default Prompt (动态选角)

```
针对以下决策进行 roundtable 讨论：

[决策描述]

请：
1. 评估决策风险级别，选择合适人数（3-8人）
2. 选择最相关的视角/角色
3. 每个角色进行两轮讨论（每轮 2-3 句话）
4. 给出 Consensus（最终建议 + action items）

输出格式：
## 🗣️ 第一轮
### [角色1 emoji] [角色名]
> "观点..."

### [角色2 emoji] [角色名]
> "观点..."

## 🗣️ 第二轮
...

## 📊 Consensus
- 最终建议

### Action Items (checkbox 格式，便于追踪)
- [ ] 第一个行动项
- [ ] 第二个行动项
- [ ] 第三个行动项
```

## 角色参考池

根据任务类型，从以下角色中选择：

| 角色 | Emoji | 擅长领域 |
|------|-------|----------|
| GrowthStrategist | 📈 | 增长、scale、ROI、机会 |
| RiskGuardian | ⚠️ | 风险、downside、防御 |
| SkepticalOperator | 🤔 | 执行现实、过度工程检测 |
| QualityArchitect | 🏛️ | 质量、可维护性、长期影响 |
| FinanceAnalyst | 💰 | 成本、现金流、ROI 计算 |
| TechEngineer | 🔧 | 技术可行性、架构、实现 |
| ProductManager | 🎯 | 用户价值、优先级、MVP |
| DataScientist | 📊 | 数据验证、A/B测试、统计 |
| SecurityAuditor | 🛡️ | 安全、合规、隐私 |
| CreativeDirector | 🎨 | 创意、差异化、品牌 |
| MarketAnalyst | 📉 | 市场情绪、趋势、交易时机 |
| DevilsAdvocate | 😈 | 专门唱反调、找漏洞、压力测试 |
| UserAdvocate | 👤 | 用户视角、体验优先、同理心 |
| LegalCounsel | ⚖️ | 合规、法律风险、条款细节 |
| HistorianAnalyst | 📚 | 历史类比、"上次怎样"、模式识别 |

**不需要背这个列表** — 根据任务自然选择合适视角即可。

## 参与人数指南

| 决策类型 | 人数 | 说明 |
|----------|------|------|
| 快速判断 | 3 | 日常决策，不需要太多视角 |
| 标准决策 | 4-5 | 默认配置，平衡深度和效率 |
| 高风险决策 | 6-7 | 真钱交易、公开发布、不可逆操作 |
| 战略级决策 | 8+ | 重大方向调整、年度规划 |

**判断标准：**
- 涉及金额 >$500 → 至少 5 人
- 不可逆操作 → 至少 6 人
- 公开发布 → 至少 5 人（含 DevilsAdvocate）
- 有历史教训的领域 → 必须含 HistorianAnalyst

## 特殊格式

### pre_trade (真钱交易前)

必须包含：
- ⚠️ RiskGuardian — 风险评估
- 💰 FinanceAnalyst — 成本/收益
- 🤔 SkepticalOperator — 质疑假设

### think_tank_review (高风险操作前)

用于：真钱交易、对外发消息、删除重要文件、修改系统配置

智库**只提问题**，不做最终决策。

## 优先级评分（可选）

如果需要对建议排序：

```
priority = (impact × 0.4) + (confidence × 0.35) + ((100 - effort) × 0.25)
```

- impact: 预期影响 0-100
- confidence: 把握程度 0-100  
- effort: 工作量 0-100

## 示例任务 → 角色选择

| 任务 | 推荐角色 | 人数 |
|------|----------|------|
| 交易决策 | RiskGuardian, FinanceAnalyst, MarketAnalyst, SkepticalOperator, HistorianAnalyst | 5 |
| X 帖子内容 | GrowthStrategist, CreativeDirector, DevilsAdvocate, UserAdvocate | 4 |
| 系统架构 | TechEngineer, SecurityAuditor, SkepticalOperator, QualityArchitect | 4 |
| 产品定价 | FinanceAnalyst, GrowthStrategist, ProductManager, UserAdvocate | 4 |
| 内容发布 | GrowthStrategist, QualityArchitect, RiskGuardian, DevilsAdvocate | 4 |
| 合同/协议 | LegalCounsel, RiskGuardian, FinanceAnalyst, SkepticalOperator | 4 |
| 大额交易 (>$1k) | RiskGuardian, FinanceAnalyst, MarketAnalyst, HistorianAnalyst, DevilsAdvocate, SkepticalOperator | 6 |

## 注意事项

- 每个角色 2-3 句话，不要长篇大论
- 角色之间要有真正的分歧，不是和稀泥
- Consensus 要有明确的行动建议
- 如果所有角色都同意，可能说明问题太简单不需要 roundtable

## 何时用 Subagent（不是 Roundtable）

以下场景应该用 `sessions_spawn`：

| 场景 | 原因 |
|------|------|
| 长任务 (>3min) | 不阻塞主对话 |
| 并行研究多个目标 | 同时跑，结果汇总 |
| 代码重构/大改动 | 隔离环境 |
| 批量处理 | 比如扫描 20 个市场 |

**Roundtable 不属于以上任何一种** — 它只是一个 prompt 技巧。
