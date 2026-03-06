#!/usr/bin/env python3
"""
统一交互入口脚本
根据场景自动选择合适的浮窗方式
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# 尝试导入项目内的模块
SCRIPT_DIR = Path(__file__).parent

def show_macos_dialog(dialog_type, title, message, default="", options=""):
    """显示 macOS 浮窗"""
    script_path = SCRIPT_DIR / "macos_dialog.py"
    
    cmd = ["python3", str(script_path), 
           "--type", dialog_type,
           "--title", title,
           "--message", message,
           "--json"]
    
    if default:
        cmd.extend(["--default", default])
    if options:
        cmd.extend(["--options", options])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            # 用户取消或超时
            return {"result": "cancel" if result.returncode == 1 else "timeout"}
    except Exception as e:
        return {"result": "error", "message": str(e)}

def show_browser_dialog(dialog_type, title, message, default="", options=""):
    """显示浏览器内浮窗（返回需要注入的JS）"""
    from . import browser_modal
    
    js_code = browser_modal.create_modal_js(dialog_type, title, message, default, options)
    
    # 返回需要注入到浏览器的 JS 代码
    return {
        "type": "browser",
        "js_code": js_code,
        "message": "需要在浏览器中注入JS来显示浮窗"
    }

def main():
    parser = argparse.ArgumentParser(description='实时交互浮窗 - 统一入口')
    parser.add_argument('--type', required=True, 
                        choices=['confirm', 'input', 'select'],
                        help='交互类型')
    parser.add_argument('--title', required=True, help='浮窗标题')
    parser.add_argument('--message', required=True, help='浮窗内容')
    parser.add_argument('--default', default='', help='默认值（input类型）')
    parser.add_argument('--options', default='', help='选项（select类型，逗号分隔）')
    parser.add_argument('--mode', default='auto',
                        choices=['auto', 'macos', 'browser'],
                        help='浮窗模式：auto自动选择，macos系统浮窗，browser浏览器内浮窗')
    parser.add_argument('--timeout', type=int, default=60, help='超时时间')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 根据模式选择合适的浮窗
    if args.mode == 'macos' or args.mode == 'auto':
        result = show_macos_dialog(args.type, args.title, args.message, 
                                  args.default, args.options)
    else:
        result = show_browser_dialog(args.type, args.title, args.message,
                                     args.default, args.options)
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("result") == "confirmed":
            print("CONFIRMED")
        elif result.get("result") == "cancel":
            print("CANCEL")
        elif result.get("result") == "timeout":
            print("TIMEOUT")
        elif result.get("result") == "error":
            print(f"ERROR: {result.get('message', 'Unknown error')}")
        else:
            print(result.get("value", ""))

if __name__ == "__main__":
    main()
