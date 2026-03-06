import argparse
import urllib.request
import sys

def send_bark_msg(key, title, content, url=None, group=None):
    # Construct base URL
    # Format: https://api.day.app/{key}/{title}/{body}?url=...&group=...
    base_url = f"https://api.day.app/{key}/"
    
    # URL encode title and content
    title_enc = urllib.parse.quote(title) if title else "Notification"
    content_enc = urllib.parse.quote(content)
    
    request_url = f"{base_url}{title_enc}/{content_enc}"
    
    params = []
    if url:
        params.append(f"url={urllib.parse.quote(url)}")
    if group:
        params.append(f"group={urllib.parse.quote(group)}")
        
    if params:
        request_url += "?" + "&".join(params)

    try:
        req = urllib.request.Request(request_url)
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Bark Message sent. Response: {result}")
    except Exception as e:
        print(f"❌ Failed to send Bark message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send message to Bark')
    parser.add_argument('--key', required=True, help='Bark key')
    parser.add_argument('--title', help='Notification title')
    parser.add_argument('--content', required=True, help='Notification content')
    parser.add_argument('--url', help='Click URL')
    parser.add_argument('--group', help='Notification group')
    
    args = parser.parse_args()
    
    send_bark_msg(args.key, args.title, args.content, args.url, args.group)
