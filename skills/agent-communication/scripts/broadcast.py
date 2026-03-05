#!/usr/bin/env python3
"""
Agent广播消息工具
用法: python3 broadcast.py --message <message> --agents <agent1,agent2,...>
"""

import argparse
import json
from pathlib import Path
from send import send_message

def broadcast_message(message: str, agents: list, priority: str = "normal", from_agent: str = "main") -> dict:
    """
    广播消息给多个Agent
    
    Args:
        message: 消息内容
        agents: 目标Agent列表
        priority: 优先级
        from_agent: 发送者Agent ID
    
    Returns:
        广播结果
    """
    results = []
    success_count = 0
    
    for agent in agents:
        result = send_message(agent, message, priority, from_agent)
        results.append(result)
        if result.get("success"):
            success_count += 1
    
    return {
        "success": True,
        "broadcast_count": len(agents),
        "success_count": success_count,
        "results": results
    }

def main():
    parser = argparse.ArgumentParser(description="Agent广播消息工具")
    parser.add_argument("--message", required=True, help="消息内容")
    parser.add_argument("--agents", required=True, help="目标Agent列表，逗号分隔")
    parser.add_argument("--from", dest="from_agent", default="main", help="发送者Agent ID")
    parser.add_argument("--priority", default="normal",
                       choices=["urgent", "high", "normal", "low"],
                       help="消息优先级")
    
    args = parser.parse_args()
    
    agents = [a.strip() for a in args.agents.split(",")]
    result = broadcast_message(args.message, agents, args.priority, args.from_agent)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()