#!/usr/bin/env python3
"""
PPT/PPTX压缩脚本
将大型PPT文件压缩并转换为PDF
"""

import os
import sys
import shutil
import subprocess
import tempfile
import zipfile

def get_file_size(path):
    """获取文件大小(字节)"""
    return os.path.getsize(path)

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"

def extract_pptx(pptx_path, extract_dir):
    """解压PPTX文件"""
    print(f"📂 正在解压PPT...")
    with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"✅ 解压完成")

def compress_images(media_dir):
    """压缩媒体目录中的大图片"""
    print(f"🖼️  正在压缩图片...")
    
    if not os.path.exists(media_dir):
        print(f"⚠️  媒体目录不存在")
        return
    
    # 获取所有图片文件
    image_extensions = ['.png', '.jpeg', '.jpg', '.gif']
    images = []
    for f in os.listdir(media_dir):
        ext = os.path.splitext(f)[1].lower()
        if ext in image_extensions:
            images.append(os.path.join(media_dir, f))
    
    compressed_count = 0
    for img_path in images:
        size = get_file_size(img_path)
        # 只压缩大于1MB的图片
        if size > 1000000:
            ext = os.path.splitext(img_path)[1].lower()
            try:
                if ext in ['.jpeg', '.jpg']:
                    subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '60', img_path, '--out', img_path], 
                                capture_output=True, timeout=30)
                elif ext == '.png':
                    subprocess.run(['sips', '-s', 'format', 'png', '-s', 'formatOptions', '60', img_path, '--out', img_path], 
                                capture_output=True, timeout=30)
                
                new_size = get_file_size(img_path)
                print(f"  压缩 {os.path.basename(img_path)}: {format_size(size)} → {format_size(new_size)}")
                compressed_count += 1
            except Exception as e:
                print(f"  ⚠️  压缩失败 {img_path}: {e}")
    
    print(f"✅ 压缩了 {compressed_count} 张图片")

def repack_pptx(extract_dir, output_path):
    """重新打包PPTX"""
    print(f"📦 正在重新打包PPT...")
    
    # 获取pptx目录下的所有文件
    # (保留用于未来扩展)
    
    # 创建新的zip文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(extract_dir):
            # 跳过__MACOSX目录
            if '__MACOSX' in root:
                continue
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, extract_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ 打包完成: {format_size(get_file_size(output_path))}")

def convert_to_pdf(pptx_path, output_dir):
    """使用LibreOffice转换为PDF"""
    print(f"📄 正在转换为PDF...")
    
    # 查找soffice
    soffice_paths = [
        '/opt/homebrew/bin/soffice',
        '/usr/local/bin/soffice',
        '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    ]
    
    soffice = None
    for path in soffice_paths:
        if os.path.exists(path):
            soffice = path
            break
    
    if not soffice:
        print(f"❌ 未找到LibreOffice，请先安装: brew install libreoffice")
        return None
    
    # 执行转换
    try:
        result = subprocess.run(
            [soffice, '--headless', '--convert-to', 'pdf', '--outdir', output_dir, pptx_path],
            capture_output=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"❌ 转换失败: {result.stderr.decode()}")
            return None
        
        # 获取输出的PDF文件名
        base_name = os.path.splitext(os.path.basename(pptx_path))[0]
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        
        if os.path.exists(pdf_path):
            print(f"✅ PDF转换完成: {format_size(get_file_size(pdf_path))}")
            return pdf_path
        else:
            # 尝试其他可能的名字
            for f in os.listdir(output_dir):
                if f.endswith('.pdf'):
                    pdf_path = os.path.join(output_dir, f)
                    print(f"✅ PDF转换完成: {format_size(get_file_size(pdf_path))}")
                    return pdf_path
            
            print(f"❌ 未找到生成的PDF文件")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"❌ 转换超时")
        return None
    except Exception as e:
        print(f"❌ 转换出错: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("用法: python3 compress.py <pptx文件路径> [输出目录]")
        sys.exit(1)
    
    pptx_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(pptx_path)
    
    # 检查输入文件
    if not os.path.exists(pptx_path):
        print(f"❌ 文件不存在: {pptx_path}")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print(f"PPT压缩工具")
    print(f"{'='*50}")
    print(f"输入文件: {pptx_path}")
    print(f"原始大小: {format_size(get_file_size(pptx_path))}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*50}\n")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extract')
        os.makedirs(extract_dir)
        
        # 步骤1: 解压
        extract_pptx(pptx_path, extract_dir)
        
        # 步骤2: 压缩图片
        media_dir = os.path.join(extract_dir, 'ppt', 'media')
        compress_images(media_dir)
        
        # 步骤3: 重新打包
        compressed_pptx = os.path.join(output_dir, 
            os.path.splitext(os.path.basename(pptx_path))[0] + '_压缩版.pptx')
        repack_pptx(extract_dir, compressed_pptx)
        
        # 步骤4: 转换为PDF
        pdf_path = convert_to_pdf(compressed_pptx, output_dir)
        
        print(f"\n{'='*50}")
        print(f"完成!")
        print(f"{'='*50}")
        
        if pdf_path:
            original_size = get_file_size(pptx_path)
            pdf_size = get_file_size(pdf_path)
            reduction = (1 - pdf_size / original_size) * 100
            print(f"原始大小: {format_size(original_size)}")
            print(f"PDF大小: {format_size(pdf_size)}")
            print(f"压缩率: {reduction:.1f}%")
            print(f"\n📄 PDF文件: {pdf_path}")
        
        # 清理临时PPTX
        if os.path.exists(compressed_pptx):
            try:
                os.remove(compressed_pptx)
                print(f"🗑️  已清理临时PPTX文件")
            except:
                pass

if __name__ == '__main__':
    main()
