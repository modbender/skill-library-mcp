#!/usr/bin/env python3
"""
Agent状态查询工具
用法: python3 status.py --agent <agent_id>
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
STATUS_DIR = DATA_DIR / "status"

def get_agent_status(agent_id: str) -> dict:
    """
    获取Agent状态
    
    Args:
        agent_id: Agent ID
    
    Returns:
        Agent状态信息
    """
    status_file = STATUS_DIR / f"{agent_id}.json"
    
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    
    return {
        "agent_id": agent_id,
        "status": "unknown",
        "last_seen": None,
        "message": "Agent状态未知"
    }

def list_all_agents() -> dict:
    """列出所有Agent状态"""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    
    agents = {}
    for status_file in STATUS_DIR.glob("*.json"):
        with open(status_file) as f:
            data = json.load(f)
            agents[data["agent_id"]] = data
    
    return {
        "count": len(agents),
        "agents": agents
    }

def update_agent_status(agent_id: str, status: str = "online") -> dict:
    """
    更新Agent状态
    
    Args:
        agent_id: Agent ID
        status: 状态 (online, offline, busy)
    
    Returns:
        更新后的状态
    """
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    
    status_data = {
        "agent_id": agent_id,
        "status": status,
        "last_seen": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    status_file = STATUS_DIR / f"{agent_id}.json"
    with open(status_file, "w") as f:
        json.dump(status_data, f, indent=2)
    
    return status_data

def main():
    parser = argparse.ArgumentParser(description="Agent状态查询工具")
    parser.add_argument("--agent", help="Agent ID")
    parser.add_argument("--list", action="store_true", help="列出所有Agent状态")
    parser.add_argument("--update", help="更新状态 (online, offline, busy)")
    
    args = parser.parse_args()
    
    if args.list:
        result = list_all_agents()
    elif args.agent and args.update:
        result = update_agent_status(args.agent, args.update)
    elif args.agent:
        result = get_agent_status(args.agent)
    else:
        result = list_all_agents()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()