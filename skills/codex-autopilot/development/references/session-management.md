# 会话持久化管理

> 复杂任务的外部记忆。基于 Manus 的 Context Engineering 理念。

## 核心理念

```
Context Window = RAM (易失性, 有限)
Filesystem = Disk (持久性, 无限)

→ 重要信息必须写入磁盘
```

---

## 三文件模式

| 文件 | 用途 | 更新时机 |
|------|------|---------|
| `task_plan.md` | 阶段、进度、决策 | 完成每个阶段后 |
| `findings.md` | 研究、发现 | 每次重要发现后 |
| `progress.md` | 会话日志、测试结果 | 整个会话过程中 |

**默认位置**: 项目根目录 或 `docs/_session/`（如已有规范）

---

## 快速开始

### 自动初始化

```bash
# 在项目根目录运行
./AIWorkFlowSkill/development/scripts/init-session.sh "我的任务"
```

### 会话恢复

```bash
# 清除上下文后，恢复之前未同步的内容
python3 ./AIWorkFlowSkill/development/scripts/session-catchup.py "$(pwd)"
```

### 检查完成度

```bash
# 验证所有阶段是否完成
./AIWorkFlowSkill/development/scripts/check-complete.sh
```

---

## task_plan.md 模板

```markdown
# Task Plan: [任务名称]

## Goal
[任务目标一句话]

## Current Phase
Phase X

## Phases

### Phase 1: [阶段名]
- [ ] 步骤1
- [ ] 步骤2
- **Status:** in_progress / complete / pending

### Phase 2: [阶段名]
- [ ] 步骤1
- **Status:** pending

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 选择方案A | 因为XXX |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| 错误描述 | 1 | 解决方法 |
```

---

## findings.md 模板

```markdown
# Findings

## [YYYY-MM-DD] 发现标题
- **问题**: [描述]
- **调查**: [做了什么]
- **结论**: [得到什么结论]
- **相关代码**: `file.ext:line`

## 技术决策
| Decision | Rationale |
|----------|-----------|
|          |           |

## 参考资源
- [链接或说明]
```

---

## progress.md 模板

```markdown
# Progress Log

## [YYYY-MM-DD HH:MM] 进度更新
- **完成**:
  - 任务1
- **进行中**:
  - 任务2
- **阻塞**:
  - 问题描述

## Errors Log
| Error | Attempt | Result | Next Action |
|-------|---------|--------|-------------|
| 描述 | 1 | 失败/成功 | 下一步 |
```

---

## 关键规则

### 1. 先创建计划

**永远不要** 在没有 `task_plan.md` 的情况下开始复杂任务。

### 2. 2-Action Rule

> 每 2 次查看/浏览/搜索操作后，**立即** 将关键发现保存到文件。

这防止视觉/多模态信息丢失。

### 3. 决策前阅读

重大决策前，先阅读计划文件。保持目标在注意力窗口中。

### 4. 行动后更新

完成任何阶段后：
- 标记阶段状态: `in_progress` → `complete`
- 记录遇到的错误
- 记录创建/修改的文件

### 5. 记录所有错误

每个错误都记入计划文件，构建知识库防止重复。

### 6. 永不重复失败

```
if action_failed:
    next_action != same_action
```

跟踪尝试过的方法，变换策略。

---

## 3-Strike Error Protocol

```
尝试 1: 诊断 & 修复
  → 仔细阅读错误
  → 识别根因
  → 应用针对性修复

尝试 2: 替代方案
  → 同样错误? 尝试不同方法
  → 不同工具? 不同库?
  → 永不重复完全相同的失败操作

尝试 3: 更广泛的反思
  → 质疑假设
  → 搜索解决方案
  → 考虑更新计划

3 次失败后: 升级给用户
  → 解释尝试过什么
  → 分享具体错误
  → 请求指导
```

---

## 5-Question Reboot Test

上下文恢复后，如果能回答这 5 个问题，说明状态恢复良好：

| 问题 | 答案来源 |
|------|---------|
| 我在哪? | task_plan.md 中的当前阶段 |
| 我要去哪? | 剩余阶段 |
| 目标是什么? | 计划中的 Goal 声明 |
| 我学到了什么? | findings.md |
| 我做了什么? | progress.md |

---

## Read vs Write 决策矩阵

| 场景 | 操作 | 原因 |
|------|------|------|
| 刚写了文件 | **不要**再读 | 内容还在上下文中 |
| 查看了图像/PDF | **立即**写发现 | 多模态内容会丢失 |
| 浏览器返回数据 | 写入文件 | 截图不会持久化 |
| 开始新阶段 | 阅读计划/发现 | 重新定向（上下文可能过时） |
| 发生错误 | 阅读相关文件 | 需要当前状态来修复 |
| 间隔后恢复 | 阅读所有 planning 文件 | 恢复状态 |

---

## 何时使用此模式

**适用于:**
- 多步骤任务 (3+ 步)
- 研究类任务
- 构建/创建项目
- 跨多个工具调用的任务
- 需要组织的任何任务

**跳过:**
- 简单问题
- 单文件编辑
- 快速查找

---

## 自动启用规则

### 硬触发（任一条件满足即启用）
- Bug修复/调试/排查
- 研究/对比/方案选型
- 跨 >= 3 文件
- 外部系统变更（API/DB/第三方）

### 软触发
- 预计 > 30 分钟
- 任务拆解 >= 3 步
- 需要多轮沟通/确认

### 灰区判断
- 命中 2 项软触发 → 直接启用
- 仅 1 项 → 询问一次是否启用

### 动态升阶
- 出现错误/失败尝试 → 立即启用
- 多次查看/搜索仍未锁定方案 → 立即启用

### 用户覆盖
- 用户明确表示"不需要会话记录" → 跳过

---

## 更新规则速查

| 操作 | 更新文件 |
|------|----------|
| 完成一个步骤 | task_plan.md |
| 每 2 次查看/检索 | findings.md |
| 出现错误/失败尝试 | progress.md + task_plan.md (Errors) |
| 做出关键决策 | task_plan.md (Decisions) |
| 新会话开始 | 先读三文件 |

---

## 脚本路径

```
AIWorkFlowSkill/development/scripts/
├── init-session.sh      # 初始化三文件
├── check-complete.sh    # 检查完成度
└── session-catchup.py   # 会话恢复
```

---

## Anti-Patterns

| 不要 | 应该 |
|------|------|
| 用内存工具做持久化 | 创建 task_plan.md 文件 |
| 说一次目标就忘 | 决策前重读计划 |
| 隐藏错误并静默重试 | 记录错误到计划文件 |
| 把所有东西塞进上下文 | 大内容存到文件 |
| 立即开始执行 | **先**创建计划文件 |
| 重复失败的操作 | 跟踪尝试，变换策略 |
