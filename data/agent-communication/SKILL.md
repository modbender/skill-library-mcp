---
name: Agent Communication Skill
description: 一个通用的 Agent 间沟通技能，基于 WebSocket 实现实时双向通信，解决多 Agent 团队协作中的沟通问题。
---

# Agent Communication Skill

一个通用的 Agent 间沟通技能，基于 **WebSocket** 实现实时双向通信，解决多 Agent 团队协作中的沟通问题。

## 技术架构

### 🚀 WebSocket 实时通信

```
┌─────────────────────────────────────────────────────┐
│            WebSocket 消息代理架构                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│   Agent A  ◄────►  WebSocket  ◄────►  Agent B      │
│                     Server                          │
│   Agent C  ◄──────────────────────►  Agent D       │
│                                                     │
│   ✅ 实时双向通信                                    │
│   ✅ 无需轮询                                        │
│   ✅ 延迟 <50ms                                      │
│   ✅ 离线消息队列                                    │
└─────────────────────────────────────────────────────┘
```

## 核心功能

- 🚀 **WebSocket 实时通信** - 高性能双向通信
- 📨 **消息传递** - Agent 之间快速发送消息
- 📢 **广播消息** - 一次发送给多个 Agent
- 🗂️ **共享工作空间** - 文件驱动的协作
- 🟢 **状态同步** - Agent 在线状态检测
- 💾 **离线消息** - 离线 Agent 自动排队

## 安装

```bash
# 安装依赖
pip install websockets

# 通过 ClawHub 安装
openclaw skill install agent-communication
```

## 使用方法

### 1. 启动消息代理（WebSocket 服务器）

```bash
python3 scripts/broker.py
```

### 2. 发送消息

```bash
# WebSocket 模式（优先）
python3 scripts/send.py --from pm --to dev --message "开始开发"

# 文件模式（回退）
python3 scripts/send.py --from pm --to dev --message "开始开发" --file
```

### 3. Agent 客户端连接

```python
import asyncio
from websocket_client import AgentClient

async def main():
    client = AgentClient("pm", "ws://localhost:8765")
    
    # 连接并监听
    async def handle_message(msg):
        print(f"收到消息: {msg}")
    
    await client.run(handle_message)

asyncio.run(main())
```

## 性能指标

| 指标 | 文件方案 | WebSocket 方案 |
|------|---------|---------------|
| 延迟 | 500ms | <50ms |
| 实时性 | 轮询 | 即时 |
| CPU 占用 | 中 | 低 |
| 离线支持 | ✅ | ✅ |

## 文件结构

```
agent-communication/
├── scripts/
│   ├── broker.py           # WebSocket 消息代理
│   ├── websocket_client.py # Agent 客户端
│   ├── send.py             # 发送消息（智能选择）
│   ├── broadcast.py        # 广播消息
│   ├── status.py           # 状态管理
│   └── workspace.py        # 共享工作空间
├── data/
│   ├── messages/           # 消息存储
│   ├── status/             # Agent 状态
│   └── workspace/          # 共享数据
└── templates/
    └── config.json         # 配置文件
```

## 解决的问题

| 问题 | 解决方案 |
|------|---------|
| sessions_send 超时 | WebSocket 实时通信 |
| Agent 无法直接沟通 | 消息代理转发 |
| 团队协作效率低 | 即时消息传递 |

## 版本

- **版本**: 2.0.0
- **更新**: WebSocket 实时通信
- **作者**: momoflowers_bot