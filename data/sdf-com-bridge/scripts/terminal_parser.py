#!/usr/bin/env python3
"""
终端仿真层
使用 pyte 解析 COM 的 ncurses 输出
"""

import re
import pyte
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
from com_interaction import ChatMessage


@dataclass
class ParsedLine:
    """解析后的行"""
    raw_text: str
    clean_text: str
    line_number: int
    

class COMTerminalParser:
    """
    COM 终端解析器
    使用 pyte 处理 xterm 输出，提取聊天内容
    """
    
    # 正则模式：匹配 COM 聊天行格式 [username] message
    CHAT_PATTERN = re.compile(r'\[([^\]]+)\]\s*(.+)')
    # 用户进入/离开模式
    JOIN_PATTERN = re.compile(r'<([^>]+)\s+appears>')
    LEAVE_PATTERN = re.compile(r'<([^>]+\s+DUMPs)>')
    # 私信模式
    PRIVATE_PATTERN = re.compile(r'From\s+([^:]+):\s*(.+)')
    # 动作/表情模式
    EMOTE_PATTERN = re.compile(r'\*\s*(\S+)\s+(.+)')
    # 系统消息模式
    SYSTEM_PATTERN = re.compile(r'^(Unlinking|Connecting|Welcome|You are in|>>>|<<<)')
    
    def __init__(self, columns: int = 80, rows: int = 24):
        """
        初始化解析器
        
        Args:
            columns: 终端列数
            rows: 终端行数
        """
        self.columns = columns
        self.rows = rows
        
        # 创建 pyte 屏幕和流
        self.screen = pyte.Screen(columns, rows)
        self.stream = pyte.ByteStream(self.screen)
        
        # 当前屏幕内容的缓存
        self._prev_lines: List[str] = []
        
    def parse(self, data: bytes) -> List[ChatMessage]:
        """
        解析终端输出数据
        
        Args:
            data: 原始终端输出字节
            
        Returns:
            提取的聊天消息列表
        """
        # 将数据送入 pyte 流
        self.stream.feed(data)
        
        # 获取当前屏幕内容
        current_lines = self._get_screen_lines()
        
        # 检测变化
        new_messages = self._detect_changes(current_lines)
        
        # 更新缓存
        self._prev_lines = current_lines.copy()
        
        return new_messages
    
    def _get_screen_lines(self) -> List[str]:
        """获取当前屏幕的所有行"""
        lines = []
        for i in range(self.screen.lines):
            line = self.screen.buffer[i]
            text = ''.join(char.data for char in line)
            lines.append(text.rstrip())
        return lines
    
    def _detect_changes(self, current_lines: List[str]) -> List[ChatMessage]:
        """检测屏幕变化并提取新消息"""
        messages = []
        
        for i, line in enumerate(current_lines):
            # 跳过空行
            if not line.strip():
                continue
                
            # 如果这是新内容或变化的行
            if i >= len(self._prev_lines) or line != self._prev_lines[i]:
                message = self._parse_line(line)
                if message:
                    messages.append(message)
        
        return messages
    
    def _parse_line(self, line: str) -> Optional[ChatMessage]:
        """
        解析单行内容
        
        Args:
            line: 要解析的行
            
        Returns:
            解析后的消息，如果不是聊天消息则返回 None
        """
        line = line.strip()
        if not line:
            return None
        
        timestamp = datetime.utcnow().isoformat()
        
        # 尝试匹配聊天消息 [user] message
        match = self.CHAT_PATTERN.match(line)
        if match:
            user = match.group(1).strip()
            message = match.group(2).strip()
            return ChatMessage(
                user=user,
                message=message,
                timestamp=timestamp,
                message_type="chat"
            )
        
        # 尝试匹配用户进入
        match = self.JOIN_PATTERN.match(line)
        if match:
            user = match.group(1).strip()
            return ChatMessage(
                user=user,
                message=f"{user} has joined the room",
                timestamp=timestamp,
                message_type="join"
            )
        
        # 尝试匹配用户离开
        match = self.LEAVE_PATTERN.match(line)
        if match:
            user = match.group(1).strip()
            return ChatMessage(
                user=user,
                message=f"{user} has left the room",
                timestamp=timestamp,
                message_type="leave"
            )
        
        # 尝试匹配私信
        match = self.PRIVATE_PATTERN.match(line)
        if match:
            user = match.group(1).strip()
            message = match.group(2).strip()
            return ChatMessage(
                user=user,
                message=message,
                timestamp=timestamp,
                message_type="private"
            )
        
        # 尝试匹配动作/表情
        match = self.EMOTE_PATTERN.match(line)
        if match:
            user = match.group(1).strip()
            action = match.group(2).strip()
            return ChatMessage(
                user=user,
                message=f"*{user} {action}",
                timestamp=timestamp,
                message_type="emote"
            )
        
        # 跳过系统消息
        if self.SYSTEM_PATTERN.match(line):
            return None
        
        # 无法识别的内容，可能是聊天的一部分
        return None
    
    def get_screen_dump(self) -> str:
        """获取当前屏幕内容的文本转储"""
        lines = self._get_screen_lines()
        return '\n'.join(lines)
    
    def clear_screen(self):
        """清空屏幕"""
        self.screen.reset()
        self._prev_lines = []
    
    def resize(self, columns: int, rows: int):
        """调整终端大小"""
        self.columns = columns
        self.rows = rows
        self.screen.resize(columns, rows)


class SimpleTextParser:
    """
    简单的文本解析器（备用）
    当 pyte 不适用时使用，直接处理纯文本输出
    """
    
    CHAT_PATTERN = re.compile(r'\[([^\]]+)\]\s*(.+)')
    
    def __init__(self):
        self._buffer = ""
        self._seen_messages: set = set()
    
    def feed(self, data: str) -> List[ChatMessage]:
        """
        处理文本数据
        
        Args:
            data: 文本数据
            
        Returns:
            新消息列表
        """
        self._buffer += data
        messages = []
        
        # 按行分割
        lines = self._buffer.split('\n')
        self._buffer = lines[-1]  # 保留最后一行（可能不完整）
        
        for line in lines[:-1]:
            msg = self._parse_line(line)
            if msg:
                # 去重
                msg_key = f"{msg.user}:{msg.message}"
                if msg_key not in self._seen_messages:
                    self._seen_messages.add(msg_key)
                    messages.append(msg)
        
        return messages
    
    def _parse_line(self, line: str) -> Optional[ChatMessage]:
        """解析单行"""
        line = line.strip()
        if not line:
            return None
        
        match = self.CHAT_PATTERN.match(line)
        if match:
            return ChatMessage(
                user=match.group(1).strip(),
                message=match.group(2).strip(),
                timestamp=datetime.utcnow().isoformat(),
                message_type="chat"
            )
        
        return None


if __name__ == "__main__":
    # 测试
    parser = COMTerminalParser()
    
    # 模拟一些输出
    test_data = b"[alice] hello everyone\n[bob] hi alice!\n"
    
    messages = parser.parse(test_data)
    
    print(f"Parsed {len(messages)} messages:")
    for msg in messages:
        print(f"  {msg}")
