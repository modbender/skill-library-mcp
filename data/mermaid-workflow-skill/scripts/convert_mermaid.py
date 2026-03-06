#!/usr/bin/env python3
"""
将Mermaid图表定义文件(.mmd)转换为PNG图片
使用mmdc (Mermaid CLI)进行转换
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import tempfile
import json

def check_mmdc_installed():
    """检查mmdc是否安装"""
    try:
        result = subprocess.run(['mmdc', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Mermaid CLI已安装: {version}")
            return True
        else:
            print("❌ Mermaid CLI未正确安装")
            return False
    except FileNotFoundError:
        print("❌ Mermaid CLI未安装")
        print("请安装: npm install -g @mermaid-js/mermaid-cli")
        return False

def create_puppeteer_config(config_path):
    """创建Puppeteer配置文件解决沙箱问题"""
    config = {
        "args": ["--no-sandbox", "--disable-setuid-sandbox"]
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Puppeteer配置文件已创建: {config_path}")
    return config_path

def convert_mermaid_to_png(input_file, output_file, width=1200, height=800, 
                          theme='default', background='white', puppeteer_config=None):
    """
    将Mermaid文件转换为PNG图片
    """
    if not Path(input_file).exists():
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 构建mmdc命令
    cmd = [
        'mmdc',
        '-i', str(input_file),
        '-o', str(output_file),
        '-w', str(width),
        '-H', str(height),
        '-b', background
    ]
    
    # 添加主题
    if theme != 'default':
        cmd.extend(['-t', theme])
    
    # 添加Puppeteer配置
    if puppeteer_config:
        cmd.extend(['-p', str(puppeteer_config)])
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Mermaid图表已转换为PNG: {output_file}")
            
            # 检查文件大小
            if output_path.exists():
                file_size = output_path.stat().st_size / 1024  # KB
                print(f"   文件大小: {file_size:.1f} KB")
                print(f"   尺寸: {width}×{height} 像素")
                return True
            else:
                print("❌ 转换成功但输出文件未创建")
                return False
        else:
            print(f"❌ Mermaid转换失败 (退出码: {result.returncode})")
            print(f"错误输出: {result.stderr}")
            
            # 尝试使用npx
            print("尝试使用npx...")
            cmd[0] = 'npx'
            cmd.insert(1, '@mermaid-js/mermaid-cli')
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ 使用npx转换成功: {output_file}")
                return True
            else:
                print(f"❌ npx转换也失败: {result.stderr}")
                return False
                
    except subprocess.TimeoutExpired:
        print("❌ 转换超时 (30秒)")
        return False
    except Exception as e:
        print(f"❌ 转换过程中发生错误: {e}")
        return False

def batch_convert_mermaid_files(input_dir, output_dir, **kwargs):
    """
    批量转换Mermaid文件
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return False
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有.mmd文件
    mmd_files = list(input_dir.glob("*.mmd"))
    
    if not mmd_files:
        print(f"❌ 在 {input_dir} 中没有找到.mmd文件")
        return False
    
    print(f"找到 {len(mmd_files)} 个Mermaid文件")
    print("=" * 60)
    
    success_count = 0
    
    for mmd_file in mmd_files:
        output_file = output_dir / f"{mmd_file.stem}.png"
        
        print(f"正在转换: {mmd_file.name}")
        
        if convert_mermaid_to_png(mmd_file, output_file, **kwargs):
            success_count += 1
        
        print("-" * 40)
    
    print(f"\n转换完成: {success_count}/{len(mmd_files)} 个文件转换成功")
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description='将Mermaid图表转换为PNG图片')
    parser.add_argument('--input', required=True, help='输入.mmd文件或目录')
    parser.add_argument('--output', help='输出.png文件（批量模式时为目录）')
    parser.add_argument('--width', type=int, default=1200, help='图片宽度（默认1200）')
    parser.add_argument('--height', type=int, default=800, help='图片高度（默认800）')
    parser.add_argument('--theme', default='default', 
                       choices=['default', 'forest', 'dark', 'neutral'],
                       help='图表主题（默认default）')
    parser.add_argument('--background', default='white', help='背景颜色（默认白色）')
    parser.add_argument('--puppeteer-config', help='Puppeteer配置文件路径')
    parser.add_argument('--batch', action='store_true', help='批量模式（转换目录中的所有.mmd文件）')
    parser.add_argument('--create-config', action='store_true', help='创建Puppeteer配置文件')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Mermaid图表转换工具")
    print("=" * 60)
    
    # 检查mmdc是否安装
    if not check_mmdc_installed():
        sys.exit(1)
    
    # 创建Puppeteer配置文件（如果需要）
    puppeteer_config = args.puppeteer_config
    if args.create_config and not puppeteer_config:
        config_path = Path.home() / '.mermaid-puppeteer-config.json'
        puppeteer_config = create_puppeteer_config(config_path)
    
    # 批量模式
    if args.batch:
        input_path = Path(args.input)
        
        if input_path.is_file():
            print("❌ 批量模式需要目录作为输入")
            sys.exit(1)
        
        output_dir = args.output if args.output else input_path / "png_output"
        
        success = batch_convert_mermaid_files(
            input_path, output_dir,
            width=args.width,
            height=args.height,
            theme=args.theme,
            background=args.background,
            puppeteer_config=puppeteer_config
        )
        
        if success:
            print(f"\n✅ 批量转换完成！")
            print(f"输出目录: {output_dir}")
        else:
            print("\n❌ 批量转换失败")
            sys.exit(1)
    
    # 单文件模式
    else:
        input_path = Path(args.input)
        
        if not input_path.exists():
            print(f"❌ 输入文件不存在: {input_path}")
            sys.exit(1)
        
        if input_path.is_dir():
            print("❌ 单文件模式需要文件作为输入，使用 --batch 进行批量转换")
            sys.exit(1)
        
        # 确定输出文件路径
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix('.png')
        
        success = convert_mermaid_to_png(
            input_path, output_path,
            width=args.width,
            height=args.height,
            theme=args.theme,
            background=args.background,
            puppeteer_config=puppeteer_config
        )
        
        if success:
            print(f"\n✅ 转换完成！")
            print(f"输出文件: {output_path}")
        else:
            print("\n❌ 转换失败")
            sys.exit(1)

if __name__ == "__main__":
    main()