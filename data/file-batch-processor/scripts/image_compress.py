#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量图片压缩工具
支持JPEG和PNG格式，可调整质量、尺寸
"""

from PIL import Image
import os
import sys
import argparse
from pathlib import Path

def compress_images(folder_path, quality=70, resize_ratio=1.0, dry_run=False):
    """
    批量压缩图片
    
    Args:
        folder_path: 文件夹路径
        quality: 压缩质量 (1-100)
        resize_ratio: 尺寸缩放比例 (0.1-1.0)
        dry_run: 是否只预览不执行
    """
    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在 {folder_path}")
        return False
    
    # 支持的图片格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    image_files = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions]
    
    if not image_files:
        print("警告：文件夹中没有找到图片文件")
        return True
    
    print(f"找到 {len(image_files)} 个图片文件，准备压缩...")
    
    compressed_count = 0
    for filename in image_files:
        old_path = os.path.join(folder_path, filename)
        name, ext = os.path.splitext(filename)
        
        # 创建备份文件名
        backup_name = f"{name}_backup{ext}"
        backup_path = os.path.join(folder_path, backup_name)
        
        try:
            # 打开图片
            with Image.open(old_path) as img:
                # 记录原始信息
                original_size = os.path.getsize(old_path)
                original_width, original_height = img.size
                
                # 调整尺寸
                if resize_ratio < 1.0:
                    new_width = int(original_width * resize_ratio)
                    new_height = int(original_height * resize_ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存压缩后的图片
                if dry_run:
                    print(f"预览: {filename} ({original_width}x{original_height}) → 质量{quality}%, 尺寸{resize_ratio*100}%")
                else:
                    # 保存为JPEG（保持原格式）
                    if ext.lower() in ['.jpg', '.jpeg']:
                        img.save(old_path, 'JPEG', quality=quality, optimize=True, progressive=True)
                    else:
                        img.save(old_path, 'PNG', optimize=True, compress_level=6)
                    
                    # 计算压缩效果
                    new_size = os.path.getsize(old_path)
                    compression_rate = (original_size - new_size) / original_size * 100
                    
                    print(f"已压缩: {filename} ({original_size/1024:.1f}KB → {new_size/1024:.1f}KB, {compression_rate:.1f}%)")
                    compressed_count += 1
                    
        except Exception as e:
            print(f"压缩失败 {filename}: {e}")
    
    print(f"完成！共压缩 {compressed_count} 个图片文件")
    return True

def main():
    parser = argparse.ArgumentParser(description='批量图片压缩工具')
    parser.add_argument('folder', help='要处理的文件夹路径')
    parser.add_argument('--quality', type=int, default=70, choices=range(1, 101),
                        help='压缩质量 (1-100)')
    parser.add_argument('--resize', type=float, default=1.0, choices=[round(x*0.1,1) for x in range(1, 11)],
                        help='尺寸缩放比例 (0.1-1.0)')
    parser.add_argument('--dry-run', action='store_true', help='只预览不执行')
    
    args = parser.parse_args()
    
    compress_images(
        folder_path=args.folder,
        quality=args.quality,
        resize_ratio=args.resize,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()