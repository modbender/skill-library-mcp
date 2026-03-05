#!/usr/bin/env python3
"""
OpenClaw 飞书体验优化者 - 消息处理模块
Message Processing Module for OpenClaw Feishu Optimizer

作者: 黄绍帅（黄白）
版本: 1.0.0
"""

import json
import re
import argparse
import os
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("voice_recognize", "/root/.openclaw/workspace/skills/openclaw-feishu-optimizer/voice-recognize.py")
voice_recognize = importlib.util.module_from_spec(spec)
spec.loader.exec_module(voice_recognize)


def format_response(text, language="zh-CN"):
    """
    格式化回复文本，优化显示效果
    """
    if language == "zh-CN":
        text = text.strip()
        # 添加适当的标点符号
        if not text.endswith(('。', '！', '？', '.', '!', '?')):
            if text.endswith(('吗', '呢', '啊', '呀')):
                text += '？'
            elif text.endswith(('了', '的', '吧')):
                text += '。'
            else:
                text += '。'
        
        return text
    
    return text.strip()


def extract_media_info(message_data):
    """
    提取消息中的媒体信息
    """
    if isinstance(message_data, str):
        try:
            message_data = json.loads(message_data)
        except:
            message_data = {}
    
    media_info = {
        "has_voice": False,
        "voice_path": None,
        "duration": 0,
        "has_image": False,
        "image_path": None,
        "has_file": False,
        "file_path": None
    }
    
    return media_info


def process_voice_message(audio_path, language="zh-CN"):
    """
    处理语音消息
    """
    print("检测到语音消息")
    
    # 识别语音
    recognized_text = voice_recognize.recognize_speech(audio_path, language)
    
    if recognized_text:
        formatted_text = format_response(recognized_text, language)
        return {
            "success": True,
            "text": recognized_text,
            "formatted": formatted_text,
            "processed": True
        }
    else:
        return {
            "success": False,
            "text": "",
            "formatted": "抱歉，未能识别语音内容。",
            "processed": False
        }


def process_text_message(text, language="zh-CN"):
    """
    处理文字消息
    """
    print("检测到文字消息")
    
    formatted_text = format_response(text, language)
    return {
        "success": True,
        "text": text,
        "formatted": formatted_text,
        "processed": True
    }


def process_message(message_data, language="zh-CN"):
    """
    处理消息的主要函数
    """
    # 检查是否是语音消息（通过音频文件路径判断）
    if isinstance(message_data, str) and os.path.exists(message_data):
        file_ext = Path(message_data).suffix.lower()
        if file_ext in [".mp3", ".wav", ".flac", ".ogg", ".m4a", ".wma"]:
            return process_voice_message(message_data, language)
    
    # 处理文字消息
    return process_text_message(str(message_data), language)


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw 飞书体验优化者 - 消息处理模块",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 process-message.py "你好，世界！"
  python3 process-message.py /path/to/audio.mp3
  python3 process-message.py /path/to/audio.ogg --language zh-CN
  python3 process-message.py "{\"text\": \"你好\"}" --language en-US

支持的消息类型:
  - 文字消息（字符串）
  - 语音消息（音频文件路径）
  - JSON 格式的消息数据
        """)
    
    parser.add_argument("message_data", help="消息数据或音频文件路径")
    parser.add_argument(
        "--language", 
        "-l", 
        default="zh-CN",
        help="语言设置（默认: zh-CN）"
    )
    parser.add_argument(
        "--output", 
        "-o",
        help="将处理结果保存到指定文件"
    )
    
    args = parser.parse_args()
    
    # 处理消息
    result = process_message(args.message_data, args.language)
    
    # 输出结果
    print(f"\n原始内容: {result['text']}")
    print(f"格式化后: {result['formatted']}")
    print(f"处理状态: {'成功' if result['success'] else '失败'}")
    
    # 保存结果（如果需要）
    if args.output and result['success']:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")
    
    return result


if __name__ == "__main__":
    main()
