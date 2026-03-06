import argparse
import urllib.request
import urllib.parse
import sys

def send_serverchan_msg(key, title, content):
    url = f"https://sctapi.ftqq.com/{key}.send"
    
    params = {
        "title": title,
        "desp": content
    }
    
    data = urllib.parse.urlencode(params).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ ServerChan Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send ServerChan message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to ServerChan (Turbo)')
    parser.add_argument('--key', required=True, help='SendKey')
    parser.add_argument('--title', required=True, help='Message title')
    parser.add_argument('--content', required=True, help='Message content (Markdown supported)')
    
    args = parser.parse_args()
    send_serverchan_msg(args.key, args.title, args.content)
