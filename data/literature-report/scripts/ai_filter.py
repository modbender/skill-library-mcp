#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI辅助检索脚本
使用LLM进行语义理解，判断论文是否相关
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

def check_paper_relevance(title, abstract, research_focus="医疗设备相关研究"):
    """使用LLM判断论文是否与研究主题相关"""
    
    prompt = f"""你是一个科研文献筛选专家。请判断以下论文是否与"{research_focus}"相关。

研究主题包括：
- 可穿戴医疗设备（如：智能手表、健康监测贴片、可穿戴传感器等）
- 药物递送设备（如：微针贴片、胰岛素泵、植入式给药系统等）
- 生物传感器（用于疾病诊断、健康监测、生物标志物检测等）
- 植入式医疗设备（如：心脏起搏器、神经刺激器、人工关节等）
- 监测+治疗闭环系统
- AI在医疗设备中的应用
- 柔性电子器件（用于医疗健康）
- 微流控芯片（用于诊断或治疗）

论文标题：{title}

论文摘要：{abstract if abstract else "无摘要"}

请回答：
1. 是否相关（是/否）
2. 相关程度（高/中/低）
3. 简要说明理由（1句话）

请严格按照以下格式回复：
是否相关：是/否
相关程度：高/中/低
理由：XXX
"""
    
    result = call_llm(prompt, max_tokens=200)
    
    if result:
        # 解析结果
        is_relevant = "是" in result.split("是否相关")[1].split("\n")[0] if "是否相关" in result else False
        relevance_level = "高" if "高" in result else ("中" if "中" in result else "低")
        
        return {
            'is_relevant': is_relevant,
            'relevance_level': relevance_level,
            'reason': result
        }
    
    return {
        'is_relevant': False,
        'relevance_level': '低',
        'reason': 'AI判断失败'
    }

def filter_papers_with_ai(papers, research_focus="医疗设备相关研究"):
    """使用AI筛选论文"""
    
    print(f"\n使用AI筛选论文（研究主题：{research_focus}）...")
    
    filtered_papers = []
    
    for i, paper in enumerate(papers):
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        
        print(f"  [{i+1}/{len(papers)}] 分析: {title[:60]}...")
        
        # 使用AI判断相关性
        result = check_paper_relevance(title, abstract, research_focus)
        
        if result['is_relevant']:
            paper['ai_relevance'] = result['relevance_level']
            paper['ai_reason'] = result['reason']
            filtered_papers.append(paper)
            print(f"    ✅ 相关程度：{result['relevance_level']}")
        else:
            print(f"    ❌ 不相关")
    
    # 按相关程度排序
    relevance_order = {'高': 3, '中': 2, '低': 1}
    filtered_papers.sort(key=lambda x: relevance_order.get(x.get('ai_relevance', '低'), 0), reverse=True)
    
    return filtered_papers

if __name__ == '__main__':
    # 测试
    test_title = "A wireless patch for the continuous monitoring of C-reactive protein in sweat"
    test_abstract = "This study presents a wireless wearable patch for continuous monitoring of biomarkers in sweat."
    
    print("测试AI相关性判断...")
    result = check_paper_relevance(test_title, test_abstract)
    print(f"\n结果：{result}")