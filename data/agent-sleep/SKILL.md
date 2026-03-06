---
name: agent-sleep
description: Agent 睡眠系统 - 记忆整合、日志归档、工作区清理（支持 CortexGraph）
metadata:
  openclaw:
    emoji: "🛌"
    category: "system"
    tags: ["memory", "sleep", "consolidation", "cortexgraph"]
    schedulable: true
---

# Agent Sleep System 🛌

像人类一样，Agent 需要"睡眠"（离线维护）来防止记忆碎片化和上下文污染。

## 功能

1. **Micro-Rest** - 快速上下文修剪
2. **Deep Sleep** - 每日日志整合到长期记忆
3. **CortexGraph 同步** - 同步到 CortexGraph（带遗忘曲线）
4. **Dreaming** - 后台模拟（可选）

## 工具

### sleep_status
检查 agent 是否"累了"（基于运行时间或 token 使用）
```bash
python3 scripts/sleep_status.py
```

### run_sleep_cycle
触发睡眠周期
- **Light**: 压缩最近日志
- **Deep**: 归档 + 文件清理
- **CortexGraph**: 同步到 CortexGraph
```bash
python3 scripts/run_sleep_cycle.py --mode [light|deep|cortexgraph]
```

### schedule
设置生物钟（cron jobs）
```bash
python3 scripts/schedule.py --set "0 3 * * *"  # 3 AM 睡眠
```

## 工作流程

### Deep Sleep 模式
```
1. 触发 → Cron 在 3:00 AM 启动
2. 读取 → memory/YYYY-MM-DD.md（昨天日志）
3. 提取 → 高价值洞察
4. 追加 → 到 MEMORY.md
5. 归档 → 原始日志到 memory/archive/
6. 清理 → 删除临时文件
```

### CortexGraph 模式
```
1. 读取 → MEMORY.md + daily logs
2. 同步 → 到 CortexGraph
3. 应用 → 遗忘曲线（自动衰减）
4. 晋升 → 高价值记忆到 LTM
```

## 遗忘曲线

CortexGraph 使用 Ebbinghaus 遗忘曲线：
```
score = (use_count)^β × e^(-λ × Δt) × strength
```

- **β** = 0.6（使用频率权重）
- **λ** = ln(2) / half_life（默认 3 天）
- **strength** = 1.0-2.0（重要性）

## 使用

### 手动触发
```bash
# 轻量睡眠
python3 scripts/run_sleep_cycle.py --mode light

# 深度睡眠
python3 scripts/run_sleep_cycle.py --mode deep

# CortexGraph 同步
python3 scripts/run_sleep_cycle.py --mode cortexgraph
```

### 定时设置
```bash
# 每天凌晨 3 点深度睡眠
python3 scripts/schedule.py --set "0 3 * * *"

# 每 6 小时 CortexGraph 同步
python3 scripts/schedule.py --set "0 */6 * * *"
```

## 目录结构

```
agent-sleep/
├── SKILL.md
├── AGENT.md
├── scripts/
│   ├── run_sleep_cycle.py
│   ├── sleep_status.py
│   └── schedule.py
└── memory/
    ├── archive/        # 归档的日志
    └── consolidated/   # 整合的记忆
```

## 配置

### 环境变量
```bash
# CortexGraph 配置
export CORTEXGRAPH_STORAGE_PATH=~/.config/cortexgraph/jsonl
export CORTEXGRAPH_DECAY_MODEL=power_law
export CORTEXGRAPH_PL_HALFLIFE_DAYS=3.0
```

### ClawHub 配置
```bash
clawhub install agent-sleep
```

## 最佳实践

1. **每日 Deep Sleep** - 凌晨 3 点
2. **每 6 小时 CortexGraph 同步** - 保持记忆新鲜
3. **每周 GC** - 清理低分记忆
4. **每月晋升** - 高价值记忆升级到 LTM

## 与其他 Skill 集成

| Skill | 集成方式 |
|-------|----------|
| memory-sync-cn | 使用其脚本同步到 CortexGraph |
| agent-library | 使用其压缩功能 |
| cortexgraph | 直接调用 MCP 工具 |

---

*版本: 1.1.0*
*更新: 添加 CortexGraph 支持*
