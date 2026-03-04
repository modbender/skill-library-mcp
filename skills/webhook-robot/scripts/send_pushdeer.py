import argparse
import urllib.request
import urllib.parse
import sys

def send_pushdeer_msg(key, content, title=None):
    url = "https://api2.pushdeer.com/message/push"
    
    params = {
        "pushkey": key,
        "text": title if title else content,
        "desp": content if title else None,
        "type": "markdown"
    }
    
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    data = urllib.parse.urlencode(params).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ PushDeer Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send PushDeer message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to PushDeer')
    parser.add_argument('--key', required=True, help='PushDeer PushKey')
    parser.add_argument('--content', required=True, help='Message content')
    parser.add_argument('--title', help='Message title (optional)')
    
    args = parser.parse_args()
    send_pushdeer_msg(args.key, args.content, args.title)
