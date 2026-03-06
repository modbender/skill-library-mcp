#!/usr/bin/env python3
"""
Memory Manager - 三级记忆管理系统
Three-Tier Memory Management System

Usage:
    python3 memory_manager.py init                    # 初始化记忆系统
    python3 memory_manager.py add --type short --content "内容"   # 添加短期记忆
    python3 memory_manager.py add --type medium --content "内容"  # 添加中期记忆
    python3 memory_manager.py add --type long --content "内容"   # 添加长期记忆
    python3 memory_manager.py search "查询内容"       # 搜索长期记忆
    python3 memory_manager.py summary                # 手动触发摘要
    python3 memory_manager.py status                 # 查看记忆状态
    python3 memory_manager.py window                  # 查看短期记忆窗口
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 配置路径
WORKSPACE_DIR = Path(os.environ.get('WORKSPACE_DIR', '/Users/scott/.openclaw/workspace'))
MEMORY_DIR = WORKSPACE_DIR / 'memory'
CONFIG_FILE = MEMORY_DIR / 'config.yaml'
SLIDING_WINDOW_FILE = MEMORY_DIR / 'sliding-window.json'
SUMMARIES_DIR = MEMORY_DIR / 'summaries'
VECTOR_STORE_DIR = MEMORY_DIR / 'vector-store'

# 默认配置
DEFAULT_CONFIG = {
    'memory': {
        'short_term': {
            'enabled': True,
            'window_size': 10,
            'max_tokens': 2000
        },
        'medium_term': {
            'enabled': True,
            'summary_threshold': 4000,
            'summary_model': 'glm-4-flash'
        },
        'long_term': {
            'enabled': True,
            'backend': 'chromadb',
            'top_k': 3,
            'min_relevance': 0.7
        }
    }
}


def ensure_dirs():
    """确保必要的目录存在"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """加载配置文件"""
    config_json = CONFIG_FILE.with_suffix('.json')
    if config_json.exists():
        with open(config_json, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG


def save_config(config: dict):
    """保存配置文件"""
    # 使用 JSON 而非 YAML，减少依赖
    config_json = CONFIG_FILE.with_suffix('.json')
    with open(config_json, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✓ 已保存配置: {config_json}")


def init_memory_system():
    """初始化记忆系统"""
    ensure_dirs()
    
    # 创建配置文件
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        print(f"✓ 已创建配置文件: {CONFIG_FILE}")
    
    # 创建短期记忆文件
    if not SLIDING_WINDOW_FILE.exists():
        with open(SLIDING_WINDOW_FILE, 'w') as f:
            json.dump({'messages': [], 'updated_at': datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
        print(f"✓ 已创建短期记忆: {SLIDING_WINDOW_FILE}")
    
    print(f"✓ 记忆系统初始化完成")
    print(f"  短期记忆: {SLIDING_WINDOW_FILE}")
    print(f"  中期记忆: {SUMMARIES_DIR}")
    print(f"  长期记忆: {VECTOR_STORE_DIR}")
    return True


def add_short_term_memory(content: str, metadata: dict = None):
    """添加短期记忆（滑动窗口）"""
    config = load_config()
    window_size = config['memory']['short_term']['window_size']
    
    with open(SLIDING_WINDOW_FILE, 'r') as f:
        data = json.load(f)
    
    messages = data.get('messages', [])
    
    # 添加新消息
    new_message = {
        'content': content,
        'timestamp': datetime.now().isoformat(),
        'metadata': metadata or {}
    }
    messages.append(new_message)
    
    # 滑动窗口：保持最近 N 条
    if len(messages) > window_size:
        messages = messages[-window_size:]
    
    data['messages'] = messages
    data['updated_at'] = datetime.now().isoformat()
    
    with open(SLIDING_WINDOW_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已添加短期记忆，当前窗口: {len(messages)}/{window_size}")
    return True


def get_short_term_memory() -> list:
    """获取短期记忆"""
    if not SLIDING_WINDOW_FILE.exists():
        return []
    with open(SLIDING_WINDOW_FILE, 'r') as f:
        data = json.load(f)
    return data.get('messages', [])


def add_medium_term_memory(content: str, summary_type: str = 'auto'):
    """添加中期记忆（摘要）"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    summary_file = SUMMARIES_DIR / f'{date_str}.json'
    
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            data = json.load(f)
    else:
        data = {'summaries': [], 'date': date_str}
    
    new_summary = {
        'content': content,
        'type': summary_type,
        'timestamp': datetime.now().isoformat()
    }
    data['summaries'].append(new_summary)
    
    with open(summary_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 已添加中期记忆: {summary_file}")
    return True


def get_medium_term_memory(days: int = 7) -> list:
    """获取中期记忆（最近 N 天）"""
    summaries = []
    cutoff = datetime.now().timestamp() - (days * 24 * 3600)
    
    for f in SUMMARIES_DIR.glob('*.json'):
        if f.stat().st_mtime > cutoff:
            with open(f, 'r') as fp:
                data = json.load(fp)
                summaries.extend(data.get('summaries', []))
    
    return summaries


def init_vector_store():
    """初始化向量存储"""
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        print("✗ 需要安装 chromadb: pip install chromadb")
        return False
    
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    
    # 创建或获取集合
    try:
        collection = client.get_collection("memory")
    except:
        collection = client.create_collection("memory", metadata={"description": "Long-term memory store"})
    
    return client, collection


def add_long_term_memory(content: str, metadata: dict = None):
    """添加长期记忆（向量存储）"""
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        print("✗ 需要安装 chromadb: pip install chromadb")
        return False
    
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    
    try:
        collection = client.get_collection("memory")
    except:
        collection = client.create_collection("memory")
    
    # 生成 ID
    memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # 添加到向量库（这里用内容本身作为 metadata，实际生产环境需要 embedding）
    collection.add(
        documents=[content],
        ids=[memory_id],
        metadatas=[metadata or {'timestamp': datetime.now().isoformat()}]
    )
    
    print(f"✓ 已添加长期记忆: {memory_id}")
    return True


def search_long_term_memory(query: str, top_k: int = 3) -> list:
    """搜索长期记忆"""
    try:
        import chromadb
    except ImportError:
        print("✗ 需要安装 chromadb: pip install chromadb")
        return []
    
    client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
    
    try:
        collection = client.get_collection("memory")
    except:
        return []
    
    # 搜索
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    memories = []
    if results and results.get('documents'):
        for i, doc in enumerate(results['documents'][0]):
            memories.append({
                'content': doc,
                'id': results['ids'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
    
    return memories


def generate_summary(messages: list) -> str:
    """
    生成摘要（调用 LLM - 使用 GLM-4 Flash）
    """
    if not messages:
        return ""
    
    # 构建对话内容
    conversation_text = "\n".join([
        f"用户: {m.get('content', '')}" 
        for m in messages
    ])
    
    # 构建 prompt
    prompt = f"""请简要总结以下对话的关键信息，包括：
1. 用户的主要意图或问题
2. 达成的事实或结论
3. 任何需要记住的用户偏好或设置

对话内容：
{conversation_text}

请用 50-100 字总结要点："""
    
    # 调用 LLM API（使用 urllib，内置模块）
    try:
        import urllib.request
        import urllib.error
        import json
        
        # 从配置文件读取 API key
        api_key = ''
        config_path = Path.home() / '.openclaw' / 'openclaw.json'
        
        if config_path.exists():
            with open(config_path) as f:
                oc_config = json.load(f)
                # 查找 zhipu API key（在 providers 下）
                providers = oc_config.get('models', {}).get('providers', {})
                zhipu_cfg = providers.get('zhipu', {})
                if zhipu_cfg.get('apiKey'):
                    api_key = zhipu_cfg['apiKey']
        
        if not api_key:
            print("⚠ 未找到 API Key，使用简单总结")
            raise Exception("No API key")
        
        # 使用 GLM-4 Flash
        api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "glm-4-flash",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.7
        }
        
        req = urllib.request.Request(
            api_url, 
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            summary = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            if summary:
                print(f"✓ LLM 摘要生成成功")
                return summary
        
    except Exception as e:
        print(f"⚠ LLM API 调用失败: {e}")
    
    # 如果 API 调用失败，使用简单总结
    content_preview = "\n".join([m.get('content', '')[:100] for m in messages])
    summary = f"[自动摘要] {len(messages)} 条消息的总结。预览: {content_preview[:200]}..."
    
    return summary


def trigger_summary():
    """手动触发摘要"""
    config = load_config()
    
    if not config['memory']['medium_term']['enabled']:
        print("✗ 中期记忆未启用")
        return False
    
    # 获取短期记忆
    short_memories = get_short_term_memory()
    
    if not short_memories:
        print("没有需要摘要的短期记忆")
        return True
    
    # 生成摘要
    summary = generate_summary(short_memories)
    
    # 存储为中期记忆
    add_medium_term_memory(summary, 'auto-summary')
    
    # 清空短期记忆（可选）
    with open(SLIDING_WINDOW_FILE, 'w') as f:
        json.dump({'messages': [], 'updated_at': datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 摘要生成完成，已归档 {len(short_memories)} 条短期记忆")
    return True


def show_status():
    """显示记忆状态"""
    config = load_config()
    
    print("\n=== 记忆系统状态 ===\n")
    
    # 短期记忆
    short_memories = get_short_term_memory()
    window_size = config['memory']['short_term']['window_size']
    print(f"📝 短期记忆: {len(short_memories)}/{window_size} 条")
    if short_memories:
        latest = short_memories[-1]
        print(f"   最新: {latest.get('content', '')[:50]}...")
    
    # 中期记忆
    medium_memories = get_medium_term_memory()
    print(f"\n📋 中期记忆: {len(medium_memories)} 条 (最近7天)")
    
    # 长期记忆
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
        collection = client.get_collection("memory")
        long_count = collection.count()
        print(f"\n🧠 长期记忆: {long_count} 条")
    except:
        print(f"\n🧠 长期记忆: 0 条")
    
    print()
    return True


def show_window():
    """显示短期记忆窗口"""
    messages = get_short_term_memory()
    
    if not messages:
        print("短期记忆为空")
        return True
    
    print(f"\n=== 短期记忆窗口 ({len(messages)} 条) ===\n")
    for i, msg in enumerate(messages):
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', '')
        preview = content[:80] + '...' if len(content) > 80 else content
        print(f"{i+1}. [{timestamp[:19]}] {preview}")
    
    print()
    return True


def main():
    parser = argparse.ArgumentParser(description='Memory Manager - 三级记忆管理系统')
    parser.add_argument('command', choices=['init', 'add', 'search', 'summary', 'status', 'window'],
                        help='命令')
    parser.add_argument('--type', choices=['short', 'medium', 'long'], default='short',
                        help='记忆类型')
    parser.add_argument('--content', '-c', type=str,
                        help='记忆内容')
    parser.add_argument('--query', '-q', type=str,
                        help='搜索查询')
    parser.add_argument('--top-k', type=int, default=3,
                        help='返回结果数量')
    parser.add_argument('--days', type=int, default=7,
                        help='查询天数（中期记忆）')
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    if args.command == 'init':
        return init_memory_system()
    
    elif args.command == 'add':
        if not args.content:
            print("✗ 需要指定 --content")
            return False
        
        if args.type == 'short':
            return add_short_term_memory(args.content)
        elif args.type == 'medium':
            return add_medium_term_memory(args.content)
        elif args.type == 'long':
            return add_long_term_memory(args.content)
    
    elif args.command == 'search':
        if not args.query:
            print("✗ 需要指定 --query")
            return False
        
        results = search_long_term_memory(args.query, args.top_k)
        
        if not results:
            print("未找到相关记忆")
            return True
        
        print(f"\n=== 搜索结果 ({len(results)} 条) ===\n")
        for i, r in enumerate(results):
            dist_info = f" (相似度: {1-r['distance']:.2f})" if r.get('distance') else ""
            print(f"{i+1}.{dist_info}")
            print(f"   {r['content'][:200]}...")
            print()
        
        return True
    
    elif args.command == 'summary':
        return trigger_summary()
    
    elif args.command == 'status':
        return show_status()
    
    elif args.command == 'window':
        return show_window()
    
    return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
