import argparse
import json
import urllib.request
import sys
import time
import hmac
import hashlib
import base64

def send_feishu_msg(url_or_token, secret, content):
    if "http" not in url_or_token:
        url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{url_or_token}"
    else:
        url = url_or_token

    headers = {'Content-Type': 'application/json'}
    data = {}

    # Sign (optional)
    if secret:
        timestamp = str(int(time.time()))
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        data["timestamp"] = timestamp
        data["sign"] = sign

    # Feishu only supports "post" type with rich text or plain text content
    # Here we simplify to plain text for broad compatibility
    data["msg_type"] = "text"
    data["content"] = {
        "text": content
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Feishu Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send Feishu message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to Feishu Robot')
    parser.add_argument('--token', help='Feishu webhook token/key')
    parser.add_argument('--url', help='Full Feishu webhook URL')
    parser.add_argument('--secret', help='Feishu secret (optional)')
    parser.add_argument('--content', required=True, help='Text content to send')
    
    args = parser.parse_args()
    target = args.url if args.url else args.token
    
    if not target:
        print("Error: --token or --url is required")
        sys.exit(1)

    send_feishu_msg(target, args.secret, args.content)
