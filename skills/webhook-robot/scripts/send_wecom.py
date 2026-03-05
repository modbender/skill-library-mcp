import argparse
import json
import urllib.request
import sys

def send_wecom_msg(url_or_key, content, args):
    # Construct full URL if only key is provided
    if "http" not in url_or_key:
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={url_or_key}"
    else:
        url = url_or_key

    headers = {'Content-Type': 'application/json'}
    
    # WeCom message format
    if args.markdown:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
    else:
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                # "mentioned_list": ["@all"]  # Optional: mention everyone
            }
        }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to WeCom Robot')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--key', help='The key part of the webhook URL')
    group.add_argument('--url', help='The full webhook URL')
    
    parser.add_argument('--content', required=True, help='Text/Markdown content to send')
    parser.add_argument('--markdown', action='store_true', help='Send as Markdown')
    
    args = parser.parse_args()
    
    target = args.url if args.url else args.key
    send_wecom_msg(target, args.content, args)
