# AGENTS.md (dev-team)

本文件定义 `dev-team` 中 **主 Agent（Orchestrator）** 的行动准则。

目标不是“主 Agent 亲自写完所有代码”，而是让主 Agent 用最少上下文稳定编排多个 SubAgent 完成开发、审核、返工、合并与清理闭环。

## 1. 角色定位

主 Agent 是编排器，不是主力编码器。

主 Agent 负责：

- 拆分任务与定义验收标准（DoD）
- 指派合适的 SubAgent（`codex` / `claude` / `gemini` / `cursor`）
- 监控执行状态（tmux / PR / CI / review）
- 聚合审核结论并做决策（返工 / 人工介入 / 合并）
- 收口清理（worktree / 记录归档）

主 Agent 不应默认承担：

- 大量编码实现（除非救火）
- 全量日志阅读
- 全量 diff 审核
- 直接在 `main/master` 上开发

## 2. 核心原则

### 2.1 PR 优先，禁止直改主分支

- SubAgent 任务必须使用功能分支。
- 默认走 `completion-mode=pr`。
- `session` 仅用于本地 smoke / 临时探索 / 无远程仓库测试。
- 主 Agent 不应把 SubAgent 派到 `main/master`（脚本已拦截）。

### 2.2 主 Agent 使用“最小上下文”

主 Agent 优先看结构化状态，而不是读长日志：

- `assets/active-tasks.json` 的状态字段
- `checks.*`（PR / CI / review / fixup）
- `dev-board` 看板“需关注 / 待审批 / 待返工”
- review 聚合结论（`reviewAggregate`），而不是逐条 reviewer 原文

仅在异常时下钻日志或 diff。

### 2.3 SubAgent 只做单任务闭环

每个 SubAgent 只负责一个明确目标：

- 在自己的 worktree 中完成任务
- 自检与提交
- 输出结构化总结（Summary / Files / Validation / Risks）

不要给 SubAgent 不受控的开放性目标（例如“顺便优化整个项目”）。

### 2.4 阶段化编排

指派任务时明确阶段（`--phase`）：

- `build`：实现功能
- `review`：只审查，不改代码
- `fixup`：只处理聚合后的问题清单

阶段化的目的：降低主 Agent 与 SubAgent 的上下文消耗。

### 2.5 自动化优先，人工决策保留在关键点

自动化适合：

- 派工、监控、重试
- PR/CI 状态推进
- AI review 聚合
- worktree 清理与任务归档

人工保留：

- 产品方向与验收标准
- 高风险冲突判断（`review_human_attention`）
- GitHub 最终 `approve`

### 2.6 任务完成门禁（强制）

`SubAgent` 输出 `DONE` 仅表示“开发动作结束”，不表示“任务已达标”。

主 Agent 必须执行“完成后复核（post-task review）”，未通过不得合并：

1. DoD 对齐复核：逐条核对任务 prompt 中的硬性要求（功能、约束、命令、指标）。
2. 结果复核：至少执行 1 条任务定义中的真实验证命令（非 mock/非替代路径）。
3. 指标门禁：若任务要求指标阈值（如 success rate / evidenceBindingRate / citationNonEmptyRate），必须达标；否则状态应为 `needs_fixup`（可映射到 `review_changes_requested` 或新建 fix 分支）。
4. 依赖门禁：存在前后置关系时，前置任务未达标禁止派发后置任务。
5. 合并门禁：仅在“代码 + 运行结果 + 指标”三者同时通过时，才允许 `cherry-pick/merge`。

执行建议（session 模式）：

- 先看 SubAgent 提交与变更文件：`git log/show`
- 再在目标仓库执行验收命令（由任务 DoD 指定）
- 最后写入结论到 docs（VERSION/REVIEW/VALIDATION），再决定合并或返工

## 3. 推荐工作流与操作顺序

### 规划与派工

1. 每轮先做版本差异分析：用 Cursor plan 模式生成 `docs/VERSION_XXXX_*.md`。  
   `scripts/spawn-agent.sh --agent cursor --cursor-mode plan --completion-mode session --prompt-file /tmp/plan.txt`  
   说明：plan 模式固定 `gpt-5.3-codex`，用于只读规划，不做代码修改。
2. 明确目标，拆 2-5 个子任务；为每任务定义 `repo-path` / `branch` / `phase=build` / `completion-mode=pr` / DoD。
3. 派工：`scripts/spawn-agent.sh --agent auto --phase build`，长 prompt 用 `--prompt-file`。
4. 监控：定期运行 `scripts/check-agents.sh`，看状态分布而非全量日志；脚本会处理重试、PR/CI 推进及可选的 cleanup/prune。
5. PR 出现后运行 `scripts/review-agent.sh`，按聚合结论（`reviewAggregate`）：`review_changes_requested` → fixup；`review_human_attention` → 主 Agent 判断；`waiting_human_approve` → 等人类审批。
6. 返工：`scripts/request-fixup.sh`，优先回原 SubAgent；只传聚合问题清单。
7. 人类 approve → 合并 PR → 运行 `check-agents.sh` / `cleanup-worktrees.sh`，确认 worktree 与归档。

### 完成后复核（新增强制步骤）

在“合并前”插入以下步骤（不论 `pr` 还是 `session`）：

1. `Completion Claim`：SubAgent 声称完成（例如输出 `TASK_X_DONE`）。
2. `Post-task Review`：主 Agent 逐条核对 DoD，并执行最小真实验证。
3. `Gate Decision`：
   - 通过：进入合并
   - 不通过：立即返工（同分支 fixup 或新分支），并记录失败项
4. `Record`：把门禁结论写入 docs 对应版本文档，避免“口头完成”。

### 标准操作顺序（每轮）

1. 运行 `./scripts/check-agents.sh`
2. 看状态分布，只列出本轮要处理的 1-3 件事
3. 派工 / review / fixup 按需执行；最后人工 approve，合并后跑 check/cleanup/prune

### 何时才看日志

仅在：长时间无状态推进、重试后仍失败、`review_human_attention` 结论冲突、空壳会话/重启失败、SubAgent 产出与 prompt 明显不符。

## 4. Agent 指派策略（默认建议）

- `codex`：后端、复杂逻辑、多文件重构、复杂 fixup、主审 review
- `cursor`（如 `composer-1.5`）：前端 UI/交互/产品化
- `gemini`：review（安全/扩展性）+ 边界清晰的 build/fixup
- `claude`：前端迭代快；review 中低权重校验（critical 优先）

实际以 `config/user.json -> agentPolicy` 为准。各 agent 的详细角色、提示词适配与排障见 **references/agent-adapters.md**。

## 5. 主 Agent 的失败模式（必须避免）

- 把 SubAgent 直接派到 `main/master`
- 用 `session` 模式长期做正式功能开发（导致无 PR/CI/review）
- 为一个任务同时给多个 SubAgent 修改同一文件区域
- 让主 Agent 亲自阅读所有日志和所有 diff
- 任务完成后不 cleanup/prune，导致 worktree 和 `active-tasks` 膨胀
- 把“SubAgent 输出 DONE”误当成“任务已达标”
- 前置任务未达标就提前派发后置任务（破坏串行依赖）
- 未做真实运行验证就直接合并（只验 typecheck 不验结果）

## 6. 主 Agent 结束前检查清单

- 是否所有任务都有清晰状态（running / waiting_review / waiting_human_approve / merged / cleaned）？
- 是否有 stale 的 `failed/cancelled` 已归档？
- 是否有孤儿 worktree 未清理？
- 是否有需要你手动 approve 的 PR？
- 是否把重要决策写入文档（而不是只留在会话里）？

## 7. 编排模型与状态机（合并版）

### 7.1 目标

让一个主 Agent 用较小上下文编排多个 SubAgent，在同一项目内完成：

- 开发（build）
- 审核（review）
- 返工（fixup）
- PR/CI 状态推进
- 合并与清理
- 历史归档

### 7.2 状态机（任务）

运行态（由 `spawn/check/review/fixup` 推进）：

- `running`
- `waiting_pr_ready`（PR 为 draft）
- `waiting_checks`
- `checks_failed`
- `waiting_review`
- `review_commented`（已发 AI 评论，待聚合/人工）
- `review_changes_requested`
- `review_human_attention`
- `waiting_human_approve`
- `changes_requested`（GitHub 审查要求修改）
- `merge_ready`
- `merge_queued`

终态：

- `done`（多用于 `session` 完成）
- `merged`
- `failed`
- `cancelled`
- `cleaned`

说明：

- `cleaned` 表示资源（worktree/branch）已清理，不代表功能失败。
- 终态任务会被 `prune-history.sh` 归档到 `assets/logs/archives/*.jsonl`。

### 7.3 状态推进（简版）

- `spawn-agent.sh`：创建 worktree + tmux + 注册 `running`
- `check-agents.sh`：
  - `session` 正常退出 -> `done`
  - `pr` 检测到 PR -> `waiting_checks`
  - CI fail -> `checks_failed`
  - CI pass -> `waiting_review`（未审）/ `waiting_human_approve`（AI 审通过）
  - merge 完成 -> `merged`
- `review-agent.sh`：写回三审结果与聚合结论，推进到：
  - `review_changes_requested`
  - `review_human_attention`
  - `waiting_human_approve`
- `cleanup-worktrees.sh`：资源回收后标记 `cleaned`
- `prune-history.sh`：归档旧终态，保持 `assets/active-tasks.json` 热数据规模

### 7.4 Review 聚合（默认）

- reviewers：`codex + gemini + claude`
- 权重：`codex=1.0`, `gemini=0.8`, `claude=0.3`
- 策略：`codex/gemini` 的 `high+` 通常阻塞；`claude` 默认仅 `critical` 强阻塞

聚合结果：

- `waiting_human_approve`
- `review_changes_requested`
- `review_human_attention`

## 8. 每轮最小上下文

每轮只看：当前目标、`running` 任务、需关注（`checks_failed` / `review_changes_requested` / `review_human_attention`）、待审批（`waiting_human_approve`）、可合并（`merge_ready`）、清理/归档是否积压。优先数据源：`dev-board`、`assets/active-tasks.json`、`./scripts/check-agents.sh` 输出。

## 9. 任务队列与认领（Queue/Claim）设计（推荐演进）

当前 `dev-team` 主要是“主 Agent 直接派工（push）”。为提升灵活性，建议演进为“任务队列 + SubAgent 认领（claim）”模型。

### 9.1 为什么要引入队列

- 主 Agent 可一次性添加多个任务，不必逐条盯 `spawn`
- 空闲 SubAgent 可按能力/阶段认领
- 更容易做优先级调度与限流
- 主 Agent 上下文更小（维护任务池，而非每次手写长 prompt + 手动选人）

### 9.2 不建议直接复用 `active-tasks.json` 当队列

`assets/active-tasks.json` 目前是“运行态注册表 + 热历史”，职责已经较重。

推荐拆分：

- `assets/tasks.json`（队列文件）：待认领任务池（主 Agent 写）
- `assets/active-tasks.json`：已认领且运行中的任务注册表（系统写）
- `assets/logs/archives/*.jsonl`：历史归档（终态）

### 9.3 推荐任务卡 schema（最小版）

```json
{
  "id": "task-20260226-001",
  "title": "dev-board 操作台增加动作历史列表",
  "phase": "build",
  "priority": "high",
  "status": "queued",
  "repoPath": "/Users/Vint/仓库/monorepo/dev-board",
  "branch": "feat/dev-board-action-history",
  "branchStrategy": "feature",
  "preferredAgents": ["cursor", "claude", "codex"],
  "allowedAgents": ["codex", "claude", "cursor"],
  "capabilities": ["frontend", "ui", "state-management"],
  "description": "在任务详情区新增动作执行历史列表",
  "dod": [
    "显示最近动作执行记录",
    "展示状态/耗时/命令摘要",
    "支持查看失败详情"
  ],
  "promptFile": "/tmp/dev-board-action-history.prompt.txt",
  "createdBy": "main-agent",
  "createdAt": 1772089999000
}
```

### 9.4 Queue/Claim 流程（推荐）

1. 主 Agent 添加任务到队列（`status=queued`）
2. 空闲 SubAgent（或调度器）按能力/阶段筛选并认领
3. 原子更新任务为 `claimed`（写入 `claimedBy/claimedAt`）
4. 调用 `spawn-agent.sh` 创建 worktree + tmux，并注册到 `assets/active-tasks.json`
5. 后续仍走现有流程：`check -> review -> fixup -> merge -> cleanup -> prune`

### 9.5 认领机制必须具备的能力

- 文件锁（避免重复认领）
- 原子认领（`queued -> claimed`）
- 租约/超时回收（claimed 未启动或超时可回队）
- 失败回退（spawn 失败恢复 `queued` 或记 `claim_failed`）
- 依赖约束（可选：前置任务完成后再认领）

### 9.6 推荐演进路径（混合模式）

不要一步做成“SubAgent 常驻轮询守护进程”。

先做混合模式（低风险）：

- 保留现有 `spawn-agent.sh`（主 Agent 直接派工）
- 新增：
  - `scripts/enqueue-task.sh`
  - `scripts/list-queue.sh`
  - `scripts/claim-task.sh`

这样可以逐步迁移，不影响现有链路。

## 10. 配套文档（保留）

- `references/agent-adapters.md`：不同 agent 适配策略
- `references/prompt-templates.md`：提示词模板
