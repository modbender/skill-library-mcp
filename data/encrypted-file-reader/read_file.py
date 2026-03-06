#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
encrypted-file-reader - 读取本地加密/受保护的文件内容

用法:
    python read_file.py <文件路径>

支持的文件类型:
    - 文本文件：.txt, .md, .java, .py, .js, .ts, .json, .xml, .yaml, .yml, .log, .csv
    - Word 文档：.docx
    - Excel 表格：.xlsx

说明:
    本工具用于读取用户有权限访问的本地文件，适用于企业环境中
    授权的文件读取场景。文件需要能通过系统授权的应用程序（如 Word、Excel）
    正常打开。本工具通过正确的字节处理方式处理特殊编码的文件内容，
    不涉及破解或绕过任何加密保护。
"""

import sys
import os
import zipfile
import re


# 文本文件扩展名列表
TEXT_EXTENSIONS = {
    # 基础文本
    '.txt', '.md', '.markdown', '.mkd', '.rst', '.adoc', '.asciidoc', '.tex',
    '.log', '.csv', '.tsv',
    
    # Java 生态
    '.java', '.properties', '.gradle', '.groovy', '.gvy', '.kt', '.kts', '.scala',
    
    # Python 生态
    '.py', '.pyw', '.pyx', '.pxd', '.ipynb',
    
    # Web 前端
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
    '.html', '.htm', '.xhtml', '.pug', '.jade', '.haml',
    '.css', '.scss', '.sass', '.less', '.styl',
    
    # 数据格式
    '.json', '.json5', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
    
    # C/C++ 家族
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx', '.m', '.mm',
    
    # 其他编程语言
    '.cs', '.go', '.rs', '.rb', '.php', '.pl', '.pm', '.lua',
    '.swift', '.dart', '.r', '.R', '.jl', '.clj', '.cljs', '.erl', '.hs',
    '.fs', '.fsx', '.ex', '.exs', '.tcl', '.awk', '.sed',
    
    # 脚本文件
    '.sh', '.bash', '.zsh', '.fish', '.bat', '.cmd', '.ps1', '.psm1', '.psd1',
    '.sql', '.graphql', '.gql',
    
    # 配置文件
    '.config', '.env', '.env.example', '.env.local', '.env.production',
    '.htaccess', '.editorconfig', '.gitignore', '.gitattributes', '.gitmodules',
    '.dockerfile', '.dockerignore',
    '.makefile', '.mk', '.cmake',
    '.tf', '.tfvars', '.tfstate',
    '.proto', '.thrift', '.avsc',
    
    # 差异文件
    '.diff', '.patch',
    
    # 其他
    '.readme', '.license', '.authors', '.contributors', '.changes', '.changelog'
}


def read_text_file(file_path):
    """读取文本文件内容"""
    with open(file_path, 'rb') as f:
        content = f.read()
    return content.decode('utf-8')


def read_docx(file_path):
    """读取 Word 文档 (.docx) 内容"""
    texts = []
    with zipfile.ZipFile(file_path, 'r') as z:
        # 读取 document.xml
        content = z.read('word/document.xml')
        # 提取所有 w:t 标签中的文本
        matches = re.findall(b'<w:t[^>]*>([^<]*)</w:t>', content)
        for match in matches:
            texts.append(match.decode('utf-8'))
    
    return '\n'.join(texts)


def read_xlsx(file_path):
    """读取 Excel 表格 (.xlsx) 内容"""
    texts = []
    with zipfile.ZipFile(file_path, 'r') as z:
        # 读取 sharedStrings.xml
        try:
            content = z.read('xl/sharedStrings.xml')
            # 提取所有 t 标签中的文本
            matches = re.findall(b'<si><t>([^<]*)</t>', content)
            for match in matches:
                texts.append(match.decode('utf-8'))
        except KeyError:
            # 如果没有 sharedStrings.xml，尝试读取 worksheets
            for name in z.namelist():
                if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                    content = z.read(name)
                    # 提取 cell 中的值
                    matches = re.findall(b'<v>([^<]*)</v>', content)
                    for match in matches:
                        try:
                            texts.append(match.decode('utf-8'))
                        except:
                            pass
    
    return '\n'.join(texts)


def read_file(file_path):
    """
    读取文件内容，自动识别文件类型
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件内容字符串
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    # 获取文件扩展名（小写）
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # 根据扩展名选择读取方式
    if ext == '.docx':
        return read_docx(file_path)
    elif ext == '.xlsx':
        return read_xlsx(file_path)
    elif ext in TEXT_EXTENSIONS:
        return read_text_file(file_path)
    else:
        # 尝试作为文本文件读取
        try:
            return read_text_file(file_path)
        except UnicodeDecodeError:
            raise ValueError(f"不支持的文件类型：{ext}")


def main():
    if len(sys.argv) < 2:
        print("用法：python read_file.py <文件路径>")
        print("示例：python read_file.py E:\\data\\test.docx")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        content = read_file(file_path)
        print(content)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
