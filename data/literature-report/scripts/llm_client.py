#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM调用脚本
使用配置文件中的API配置
"""

import requests
import json
from pathlib import Path
import sys

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config_loader import get_api_config

def call_llm(prompt, max_tokens=500):
    """调用LLM API"""
    
    # 从配置文件读取API配置
    try:
        api_config = get_api_config()
        api_key = api_config['api_key']
        base_url = api_config['base_url']
        model = api_config['model']
    except Exception as e:
        print(f"❌ API配置加载失败: {e}")
        return None
    
    # 检查API Key是否已配置
    if api_key == "YOUR_API_KEY_HERE":
        print("❌ 请先在config.yaml中配置API Key")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"API调用失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"API调用异常: {e}")
        return None

def generate_chinese_title(english_title):
    """生成中文标题"""
    
    prompt = f"""请将以下英文论文标题翻译成中文，要求：
1. 准确传达原文含义
2. 符合中文学术表达习惯
3. 不要添加任何解释或说明，只输出翻译后的中文标题

英文标题：{english_title}

中文标题："""
    
    return call_llm(prompt, max_tokens=200)

def generate_english_summary(title, abstract):
    """生成100词英文摘要"""
    
    # 如果摘要太短，用标题生成
    if len(abstract) < 100 or 'EarlyView' in abstract or 'Volume' in abstract:
        prompt = f"""请根据以下论文标题生成一段约100词的英文摘要，要求：
1. 简明扼要地概述研究内容
2. 突出创新点和应用价值
3. 使用学术写作风格
4. 控制在80-120词之间

标题：{title}

摘要："""
    else:
        prompt = f"""请将以下论文摘要压缩成约100词的简洁版本，要求：
1. 保留核心研究内容和创新点
2. 突出应用价值
3. 控制在80-120词之间

标题：{title}

原始摘要：{abstract}

精简摘要："""
    
    return call_llm(prompt, max_tokens=300)

def generate_key_findings(title, abstract):
    """生成关键发现"""
    
    prompt = f"""请根据以下论文信息提取3个关键发现，要求：
1. 每个发现用一句话概括
2. 突出创新性和应用价值
3. 使用简洁的学术表达

标题：{title}
摘要：{abstract}

关键发现（3条）："""
    
    result = call_llm(prompt, max_tokens=300)
    
    if result:
        # 解析关键发现
        findings = []
        for line in result.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # 移除编号
                if line[0].isdigit():
                    line = line.split('.', 1)[-1].strip()
                elif line.startswith('-') or line.startswith('•'):
                    line = line[1:].strip()
                findings.append(line)
        
        return findings[:3] if findings else ["请查看原文获取详细信息"]
    
    return ["请查看原文获取详细信息"]

def process_paper(paper):
    """处理单篇论文，生成中文标题、英文摘要和关键发现"""
    
    title = paper.get('title', '')
    abstract = paper.get('abstract', '')
    
    print(f"  处理: {title[:50]}...")
    
    # 生成中文标题
    title_cn = generate_chinese_title(title)
    if not title_cn:
        title_cn = title
    
    # 生成英文摘要
    summary_en = generate_english_summary(title, abstract)
    if not summary_en:
        summary_en = abstract[:200] if abstract else "Please refer to the original article for details."
    
    # 生成关键发现
    key_findings = generate_key_findings(title, abstract)
    
    return {
        'title_cn': title_cn,
        'summary_en': summary_en,
        'key_findings': key_findings
    }

if __name__ == '__main__':
    # 测试
    test_title = "Machine Learning‐Informed Nano Co‐Assembly Inhibits Fibroblast Activation Protein and Improves Drug Delivery in Fibrotic Tissue"
    test_abstract = "This study presents a novel approach using machine learning to optimize nano co-assembly for improved drug delivery."
    
    print("测试LLM调用...")
    print("\n生成中文标题...")
    title_cn = generate_chinese_title(test_title)
    print(f"中文标题: {title_cn}")
    
    print("\n生成英文摘要...")
    summary_en = generate_english_summary(test_title, test_abstract)
    print(f"英文摘要: {summary_en}")