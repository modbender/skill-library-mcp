#!/usr/bin/env python3
"""
FIS 3.2.0 SubAgent 自动化工具
简化版 - 不包含复杂生命周期管理
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SHARED_HUB = Path.home() / ".openclaw" / "fis-hub"
BADGE_GENERATOR = WORKSPACE / "skills" / "fis-architecture" / "lib" / "badge_generator_v7.py"
TICKETS_DIR = SHARED_HUB / "tickets"

def create_ticket(agent_id, task_name, role="worker", parent="cybermao"):
    """创建任务工牌（Ticket 文件）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_id = f"TASK_{parent.upper()}_{timestamp}_{agent_id}_{task_name[:20]}"
    
    ticket_data = {
        "ticket_id": ticket_id,
        "agent_id": agent_id,
        "parent": parent,
        "role": role,
        "task": task_name,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # 保存到 active
    ticket_path = TICKETS_DIR / "active" / f"{ticket_id}.json"
    ticket_path.write_text(json.dumps(ticket_data, indent=2, ensure_ascii=False))
    
    return ticket_id, ticket_path

def generate_badge(ticket_id, agent_name, role="worker", parent="cybermao", task_desc="Test Task"):
    """生成工牌图片"""
    if not BADGE_GENERATOR.exists():
        print(f"❌ Badge generator not found: {BADGE_GENERATOR}")
        return None
    
    # 创建临时 Python 脚本调用 badge_generator_v7
    badge_script = f"""
import sys
sys.path.insert(0, '{BADGE_GENERATOR.parent}')
from badge_generator_v7 import generate_badge_with_task

output = generate_badge_with_task(
    agent_name='{agent_name}',
    role='{role}',
    task_desc='{task_desc}',
    task_requirements=['Execute task with precision', 'Report progress within deadline', 'Follow FIS 3.1 protocol'],
    output_dir=None
)
print(f"✅ Badge: {{output}}")
"""
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", badge_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ {result.stderr}")
        return True
    except Exception as e:
        print(f"❌ Badge generation failed: {e}")
        return None

def complete_ticket(ticket_id):
    """完成任务并归档"""
    active_path = TICKETS_DIR / "active" / f"{ticket_id}.json"
    completed_path = TICKETS_DIR / "completed" / f"{ticket_id}.json"
    
    if not active_path.exists():
        print(f"⚠️ Ticket not found in active: {ticket_id}")
        return False
    
    # 读取并更新状态
    ticket = json.loads(active_path.read_text())
    ticket["status"] = "completed"
    ticket["completed_at"] = datetime.now().isoformat()
    
    # 移动到 completed
    completed_path.write_text(json.dumps(ticket, indent=2, ensure_ascii=False))
    active_path.unlink()
    
    print(f"✅ Ticket archived: {ticket_id}")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FIS 3.2.0 SubAgent Tool")
    parser.add_argument("action", choices=["create", "badge", "complete", "full"])
    parser.add_argument("--agent", default="test-agent")
    parser.add_argument("--task", default="Test Task")
    parser.add_argument("--role", default="worker")
    parser.add_argument("--parent", default="cybermao")
    parser.add_argument("--ticket-id", help="For complete action")
    
    args = parser.parse_args()
    
    if args.action == "create":
        ticket_id, path = create_ticket(args.agent, args.task, args.role, args.parent)
        print(f"✅ Created: {ticket_id}")
        print(f"📁 Path: {path}")
    
    elif args.action == "badge":
        generate_badge(args.ticket_id or f"TEST-{datetime.now().strftime('%Y%m%d')}", 
                      args.agent, args.role, args.parent)
    
    elif args.action == "complete":
        if not args.ticket_id:
            print("❌ --ticket-id required")
            sys.exit(1)
        complete_ticket(args.ticket_id)
    
    elif args.action == "full":
        # 完整流程
        ticket_id, path = create_ticket(args.agent, args.task, args.role, args.parent)
        print(f"✅ Created ticket: {ticket_id}")
        generate_badge(ticket_id, args.agent, args.role, args.parent)
        print("🚀 Ready to spawn subagent via sessions_spawn")
        print(f"   After completion, run: python3 {__file__} complete --ticket-id {ticket_id}")
