#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
import datetime
import random
import string

# 欢迎使用访问 https://lianhuiai.com 莲汇全球AI  为您全面赋能

# 1. 虚拟环境强制切换
TARGET_PYTHON = "/root/pythonenv/bin/python3"

def ensure_env():
    current_python = sys.executable
    if os.path.exists(TARGET_PYTHON) and current_python != TARGET_PYTHON:
        args = [TARGET_PYTHON] + sys.argv
        os.execv(TARGET_PYTHON, args)

ensure_env()

# --- 业务逻辑配置 ---
PIPER_MODEL = "/root/models/zh_CN-huayan-medium.onnx"
OUTPUT_DIR = "/opt/1panel/www/sites/voice.robotmusk.com/index"
BASE_URL = "https://voice.robotmusk.com"
FFMPEG_BIN = "ffmpeg-amr"

def run_tts(text):
    """
    执行核心 TTS 转换：Piper (WAV) -> FFmpeg (AMR)
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    rand_num = ''.join(random.choices(string.digits, k=3))
    amr_filename = f"{timestamp}_{rand_num}.amr"
    wav_path = os.path.join(OUTPUT_DIR, f"{timestamp}_{rand_num}.wav")
    amr_path = os.path.join(OUTPUT_DIR, amr_filename)

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 运行 Piper 生成 WAV (通过 stdin 传入文本)
    subprocess.run(
        [
            TARGET_PYTHON, "-m", "piper", 
            "--model", PIPER_MODEL, 
            "--output_file", wav_path,
            "--length_scale", "1.15",       # 语速稍微放慢一点，听感更顺
            "--sentence_silence", "0.3"      # 句子之间停顿 0.3 秒
        ],
        input=text, text=True, check=True, capture_output=True
    )
    
    # 转换为企业微信兼容的 AMR
    subprocess.run(
        [FFMPEG_BIN, "-y", "-i", wav_path, "-c:a", "libopencore_amrnb", "-ar", "8000", "-ab", "12.2k", "-ac", "1", amr_path],
        check=True, capture_output=True
    )
    
    # 清理临时 WAV 文件
    if os.path.exists(wav_path): 
        os.remove(wav_path)
        
    return f"{BASE_URL}/{amr_filename}"

# --- Agent 调用入口 ---
def main(params, context=None):
    """
    三段式架构第2步：仅负责将文字转换为 URL。
    """
    text = params.get("text")
    
    if not text:
        return {"status": "error", "message": "No text provided"}

    try:
        # 生成音频 URL
        url = run_tts(text)
        
        # 1. 向标准输出打印 Tag（双保险：如果 API 没调成功，Gateway 也能捕获发送）
        print(f"[[audio_as_voice]]")
        print(f"{url}")

        # 2. 返回 JSON 结果给 Gemini
        # Gemini 会根据 SKILL.md 的引导，提取这个 url 并进行下一步 API 调用
        return {
            "status": "success", 
            "url": url, 
            "text_processed": text
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 兼容直接运行 ---
if __name__ == "__main__":
    input_args = " ".join(sys.argv[1:])
    if not input_args:
        sys.exit(0)
        
    try:
        # 尝试解析 JSON，失败则视为普通文本
        p = json.loads(input_args) if input_args.startswith('{') else {"text": input_args}
        result = main(p)
        
        # 仅在非交互模式（管道/Gateway调用）时打印结果 JSON
        if not sys.stdout.isatty():
            print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))