#!/usr/bin/env python3
"""
图片处理工作流
用于处理用户发送的图片，通过视觉模型分析后返回文字描述
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from vision import VisionRecognizer


def process_user_image(image_path: str) -> str:
    """
    处理用户发送的图片
    
    Args:
        image_path: 图片路径
    
    Returns:
        图片内容描述
    """
    try:
        # 初始化视觉识别器
        vision = VisionRecognizer()
        
        # 分析图片
        result = vision.analyze_image(
            image_path,
            "详细描述这张图片的内容，包括所有可见的文字、按钮、布局、颜色等。"
        )
        
        if result.get('success'):
            return result.get('content', '')
        else:
            return f"图片分析失败：{result}"
    
    except Exception as e:
        return f"图片处理错误：{e}"


def extract_text_from_user_image(image_path: str) -> str:
    """
    从用户图片提取文字（OCR）
    
    Args:
        image_path: 图片路径
    
    Returns:
        提取的文字内容
    """
    try:
        vision = VisionRecognizer()
        result = vision.extract_text(image_path)
        
        if result.get('success'):
            return result.get('content', '')
        else:
            return f"OCR 失败：{result}"
    
    except Exception as e:
        return f"OCR 错误：{e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python process_image.py <图片路径>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"错误：文件不存在 {image_path}")
        sys.exit(1)
    
    print("正在分析图片...")
    description = process_user_image(image_path)
    print("\n图片内容：")
    print(description)
