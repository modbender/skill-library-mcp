# SafeExec GitHub Issue Monitor

自动监控 GitHub 仓库的新 issue 并通过飞书通知。

## 功能特性

- 🔍 **自动检测** - 每2小时检查一次 GitHub API
- 📱 **飞书通知** - 新 issue 实时推送到个人飞书
- 📝 **智能追踪** - 避免重复通知已知的 issue
- ⚙️ **易于管理** - 简单的状态查看和手动控制

## 文件说明

### 核心脚本

- **check-github-issues.sh** - 主检查脚本，获取并比对 GitHub issues
- **run-issue-check.sh** - Cron 执行包装器
- **issue-monitor-status.sh** - 状态查看脚本

### 数据文件

- **~/.openclaw/safe-exec-known-issues.txt** - 已知的 issue 编号列表
- **~/.openclaw/safe-exec/new-issues-output.txt** - 最新检查的输出

## 使用方法

### 自动监控（Cron Job）

Cron 任务已配置，每2小时自动运行一次：

```bash
# 查看 cron 任务
openclaw cron list

# 启用/禁用
openclaw cron update b9493121-3553-42a4-85a0-e1873d409353 --patch '{"enabled":true}'
openclaw cron update b9493121-3553-42a4-85a0-e1873d409353 --patch '{"enabled":false}'
```

### 手动检查

```bash
# 运行一次检查
/home/otto/.openclaw/skills/safe-exec/check-github-issues.sh

# 查看监控状态
/home/otto/.openclaw/skills/safe-exec/issue-monitor-status.sh
```

### 重置追踪

```bash
# 删除已知 issues 文件（会重新报告所有 open issues）
rm ~/.openclaw/safe-exec-known-issues.txt
```

## 通知格式

当检测到新 issue 时，你会收到如下格式的飞书消息：

```
🔔 **New GitHub Issue Detected**

📦 **Repository:** OTTTTTO/safe-exec
🔢 **Issue:** #123
📝 **Title:** Issue title here
🕐 **Created:** 2026-02-01T10:00:00Z
🔗 **URL:** https://github.com/OTTTTTO/safe-exec/issues/123

---
This is an automated notification from SafeExec GitHub Issue Monitor.
```

## 配置

### 监控的仓库

当前配置：`OTTTTTO/safe-exec`

修改仓库：编辑 `check-github-issues.sh` 中的 `REPO` 变量。

### 检查间隔

当前：每2小时（7,200,000 毫秒）

修改间隔：
```bash
# 更新 cron 任务（间隔单位：毫秒）
openclaw cron update b9493121-3553-42a4-85a0-e1873d409353 --patch '{
  "schedule": {
    "kind": "every",
    "everyMs": 3600000
  }
}'
```

### 通知目标

当前：飞书个人聊天（ou_7fc27bedb0c6fec1c2d344352f524400）

## 工作原理

1. **Cron 触发** - 定时任务触发检查
2. **GitHub API** - 获取最新的 open issues
3. **比对已知** - 与本地追踪文件比对
4. **飞书通知** - 新 issue 通过 OpenClaw message 系统发送
5. **记录追踪** - 新 issue 编号写入追踪文件

## 故障排查

### 没有收到通知

```bash
# 检查 cron 状态
openclaw cron list

# 手动运行检查
/home/otto/.openclaw/skills/safe-exec/check-github-issues.sh

# 检查飞书配置
openclaw status
```

### GitHub API 失败

```bash
# 测试 GitHub API 连接
curl -s "https://api.github.com/repos/OTTTTTO/safe-exec/issues?state=open&per_page=1" | jq .

# 检查网络连接
ping api.github.com
```

### 重置监控状态

```bash
# 完全重置（会重新报告所有 open issues）
rm ~/.openclaw/safe-exec-known-issues.txt
rm ~/.openclaw/safe-exec/new-issues-output.txt
```

## 扩展功能

### 监控多个仓库

复制并修改 `check-github-issues.sh`，为每个仓库创建独立的 cron 任务。

### 自定义通知渠道

修改脚本中的通知部分，支持其他消息平台（Telegram、Email等）。

### 过滤规则

在脚本中添加 issue 标签、创建者等过滤条件。

## 相关文档

- [SafeExec SKILL.md](./SKILL.md) - SafeExec 主文档
- [HEARTBEAT.md](/home/otto/.openclaw/workspace-work/HEARTBEAT.md) - 定时任务配置
- [OpenClaw Cron Docs](https://docs.openclaw.ai/tools/cron) - Cron 任务管理

---

**Created:** 2026-02-01
**Maintainer:** OTTTTTO
**Cron Job ID:** b9493121-3553-42a4-85a0-e1873d409353
