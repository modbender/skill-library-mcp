---
name: restart-guard
version: 2.2.0
description: Deterministic OpenClaw gateway restart with down/up state-machine verification, origin-session proactive ACK, and backward-compatible config.
metadata: {"openclaw":{"requires":{"bins":["python3","curl"],"env":["GATEWAY_AUTH_TOKEN"],"env_any":["TELEGRAM_BOT_TOKEN","DISCORD_WEBHOOK_URL","SLACK_WEBHOOK_URL","RESTART_GUARD_WEBHOOK_URL","FEISHU_WEBHOOK_URL"]}}}
---

# Restart Guard

## Purpose / 目标

Safely restart gateway while preserving context and guaranteeing a post-restart report path to the user session.  
安全重启网关，保留上下文，并保证重启后可主动回报到用户会话。

## Trigger / 触发条件

Use this skill when the task involves OpenClaw gateway restart, watchdog recovery, or post-restart reporting.  
当任务涉及 OpenClaw 网关重启、看门狗恢复、重启后回报时使用。

Natural-language triggers (must auto-run, do not ask user for script commands):
- "可以重启了"
- "现在重启吧"
- "restart now"
- "go ahead and restart"

自然语言触发（必须自动执行，不让用户手工跑脚本）：
- “可以重启了”
- “现在重启吧”
- “restart now”
- “go ahead and restart”

## Required Preconditions / 前置条件

- `openclaw` CLI is available.
- Restart config exists (`config.example.yaml` or `config/restart-guard.yaml.example` copied to runtime path).
- Agent can execute shell commands.
- `openclaw` CLI 可用。
- 重启配置文件存在（从示例拷贝到运行路径）。
- agent 具备执行命令能力。

## Workflow / 标准流程

### 0) Default behavior / 默认行为

When user expresses restart intent without specifying channel details:
- Run full flow automatically via `scripts/auto_restart.py`.
- Default `--notify-mode origin`.
- Infer origin session key automatically (env/context/sessions), no user input required.
- Auto-discover external channels and persist `effective_notify_plan`.
- Before trigger, proactively announce disaster delivery route/channels to origin session.
- After restart event arrives, net summarizes result to user.

当用户仅表达重启意图且未指定渠道细节时：
- 使用 `scripts/auto_restart.py` 自动执行全流程。
- 默认 `--notify-mode origin`。
- 自动推断源会话 key（env/context/sessions），无需用户补参数。
- 自动发现外部渠道并写入 `effective_notify_plan`。
- 触发前先在源会话预告灾难通知路由与渠道。
- 收到重启事件后，由 net 向用户汇总结果。

### 1) Discover channels and mode / 发现渠道与模式（可选）

```bash
python3 <skill-dir>/scripts/discover_channels.py --config <config-path> --json
```

Ask user:
- notify mode (`origin` recommended, or `selected`, `all`)
- selected channel/target if needed

询问用户：
- 通知模式（推荐 `origin`，可选 `selected`、`all`）
- 若需要，指定渠道与目标

### 2) Write context / 写入现场

```bash
python3 <skill-dir>/scripts/write_context.py \
  --config <config-path> \
  --reason "config change" \
  --verify 'openclaw health --json' 'ok' \
  --resume "report restart result to user"
```

### 3) Execute restart / 执行重启

Recommended one-command entry:

```bash
python3 <skill-dir>/scripts/auto_restart.py \
  --config <config-path> \
  --reason "config change" \
  --notify-mode origin
```

推荐单命令入口：

```bash
python3 <skill-dir>/scripts/auto_restart.py \
  --config <config-path> \
  --reason "配置变更" \
  --notify-mode origin
```

```bash
python3 <skill-dir>/scripts/restart.py \
  --config <config-path> \
  --reason "config change" \
  --notify-mode origin \
  --origin-session-key <session-key>
```

Selected channel mode:

```bash
python3 <skill-dir>/scripts/restart.py \
  --config <config-path> \
  --reason "config change" \
  --notify-mode selected \
  --channel telegram \
  --target 726647436
```

### 4) Postcheck / 事后校验

```bash
python3 <skill-dir>/scripts/postcheck.py --config <config-path>
```

## Contract / 契约

- Event contract: `restart_guard.result.v1`
- Required fields: `status`, `restart_id`
- Context adds:
  - `restart_id`
  - `origin_session_key`
  - `notify_mode`
  - `channel_selection`
  - `effective_notify_plan`
  - `state_timestamps`
  - `diagnostics_file`
  - `delivery_status`
- Optional event fields:
  - `severity`
  - `failure_phase`
  - `error_code`
  - `delivery_attempts`
  - `delivery_route`
  - `delivery_exhausted`
  - `diagnostics_file`

## Notes / 注意事项

- `webui` is not treated as disabled notification anymore; origin-session ACK is primary path.
- `webui` 不再视为禁用通知；主路径是回发到发起会话。
- Verify/diagnostics commands run in strict non-shell mode.
- 校验/诊断命令以严格非 shell 模式执行（包含管道等 shell 元字符会被拒绝）。
- For implementation-level replication details, see `ENHANCED_RESTART_IMPLEMENTATION_SPEC.md`.
- 若需按工程级标准复刻实现，请参考 `ENHANCED_RESTART_IMPLEMENTATION_SPEC.md`。
- Do not expose internal scripts/steps unless user explicitly asks for internals.
- 除非用户明确要求细节，否则不要向用户暴露内部脚本步骤。
- Guardian uses strict success invariant:
  - `down_detected && start_attempted && up_healthy`
- Guardian success requires strict invariant:
  - `down_detected && start_attempted && up_healthy`

## Failure Handling / 故障处理

- On timeout/failure, guardian writes local diagnostics file (`restart-diagnostics-<restart_id>.md/json`), sends concise summary, and retries delivery within budget.
- 若超时或失败，guardian 会写本地诊断文件（`restart-diagnostics-<restart_id>.md/json`），发送简要摘要，并在预算内重试送达。
- Fixed disaster route: `origin session -> agent:main:main -> all discovered external channels`.
- 固定灾难路由：`源会话 -> agent:main:main -> 所有已发现外部渠道`。
- Guardian exits after successful delivery or budget exhaustion; no long-lived watchdog process after disaster handling.
- 灾难处理结束后（送达成功或预算耗尽）guardian 必须退出，不长期驻留。
