#!/usr/bin/env python3
"""
错误恢复机制
状态保存、重连、失败恢复
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime


STATE_FILE = Path.home() / ".openclaw/workspace/.com-bridge/state.json"
ERROR_LOG = Path.home() / ".openclaw/workspace/.com-bridge/error.log"


@dataclass
class BridgeState:
    """桥接状态"""
    connected: bool = False
    room: str = ""
    user: str = ""
    host: str = ""
    last_message_time: Optional[str] = None
    message_count: int = 0
    connection_errors: int = 0
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BridgeState":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ErrorRecovery:
    """错误恢复管理器"""
    
    MAX_RECONNECT_ATTEMPTS = 5
    RECONNECT_DELAY_BASE = 2.0  # 指数退避基数
    
    def __init__(self):
        self.state = BridgeState()
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, **kwargs):
        """
        保存状态
        
        Args:
            **kwargs: 状态字段更新
        """
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        
        # 更新时间戳
        self.state.last_message_time = datetime.utcnow().isoformat()
        
        try:
            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_error(f"Failed to save state: {e}")
    
    def load_state(self) -> Optional[BridgeState]:
        """加载状态"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return BridgeState.from_dict(data)
        except Exception as e:
            self.log_error(f"Failed to load state: {e}")
        return None
    
    def log_error(self, message: str):
        """
        记录错误日志
        
        写入 .com-bridge/error.log，便于排查问题
        """
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        try:
            with open(ERROR_LOG, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            self.state.last_error = message
        except Exception:
            pass
        
        print(f"[ERROR] {message}")
    
    def get_reconnect_delay(self, attempt: int) -> float:
        """
        计算重连延迟
        
        使用指数退避：2^attempt 秒
        
        Args:
            attempt: 当前重试次数（从0开始）
            
        Returns:
            延迟秒数
        """
        delay = self.RECONNECT_DELAY_BASE * (2 ** attempt)
        return min(delay, 60.0)  # 最大60秒
    
    def should_retry(self, attempt: int) -> bool:
        """检查是否应该继续重试"""
        return attempt < self.MAX_RECONNECT_ATTEMPTS
    
    def reset_error_count(self):
        """重置错误计数"""
        self.state.connection_errors = 0
        self.save_state()
    
    def increment_error(self) -> int:
        """增加错误计数，返回当前错误数"""
        self.state.connection_errors += 1
        self.save_state()
        return self.state.connection_errors
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        return {
            "state_file": str(STATE_FILE),
            "error_log": str(ERROR_LOG),
            "current_state": self.state.to_dict(),
            "can_recover": self.state.connection_errors < self.MAX_RECONNECT_ATTEMPTS
        }
    
    @staticmethod
    def print_recovery_instructions():
        """打印恢复指引"""
        print("\n" + "=" * 60)
        print("RECOVERY OPTIONS (恢复选项)")
        print("=" * 60)
        print()
        print("1. Check state file:")
        print(f"   cat {STATE_FILE}")
        print()
        print("2. View error log:")
        print(f"   tail -f {ERROR_LOG}")
        print()
        print("3. Manual recovery steps:")
        print("   a. Verify SSH connection: ssh yupeng@sdf.org")
        print("   b. Check COM availability: com")
        print("   c. Restart bridge: python main.py")
        print()
        print("4. Clear state and start fresh:")
        print(f"   rm {STATE_FILE}")
        print("   python main.py")
        print()
        print("=" * 60)


# 便捷函数
def save_connection_state(**kwargs):
    """保存连接状态"""
    recovery = ErrorRecovery()
    recovery.save_state(**kwargs)


def log_connection_error(message: str):
    """记录连接错误"""
    recovery = ErrorRecovery()
    recovery.log_error(message)


def get_reconnect_strategy(attempt: int) -> tuple:
    """
    获取重连策略
    
    Returns:
        (should_retry, delay_seconds)
    """
    recovery = ErrorRecovery()
    should = recovery.should_retry(attempt)
    delay = recovery.get_reconnect_delay(attempt) if should else 0
    return should, delay


if __name__ == "__main__":
    # 测试
    recovery = ErrorRecovery()
    recovery.save_state(connected=True, room="anonradio", user="yupeng")
    
    print("State saved!")
    loaded = recovery.load_state()
    print(f"Loaded: {loaded.to_dict()}")
    
    recovery.log_error("Test error message")
    print(f"\nStatus: {recovery.get_status_report()}")
    
    recovery.print_recovery_instructions()
