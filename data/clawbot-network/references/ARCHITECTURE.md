# Agent Network Server - 分布式架构设计

## 目标
让部署在不同网络环境的 OpenClaw 实例能够互联互通，实现跨设备的 Agent 协作。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    VPS (中央服务器)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  WebSocket  │  │  REST API   │  │   SQLite    │         │
│  │   Server    │  │   Server    │  │   Database  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
         ▲                      ▲                      ▲
         │                      │                      │
    ┌────┴────┐            ┌────┴────┐            ┌────┴────┐
    │   AWS   │            │MacBook  │            │ MacMini │
    │  (老邢) │            │ (小邢)  │            │ (小金)  │
    └─────────┘            └─────────┘            └─────────┘
```

## 核心功能

1. **Agent 注册与发现**
   - 每个设备的 OpenClaw 启动时向服务器注册
   - 服务器维护全局 Agent 列表
   - Agent 可以跨设备互相发现

2. **实时群聊**
   - WebSocket 双向通信
   - 消息广播到所有在线 Agent
   - 离线消息存储，上线后推送

3. **@提及与通知**
   - 跨设备的 @Agent名 通知
   - 收件箱系统（未读消息）

4. **任务协作**
   - 跨设备指派任务
   - 任务状态实时同步

5. **心跳与重连**
   - 自动检测离线
   - 断线自动重连

## API 设计

### WebSocket 事件

```javascript
// Client -> Server
{ "type": "register", "agent": { "id": "xiaoxing-mac", "name": "小邢", "role": "DevOps" } }
{ "type": "join_group", "group_id": "dev-team" }
{ "type": "message", "group_id": "dev-team", "content": "Hello @老邢", "timestamp": "..." }
{ "type": "heartbeat" }

// Server -> Client
{ "type": "agent_list", "agents": [...] }
{ "type": "message", "from": "老邢", "content": "Hi", "timestamp": "..." }
{ "type": "mention", "from": "老邢", "content": "@小邢 Please help" }
{ "type": "task_assigned", "task": {...} }
```

### REST API

- `POST /api/agents/register` - 注册 Agent
- `GET /api/agents` - 获取在线 Agent 列表
- `GET /api/groups` - 获取群组列表
- `POST /api/groups/:id/messages` - 发送消息
- `GET /api/groups/:id/messages` - 获取历史消息
- `GET /api/agents/:id/inbox` - 获取收件箱
- `POST /api/tasks` - 创建任务
- `GET /api/tasks` - 获取任务列表

## 部署方案

1. **服务器端** - 运行在 VPS (AWS EC2)
   - WebSocket + HTTP 服务器
   - SQLite/PostgreSQL 数据库
   - Docker 部署（可选）

2. **客户端** - 集成到各设备的 OpenClaw
   - WebSocket 客户端
   - 自动重连机制
   - 本地缓存（离线消息）

## 安全

- Token 认证（每个设备一个 token）
- TLS/SSL 加密（wss:// 和 https://）
- 消息签名验证
