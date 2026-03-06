---
name: agent-evolution
description: Agent 行为固化与进化系统。追踪规则执行、检测行为模式、维护身份连续性。用于：让 agent 的行为规则从"写下来"变成"做到了"。当 agent 需要自我改进、行为追踪、角色一致性、重复检测时激活。与 Memelord/memory-tools 互补：它们管记忆，本 skill 管行为。
---

# agent-evolution

Agent 行为固化与进化系统。追踪规则执行、检测行为模式、维护身份连续性。用于：让 agent 的行为规则从"写下来"变成"做到了"。当 agent 需要自我改进、行为追踪、角色一致性、重复检测时激活。与 Memelord/memory-tools 互补：它们管记忆，本 skill 管行为。

## 使用

所有命令通过 `node scripts/evolution.js <command> [args]` 执行，输出均为 JSON。

存储路径：`~/.openclaw/workspace/.agent-evolution/state.json`

## 模块

### 行为追踪器
追踪规则执行与违反，计算权重。

```bash
# 初始化（首次使用）
node scripts/evolution.js init

# 添加规则
node scripts/evolution.js add-rule <rule_id> <description> <source>

# 执行规则前调用，记录 +1
node scripts/evolution.js check <rule_id>

# 记录违反
node scripts/evolution.js violation <rule_id> <context>

# 查看统计
node scripts/evolution.js stats
```

### 身份状态层
跨会话持久化的结构化身份。

```bash
# 查看身份
node scripts/evolution.js identity

# 更新字段
node scripts/evolution.js identity-update <field> <value>

# 记录进化事件
node scripts/evolution.js evolve <change> <trigger>
```

### 模式检测器
检测重复行为和角色偏离。

```bash
# 记录操作
node scripts/evolution.js log <action_type> <detail>

# 检查告警
node scripts/evolution.js detect

# 重置计数器
node scripts/evolution.js reset <pattern_id>
```

### 综合报告

```bash
node scripts/evolution.js report
```

## 初始化规则

从 AGENTS.md / SOUL.md 自动提取规则：

```bash
bash scripts/init-rules.sh --agents /path/to/AGENTS.md --soul /path/to/SOUL.md
```

## 心跳检查

供 HEARTBEAT.md 调用：

```bash
bash scripts/heartbeat-check.sh
```
