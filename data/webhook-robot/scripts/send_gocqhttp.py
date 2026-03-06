import argparse
import json
import urllib.request
import sys

def send_gocq_msg(url, user_id=None, group_id=None, content=""):
    # Determine endpoint based on target
    if group_id:
        endpoint = f"{url}/send_group_msg"
        data = {"group_id": group_id, "message": content}
    elif user_id:
        endpoint = f"{url}/send_private_msg"
        data = {"user_id": user_id, "message": content}
    else:
        print("❌ Error: Either user_id or group_id must be provided")
        sys.exit(1)

    headers = {'Content-Type': 'application/json'}

    try:
        req = urllib.request.Request(endpoint, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ GoCqHttp Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send GoCqHttp message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message via GoCqHttp (OneBot)')
    parser.add_argument('--url', required=True, help='GoCqHttp API base URL (e.g. http://127.0.0.1:5700)')
    parser.add_argument('--user_id', help='Target User ID')
    parser.add_argument('--group_id', help='Target Group ID')
    parser.add_argument('--content', required=True, help='Message content')
    
    args = parser.parse_args()
    send_gocq_msg(args.url, args.user_id, args.group_id, args.content)
