# 模型路由策略

> **目标**：根据任务类型自动选择最优模型，平衡质量与成本

## 🎯 路由规则

### Tier 1: Gemini Flash（$0.15/1M 输入，$0.30/1M 输出）
**适用：** 低复杂度、高重复性任务

- ✅ 文档归档、分类、移动
- ✅ CHANGELOG/TASK 清理
- ✅ 格式转换（Markdown ↔ YAML）
- ✅ 简单摘要（<500 words）
- ✅ 日志分析、状态检查
- ✅ 文件重命名、批量处理
- ✅ 代码格式化（已有规则）

**关键词触发：**
`归档`、`清理`、`整理`、`分类`、`移动`、`格式化`、`检查状态`

---

### Tier 2: Sonnet 4.5（$3/1M 输入，$15/1M 输出）
**适用：** 中等复杂度，需要上下文理解

- ✅ 代码 review、重构建议
- ✅ 项目规划、任务拆解
- ✅ 技术文档撰写
- ✅ 复杂摘要（需要推理）
- ✅ API 设计、架构讨论
- ✅ 调试辅助
- ✅ 日常对话（默认）

**关键词触发：**
`设计`、`规划`、`重构`、`分析`、`解释`、`建议`

---

### Tier 3: Opus 4.6（$15/1M 输入，$75/1M 输出）
**适用：** 高复杂度、创意、深度推理

- ✅ 复杂系统架构设计
- ✅ 创意写作、内容创作
- ✅ 深度代码审查
- ✅ 复杂问题诊断
- ✅ 战略决策建议
- ✅ 学习新技术并应用

**关键词触发：**
`深度`、`创意`、`架构`、`战略`、`复杂`、明确要求

---

## 🤖 自动路由逻辑

```python
def route_task(user_message):
    # Tier 1: Flash 触发词
    if any(kw in user_message for kw in 
           ['归档', '清理', '整理', '分类', '移动', 'archive', 'cleanup']):
        return 'gemini-flash'
    
    # Tier 3: Opus 触发词
    if any(kw in user_message for kw in 
           ['深度', '创意', '架构', 'opus', '复杂系统']):
        return 'opus'
    
    # 默认 Tier 2: Sonnet
    return 'sonnet'
```

---

## 📈 成本预估

### 典型日常使用（每天）

| 任务类型 | 次数 | 模型 | 成本/次 | 日成本 |
|---------|------|------|---------|--------|
| 归档维护 | 1 | Flash | $0.0003 | $0.0003 |
| 日常对话 | 10 | Sonnet | $0.01 | $0.10 |
| 深度分析 | 1 | Opus | $0.05 | $0.05 |
| **总计** | - | - | - | **$0.15** |

**vs 全部用 Sonnet：** $0.24/天 → **省 38%**  
**vs 全部用 Opus：** $0.65/天 → **省 77%** 🎉

**年度节省：** 
- vs Sonnet: $33
- vs Opus: $183

---

## 🛠️ 实现方式

### 方式 1：明确指定（当前可用）
```
"用 Flash 归档 CHANGELOG"
"用 Opus 深度分析这个架构"
```

### 方式 2：Sub-agent Spawn（推荐）
```python
sessions_spawn(
    agentId="gemini3",  # Gemini Flash
    task="归档 CHANGELOG 中超过 2 周的条目"
)
```

### 方式 3：Cron 定时任务（自动化）
```json
{
  "schedule": {"kind": "cron", "expr": "0 0 * * 0"},
  "payload": {
    "kind": "agentTurn",
    "message": "读 CHANGELOG.md，归档 2 周前的内容",
    "model": "google/gemini-3-flash-preview"
  }
}
```

---

## 🎯 推荐策略

**阶段 1：立即实施**
- 明确维护任务（归档、清理）→ 手动指定 Flash
- 保持日常对话 → Sonnet

**阶段 2：自动化**
- 设置周度 cron job → 自动用 Flash 归档
- 省人力 + 省成本

**阶段 3：智能路由**
- 我（main agent）根据任务自动选择模型
- 用户无感知，成本自动优化

---

**Token 效率 × 成本优化 = 指数级节省！** 🚀
