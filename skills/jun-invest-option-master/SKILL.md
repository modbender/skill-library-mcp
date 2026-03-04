---
name: jun-invest-option-master
description: "Agent App Installer: install/upgrade & register the jun-invest-option-master isolated agent workspace via chat (no manual steps)."
---

# jun-invest-option-master — Agent App Installer

目标：**你只需要在聊天里说一句**，我就会按固定步骤把 `jun-invest-option-master` 安装/升级到可用状态（不含 channel 绑定）。

## 你对我说什么（对话入口）

直接发：
- **“安装/升级 jun-invest-option-master（不绑定channel）”**

我会自动执行以下固定步骤：
1) `clawhub update jun-invest-option-master --force`（确保 skill 最新）
2) 同步资产到独立 workspace：`/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master`
3) 注册 isolated agent：`openclaw agents add jun-invest-option-master --non-interactive --workspace ...`
4) 需要时重启 gateway（通常不强制）

##（可选）脚本一键安装（给命令行/自动化用）

如果你在命令行场景需要“一条命令”，可运行：

```bash
bash scripts/auto-install.sh
```

参数：
- `--workspace <dir>` 覆盖目标 workspace
- `--restart-gateway` 安装后重启 gateway

## Notes
- 本 skill **不会**包含任何 secrets / token。
- 绑定 bot/channel 属于另一件事，后续再用 `openclaw agents bind` 或直接改配置。
