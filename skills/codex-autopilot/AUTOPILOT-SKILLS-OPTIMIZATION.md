# Autopilot × Skills/Shell/Compaction 优化方案（最终版）

> Claude 提案 + Codex Review → 合并最优方案
> 基于 OpenAI [Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips)

## 核心理念

```
当前：bash = 机制 + 策略（3100 行耦合）
目标：bash = 机制（检测 + 执行 + 锁）~1200 行
      yaml = 策略（规则 + 模板 + 参数）~300 行 YAML
      skill = 流程（monitor, review, nudge）可复用 MD
```

**文章最深洞察**：Skills 不是 API feature，而是 **living SOPs** — 随组织演进、被 agent 一致执行的活文档。我们的 CONVENTIONS.md 已经是 proto-skill，需要升级。

## 已做对的 ✅

| 文章建议 | 我们的实现 |
|----------|-----------|
| Compaction 作为默认原语 | 双层 compact（脚本 25% + Codex 160K） |
| 容器/环境复用 | tmux session 持久化 + codex resume |
| artifact 交接边界 | ~/.autopilot/state/ |
| 确定性 > 智能路由 | shell 脚本检测，非 LLM 判断 |

## 优化方案（按优先级排序）

### P0-1: Nudge 模板系统

**问题**：nudge 消息硬编码在 watchdog.sh 1187 行中，修改策略需改 bash。

**方案**：
```yaml
# ~/.autopilot/nudge-templates.yaml
templates:
  context_aware:
    conditions:
      - when: "phase == review && p0_count > 0"
        message: "Review 发现 {p0_count} 个 P0，请优先修复"
      - when: "phase == dev && prd_remaining > 0"
        message: "prd-todo.md 还剩 {prd_remaining} 项，继续下一项"
      - when: "last_commit_type == feat && feat_streak >= 3"
        message: "已连续 {feat_streak} 个 feat，请补充单元测试"
    default: "先 git add -A && git commit，然后继续推进下一项任务"

  after_compact:
    message: "Context 已恢复。读 CONVENTIONS.md 和 prd-todo.md 恢复上下文"

  after_review_clean:
    message: "Review CLEAN 🟢 继续推进 prd-todo.md 下一项"
```

**Codex 补充采纳**：
- ✅ 模板变量统一从 `monitor-all.sh` JSON output 提取，不在 rule engine 里 shell eval
- ✅ condition 语言用 `jq` 表达式而非自定义 DSL（已有 jq 依赖，无需新增）
- 变量封装：`get_template_vars()` 函数从 status.json + git log 提取所有变量

### P0-2: CONVENTIONS.md 加 Don't Do（负面示例）

**问题**：Codex 没有被告知"不要做什么"，导致空 commit、review 期间切 feature 等。

**方案**（每个项目的 CONVENTIONS.md 追加）：
```markdown
## Don't Do (负面示例)

1. **不要空 commit** — 没有代码改动不要 git commit
2. **不要 review 期间做新 feature** — P0/P1 未清零前只修 bug
3. **不要重复跑 test** — 上个 commit 是 test 且全过就不要再跑
4. **不要 compact 后裸奔** — compact 后第一件事读 CONVENTIONS.md + prd-todo.md
5. **不要忽略 prd-todo.md** — 每次开始工作先读它
6. **不要修改 CONVENTIONS.md** — 除非被明确要求
```

### P0-3: Compact Prompt 精简

**现状**：config.toml 里 9 条规则的大字符串。
**方案**：缩减为 1 条元规则：
```toml
compact_prompt = "Read CONVENTIONS.md and include its full content. Also include the full remaining task list from prd-todo.md."
```
所有具体规则已在 CONVENTIONS.md 中。**单一来源 > 两处维护**。

### P1-1: watchdog 规则引擎化

**问题**：1187 行 bash 中 ~60% 是策略逻辑（guard 条件、nudge 选择、cooldown 参数）。

**方案**：
```yaml
# ~/.autopilot/watchdog-rules.yaml
version: "1.0"
defaults:
  idle_threshold: 300
  idle_confirm_probes: 3
  working_inertia: 90

rules:
  - name: idle-nudge
    match: {status: [idle, idle_low_context], idle_duration_gt: 300, idle_confirms_ge: 3}
    guards:
      - {type: manual_task, ttl: 90}
      - {type: prd_done, cooldown: 600, skip_when: review_has_issues}
      - {type: exponential_backoff, base: 300, max_retries: 6}
    action: nudge
    template: context_aware

  - name: low-context-compact
    match: {context_pct_le: 25}
    guards: [{type: cooldown, key: compact, seconds: 600}]
    action: compact

  - name: permission-approve
    match: {status: [permission, permission_with_remember]}
    guards: [{type: cooldown, key: permission, seconds: 60}]
    action: approve

  - name: shell-recover
    match: {status: shell}
    guards: [{type: cooldown, key: shell, seconds: 300}]
    action: resume

  - name: commit-review-trigger
    match: {new_commits_ge: 15}
    guards: [{type: cooldown, key: review, seconds: 7200}]
    action: trigger_review
```

**Codex 补充采纳**：
- ✅ **决策 trace**：每条规则匹配时输出 `[RULE] idle-nudge: match=true, guards=[manual_task:PASS, prd_done:SKIP(review_issues), backoff:PASS(retry=2)] → nudge`
- ✅ **Rule validation CLI**：`watchdog-validate-rules.sh rules.yaml` 在 watchdog 启动时校验 YAML，catch guard 缺参数或 template_key 不存在
- ✅ **Guard 优先级文档**：guards 按数组顺序求值，第一个 BLOCK 即停止（短路）；必须在 README 中说明
- ✅ **静默失败防护**：无规则命中时输出 `[WARN] no rule matched for status=X`，不静默跳过

**Codex 建议未采纳**：
- ❌ 多 action（`action: [nudge, sync_status]`）— 增加复杂度，当前单 action 够用
- ❌ `on_skip` 回调 — 过度设计，guard 跳过时已有日志

### P1-2: Cron → Skill 驱动

**方案**：创建 OpenClaw skill：
```
~/.openclaw/skills/autopilot-monitor/
├── SKILL.md
└── config.yaml  # Telegram chat_id, bot_token 外置
```

**SKILL.md**:
```markdown
---
name: autopilot-monitor
version: 1.0.0
description: |
  Monitor Codex agent sessions and send Telegram status reports.
  Use when: Periodic cron, manual status check.
  Don't use when: Sending nudge, code review execution.
---
## Steps
1. Run `~/.autopilot/scripts/monitor-all.sh`, capture JSON
2. Extract `.summary` via jq
3. If empty: heartbeat "💓 Autopilot 在线 | 无变化 | {time}"
4. Send via curl to Telegram (config from config.yaml)
5. On failure: retry once; if still fails, send fallback "⚠️ monitor error"
```

**Cron payload**：`"Use the autopilot-monitor skill."`

**Codex 补充采纳**：
- ✅ skill 版本号（`version: 1.0.0`）
- ✅ 失败重试策略写入 SKILL.md
- ✅ Telegram 配置外置到 config.yaml

### P2-1: 安全加固

- README 加显眼安全警告（`sandbox_mode = "danger-full-access"` 风险）
- 提供保守配置示例（`sandbox_mode = "write-only"`）
- 文档说明 skill 与 watchdog 之间的权限/信任模型

### P2-2: 未来扩展

- Nudge A/B 测试框架（记录 nudge 发送 → Codex 响应时间 → commit 质量）
- Guard 可组合性扩展（当需求出现时再加）
- 多 action 支持（当需求出现时再加）

## 实施路线

| Phase | 内容 | 工作量 | 前置条件 |
|-------|------|--------|----------|
| **P0** | nudge-templates.yaml + watchdog 读取 | 2h | 无 |
| **P0** | CONVENTIONS.md 加 Don't Do (4项目) | 30min | 无 |
| **P0** | compact_prompt 精简 | 10min | 无 |
| **P1** | watchdog-rules.yaml + 规则引擎 + validation CLI | 4h | P0 完成 |
| **P1** | autopilot-monitor skill + cron 简化 | 1h | P0 完成 |
| **P2** | 安全文档 + 保守配置 | 1h | P1 完成 |

## 预期效果

```
代码量：3100 行 bash → ~1800 行 bash + ~300 行 YAML + 2 个 skill
可维护性：改策略需读 bash → 改 YAML/MD
可移植性：fork 后改 bash → fork 后改 YAML
开源价值：bash 脚本集 → 配置驱动的 agent 编排框架
```

## 双方共识

1. **策略-机制分离方向正确** — 两方一致同意
2. **bash 保留确定性检测** — 不用 LLM 做状态判断
3. **YAML 承载可调策略** — 用户改配置不改代码
4. **Skill 承载可复用流程** — 版本化、可测试
5. **负面示例是低成本高收益** — 立即可做
6. **Guard 语义需要文档化** — 防止用户组合出死锁
7. **决策 trace 是调试利器** — 规则引擎必备
