# jun-invest-option-master-agent

OpenClaw Agent App（isolated workspace）安装器 + 自动备份/版本管理闭环（ClawHub）。

## 核心路径

- 运行真源（绑定 channel 的主战场）：
  - `~/.openclaw/workspace-jun-invest-option-master-agent`
- 发布工件（本 skill 的 `agent/`，用于 `clawhub publish`）：
  - `~/.openclaw/workspace/skills/jun-invest-option-master-agent/agent`

## 一键安装/升级

```bash
bash scripts/auto-install.sh
```

## 自动化闭环

- Growth 在运行真源里落地改动后会自动 `git commit`
- commit 会触发 `scripts/sync-runtime-to-artifact.sh` 同步到发布工件
- macOS launchd 定时任务会自动执行 `scripts/publish.sh` 发布到 ClawHub（有新 commit 才发）

## 外部 skills 依赖（不锁版本）

见 `skills.lock.json`（只列 slug，安装时 `clawhub update --force` best-effort）。
