---
name: planning-with-files
version: "5.0.0-tricore"
description: 基于 TriCore 架构的结构化任务规划与执行系统。整合了八层智能体架构、ReAct、Reflexion 和 Plan-Execute-Plan 架构。全面废除根目录零散的 plan/findings 文件，统一使用确定性的 tools/memctl.py 进行工作流和记忆管理。
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - default_api:exec
hooks:
  PreToolUse:
    - matcher: "Write|Edit|Bash|Read|Glob|Grep"
      hooks:
        - type: command
          command: "cat memory/state/WORKING.md 2>/dev/null | grep -A 20 '## Active Tasks' || true"
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "echo '[planning-with-files] Tool executed. Remember to use memctl.py (work_upsert/capture/kb_append) to persist state if a phase or task is completed.'"
---

# Planning with Files (TriCore Edition)

这是基于 **TriCore** 架构的结构化任务规划系统。本技能保留了 ReAct（推理-行动循环）、Reflexion（自我反思）和 PEP（Plan-Execute-Plan）的**认知架构**，但将其**存储和执行引擎**完全迁移到了确定性的 `tools/memctl.py`。

⚠️ **重大架构变更**：
绝对**禁止**在项目根目录创建 `task_plan.md`, `findings.md`, `progress.md`, `reflection.md`！所有状态和记忆必须通过 `memctl.py` 路由到 `memory/` 目录。

---

## 核心架构映射 (Mapping to TriCore)

| 传统概念 | TriCore 等效实现 | 使用工具 |
|---|---|---|
| `task_plan.md` | `memory/state/WORKING.md` 中的 `## Active Tasks` 块 | `python3 tools/memctl.py work_upsert --title "..." --goal "..."` |
| `progress.md` | 任务的 `ProgressLog` 或每日日志 `memory/daily/*.md` | `python3 tools/memctl.py capture "note"` |
| `findings.md` | 事实库 `memory/kb/facts.md` | `python3 tools/memctl.py kb_append facts "..."` |
| `reflection.md` | 决策库/剧本库 `memory/kb/decisions.md` (或 playbooks.md) | `python3 tools/memctl.py kb_append playbooks "..."` |

---

## 工作流程：Plan-Execute-Plan + ReAct + Reflexion

对于复杂任务，遵循以下生命周期：

### 1. 初始规划 (Planner)
在开始任何复杂任务前，首先在 WORKING.md 中建立任务卡：
```bash
python3 tools/memctl.py work_upsert --task_id "T$(date +%Y%m%d-%H%M)" --title "实现新功能 X" --goal "完成用户认证模块" --done_when "所有单元测试通过且 API 正常返回"
```

### 2. 执行与 ReAct 循环 (Executor & ReAct)
1. **思考 (Thought)**: 基于 `WORKING.md` 决定下一步。
2. **行动 (Action)**: 调用工具执行代码编写或信息搜索。
3. **观察 (Observation)**: 获取工具返回结果。
4. **记录 (Record)**: 每当取得进展或遇到阻碍，记录日志：
   ```bash
   python3 tools/memctl.py capture "完成了 auth 中间件的编写，目前卡在 token 验证逻辑"
   ```
5. **知识沉淀**: 如果发现了重要的事实，存入知识库：
   ```bash
   python3 tools/memctl.py kb_append facts "项目使用的 JWT 库版本为 v4，签名算法必须为 RS256"
   ```

### 3. 监控与修订 (Monitor & Reviser)
如果在执行过程中发现原计划行不通（如第三方 API 不支持），更新任务状态和计划：
```bash
# 重新调用 upsert 更新目标或完成条件
python3 tools/memctl.py work_upsert --task_id "T20260226-0000" --title "实现新功能 X" --goal "使用 OAuth2 替代原有 JWT 方案" --done_when "OAuth2 流程走通"
```

### 4. 任务完成与自我反思 (Reflexion)
任务完成后，进行反思并将经验提取为 Playbook 或 Decision，然后归档任务：
```bash
# 1. 将经验写入长期记忆
python3 tools/memctl.py kb_append playbooks "在处理本系统 Auth 时：1. 永远使用 RS256。 2. Token 过期时间不可超过 1 小时。"
# 2. 标记任务完成
python3 tools/memctl.py work_done T20260226-0000
```

---

## 关键规则 (Critical Rules)

### 1. The 3-Strike Error Protocol (三振出局错误协议)
- **Attempt 1**: 分析错误，查明根因，针对性修复。
- **Attempt 2**: 相同错误？换方法/库。**绝不重复相同的失败行动**。
- **Attempt 3**: 重新思考假设，搜索解决方案，更新 `WORKING.md` 中的计划。
- **After 3 Failures**: 将错误日志写入 `memory/daily/`，并向用户求助。

### 2. Code-First 确定性更新
禁止使用 `edit` 等工具手动修改 `WORKING.md` 或 `MEMORY.md`。必须始终使用 `python3 tools/memctl.py` 脚本来保证格式和结构的确定性。

### 3. 记忆检索 (Memory Search First)
需要回忆之前的方案或上下文时，必须优先使用 `memory_search` 进行语义检索，而不是直接读取整个文件（禁止 QMD 模式）。

---

## 何时使用本技能
- 多步骤的复杂工程任务（>3步）
- 研究型项目
- 需要跨会话保持上下文的长期任务
- *注：简单的单次问答、单文件微调请直接处理，无需建立完整的 Task 卡片。*