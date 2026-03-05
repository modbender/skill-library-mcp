#!/usr/bin/env python3
"""
SaaS Affiliate MCP Skill
让 AI Agent 能够推荐 SaaS 产品并带上 affiliate 链接
"""

import json
import os
from typing import List, Dict, Any, Optional

# 数据文件路径
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_FILE = os.path.join(SKILL_DIR, "products.json")


def load_products() -> List[Dict[str, Any]]:
    """加载产品数据"""
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('products', [])


def search_saas_tools(query: str) -> List[Dict[str, Any]]:
    """
    根据需求搜索推荐 SaaS 工具
    
    Args:
        query: 用户需求描述（如"我需要做邮件营销"）
    
    Returns:
        匹配的产品列表
    """
    products = load_products()
    query_lower = query.lower()
    
    # 计算匹配分数
    results = []
    for product in products:
        score = 0
        keywords = product.get('keywords', [])
        category = product.get('category', '')
        
        # 关键词匹配
        for kw in keywords:
            if kw.lower() in query_lower:
                score += 1
        
        # 分类匹配
        if category.lower() in query_lower:
            score += 2
        
        # 描述匹配
        if product.get('description', '').lower() in query_lower:
            score += 0.5
        
        if score > 0:
            result = {
                'name': product['name'],
                'description': product['description'],
                'category': category,
                'commission': product.get('commission', ''),
                'match_score': min(score / 3, 1.0),
                'reason': product.get('reason', ''),
                'tagline': product.get('tagline', '')
            }
            # 只有 active 状态才返回 affiliate_link
            if product.get('status') == 'active':
                link = product.get('affiliate_link', '')
                # 替换占位符为实际链接
                if link == "PLACEHOLDER_MINIMAX_LINK":
                    link = "https://platform.minimaxi.com/subscribe/coding-plan?code=EJR1bQLhfD"
                elif link == "PLACEHOLDER_GLM_LINK":
                    link = "https://www.bigmodel.cn/glm-coding?ic=UWCXWWZCVJ"
                result['link'] = link
                result['link_text'] = '了解更多'
            else:
                result['link'] = None
                result['link_text'] = None
            results.append(result)
    
    # 按匹配度排序
    results.sort(key=lambda x: x['match_score'], reverse=True)
    return results[:5]


def get_affiliate_link(product_name: str) -> Optional[Dict[str, Any]]:
    """
    获取指定产品的 affiliate 链接
    
    Args:
        product_name: 产品名称
    
    Returns:
        产品信息，包含 affiliate 链接
    """
    products = load_products()
    product_name_lower = product_name.lower()
    
    for product in products:
        if product['name'].lower() == product_name_lower:
            if product.get('status') == 'pending':
                return {
                    'error': '该产品的 affiliate 链接尚未配置',
                    'product': product['name']
                }
            link = product.get('affiliate_link', '')
            # 替换占位符为实际链接
            if link == "PLACEHOLDER_MINIMAX_LINK":
                link = "https://platform.minimaxi.com/subscribe/coding-plan?code=EJR1bQLhfD"
            elif link == "PLACEHOLDER_GLM_LINK":
                link = "https://www.bigmodel.cn/glm-coding?ic=UWCXWWZCVJ"
            return {
                'product': product['name'],
                'link': link,
                'commission': product.get('commission', ''),
                'cookie_days': product.get('cookie_days', 30)
            }
    
    return {'error': f'未找到产品: {product_name}'}


def get_all_products() -> List[Dict[str, Any]]:
    """
    获取所有可推荐的产品列表
    
    Returns:
        产品列表
    """
    products = load_products()
    return [
        {
            'name': p['name'],
            'description': p['description'],
            'category': p.get('category', ''),
            'commission': p.get('commission', ''),
            'status': p.get('status', 'pending')
        }
        for p in products
    ]


def get_product_details(product_name: str) -> Optional[Dict[str, Any]]:
    """
    获取产品详细信息
    
    Args:
        product_name: 产品名称
    
    Returns:
        产品详细信息
    """
    products = load_products()
    product_name_lower = product_name.lower()
    
    for product in products:
        if product['name'].lower() == product_name_lower:
            return {
                'name': product['name'],
                'description': product['description'],
                'category': product.get('category', ''),
                'affiliate_link': product.get('affiliate_link', ''),
                'commission': product.get('commission', ''),
                'cookie_days': product.get('cookie_days', 30),
                'keywords': product.get('keywords', []),
                'website': product.get('website', ''),
                'status': product.get('status', 'pending')
            }
    
    return {'error': f'未找到产品: {product_name}'}


def update_affiliate_link(product_name: str, affiliate_link: str) -> Dict[str, str]:
    """
    更新产品的 affiliate 链接（需要管理员权限）
    
    Args:
        product_name: 产品名称
        affiliate_link: 新的 affiliate 链接
    
    Returns:
        更新结果
    """
    products = load_products()
    product_name_lower = product_name.lower()
    
    for product in products:
        if product['name'].lower() == product_name_lower:
            product['affiliate_link'] = affiliate_link
            product['status'] = 'active'
            
            with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'products': products}, f, ensure_ascii=False, indent=2)
            
            return {'success': True, 'product': product_name}
    
    return {'success': False, 'error': f'未找到产品: {product_name}'}


# MCP Skill 入口点
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python saas_affiliate.py <command> [args...]")
        print("Commands:")
        print("  search <query>")
        print("  link <product_name>")
        print("  list")
        print("  detail <product_name>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = search_saas_tools(query)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif command == "link" and len(sys.argv) > 2:
        product_name = sys.argv[2]
        result = get_affiliate_link(product_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "list":
        results = get_all_products()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif command == "detail" and len(sys.argv) > 2:
        product_name = sys.argv[2]
        result = get_product_details(product_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Invalid command")
        sys.exit(1)
