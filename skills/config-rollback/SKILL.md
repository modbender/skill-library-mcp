---
name: config-rollback
description: 自动回滚保护。修改配置前先备份+设5分钟系统定时任务，改坏自动还原。当用户说"自动回滚"或需要改配置时使用此 Skill。
---

# Config Rollback - 自动回滚保护

## 口令
用户说"自动回滚"时触发

## 执行流程

1. **备份当前配置**
```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
```

2. **设系统级定时任务（5分钟后）**
```bash
echo "cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json && systemctl restart openclaw-gateway" | at now + 5 minutes
```

3. **返回 job ID**

4. **用户确认正常后**
```bash
atrm <job-id>
```

## 适用场景
- 修改 channel 配置
- 修改代理路由
- 更新插件
- 修改模型配置
- 任何需要重启 gateway 的操作

## 核心原则
- 必须是系统级定时任务（at/crontab）
- 不能依赖 OpenClaw 本身
- 双重保护：git commit + 自动回滚
