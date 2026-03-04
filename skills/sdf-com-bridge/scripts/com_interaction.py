#!/usr/bin/env python3
"""
COM 命令交互层
封装 com 的主要命令
"""

from typing import Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import time

class COMCommand(Enum):
    """COM 命令枚举"""
    WHO_CURRENT = 'w'          # 查看当前房间用户
    WHO_OTHER = 'W'            # 查看其他房间用户
    LIST_ROOMS = 'l'           # 列出房间
    GOTO = 'g'                 # 进入房间
    HISTORY = 'r'              # 查看历史
    HISTORY_EXT = 'R'            # 扩展历史
    PEEK = 'p'                 # 查看其他房间
    SEND_PRIVATE = 's'         # 发送私信
    EMOTE = 'e'                # 表情动作
    IDLE = 'I'                 # 查看用户空闲时间
    HELP = 'h'                 # 帮助
    QUIT = 'q'                 # 退出
    TOGGLE_BACKSPACE = '-'     # 切换退格行为
    UTC_TIME = '+'             # 显示 UTC 时间
    USER_INFO = 'U'            # 用户信息


@dataclass
class ChatMessage:
    """聊天消息数据结构"""
    user: str
    message: str
    timestamp: Optional[str] = None
    room: Optional[str] = None
    message_type: str = "chat"  # chat, emote, join, leave, private
    
    def to_dict(self) -> dict:
        return {
            "user": self.user,
            "message": self.message,
            "timestamp": self.timestamp,
            "room": self.room,
            "message_type": self.message_type
        }


class COMInteraction:
    """
    COM 命令交互封装
    提供高级接口与 COM 交互
    """
    
    DEFAULT_ROOM = "lobby"
    TARGET_ROOM = "anonradio"
    
    def __init__(self, send_callback: Callable[[str], bool],
                 wait_callback: Callable[[float], str]):
        """
        初始化 COM 交互器
        
        Args:
            send_callback: 发送数据的回调函数
            wait_callback: 等待并获取输出的回调函数
        """
        self.send = send_callback
        self.wait = wait_callback
        self.current_room = self.DEFAULT_ROOM
        self._in_input_mode = False
        
    def enter_input_mode(self) -> bool:
        """进入输入模式（按空格）"""
        if not self._in_input_mode:
            self.send(' ')
            self._in_input_mode = True
            time.sleep(0.1)
            return True
        return False
    
    def exit_input_mode(self) -> bool:
        """退出输入模式（按回车发送后自动退出）"""
        self._in_input_mode = False
        return True
    
    def join_room(self, room_name: str) -> bool:
        """
        进入指定房间
        
        Args:
            room_name: 房间名
        """
        if self._in_input_mode:
            self.send('\x03')  # Ctrl+C 取消输入
            self._in_input_mode = False
            time.sleep(0.1)
        
        self.current_room = room_name
        self.send('g')
        time.sleep(0.2)
        self.send(room_name + '\n')
        time.sleep(0.5)
        return True
    
    def join_target_room(self) -> bool:
        """进入目标房间（anonradio）"""
        return self.join_room(self.TARGET_ROOM)
    
    def say(self, message: str) -> bool:
        """
        在聊天室发言
        
        Args:
            message: 要发送的消息
        """
        self.enter_input_mode()
        self.send(message + '\n')
        self._in_input_mode = False
        time.sleep(0.1)
        return True
    
    def emote(self, action: str) -> bool:
        """
        发送表情动作
        
        Args:
            action: 动作描述
        """
        self.send('e')
        time.sleep(0.1)
        self.send(action + '\n')
        time.sleep(0.1)
        return True
    
    def send_private(self, username: str, host: str, message: str,
                     room: Optional[str] = None) -> bool:
        """
        发送私信
        
        Args:
            username: 用户名
            host: 主机名
            message: 消息内容
            room: 可选，对方所在房间
        """
        self.send('s')
        time.sleep(0.1)
        
        target = f"{username}@{host}"
        if room:
            target += f" {room}"
        
        self.send(target + '\n')
        time.sleep(0.1)
        self.send(message + '\n')
        time.sleep(0.1)
        return True
    
    def get_users(self) -> str:
        """获取当前房间用户列表"""
        self.send('w')
        time.sleep(0.3)
        return self.wait(0.5)
    
    def get_history(self, lines: int = 18) -> str:
        """
        获取历史消息
        
        Args:
            lines: 要获取的行数（默认 18 行）
        """
        if lines == 18:
            self.send('r')
        else:
            self.send('R')
            time.sleep(0.1)
            self.send(str(lines) + '\n')
        
        time.sleep(0.3)
        return self.wait(0.5)
    
    def list_rooms(self) -> str:
        """列出所有房间"""
        self.send('l')
        time.sleep(0.3)
        return self.wait(0.5)
    
    def peek_room(self, room_name: str, lines: int = 18) -> str:
        """
        查看其他房间的消息
        
        Args:
            room_name: 房间名
            lines: 历史行数
        """
        self.send('p')
        time.sleep(0.1)
        
        if lines == 18:
            self.send(room_name + '\n')
        else:
            self.send(f"{room_name} {lines}\n")
        
        time.sleep(0.3)
        return self.wait(0.5)
    
    def quit(self) -> bool:
        """退出 COM"""
        self.send('q')
        time.sleep(0.2)
        return True
    
    def fix_backspace(self) -> bool:
        """修复退格键"""
        self.send('-')
        time.sleep(0.1)
        return True
    
    def get_idle_times(self) -> str:
        """获取用户空闲时间"""
        self.send('I')
        time.sleep(0.3)
        return self.wait(0.5)
    
    def get_utc_time(self) -> str:
        """获取 UTC 时间"""
        self.send('+')
        time.sleep(0.2)
        return self.wait(0.3)
    
    def get_user_info(self) -> str:
        """获取其他用户信息"""
        self.send('U')
        time.sleep(0.3)
        return self.wait(0.5)
    
    def get_help(self) -> str:
        """获取帮助"""
        self.send('h')
        time.sleep(0.3)
        return self.wait(0.5)


if __name__ == "__main__":
    # 简单测试
    print("COM Interaction module loaded")
    print(f"Default room: {COMInteraction.DEFAULT_ROOM}")
    print(f"Target room: {COMInteraction.TARGET_ROOM}")
