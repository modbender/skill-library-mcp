#!/usr/bin/env python3
"""AgentRelay 处理器 - 向后兼容的 Wrapper 脚本

⚠️ 注意：此脚本仅用于向后兼容，推荐使用 run_relay.py

用法:
    python handle_relay.py receive "REQ,event_id,s/file.json,,"
    python handle_relay.py update event_id '{"status": "completed"}'
    python handle_relay.py ack event_id SECRET123
"""

import sys
from pathlib import Path

# 使用相对路径，避免硬编码
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

# 重定向到 run_relay.py
from run_relay import main

if __name__ == "__main__":
    main()
