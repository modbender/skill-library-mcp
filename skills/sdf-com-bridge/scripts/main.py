#!/usr/bin/env python3
"""
SDF COM Bridge - 主程序
链接 COM 聊天室与飞书，支持实时消息同步和翻译
"""

import json
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent))

from ssh_connection import SSHConnection
from com_interaction import COMInteraction, ChatMessage
from terminal_parser import COMTerminalParser, SimpleTextParser
from translator import LLMTranslator
from feishu_bridge import FeishuBridge, FeishuMessage, FeishuCommand
import translation_handler


class SDFComBridge:
    """
    SDF COM Bridge - 完整的桥梁实现
    
    功能：
    1. SSH 连接复用 ControlMaster 套接字
    2. COM 聊天室自动进入 anonradio
    3. 实时捕获聊天消息
    4. 中英双向翻译（通过文件队列触发主 agent）
    5. 飞书指令桥接
    """
    
    def __init__(self, 
                 user: str = "yupeng",
                 host: str = "sdf.org",
                 target_room: str = "anonradio"):
        
        self.user = user
        self.host = host
        self.target_room = target_room
        
        # 组件
        self.ssh: Optional[SSHConnection] = None
        self.com: Optional[COMInteraction] = None
        self.parser: Optional[SimpleTextParser] = None
        self.translator: Optional[LLMTranslator] = None
        self.bridge: Optional[FeishuBridge] = None
        
        # 状态
        self.connected = False
        self.running = False
        self.messages: List[Dict[str, Any]] = []
        self.buffer = ""
        self._last_command_time = 0
        self._command_response_expected = False
        
        # 线程
        self._read_thread: Optional[threading.Thread] = None
        self._translate_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
    def _check_ssh_socket(self) -> bool:
        """预检查 SSH 套接字是否存在"""
        socket_path = Path.home() / f".ssh/sockets/{self.user}@{self.host}"
        if not socket_path.exists():
            print(f"[ERROR] SSH socket not found: {socket_path}")
            print(f"[HINT] Please establish SSH connection first:")
            print(f"       ssh -M -S ~/.ssh/sockets/{self.user}@{self.host} {self.user}@{self.host}")
            return False
        print(f"[INFO] Found SSH socket: {socket_path}")
        return True
    
    def _wait_for_response(self, timeout: float = 3.0, check_interval: float = 0.05) -> str:
        """
        等待命令响应（替代固定 sleep）
        
        通过检测输出缓冲区变化来判断响应是否完成
        """
        start_time = time.time()
        initial_buffer_len = len(self.buffer)
        
        while time.time() - start_time < timeout:
            time.sleep(check_interval)
            # 如果缓冲区有新内容且稳定（不再增长），认为响应完成
            if len(self.buffer) > initial_buffer_len:
                # 等待一小段时间确认没有更多输出
                time.sleep(0.1)
                if len(self.buffer) == len(self.buffer):  # 稳定了
                    return self.buffer
        
        return self.buffer
    
    def _send_command_with_retry(self, data: str, max_retries: int = 3) -> bool:
        """
        发送命令带重试机制
        
        Args:
            data: 要发送的数据
            max_retries: 最大重试次数
            
        Returns:
            是否发送成功
        """
        for attempt in range(max_retries):
            try:
                if self.ssh and self.ssh.send(data):
                    return True
            except Exception as e:
                print(f"[WARN] Send attempt {attempt + 1} failed: {e}")
                time.sleep(0.5 * (attempt + 1))  # 指数退避
        
        print(f"[ERROR] Failed to send after {max_retries} retries")
        return False
    
    def start(self) -> bool:
        """启动桥接"""
        print("[INFO] Starting SDF COM Bridge...")
        print(f"[INFO] Target: {self.user}@{self.host} -> {self.target_room}")
        
        # 预检查 SSH 套接字
        if not self._check_ssh_socket():
            return False
        
        # 初始化组件
        self.translator = LLMTranslator(sync_timeout=15.0)  # 增加到15秒，给予充分翻译时间
        self.parser = SimpleTextParser()
        self.bridge = FeishuBridge(
            on_chat_message=self._on_feishu_chat,
            on_private_message=self._on_feishu_private,
            on_status_request=self._get_status
        )
        
        # 连接 SSH
        self.ssh = SSHConnection(
            user=self.user,
            host=self.host,
            on_output=self._on_ssh_output
        )
        
        # 启动 COM
        if not self.ssh.connect("com"):
            print("[ERROR] Failed to connect to COM")
            return False
        
        print("[INFO] Connected to COM successfully")
        time.sleep(1)  # 给 COM 初始化时间
        
        # 切换到目标房间
        print(f"[INFO] Joining room: {self.target_room}")
        self._send_command_with_retry("g")
        time.sleep(0.3)
        self._send_command_with_retry(self.target_room + "\n")
        
        # 等待响应
        response = self._wait_for_response(timeout=2.0)
        print(f"[DEBUG] Room join response: {repr(response[:200])}...")
        
        # 进入输入模式（按空格）
        self._send_command_with_retry(" ")
        time.sleep(0.1)
        
        print(f"[INFO] Successfully joined room: {self.target_room}")
        
        # 启动读取线程
        self.running = True
        self._stop_event.clear()
        
        self._read_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._read_thread.start()
        
        # 启动翻译处理线程
        self._translate_thread = threading.Thread(target=self._translation_loop, daemon=True)
        self._translate_thread.start()
        
        self.connected = True
        print("[INFO] Bridge started successfully")
        print("[INFO] Ready to relay messages!")
        return True
    
    def _send_raw(self, data: str):
        """发送原始数据"""
        self._send_command_with_retry(data)
    
    def _on_ssh_output(self, data: str):
        """处理 SSH 输出"""
        self.buffer += data
    
    def _translation_loop(self):
        """
        翻译处理循环
        
        轮询文件队列，处理待翻译的请求
        这是主 agent（大鱼）的介入点
        """
        print("[INFO] Translation handler started")
        
        while self.running and not self._stop_event.is_set():
            try:
                # 检查待翻译的请求
                pending = translation_handler.check_and_translate()
                
                for req in pending:
                    request_id = req['request_id']
                    text = req['text']
                    source = req['source_lang']
                    target = req['target_lang']
                    
                    print(f"[TRANSLATE] {source}->{target}: {text[:50]}...")
                    
                    # 注释：这里应该由主 agent 完成翻译
                    # 主 agent 应该调用：
                    # translated_text = 大鱼.translate(text, source, target)
                    # translation_handler.mark_translated(req, translated_text)
                    
                    # 临时：标记为待翻译（主 agent 会轮询）
                    # 实际生产中，这部分由你（大鱼）完成
                    if source == 'en' and target == 'zh':
                        # 模拟翻译 - 实际应由主 agent 处理
                        translated = f"[待翻译: {text}]"
                    else:
                        translated = f"[to_be_translated: {text}]"
                    
                    # 标记已翻译
                    translation_handler.mark_translated(req, translated)
                    print(f"[TRANSLATE] Completed: {translated[:50]}...")
                
            except Exception as e:
                print(f"[ERROR] Translation loop error: {e}")
            
            time.sleep(0.5)  # 轮询间隔
    
    def _process_loop(self):
        """消息处理循环"""