#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

def truncate_text(text, max_words):
    """截断文本到指定的单词数"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + '...'

def is_related_to_product_development(title, content):
    """检查内容是否与产品开发相关"""
    product_keywords = ['product', 'development', 'launch', 'release', 'feature', 'update', 'announcement', 'api', 'platform', 'tool', 'framework', 'library', 'service']
    ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network']
    
    combined = product_keywords + ai_keywords
    text = (title + ' ' + content).lower()
    
    return any(keyword in text for keyword in combined)

def read_websites():
    """读取网站列表"""
    return [
        {'name': 'TechCrunch', 'url': 'https://techcrunch.com'},
        {'name': 'VentureBeat', 'url': 'https://venturebeat.com'},
        {'name': 'MIT Tech Review', 'url': 'https://www.technologyreview.com'},
        {'name': 'ZDNet', 'url': 'https://www.zdnet.com'},
        {'name': 'Wired', 'url': 'https://www.wired.com'},
        {'name': 'Ars Technica', 'url': 'https://arstechnica.com'}
    ]

def main():
    print("AI Research Scraper - 抓取AI领域最新研究信息")
    print("=" * 60)
    
    # 使用tavily-search技能获取结果
    try:
        result = subprocess.run([
            'node', '/root/.openclaw/workspace/skills/tavily-search/scripts/search.mjs',
            'AI product development',
            '-n', '10',
            '--topic', 'news'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # 解析tavily-search的输出
            output = result.stdout.split('\n')
            i = 0
            while i < len(output):
                if output[i].startswith('## Answer'):
                    i += 2
                    continue
                if output[i].startswith('## Sources'):
                    i += 2
                    while i < len(output):
                        if output[i].startswith('- **') and len(output[i]) > 5:
                            title = output[i].split('**')[1]
                            title = title.split('(')[0].strip()
                            source = output[i + 1].strip() if (i + 1 < len(output) and output[i + 1].strip()) else ''
                            summary = output[i + 2].strip() if (i + 2 < len(output) and output[i + 2].strip()) else ''
                            i += 3
                            
                            # 处理摘要：截断
                            if len(summary) > 200:
                                summary = summary[:200] + '...'
                            
                            print(f"标题: {title}")
                            print(f"摘要: {summary}")
                            print(f"来源: {source}")
                            print()
                        else:
                            i += 1
                else:
                    i += 1
        else:
            print(f"  查询失败: {result.stderr}")
    except Exception as e:
        print(f"  调用tavily-search技能失败: {str(e)}")

if __name__ == "__main__":
    main()