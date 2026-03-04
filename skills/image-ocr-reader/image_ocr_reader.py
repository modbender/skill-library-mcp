#!/usr/bin/env python3
"""
Image OCR Reader - 从图片中提取文字
支持中文和英文识别

使用方法:
    python3 image_ocr_reader.py --file /path/to/image.jpg
    python3 image_ocr_reader.py --file /path/to/image.jpg --lang chi_sim+eng
"""

import argparse
import os
import sys
import json
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except ImportError:
    print("Error: 请先安装依赖")
    print("pip install pytesseract Pillow")
    sys.exit(1)


def extract_text(image_path, lang='chi_sim+eng'):
    """
    从图片中提取文字
    
    Args:
        image_path: 图片文件路径
        lang: 语言代码，默认中文简体+英文
    
    Returns:
        提取的文字内容
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 如果是RGBA模式，转换为RGB
        if img.mode == 'RGBA':
            # 创建一个白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            # 合并图层
            background.paste(img, mask=img.split()[3])
            img = background
        
        # 使用Tesseract OCR提取文字
        text = pytesseract.image_to_string(img, lang=lang)
        
        return text.strip()
    
    except Exception as e:
        raise Exception(f"OCR识别失败: {str(e)}")


def extract_text_detailed(image_path, lang='chi_sim+eng'):
    """
    从图片中提取文字（详细模式，返回位置信息）
    
    Args:
        image_path: 图片文件路径
        lang: 语言代码
    
    Returns:
        包含位置信息的文字列表
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    img = Image.open(image_path)
    
    # 获取详细识别结果
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
    
    results = []
    n_boxes = len(data['text'])
    
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if text:  # 只返回非空文本
            results.append({
                'text': text,
                'conf': data['conf'][i],
                'left': data['left'][i],
                'top': data['top'][i],
                'width': data['width'][i],
                'height': data['height'][i]
            })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='从图片中提取文字 (OCR)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 image_ocr_reader.py --file photo.jpg
    python3 image_ocr_reader.py --file image.png --lang eng
    python3 image_ocr_reader.py --file screenshot.jpg --output result.txt
        """
    )
    
    parser.add_argument('--file', '-f', required=True, help='图片文件路径')
    parser.add_argument('--lang', '-l', default='chi_sim+eng', 
                        help='语言代码: chi_sim(中文简体), eng(英文), 组合用+分隔')
    parser.add_argument('--output', '-o', help='输出文件路径 (可选)')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')
    parser.add_argument('--detailed', '-d', action='store_true', help='详细模式(包含位置信息)')
    
    args = parser.parse_args()
    
    try:
        # 提取文字
        if args.detailed:
            results = extract_text_detailed(args.file, args.lang)
            if args.json:
                print(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                for item in results:
                    print(f"[{item['conf']:>5.1f}%] {item['text']}")
        else:
            text = extract_text(args.file, args.lang)
            
            if args.json:
                result = {
                    'file': args.file,
                    'text': text,
                    'lang': args.lang
                }
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(text)
        
        # 保存到文件
        if args.output and not args.detailed:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n已保存到: {args.output}", file=sys.stderr)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
