#!/usr/bin/env python3
"""
Session Monitor - 自动显示 token 消耗和模型信息
"""

import os
import json
import sys
from typing import Dict, Any, Optional

class SessionMonitor:
    def __init__(self):
        self.workspace = os.getenv('OPENCLAW_WORKSPACE', '/home/admin/.openclaw/workspace')
        self.config_path = os.path.join(self.workspace, 'session_monitor_config.json')
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "enabled": True,
            "position": "bottom",  # top, bottom, inline
            "format": "compact",   # compact, detailed
            "show_model": True,
            "show_tokens": True,
            "show_context": True
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception:
                pass
                
        return default_config
        
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}", file=sys.stderr)
            
    def toggle_enabled(self, enabled: bool):
        """切换启用状态"""
        self.config['enabled'] = enabled
        self.save_config()
        return f"Session monitor {'enabled' if enabled else 'disabled'}"
        
    def set_position(self, position: str):
        """设置显示位置"""
        if position in ['top', 'bottom', 'inline']:
            self.config['position'] = position
            self.save_config()
            return f"Display position set to {position}"
        return f"Invalid position: {position}. Use top, bottom, or inline"
        
    def set_format(self, format_type: str):
        """设置显示格式"""
        if format_type in ['compact', 'detailed']:
            self.config['format'] = format_type
            self.save_config()
            return f"Format set to {format_type}"
        return f"Invalid format: {format_type}. Use compact or detailed"
        
    def get_status_info(self, session_data: Dict[str, Any]) -> str:
        """获取状态信息字符串"""
        if not self.config['enabled']:
            return ""
            
        model = session_data.get('model', 'unknown')
        input_tokens = session_data.get('input_tokens', 0)
        output_tokens = session_data.get('output_tokens', 0)
        context_used = session_data.get('context_used', 0)
        context_total = session_data.get('context_total', 262144)
        
        # 格式化数字
        def format_number(num):
            if num >= 1000000:
                return f"{num//1000000}M"
            elif num >= 1000:
                return f"{num//1000}k"
            else:
                return str(num)
                
        context_percent = (context_used / context_total * 100) if context_total > 0 else 0
        
        if self.config['format'] == 'compact':
            parts = []
            if self.config['show_model']:
                parts.append(f"🧠 {model.split('/')[-1] if '/' in model else model}")
            if self.config['show_tokens']:
                parts.append(f"📥{format_number(input_tokens)}/📤{format_number(output_tokens)}")
            if self.config['show_context']:
                parts.append(f"Context: {context_percent:.0f}%")
            return f"[{' | '.join(parts)}]"
        else:
            lines = []
            if self.config['show_model']:
                lines.append(f"Model: {model}")
            if self.config['show_tokens']:
                lines.append(f"Tokens: Input {format_number(input_tokens)}, Output {format_number(output_tokens)}")
            if self.config['show_context']:
                lines.append(f"Context: {format_number(context_used)}/{format_number(context_total)} ({context_percent:.1f}%)")
            return "\n".join(lines)
            
    def inject_status(self, response: str, session_data: Dict[str, Any]) -> str:
        """将状态信息注入到响应中"""
        status_info = self.get_status_info(session_data)
        if not status_info:
            return response
            
        if self.config['position'] == 'top':
            return f"{status_info}\n\n{response}"
        elif self.config['position'] == 'bottom':
            return f"{response}\n\n{status_info}"
        else:  # inline
            return f"{response} {status_info}"

def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Session Monitor CLI')
    parser.add_argument('--toggle', choices=['on', 'off'], help='Enable or disable session monitor')
    parser.add_argument('--position', choices=['top', 'bottom', 'inline'], help='Set display position')
    parser.add_argument('--format', choices=['compact', 'detailed'], help='Set display format')
    parser.add_argument('--status', action='store_true', help='Show current status info')
    parser.add_argument('--inject', action='store_true', help='Inject status into response')
    parser.add_argument('--response', help='Response text to inject status into')
    parser.add_argument('--session-data', help='JSON string of session data')
    
    args = parser.parse_args()
    
    monitor = SessionMonitor()
    
    if args.toggle:
        enabled = args.toggle == 'on'
        print(monitor.toggle_enabled(enabled))
    elif args.position:
        print(monitor.set_position(args.position))
    elif args.format:
        print(monitor.set_format(args.format))
    elif args.status:
        if args.session_data:
            session_data = json.loads(args.session_data)
            print(monitor.get_status_info(session_data))
        else:
            print("No session data provided")
    elif args.inject:
        if args.response and args.session_data:
            session_data = json.loads(args.session_data)
            result = monitor.inject_status(args.response, session_data)
            print(result)
        else:
            print("Both --response and --session-data are required for injection")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()