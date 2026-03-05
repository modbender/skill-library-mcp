#!/usr/bin/env python3
"""
调试Notion页面结构 - 查看页面属性和内容结构
"""

import os
import json
import sys
import requests

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        notion_config = config.get('notion', {})
        return {
            'NOTION_API_KEY': notion_config.get('api_key', ''),
            'NOTION_VERSION': notion_config.get('api_version', '2022-06-28')
        }
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return {
            'NOTION_API_KEY': '',
            'NOTION_VERSION': '2022-06-28'
        }

# 加载配置
CONFIG = load_config()
NOTION_API_KEY = CONFIG['NOTION_API_KEY']
NOTION_VERSION = CONFIG['NOTION_VERSION']

# 请求头
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': NOTION_VERSION,
    'Content-Type': 'application/json'
}

def search_pages():
    """搜索页面并显示属性结构"""
    print("🔍 调试Notion页面结构")
    print("=" * 60)
    
    # 检查API密钥
    if not NOTION_API_KEY or NOTION_API_KEY.startswith('ntn_your_api_key'):
        print("❌ 请先在config.json中配置正确的Notion API密钥")
        return
    
    print("✅ 使用配置的Notion API密钥")
    print("=" * 60)
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/search",
            headers=HEADERS,
            json={
                "filter": {"value": "page", "property": "object"},
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "page_size": 3
            },
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        pages = data.get('results', [])
        
        print(f"✅ 找到 {len(pages)} 个页面")
        print("=" * 60)
        
        for i, page in enumerate(pages):
            page_id = page['id']
            print(f"\n📄 页面 {i+1}: {page_id}")
            print(f"   创建时间: {page.get('created_time')}")
            print(f"   最后编辑: {page.get('last_edited_time')}")
            print(f"   URL: {page.get('url', '')}")
            
            # 显示所有属性
            properties = page.get('properties', {})
            print(f"   属性数量: {len(properties)}")
            
            for prop_name, prop_value in properties.items():
                prop_type = prop_value.get('type', 'unknown')
                print(f"   - {prop_name} ({prop_type}):")
                
                if prop_type == 'title':
                    title_items = prop_value.get('title', [])
                    if title_items:
                        title_text = ''.join([item.get('plain_text', '') for item in title_items])
                        print(f"      标题内容: {title_text[:50]}...")
                
                elif prop_type == 'rich_text':
                    text_items = prop_value.get('rich_text', [])
                    if text_items:
                        text_content = ''.join([item.get('plain_text', '') for item in text_items])
                        print(f"      文本内容: {text_content[:50]}...")
                
                elif prop_type == 'multi_select':
                    options = prop_value.get('multi_select', [])
                    if options:
                        option_names = [opt.get('name', '') for opt in options]
                        print(f"      选项: {', '.join(option_names)}")
                
                elif prop_type == 'date':
                    date_value = prop_value.get('date', {})
                    if date_value:
                        print(f"      日期: {date_value.get('start')}")
                
                elif prop_type == 'url':
                    url_value = prop_value.get('url', '')
                    if url_value:
                        print(f"      URL: {url_value}")
                
                elif prop_type == 'relation':
                    relation_items = prop_value.get('relation', [])
                    if relation_items:
                        print(f"      关联数量: {len(relation_items)}")
            
            print("-" * 40)
            
            # 显示前几个内容块
            print("   内容块预览:")
            try:
                blocks_response = requests.get(
                    f"https://api.notion.com/v1/blocks/{page_id}/children",
                    headers=HEADERS,
                    params={"page_size": 3},
                    timeout=30
                )
                blocks_response.raise_for_status()
                
                blocks_data = blocks_response.json()
                blocks = blocks_data.get('results', [])
                
                for j, block in enumerate(blocks[:2]):  # 只显示前2个块
                    block_type = block.get('type')
                    print(f"     [{j+1}] {block_type}")
                    
                    if block_type == 'paragraph':
                        rich_text = block.get('paragraph', {}).get('rich_text', [])
                        if rich_text:
                            text = ''.join([item.get('plain_text', '') for item in rich_text])
                            print(f"        文本: {text[:50]}...")
                    
                    elif block_type == 'heading_1':
                        rich_text = block.get('heading_1', {}).get('rich_text', [])
                        if rich_text:
                            text = ''.join([item.get('plain_text', '') for item in rich_text])
                            print(f"        标题: {text[:50]}...")
            
            except Exception as e:
                print(f"     获取内容块失败: {e}")
            
            print("=" * 60)
    
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        print("请检查:")
        print("1. API密钥是否正确")
        print("2. 集成是否已分享到Notion工作空间")
        print("3. 网络连接是否正常")

def main():
    """主函数"""
    search_pages()
    
    print("\n📝 调试信息总结:")
    print("=" * 60)
    print("1. 检查页面是否有 '标题' 或 'Title' 属性")
    print("2. 确认属性类型为 'title' (不是 'rich_text')")
    print("3. 检查 '摘要' 或其他文本属性是否干扰标题提取")
    print("4. 确保Python检查器使用正确的属性名提取标题")
    print("=" * 60)
    print("\n🔧 修复建议:")
    print("如果标题提取不正确，请:")
    print("1. 修改 real_notion_checker.py 中的 get_page_title 函数")
    print("2. 添加你的特定属性名到 preferred_title_names 列表")
    print("3. 重新启动定时同步系统")
    print("=" * 60)

if __name__ == "__main__":
    main()