#!/usr/bin/env python3
"""
Whisper 语音转文字工具
依赖: openai-whisper, ffmpeg
安装: pip3 install openai-whisper && brew install ffmpeg
"""

import whisper
import argparse
import os
import sys
from pathlib import Path


def load_model(model_name: str = "base"):
    """加载Whisper模型"""
    print(f"加载模型: {model_name}...")
    model = whisper.load_model(model_name)
    print("模型加载完成!")
    return model


def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """
    识别语音并返回文字
    
    Args:
        audio_path: 音频文件路径
        model_name: 模型名称
    
    Returns:
        识别的文字
    """
    audio_path = Path(audio_path)
    
    if not audio_path.exists():
        raise FileNotFoundError(f"文件不存在: {audio_path}")
    
    # 加载模型
    model = load_model(model_name)
    
    # 识别
    print(f"正在识别: {audio_path.name}")
    result = model.transcribe(str(audio_path), language="zh")
    
    text = result["text"].strip()
    return text


def main():
    parser = argparse.ArgumentParser(description="Whisper语音转文字")
    parser.add_argument("--input", "-i", required=True, help="输入音频文件")
    parser.add_argument("--model", "-m", default="base", 
                       choices=["tiny", "base", "small", "medium", "large", "turbo"],
                       help="模型大小 (默认: base)")
    parser.add_argument("--output", "-o", help="输出文件 (可选)")
    
    args = parser.parse_args()
    
    try:
        text = transcribe_audio(args.input, args.model)
        
        print("\n" + "="*50)
        print("识别结果:")
        print("="*50)
        print(text)
        print("="*50)
        
        # 保存到文件
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"\n已保存到: {args.output}")
        
        return text
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Author Identity
__author_identity__ = "yanyan@3c3d77679723a2fe95d3faf9d2c2e5a65559acbc97fef1ef37783514a80ae453"
