#!/usr/bin/env python3
"""
阿里云纯ASR技能主入口
只提供语音识别功能，无TTS/OSS
"""

import sys
import os
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: main.py <audio_file>", file=sys.stderr)
        sys.exit(1)
    
    from handle_media import handle_media
    result = handle_media(sys.argv[1])
    print(result)