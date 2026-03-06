#!/usr/bin/env python3
"""
二维码生成技能使用示例
"""

import sys
import os

# 添加技能路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import handle_call

def example_text_qr():
    """示例1: 生成文本二维码"""
    print("📝 示例1: 生成文本二维码")
    result = handle_call({"content": "Hello OpenClaw! 欢迎使用二维码生成技能。"})
    print(f"结果: {result}")
    print()

def example_url_qr():
    """示例2: 生成链接二维码"""
    print("🔗 示例2: 生成链接二维码")
    result = handle_call({"content": "https://openclaw.ai"})
    print(f"结果: {result}")
    print()

def example_image_qr():
    """示例3: 生成图片二维码"""
    print("🖼️ 示例3: 生成图片二维码")
    
    # 创建一个测试图片
    from PIL import Image
    test_image_path = "/tmp/test_qr_image.jpg"
    
    # 生成一个简单的测试图片
    img = Image.new('RGB', (100, 100), color='red')
    img.save(test_image_path, 'JPEG')
    
    print(f"测试图片: {test_image_path}")
    result = handle_call({"image": test_image_path})
    print(f"结果: {result}")
    print()

def example_error():
    """示例4: 错误处理"""
    print("❌ 示例4: 错误处理")
    
    # 测试不存在的图片
    result = handle_call({"image": "/path/to/nonexistent/image.jpg"})
    print(f"不存在的图片: {result}")
    print()
    
    # 测试无参数
    result = handle_call({})
    print(f"无参数: {result}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("二维码生成技能示例程序")
    print("=" * 50)
    print()
    
    example_text_qr()
    example_url_qr()
    example_image_qr()
    example_error()
    
    print("=" * 50)
    print("✅ 所有示例完成")
    print("=" * 50)