#!/usr/bin/env python3
"""
PyZotero Python Script - 支持本地和在线 API 的 Zotero 库管理工具

环境变量:
  ZOTERO_LOCAL: "true" 或 "false" (默认："true")
    - true: 使用本地 Zotero API (需要 Zotero 7+ 运行并启用本地访问)
    - false: 使用 Zotero 在线 Web API (需要 API Key)
  
  ZOTERO_USER_ID: (在线 API 必需) 您的 Zotero 用户 ID
  ZOTERO_API_KEY: (在线 API 必需) 您的 Zotero API Key

用法:
  python3 pyzotero.py search -q "关键词"
  python3 pyzotero.py listcollections
  python3 pyzotero.py itemtypes
  python3 pyzotero.py item ITEM_KEY
"""

import os
import sys
import json
import argparse
from datetime import datetime

# 导入 pyzotero
try:
    from pyzotero import zotero
    print("✓ pyzotero 导入成功", file=sys.stderr)
except Exception as e:
    print(f"错误：无法导入 pyzotero 库：{type(e).__name__}: {e}", file=sys.stderr)
    print("请运行：pipx install pyzotero 或 pip install --user --break-system-packages pyzotero", file=sys.stderr)
    sys.exit(1)


def get_zotero_instance():
    """
    根据 ZOTERO_LOCAL 环境变量创建 Zotero 实例
    
    返回:
        zotero.Zotero 或 zotero.Zotero 本地实例
    """
    local_mode = os.environ.get('ZOTERO_LOCAL', 'true').lower() == 'true'
    
    if local_mode:
        # 本地模式：使用本地 Zotero API
        try:
            zot = zotero.Zotero('local', 'user')
            # 测试连接
            zot.num_items()
            print(f"✓ 已连接到本地 Zotero", file=sys.stderr)
            return zot
        except Exception as e:
            print(f"✗ 无法连接到本地 Zotero: {e}", file=sys.stderr)
            print(f"提示：请确保 Zotero 正在运行，并在 设置 > 高级 > 中启用", file=sys.stderr)
            print(f"      '允许此计算机上的其他应用程序与 Zotero 通信'", file=sys.stderr)
            sys.exit(1)
    else:
        # 在线模式：使用 Zotero Web API
        user_id = os.environ.get('ZOTERO_USER_ID')
        api_key = os.environ.get('ZOTERO_API_KEY')
        
        if not user_id or not api_key:
            print("错误：在线模式需要设置 ZOTERO_USER_ID 和 ZOTERO_API_KEY 环境变量", file=sys.stderr)
            print(f"提示：export ZOTERO_USER_ID='your_user_id'", file=sys.stderr)
            print(f"      export ZOTERO_API_KEY='your_api_key'", file=sys.stderr)
            sys.exit(1)
        
        try:
            zot = zotero.Zotero(user_id, 'user', api_key)
            # 测试连接
            zot.num_items()
            print(f"✓ 已连接到 Zotero 在线 API (用户：{user_id})", file=sys.stderr)
            return zot
        except Exception as e:
            print(f"✗ 无法连接到 Zotero 在线 API: {e}", file=sys.stderr)
            sys.exit(1)


def search_items(zot, query, fulltext=False, itemtype=None, collection=None, limit=20, json_output=False):
    """搜索 Zotero 库中的项目"""
    try:
        # 构建搜索参数
        params = {'q': query, 'limit': limit}
        
        if fulltext:
            params['qmode'] = 'everything'
        
        if itemtype:
            params['itemType'] = itemtype
        
        if collection:
            params['collection'] = collection
        
        items = zot.top(**params)
        
        if not items:
            print("未找到匹配的项目。")
            return
        
        if json_output:
            print(json.dumps(items, indent=2, ensure_ascii=False))
        else:
            print(f"找到 {len(items)} 个项目:\n")
            for i, item in enumerate(items, 1):
                data = item.get('data', {})
                title = data.get('title', '无标题')
                item_type = data.get('itemType', 'unknown')
                creators = data.get('creators', [])
                authors = []
                for c in creators[:2]:  # 只显示前两个作者
                    if c.get('firstName') and c.get('lastName'):
                        authors.append(f"{c['firstName']} {c['lastName']}")
                    elif c.get('name'):
                        authors.append(c['name'])
                
                year = data.get('date', '')[:4] if data.get('date') else '无年份'
                
                print(f"{i}. [{item_type}] {title}")
                if authors:
                    print(f"   作者：{', '.join(authors)}")
                print(f"   年份：{year}")
                
                # 显示标签
                tags = data.get('tags', [])
                if tags:
                    tag_list = [t['tag'] for t in tags[:5]]
                    print(f"   标签：{', '.join(tag_list)}")
                
                print(f"   链接：https://www.zotero.org/{zot.library_id}/items/{item['key']}")
                print()
                
    except Exception as e:
        print(f"搜索失败：{e}", file=sys.stderr)
        sys.exit(1)


def list_collections(zot, json_output=False):
    """列出所有集合"""
    try:
        collections = zot.collections()
        
        if not collections:
            print("未找到任何集合。")
            return
        
        if json_output:
            print(json.dumps(collections, indent=2, ensure_ascii=False))
        else:
            print(f"共有 {len(collections)} 个集合:\n")
            for i, coll in enumerate(collections, 1):
                data = coll.get('data', {})
                name = data.get('name', '未命名')
                key = coll.get('key', '')
                parent = data.get('parentCollection', '')
                indent = "  " if parent else ""
                print(f"{i}. {indent}📁 {name}")
                print(f"   密钥：{key}")
                if parent:
                    print(f"   父集合：{parent}")
                print()
                
    except Exception as e:
        print(f"获取集合失败：{e}", file=sys.stderr)
        sys.exit(1)


def list_item_types(zot, json_output=False):
    """列出所有项目类型"""
    try:
        item_types = zot.item_types()
        
        if json_output:
            print(json.dumps(item_types, indent=2, ensure_ascii=False))
        else:
            print(f"共有 {len(item_types)} 种项目类型:\n")
            for i, it in enumerate(item_types, 1):
                print(f"{i}. {it['itemType']}")
                
    except Exception as e:
        print(f"获取项目类型失败：{e}", file=sys.stderr)
        sys.exit(1)


def get_item(zot, item_key, json_output=False):
    """获取单个项目详情"""
    try:
        item = zot.item(item_key)
        
        if not item:
            print("未找到该项目。")
            return
        
        if json_output:
            print(json.dumps(item, indent=2, ensure_ascii=False))
        else:
            data = item.get('data', {})
            print(f"标题：{data.get('title', '无标题')}")
            print(f"类型：{data.get('itemType', 'unknown')}")
            print(f"日期：{data.get('date', '无日期')}")
            
            creators = data.get('creators', [])
            if creators:
                print("\n作者/创作者:")
                for c in creators:
                    if c.get('firstName') and c.get('lastName'):
                        print(f"  - {c['firstName']} {c['lastName']} ({c.get('creatorType', 'Author')})")
                    elif c.get('name'):
                        print(f"  - {c['name']}")
            
            # 显示摘要
            if data.get('abstractNote'):
                print(f"\n摘要：{data['abstractNote'][:500]}")
            
            # 显示标签
            tags = data.get('tags', [])
            if tags:
                print(f"\n标签：{', '.join([t['tag'] for t in tags])}")
            
            # 显示附件
            attachments = zot.children(item_key)
            if attachments:
                print(f"\n附件 ({len(attachments)}):")
                for att in attachments[:5]:
                    att_data = att.get('data', {})
                    print(f"  - {att_data.get('title', '未命名')} ({att_data.get('itemType', 'unknown')})")
            
            print(f"\n链接：https://www.zotero.org/{zot.library_id}/items/{item_key}")
                
    except Exception as e:
        print(f"获取项目失败：{e}", file=sys.stderr)
        sys.exit(1)


def add_item(zot, item_data, json_output=False):
    """
    添加单个项目到 Zotero
    
    参数:
        zot: Zotero 实例
        item_data: 包含项目信息的字典，格式如下：
            {
                "itemType": "journalArticle",
                "title": "文章标题",
                "creators": [{"firstName": "First", "lastName": "Last", "creatorType": "author"}],
                "publicationTitle": "期刊名",
                "date": "2024",
                "DOI": "10.xxxx/xxxxx",
                "tags": [{"tag": "tag1", "type": 1}],
                "abstractNote": "摘要",
                "url": "网址"
            }
    """
    try:
        # 创建项目
        response = zot.create_items([item_data])
        
        if json_output:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print(f"✓ 成功添加：{item_data.get('title', '无标题')}")
            
            # 返回新项目的 key
            if response.get('success'):
                new_key = response['success'][0]
                print(f"  项目密钥：{new_key}")
                print(f"  链接：https://www.zotero.org/{zot.library_id}/items/{new_key}")
            
    except Exception as e:
        print(f"✗ 添加失败：{e}", file=sys.stderr)
        
        # 尝试使用 item_template 方法
        try:
            print("   尝试使用备用方法...", file=sys.stderr)
            
            # 获取模板
            template = zot.item_template(item_data['itemType'])
            
            # 更新模板数据
            for key, value in item_data.items():
                if key in template['data']:
                    template['data'][key] = value
            
            # 创建项目
            response = zot.create_items([template])
            
            if json_output:
                print(json.dumps(response, indent=2, ensure_ascii=False))
            else:
                print(f"✓ 备用方法成功：{item_data.get('title', '无标题')}")
                
        except Exception as e2:
            print(f"✗ 备用方法也失败：{e2}", file=sys.stderr)
            sys.exit(1)


def add_items_from_json(zot, json_file, json_output=False):
    """
    从 JSON 文件批量添加项目
    
    参数:
        zot: Zotero 实例
        json_file: JSON 文件路径，包含项目列表
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        if not isinstance(items, list):
            items = [items]
        
        print(f"准备添加 {len(items)} 个项目...\n")
        
        success_count = 0
        fail_count = 0
        
        for i, item_data in enumerate(items, 1):
            title_short = item_data.get('title', '无标题')[:50]
            try:
                add_item(zot, item_data, json_output=False)
                success_count += 1
            except Exception as e:
                print(f"✗ [{i}/{len(items)}] 失败：{title_short}... - {e}", file=sys.stderr)
                fail_count += 1
        
        print(f"\n{'='*60}")
        print(f"完成！成功添加 {success_count}/{len(items)} 个项目")
        if fail_count > 0:
            print(f"失败 {fail_count} 个")
        print(f"{'='*60}")
            
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON 文件格式不正确：{e}", file=sys.stderr)
        sys.exit(1)


def create_collection(zot, name, parent_key=None, json_output=False):
    """
    创建新集合
    
    参数:
        zot: Zotero 实例
        name: 集合名称
        parent_key: 父集合密钥（可选，用于创建子集合）
    """
    try:
        collection_data = {
            'name': name,
            'parentCollection': parent_key if parent_key else ''
        }
        
        response = zot.create_collections([collection_data])
        
        if json_output:
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            # 响应格式：{'successful': {'0': {...}}, 'success': {'0': 'KEY'}}
            if isinstance(response, dict):
                if response.get('success'):
                    # 获取第一个成功的密钥
                    success_keys = list(response['success'].values())
                    if success_keys:
                        new_key = success_keys[0]
                        print(f"✓ 成功创建集合：{name}")
                        print(f"  集合密钥：{new_key}")
                        if parent_key:
                            print(f"  父集合：{parent_key}")
                elif response.get('successful'):
                    # 另一种响应格式
                    success_data = list(response['successful'].values())[0]
                    new_key = success_data.get('key', 'unknown')
                    print(f"✓ 成功创建集合：{name}")
                    print(f"  集合密钥：{new_key}")
                else:
                    print(f"✗ 创建失败：{response}")
            else:
                print(f"✓ 成功创建集合：{name}")
                
    except Exception as e:
        print(f"✗ 创建集合失败：{e}", file=sys.stderr)
        sys.exit(1)


def delete_collection(zot, collection_key, confirm=False):
    """
    删除集合
    
    参数:
        zot: Zotero 实例
        collection_key: 集合密钥
        confirm: 是否需要确认
    """
    try:
        import requests
        
        # 获取集合信息（包括版本）
        collections = zot.collections()
        coll = None
        for c in collections:
            if c['key'] == collection_key:
                coll = c
                break
        
        if not coll:
            print(f"✗ 找不到集合：{collection_key}", file=sys.stderr)
            sys.exit(1)
        
        name = coll['data'].get('name', '未知')
        version = coll['data'].get('version', 0)
        
        if not confirm:
            print(f"⚠️  警告：即将删除集合 '{name}' ({collection_key})")
            print(f"   此操作不可恢复！")
            response = input("确认删除？(y/N): ")
            if response.lower() != 'y':
                print("已取消删除。")
                return
        
        # 使用 requests 直接调用 API 删除
        user_id = zot.library_id
        api_key = zot.api_key
        url = f'https://api.zotero.org/users/{user_id}/collections/{collection_key}'
        
        headers = {
            'Zotero-API-Key': api_key,
            'If-Unmodified-Since-Version': str(version)
        }
        
        resp = requests.delete(url, headers=headers)
        
        if resp.status_code == 204:
            print(f"✓ 成功删除集合：{name}")
        else:
            print(f"✗ 删除失败：HTTP {resp.status_code} - {resp.text}")
            sys.exit(1)
        
    except Exception as e:
        print(f"✗ 删除集合失败：{e}", file=sys.stderr)
        sys.exit(1)


def rename_collection(zot, collection_key, new_name):
    """
    重命名集合
    
    参数:
        zot: Zotero 实例
        collection_key: 集合密钥
        new_name: 新名称
    """
    try:
        # 获取所有集合并查找
        collections = zot.collections()
        coll = None
        for c in collections:
            if c['key'] == collection_key:
                coll = c
                break
        
        if not coll:
            print(f"✗ 找不到集合：{collection_key}", file=sys.stderr)
            sys.exit(1)
        
        old_name = coll['data'].get('name', '未知')
        
        # 使用 create_collections 进行更新（需要 key 和 version）
        update_data = {
            'key': collection_key,
            'name': new_name,
            'version': coll['data']['version']
        }
        
        zot.create_collections([update_data])
        
        print(f"✓ 成功重命名：'{old_name}' → '{new_name}'")
        
    except Exception as e:
        print(f"✗ 重命名集合失败：{e}", file=sys.stderr)
        sys.exit(1)


def add_item_to_collection(zot, item_key, collection_key):
    """
    添加项目到集合
    
    参数:
        zot: Zotero 实例
        item_key: 项目密钥
        collection_key: 集合密钥
    """
    try:
        # 获取项目当前集合
        item = zot.item(item_key)
        collections = item['data'].get('collections', [])
        
        if collection_key not in collections:
            collections.append(collection_key)
            item['data']['collections'] = collections
            zot.update_item(item)
            
            # 获取集合名称
            coll = zot.collection(collection_key)
            coll_name = coll['data'].get('name', '未知')
            
            print(f"✓ 成功添加项目到集合：{coll_name}")
        else:
            print(f"ℹ️  项目已在该集合中")
        
    except Exception as e:
        print(f"✗ 添加项目失败：{e}", file=sys.stderr)
        sys.exit(1)


def remove_item_from_collection(zot, item_key, collection_key):
    """
    从集合移除项目
    
    参数:
        zot: Zotero 实例
        item_key: 项目密钥
        collection_key: 集合密钥
    """
    try:
        item = zot.item(item_key)
        collections = item['data'].get('collections', [])
        
        if collection_key in collections:
            collections.remove(collection_key)
            item['data']['collections'] = collections
            zot.update_item(item)
            
            coll = zot.collection(collection_key)
            coll_name = coll['data'].get('name', '未知')
            
            print(f"✓ 成功从集合移除：{coll_name}")
        else:
            print(f"ℹ️  项目不在该集合中")
        
    except Exception as e:
        print(f"✗ 移除项目失败：{e}", file=sys.stderr)
        sys.exit(1)


def list_collection_items(zot, collection_key, limit=20, json_output=False):
    """
    列出集合中的所有项目
    
    参数:
        zot: Zotero 实例
        collection_key: 集合密钥
        limit: 结果数量限制
        json_output: 是否输出 JSON
    """
    try:
        # 获取集合信息
        coll = zot.collection(collection_key)
        coll_name = coll['data'].get('name', '未知')
        
        # 获取集合中的项目
        items = zot.collection_items(collection_key, limit=limit)
        
        if not items:
            print(f"集合 '{coll_name}' 中没有项目。")
            return
        
        if json_output:
            print(json.dumps(items, indent=2, ensure_ascii=False))
        else:
            print(f"📁 集合：{coll_name} ({len(items)} 个项目)\n")
            for i, item in enumerate(items, 1):
                data = item.get('data', {})
                title = data.get('title', '无标题')
                item_type = data.get('itemType', 'unknown')
                creators = data.get('creators', [])
                
                authors = []
                for c in creators[:2]:
                    if c.get('firstName') and c.get('lastName'):
                        authors.append(f"{c['firstName']} {c['lastName']}")
                    elif c.get('name'):
                        authors.append(c['name'])
                
                year = data.get('date', '')[:4] if data.get('date') else ''
                
                print(f"{i}. [{item_type}] {title}")
                if authors:
                    print(f"   作者：{', '.join(authors)}")
                if year:
                    print(f"   年份：{year}")
                print()
                
    except Exception as e:
        print(f"✗ 获取集合项目失败：{e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='PyZotero Python 脚本 - Zotero 库管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量:
  ZOTERO_LOCAL     "true" 或 "false" (默认："true")
                   - true: 使用本地 Zotero API
                   - false: 使用 Zotero 在线 Web API
  
  ZOTERO_USER_ID   (在线模式必需) 您的 Zotero 用户 ID
  ZOTERO_API_KEY   (在线模式必需) 您的 Zotero API Key

可用命令:
  search           搜索 Zotero 库
  listcollections  列出所有集合
  itemtypes        列出所有项目类型
  item             获取单个项目详情
  add              添加单个项目到 Zotero
  add-from-json    从 JSON 文件批量添加项目

示例:
  # 搜索
  python3 pyzotero.py search -q "machine learning"
  python3 pyzotero.py search -q "neural networks" --fulltext
  python3 pyzotero.py search -q "python" --itemtype journalArticle --json
  
  # 浏览
  python3 pyzotero.py listcollections
  python3 pyzotero.py itemtypes
  
  # 获取详情
  python3 pyzotero.py item ABC123
  
  # 添加单个项目
  python3 pyzotero.py add -t "文章标题" -a "FirstName LastName" -p "期刊名" -d "2024" --doi "10.xxxx/xxxxx"
  python3 pyzotero.py add -t "Python 文献" --tags ophthalmology python AI
  
  # 从 JSON 批量添加
  python3 pyzotero.py add-from-json papers.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索 Zotero 库')
    search_parser.add_argument('-q', '--query', required=True, help='搜索关键词')
    search_parser.add_argument('--fulltext', action='store_true', help='全文搜索 (包括 PDF)')
    search_parser.add_argument('--itemtype', help='按项目类型过滤')
    search_parser.add_argument('--collection', help='在特定集合中搜索')
    search_parser.add_argument('-l', '--limit', type=int, default=20, help='结果数量限制 (默认：20)')
    search_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # listcollections 命令
    lc_parser = subparsers.add_parser('listcollections', help='列出所有集合')
    lc_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # itemtypes 命令
    it_parser = subparsers.add_parser('itemtypes', help='列出所有项目类型')
    it_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # item 命令
    item_parser = subparsers.add_parser('item', help='获取单个项目详情')
    item_parser.add_argument('item_key', help='项目密钥 (key)')
    item_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # add 命令 - 添加单个项目
    add_parser = subparsers.add_parser('add', help='添加单个项目到 Zotero')
    add_parser.add_argument('--type', dest='itemtype', default='journalArticle', 
                           help='项目类型 (默认：journalArticle)')
    add_parser.add_argument('-t', '--title', required=True, help='标题')
    add_parser.add_argument('-a', '--authors', nargs='+', help='作者列表 (格式：FirstName LastName)')
    add_parser.add_argument('-p', '--publication', help='期刊/出版物名称')
    add_parser.add_argument('-d', '--date', help='发表日期 (格式：YYYY 或 YYYY-MM-DD)')
    add_parser.add_argument('--doi', help='DOI 号')
    add_parser.add_argument('--url', help='URL 链接')
    add_parser.add_argument('--abstract', help='摘要')
    add_parser.add_argument('--tags', nargs='+', help='标签列表')
    add_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # add-from-json 命令 - 从 JSON 文件批量添加
    addjson_parser = subparsers.add_parser('add-from-json', help='从 JSON 文件批量添加项目')
    addjson_parser.add_argument('json_file', help='JSON 文件路径')
    addjson_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # collection-create 命令 - 创建集合
    coll_create_parser = subparsers.add_parser('collection-create', help='创建新集合')
    coll_create_parser.add_argument('-n', '--name', required=True, help='集合名称')
    coll_create_parser.add_argument('-p', '--parent', help='父集合密钥（创建子集合）')
    coll_create_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    # collection-delete 命令 - 删除集合
    coll_del_parser = subparsers.add_parser('collection-delete', help='删除集合')
    coll_del_parser.add_argument('collection_key', help='集合密钥')
    coll_del_parser.add_argument('-y', '--yes', action='store_true', dest='confirm', help='确认删除（跳过提示）')
    
    # collection-rename 命令 - 重命名集合
    coll_rename_parser = subparsers.add_parser('collection-rename', help='重命名集合')
    coll_rename_parser.add_argument('collection_key', help='集合密钥')
    coll_rename_parser.add_argument('-n', '--name', required=True, help='新名称')
    
    # collection-add-item 命令 - 添加项目到集合
    coll_add_parser = subparsers.add_parser('collection-add-item', help='添加项目到集合')
    coll_add_parser.add_argument('item_key', help='项目密钥')
    coll_add_parser.add_argument('-c', '--collection', required=True, help='集合密钥')
    
    # collection-remove-item 命令 - 从集合移除项目
    coll_remove_parser = subparsers.add_parser('collection-remove-item', help='从集合移除项目')
    coll_remove_parser.add_argument('item_key', help='项目密钥')
    coll_remove_parser.add_argument('-c', '--collection', required=True, help='集合密钥')
    
    # collection-list 命令 - 列出集合中的项目
    coll_list_parser = subparsers.add_parser('collection-list', help='列出集合中的项目')
    coll_list_parser.add_argument('collection_key', help='集合密钥')
    coll_list_parser.add_argument('-l', '--limit', type=int, default=20, help='结果数量限制')
    coll_list_parser.add_argument('--json', action='store_true', dest='json_output', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 获取 Zotero 实例
    zot = get_zotero_instance()
    
    # 执行命令
    if args.command == 'search':
        search_items(
            zot, 
            args.query, 
            fulltext=args.fulltext,
            itemtype=args.itemtype,
            collection=args.collection,
            limit=args.limit,
            json_output=args.json_output
        )
    elif args.command == 'listcollections':
        list_collections(zot, json_output=args.json_output)
    elif args.command == 'itemtypes':
        list_item_types(zot, json_output=args.json_output)
    elif args.command == 'item':
        get_item(zot, args.item_key, json_output=args.json_output)
    elif args.command == 'add':
        # 构建项目数据
        item_data = {
            "itemType": args.itemtype,
            "title": args.title
        }
        
        # 添加作者
        if args.authors:
            creators = []
            for author in args.authors:
                parts = author.split(' ', 1)
                if len(parts) == 2:
                    creators.append({"firstName": parts[0], "lastName": parts[1], "creatorType": "author"})
                else:
                    creators.append({"name": parts[0], "creatorType": "author"})
            item_data["creators"] = creators
        
        # 添加其他字段
        if args.publication:
            item_data["publicationTitle"] = args.publication
        if args.date:
            item_data["date"] = args.date
        if args.doi:
            item_data["DOI"] = args.doi
        if args.url:
            item_data["url"] = args.url
        if args.abstract:
            item_data["abstractNote"] = args.abstract
        if args.tags:
            item_data["tags"] = [{"tag": tag, "type": 1} for tag in args.tags]
        
        add_item(zot, item_data, json_output=args.json_output)
    
    elif args.command == 'add-from-json':
        add_items_from_json(zot, args.json_file, json_output=args.json_output)
    
    elif args.command == 'collection-create':
        create_collection(zot, args.name, parent_key=args.parent, json_output=args.json_output)
    
    elif args.command == 'collection-delete':
        delete_collection(zot, args.collection_key, confirm=args.confirm)
    
    elif args.command == 'collection-rename':
        rename_collection(zot, args.collection_key, args.name)
    
    elif args.command == 'collection-add-item':
        add_item_to_collection(zot, args.item_key, args.collection)
    
    elif args.command == 'collection-remove-item':
        remove_item_from_collection(zot, args.item_key, args.collection)
    
    elif args.command == 'collection-list':
        list_collection_items(zot, args.collection_key, limit=args.limit, json_output=args.json_output)


if __name__ == '__main__':
    main()
