#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成摘要和关键发现
使用硅基流动API调用Step-3.5-Flash模型
"""

import json
from pathlib import Path
import sys

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入LLM模块
from llm_client import generate_chinese_title, generate_english_summary, generate_key_findings

def process_papers():
    """处理所有论文"""
    
    # 读取数据
    input_file = PROJECT_ROOT / 'data' / 'latest_papers.json'
    with open(input_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    print(f"读取到 {len(papers)} 篇论文")
    
    # 生成摘要
    for paper in papers:
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        
        print(f"\n处理: {title[:60]}...")
        
        # 生成中文标题
        title_cn = generate_chinese_title(title)
        paper['title_cn'] = title_cn if title_cn else title
        print(f"  ✅ 中文标题: {paper['title_cn'][:50]}...")
        
        # 生成英文摘要
        summary_en = generate_english_summary(title, abstract)
        paper['summary_en'] = summary_en if summary_en else abstract[:200] if abstract else "Please refer to the original article."
        print(f"  ✅ 英文摘要已生成 ({len(paper['summary_en'])} chars)")
        
        # 生成关键发现
        key_findings = generate_key_findings(title, abstract)
        paper['key_findings'] = key_findings
        print(f"  ✅ 关键发现: {len(key_findings)} 条")
    
    # 保存数据
    output_file = PROJECT_ROOT / 'data' / 'papers_with_summary.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到: {output_file}")
    
    return papers

if __name__ == '__main__':
    process_papers()