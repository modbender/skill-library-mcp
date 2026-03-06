#!/usr/bin/env python3
"""
MiniMax TTS - 调用 MiniMax API 生成语音
"""

import os
import sys
import json
import argparse
import requests
import subprocess

API_BASE = "https://api.minimaxi.com"
DEFAULT_VOICE = "male-qn-qingse"
DEFAULT_MODEL = "speech-2.8-turbo"

def get_api_key():
    """获取 API Key"""
    key = os.environ.get("MINIMAX_API_KEY")
    if not key:
        print("Error: MINIMAX_API_KEY 环境变量未设置", file=sys.stderr)
        print("请运行: export MINIMAX_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)
    return key

def get_voice_list(api_key):
    """获取可用音色列表"""
    url = f"{API_BASE}/v1/get_voice"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {"voice_type": "all"}
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        print("可用音色列表：\n")
        
        if "system_voice" in result and result["system_voice"]:
            print("=== 系统音色 ===")
            for v in result["system_voice"]:
                print(f"  {v.get('voice_id')}: {v.get('voice_name')}")
        
        if "voice_cloning" in result and result["voice_cloning"]:
            print("\n=== 克隆音色 ===")
            for v in result["voice_cloning"]:
                print(f"  {v.get('voice_id')}")
        
        if "voice_generation" in result and result["voice_generation"]:
            print("\n=== 生成的音色 ===")
            for v in result["voice_generation"]:
                print(f"  {v.get('voice_id')}")
                
    except Exception as e:
        print(f"获取音色列表失败: {e}", file=sys.stderr)
        sys.exit(1)

def text_to_speech(text, api_key, model=DEFAULT_MODEL, voice=DEFAULT_VOICE, 
                   speed=1.0, format="mp3", output_file=None, pause=0):
    """调用 TTS API"""
    url = f"{API_BASE}/v1/t2a_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 处理停顿：在句子之间添加停顿标记
    if pause > 0:
        # 在句号、问号、感叹号后添加停顿
        import re
        text = re.sub(r'([。！？\.])([^<])', r'\1<#' + str(pause) + '#>\2', text)
    
    data = {
        "model": model,
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice,
            "speed": speed,
            "vol": 1,
            "pitch": 0
        },
        "audio_setting": {
            "format": format,
            "sample_rate": 32000,
            "bitrate": 128000,
            "channel": 1
        }
    }
    
    try:
        print(f"正在生成语音...", file=sys.stderr)
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("base_resp", {}).get("status_code") != 0:
            error_msg = result.get("base_resp", {}).get("status_msg", "未知错误")
            print(f"API 错误: {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        audio_data = result.get("data", {}).get("audio")
        if not audio_data:
            print("错误：未获取到音频数据", file=sys.stderr)
            sys.exit(1)
        
        # 解码 hex 音频数据
        audio_bytes = bytes.fromhex(audio_data)
        
        # 确定输出文件
        if not output_file:
            output_file = f"tts_output.{format}"
        
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        # 获取音频信息
        extra = result.get("extra_info", {})
        duration_ms = extra.get("audio_length", 0)
        duration_sec = duration_ms / 1000 if duration_ms else 0
        
        print(f"✅ 语音已保存到: {output_file}", file=sys.stderr)
        print(f"   时长: {duration_sec:.2f}秒", file=sys.stderr)
        print(f"   格式: {format}", file=sys.stderr)
        
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="MiniMax TTS 语音合成")
    parser.add_argument("text", nargs="?", help="要转语音的文本")
    parser.add_argument("--list-voices", "-l", action="store_true", help="列出所有可用音色")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"模型 (默认: {DEFAULT_MODEL})")
    parser.add_argument("--voice", "-v", default=DEFAULT_VOICE, help=f"音色ID (默认: {DEFAULT_VOICE})")
    parser.add_argument("--speed", "-s", type=float, default=1.0, help="语速 (默认: 1.0)")
    parser.add_argument("--pause", "-p", type=float, default=0, help="句间停顿秒数 (默认: 0, 如0.5)")
    parser.add_argument("--format", "-f", default="mp3", help="音频格式 (默认: mp3)")
    parser.add_argument("--output", "-o", help="输出文件路径")
    
    args = parser.parse_args()
    
    api_key = get_api_key()
    
    if args.list_voices:
        get_voice_list(api_key)
        return
    
    if not args.text:
        parser.print_help()
        print("\n示例:")
        print(f"  {sys.argv[0]} \"你好世界\"")
        print(f"  {sys.argv[0]} \"测试\" --voice Chinese_Female_Adult --output test.mp3")
        print(f"  {sys.argv[0]} -l  # 列出所有音色")
        sys.exit(1)
    
    output_file = text_to_speech(
        text=args.text,
        api_key=api_key,
        model=args.model,
        voice=args.voice,
        speed=args.speed,
        format=args.format,
        output_file=args.output,
        pause=args.pause
    )
    
    # 输出文件路径（供其他工具使用）
    print(output_file)

if __name__ == "__main__":
    main()
