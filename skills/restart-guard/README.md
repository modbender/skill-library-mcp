# restart-guard

## Overview / 概览

`restart-guard` provides deterministic OpenClaw gateway restart with context preservation and post-restart proactive report in the originating session.  
`restart-guard` 提供确定性的 OpenClaw 网关重启：保留现场、守护进程兜底，并在发起会话主动回报结果。

## Release / 版本

- Current: `v2.2.0`
- Upgrade path: compatible with `v1.0.1` / `v1.1.x` config fields (no forced migration).
- 当前版本：`v2.2.0`
- 升级路径：兼容 `v1.0.1` / `v1.1.x` 配置字段（无需强制迁移）。

Full replication spec / 完整复刻规范:
- [`ENHANCED_RESTART_IMPLEMENTATION_SPEC.md`](./ENHANCED_RESTART_IMPLEMENTATION_SPEC.md)

Core state machine / 核心状态机:

1. `restart.py` writes `restart_id` + context snapshot, then spawns detached `guardian.py`.
2. `restart.py` triggers restart and exits.
3. `guardian.py` enforces: `WAIT_DOWN -> START_GATEWAY -> WAIT_UP_HEALTHY -> ACK_ORIGIN_SESSION`.
4. Guardian sends `restart_guard.result.v1` to the origin session; net reads context and reports to user.

User experience target / 用户体验目标:
- User only says restart intent (e.g. "可以重启了" / "restart now").
- Agent runs restart-guard automatically and reports result after restart.
- 用户只需表达重启意图（如“可以重启了”/“restart now”）。
- agent 自动执行 restart-guard，并在重启后主动汇报结果。

## Quick Start / 快速开始

```bash
SKILL=skills/restart-guard/scripts
CFG=~/.openclaw/custom/config/restart-guard.yaml

# One-command auto flow (recommended)
python3 $SKILL/auto_restart.py \
  --config $CFG \
  --reason "config change" \
  --notify-mode origin

# selected mode example
python3 $SKILL/auto_restart.py \
  --config $CFG \
  --reason "config change" \
  --notify-mode selected \
  --channel telegram \
  --target 726647436

# 4) postcheck
python3 $SKILL/postcheck.py --config $CFG
```

## Behavior Notes / 行为说明

- `webui` is no longer treated as "disable notification". In `origin` mode, guardian ACK goes back to the initiating session.
- `webui` 不再等价“禁用通知”。在 `origin` 模式下，guardian 会回发到发起会话。
- `notify.py` supports generic OpenClaw channel passthrough (for feishu and other enabled channels).
- `notify.py` 支持通用渠道透传（例如飞书等已启用渠道）。
- Guardian always uses disaster route `origin -> agent:main:main -> external broadcast` with retry budget.
- guardian 固定使用灾难送达链路 `源会话 -> agent:main:main -> 外部渠道广播`，并带重试预算。

## Zero-Config UX / 零配置体验

- User only needs restart intent text; no channel arguments are required.
- 用户只需表达重启语义，不需要手填渠道参数。
- `restart.py` auto-discovers enabled channels from `openclaw.json` + skill config and writes `effective_notify_plan`.
- `restart.py` 会自动从 `openclaw.json` 与 skill 配置发现可用渠道，并写入 `effective_notify_plan`。
- Before triggering restart, restart-guard proactively announces disaster channels in origin session.
- 触发重启前，restart-guard 会先在源会话预告灾难通知渠道。

## Disaster Delivery Model / 灾难通知模型

1. Deliver result to origin session.
2. If failed, fallback to `agent:main:main`.
3. If still failed, broadcast to all discovered external channels.
4. Stop when delivered, or exit after retry budget exhausted.

1. 先向源会话回发结果。
2. 失败则回退到 `agent:main:main`。
3. 仍失败则广播到所有发现到的外部渠道。
4. 任一路由成功即停止；预算耗尽后守护进程退出。

## Compatibility Matrix / 兼容矩阵

| Area | Old behavior | New behavior |
|---|---|---|
| Success criteria | Health-only may false-positive | Strict `down_detected && start_attempted && up_healthy` |
| WebUI selection | Converted to no external message only | Origin-session proactive ACK, then net reports |
| Channel target | Mostly Telegram-centric | Generic channel passthrough + auto-discovered external broadcast |
| Config parsing | Minimal parser could misread lists | Robust YAML loading + safe fallback parser |
| Context fields | Basic reason/verify/resume | Adds `restart_id`, `origin_session_key`, `notify_mode`, `channel_selection`, `effective_notify_plan`, `state_timestamps`, `diagnostics_file`, `delivery_status` |

## Deprecated Behaviors / 已弃用行为

- Deprecated: treating `webui` as immediate no-op notification.
- Deprecated: assuming guardian success when health is already `ok` without observing down/up transition.
- Deprecated: relying on weak YAML list parsing in `write_context.py`.

## File Layout / 文件结构

```text
restart-guard/
├── SKILL.md
├── README.md
├── config.example.yaml
├── config/
│   └── restart-guard.yaml.example
├── scripts/
│   ├── write_context.py
│   ├── discover_channels.py
│   ├── auto_restart.py
│   ├── restart.py
│   ├── guardian.py
│   ├── postcheck.py
│   └── notify.py
├── templates/
│   └── restart-context.md
└── references/
    └── troubleshooting.md
```

## Requirements / 依赖

- `openclaw.json` must allow gateway restart operation in your environment.
- Python 3.10+
- `curl`
- `GATEWAY_AUTH_TOKEN` for HTTP tool path (restart chain still has signal/CLI fallback)

## Security Notes / 安全说明

- Verify/diagnostics commands run in strict non-shell mode.
- Shell metacharacters are rejected in command strings (for example: `|`, `;`, `&&`, `` ` ``).

## Why ClawHub May Mark `suspicious` / 为什么可能被标记为 `suspicious`

- This skill can restart gateway and send external notifications (Telegram/Feishu/Webhook-style channels).
- 该 skill 具备“重启网关 + 外部通知”能力，属于高影响操作，因此在平台安全策略中可能被标注为 `suspicious`。
- The `suspicious` label here is capability-based, not evidence of malicious behavior.
- 这里的 `suspicious` 是“能力级风险提示”，不等于存在恶意行为。

What this skill does for safety / 本 skill 的安全边界：
- No command injection path: critical runtime commands use strict non-shell execution; shell metacharacters are explicitly rejected.
- 无命令注入路径：关键运行命令采用严格非 shell 执行；显式拒绝 shell 元字符。
- No extra port binding: restart-guard does not create a new listener or service port; it only checks/uses configured gateway endpoint.
- 不新增端口监听：restart-guard 不创建新监听端口或新服务，仅检查/使用已配置网关端点。
- Full source is public for audit.
- 全量源码可审计：<https://github.com/Zjianru/restart-guard>

Operational advantage / 实际优势：
- External disaster notification ensures restart result is still delivered even if the origin session is interrupted.
- 外部灾难通知确保源会话中断时仍可收到重启结果。
- Strict state-machine verification reduces false-success restarts and repeated restart chaos.
- 严格状态机校验可减少“假成功”与重复重启带来的运行混乱。

## License / 许可

MIT
