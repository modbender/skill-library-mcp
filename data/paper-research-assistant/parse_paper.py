#!/usr/bin/env python3
"""
论文 PDF 解析脚本
提取论文元数据、摘要、核心章节内容
"""

import argparse
import json
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("请安装 PyMuPDF: pip install pymupdf")
    exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """从 PDF 提取全文文本"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_metadata(text: str) -> dict:
    """提取论文元数据"""
    lines = text.split('\n')
    metadata = {
        'title': '',
        'authors': [],
        'abstract': '',
        'keywords': [],
        'sections': []
    }
    
    # 提取标题（通常是第一行非空文本）
    for line in lines:
        line = line.strip()
        if line and len(line) > 10:
            metadata['title'] = line
            break
    
    # 提取摘要
    abstract_match = re.search(r'Abstract\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)', text, re.DOTALL | re.IGNORECASE)
    if abstract_match:
        metadata['abstract'] = abstract_match.group(1).strip()
    
    # 提取关键词
    keywords_match = re.search(r'(?:Keywords?|Index Terms)\s*[:\-]?\s*(.*?)(?=\n\s*\n|\n\s*[A-Z])', text, re.DOTALL | re.IGNORECASE)
    if keywords_match:
        keywords_str = keywords_match.group(1)
        metadata['keywords'] = [k.strip() for k in re.split(r'[;,]', keywords_str) if k.strip()]
    
    # 提取章节标题
    section_pattern = re.compile(r'^\d+\.\s+([A-Z][^\n]+)$', re.MULTILINE)
    metadata['sections'] = section_pattern.findall(text)
    
    return metadata


def identify_paper_type(metadata: dict) -> str:
    """识别论文类型"""
    title = metadata['title'].lower()
    abstract = metadata['abstract'].lower()
    
    if 'survey' in title or 'review' in title or '综述' in title:
        return 'survey'
    elif 'method' in title or 'approach' in title or 'framework' in title:
        return 'method'
    elif 'experiment' in abstract or 'empirical' in abstract:
        return 'experimental'
    else:
        return 'theoretical'


def extract_key_formulas(text: str) -> list:
    """提取关键公式（简单启发式）"""
    formulas = []
    formula_pattern = re.compile(r'\((\d+)\)\s*([^\n]{10,200})', re.MULTILINE)
    for match in formula_pattern.finditer(text):
        formulas.append({
            'number': match.group(1),
            'content': match.group(2).strip()[:100]
        })
    return formulas[:10]


def main():
    parser = argparse.ArgumentParser(description='论文 PDF 解析工具')
    parser.add_argument('--pdf', required=True, help='PDF 文件路径')
    parser.add_argument('--output', required=True, help='输出 JSON 文件路径')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"错误：文件不存在 {pdf_path}")
        return
    
    print(f"正在解析：{pdf_path}")
    full_text = extract_text_from_pdf(str(pdf_path))
    metadata = extract_metadata(full_text)
    metadata['paper_type'] = identify_paper_type(metadata)
    metadata['key_formulas'] = extract_key_formulas(full_text)
    metadata['full_text_preview'] = full_text[:5000]
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"解析完成：{output_path}")
    print(f"标题：{metadata['title']}")
    print(f"类型：{metadata['paper_type']}")


if __name__ == '__main__':
    main()
