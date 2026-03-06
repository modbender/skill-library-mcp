#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动文件分类整理工具
按文件类型自动归类到不同文件夹
"""

import os
import shutil
import sys
import argparse
from pathlib import Path

def organize_files(folder_path, dry_run=False):
    """
    自动分类整理文件
    
    Args:
        folder_path: 文件夹路径
        dry_run: 是否只预览不执行
    """
    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在 {folder_path}")
        return False
    
    # 分类规则
    categories = {
        '文档': ['.doc', '.docx', '.pdf', '.txt', '.md', '.rtf'],
        '图片': ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'],
        '音频': ['.mp3', '.wav', '.aac', '.ogg', '.m4a'],
        '视频': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
        '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        '其他': []
    }
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    if not files:
        print("警告：文件夹中没有找到文件")
        return True
    
    print(f"找到 {len(files)} 个文件，准备分类整理...")
    
    # 创建分类文件夹
    for category in categories.keys():
        category_folder = os.path.join(folder_path, category)
        if not os.path.exists(category_folder):
            if not dry_run:
                os.makedirs(category_folder)
            print(f"创建文件夹: {category}")
    
    organized_count = 0
    for filename in files:
        old_path = os.path.join(folder_path, filename)
        name, ext = os.path.splitext(filename)
        
        # 确定文件类别
        category = '其他'
        for cat, extensions in categories.items():
            if ext.lower() in extensions:
                category = cat
                break
        
        # 目标路径
        new_path = os.path.join(folder_path, category, filename)
        
        try:
            if dry_run:
                print(f"预览: {filename} → {category}/")
            else:
                # 移动文件
                shutil.move(old_path, new_path)
                print(f"已整理: {filename} → {category}/")
                organized_count += 1
                
        except Exception as e:
            print(f"整理失败 {filename}: {e}")
    
    print(f"完成！共整理 {organized_count} 个文件")
    return True

def main():
    parser = argparse.ArgumentParser(description='自动文件分类整理工具')
    parser.add_argument('folder', help='要处理的文件夹路径')
    parser.add_argument('--dry-run', action='store_true', help='只预览不执行')
    
    args = parser.parse_args()
    
    organize_files(
        folder_path=args.folder,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()