---
name: openclaw-session-guard
description: 管理 OpenClaw 长会话防爆机制（80%自动归档、自动轮换新会话、低 token 交接）及定时任务安装。用户提到 compacting context、会话过长、自动总结归档、session 轮换、LaunchAgent 定时任务时使用。
---

# OpenClaw Session Guard

用于治理 OpenClaw 会话上下文过长导致的反复 compaction。

## 适用场景

- 用户反馈 `compacting context` 频繁出现
- 想要“到阈值自动摘要+存档+续聊”
- 需要安装/检查/卸载会话轮换定时任务

## 默认策略

- 阈值：`80%`
- 冷却：`1800s`（30 分钟）
- 扫描周期：`300s`（5 分钟）
- 摘要条数：每个角色最近 `6` 条

## 快速操作

1. 安装/更新
```bash
bash ~/.openclaw/skills/openclaw-session-guard/scripts/install.sh
```

2. 查看状态
```bash
bash ~/.openclaw/skills/openclaw-session-guard/scripts/status.sh
```

3. 卸载
```bash
bash ~/.openclaw/skills/openclaw-session-guard/scripts/uninstall.sh
```

## 交付要求

- 给用户汇报：当前阈值、冷却、扫描周期
- 给用户汇报：最新归档文件与最新轮换 sessionId
- 若失败：给出可执行修复命令，不只描述原因

## 参考

- 详细机制和目录说明见 [reference.md](reference.md)
