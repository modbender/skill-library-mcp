---
name: openclaw-ops-guardrails
description: OpenClaw 运维防呆与排障标准化技能。用于跨设备（Gateway + Mac nodes）巡检、远程执行稳定性治理、CLI-only 兼容、配对/审批异常排查、以及对外发布前脱敏检查。用户提到“又报错了/审批超时/pairing required/system.run failed/如何标准化运维规则”时使用。
---

# OpenClaw Ops Guardrails

先阅读：
- `references/failure-playbook.md`（按错误类型排障）
- `references/publish-sanitization-checklist.md`（对外发布前脱敏）

1. 先执行全量只读体检：
   - `openclaw status --deep`
   - `openclaw security audit --deep`
   - `openclaw gateway status --json`
   - `openclaw health --json`
   - `openclaw nodes status --connected`

2. 检查 node 执行能力：
   - 确认 `system.run` 在 node commands 中存在
   - `nodes.run` 失败时按顺序归因：
     - approval timeout
     - pairing required
     - system.run unsupported
     - gateway timeout

3. 强制执行稳定性策略：
   - 使用 nodeId，不用 displayName
   - 同一 node 串行执行，不并发
   - 失败重试 1 次后再告警

4. CLI-only Mac 标准模板：
   - remote url 使用占位符 `<api-endpoint>`
   - sshTarget 使用占位符 `<ssh-target>`
   - 凭据使用占位符 `<gateway-token>`（与 gateway token 对齐）

5. 变更后验收：
   - 目标设备执行一条最小命令（echo/date/whoami）
   - 再跑一次 `status --deep`

6. 输出格式：
   - 总结：可用/不可用
   - 成功项
   - 失败项与根因
   - 遗留风险
   - 下一步建议（按优先级）

7. 对外分享前脱敏（必须）：
   - 不包含 token/key/password/IP/用户名/绝对路径
   - 输出脱敏版文档和发布说明
