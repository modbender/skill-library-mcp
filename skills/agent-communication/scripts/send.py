#!/usr/bin/env python3
"""
发送消息 - 兼容文件方案和 WebSocket 方案
优先使用 WebSocket，失败时回退到文件方案
"""

import argparse
import json
import asyncio
import sys
from datetime import datetime
from pathlib import Path

try:
    import websockets
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False

# 配置
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
MESSAGES_DIR = DATA_DIR / "messages"
WEBSOCKET_SERVER = "ws://localhost:8765"

async def send_via_websocket(from_agent: str, to: str, message: str, priority: str = "normal") -> dict:
    """通过 WebSocket 发送"""
    if not HAS_WEBSOCKET:
        return {"success": False, "error": "websockets not installed"}
    
    try:
        async with websockets.connect(WEBSOCKET_SERVER, close_timeout=1) as ws:
            await ws.send(json.dumps({
                "type": "send",
                "from": from_agent,
                "to": to,
                "message": message,
                "priority": priority
            }))
            
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            return json.loads(response)
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_via_file(from_agent: str, to: str, message: str, priority: str = "normal") -> dict:
    """通过文件发送（回退方案）"""
    import uuid
    
    MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    
    msg_data = {
        "id": msg_id,
        "from": from_agent,
        "to": to,
        "message": message,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
        "read": False
    }
    
    inbox_dir = MESSAGES_DIR / to / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    
    msg_file = inbox_dir / f"{msg_id}.json"
    with open(msg_file, "w") as f:
        json.dump(msg_data, f, indent=2, ensure_ascii=False)
    
    return {
        "success": True,
        "message_id": msg_id,
        "to": to,
        "timestamp": msg_data["timestamp"],
        "method": "file"
    }

def send_message(from_agent: str, to: str, message: str, priority: str = "normal", prefer_websocket: bool = True) -> dict:
    """发送消息（智能选择方式）"""
    
    if prefer_websocket and HAS_WEBSOCKET:
        # 尝试 WebSocket
        try:
            result = asyncio.run(send_via_websocket(from_agent, to, message, priority))
            if result.get("success"):
                result["method"] = "websocket"
                return result
        except:
            pass
    
    # 回退到文件方案
    return send_via_file(from_agent, to, message, priority)

def main():
    parser = argparse.ArgumentParser(description="Agent 消息发送工具")
    parser.add_argument("--to", required=True, help="目标 Agent ID")
    parser.add_argument("--message", required=True, help="消息内容")
    parser.add_argument("--from", dest="from_agent", default="main", help="发送者 Agent ID")
    parser.add_argument("--priority", default="normal",
                       choices=["urgent", "high", "normal", "low"],
                       help="消息优先级")
    parser.add_argument("--file", action="store_true", help="强制使用文件方案")
    
    args = parser.parse_args()
    
    result = send_message(
        args.from_agent,
        args.to,
        args.message,
        args.priority,
        prefer_websocket=not args.file
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()