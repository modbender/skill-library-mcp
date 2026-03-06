#!/usr/bin/env python3
"""
飞书联动层
处理飞书消息和指令
"""

import json
import re
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class FeishuCommand(Enum):
    """飞书指令类型"""
    UNKNOWN = "unknown"
    SEND_CHAT = "send_chat"      # com: 发送消息到聊天室
    STATUS = "status"            # com:pwd 报告状态
    SEND_PRIVATE = "send_pm"     # s: 发送私信
    HELP = "help"                # 帮助


@dataclass
class FeishuMessage:
    """飞书消息结构"""
    command: FeishuCommand
    raw_text: str
    content: str
    target_user: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class FeishuBridge:
    """飞书桥接器"""
    
    def __init__(self,
                 on_chat_message: Optional[Callable[[str], bool]] = None,
                 on_private_message: Optional[Callable[[str, str], bool]] = None,
                 on_status_request: Optional[Callable[[], str]] = None):
        self.CHAT_PREFIX = "com:"
        self.STATUS_PREFIX = "com:pwd"
        self.PRIVATE_PREFIX = "s:"
        self.on_chat_message = on_chat_message
        self.on_private_message = on_private_message
        self.on_status_request = on_status_request
        
    def parse_instruction(self, text: str) -> FeishuMessage:
        """解析飞书指令"""
        text = text.strip()
        
        if text == self.STATUS_PREFIX:
            return FeishuMessage(command=FeishuCommand.STATUS, raw_text=text, content="")
        
        if text.startswith(self.PRIVATE_PREFIX):
            content = text[len(self.PRIVATE_PREFIX):].strip()
            match = re.match(r'(\S+@\S+)\s+(.+)', content)
            if match:
                return FeishuMessage(
                    command=FeishuCommand.SEND_PRIVATE,
                    raw_text=text,
                    content=match.group(2),
                    target_user=match.group(1)
                )
        
        if text.startswith(self.CHAT_PREFIX):
            return FeishuMessage(
                command=FeishuCommand.SEND_CHAT,
                raw_text=text,
                content=text[len(self.CHAT_PREFIX):].strip()
            )
        
        return FeishuMessage(command=FeishuCommand.HELP, raw_text=text, content=self._get_help_text())
    
    def _get_help_text(self) -> str:
        return """SDF COM Bridge 指令:
- com: <message> - 发送到聊天室
- com:pwd - 查看状态
- s: user@host <message> - 发送私信"""


if __name__ == "__main__":
    bridge = FeishuBridge()
    print("FeishuBridge ready")
