#!/usr/bin/env python3
"""
Moltbook 私信管理工具
用法: python dm.py [--check] [--unread] [--conversations] [--requests]
                 [--approve ID] [--reject ID]
                 [--send "目标代理名" "内容"]
"""

import argparse
import json
import sys

WORKSPACE = r'C:\Users\10405\.openclaw\workspace'
CONFIG_FILE = WORKSPACE + r'\configs\moltbook.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_headers(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

def check_dm_status(headers):
    """检查私信状态"""
    import requests
    
    r = requests.get(
        'https://www.moltbook.com/api/v1/agents/dm/check',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'检查失败: {r.status_code}'}
    
    data = r.json()
    
    result = {
        'success': True,
        'pending_requests': data.get('pending_requests', 0),
        'unread_count': data.get('unread_count', 0)
    }
    
    return result

def list_requests(headers):
    """列出待处理请求"""
    import requests
    
    r = requests.get(
        'https://www.moltbook.com/api/v1/agents/dm/requests',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取请求列表失败: {r.status_code}'}
    
    requests_list = r.json().get('requests', [])
    
    result = {
        'success': True,
        'count': len(requests_list),
        'requests': []
    }
    
    for req in requests_list:
        result['requests'].append({
            'id': req.get('id', '')[:8],
            'from': req.get('from', {}).get('name', 'unknown'),
            'message': req.get('message', '')[:100],
            'created_at': req.get('created_at', '')
        })
    
    return result

def list_conversations(headers):
    """列出私信会话"""
    import requests
    
    r = requests.get(
        'https://www.moltbook.com/api/v1/agents/dm/conversations',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取会话列表失败: {r.status_code}'}
    
    convos = r.json().get('conversations', [])
    
    result = {
        'success': True,
        'count': len(convos),
        'conversations': []
    }
    
    for c in convos:
        result['conversations'].append({
            'id': c.get('id', '')[:8],
            'with': c.get('with', {}).get('name', 'unknown'),
            'last_message': c.get('last_message', {}).get('content', '')[:50],
            'unread': c.get('unread', False),
            'needs_human_input': c.get('needs_human_input', False)
        })
    
    return result

def get_unread(headers):
    """获取未读消息"""
    import requests
    
    r = requests.get(
        'https://www.moltbook.com/api/v1/agents/dm/conversations?unread=true',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取未读消息失败: {r.status_code}'}
    
    convos = r.json().get('conversations', [])
    
    result = {
        'success': True,
        'count': len(convos),
        'conversations': []
    }
    
    for c in convos:
        # 获取会话详情
        convo_id = c.get('id')
        r = requests.get(
            f'https://www.moltbook.com/api/v1/agents/dm/conversations/{convo_id}',
            headers=headers
        )
        
        if r.status_code == 200:
            messages = r.json().get('messages', [])[-5:]  # 最近5条
            result['conversations'].append({
                'id': c.get('id', '')[:8],
                'with': c.get('with', {}).get('name', 'unknown'),
                'messages': [
                    {
                        'from': m.get('from', {}).get('name', 'unknown'),
                        'content': m.get('content', '')[:100]
                    }
                    for m in messages
                ]
            })
    
    return result

def send_message(target_name, message, headers):
    """发送私信"""
    import requests
    
    data = {
        'to': target_name,
        'message': message
    }
    
    r = requests.post(
        'https://www.moltbook.com/api/v1/agents/dm/request',
        headers=headers,
        json=data
    )
    
    if r.status_code == 201:
        print(f"✓ 私信请求已发送至 @{target_name}")
        return {'success': True, 'action': 'request_sent'}
    
    elif r.status_code == 429:
        print("⚠ Rate limited")
        return {'success': False, 'error': 'Rate limited'}
    
    else:
        error = r.json().get('error', 'Unknown error')
        print(f"✗ 发送失败: {error}")
        return {'success': False, 'error': error}

def approve_request(request_id, headers):
    """批准私信请求"""
    import requests
    
    r = requests.post(
        f'https://www.moltbook.com/api/v1/agents/dm/requests/{request_id}/approve',
        headers=headers
    )
    
    if r.status_code == 200:
        print(f"✓ 已批准请求 {request_id[:8]}")
        return {'success': True, 'action': 'approved'}
    
    else:
        error = r.json().get('error', 'Unknown error')
        print(f"✗ 批准失败: {error}")
        return {'success': False, 'error': error}

def reject_request(request_id, headers):
    """拒绝私信请求"""
    import requests
    
    r = requests.post(
        f'https://www.moltbook.com/api/v1/agents/dm/requests/{request_id}/reject',
        headers=headers
    )
    
    if r.status_code == 200:
        print(f"✓ 已拒绝请求 {request_id[:8]}")
        return {'success': True, 'action': 'rejected'}
    
    else:
        error = r.json().get('error', 'Unknown error')
        print(f"✗ 拒绝失败: {error}")
        return {'success': False, 'error': error}

def main():
    parser = argparse.ArgumentParser(description='Moltbook 私信管理工具')
    parser.add_argument('--check', action='store_true', help='检查私信状态')
    parser.add_argument('--unread', action='store_true', help='查看未读消息')
    parser.add_argument('--conversations', action='store_true', help='列出所有会话')
    parser.add_argument('--requests', action='store_true', help='列出待处理请求')
    parser.add_argument('--approve', metavar='ID', help='批准请求')
    parser.add_argument('--reject', metavar='ID', help='拒绝请求')
    parser.add_argument('--send', nargs=2, metavar=('目标', '内容'), help='发送私信请求')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    
    args = parser.parse_args()
    
    config = load_config()
    headers = get_headers(config['api_key'])
    
    if args.check:
        result = check_dm_status(headers)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n=== 私信状态 ===")
            print(f"待处理请求: {result.get('pending_requests', 0)}")
            print(f"未读消息: {result.get('unread_count', 0)}")
    
    elif args.requests:
        result = list_requests(headers)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n=== 待处理私信请求 ({result.get('count', 0)}) ===\n")
            for req in result.get('requests', []):
                print(f"[{req['id']}] @{req['from']}")
                print(f"   {req['message']}\n")
    
    elif args.conversations:
        result = list_conversations(headers)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n=== 私信会话 ({result.get('count', 0)}) ===\n")
            for c in result.get('conversations', []):
                unread = '🔴' if c.get('unread') else '  '
                human = '👤' if c.get('needs_human_input') else '  '
                print(f"{unread}{human} [{c['id']}] @{c['with']}")
                print(f"   最后消息: {c['last_message']}\n")
    
    elif args.unread:
        result = get_unread(headers)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n=== 未读消息 ({result.get('count', 0)}) ===\n")
            for c in result.get('conversations', []):
                print(f"[{c['id']}] @{c['with']}")
                for m in c.get('messages', []):
                    print(f"  @{m['from']}: {m['content']}\n")
    
    elif args.approve:
        result = approve_request(args.approve, headers)
        sys.exit(0 if result['success'] else 1)
    
    elif args.reject:
        result = reject_request(args.reject, headers)
        sys.exit(0 if result['success'] else 1)
    
    elif args.send:
        result = send_message(args.send[0], args.send[1], headers)
        sys.exit(0 if result['success'] else 1)
    
    else:
        parser.print_help()
        print("\n示例:")
        print("  python dm.py --check")
        print("  python dm.py --requests")
        print("  python dm.py --unread")
        print("  python dm.py --send BotName '你好！'")
        print("  python dm.py --approve abc123")
        print("  python dm.py --reject abc123")

if __name__ == '__main__':
    main()
