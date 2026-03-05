# 执行模式

Phase 5 实现阶段支持三种执行模式。默认 Step Mode。

## Step Mode（默认）

逐任务执行，每个任务完成后等待用户确认。

**触发词**: "start implementation", "开始执行"

**适用场景**: 复杂任务、需要仔细审查、首次使用 spec-flow

**流程**:
```
User: start implementation

AI: 🔄 Task T-001: [description]
    [Executes task]
    ✅ Completed (1/10)
    👉 Say "continue" for next task

User: continue

AI: 🔄 Task T-002: [description]
    ...
```

## Batch Mode

一次性执行所有剩余任务。

**触发词**: "execute all", "全部执行", "batch mode", "批量执行", "一口气执行完"

**适用场景**: 简单任务、信任计划、追求速度

**流程**:
```
User: execute all tasks

AI: ⚡ Batch Mode Activated

    🔄 T-001: [description] → ✅
    🔄 T-002: [description] → ✅
    🔄 T-003: [description] → ✅

    📊 Batch Complete: 10/10 tasks done
```

**规则**:
- 每个任务完成后仍需更新 tasks.md
- 任何任务失败立即停止
- 用户可用 "stop"/"暂停" 中断

## Phase Mode

按阶段批量执行（Setup → Core → Testing → Docs），每个阶段完成后等待确认。

**触发词**: "execute phase 1", "执行第一阶段", "execute setup"

**流程**:
```
User: execute setup phase

AI: 📦 Phase Mode: Setup

    🔄 T-001: [description] → ✅
    🔄 T-002: [description] → ✅

    ✅ Setup Phase Complete (2/10 total)
    Next phase: Core Implementation
    👉 Say "continue" or "execute next phase"
```

## 所有模式通用规则

### 执行前必做

1. 读取 tasks.md — 获取当前任务列表和状态
2. 确认目标任务 — 根据模式确定执行范围
3. 检查依赖 — 确保前置任务已完成（`- [x]`）
4. 读取 design.md — 查看相关设计

### 执行后必做

- 更新 tasks.md 状态（`- [ ]` → `- [x]`）
- 显示进度

### 何时停止

- 任务失败或报错
- 设计文档不完整
- 依赖缺失或被阻塞
- 任务描述模糊
- 需要 design.md 中未覆盖的决策
