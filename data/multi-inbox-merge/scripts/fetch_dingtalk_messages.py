#!/usr/bin/env python3
import argparse
import json
import os
import urllib.request


def post_json(url, data, headers=None):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))


def normalize(item):
    return {
        'source': 'dingtalk',
        'conversation_id': item.get('conversation_id') or item.get('chat_id') or '',
        'sender_name': item.get('sender_name') or item.get('sender_nick') or item.get('sender') or '',
        'msg_time': str(item.get('msg_time') or item.get('send_time') or item.get('timestamp') or ''),
        'msg_content': item.get('msg_content') or item.get('content') or item.get('text') or '',
        'direction': item.get('direction') or ('outbound' if item.get('is_from_me') else 'inbound'),
        'contact_key': item.get('contact_key') or item.get('sender_staff_id') or item.get('sender') or '',
    }


def main():
    ap = argparse.ArgumentParser(description='通过钉钉开放平台接口拉取消息并导出为 multi-inbox-merge 可读 JSON')
    ap.add_argument('--client-id', default=os.getenv('DINGTALK_CLIENT_ID', ''))
    ap.add_argument('--client-secret', default=os.getenv('DINGTALK_CLIENT_SECRET', ''))
    ap.add_argument('--token-url', default='https://api.dingtalk.com/v1.0/oauth2/accessToken')
    ap.add_argument('--messages-url', default=os.getenv('DINGTALK_MESSAGES_API_URL', ''), help='你的消息查询接口 URL（按企业应用能力配置）')
    ap.add_argument('--conversation-id', default='')
    ap.add_argument('--limit', type=int, default=100)
    ap.add_argument('--cursor', default='')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    if not args.client_id or not args.client_secret:
        raise SystemExit('缺少 client_id/client_secret，请传参或设置 DINGTALK_CLIENT_ID / DINGTALK_CLIENT_SECRET')
    if not args.messages_url:
        raise SystemExit('缺少 messages_url，请传 --messages-url 或设置 DINGTALK_MESSAGES_API_URL')

    token_resp = post_json(args.token_url, {
        'appKey': args.client_id,
        'appSecret': args.client_secret,
    })
    access_token = token_resp.get('accessToken')
    if not access_token:
        raise SystemExit(f'获取 access token 失败: {token_resp}')

    payload = {
        'limit': args.limit,
        'cursor': args.cursor,
    }
    if args.conversation_id:
        payload['conversation_id'] = args.conversation_id

    data_resp = post_json(args.messages_url, payload, headers={
        'x-acs-dingtalk-access-token': access_token,
    })

    # 兼容常见返回结构
    items = []
    if isinstance(data_resp, list):
        items = data_resp
    elif isinstance(data_resp, dict):
        for key in ('messages', 'data', 'items', 'result'):
            v = data_resp.get(key)
            if isinstance(v, list):
                items = v
                break

    normalized = [normalize(x) for x in items if isinstance(x, dict)]
    out = {
        'messages': normalized,
        'meta': {
            'source': 'dingtalk-api',
            'count': len(normalized),
        }
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'已导出钉钉消息: {args.out}，共 {len(normalized)} 条')


if __name__ == '__main__':
    main()
