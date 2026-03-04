#!/usr/bin/env python3
"""AgentRelay SKILL - 兼容层（让 LLM "猜"的导入路径也能工作）

这个文件是 __init__.py 的别名，让以下导入语句有效：
    from agentrelay.SKILL import agentrelay_update_file
"""

# 直接从 __init__.py 导入所有公开函数
from __init__ import (
    agentrelay_send,
    agentrelay_receive,
    agentrelay_ack,
    agentrelay_update_file,
    AgentRelayTool,
    generate_secret,
    get_file_alias_path,
    resolve_alias,
    build_csv,
    parse_csv,
    STORAGE_PATH,
    LOG_PATH,
)

# 重新导出，让 LLM 常用的导入方式有效
__all__ = [
    'agentrelay_send',
    'agentrelay_receive', 
    'agentrelay_ack',
    'agentrelay_update_file',
    'AgentRelayTool',
]
