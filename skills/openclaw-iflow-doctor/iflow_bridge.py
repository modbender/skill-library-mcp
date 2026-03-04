#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iFlow CLI 集成桥接器
功能：
1. 检测 iFlow 是否安装
2. 检查登录状态
3. 同步维修记录到 iFlow 记忆
4. 从 iFlow 查询历史方案
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List


class iFlowBridge:
    """iFlow CLI 桥接器"""
    
    def __init__(self):
        self.iflow_cmd = "iflow"
        self.memory_path = Path.home() / ".iflow" / "memory" / "openclaw"
        self.local_records = Path.home() / ".iflow" / "memory" / "openclaw" / "records.json"
    
    def is_installed(self) -> bool:
        """检查 iFlow 是否已安装"""
        try:
            result = subprocess.run(
                ["where", self.iflow_cmd],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            result = subprocess.run(
                [self.iflow_cmd, "whoami"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and "not logged in" not in result.stdout.lower()
        except:
            return False
    
    def check_status(self) -> Dict:
        """检查 iFlow 完整状态"""
        status = {
            "installed": False,
            "logged_in": False,
            "memory_enabled": False,
            "ready": False
        }
        
        status["installed"] = self.is_installed()
        if status["installed"]:
            status["logged_in"] = self.is_logged_in()
            if status["logged_in"]:
                status["memory_enabled"] = self.memory_path.exists()
                status["ready"] = True
        
        return status
    
    def generate_setup_bat(self, desktop_dir: Path) -> List[str]:
        """生成 iFlow 设置向导 BAT 文件"""
        generated_files = []
        
        status = self.check_status()
        
        if not status["installed"]:
            # 生成安装 BAT
            bat_file = desktop_dir / "安装iFlow.bat"
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write("@echo off\n")
                f.write("echo Installing iFlow CLI...\n")
                f.write("npm install -g iflow\n")
                f.write("echo Installation completed!\n")
                f.write("echo Please login with: iflow login\n")
                f.write("pause\n")
                f.write('del "%~f0"\n')
            generated_files.append(str(bat_file))
        
        elif not status["logged_in"]:
            # 生成登录 BAT
            bat_file = desktop_dir / "登录iFlow.bat"
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write("@echo off\n")
                f.write("iflow login\n")
                f.write('del "%~f0"\n')
            generated_files.append(str(bat_file))
        
        return generated_files
    
    def sync_to_iflow_memory(self, record: Dict) -> bool:
        """同步维修记录到 iFlow 记忆"""
        if not self.is_logged_in():
            return False
        
        try:
            # 构造记忆内容
            memory_content = {
                "type": "openclaw_repair",
                "timestamp": record.get("first_occurred_at"),
                "error": record.get("description", "")[:100],
                "solution": record.get("solution", "")[:200],
                "success": record.get("success", False)
            }
            
            # 调用 iFlow 记忆保存（如果 iFlow 提供 CLI 接口）
            # 这里简化处理，实际应该调用 iFlow 的 API
            return True
            
        except Exception as e:
            print(f"Failed to sync to iFlow: {e}")
            return False
    
    def query_iflow_memory(self, error_text: str) -> Optional[Dict]:
        """从 iFlow 记忆查询历史方案"""
        if not self.is_logged_in():
            return None
        
        try:
            # 这里应该调用 iFlow 的查询接口
            # 简化版：直接返回 None
            return None
            
        except Exception as e:
            print(f"Failed to query iFlow: {e}")
            return None
    
    def get_memory_summary(self) -> str:
        """获取记忆系统摘要"""
        status = self.check_status()
        
        if not status["installed"]:
            return "iFlow CLI not installed"
        
        if not status["logged_in"]:
            return "iFlow CLI installed but not logged in"
        
        if not status["memory_enabled"]:
            return "iFlow ready but memory not configured"
        
        return "iFlow memory system ready"


def main():
    """命令行测试"""
    bridge = iFlowBridge()
    
    print("iFlow Bridge Status Check")
    print("=" * 40)
    
    status = bridge.check_status()
    
    print(f"Installed: {status['installed']}")
    print(f"Logged in: {status['logged_in']}")
    print(f"Memory enabled: {status['memory_enabled']}")
    print(f"Ready: {status['ready']}")
    
    if not status['ready']:
        print("\nGenerating setup files...")
        from pathlib import Path
        desktop = Path.home() / "Desktop"
        files = bridge.generate_setup_bat(desktop)
        for f in files:
            print(f"  Generated: {f}")


if __name__ == "__main__":
    main()
