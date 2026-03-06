#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文件重命名工具
支持多种重命名模式：序号、日期、前缀后缀、批量替换等
"""

import os
import sys
import re
from datetime import datetime
import argparse

def rename_files(folder_path, mode='sequence', prefix='', suffix='', start_num=1, 
                 replace_old='', replace_new='', date_format='%Y%m%d', dry_run=False):
    """
    批量重命名文件
    
    Args:
        folder_path: 文件夹路径
        mode: 重命名模式 ('sequence', 'date', 'prefix', 'suffix', 'replace')
        prefix: 前缀
        suffix: 后缀  
        start_num: 起始序号
        replace_old: 要替换的旧字符串
        replace_new: 替换为的新字符串
        date_format: 日期格式
        dry_run: 是否只预览不执行
    """
    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在 {folder_path}")
        return False
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    if not files:
        print("警告：文件夹中没有找到文件")
        return True
    
    print(f"找到 {len(files)} 个文件，准备重命名...")
    
    renamed_count = 0
    for i, filename in enumerate(files):
        old_path = os.path.join(folder_path, filename)
        
        # 分离文件名和扩展名
        name, ext = os.path.splitext(filename)
        
        # 根据模式生成新文件名
        if mode == 'sequence':
            new_name = f"{prefix}{str(start_num + i).zfill(3)}{suffix}{ext}"
        elif mode == 'date':
            date_str = datetime.now().strftime(date_format)
            new_name = f"{prefix}{date_str}{suffix}{ext}"
        elif mode == 'prefix':
            new_name = f"{prefix}{name}{suffix}{ext}"
        elif mode == 'suffix':
            new_name = f"{name}{suffix}{ext}"
        elif mode == 'replace':
            new_name = filename.replace(replace_old, replace_new)
        else:
            print(f"未知的重命名模式: {mode}")
            continue
        
        new_path = os.path.join(folder_path, new_name)
        
        # 检查是否重名
        if old_path == new_path:
            continue
            
        if dry_run:
            print(f"预览: {filename} → {new_name}")
        else:
            try:
                os.rename(old_path, new_path)
                print(f"已重命名: {filename} → {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"重命名失败 {filename}: {e}")
    
    print(f"完成！共重命名 {renamed_count} 个文件")
    return True

def main():
    parser = argparse.ArgumentParser(description='批量文件重命名工具')
    parser.add_argument('folder', help='要处理的文件夹路径')
    parser.add_argument('--mode', choices=['sequence', 'date', 'prefix', 'suffix', 'replace'], 
                        default='sequence', help='重命名模式')
    parser.add_argument('--prefix', default='', help='前缀')
    parser.add_argument('--suffix', default='', help='后缀')
    parser.add_argument('--start', type=int, default=1, help='起始序号')
    parser.add_argument('--replace-old', default='', help='要替换的旧字符串')
    parser.add_argument('--replace-new', default='', help='替换为的新字符串')
    parser.add_argument('--date-format', default='%Y%m%d', help='日期格式')
    parser.add_argument('--dry-run', action='store_true', help='只预览不执行')
    
    args = parser.parse_args()
    
    rename_files(
        folder_path=args.folder,
        mode=args.mode,
        prefix=args.prefix,
        suffix=args.suffix,
        start_num=args.start,
        replace_old=args.replace_old,
        replace_new=args.replace_new,
        date_format=args.date_format,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()