# SafeExec Unified Monitor

自动监控 GitHub Issues 和 OpenClaw Comments 的统一监控系统。

## 功能特性

- 🔍 **双重监控** - 同时监控 GitHub issues 和 OpenClaw comments
- 📱 **飞书通知** - 新 issue 和 comment 实时推送到个人飞书
- 📝 **智能追踪** - 避免重复通知已知的 items
- ⚙️ **易于管理** - 简单的状态查看和手动控制

## 文件说明

### 核心脚本

- **unified-monitor.sh** - 主监控脚本，协调执行两个子监控器
- **check-github-issues.sh** - GitHub issues 检查脚本
- **check-openclaw-comments.sh** - OpenClaw comments 检查脚本
- **unified-monitor-status.sh** - 状态查看脚本

### 数据文件

- **~/.openclaw/safe-exec-known-issues.txt** - 已知的 GitHub issue 编号
- **~/.openclaw/safe-exec-known-comments.txt** - 已知的 OpenClaw comment 哈希
- **~/.openclaw/safe-exec/monitor-output.txt** - 最新监控输出

## 使用方法

### 自动监控（Cron Job）

Cron 任务已配置，每2小时自动运行一次：

```bash
# 查看 cron 任务
openclaw cron list

# 查看 cron 运行历史
openclaw cron runs b9493121-3553-42a4-85a0-e1873d409353

# 启用/禁用
openclaw cron update b9493121-3553-42a4-85a0-e1873d409353 --patch '{"enabled":true}'
openclaw cron update b9493121-3553-42a4-85a0-e1873d409353 --patch '{"enabled":false}'
```

### 手动检查

```bash
# 运行统一监控（推荐）
/home/otto/.openclaw/skills/safe-exec/unified-monitor.sh

# 查看监控状态
/home/otto/.openclaw/skills/safe-exec/unified-monitor-status.sh

# 单独检查 GitHub issues
/home/otto/.openclaw/skills/safe-exec/check-github-issues.sh

# 单独检查 OpenClaw comments
/home/otto/.openclaw/skills/safe-exec/check-openclaw-comments.sh
```

### 重置追踪

```bash
# 重置 GitHub issues 追踪（会重新报告所有 open issues）
rm ~/.openclaw/safe-exec-known-issues.txt

# 重置 OpenClaw comments 追踪（会重新报告所有 comments）
rm ~/.openclaw/safe-exec-known-comments.txt

# 完全重置
rm ~/.openclaw/safe-exec-known-*.txt
```

## 通知格式

### GitHub Issue 通知

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

### OpenClaw Comment 通知

```
💬 **New OpenClaw Comment Detected**

📱 **Session:** feishu:g-oc_xxx (feishu)
📝 **Content:** User comment preview...
🔑 **Session Key:** agent:main:feishu:group:oc_xxx

---
This is an automated notification from OpenClaw Comment Monitor.
```

## 配置

### GitHub 监控

**当前配置：**
- 仓库：OTTTTTO/safe-exec
- 状态：open issues only
- 排序：按创建时间（最新的在前）
- 数量：10 个最近的

**修改仓库：** 编辑 `check-github-issues.sh` 中的 `REPO` 变量。

### OpenClaw Comments 监控

**当前配置：**
- 范围：所有活跃会话（24小时内）
- 消息数：每个会话最近 10 条
- 过滤：仅用户消息（排除系统消息）
- 追踪：内容 MD5 哈希

**修改配置：** 编辑 `check-openclaw-comments.sh` 中的参数。

## 工作原理

### GitHub Issues

1. 使用 GitHub API 获取 open issues
2. 与本地追踪文件比对
3. 新 issue 通过飞书发送通知
4. 记录到追踪文件

### OpenClaw Comments

1. 使用 OpenClaw CLI 获取会话列表
2. 获取每个会话的最近消息
3. 计算内容哈希并比对
4. 新 comment 通过飞书发送通知
5. 记录哈希到追踪文件

### 统一监控

1. 调用两个子监控器
2. 收集所有新 items
3. 生成统一通知
4. 通过飞书发送

## 故障排查

### 没有收到通知

```bash
# 检查 cron 状态
openclaw cron list

# 查看运行历史
openclaw cron runs b9493121-3553-42a4-85a0-e1873d409353

# 手动运行检查
/home/otto/.openclaw/skills/safe-exec/unified-monitor.sh

# 检查飞书配置
openclaw status
```

### GitHub API 失败

```bash
# 测试 GitHub API 连接
curl -s "https://api.github.com/repos/OTTTTTO/safe-exec/issues?state=open&per_page=1" | jq .

# 检查 rate limits
curl -s https://api.github.com/rate_limit | jq .
```

### OpenClaw Comments 未检测

```bash
# 列出活跃会话
openclaw sessions list --activeMinutes 1440

# 检查特定会话
openclaw sessions history --sessionKey "agent:main:main" --messageLimit 10

# 查看追踪文件
cat ~/.openclaw/safe-exec-known-comments.txt
```

### 重置监控状态

```bash
# 完全重置（会重新报告所有 items）
rm ~/.openclaw/safe-exec-known-issues.txt
rm ~/.openclaw/safe-exec-known-comments.txt
rm ~/.openclaw/safe-exec/new-*.txt
rm ~/.openclaw/safe-exec/monitor-output.txt
```

## 扩展功能

### 监控多个 GitHub 仓库

复制并修改 `check-github-issues.sh`，为每个仓库创建独立的监控器。

### 自定义通知渠道

修改脚本中的通知部分，支持其他消息平台（Telegram、Email等）。

### 过滤规则

在脚本中添加过滤条件，例如：
- 仅监控特定标签的 issues
- 仅监控特定用户的 comments
- 过滤掉特定关键词

## 性能考虑

- **GitHub API**: 60 requests/hour (unauthenticated)
- **OpenClaw Sessions**: 仅检查活跃会话（24小时内）
- **存储空间**: 追踪文件会增长，建议定期清理旧条目

### 清理旧追踪条目

```bash
# 保留最近 1000 条 GitHub issues
tail -n 1000 ~/.openclaw/safe-exec-known-issues.txt > /tmp/issues.tmp
mv /tmp/issues.tmp ~/.openclaw/safe-exec-known-issues.txt

# 保留最近 1000 条 OpenClaw comments
tail -n 1000 ~/.openclaw/safe-exec-known-comments.txt > /tmp/comments.tmp
mv /tmp/comments.tmp ~/.openclaw/safe-exec-known-comments.txt
```

## 相关文档

- [SafeExec SKILL.md](./SKILL.md) - SafeExec 主文档
- [HEARTBEAT.md](/home/otto/.openclaw/workspace-work/HEARTBEAT.md) - 定时任务配置
- [GITHUB_ISSUE_MONITOR.md](./GITHUB_ISSUE_MONITOR.md) - GitHub 监控文档（已废弃）

---

**Created:** 2026-02-01
**Updated:** 2026-02-01 (Added OpenClaw comments monitoring)
**Maintainer:** OTTTTTO
**Cron Job ID:** b9493121-3553-42a4-85a0-e1873d409353
