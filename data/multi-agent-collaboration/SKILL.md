---
name: multi-agent-collaboration
description: |
  多智能体协作系统V1.4（最终版），支持**所有行业所有内容**的智能协作：
  通用信息守护者(信息采集)、内容趋势优化系统(趋势创作)、状态洞察模块(个人状态)、工作流沉淀系统(报告生成)。
  适用于：金融、医疗、教育、零售、科技、制造业、餐饮、服务业等**全行业**。
  核心功能：意图识别+智能路由+反思机制+主动感知+用户自适应，支持串行/并行/跳过/精简多种执行模式，
  执行前自动检索记忆库，学习用户偏好，动态调整交互方式，预测用户需求。
  包含强大的记忆系统V2，支持场景化记忆、分层存储、遗忘机制和智能检索。
---

# 多智能体协作系统 V1.4（最终版）

> 🎯 **最终版本**：用户自适应 - 学习用户偏好，动态调整交互

## V1.4 核心升级

| 新功能 | 说明 |
|--------|------|
| **用户画像** | 记录用户交互偏好 |
| **自适应确认** | 根据跳过率调整确认频率 |
| **个性化输出** | 根据偏好调整报告风格 |
| **预测服务** | 主动预测用户下一步需求 |

## 完整执行流程

```
用户输入
    │
    ▼
┌─────────────────────────────────────┐
│  查用户画像 ←─────────────────────┐ │
│  • 了解用户偏好                   │ │
│  • 获取历史交互模式               │ │
└─────────────────────────────────────┘ │
    │                                    │
    ▼                                    │
意图识别 → 智能路由 ←───────────────────┘
    │                    (参考用户偏好)
    ▼
主动感知
    │
    ▼
┌─────────────────────────────────────┐
│           模块执行                   │
│  (串行/并行/跳过)                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│           反思机制                   │
│  评估 → 优化 → 重试                │
└─────────────────────────────────────┘
    │
    ▼
记录行为 → 更新画像 ─────────────────→ (回到用户画像)
    │
    ▼
用户确认 → 继续/退出
```

---

## 用户画像详解

### 学习数据

```typescript
interface UserProfile {
  user_id: string;
  
  // 交互习惯
  confirmation_habit: {
    total_decisions: number;
    skip_count: number;
    skip_rate: number;          // 跳过率
    avg_decision_time_ms: number;
  };
  
  // 输出偏好
  output_preference: {
    detailed_count: number;
    concise_count: number;
    preferred_style: 'detailed' | 'concise' | 'balanced';
  };
  
  // 推荐接受
  recommendation: {
    total: number;
    accepted: number;
    acceptance_rate: number;
  };
  
  // 执行偏好
  execution: {
    parallel_count: number;
    serial_count: number;
    preferred_mode: 'parallel' | 'serial';
  };
  
  // 模块偏好
  module_preference: {
    module_sequence_history: string[];
    common_paths: string[];
  };
  
  updated_at: string;
}
```

### 自适应策略

| 用户特征 | 系统调整 |
|----------|----------|
| 跳过率 > 60% | 减少确认步骤 |
| 跳过率 < 30% | 保持完整确认 |
| 偏好详细 | 输出更多解释 |
| 偏好精简 | 输出关键要点 |
| 推荐接受 > 70% | 多推荐 |
| 推荐接受 < 30% | 少推荐 |
| 偏好并行 | 优先并行执行 |
| 偏好串行 | 保持串行执行 |

---

## V1.4 交互示例

### 完整交互流程

```
用户：帮我分析新能源汽车行业趋势
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【行业分析】
识别意图：信息获取 + 内容创作
目标行业：新能源汽车

【用户画像】
┌─────────────────────────────────────┐
│  画像：user_001                     │
│  • 跳过率：75% → 简化确认           │
│  • 输出偏好：详细（80%）           │
│  • 推荐接受：90% → 多推荐           │
│  • 执行偏好：并行                   │
└─────────────────────────────────────┘

【自适应决策】
✓ 减少确认步骤
✓ 输出详细报告
✓✓ 尝试并行 多提供推荐


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【执行】模块1 → 模块2（并行）

【模块1 - 反思评估】
✓ 完整性：90% | 质量：8.2/10 | 可用性：92%

【模块2 - 反思评估】
✓ 完整性：88% | 质量：8.0/10 | 可用性：90%

【模块执行完成】

【自适应确认】
✓ 跳过非必要确认（跳过率75%）

摘要：
- 行业趋势：3个
- 创作方案：2套
- 预估时间：25分钟

继续到模块3/4？
1. 继续到模块3
2. 继续到模块4
3. 查看完整报告
4. 结束

请回复：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 预测性服务

```
用户：看看金融行业新闻

【行业分析】
识别意图：信息获取
目标行业：金融

【预测服务】
根据您的历史行为：
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 87% 概率：您会继续到模块2（创作）
• 60% 概率：您会查看详细报告
• 常用路径：模块1 → 模块2
━━━━━━━━━━━━━━━━━━━━━━━━━━━

【预执行】
已在后台准备模块2内容（如果继续）

开始执行模块1...
━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**注意**：以上示例适用于任何行业（金融、医疗、教育、零售、科技、新能源汽车、餐饮等）

---

## 全面自检报告

### ✅ 版本一致性检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| V1.0 核心保留 | ✓ | 串行流程、用户确认、数据传递、灵活退出 |
| V1.1 增量引入 | ✓ | 意图识别、智能路由、并行执行 |
| V1.2 增量引入 | ✓ | 反思机制、自动重试、优化尝试 |
| V1.3 增量引入 | ✓ | 主动感知、增量更新、模式复用 |
| V1.4 增量引入 | ✓ | 用户画像、自适应、预测服务 |

### ✅ 功能完整性检查

| 模块 | 功能 | 状态 |
|------|------|------|
| 模块1 | 信息采集+过滤+评估+分级 | ✓ |
| 模块2 | 趋势分析+爆款分析+创作方案+发布策略 | ✓ |
| 模块3 | 状态分析+成长洞察+AI信件 | ✓ |
| 模块4 | 工具推荐+工作流记录+模板生成+效率报告 | ✓ |

### ✅ 记忆系统检查

| 功能 | 状态 |
|------|------|
| 五层架构（L0-L4） | ✓ |
| 场景化配置 | ✓ |
| 智能检索 | ✓ |
| 遗忘机制 | ✓ |
| 反馈闭环 | ✓ |
| 增量更新 | ✓ |

### ✅ 逻辑一致性检查

| 检查项 | 状态 |
|--------|------|
| 模块执行顺序（1→2/3/4） | ✓ |
| 数据传递（后续模块可访问前置输出） | ✓ |
| 用户确认点（每模块后） | ✓ |
| 灵活退出（任何时候可退出） | ✓ |
| 记忆流转（L0→L2→L3→L4） | ✓ |
| 反思触发（每模块后） | ✓ |
| 自适应依赖（需要画像数据） | ✓ |

### ✅ 向后兼容性检查

| 配置项 | 默认值 | 可关闭 |
|--------|--------|--------|
| intent_recognition | true | ✓ |
| smart_routing | true | ✓ |
| parallel_execution | true | ✓ |
| reflection | true | ✓ |
| proactive_memory | true | ✓ |
| user_adaptation | true | ✓ |
| user_confirmation | true | ✗ (必须开启) |
| data_passing | true | ✗ (必须开启) |
| flexible_exit | true | ✗ (必须开启) |

---

## 完整配置

```typescript
const MULTI_AGENT_SYSTEM_V1_4 = {
  // 版本
  version: "1.4",
  release_date: "2026-02-25",
  
  // V1.4 功能
  user_adaptation: {
    enabled: true,
    profile_tracking: true,
    adaptive_confirmation: true,
    personalized_output: true,
    predictive_service: true
  },
  
  // V1.3 功能
  proactive_memory: {
    enabled: true,
    incremental_update: true,
    cache_ttl_hours: 168,
    reuse_bonus: 0.2
  },
  
  // V1.2 功能
  reflection: {
    enabled: true,
    auto_retry: true,
    max_retries: 3,
    dimensions: ['completeness', 'quality', 'usability']
  },
  
  // V1.1 功能
  routing: {
    intent_recognition: true,
    smart_routing: true,
    parallel_execution: true,
    patterns: ['serial', 'parallel', 'skip', '精简']
  },
  
  // V1 核心（不可关闭）
  core: {
    user_confirmation: true,
    data_passing: true,
    flexible_exit: true
  },
  
  // 模块配置
  modules: {
    module1: {
      name: "信息守护者",
      layer: "L0",
      retention: "1小时"
    },
    module2: {
      name: "内容趋势优化系统",
      layer: "L2",
      retention: "7天"
    },
    module3: {
      name: "状态洞察模块",
      layer: "L3-L4",
      retention: "90天"
    },
    module4: {
      name: "工作流沉淀系统",
      layer: "L3",
      retention: "永久"
    }
  },
  
  // 记忆系统
  memory: {
    enabled: true,
    layers: ['L0', 'L1', 'L2', 'L3', 'L4'],
    scenarios: ['duty', 'sentiment', 'workflow', 'goal', 'general']
  }
};
```

---

## 执行模式汇总

| 模式 | V1.0 | V1.1 | V1.2 | V1.3 | V1.4 |
|------|------|------|------|------|------|
| 串行执行 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 意图识别 | - | ✓ | ✓ | ✓ | ✓ |
| 智能路由 | - | ✓ | ✓ | ✓ | ✓ |
| 并行执行 | - | ✓ | ✓ | ✓ | ✓ |
| 反思机制 | - | - | ✓ | ✓ | ✓ |
| 主动感知 | - | - | - | ✓ | ✓ |
| 用户自适应 | - | - | - | - | ✓ |

---

## 参考文档

- 完整工作流设计： [references/workflow-design.md](references/workflow-design.md)
- 模块间数据流转： [references/data-flow.md](references/data-flow.md)
- 记忆系统V2源码： [scripts/memory-v2.ts](scripts/memory-v2.ts)
