import argparse
import json
import urllib.request
import sys

def send_telegram_msg(token, chat_id, content, markdown=False):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "chat_id": chat_id,
        "text": content
    }
    
    if markdown:
        data["parse_mode"] = "MarkdownV2"

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Telegram Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to Telegram Bot')
    parser.add_argument('--token', required=True, help='Bot token')
    parser.add_argument('--chat_id', required=True, help='Target chat ID')
    parser.add_argument('--content', required=True, help='Message content')
    parser.add_argument('--markdown', action='store_true', help='Use MarkdownV2')
    
    args = parser.parse_args()
    
    send_telegram_msg(args.token, args.chat_id, args.content, args.markdown)
