#!/usr/bin/env python3
"""
SSH Connection Manager for SDF COM Bridge
复用已有 SSH ControlMaster 套接字连接
"""

import subprocess
import socket
import os
import sys
from pathlib import Path
from typing import Optional, Callable
import select
import threading
import time

class SSHConnection:
    """管理到 SDF 的 SSH 连接，复用 ControlMaster 套接字"""
    
    def __init__(self, user: str = "yupeng", host: str = "sdf.org",
                 socket_path: Optional[str] = None,
                 on_output: Optional[Callable[[str], None]] = None):
        self.user = user
        self.host = host
        self.socket_path = socket_path or f"~/.ssh/sockets/{user}@{host}"
        self.socket_path = os.path.expanduser(self.socket_path)
        self.on_output = on_output
        
        self.process: Optional[subprocess.Popen] = None
        self.connected = False
        self._read_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
    def _check_socket(self) -> bool:
        """检查 ControlMaster 套接字是否存在且可用"""
        if not os.path.exists(self.socket_path):
            return False
        try:
            # 验证套接字是否可用
            result = subprocess.run(
                ["ssh", "-O", "check", f"{self.user}@{self.host}"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def connect(self, command: Optional[str] = None) -> bool:
        """
        连接到 SSH 并执行命令
        如果 command 为 None，则启动交互式 shell
        """
        if not self._check_socket():
            print(f"[ERROR] SSH socket not available: {self.socket_path}")
            return False
        
        cmd = ["ssh", f"{self.user}@{self.host}"]
        if command:
            cmd.extend(command.split() if isinstance(command, str) else command)
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
                universal_newlines=False
            )
            self.connected = True
            
            # 启动读取线程
            self._stop_event.clear()
            self._read_thread = threading.Thread(target=self._read_output, daemon=True)
            self._read_thread.start()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False
    
    def _read_output(self):
        """后台读取 SSH 输出"""
        if not self.process or not self.process.stdout:
            return
        
        while not self._stop_event.is_set():
            try:
                # 使用 select 进行非阻塞读取
                ready, _, _ = select.select([self.process.stdout], [], [], 0.1)
                if ready:
                    data = self.process.stdout.read(4096)
                    if data:
                        try:
                            text = data.decode('utf-8', errors='replace')
                            if self.on_output:
                                self.on_output(text)
                        except Exception:
                            pass
                    else:
                        break
            except Exception:
                break
        
        self.connected = False
    
    def send(self, data: str) -> bool:
        """发送数据到 SSH 进程"""
        if not self.process or not self.process.stdin:
            return False
        
        try:
            self.process.stdin.write(data.encode('utf-8'))
            self.process.stdin.flush()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send: {e}")
            return False
    
    def send_line(self, data: str) -> bool:
        """发送一行数据（自动添加换行符）"""
        return self.send(data + '\n')
    
    def disconnect(self):
        """断开连接"""
        self._stop_event.set()
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                self.process.kill()
            
        self.connected = False
        print("[INFO] SSH connection closed")
    
    def is_alive(self) -> bool:
        """检查连接是否仍然活跃"""
        if not self.process:
            return False
        return self.process.poll() is None


def test_connection():
    """测试 SSH 连接"""
    print("Testing SSH connection to sdf.org...")
    
    def on_output(data: str):
        print(f"[OUTPUT] {repr(data)}")
    
    conn = SSHConnection(on_output=on_output)
    
    if conn.connect("echo 'SSH test successful'"):
        print("[INFO] Connected successfully")
        time.sleep(2)
        conn.disconnect()
    else:
        print("[ERROR] Failed to connect")


if __name__ == "__main__":
    test_connection()
