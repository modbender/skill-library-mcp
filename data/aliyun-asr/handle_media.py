#!/usr/bin/env python3
"""
OpenClaw媒体处理器入口
提供标准的handle_media函数接口
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

def handle_media(file_path: str) -> str:
    """
    OpenClaw标准媒体处理接口
    
    Args:
        file_path: 媒体文件路径
        
    Returns:
        处理后的文本内容
    """
    try:
        from aliyun_pure_asr import AliyunPureASR
        asr = AliyunPureASR()
        text = asr.speech_to_text(file_path)
        return text.strip() if text else ""
    except Exception as e:
        # 记录错误但不抛出异常
        # 返回空字符串让OpenClaw处理
        return ""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: handle_media.py <file_path>", file=sys.stderr)
        sys.exit(1)
    
    result = handle_media(sys.argv[1])
    print(result)