#!/usr/bin/env python3
"""
本地记忆搜索 - 基于 Ollama（无 ChromaDB 依赖）
用法: 
  python memory_search_simple.py --build     # 构建索引
  python memory_search_simple.py "查询内容"  # 搜索
"""

import os
import sys
import glob
import json
import math
import subprocess

# 配置
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
MEMORY_PATHS = [
    f"{WORKSPACE}/MEMORY.md",
    f"{WORKSPACE}/memory/*.md",
    f"{WORKSPACE}/knowledge/**/*.md",
]
INDEX_PATH = os.path.expanduser("~/.openclaw/memory_index.json")
EMBEDDING_MODEL = "nomic-embed-text"

def get_all_files():
    """获取所有记忆文件"""
    files = []
    for pattern in MEMORY_PATHS:
        files.extend(glob.glob(pattern, recursive=True))
    return [f for f in files if os.path.isfile(f)]

def chunk_file(filepath, chunk_size=500):
    """将文件分块"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    current_size = 0
    start_line = 1
    
    for i, line in enumerate(lines, 1):
        current_chunk.append(line)
        current_size += len(line)
        
        if current_size >= chunk_size:
            text = '\n'.join(current_chunk).strip()
            if text:
                chunks.append({
                    'text': text,
                    'file': filepath,
                    'start_line': start_line,
                    'end_line': i
                })
            current_chunk = []
            current_size = 0
            start_line = i + 1
    
    if current_chunk:
        text = '\n'.join(current_chunk).strip()
        if text:
            chunks.append({
                'text': text,
                'file': filepath,
                'start_line': start_line,
                'end_line': len(lines)
            })
    
    return chunks

def get_embedding(text):
    """通过 ollama CLI 获取 embedding"""
    result = subprocess.run(
        ['ollama', 'embed', EMBEDDING_MODEL, text],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # 备用方案：用 API
        import urllib.request
        import json as json_lib
        data = json_lib.dumps({"model": EMBEDDING_MODEL, "input": text}).encode()
        req = urllib.request.Request(
            "http://localhost:11434/api/embed",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            result = json_lib.loads(resp.read())
            return result['embeddings'][0]
    return json.loads(result.stdout)['embeddings'][0]

def cosine_similarity(a, b):
    """计算余弦相似度（纯 Python）"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot / (norm_a * norm_b)

def build_index():
    """构建索引"""
    print("构建记忆索引...")
    
    files = get_all_files()
    print(f"找到 {len(files)} 个文件")
    
    all_chunks = []
    for f in files:
        chunks = chunk_file(f)
        all_chunks.extend(chunks)
    
    print(f"共 {len(all_chunks)} 个文本块")
    
    index = []
    for i, chunk in enumerate(all_chunks):
        try:
            embedding = get_embedding(chunk['text'][:1000])  # 限制长度
            index.append({
                'text': chunk['text'],
                'file': chunk['file'],
                'start_line': chunk['start_line'],
                'end_line': chunk['end_line'],
                'embedding': embedding
            })
            if (i + 1) % 10 == 0:
                print(f"已处理 {i + 1}/{len(all_chunks)}")
        except Exception as e:
            print(f"跳过块 {i}: {e}")
    
    with open(INDEX_PATH, 'w') as f:
        json.dump(index, f)
    
    print(f"索引构建完成！保存到 {INDEX_PATH}")
    print(f"索引大小: {os.path.getsize(INDEX_PATH) / 1024 / 1024:.1f} MB")

def search(query, top_k=5):
    """搜索记忆"""
    if not os.path.exists(INDEX_PATH):
        print("索引不存在，请先运行: python memory_search_simple.py --build")
        return []
    
    with open(INDEX_PATH, 'r') as f:
        index = json.load(f)
    
    query_embedding = get_embedding(query)
    
    results = []
    for item in index:
        score = cosine_similarity(query_embedding, item['embedding'])
        results.append({
            'text': item['text'],
            'file': item['file'],
            'start_line': item['start_line'],
            'end_line': item['end_line'],
            'score': score
        })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python memory_search_simple.py --build     # 构建索引")
        print("  python memory_search_simple.py '查询内容'  # 搜索")
        return
    
    if sys.argv[1] == '--build':
        build_index()
        return
    
    query = ' '.join(sys.argv[1:])
    results = search(query)
    
    if not results:
        print("未找到相关记忆")
        return
    
    print(f"\n🔍 搜索: {query}\n")
    print("=" * 60)
    
    for i, r in enumerate(results):
        rel_path = r['file'].replace(WORKSPACE + '/', '')
        print(f"\n[{i+1}] 相似度: {r['score']:.3f}")
        print(f"    来源: {rel_path}#{r['start_line']}-{r['end_line']}")
        preview = r['text'][:200].replace('\n', ' ')
        print(f"    内容: {preview}...")

if __name__ == "__main__":
    main()
