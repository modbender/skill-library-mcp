#!/usr/bin/env python3
"""
真实Notion API文章检查器
使用真实的Notion API检查文章更新并导出到Obsidian
"""

import os
import json
import sys
import requests
from datetime import datetime, timedelta
import pytz
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 设置默认值
        notion_config = config.get('notion', {})
        obsidian_config = config.get('obsidian', {})
        sync_config = config.get('sync', {})
        export_config = config.get('export', {})
        logging_config = config.get('logging', {})
        
        return {
            'NOTION_API_KEY': notion_config.get('api_key', ''),
            'NOTION_VERSION': notion_config.get('api_version', '2022-06-28'),
            'OBSIDIAN_ROOT': obsidian_config.get('root_dir', '/path/to/your/obsidian'),
            'CHECK_INTERVAL': sync_config.get('check_interval_minutes', 15),
            'QUIET_START': sync_config.get('quiet_hours_start', '00:00'),
            'QUIET_END': sync_config.get('quiet_hours_end', '08:30'),
            'TIMEZONE': export_config.get('timezone', 'Asia/Shanghai'),
            'LOG_FILE': logging_config.get('log_file', 'sync_timer.log')
        }
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        # 返回默认配置
        return {
            'NOTION_API_KEY': '',
            'NOTION_VERSION': '2022-06-28',
            'OBSIDIAN_ROOT': '/path/to/your/obsidian',
            'CHECK_INTERVAL': 15,
            'QUIET_START': '00:00',
            'QUIET_END': '08:30',
            'TIMEZONE': 'Asia/Shanghai',
            'LOG_FILE': 'sync_timer.log'
        }

# 加载配置
CONFIG = load_config()

# 配置常量
NOTION_API_KEY = CONFIG['NOTION_API_KEY']
NOTION_VERSION = CONFIG['NOTION_VERSION']
OBSIDIAN_ROOT = CONFIG['OBSIDIAN_ROOT']
TIMEZONE = pytz.timezone(CONFIG['TIMEZONE'])

# 请求头
HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Notion-Version': NOTION_VERSION,
    'Content-Type': 'application/json'
}

def get_notion_databases():
    """获取Notion中的所有数据库"""
    try:
        print("📋 获取Notion数据库列表...")
        response = requests.post(
            'https://api.notion.com/v1/search',
            headers=HEADERS,
            json={
                'filter': {'property': 'object', 'value': 'database'},
                'sort': {'direction': 'descending', 'timestamp': 'last_edited_time'}
            },
            timeout=30
        )
        response.raise_for_status()
        databases = response.json().get('results', [])
        print(f"✅ 找到 {len(databases)} 个数据库")
        return databases
    except Exception as e:
        print(f"❌ 获取数据库失败: {e}")
        return []

def get_page_title(page):
    """从页面属性中提取标题（修复版本）"""
    properties = page.get('properties', {})
    
    # 优先查找常见的标题属性名（中文和英文）
    preferred_title_names = ['标题', 'Title', '名称', 'Name', 'title', '名称', '標題']
    
    # 1. 首先按属性名查找
    for prop_name, prop_value in properties.items():
        if prop_name in preferred_title_names:
            prop_type = prop_value.get('type')
            if prop_type == 'title':
                title_items = prop_value.get('title', [])
                if title_items:
                    title_text = ''.join([item.get('plain_text', '') for item in title_items])
                    if title_text.strip():
                        return title_text
    
    # 2. 然后按类型查找（title类型）
    for prop_name, prop_value in properties.items():
        prop_type = prop_value.get('type')
        if prop_type == 'title':
            title_items = prop_value.get('title', [])
            if title_items:
                title_text = ''.join([item.get('plain_text', '') for item in title_items])
                if title_text.strip():
                    return title_text
    
    # 3. 如果没有找到合适的标题，使用页面ID
    return f"未命名页面_{page['id'][:8]}"

def get_page_blocks(page_id):
    """获取页面的所有内容块"""
    try:
        print(f"    获取页面内容块 {page_id[:8]}...")
        all_blocks = []
        has_more = True
        start_cursor = None
        
        while has_more:
            params = {}
            if start_cursor:
                params['start_cursor'] = start_cursor
            
            response = requests.get(
                f'https://api.notion.com/v1/blocks/{page_id}/children',
                headers=HEADERS,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            all_blocks.extend(data.get('results', []))
            has_more = data.get('has_more', False)
            start_cursor = data.get('next_cursor')
        
        print(f"    获取到 {len(all_blocks)} 个内容块")
        return all_blocks
    except Exception as e:
        print(f"❌ 获取内容块失败: {e}")
        return []

def extract_rich_text(rich_text):
    """提取富文本内容并应用格式"""
    if not rich_text:
        return ''
    
    text_parts = []
    for text_item in rich_text:
        text_content = text_item.get('plain_text', '')
        annotations = text_item.get('annotations', {})
        
        # 应用文本格式
        if annotations.get('bold'):
            text_content = f'**{text_content}**'
        if annotations.get('italic'):
            text_content = f'*{text_content}*'
        if annotations.get('strikethrough'):
            text_content = f'~~{text_content}~~'
        if annotations.get('code'):
            text_content = f'`{text_content}`'
        
        # 处理链接
        if text_item.get('href'):
            text_content = f'[{text_content}]({text_item["href"]})'
        
        text_parts.append(text_content)
    
    return ''.join(text_parts)

def convert_block_to_markdown(block, indent_level=0):
    """将单个Notion块转换为Markdown"""
    block_type = block.get('type')
    block_content = block.get(block_type, {})
    
    # 缩进
    indent = '  ' * indent_level
    
    if block_type == 'paragraph':
        text = extract_rich_text(block_content.get('rich_text', []))
        return f"{indent}{text}\n" if text else ''
    
    elif block_type == 'heading_1':
        text = extract_rich_text(block_content.get('rich_text', []))
        return f"{indent}# {text}\n\n" if text else ''
    
    elif block_type == 'heading_2':
        text = extract_rich_text(block_content.get('rich_text', []))
        return f"{indent}## {text}\n\n" if text else ''
    
    elif block_type == 'heading_3':
        text = extract_rich_text(block_content.get('rich_text', []))
        return f"{indent}### {text}\n\n" if text else ''
    
    elif block_type == 'bulleted_list_item':
        text = extract_rich_text(block_content.get('rich_text', []))
        bullet = f"{indent}* "
        return f"{bullet}{text}\n" if text else ''
    
    elif block_type == 'numbered_list_item':
        text = extract_rich_text(block_content.get('rich_text', []))
        number = f"{indent}1. "
        return f"{number}{text}\n" if text else ''
    
    elif block_type == 'to_do':
        text = extract_rich_text(block_content.get('rich_text', []))
        checked = block_content.get('checked', False)
        checkbox = '[x]' if checked else '[ ]'
        return f"{indent}{checkbox} {text}\n" if text else ''
    
    elif block_type == 'code':
        text = extract_rich_text(block_content.get('rich_text', []))
        language = block_content.get('language', '')
        return f"{indent}```{language}\n{indent}{text}\n{indent}```\n\n" if text else ''
    
    elif block_type == 'quote':
        text = extract_rich_text(block_content.get('rich_text', []))
        return f"{indent}> {text}\n\n" if text else ''
    
    elif block_type == 'divider':
        return f"{indent}---\n\n"
    
    elif block_type == 'image':
        image_url = block_content.get('external', {}).get('url') or block_content.get('file', {}).get('url')
        if image_url:
            return f"{indent}![Image]({image_url})\n\n"
    
    elif block_type == 'bookmark':
        url = block_content.get('url', '')
        if url:
            return f"{indent}[Bookmark]({url})\n\n"
    
    return ''

def save_page_as_markdown(page, markdown_content):
    """将页面保存为Markdown文件"""
    try:
        # 创建年-月目录
        now = datetime.now(TIMEZONE)
        year_month = now.strftime('%Y-%m')
        
        # 创建notion子目录
        target_dir = Path(OBSIDIAN_ROOT) / 'notion' / year_month
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取页面信息
        page_id = page['id']
        page_title = get_page_title(page)
        created_time = page.get('created_time', '')
        last_edited_time = page.get('last_edited_time', '')
        url = page.get('url', '')
        
        # 生成安全的文件名
        safe_title = ''.join(c for c in page_title if c.isalnum() or c in (' ', '-', '_', '，', '。')).strip()
        safe_title = safe_title[:80] or 'untitled'
        
        filename = f"{safe_title}.md"
        filepath = target_dir / filename
        
        # 避免文件名冲突
        counter = 1
        while filepath.exists():
            filename = f"{safe_title}_{counter}.md"
            filepath = target_dir / filename
            counter += 1
        
        # 创建完整的Markdown内容
        full_content = f"""---
title: {page_title}
notion_id: {page_id}
created_time: {created_time}
last_edited_time: {last_edited_time}
original_url: {url}
export_time: {now.isoformat()}
---

# {page_title}

{markdown_content}
"""
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"✅ 保存: {page_title} -> {filepath}")
        return str(filepath)
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 真实Notion API文章检查器")
    print("=" * 50)
    
    # 检查API密钥
    if not NOTION_API_KEY or NOTION_API_KEY.startswith('ntn_your_api_key'):
        print("❌ 请先在config.json中配置正确的Notion API密钥")
        return
    
    print(f"✅ 使用配置的Notion API密钥")
    print(f"时区: {TIMEZONE}")
    print(f"导出目录: {OBSIDIAN_ROOT}/notion/")
    print(f"当前时间: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 获取数据库
    databases = get_notion_databases()
    if not databases:
        print("❌ 没有找到数据库，检查API权限")
        return
    
    exported_files = []
    
    # 检查每个数据库
    for db in databases:
        db_id = db['id']
        db_title = db.get('title', [{}])[0].get('plain_text', '未命名数据库')
        
        print(f"\n📁 检查数据库: {db_title}")
        
        # 查询最近编辑的页面（最近24小时）
        last_check_time = datetime.now(TIMEZONE) - timedelta(hours=24)
        
        try:
            response = requests.post(
                f'https://api.notion.com/v1/databases/{db_id}/query',
                headers=HEADERS,
                json={
                    'filter': {
                        'timestamp': 'last_edited_time',
                        'last_edited_time': {
                            'after': last_check_time.isoformat()
                        }
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            pages = response.json().get('results', [])
        except Exception as e:
            print(f"❌ 查询数据库失败: {e}")
            continue
        
        print(f"  找到 {len(pages)} 个最近编辑的页面")
        
        if not pages:
            print("  没有最近编辑的页面")
            continue
        
        # 处理每个页面
        for page in pages:
            page_id = page['id']
            page_title = get_page_title(page)
            
            print(f"  📄 处理页面: {page_title}")
            
            # 获取页面内容块
            blocks = get_page_blocks(page_id)
            if not blocks:
                print(f"    页面没有内容块")
                continue
            
            # 转换为Markdown
            markdown_content = []
            for block in blocks:
                content = convert_block_to_markdown(block)
                if content:
                    markdown_content.append(content)
            
            if not markdown_content:
                print(f"    页面内容为空")
                continue
            
            full_markdown = ''.join(markdown_content)
            
            # 保存为文件
            filepath = save_page_as_markdown(page, full_markdown)
            if filepath:
                exported_files.append((page_title, filepath))
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 检查完成")
    print(f"处理数据库: {len(databases)} 个")
    print(f"导出文章: {len(exported_files)} 篇")
    
    if exported_files:
        print("\n📁 导出的文章:")
        for title, path in exported_files:
            print(f"  ✅ {title}")
        
        # 发送移动端优化通知
        print("\n📱 移动端通知格式:")
        for title, path in exported_files:
            print(f"""
📱 Notion文章更新通知

📄 文章标题: {title}
📁 保存位置: {path}
🕒 更新时间: {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M')}
🔗 原始链接: [Notion页面]

✅ 文章已成功导出到Obsidian
""")
    else:
        print("📭 没有发现新的文章更新")
    
    print("=" * 50)

if __name__ == "__main__":
    main()