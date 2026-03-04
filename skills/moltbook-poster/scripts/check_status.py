#!/usr/bin/env python3
"""
Moltbook 状态检查工具
用法: python check_status.py
"""

import json
import time

WORKSPACE = r'C:\Users\10405\.openclaw\workspace'
CONFIG_FILE = WORKSPACE + r'\configs\moltbook.json'
POST_HISTORY_FILE = WORKSPACE + r'\configs\moltbook-post.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_headers(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

def check_agent_status(headers):
    """检查账号状态"""
    import requests
    
    r = requests.get(
        'https://www.moltbook.com/api/v1/agents/status',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'检查失败: {r.status_code}'}
    
    data = r.json()
    
    return {
        'success': True,
        'status': data.get('status', 'unknown'),
        'agent_name': data.get('agent', {}).get('name', 'unknown'),
        'claimed_at': data.get('agent', {}).get('claimed_at', '')
    }

def get_recent_posts(headers, limit=10):
    """获取最近帖子"""
    import requests
    
    r = requests.get(
        f'https://www.moltbook.com/api/v1/posts/me?limit={limit}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取帖子失败: {r.status_code}'}
    
    posts = r.json().get('posts', [])
    
    result = {
        'success': True,
        'count': len(posts),
        'posts': []
    }
    
    now = time.time()
    
    for p in posts:
        created = p.get('created_at', '')
        age_seconds = 0
        
        if created:
            try:
                ts = time.mktime(time.strptime(created, '%Y-%m-%dT%H:%M:%S+00:00'))
                age_seconds = now - ts
            except:
                pass
        
        result['posts'].append({
            'id': p.get('id', '')[:8],
            'title': p.get('title', 'Untitled')[:40],
            'created_at': created,
            'age_minutes': int(age_seconds / 60) if age_seconds > 0 else 0,
            'upvotes': p.get('upvotes', 0)
        })
    
    return result

def check_rate_limit_status(headers):
    """检查 rate limit 状态"""
    posts = get_recent_posts(headers, limit=10)
    
    if not posts['success']:
        return {'can_post': True, 'wait_minutes': 0}
    
    # 检查最近1小时内的帖子数
    recent_posts = [p for p in posts.get('posts', []) if p.get('age_minutes', 9999) < 60]
    
    if len(recent_posts) >= 1:
        # 计算距离下一篇文章的时间
        oldest_recent = min(recent_posts, key=lambda x: x.get('age_minutes', 0))
        wait_minutes = max(0, 31 - oldest_recent.get('age_minutes', 0))
        return {
            'can_post': False,
            'wait_minutes': wait_minutes,
            'recent_posts': len(recent_posts),
            'last_post_age': oldest_recent.get('age_minutes', 0)
        }
    
    return {'can_post': True, 'wait_minutes': 0, 'recent_posts': len(recent_posts)}

def main():
    print("=" * 60)
    print("  Moltbook 状态检查")
    print("=" * 60)
    
    config = load_config()
    headers = get_headers(config['api_key'])
    
    # 检查账号状态
    print("\n📋 账号状态...")
    agent_status = check_agent_status(headers)
    
    if agent_status['success']:
        status_icon = "✅" if agent_status['status'] == 'claimed' else "❓"
        print(f"   {status_icon} 状态: {agent_status['status']}")
        print(f"   🤖 代理名: {agent_status['agent_name']}")
        
        if agent_status['status'] != 'claimed':
            print("   ⚠️  提示: 账号尚未被认领，请提醒主人完成认领！")
    else:
        print(f"   ❌ 检查失败: {agent_status.get('error')}")
    
    # 检查 rate limit
    print("\n⏱️  Rate Limit...")
    rate_status = check_rate_limit_status(headers)
    
    if rate_status.get('can_post'):
        print(f"   ✅ 可以发帖")
        print(f"   📊 最近1小时帖子: {rate_status.get('recent_posts', 0)}")
    else:
        wait = rate_status.get('wait_minutes', 0)
        print(f"   ❌ Rate limited")
        print(f"   ⏰ 需要等待: {wait} 分钟")
        print(f"   📊 最近1小时帖子: {rate_status.get('recent_posts', 0)}")
    
    # 获取最近帖子
    print("\n📝 最近帖子:")
    posts = get_recent_posts(headers, limit=5)
    
    if posts['success'] and posts.get('posts'):
        for p in posts.get('posts', []):
            age = p.get('age_minutes', 0)
            if age < 60:
                age_str = f"{age}分钟前"
            elif age < 1440:
                age_str = f"{age // 60}小时前"
            else:
                age_str = f"{age // 1440}天前"
            
            print(f"   • {p['title'][:35]}...")
            print(f"     [{p['id']}] {age_str} | 👍 {p['upvotes']}")
    else:
        print("   (暂无帖子)")
    
    # 建议操作
    print("\n💡 建议操作:")
    if agent_status['status'] != 'claimed':
        print("   1. 完成账号认领")
    elif not rate_status.get('can_post'):
        print(f"   1. 等待 {rate_status.get('wait_minutes')} 分钟后发帖")
        print("   2. 可以先浏览动态、参与评论")
    else:
        print("   1. 发帖分享你的想法")
        print("   2. 浏览动态，发现有趣内容")
        print("   3. 点赞和评论其他帖子")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
