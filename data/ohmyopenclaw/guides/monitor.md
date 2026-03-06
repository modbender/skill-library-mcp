# Proactive Monitoring Guide

## 适用场景

- 希望 AI 主动发现和处理任务
- 需要持续监控项目状态
- 想要自动化错误恢复
- 实现无人值守的工作流

## 配置变更

本指南将修改以下文件：

1. `openclaw.json` - 配置 cron、heartbeat 和监控规则
2. `workspace/AGENTS.md` - 添加主动监控流程
3. `workspace/.monitoring/` - 创建监控配置目录

## 监控架构

### Ralph Loop V2

```
┌─────────────────────────────────────────┐
│         Ralph Loop V2 Pipeline          │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │   1. Heartbeat (Every 5 min)      │  │
│  │   ├─ Check active tasks           │  │
│  │   ├─ Update task status           │  │
│  │   └─ Detect timeout               │  │
│  └───────────────────────────────────┘  │
│                  ↓                      │
│  ┌───────────────────────────────────┐  │
│  │   2. Proactive Scan               │  │
│  │   ├─ Scan for TODOs in code       │  │
│  │   ├─ Check open issues            │  │
│  │   ├─ Monitor error logs           │  │
│  │   └─ Find stale branches          │  │
│  └───────────────────────────────────┘  │
│                  ↓                      │
│  ┌───────────────────────────────────┐  │
│  │   3. Task Discovery               │  │
│  │   ├─ Prioritize tasks             │  │
│  │   ├─ Create task files            │  │
│  │   └─ Spawn agents                 │  │
│  └───────────────────────────────────┘  │
│                  ↓                      │
│  ┌───────────────────────────────────┐  │
│  │   4. Error Recovery               │  │
│  │   ├─ Analyze failures             │  │
│  │   ├─ Improve prompts              │  │
│  │   └─ Retry with fixes             │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Cron Jobs

定期执行的监控任务：

```json
{
  "cron": {
    "jobs": [
      {
        "name": "check-tasks",
        "schedule": "*/5 * * * *",
        "action": "heartbeat"
      },
      {
        "name": "scan-errors",
        "schedule": "*/10 * * * *",
        "action": "scan-errors"
      },
      {
        "name": "daily-report",
        "schedule": "0 9 * * *",
        "action": "generate-report"
      }
    ]
  }
}
```

## 安装命令

### 1. 更新 openclaw.json

```json
{
  "heartbeat": {
    "enabled": true,
    "interval": 300000,
    "actions": [
      "check-tasks",
      "scan-errors",
      "discover-work"
    ]
  },
  "cron": {
    "enabled": true,
    "jobs": [
      {
        "name": "check-active-tasks",
        "schedule": "*/5 * * * *",
        "action": "check-tasks",
        "params": {
          "timeout": 600000,
          "autoRecover": true
        }
      },
      {
        "name": "scan-error-logs",
        "schedule": "*/10 * * * *",
        "action": "scan-errors",
        "params": {
          "logPath": "/var/log/myapp",
          "pattern": "ERROR|Exception"
        }
      },
      {
        "name": "discover-todos",
        "schedule": "0 */2 * * *",
        "action": "scan-code",
        "params": {
          "pattern": "TODO|FIXME|XXX",
          "path": "./src"
        }
      },
      {
        "name": "daily-summary",
        "schedule": "0 18 * * *",
        "action": "report",
        "params": {
          "channels": ["discord", "email"]
        }
      }
    ]
  },
  "monitoring": {
    "enabled": true,
    "autoSpawn": true,
    "maxConcurrentScans": 3,
    "recovery": {
      "maxRetries": 3,
      "backoff": "exponential",
      "initialDelay": 60000
    }
  }
}
```

### 2. 创建监控目录结构

```bash
mkdir -p ~/.openclaw/workspace/.monitoring
mkdir -p ~/.openclaw/workspace/.monitoring/rules
mkdir -p ~/.openclaw/workspace/.monitoring/alerts
mkdir -p ~/.openclaw/logs
```

### 3. 创建监控规则

创建 `~/.openclaw/workspace/.monitoring/rules/error-detection.md`:

```markdown
# Error Detection Rules

## Patterns to Watch

### Critical Errors
- `OutOfMemoryError`
- `StackOverflowError`
- `ConnectionRefused`

### Warnings
- `Deprecated API usage`
- `Slow query detected`
- `Cache miss rate high`

## Actions

1. Log to alerts/
2. Spawn analysis agent
3. Notify via configured channels
```

创建 `~/.openclaw/workspace/.monitoring/rules/task-discovery.md`:

```markdown
# Task Discovery Rules

## Code Scans

### TODOs
- Priority: medium
- Pattern: `TODO:`
- Action: Create task, suggest implementation

### FIXMEs
- Priority: high
- Pattern: `FIXME:`
- Action: Create task, prioritize fix

## Issue Tracking

### Open Issues
- Scan GitHub issues
- Priority by labels
- Auto-assign based on expertise

### Stale PRs
- Detect PRs > 7 days old
- Create reminder task
- Suggest actions
```

### 4. 更新 AGENTS.md

添加监控流程：

```markdown
## Proactive Monitoring

### Heartbeat Actions

Every 5 minutes:
1. **Check Active Tasks**
   - Verify task progress
   - Detect stuck tasks
   - Update task files

2. **Scan for Errors**
   - Check application logs
   - Parse error patterns
   - Create fix tasks

3. **Discover Work**
   - Scan code for TODOs
   - Check GitHub issues
   - Find optimization opportunities

### Auto-Recovery

When task fails:
1. Analyze error context
2. Identify root cause
3. Improve prompt or context
4. Retry with enhanced parameters
5. Escalate if max retries exceeded

### Alert Channels

- Discord: Real-time notifications
- Email: Daily summary
- Log: Detailed records

### Manual Triggers

Force immediate scan:
```
Run heartbeat now
```

Check specific area:
```
Scan for errors in authentication module
```
```

## 验证步骤

### 1. 验证配置

```bash
cat ~/.openclaw/openclaw.json | grep -A 20 "heartbeat\|cron\|monitoring"
```

### 2. 手动触发 Heartbeat

```
Run heartbeat now
```

Expected:
- AI checks active tasks
- AI scans for new work
- AI reports findings

### 3. 测试错误检测

创建一个带 TODO 的文件：

```javascript
// TODO: Implement error handling
function riskyOperation() {
  // ...
}
```

然后：
```
Scan code for TODOs
```

Expected:
- AI finds the TODO
- AI creates task
- AI suggests implementation

### 4. 测试自动恢复

模拟失败任务：

```json
// .tasks/active/task-test-fail.json
{
  "id": "task-test-fail",
  "status": "in_progress",
  "created": "2026-02-27T08:00:00Z",
  "error": "Connection timeout",
  "retryCount": 0
}
```

等待 heartbeat 或手动触发，AI 应该：
1. Detect the failure
2. Analyze the error
3. Attempt recovery

## 使用示例

### 查看监控状态

```
Show me the monitoring status
```

### 手动扫描

```
Scan the codebase for TODOs and create tasks
```

### 检查错误日志

```
Check error logs for the past hour
```

### 生成报告

```
Generate a daily summary report
```

### 暂停/恢复监控

```
Pause proactive monitoring for 1 hour
```

```
Resume proactive monitoring
```

## 监控场景

### 场景 1: 自动修复 Bug

1. Heartbeat 扫描错误日志
2. 发现 `NullPointerException` in UserAuth.java
3. 创建修复任务
4. Spawn Codex worker
5. Worker fixes the bug
6. Verify and close task

### 场景 2: 处理 TODO

1. 定期扫描代码
2. 发现 `// TODO: Add input validation`
3. 创建实现任务
4. Spawn worker
5. Implement and test
6. Remove TODO comment

### 场景 3: 性能优化

1. 监控到慢查询日志
2. 分析查询模式
3. 创建优化任务
4. Add indexes
5. Verify improvement

## 进阶配置

### 自定义监控规则

创建 `~/.openclaw/workspace/.monitoring/rules/custom.md`:

```markdown
# Custom Monitoring Rules

## Business Logic Monitoring

### High-Value Errors
- Payment failures
- Data loss risks
- Security vulnerabilities

## Metrics to Track

- Response time > 1s
- Error rate > 1%
- Memory usage > 80%
```

### Webhook 集成

```json
{
  "monitoring": {
    "webhooks": {
      "onError": "https://hooks.slack.com/services/YOUR/WEBHOOK",
      "onTaskComplete": "https://api.example.com/callback"
    }
  }
}
```

### 条件触发

```json
{
  "monitoring": {
    "conditions": [
      {
        "metric": "error_rate",
        "operator": ">",
        "value": 0.05,
        "action": "spawn-debug-agent"
      }
    ]
  }
}
```

## 故障排除

### Heartbeat 未执行

1. Check cron configuration
2. Verify OpenClaw process is running
3. Check logs for errors

### 误报过多

1. Refine detection patterns
2. Adjust thresholds
3. Filter known issues

### 自动恢复失败

1. Check maxRetries setting
2. Review error analysis logic
3. Escalate to manual intervention

## 相关指南

- [agent-swarm.md](agent-swarm.md) - 监控需要 Worker 支持
- [memory-optimized.md](memory-optimized.md) - 记住监控历史
- [cost-optimization.md](cost-optimization.md) - 监控成本

## 监控最佳实践

1. **渐进式启用**
   - 先启用基础监控
   - 观察效果
   - 逐步增加规则

2. **平衡频率**
   - 不要过于频繁扫描
   - 根据项目规模调整
   - 避免资源浪费

3. **明确优先级**
   - Critical > High > Medium > Low
   - 自动处理低风险任务
   - 人工确认高风险任务

4. **定期审查**
   - 每周审查监控规则
   - 移除不再需要的规则
   - 优化检测模式
