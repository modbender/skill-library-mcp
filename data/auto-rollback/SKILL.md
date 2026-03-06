---
name: auto-rollback
description: Backup + timed rollback safety net for openclaw.json changes (macOS launchd)
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "os": ["darwin"],
        "requires": { "bins": ["bash", "launchctl", "jq"] }
      }
  }
---

# Auto-Rollback Skill 🛡️

This skill makes OpenClaw config changes safe.

Before you edit `~/.openclaw/openclaw.json`, it automatically creates a backup and schedules a rollback job (10 minutes later). If the new config breaks the Gateway and it won’t start, the rollback restores the last known-good config and restarts the Gateway for you — so you don’t need to remote-login to the host to fix a broken config.

Once the Gateway restarts successfully, the pending rollback is automatically cancelled (via the bundled `boot-md` hook running your `BOOT.md`). This prevents an unnecessary rollback after a successful change.

---

这个 skill 的核心价值是让你可以放心改 OpenClaw 配置。

在你修改 `~/.openclaw/openclaw.json` 之前，它会先自动备份，并设置一个 10 分钟后的回滚任务。如果你改坏了配置导致 Gateway 起不来，回滚任务会自动恢复到上一个可用配置并重启 Gateway —— 你不需要再远程登录主机手动修复。

当 Gateway 成功重启起来后，系统会自动取消掉这次预设的回滚（通过内置的 `boot-md` hook 执行 `BOOT.md` 完成），避免“明明已经成功了还被回滚”。

## When to Use / 适用场景

- You (or an agent) are about to change `~/.openclaw/openclaw.json` and restart the Gateway.
- You want a safety net so a bad change won’t take the system down.

---

- 当你（或 agent）要修改 `~/.openclaw/openclaw.json` 并重启 Gateway。
- 你希望即使配置写错，系统也能自动自愈，不用登录主机救火。

## Workflow / 工作流程

1) `start` → backup config + schedule rollback in 10 minutes
2) edit config
3) restart Gateway
4) If restart succeeds → rollback auto-cancels on next successful startup (BOOT.md)
5) If restart fails → wait; rollback restores backup and restarts Gateway automatically

---

1) `start` → 备份配置 + 设置 10 分钟后回滚
2) 修改配置
3) 重启 Gateway
4) 如果启动成功 → 下次成功启动时自动取消回滚（BOOT.md）
5) 如果启动失败 → 等待回滚自动恢复配置并重启 Gateway

## Commands / 命令

### start (before editing) / 修改前执行

```bash
skills/auto-rollback/auto-rollback.sh start --reason "your change description"
```

### cancel (optional fallback) / 手动取消（兜底）

```bash
skills/auto-rollback/auto-rollback.sh cancel
```

Note: With the BOOT.md integration installed, a successful Gateway startup will cancel rollback automatically.

---

说明：如果你启用了/安装了 BOOT.md 集成，Gateway 成功启动后会自动取消回滚；手动 cancel 只是兜底。

### status / 查看状态

```bash
skills/auto-rollback/auto-rollback.sh status
```

## BOOT.md Auto-Cancel / 自动取消回滚（关键）

This skill includes a `BOOT.md` snippet at `skills/auto-rollback/BOOT.md`.

To enable auto-cancel on successful startup:
- Merge (append) that snippet into your workspace `BOOT.md`.
- The bundled `boot-md` hook runs `BOOT.md` on every successful Gateway startup.

---

本 skill 自带一个 `BOOT.md` 片段：`skills/auto-rollback/BOOT.md`。

要启用“启动成功自动取消回滚”：
- 把这段内容合并（追加）到你的 workspace 根目录 `BOOT.md` 里。
- OpenClaw 内置的 `boot-md` hook 会在每次 Gateway 成功启动时执行 `BOOT.md`。

## Files & Logs / 文件与日志

- Script / 脚本: `skills/auto-rollback/auto-rollback.sh`
- Backups / 备份: `~/.openclaw/openclaw.json.YYYYMMDD-HHMMSS`
- State / 状态: `~/.openclaw/state/rollback-pending.json`
- Rollback log / 回滚日志: `~/.openclaw/logs/rollback.log`
- launchd plist / 回滚任务: `~/.openclaw/ai.openclaw.rollback.plist`

## Agent-only Enforcement / 只对 Agent 生效的约束

Installing this skill does not technically prevent a human from editing the file.
To ensure agents always use the safety net, write an SOP rule (e.g. in `AGENTS.md`) that any `openclaw.json` change must run `start` first.

---

安装 skill 不会从技术上阻止人类去手改文件。
想让 agent “强制执行”，需要把 SOP 写进 agent 的规范文件（例如 `AGENTS.md`）：只要改 `openclaw.json`，就必须先 `start`。
