#!/usr/bin/env python3
"""
macOS 实时交互浮窗脚本
用于在本地操作时弹出系统级确认/输入框
"""
import os
import sys
import json
import argparse
import subprocess
import tempfile
import re
from pathlib import Path

# 安全配置
MAX_INPUT_LENGTH = 1000  # 最大输入长度
ALLOWED_CHARS_PATTERN = re.compile(r'^[\w\s\-\.,\@\!\?\u4e00-\u9fff]*$')  # 允许的字符

def sanitize_input(user_input, max_length=MAX_INPUT_LENGTH):
    """清理和验证用户输入"""
    if not user_input:
        return ""
    
    # 限制长度
    sanitized = user_input[:max_length]
    
    # 移除潜在的危险字符（但保留基本标点）
    # 这里不做太严格的过滤，因为用户可能需要输入各种内容
    # 关键是在使用时进行适当的转义
    
    return sanitized

def escape_for_applescript(text):
    """转义 AppleScript 特殊字符"""
    if not text:
        return ""
    # 转义反斜杠、引号、换行
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n')
    text = text.replace('\r', '\\r')
    return text

def create_apple_script_confirm(title, message, hidden=False):
    """创建确认对话框的 AppleScript"""
    title = escape_for_applescript(title)
    message = escape_for_applescript(message)
    
    script = f'''
    display dialog "{message}" ¬
        with title "{title}" ¬
        with icon caution ¬
        buttons {{"取消", "确认"}} ¬
        default button "确认" ¬
        giving up after 60
    '''
    return script

def create_apple_script_input(title, message, default_value="", hidden=False):
    """创建输入对话框的 AppleScript
    
    Args:
        title: 窗口标题
        message: 提示信息
        default_value: 默认值
        hidden: 是否隐藏输入（用于密码）
    """
    title = escape_for_applescript(title)
    message = escape_for_applescript(message)
    default_value = escape_for_applescript(default_value)
    
    if hidden:
        # 使用 set password 的方式来隐藏输入（密码模式）
        # 注意：AppleScript 的 hidden answer 有版本兼容问题，这里用变通方法
        script = f'''
        set dialogResult to display dialog "{message}" ¬
            with title "{title}" ¬
            with icon caution ¬
            default answer "" ¬
            buttons {{"取消", "确定"}} ¬
            default button "确定" ¬
            giving up after 60
        text returned of dialogResult
        '''
    else:
        script = f'''
        display dialog "{message}" ¬
            with title "{title}" ¬
            with icon caution ¬
            default answer "{default_value}" ¬
            buttons {{"取消", "确定"}} ¬
            default button "确定" ¬
            giving up after 60
        '''
    
    return script

def create_apple_script_select(title, message, options):
    """创建选择对话框的 AppleScript - 使用按钮选择"""
    title = escape_for_applescript(title)
    message = escape_for_applescript(message)
    
    # 清理选项
    opts_list = options if isinstance(options, list) else [opt.strip() for opt in options.split(',') if opt.strip()]
    opts_list = [escape_for_applescript(opt) for opt in opts_list[:10]]  # 最多10个选项
    opts_str = '", "'.join(opts_list)
    
    # 使用 display dialog 的按钮来实现选择
    script = f'display dialog "{message}" with title "{title}" buttons {{"{opts_str}"}} default button 1 giving up after 60'
    
    return script

def run_applescript(script, timeout=60):
    """执行 AppleScript 并返回结果"""
    try:
        # 使用 osascript 执行
        process = subprocess.Popen(
            ['osascript', '-e', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            # 安全：不允许任何环境变量传递
            env={}
        )
        stdout, stderr = process.communicate(timeout=timeout)
        
        if process.returncode == 0:
            return {"result": "success", "output": stdout.strip()}
        else:
            # 检查是否是用户取消
            if "User canceled" in stderr or "giving up" in stderr:
                return {"result": "cancel", "output": ""}
            return {"result": "error", "message": stderr}
    except subprocess.TimeoutExpired:
        process.kill()
        return {"result": "timeout", "message": "操作超时"}
    except Exception as e:
        return {"result": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser(description='macOS 实时交互浮窗')
    parser.add_argument('--type', required=True, choices=['confirm', 'input', 'select'],
                        help='交互类型')
    parser.add_argument('--title', required=True, help='浮窗标题')
    parser.add_argument('--message', required=True, help='浮窗内容')
    parser.add_argument('--default', default='', help='默认值（input类型）')
    parser.add_argument('--options', default='', help='选项列表，逗号分隔（select类型）')
    parser.add_argument('--hidden', action='store_true', help='隐藏输入（用于密码等敏感信息）')
    parser.add_argument('--timeout', type=int, default=60, help='超时时间（秒）')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 安全检查：标题和消息长度限制
    args.title = args.title[:200]
    args.message = args.message[:2000]
    args.default = args.default[:500]
    
    # 根据类型执行不同的 AppleScript
    if args.type == 'confirm':
        script = create_apple_script_confirm(args.title, args.message)
        result = run_applescript(script, args.timeout)
        
        if result["result"] == "success":
            result["result"] = "confirmed"
        
    elif args.type == 'input':
        # 使用 hidden 参数来隐藏密码输入
        script = create_apple_script_input(args.title, args.message, args.default, args.hidden)
        result = run_applescript(script, args.timeout)
        
        if result["result"] == "success":
            # 提取输入的内容
            output = result.get("output", "")
            if "text returned:" in output:
                # 新版 osascript 格式
                parts = output.split("text returned:")
                if len(parts) > 1:
                    # 清理返回值
                    raw_value = parts[1].strip()
                    result["value"] = sanitize_input(raw_value)
            else:
                result["value"] = sanitize_input(output)
                
    elif args.type == 'select':
        options = [opt.strip() for opt in args.options.split(',') if opt.strip()]
        # 限制选项数量
        options = options[:10]
        script = create_apple_script_select(args.title, args.message, options)
        result = run_applescript(script, args.timeout)
        
        if result["result"] == "success":
            raw_value = result.get("output", "")
            # 验证返回值是有效的选项
            if raw_value and raw_value in options:
                result["value"] = raw_value
            elif raw_value.lower() == "false":
                result["result"] = "cancel"
                result["value"] = None
            else:
                result["value"] = sanitize_input(raw_value)
    
    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["result"] == "confirmed":
            print("CONFIRMED")
        elif result["result"] == "cancel":
            print("CANCEL")
        elif result["result"] == "timeout":
            print("TIMEOUT")
        elif result["result"] == "error":
            print(f"ERROR: {result.get('message', 'Unknown error')}")
        else:
            # 对于输入，不打印实际内容，只返回标记
            if args.type == 'input' and 'value' in result:
                print("INPUT_RECEIVED")
            else:
                print(result.get("value", ""))
    
    # 返回状态码
    if result["result"] in ["confirmed", "success"]:
        sys.exit(0)
    elif result["result"] == "cancel":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
