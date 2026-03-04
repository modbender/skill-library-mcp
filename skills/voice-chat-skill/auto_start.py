#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动启动语音对话系统的包装脚本
"""
import subprocess
import sys
import os

def main():
    """自动启动语音对话系统"""
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    print("🚀 正在启动语音对话系统...")
    print("📱 自动选择：开始语音对话")
    
    # 启动语音对话系统并自动选择选项1
    try:
        # 使用子进程，模拟用户输入
        process = subprocess.Popen(
            [sys.executable, 'voice_chat.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # 发送选项1（开始语音对话）
        stdout, stderr = process.communicate(input='1\n', timeout=5)
        
        # 检查输出
        if process.returncode != 0:
            print(f"❌ 启动失败，返回码: {process.returncode}")
            if stderr:
                print(f"错误信息: {stderr[:500]}")
        else:
            print("✅ 语音对话系统已启动")
            if stdout:
                print(f"输出: {stdout[:1000]}")
                
    except subprocess.TimeoutExpired:
        # 如果程序继续运行（这是期望的）
        print("✅ 语音对话系统正在运行中...")
        print("💡 系统正在等待你的语音输入")
        print("🎤 请说'你好'开始对话")
        print("🗣️  说'退出'结束对话")
        return True
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)