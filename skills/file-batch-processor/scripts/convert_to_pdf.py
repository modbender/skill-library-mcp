#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文件转PDF工具
支持图片、文本文件转PDF
"""

import os
import sys
import argparse
from PIL import Image
from fpdf import FPDF
import PyPDF2

def convert_to_pdf(folder_path, output_folder=None, dry_run=False):
    """
    批量转换文件为PDF
    
    Args:
        folder_path: 源文件夹路径
        output_folder: 输出文件夹路径（默认在原文件夹）
        dry_run: 是否只预览不执行
    """
    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在 {folder_path}")
        return False
    
    if output_folder is None:
        output_folder = folder_path
    
    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 支持的源文件格式
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    text_extensions = ['.txt', '.md']
    
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    convertible_files = [f for f in files if os.path.splitext(f)[1].lower() in image_extensions + text_extensions]
    
    if not convertible_files:
        print("警告：文件夹中没有找到可转换的文件")
        return True
    
    print(f"找到 {len(convertible_files)} 个可转换文件，准备转PDF...")
    
    converted_count = 0
    for filename in convertible_files:
        old_path = os.path.join(folder_path, filename)
        name, ext = os.path.splitext(filename)
        
        # 生成PDF文件名
        pdf_filename = f"{name}.pdf"
        pdf_path = os.path.join(output_folder, pdf_filename)
        
        try:
            if dry_run:
                print(f"预览: {filename} → {pdf_filename}")
            else:
                if ext.lower() in image_extensions:
                    # 图片转PDF
                    with Image.open(old_path) as img:
                        # 创建PDF
                        pdf = FPDF()
                        pdf.add_page()
                        
                        # 计算合适的尺寸
                        width, height = img.size
                        max_width = 200  # mm
                        max_height = 280  # mm
                        
                        if width > height:
                            new_width = max_width
                            new_height = height * (max_width / width)
                        else:
                            new_height = max_height
                            new_width = width * (max_height / height)
                        
                        # 调整图片大小并保存到PDF
                        img.save('temp_image.jpg', quality=95)
                        pdf.image('temp_image.jpg', x=(210-new_width)/2, y=(297-new_height)/2, 
                                 w=new_width, h=new_height)
                        pdf.output(pdf_path)
                        os.remove('temp_image.jpg')
                        
                elif ext.lower() in text_extensions:
                    # 文本转PDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    
                    # 读取文本文件
                    with open(old_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 添加文本到PDF
                    for line in lines:
                        pdf.cell(200, 10, txt=line.rstrip(), ln=True)
                    
                    pdf.output(pdf_path)
                
                print(f"已转换: {filename} → {pdf_filename}")
                converted_count += 1
                
        except Exception as e:
            print(f"转换失败 {filename}: {e}")
    
    print(f"完成！共转换 {converted_count} 个文件为PDF")
    return True

def main():
    parser = argparse.ArgumentParser(description='批量文件转PDF工具')
    parser.add_argument('folder', help='要处理的文件夹路径')
    parser.add_argument('--output', help='输出文件夹路径（默认同源文件夹）')
    parser.add_argument('--dry-run', action='store_true', help='只预览不执行')
    
    args = parser.parse_args()
    
    convert_to_pdf(
        folder_path=args.folder,
        output_folder=args.output,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()