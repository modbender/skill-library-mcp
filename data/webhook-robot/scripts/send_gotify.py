import argparse
import urllib.request
import urllib.parse
import json
import sys

def send_gotify_msg(url, token, title, content, priority=5):
    # Ensure URL ends with /message
    if not url.endswith('/message'):
        url = url.rstrip('/') + '/message'
    
    headers = {
        'X-Gotify-Key': token,
        'Content-Type': 'application/json'
    }
    
    data = {
        "title": title,
        "message": content,
        "priority": priority,
        "extras": {
            "client::display": {
                "contentType": "text/markdown"
            }
        }
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Gotify Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send Gotify message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to Gotify')
    parser.add_argument('--url', required=True, help='Gotify Server URL')
    parser.add_argument('--token', required=True, help='App Token')
    parser.add_argument('--title', default='Notification', help='Message title')
    parser.add_argument('--content', required=True, help='Message content')
    parser.add_argument('--priority', type=int, default=5, help='Priority (0-10)')
    
    args = parser.parse_args()
    send_gotify_msg(args.url, args.token, args.title, args.content, args.priority)
