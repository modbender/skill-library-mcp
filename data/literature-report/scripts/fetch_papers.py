#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS抓取脚本 + PubMed API搜索
从各期刊RSS源抓取最新论文，并使用PubMed API补充缺失的期刊
"""

import feedparser
import json
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 期刊RSS列表（可用）
JOURNALS_RSS = {
    'Nature': 'https://www.nature.com/nature.rss',
    'Nature Biotechnology': 'https://www.nature.com/nbt.rss',
    'Nature Materials': 'https://www.nature.com/nmat.rss',
    'Nature Communications': 'https://www.nature.com/ncomms.rss',
    'Nature Nanotechnology': 'https://www.nature.com/nnano.rss',
    'Nature Sustainability': 'https://www.nature.com/s41893.rss',
    'Nature Reviews Drug Discovery': 'https://www.nature.com/nrd.rss',
    'Nature Reviews Materials': 'https://www.nature.com/natrevmats.rss',
    'Advanced Materials': 'https://onlinelibrary.wiley.com/feed/15214095/most-recent',
    'Advanced Science': 'https://onlinelibrary.wiley.com/feed/21983844/most-recent',
}

# 期刊PubMed搜索列表（补充无法用RSS的期刊）
JOURNALS_PUBMED = {
    # Nature子刊
    'Nature Biomedical Engineering': '"Nature Biomedical Engineering"[Journal]',
    'Nature Electronics': '"Nature Electronics"[Journal]',
    'Nature Machine Intelligence': '"Nature Machine Intelligence"[Journal]',
    'Nature Sensors': '"Nature Sensors"[Journal]',
    
    # Nature Reviews系列
    'Nature Reviews Bioengineering': '"Nature Reviews Bioengineering"[Journal]',
    'Nature Reviews Electrical Engineering': '"Nature Reviews Electrical Engineering"[Journal]',
    
    # Science系列
    'Science': '"Science"[Journal]',
    'Science Translational Medicine': '"Science Translational Medicine"[Journal]',
    'Science Advances': '"Science Advances"[Journal]',
    
    # 专业期刊（新增）
    'Biomaterials': '"Biomaterials"[Journal]',
    'Journal of Controlled Release': '"Journal of Controlled Release"[Journal]',
    'ACS Nano': '"ACS Nano"[Journal]',
    'Biosensors and Bioelectronics': '"Biosensors and Bioelectronics"[Journal]',
    'Nano Letters': '"Nano Letters"[Journal]',
    'Advanced Healthcare Materials': '"Advanced Healthcare Materials"[Journal]',
}

# 核心关键词（宽松匹配，只检查标题）
CORE_KEYWORDS = [
    'drug delivery',
    'drug-device',
    'microneedle',
    'transdermal',
    'insulin pump',
    'infusion pump',
    'theranostic',
    'biosensor',
    'patch',
    'wearable',
    'implantable',
    'sensor',
    'microfluidic',
]

# 排除关键词（标题中包含这些词的跳过）
EXCLUDE_KEYWORDS = [
    # 文献类型
    'editorial', 'comment', 'news', 'perspective', 
    'correspondence', 'letter', 'highlight', 'book review',
    'nature news', 'news and views', 'breaking news',
    'review', 'perspective', 'opinion', 'editorial',
    'correction', 'retraction', 'erratum',
    
    # 不相关主题
    'tree', 'forest', 'climate', 'policy', 'politics',
    'counting', 'together', 'eu', 'europe',
    'coral', 'microbiome', 'electrodeposition', 'window',
    'plant', 'agriculture', 'soil', 'water treatment',
    
    # 过于基础的研究
    'theoretical', 'simulation', 'modeling only',
]

def fetch_journal_papers_rss(journal_name, rss_url, days=14):
    """通过RSS抓取期刊最新论文"""
    papers = []
    
    try:
        print(f"正在抓取 {journal_name}...")
        feed = feedparser.parse(rss_url)
        
        if feed.bozo:
            print(f"  ⚠️ RSS解析警告: {feed.bozo_exception}")
        
        for entry in feed.entries:
            # 解析发布时间
            published = entry.get('published_parsed') or entry.get('updated_parsed')
            if published:
                pub_date = datetime(*published[:6])
                # 只抓取最近N天的论文
                if (datetime.now() - pub_date).days > days:
                    continue
            else:
                pub_date = None
            
            paper = {
                'title': entry.get('title', ''),
                'authors': entry.get('author', ''),
                'abstract': entry.get('summary', ''),
                'journal': journal_name,
                'link': entry.get('link', ''),
                'published': pub_date.strftime('%Y-%m-%d') if pub_date else '',
                'doi': entry.get('dc_identifier', '').replace('doi:', '') if entry.get('dc_identifier') else '',
            }
            
            papers.append(paper)
        
        print(f"  ✅ 抓取到 {len(papers)} 篇论文")
        
    except Exception as e:
        print(f"  ❌ 抓取失败: {e}")
    
    return papers

def fetch_journal_papers_pubmed(journal_query, journal_name, days=14):
    """通过PubMed API搜索期刊最新论文"""
    papers = []
    
    try:
        print(f"正在PubMed搜索 {journal_name}...")
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[PDAT]"
        
        # 构建搜索查询
        search_query = f"{journal_query} AND {date_range}"
        
        # PubMed API搜索
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': search_query,
            'retmax': 50,
            'retmode': 'json',
            'sort': 'pub_date',
        }
        
        response = requests.get(search_url, params=params, timeout=30)
        data = response.json()
        
        if 'esearchresult' not in data:
            print(f"  ⚠️ 无搜索结果")
            return papers
        
        pmids = data['esearchresult'].get('idlist', [])
        
        if not pmids:
            print(f"  ⚠️ 未找到论文")
            return papers
        
        # 获取论文详情
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids[:20]),  # 限制20篇
            'retmode': 'xml',
        }
        
        response = requests.get(fetch_url, params=params, timeout=30)
        
        # 简单解析XML（只提取标题和摘要）
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        
        for article in root.findall('.//PubmedArticle'):
            try:
                title_elem = article.find('.//ArticleTitle')
                title = title_elem.text if title_elem is not None else ''
                
                abstract_elem = article.find('.//Abstract/AbstractText')
                abstract = abstract_elem.text if abstract_elem is not None else ''
                
                authors_elem = article.findall('.//Author')
                authors = []
                for author in authors_elem[:5]:  # 只取前5个作者
                    lastname = author.find('LastName')
                    if lastname is not None:
                        authors.append(lastname.text)
                authors_str = ', '.join(authors)
                
                pub_date_elem = article.find('.//PubDate/Year')
                pub_date = pub_date_elem.text if pub_date_elem is not None else ''
                
                pmid_elem = article.find('.//PMID')
                pmid = pmid_elem.text if pmid_elem is not None else ''
                
                paper = {
                    'title': title,
                    'authors': authors_str,
                    'abstract': abstract,
                    'journal': journal_name,
                    'link': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'published': pub_date,
                    'doi': '',
                }
                
                papers.append(paper)
                
            except Exception as e:
                continue
        
        print(f"  ✅ 抓取到 {len(papers)} 篇论文")
        
        # 避免API限流
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ❌ PubMed搜索失败: {e}")
    
    return papers

def filter_papers_by_keywords(papers):
    """根据关键词进行宽松筛选（第一轮）"""
    filtered_papers = []
    
    for paper in papers:
        # 过滤文献类型：只保留article和review
        title = paper.get('title', '')
        if not title or title is None:
            continue
        
        title_lower = title.lower()
        
        # 排除非article/review类型
        if any(exclude in title_lower for exclude in EXCLUDE_KEYWORDS):
            continue
        
        # 宽松匹配：标题中包含任意核心关键词
        for keyword in CORE_KEYWORDS:
            if keyword.lower() in title_lower:
                filtered_papers.append(paper)
                break
    
    return filtered_papers

def main():
    """主函数"""
    print("=" * 60)
    print("开始抓取最新论文")
    print("=" * 60)
    
    all_papers = []
    
    # 通过RSS抓取期刊
    print("\n【通过RSS抓取期刊】")
    for journal_name, rss_url in JOURNALS_RSS.items():
        papers = fetch_journal_papers_rss(journal_name, rss_url, days=14)
        all_papers.extend(papers)
    
    # 通过PubMed API补充期刊
    print("\n【通过PubMed API补充期刊】")
    for journal_name, journal_query in JOURNALS_PUBMED.items():
        papers = fetch_journal_papers_pubmed(journal_query, journal_name, days=14)
        all_papers.extend(papers)
    
    print(f"\n总共抓取到 {len(all_papers)} 篇论文")
    
    # 第一轮：关键词筛选（宽松）
    print("\n【第一轮】关键词筛选...")
    filtered_papers = filter_papers_by_keywords(all_papers)
    print(f"筛选后剩余 {len(filtered_papers)} 篇候选论文")
    
    # 第二轮：AI语义理解（如果候选论文较多，限制数量）
    max_ai_papers = 20  # 限制AI判断的论文数量
    if len(filtered_papers) > max_ai_papers:
        print(f"\n候选论文较多，限制AI判断数量为 {max_ai_papers} 篇")
        # 随机选择或按期刊分布选择
        filtered_papers = filtered_papers[:max_ai_papers]
    
    # 使用AI筛选
    from ai_filter import filter_papers_with_ai
    ai_filtered_papers = filter_papers_with_ai(filtered_papers, research_focus="医疗设备相关研究")
    print(f"AI筛选后剩余 {len(ai_filtered_papers)} 篇相关论文")
    
    # 去重（根据标题）
    seen_titles = set()
    unique_papers = []
    for paper in ai_filtered_papers:
        title_key = paper['title'].lower().strip()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_papers.append(paper)
    
    print(f"去重后剩余 {len(unique_papers)} 篇论文")
    
    # 按发布时间排序
    unique_papers.sort(key=lambda x: x['published'], reverse=True)
    
    # 限制数量
    max_papers = 5
    final_papers = unique_papers[:max_papers]
    
    print(f"\n最终选择 {len(final_papers)} 篇论文")
    
    # 保存数据
    output_file = PROJECT_ROOT / 'data' / 'latest_papers.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_papers, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到: {output_file}")
    print("=" * 60)
    
    return final_papers

if __name__ == '__main__':
    main()