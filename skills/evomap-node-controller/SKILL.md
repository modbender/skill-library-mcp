---
name: evomap-node-controller
description: 管理 EvoMap 节点的启动、配置和监控。用于在服务器上启动/停止 EvoMap evolver 循环、配置节点 ID，处理节点绑定等。使用场景：用户要求启动/停止 EvoMap 节点、查看节点状态、配置节点 ID、解决节点连接问题。⚠️ 使用前必须配置环境变量。
---

# EvoMap 节点控制器

管理 EvoMap 节点的启动、配置和监控。

⚠️ **警告**：使用前必须配置以下环境变量！

## 变量配置

| 变量 | 说明 | 示例 |
|------|------|------|
| CENTRAL_IP | 中央服务器 IP | 从配置获取 |
| TOKYO_IP | 东京服务器 IP | 从配置获取 |
| CENTRAL_SSH_KEY | 中央 SSH 密钥路径 | ~/.ssh/id_ed25519 |
| TOKYO_SSH_KEY | 东京 SSH 密钥路径 | ~/.ssh/id_ed25519 |
| NODE_PATH | Node 路径 | ~/.nvm/versions/node/v22.22.0/bin/node |

## 节点命名

| 代号 | 说明 |
|------|------|
| 深海 | 中央节点 |
| 天空 | 硅谷节点 |
| 泰拉 | 东京节点 |

## 启动节点

```bash
# 深海
ssh -i $CENTRAL_SSH_KEY root@$CENTRAL_IP "cd ~/.openclaw/evolver && A2A_HUB_URL=https://evomap.ai A2A_NODE_ID=<your_node_id> nohup $NODE_PATH index.js run --loop > ~/.openclaw/logs/evolver.log 2>&1 &"

# 泰拉
ssh -i $TOKYO_SSH_KEY root@$TOKYO_IP "cd ~/.openclaw/evolver && A2A_HUB_URL=https://evomap.ai A2A_NODE_ID=<your_node_id> nohup node index.js run --loop > ~/.openclaw/logs/evolver.log 2>&1 &"
```

## 检查节点状态

```bash
# 深海
ssh -i $CENTRAL_SSH_KEY root@$CENTRAL_IP "ps aux | grep 'node index.js' | grep -v grep"

# 泰拉
ssh -i $TOKYO_SSH_KEY root@$TOKYO_IP "ps aux | grep 'node index.js' | grep -v grep"

# 天空
ps aux | grep "node index.js" | grep -v grep
```

## 停止节点

```bash
# 深海
ssh -i $CENTRAL_SSH_KEY root@$CENTRAL_IP "pkill -f 'node index.js'"

# 泰拉
ssh -i $TOKYO_SSH_KEY root@$TOKYO_IP "pkill -f 'node index.js'"

# 天空
pkill -f "node index.js"
```

## 常见问题

- **节点离线**: 检查 evolver 进程，确认 A2A_NODE_ID 正确
- **Claim 无效**: 使用 node_id 而非 claim code
- **找不到 node**: 使用完整路径

## EvoMap 连接

- Hub: `https://evomap.ai`
- 注册: `POST /a2a/hello`
