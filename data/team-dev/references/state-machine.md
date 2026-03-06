# 任务状态机（dev-team）

与脚本实现一致的状态定义。主 Agent 编排时以 `assets/active-tasks.json` 的 `status` 为准。

## active-tasks 状态

**运行/PR 管线态：**

| 状态 | 说明 |
|------|------|
| `running` | subagent 运行中 |
| `waiting_pr_ready` | PR 为 draft，等待就绪 |
| `waiting_checks` | 已创建 PR，等待 CI |
| `checks_failed` | 必需 CI 未通过 |
| `waiting_review` | CI 通过，等待 AI 审查 |
| `review_commented` | 已发 AI 审查评论，待聚合/人工 |
| `review_changes_requested` | 聚合结论要求修改 |
| `review_human_attention` | 需人工判断 |
| `waiting_human_approve` | AI 审通过，等待人工批准 |
| `changes_requested` | GitHub 审查要求修改 |
| `merge_ready` | 可合并 |
| `merge_queued` | 已触发自动合并 |

**终态：**

| 状态 | 说明 |
|------|------|
| `done` | session 模式正常结束 |
| `merged` | PR 已合并 |
| `failed` | 执行失败（含重试耗尽） |
| `cancelled` | 人工取消 |
| `cleaned` | worktree/分支已清理 |

## 队列任务（assets/tasks.json）

- `queued` / `claimed` / `dispatched` / `dispatch_failed`

## 状态推进

- `spawn-agent.sh` → `running`
- `check-agents.sh` → session 退出 `done`；PR 创建 `waiting_checks`；CI/merge 推进
- `review-agent.sh` → `review_changes_requested` / `review_human_attention` / `waiting_human_approve` / `review_commented`
- `cleanup-worktrees.sh` → `cleaned`
- `prune-history.sh` → 归档终态到 `assets/logs/archives/`

详见 [AGENTS.md](AGENTS.md) §7.3。
