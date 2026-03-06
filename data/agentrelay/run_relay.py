#!/usr/bin/env python3
"""AgentRelay 完整执行脚本 - agents 必须调用这个脚本完成接力"""

import sys
import json
import os
from pathlib import Path

# 使用相对路径，避免硬编码
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

from __init__ import AgentRelayTool

def main():
    if len(sys.argv) < 3:
        print("Usage: run_relay.py <action> <csv_or_event_id> [data]")
        print("Actions: receive, complete")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "receive":
        csv_msg = sys.argv[2]
        result = AgentRelayTool.receive(csv_msg)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "complete":
        event_id = sys.argv[2]
        poem_line = sys.argv[3] if len(sys.argv) > 3 else ""
        next_agent = sys.argv[4] if len(sys.argv) > 4 else ""
        next_event_id = sys.argv[5] if len(sys.argv) > 5 else None
        
        # 更新文件（为下一跳准备）
        AgentRelayTool.update(event_id, {
            'status': 'completed',
            'poem_line': poem_line,
            'next_agent': next_agent
        }, next_event_id)
        print(f"✅ Created pointer for {next_event_id or event_id}")
        
        # 生成 CMP (Complete)
        cmp_msg = AgentRelayTool.ack(event_id, '')
        print(f"✅ CMP: {cmp_msg}")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
