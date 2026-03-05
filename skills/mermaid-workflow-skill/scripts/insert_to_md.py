#!/usr/bin/env python3
"""
将PNG图片插入到Markdown文件
支持替换占位符或在指定位置插入
"""

import os
import sys
import argparse
import re
from pathlib import Path
import shutil

def insert_image_to_markdown(md_file, image_file, placeholder=None, section=None, 
                           caption=None, position='after', relative_path=True):
    """
    将图片插入到Markdown文件
    """
    if not Path(md_file).exists():
        print(f"❌ Markdown文件不存在: {md_file}")
        return False
    
    if not Path(image_file).exists():
        print(f"❌ 图片文件不存在: {image_file}")
        return False
    
    # 读取Markdown内容
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 计算相对路径
    if relative_path:
        md_path = Path(md_file).parent
        img_path = Path(image_file)
        
        try:
            # 计算相对路径
            rel_path = os.path.relpath(img_path, md_path)
            image_ref = rel_path
        except ValueError:
            # 如果无法计算相对路径，使用绝对路径
            image_ref = str(img_path)
            print(f"⚠️ 使用绝对路径: {image_ref}")
    else:
        image_ref = str(Path(image_file).name)
    
    # 构建图片Markdown语法
    if caption:
        image_markdown = f'![{caption}]({image_ref})'
    else:
        # 使用文件名作为默认标题
        caption_text = Path(image_file).stem.replace('_', ' ').replace('-', ' ')
        image_markdown = f'![{caption_text}]({image_ref})'
    
    # 添加图片说明
    if caption:
        image_markdown += f'\n\n*图: {caption}*'
    
    new_content = content
    
    # 情况1: 替换占位符
    if placeholder:
        if placeholder in content:
            new_content = content.replace(placeholder, image_markdown)
            print(f"✅ 已替换占位符: {placeholder}")
        else:
            print(f"⚠️ 占位符未找到: {placeholder}")
            print("将在文件末尾插入图片")
            new_content = content + f'\n\n{image_markdown}'
    
    # 情况2: 插入到指定章节
    elif section:
        # 查找章节
        lines = content.split('\n')
        section_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith(section):
                section_index = i
                break
        
        if section_index >= 0:
            if position == 'before':
                # 插入到章节前
                lines.insert(section_index, '')
                lines.insert(section_index, image_markdown)
                new_content = '\n'.join(lines)
                print(f"✅ 已插入图片到章节前: {section}")
            elif position == 'after':
                # 插入到章节后
                # 找到章节结束位置（下一个同级或更高级标题）
                insert_index = section_index + 1
                while insert_index < len(lines):
                    line = lines[insert_index]
                    if line.strip() and line.strip()[0] == '#':
                        # 找到下一个标题，停止
                        break
                    insert_index += 1
                
                lines.insert(insert_index, '')
                lines.insert(insert_index, image_markdown)
                new_content = '\n'.join(lines)
                print(f"✅ 已插入图片到章节后: {section}")
            else:  # replace
                # 替换章节内容
                # 找到章节内容范围
                start_index = section_index + 1
                end_index = start_index
                while end_index < len(lines):
                    line = lines[end_index]
                    if line.strip() and line.strip()[0] == '#':
                        # 找到下一个标题，停止
                        break
                    end_index += 1
                
                # 替换章节内容
                new_lines = lines[:start_index] + ['', image_markdown, ''] + lines[end_index:]
                new_content = '\n'.join(new_lines)
                print(f"✅ 已替换章节内容: {section}")
        else:
            print(f"⚠️ 章节未找到: {section}")
            print("将在文件末尾插入图片")
            new_content = content + f'\n\n{image_markdown}'
    
    # 情况3: 插入到文件末尾
    else:
        new_content = content + f'\n\n{image_markdown}'
        print("✅ 已插入图片到文件末尾")
    
    # 写入文件
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ 图片已插入到: {md_file}")
    print(f"   图片引用: {image_ref}")
    if caption:
        print(f"   图片标题: {caption}")
    
    return True

def batch_insert_images(md_file, image_dir, pattern=None, placeholder_prefix='[IMAGE_'):
    """
    批量插入图片到Markdown文件
    """
    if not Path(md_file).exists():
        print(f"❌ Markdown文件不存在: {md_file}")
        return False
    
    if not Path(image_dir).exists():
        print(f"❌ 图片目录不存在: {image_dir}")
        return False
    
    # 查找图片文件
    if pattern:
        image_files = list(Path(image_dir).glob(pattern))
    else:
        image_files = list(Path(image_dir).glob("*.png")) + \
                     list(Path(image_dir).glob("*.jpg")) + \
                     list(Path(image_dir).glob("*.jpeg"))
    
    if not image_files:
        print(f"❌ 在 {image_dir} 中没有找到图片文件")
        return False
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 读取Markdown内容
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有占位符
    placeholders = re.findall(rf'{re.escape(placeholder_prefix)}[^\]]+\]', content)
    
    if not placeholders:
        print(f"❌ 未找到占位符（前缀: {placeholder_prefix}）")
        return False
    
    print(f"找到 {len(placeholders)} 个占位符")
    
    # 按数字排序占位符
    def extract_number(ph):
        match = re.search(r'(\d+)', ph)
        return int(match.group(1)) if match else 0
    
    sorted_placeholders = sorted(placeholders, key=extract_number)
    
    # 按数字排序图片文件
    def extract_image_number(img_path):
        match = re.search(r'(\d+)', img_path.stem)
        return int(match.group(1)) if match else 0
    
    sorted_images = sorted(image_files, key=extract_image_number)
    
    # 确保数量匹配
    if len(sorted_placeholders) != len(sorted_images):
        print(f"⚠️ 占位符数量({len(sorted_placeholders)})与图片数量({len(sorted_images)})不匹配")
        min_count = min(len(sorted_placeholders), len(sorted_images))
        sorted_placeholders = sorted_placeholders[:min_count]
        sorted_images = sorted_images[:min_count]
        print(f"   将处理前 {min_count} 个")
    
    # 替换占位符
    new_content = content
    success_count = 0
    
    for i, (placeholder, image_file) in enumerate(zip(sorted_placeholders, sorted_images), 1):
        # 计算相对路径
        md_path = Path(md_file).parent
        rel_path = os.path.relpath(image_file, md_path)
        
        # 构建图片Markdown语法
        caption = image_file.stem.replace('_', ' ').replace('-', ' ')
        image_markdown = f'![{caption}]({rel_path})'
        
        # 替换占位符
        if placeholder in new_content:
            new_content = new_content.replace(placeholder, image_markdown)
            print(f"  ✅ 替换 {placeholder} → {image_file.name}")
            success_count += 1
        else:
            print(f"  ⚠️ 占位符未找到: {placeholder}")
    
    # 写入文件
    if success_count > 0:
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n✅ 批量插入完成: {success_count}/{len(sorted_placeholders)} 个图片已插入")
        return True
    else:
        print("\n❌ 批量插入失败: 未插入任何图片")
        return False

def copy_image_to_md_directory(md_file, image_file):
    """
    将图片复制到Markdown文件所在目录
    """
    md_dir = Path(md_file).parent
    image_name = Path(image_file).name
    dest_path = md_dir / image_name
    
    try:
        shutil.copy2(image_file, dest_path)
        print(f"✅ 图片已复制到: {dest_path}")
        return str(dest_path)
    except Exception as e:
        print(f"❌ 复制图片失败: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='将PNG图片插入到Markdown文件')
    parser.add_argument('--md-file', required=True, help='Markdown文件路径')
    parser.add_argument('--image', help='图片文件路径（单文件模式）')
    parser.add_argument('--image-dir', help='图片目录路径（批量模式）')
    parser.add_argument('--placeholder', help='要替换的占位符（如 [IMAGE_1]）')
    parser.add_argument('--section', help='要插入的章节标题（如 ## 技术路线图）')
    parser.add_argument('--caption', help='图片标题')
    parser.add_argument('--position', choices=['before', 'after', 'replace'], 
                       default='after', help='插入位置（默认after）')
    parser.add_argument('--relative-path', action='store_true', default=True,
                       help='使用相对路径（默认）')
    parser.add_argument('--absolute-path', action='store_false', dest='relative_path',
                       help='使用绝对路径')
    parser.add_argument('--copy-image', action='store_true',
                       help='将图片复制到Markdown文件所在目录')
    parser.add_argument('--batch', action='store_true', help='批量模式')
    parser.add_argument('--pattern', help='图片文件模式（如 *.png）')
    parser.add_argument('--placeholder-prefix', default='[IMAGE_',
                       help='占位符前缀（默认[IMAGE_）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Markdown图片插入工具")
    print("=" * 60)
    
    # 检查Markdown文件
    if not Path(args.md_file).exists():
        print(f"❌ Markdown文件不存在: {args.md_file}")
        sys.exit(1)
    
    # 批量模式
    if args.batch:
        if not args.image_dir:
            print("❌ 批量模式需要 --image-dir 参数")
            sys.exit(1)
        
        success = batch_insert_images(
            args.md_file, args.image_dir,
            pattern=args.pattern,
            placeholder_prefix=args.placeholder_prefix
        )
        
        if success:
            print(f"\n✅ 批量插入完成！")
            print(f"Markdown文件: {args.md_file}")
        else:
            print("\n❌ 批量插入失败")
            sys.exit(1)
    
    # 单文件模式
    else:
        if not args.image:
            print("❌ 单文件模式需要 --image 参数")
            sys.exit(1)
        
        # 复制图片（如果需要）
        image_path = args.image
        if args.copy_image:
            new_path = copy_image_to_md_directory(args.md_file, args.image)
            if new_path:
                image_path = new_path
            else:
                print("⚠️ 图片复制失败，使用原始路径")
        
        success = insert_image_to_markdown(
            args.md_file, image_path,
            placeholder=args.placeholder,
            section=args.section,
            caption=args.caption,
            position=args.position,
            relative_path=args.relative_path
        )
        
        if success:
            print(f"\n✅ 插入完成！")
            print(f"Markdown文件: {args.md_file}")
            print(f"图片文件: {image_path}")
        else:
            print("\n❌ 插入失败")
            sys.exit(1)

if __name__ == "__main__":
    main()