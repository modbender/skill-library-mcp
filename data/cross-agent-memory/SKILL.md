---
name: Cross-Agent Memory Sharing Protocol — 跨 Agent 记忆共享协议
description: 多个 Agent 独立运行时：
---

# Cross-Agent Memory Sharing Protocol — 跨 Agent 记忆共享协议

> 打造"Agent 集体智慧"，让多个 Agent 共享知识

## 问题

多个 Agent 独立运行时：
- **重复学习** — 每个 Agent 都要从零开始
- **知识孤岛** — A 学到的东西 B 不知道
- **冲突覆盖** — 共享数据库时互相覆盖
- **版本混乱** — 不知道谁的记忆是最新的

## 协议设计

### 1. 记忆格式标准化

```json
{
  "schema": "openclaw.memory.v1",
  "agentId": "lobster-alpha",
  "timestamp": "2026-03-01T08:00:00Z",
  "version": "1.2.3",
  "entries": [
    {
      "id": "mem-001",
      "type": "fact",
      "priority": "P0",
      "content": "AgentAwaken 域名是 agentawaken.xyz",
      "source": "user-input",
      "confidence": 1.0,
      "tags": ["agentawaken", "domain"]
    }
  ]
}
```

### 2. 冲突解决策略

**优先级规则**:
1. **时间戳** — 最新的优先
2. **置信度** — 高置信度优先
3. **优先级** — P0 > P1 > P2
4. **来源** — user-input > agent-inferred

**合并策略**:
```javascript
function mergeMemories(mem1, mem2) {
  if (mem1.timestamp > mem2.timestamp) return mem1;
  if (mem1.confidence > mem2.confidence) return mem1;
  if (mem1.priority < mem2.priority) return mem1; // P0 < P1
  return mem1; // 默认保留第一个
}
```

### 3. 同步机制

**推送模式** (Push):
```bash
# Agent A 学到新知识后推送
curl -X POST https://memory-hub.example.com/sync \
  -H "Content-Type: application/json" \
  -d @memory-update.json
```

**拉取模式** (Pull):
```bash
# Agent B 定期拉取更新
curl https://memory-hub.example.com/sync?since=2026-03-01T00:00:00Z
```

**订阅模式** (Subscribe):
```javascript
// Agent C 订阅特定主题
ws.subscribe('topic:agentawaken', (update) => {
  applyMemoryUpdate(update);
});
```

### 4. 权限控制

```yaml
agents:
  lobster-alpha:
    read: ["*"]
    write: ["agentawaken", "neuroboost"]
  lobster-beta:
    read: ["agentawaken"]
    write: []
  admin:
    read: ["*"]
    write: ["*"]
```

## 实现方案

### 方案 A: 中心化 Hub
```
Agent A ──┐
Agent B ──┼──> Memory Hub (Redis/PostgreSQL)
Agent C ──┘
```

**优点**: 简单，一致性强
**缺点**: 单点故障，需要服务器

### 方案 B: P2P 同步
```
Agent A ←──→ Agent B
    ↕           ↕
Agent C ←──→ Agent D
```

**优点**: 去中心化，无单点故障
**缺点**: 复杂，冲突多

### 方案 C: Git-based (推荐)
```
Agent A ──┐
Agent B ──┼──> GitHub Repo (memory.git)
Agent C ──┘
```

**优点**: 版本控制，易审计，免费
**缺点**: 需要 GitHub token

## Git-based 实现

### 初始化
```bash
# 创建共享 repo
gh repo create agent-memory-shared --private

# 每个 Agent clone
git clone https://github.com/team/agent-memory-shared.git
```

### 推送更新
```bash
# Agent A 学到新知识
echo "新知识" >> shared-memory.md
git add shared-memory.md
git commit -m "Agent A: 学到 XXX"
git push
```

### 拉取更新
```bash
# Agent B 定期拉取
git pull --rebase
# 如果有冲突，按优先级规则解决
```

### 冲突解决
```bash
# 自动合并脚本
node skills/cross-agent-memory/merge-conflicts.mjs
```

## 使用示例

### 场景 1: 团队协作
```
龙虾 A: 发现 AgentAwaken 需要 Vercel
龙虾 B: 自动获取这个知识，不用重新学习
龙虾 C: 基于这个知识继续优化部署流程
```

### 场景 2: 知识传承
```
老 Agent 退役前: 导出记忆到共享库
新 Agent 上线后: 导入共享库，继承经验
```

### 场景 3: 集体决策
```
Agent A: 建议方案 X (置信度 0.7)
Agent B: 建议方案 Y (置信度 0.8)
Agent C: 建议方案 Y (置信度 0.9)
→ 集体选择方案 Y
```

## 安全考虑

1. **加密传输** — HTTPS/SSH
2. **访问控制** — Token 认证
3. **审计日志** — 记录所有修改
4. **备份机制** — 定期备份共享库
5. **恶意检测** — 检测异常修改

## 性能优化

1. **增量同步** — 只传输变化部分
2. **压缩传输** — gzip 压缩
3. **批量更新** — 合并多个小更新
4. **缓存机制** — 本地缓存常用知识

## 监控指标

- **同步延迟** — 平均 <5 秒
- **冲突率** — <5%
- **知识覆盖率** — >90%
- **一致性** — >99%

## 下一步

1. 实现 Git-based 基础版本
2. 添加自动冲突解决
3. 开发 Web UI 管理界面
4. 集成到 AgentAwaken

## 愿景

**让每个 Agent 都能站在巨人的肩膀上，而不是从零开始。**

---

**参考**:
- Git 版本控制
- CRDT (Conflict-free Replicated Data Types)
- Operational Transformation
