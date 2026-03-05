#!/usr/bin/env python3
"""文档处理工具 - Word, PDF, Excel"""

import sys
import os
from pathlib import Path

def read_docx(filepath):
    from docx import Document
    doc = Document(filepath)
    return '\n'.join([p.text for p in doc.paragraphs])

def read_pdf(filepath):
    import pdfplumber
    text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or '')
    return '\n\n---PAGE---\n\n'.join(text)

def read_xlsx(filepath):
    import pandas as pd
    # 读取所有 sheet
    excel_file = pd.ExcelFile(filepath)
    result = []
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        result.append(f"=== Sheet: {sheet_name} ===\n{df.to_string()}")
    return '\n\n'.join(result)

def read_file(filepath):
    ext = Path(filepath).suffix.lower()
    if ext == '.docx':
        return read_docx(filepath)
    elif ext == '.pdf':
        return read_pdf(filepath)
    elif ext in ['.xlsx', '.xls']:
        return read_xlsx(filepath)
    else:
        return f"不支持的文件类型: {ext}"

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: doc_handler.py <read> <文件路径>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    filepath = sys.argv[2]
    
    if cmd == 'read':
        try:
            print(read_file(filepath))
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
