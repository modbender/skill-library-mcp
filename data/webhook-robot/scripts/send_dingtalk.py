import argparse
import json
import urllib.request
import sys
import time
import hmac
import hashlib
import base64

def send_dingtalk_msg(token, secret, content, markdown=False):
    # Construct URL with timestamp and sign if secret is provided
    url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    
    if secret:
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url = f"{url}&timestamp={timestamp}&sign={sign}"

    headers = {'Content-Type': 'application/json'}
    
    if markdown:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": "Notification",
                "text": content
            }
        }
    else:
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ DingTalk Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send DingTalk message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to DingTalk Robot')
    parser.add_argument('--token', required=True, help='DingTalk access token')
    parser.add_argument('--secret', help='DingTalk secret (optional, for security)')
    parser.add_argument('--content', required=True, help='Text/Markdown content to send')
    parser.add_argument('--markdown', action='store_true', help='Send as Markdown')
    
    args = parser.parse_args()
    
    send_dingtalk_msg(args.token, args.secret, args.content, args.markdown)
