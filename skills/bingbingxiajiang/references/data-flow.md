# 模块间数据流转（含记忆系统）

## 数据流转总览（含记忆层）

```
模块1（AI信息守护者）
    │
    ├─ 输出：结构化信息列表
    │   ├─ A级信息列表
    │   ├─ B级信息列表
    │   ├─ C级信息列表
    │   ├─ 行业趋势分析
    │   └─ 信源推荐
    │
    ├─ 记忆处理：
    │   ├─ 存入 L0 闪存（当前任务变量）
    │   ├─ 高价值信息 → L2 经验记忆
    │   └─ 行业趋势 → L3 知识记忆
    │
    ├─ 可传递给：
    │   ├─ 模块2：用于趋势分析
    │   ├─ 模块3：用于状态分析（作为参考）
    │   └─ 模块4：用于工作流编排
    │
    └─ 数据格式：JSON


模块2（内容趋势优化系统）
    │
    ├─ 输出：趋势分析与创作方案
    │   ├─ 趋势扫描报告
    │   ├─ 爆款分析报告
    │   ├─ 平台差异化创作方案
    │   └─ 发布时机建议
    │
    ├─ 输入：模块1的输出 + L0/L2 记忆
    │
    ├─ 记忆处理：
    │   ├─ 存入 L2 经验记忆
    │   ├─ 创作模式 → L3 知识记忆
    │   └─ 爆款因素 → L3 模式库
    │
    ├─ 可传递给：
    │   ├─ 模块3：用于状态分析（作为参考）
    │   └─ 模块4：用于工作流编排
    │
    └─ 数据格式：JSON


模块3（状态洞察模块）
    │
    ├─ 输出：状态分析与洞察建议
    │   ├─ 精力分配分析
    │   ├─ 成长轨迹分析
    │   ├─ 情绪状态分析
    │   └─ 前瞻洞察建议
    │
    ├─ 输入：
    │   ├─ 模块1的输出（作为参考）
    │   ├─ 模块2的输出（如适用）
    │   └─ 用户历史数据（L3-L4）
    │
    ├─ 记忆处理：
    │   ├─ 存入 L3 知识记忆
    │   ├─ 洞察 → L4 智慧记忆
    │   └─ 状态趋势 → 长期追踪
    │
    ├─ 可传递给：
    │   └─ 模块4：用于工作流编排
    │
    └─ 数据格式：JSON


模块4（工作流沉淀系统）
    │
    ├─ 输出：工作流报告与模板
    │   ├─ AI工具组合推荐
    │   ├─ 工作流模板
    │   ├─ 可复用Skill模板
    │   └─ 效率报告
    │
    ├─ 输入：
    │   ├─ 模块1的输出
    │   ├─ 模块2的输出（如适用）
    │   ├─ 模块3的输出（如适用）
    │   └─ L2-L3 历史工作流
    │
    ├─ 记忆处理：
    │   ├─ 存入 L3 知识记忆（永久）
    │   ├─ 生成可复用模板 → L3
    │   └─ 效率数据 → L2 经验
    │
    └─ 数据格式：JSON
```

---

## 记忆流转规则

### 模块 → 记忆层映射

| 模块 | 主要记忆层 | 压缩目标 | 提炼目标 |
|------|-----------|----------|----------|
| 模块1 (信息守护者) | L0 → L2 | 高价值信息 | 行业趋势 |
| 模块2 (内容优化) | L2 | 创作模式 | 爆款因素 |
| 模块3 (状态洞察) | L3 → L4 | 洞察建议 | 成长模式 |
| 模块4 (工作流) | L3 | 工作流模板 | 效率模式 |

### 记忆保留周期

```typescript
const MEMORY_RETENTION = {
  // 模块1：信息时效性强，快速遗忘
  module1_L0: { layer: 'L0', ttl_hours: 1 },
  module1_L2: { layer: 'L2', ttl_days: 7 },
  
  // 模块2：创作经验可复用
  module2_L2: { layer: 'L2', ttl_days: 7 },
  module2_L3: { layer: 'L3', ttl_days: 30 },
  
  // 模块3：状态需长期追踪
  module3_L3: { layer: 'L3', ttl_days: 90 },
  module3_L4: { layer: 'L4', ttl_days: 365 },
  
  // 模块4：工作流模板永久保存
  module4_L3: { layer: 'L3', ttl_days: null }  // 永久
};
```

---

## 用户反馈与记忆调整

### 反馈类型 → 记忆影响

| 用户行为 | 反馈效果 | 记忆调整 |
|----------|----------|----------|
| 选择继续到下一模块 | success | +10% 重要性 |
| 选择退出 | neutral | 不变 |
| 要求重试 | failure | -10% 重要性 |
| 完成全部模块 | success | 模式提炼到L3 |

### 记忆自动优化

```python
# 用户确认后的记忆处理
def on_user_confirm(choice, module_output):
    if choice == "continue":
        # 成功：强化当前记忆
        enhance_memory(module_output, bonus=0.1)
        # 准备传递给下一模块
        return prepare_for_next_module(module_output)
    
    elif choice == "exit":
        # 退出：保存当前模块记忆
        save_to_L2(module_output)
        # 生成最终报告
        return generate_final_report()
    
    elif choice == "retry":
        # 重试：降低相关记忆权重
        weaken_memory(module_output, penalty=0.1)
        # 重新执行当前模块
        return reexecute_module(module_output)
```

---

## 上下文数据结构（含记忆）

```python
# 完整的上下文对象
context = {
    "session_id": "session_20260225_001",
    "user_id": "user_001",
    "start_time": "2026-02-25 15:00:00",
    "current_module": "module_1",
    "execution_path": ["module_1"],
    
    # 模块输出（含记忆位置）
    "module_outputs": {
        "module_1": {
            "name": "AI信息守护者",
            "output": {...},
            "memory_layer": "L0",        # 当前存储层
            "compress_target": "L2",      # 压缩目标
            "retention": "1小时"          # 保留周期
        },
        "module_2": {...},
        "module_3": {...},
        "module_4": {...}
    },
    
    # 记忆系统上下文
    "memory_context": {
        "scenario": "workflow",
        "L0_vars": {...},                # 当前任务变量
        "recent_L2": [...],              # 最近经验（供参考）
        "relevant_L3": [...],            # 相关知识（供参考）
        "user_history": {...}            # 用户长期状态
    },
    
    "user_choices": {
        "step_1": "continue_to_module_2",
        "step_2": "continue_to_module_3",
        "step_3": "continue_to_module_4"
    }
}
```

---

## 智能检索示例

### 模块2调用模块1的记忆

```python
# 模块2执行时，检索相关记忆
relevant_memories = memory.smartQuery(
    query="AI行业趋势",
    scenario="workflow",
    options={
        "min_credibility": 0.7,
        "min_success_rate": 0.6,
        "max_age": 7  # 只检索7天内的
    }
)

# 使用记忆辅助创作
for mem in relevant_memories:
    if mem.category == "pattern":
        # 使用提炼的模式
        apply_pattern(mem.value)
```

### 模块3调用长期状态

```python
# 模块3分析用户状态
user_history = memory.query(
    layer="L3-L4",
    category=["goal", "insight"],
    user_id="user_001"
)

# 结合历史生成洞察
insight = generate_insight(
    current_state=module3_input,
    historical_data=user_history
)
```

---

## 最终交付报告（含记忆摘要）

```python
final_report = {
    "session_info": {
        "session_id": "session_20260225_001",
        "execution_path": "模块1 → 模块2 → 模块3 → 模块4",
        "duration": "60分钟"
    },
    
    "module_outputs": {...},
    
    "memory_summary": {
        "stored_L0": 5,    # 当前任务变量
        "stored_L2": 12,   # 新增经验
        "stored_L3": 3,    # 新增知识
        "extracted_patterns": 2,  # 提炼的模式
        "forgotten": 1      # 遗忘的低价值记忆
    },
    
    "reusable_assets": [
        "综合管理工作流模板",
        "AI行业趋势分析模式",
        "内容创作工作流模板"
    ],
    
    "next_session_context": {
        "suggested_module": "模块3",  # 基于用户状态推荐
        "relevant_history": [...],    # 可继承的记忆
        "pending_goals": [...]        # 未完成目标
    }
}
```
