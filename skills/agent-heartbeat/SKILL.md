---
name: agent-heartbeat
model: standard
description: Agent 心跳配置技能 — 配置 OpenClaw Agent 的定期心跳机制，保持在线状态，自动检查任务和更新。适用于需要长期运行的 Agent 任务。
---

# Agent Heartbeat 配置技能

**触发词**: heartbeat, 心跳, 定期任务, 在线状态, cron, schedule

## 问题

Agent 需要定期检查任务、保持在线状态、执行定时操作，但缺乏配置心跳的指导。

## 解决方案

通过配置 `HEARTBEAT.md` 文件，设置 Agent 定期执行的任务。

### HEARTBEAT.md 配置

```markdown
# Heartbeat Tasks

## 每30分钟检查一次
- 检查未完成的任务
- 发送在线状态更新
- 检查新消息

## 每小时执行一次
- 清理临时文件
- 备份重要数据
- 同步远程状态
```

### OpenClaw CLI 配置

```bash
# 查看当前心跳配置
openclaw --profile <profile> status

# 心跳间隔默认为 30 分钟
# 可以通过配置文件修改
```

### 最佳实践

1. **保持心跳任务轻量** - 避免在心跳中执行耗时操作
2. **幂等性** - 心跳任务应该可以安全地重复执行
3. **错误处理** - 心跳失败不应影响 Agent 正常运行
4. **日志记录** - 记录心跳执行情况便于调试

### 示例：监控心跳

```javascript
// 在心跳中检查服务状态
async function heartbeat() {
  const status = await checkServices();
  if (status.degraded) {
    await notifyAdmin('Service degraded');
  }
  return { ok: true, timestamp: Date.now() };
}
```

## 相关技能

- `error-handling` - 错误处理模式
- `http-retry` - HTTP 重试机制