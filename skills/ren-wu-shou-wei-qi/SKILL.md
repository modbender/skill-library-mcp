---
name: 任务收尾器
description: "name: 任务收尾器 version: 1.0.2 description:
  强制任务收尾与证据提交。确保每个任务都有明确的目标、进度、下一步和完成证据。"
---

﻿---
name: 任务收尾器
version: 1.0.2
description: 强制任务收尾与证据提交。确保每个任务都有明确的目标、进度、下一步和完成证据。
---

# 任务收尾器

强制任务收尾，确保每个任务都有明确的完成证据。防止任务中途停滞、无证据完成。

## 为什么需要这个技能

**问题**: AI 代理经常：
- 任务中途停止，无解释
- 只输出计划，不执行
- 缺少明确的完成标准
- 没有证据工件

**解决方案**: 此技能强制执行：
- 每个实质性步骤输出目标/进度/下一步
- 完成时必须提供证据
- 多步骤任务必须有完成证明格式

## 工作流程

### 1. 任务启动

每个任务开始时输出：

```markdown
**目标**: 完成时是什么样子
**进度**: 已完成什么
**下一步**: 现在执行的一个具体行动
```

### 2. 执行中更新

每个实质性步骤后更新进度：

```markdown
**进度更新**:
- 已完成：步骤 1, 2
- 当前：执行步骤 3
- 阻塞：无（或具体阻塞 + 已尝试 + 最小解锁输入）
```

### 3. 完成证明格式

2 步以上的任务必须包含：

```markdown
**DONE_CHECKLIST**:
- [ ] 项目 1 已完成
- [ ] 项目 2 已完成

**EVIDENCE**:
- 已执行：命令/操作摘要
- 工件：路径/URL/ID
- 已验证：检查命令结果

**NEXT_AUTONOMOUS_STEP**:
- 一个无需用户输入即可执行的后续步骤
```

### 4. 反停滞规则

- 仅计划的回复：最多 1 次
- 下一次回复必须包含执行证据
- 永远不要以"我现在将..."结束而不显示工具结果

## 可执行完成标准

任务完成当且仅当：

| 标准 | 验证 |
|------|------|
| 目标已陈述 | Select-String "目标" memory/{date}.md 匹配 |
| 进度已追踪 | Select-String "进度" memory/{date}.md 匹配 |
| 下一步已定义 | Select-String "下一步" memory/{date}.md 匹配 |
| 证据存在 | 工件路径/URL 存在 |
| 无未解决标记 | Select-String "TODO|PENDING|TBD" artifact 无返回 |

## 使用示例

### 示例 1：发布技能到 ClawHub

```markdown
**目标**: 发布 skill 到 ClawHub，返回 URL 和 skill_id

**进度**: 
- 已完成：读取 SKILL.md，打开浏览器
- 当前：填写发布表单

**下一步**: 填写 Slug/Name/Version 字段

---

**进度更新**:
- 已完成：表单填写，文件上传
- 当前：等待发布确认
- 阻塞：无

---

**DONE_CHECKLIST**:
- [x] 技能已发布
- [x] URL 已验证可访问
- [x] skill_id 已记录

**EVIDENCE**:
- 已执行：clawhub publish 命令
- 工件：https://clawhub.ai/Dalomeve/my-skill
- skill_id: k97xxxxx
- 已验证：浏览器导航到 URL，200 OK

**NEXT_AUTONOMOUS_STEP**:
- 更新 INDEX.md 添加新技能条目
```

### 示例 2：研究 GitHub 热门项目

```markdown
**目标**: 研究 12+ GitHub 热门项目，提炼 3-5 个痛点，选择一个方向实现

**进度**:
- 已完成：浏览 GitHub Trending，记录 14 个项目
- 当前：分析痛点，选择方向

**下一步**: 编写研究报告到 outputs/

---

**DONE_CHECKLIST**:
- [x] 14 个项目已分析
- [x] 5 个痛点已识别
- [x] 研究方向已选择（验证空白）
- [x] 新项目已创建并发布

**EVIDENCE**:
- 研究报告：outputs/2026-03-01-github-research.md
- 新项目：https://github.com/Dalomeve/agent-audit-trail
- 测试通过：python test_audit_trail.py (4/4 tests passed)
- Commit: 03307bdc84abab4bd5e78ab51abcd271ca85a4ab

**NEXT_AUTONOMOUS_STEP**:
- 将新项目添加到长期任务追踪
```

## 隐私/安全

- 证据中不包含敏感数据
- 工件路径使用相对路径或工作空间路径
- 任务日志中不包含凭据

## 自触发

当以下情况时使用：
- 启动任何多步骤任务
- 中断后恢复
- 移交给另一个代理
- 用户要求"不要只给计划，直接执行"

## 与其他技能集成

- **task-finish-contract**: 英文版本，概念相同
- **agent-audit-trail**: 使用审计追踪记录证据
- **phoenix-loop**: 从失败中学习，更新收尾模式
- **HEARTBEAT.md**: 心跳检查任务收尾状态

## 限制

- 需要代理自觉遵守
- 证据验证是尽力的（URL 可能过期）
- 不适用于单步骤简单任务

## 参考

- `tasks/QUEUE.md` - 任务队列格式
- `memory/tasks.md` - 任务历史
- `skills/task-finish-contract/` - 英文版本

---

**有始有终。用证据证明。**