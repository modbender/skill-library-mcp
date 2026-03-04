#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 监控守护进程
功能：
1. 监控 openclaw-gateway 进程
2. 检测到崩溃时自动调用修复技能
3. 支持日志监控和健康检查
"""

import os
import sys
import time
import json
import psutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path


class OpenClawWatchdog:
    """OpenClaw 监控守护进程"""
    
    def __init__(self):
        self.running = False
        self.gateway_process = None
        # Bug #5 修复：使用 expanduser() 展开波浪号
        self.log_file = Path.home().expanduser() / ".openclaw" / "logs" / "watchdog.log"
        self.check_interval = 10  # 检查间隔（秒）
        self.crash_threshold = 3  # 崩溃次数阈值
        self.crash_count = 0
        self.last_restart = None
        
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
        
        print(log_line.strip())
    
    def is_gateway_running(self):
        """检查 gateway 是否在运行"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'openclaw-gateway' in cmdline or 'openclaw' in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    
    def check_gateway_health(self):
        """检查 gateway 健康状态"""
        try:
            import urllib.request
            response = urllib.request.urlopen(
                'http://localhost:18789/health',
                timeout=5
            )
            return response.status == 200
        except:
            return False
    
    def call_healing_skill(self, error_msg, error_logs=""):
        """调用修复技能"""
        self.log(f"Calling healing skill for: {error_msg[:50]}...")
        
        try:
            # Bug #4/#5 修复：使用 expanduser() 且不使用 Desktop 目录
            healer_script = Path.home().expanduser() / ".iflow" / "memory" / "openclaw" / "openclaw_memory.py"
            
            result = subprocess.run(
                ['python', str(healer_script), '--fix', error_msg, '--logs', error_logs],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.log(f"Healing result: {result.returncode}")
            if result.stdout:
                self.log(f"Output: {result.stdout[:200]}")
            
            return result.returncode == 0
            
        except Exception as e:
            self.log(f"Healing failed: {e}", "ERROR")
            return False
    
    def restart_gateway(self):
        """重启 gateway"""
        self.log("Restarting OpenClaw Gateway...")
        
        try:
            # Kill existing process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'openclaw-gateway' in cmdline:
                        proc.terminate()
                        proc.wait(timeout=5)
                except:
                    pass
            
            # Wait a moment
            time.sleep(2)
            
            # Start new process
            subprocess.Popen(
                ['openclaw', 'gateway'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            self.last_restart = datetime.now()
            self.log("Gateway restarted successfully")
            return True
            
        except Exception as e:
            self.log(f"Failed to restart gateway: {e}", "ERROR")
            return False
    
    def monitor_loop(self):
        """主监控循环"""
        self.log("Watchdog started")
        self.running = True
        
        while self.running:
            try:
                # 1. 检查进程是否存在
                if not self.is_gateway_running():
                    self.crash_count += 1
                    self.log(f"Gateway not running! Crash count: {self.crash_count}", "WARN")
                    
                    if self.crash_count >= self.crash_threshold:
                        self.log("Crash threshold reached, calling healing skill...", "WARN")
                        
                        # 调用修复技能
                        error_msg = f"Gateway crashed {self.crash_count} times"
                        healing_result = self.call_healing_skill(error_msg)
                        
                        if healing_result:
                            self.log("Healing completed, resetting crash count")
                            self.crash_count = 0
                        else:
                            self.log("Healing failed, manual intervention needed", "ERROR")
                    
                    # 尝试重启
                    self.restart_gateway()
                
                else:
                    # 进程在运行，检查健康状态
                    if not self.check_gateway_health():
                        self.log("Gateway process exists but not responding", "WARN")
                    else:
                        # 健康，重置崩溃计数
                        if self.crash_count > 0:
                            self.log("Gateway healthy, resetting crash count")
                            self.crash_count = 0
                
                # 等待下一次检查
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("Watchdog stopped by user")
                self.running = False
            except Exception as e:
                self.log(f"Watchdog error: {e}", "ERROR")
                time.sleep(self.check_interval)
    
    def start(self):
        """启动监控"""
        self.log("="*60)
        self.log("OpenClaw Watchdog Starting...")
        self.log(f"Check interval: {self.check_interval}s")
        self.log(f"Crash threshold: {self.crash_threshold}")
        self.log("="*60)
        
        # 在后台线程运行
        # Bug #1 修复：daemon=False 防止随主线程退出
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = False  # 修复：非守护线程
        monitor_thread.start()
        
        return monitor_thread
    
    def stop(self):
        """停止监控"""
        self.running = False
        self.log("Watchdog stopping...")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Watchdog")
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--stop', action='store_true', help='Stop monitoring')
    parser.add_argument('--status', action='store_true', help='Check status')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    watchdog = OpenClawWatchdog()
    
    if args.start or args.daemon:
        if args.daemon:
            # 后台运行
            watchdog.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                watchdog.stop()
        else:
            # 前台运行
            watchdog.monitor_loop()
    
    elif args.status:
        running = watchdog.is_gateway_running()
        healthy = watchdog.check_gateway_health() if running else False
        print(f"Gateway running: {running}")
        print(f"Gateway healthy: {healthy}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
