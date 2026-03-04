#!/usr/bin/env python3
"""
WebSocket 消息代理服务器
高性能 Agent 通信核心
"""

import asyncio
import json
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Set

try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("安装依赖: pip install websockets")
    sys.exit(1)

# 配置
HOST = "0.0.0.0"
PORT = 8765
DATA_DIR = Path(__file__).parent.parent / "data"

class MessageBroker:
    """WebSocket 消息代理"""
    
    def __init__(self):
        self.agents: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_queue: Dict[str, list] = {}  # 离线消息队列
        self.connections: Set[websockets.WebSocketServerProtocol] = set()
        self.stats = {
            "total_messages": 0,
            "total_broadcasts": 0,
            "started_at": datetime.now().isoformat()
        }
    
    async def register_agent(self, agent_id: str, websocket: websockets.WebSocketServerProtocol):
        """注册 Agent"""
        self.agents[agent_id] = websocket
        self.connections.add(websocket)
        print(f"[REGISTER] Agent '{agent_id}' 已连接")
        
        # 发送离线消息
        if agent_id in self.message_queue:
            for msg in self.message_queue[agent_id]:
                await websocket.send(json.dumps(msg))
            del self.message_queue[agent_id]
            print(f"[OFFLINE] 发送 {len(self.message_queue.get(agent_id, []))} 条离线消息")
        
        # 广播在线状态
        await self.broadcast_status(agent_id, "online")
    
    async def unregister_agent(self, agent_id: str):
        """注销 Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
        print(f"[UNREGISTER] Agent '{agent_id}' 已断开")
        
        # 广播离线状态
        await self.broadcast_status(agent_id, "offline")
    
    async def broadcast_status(self, agent_id: str, status: str):
        """广播 Agent 状态"""
        status_msg = {
            "type": "status",
            "agent_id": agent_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新状态文件
        status_file = DATA_DIR / "status" / f"{agent_id}.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(status_file, "w") as f:
            json.dump(status_msg, f, indent=2)
        
        # 广播给所有 Agent
        for aid, ws in self.agents.items():
            if aid != agent_id:
                try:
                    await ws.send(json.dumps(status_msg))
                except:
                    pass
    
    async def send_message(self, from_agent: str, to_agent: str, message: str, priority: str = "normal"):
        """发送消息"""
        msg = {
            "type": "message",
            "id": f"msg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        self.stats["total_messages"] += 1
        
        # 保存消息文件（兼容文件方案）
        await self.save_message(msg)
        
        # 实时发送
        if to_agent in self.agents:
            try:
                await self.agents[to_agent].send(json.dumps(msg))
                print(f"[MESSAGE] {from_agent} -> {to_agent}: {message[:50]}...")
                return {"success": True, "message_id": msg["id"], "delivered": True}
            except Exception as e:
                print(f"[ERROR] 发送失败: {e}")
        
        # 离线消息队列
        if to_agent not in self.message_queue:
            self.message_queue[to_agent] = []
        self.message_queue[to_agent].append(msg)
        
        print(f"[QUEUED] {from_agent} -> {to_agent} (离线)")
        return {"success": True, "message_id": msg["id"], "delivered": False, "queued": True}
    
    async def broadcast_message(self, from_agent: str, message: str, agents: list, priority: str = "normal"):
        """广播消息"""
        results = []
        for agent in agents:
            result = await self.send_message(from_agent, agent, message, priority)
            results.append(result)
        
        self.stats["total_broadcasts"] += 1
        return {"success": True, "results": results}
    
    async def save_message(self, msg: dict):
        """保存消息到文件（兼容文件方案）"""
        try:
            inbox_dir = DATA_DIR / "messages" / msg["to"] / "inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            
            msg_file = inbox_dir / f"{msg['id']}.json"
            with open(msg_file, "w") as f:
                json.dump(msg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] 保存消息失败: {e}")
    
    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol):
        """处理连接"""
        agent_id = None
        
        try:
            async for data in websocket:
                try:
                    msg = json.loads(data)
                    
                    # 注册
                    if msg.get("type") == "register":
                        agent_id = msg.get("agent_id")
                        await self.register_agent(agent_id, websocket)
                        await websocket.send(json.dumps({
                            "type": "registered",
                            "agent_id": agent_id,
                            "status": "online"
                        }))
                    
                    # 发送消息
                    elif msg.get("type") == "send":
                        result = await self.send_message(
                            msg.get("from", "unknown"),
                            msg.get("to"),
                            msg.get("message"),
                            msg.get("priority", "normal")
                        )
                        await websocket.send(json.dumps(result))
                    
                    # 广播消息
                    elif msg.get("type") == "broadcast":
                        result = await self.broadcast_message(
                            msg.get("from", "unknown"),
                            msg.get("message"),
                            msg.get("agents", []),
                            msg.get("priority", "normal")
                        )
                        await websocket.send(json.dumps(result))
                    
                    # 心跳
                    elif msg.get("type") == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                    
                    # 状态查询
                    elif msg.get("type") == "status":
                        await websocket.send(json.dumps({
                            "type": "status_response",
                            "agents": list(self.agents.keys()),
                            "stats": self.stats
                        }))
                
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
                except Exception as e:
                    await websocket.send(json.dumps({"error": str(e)}))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if agent_id:
                await self.unregister_agent(agent_id)
            self.connections.discard(websocket)

# 全局代理实例
broker = MessageBroker()

async def main():
    """启动服务器"""
    print(f"🚀 WebSocket 消息代理启动")
    print(f"   地址: ws://{HOST}:{PORT}")
    print(f"   时间: {datetime.now().isoformat()}")
    print()
    
    async with serve(broker.handle_connection, HOST, PORT):
        await asyncio.Future()  # 永久运行

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)