#!/usr/bin/env python3
"""
Feishu Send Message & File Tool - Ultimate Version

支持功能：
1. 发送文本消息（自动分片）
2. 直接发送文件（支持所有格式）
3. 读取文件发送（自动选择最佳方式）

Usage:
    # 发送文件
    python send_message.py <identifier> --file <path>
    
    # 发送文本
    python send_message.py <identifier> "消息内容"
    
    # 读取文件发送（自动选择）
    python send_message.py <identifier> --file <path>
"""

import json
import sys
import os
import re
import urllib.request
import urllib.error
import base64
import mimetypes

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
USERS_CONFIG_PATH = os.path.expanduser("~/.openclaw/workspace/configs/feishu-users.json")


def get_feishu_credentials():
    """Extract Feishu credentials from OpenClaw config."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        feishu_config = config.get('channels', {}).get('feishu', {})
        accounts = feishu_config.get('accounts', {})
        
        if 'main' in accounts:
            account = accounts['main']
        elif accounts:
            account = list(accounts.values())[0]
        else:
            return None, None, None
        
        return account.get('appId'), account.get('appSecret'), feishu_config.get('domain', 'feishu')
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        return None, None, None


def get_user_ids_from_config(identifier):
    """Get user IDs from local config file."""
    try:
        if not os.path.exists(USERS_CONFIG_PATH):
            return None
        
        with open(USERS_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        users = config.get('users', {})
        
        for name, user_info in users.items():
            if user_info.get('phone') == identifier:
                return user_info.get('ids', {})
            ids = user_info.get('ids', {})
            for id_type, id_value in ids.items():
                if id_value == identifier:
                    return ids
        
        return None
    except Exception as e:
        print(f"Error reading users config: {e}", file=sys.stderr)
        return None


def get_tenant_access_token(app_id, app_secret, domain='feishu'):
    """Fetch tenant_access_token from Feishu API."""
    base_url = f"https://open.{domain}.cn"
    url = f"{base_url}/open-apis/auth/v3/tenant_access_token/internal/"

    data = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    }).encode('utf-8')
    
    request = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('tenant_access_token'), base_url
            else:
                print(f"Failed to get token: {result.get('msg')}", file=sys.stderr)
                return None, None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None, None


def get_user_id_by_phone(token, base_url, phone):
    """Get user IDs by phone number."""
    url = f"{base_url}/open-apis/contact/v3/users/batch_get_id"
    
    data = json.dumps({"mobiles": [phone]}).encode('utf-8')
    
    request = urllib.request.Request(
        url, data=data,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0 and result.get('data', {}).get('items'):
                user_info = result['data']['items'][0]
                user_ids = {
                    'open_id': user_info.get('user_id'),
                    'union_id': user_info.get('union_id')
                }
                actual_user_id = get_actual_user_id(token, base_url, user_ids['open_id'])
                if actual_user_id:
                    user_ids['user_id'] = actual_user_id
                return user_ids
            return None
    except Exception as e:
        print(f"Error getting user ID: {e}", file=sys.stderr)
        return None


def get_actual_user_id(token, base_url, open_id):
    """Get actual user_id from open_id."""
    url = f"{base_url}/open-apis/contact/v3/users/{open_id}"
    
    request = urllib.request.Request(
        url, headers={'Authorization': f'Bearer {token}'}, method='GET'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('data', {}).get('user', {}).get('user_id')
            return None
    except Exception as e:
        print(f"Error getting actual user_id: {e}", file=sys.stderr)
        return None


def parse_markdown_to_feishu_post(markdown_text):
    """Parse markdown to Feishu post format."""
    lines = markdown_text.strip().split('\n')
    title = "来自千的消息"
    content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('# ') and not content:
            title = line[2:].strip()
            continue
        
        elements = []
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        parts = []
        last_end = 0
        
        for match in re.finditer(link_pattern, line):
            if match.start() > last_end:
                text_part = line[last_end:match.start()]
                if text_part:
                    parts.append(('text', text_part))
            parts.append(('link', match.group(1), match.group(2)))
            last_end = match.end()
        
        if last_end < len(line):
            text_part = line[last_end:]
            if text_part:
                parts.append(('text', text_part))
        
        if not parts:
            parts = [('text', line)]
        
        paragraph_elements = []
        for part in parts:
            if part[0] == 'text':
                text = part[1]
                text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                text = re.sub(r'\*(.+?)\*', r'\1', text)
                text = re.sub(r'`(.+?)`', r'\1', text)
                if text:
                    paragraph_elements.append({"tag": "text", "text": text})
            elif part[0] == 'link':
                paragraph_elements.append({"tag": "a", "text": part[1], "href": part[2]})
        
        if paragraph_elements:
            content.append(paragraph_elements)
    
    return {"zh_cn": {"title": title, "content": content}}


def is_rich_text(message):
    """Check if message requires rich text format."""
    if '# ' in message or '#\n' in message:
        return True
    if any(mark in message for mark in ['**', '*', '`']):
        return True
    return False


def upload_file(token, base_url, file_path):
    """Upload file to Feishu and get file_id."""
    url = f"{base_url}/open-apis/im/v1/files"
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    # Determine file type
    ext = os.path.splitext(file_name)[1].lower()
    file_type_map = {
        '.pdf': 'pdf',
        '.doc': 'doc',
        '.docx': 'docx',
        '.xls': 'xls',
        '.xlsx': 'xlsx',
        '.ppt': 'ppt',
        '.pptx': 'pptx',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.mp4': 'video',
        '.mp3': 'audio',
    }
    file_type = file_type_map.get(ext, 'pdf')
    
    # For images, check size limit (10MB)
    if file_type == 'image' and file_size > 10 * 1024 * 1024:
        print("Warning: Image file size exceeds 10MB limit", file=sys.stderr)
        return None
    
    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    # Create multipart form data
    boundary = '----FeishuBoundary' + str(base64.b64encode(os.urandom(12)).decode())
    
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file_type"\r\n\r\n{file_type}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file_name"\r\n\r\n{file_name}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file_size"\r\n\r\n{file_size}\r\n'
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'
    ).encode('utf-8') + file_content + f'\r\n--{boundary}--\r\n'.encode('utf-8')
    
    request = urllib.request.Request(
        url, data=body,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                file_id = result.get('data', {}).get('file_key') or result.get('data', {}).get('file_id')
                print(f"File uploaded successfully: {file_name} ({file_size} bytes)")
                return file_id
            else:
                print(f"Failed to upload file: {result.get('msg')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"Error uploading file: {e}", file=sys.stderr)
        return None


def send_file_message(token, base_url, user_id, id_type, file_id, file_name):
    """Send file message to Feishu user."""
    url = f"{base_url}/open-apis/im/v1/messages?receive_id_type={id_type}"
    
    content = json.dumps({"file_key": file_id})
    
    data = json.dumps({
        "receive_id": user_id,
        "msg_type": "file",
        "content": content
    }).encode('utf-8')
    
    request = urllib.request.Request(
        url, data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('data', {}).get('message_id')
            else:
                print(f"Failed to send file: {result.get('msg')}", file=sys.stderr)
                return None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            error_result = json.loads(body)
            print(f"HTTP Error: {error_result.get('msg', e.reason)}", file=sys.stderr)
        except:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error sending file: {e}", file=sys.stderr)
        return None


def send_file_with_all_ids(token, base_url, user_ids, file_id, file_name):
    """Try sending file with different user ID types."""
    id_types = ['user_id', 'union_id', 'open_id']
    
    for id_type in id_types:
        user_id = user_ids.get(id_type)
        if not user_id:
            continue
        
        message_id = send_file_message(token, base_url, user_id, id_type, file_id, file_name)
        if message_id:
            return message_id, id_type
    
    return None, None


def send_post_message(token, base_url, user_id, id_type, content):
    """Send rich text post message."""
    url = f"{base_url}/open-apis/im/v1/messages?receive_id_type={id_type}"
    post_content = parse_markdown_to_feishu_post(content)
    
    data = json.dumps({
        "receive_id": user_id,
        "msg_type": "post",
        "content": json.dumps(post_content)
    }).encode('utf-8')
    
    request = urllib.request.Request(
        url, data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('data', {}).get('message_id')
            else:
                print(f"Failed to send post: {result.get('msg')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def send_text_message(token, base_url, user_id, id_type, content):
    """Send plain text message."""
    url = f"{base_url}/open-apis/im/v1/messages?receive_id_type={id_type}"
    
    data = json.dumps({
        "receive_id": user_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }).encode('utf-8')
    
    request = urllib.request.Request(
        url, data=data,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('data', {}).get('message_id')
            else:
                print(f"Failed to send text: {result.get('msg')}", file=sys.stderr)
                return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def send_message_with_all_ids(token, base_url, user_ids, content):
    """Try sending message with different user ID types."""
    id_types = ['user_id', 'union_id', 'open_id']
    use_rich = is_rich_text(content)
    
    for id_type in id_types:
        user_id = user_ids.get(id_type)
        if not user_id:
            continue
        
        if use_rich:
            message_id = send_post_message(token, base_url, user_id, id_type, content)
        else:
            message_id = send_text_message(token, base_url, user_id, id_type, content)
        
        if message_id:
            return message_id, id_type
    
    return None, None


def split_content(content, max_chars=4000):
    """Split content into parts."""
    if len(content) <= max_chars:
        return [content]
    
    parts = []
    current = ""
    lines = content.split('\n')
    
    for line in lines:
        if len(current) + len(line) + 1 > max_chars:
            if current:
                parts.append(current.strip())
            current = line
        else:
            current = current + '\n' + line if current else line
    
    if current:
        parts.append(current.strip())
    
    return parts


def send_long_content(token, base_url, user_ids, content):
    """Send long content by splitting."""
    parts = split_content(content, max_chars=4000)
    
    if len(parts) == 1:
        message_id, id_type = send_message_with_all_ids(token, base_url, user_ids, content)
        if message_id:
            print(f"Message sent! Parts: 1/1, message_id: {message_id}")
            return True
        return False
    
    success_count = 0
    for i, part in enumerate(parts, 1):
        header = f"📄 【第 {i}/{len(parts)} 部分】】\n\n"
        part_content = header + part
        message_id, id_type = send_message_with_all_ids(token, base_url, user_ids, part_content)
        if message_id:
            success_count += 1
            print(f"Part {i}/{len(parts)} sent, message_id: {message_id}")
        
        import time
        time.sleep(0.5)
    
    print(f"Total: {success_count}/{len(parts)} parts sent")
    return success_count == len(parts)


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python send_message.py <identifier> <message>", file=sys.stderr)
        print("       python send_message.py <identifier> --file <path>", file=sys.stderr)
        sys.exit(1)
    
    identifier = sys.argv[1]
    use_file = False
    file_path = None
    
    # Check for --file flag
    if len(sys.argv) >= 4 and sys.argv[2] in ['--file', '-f']:
        identifier = sys.argv[1]
        file_path = sys.argv[3]
        use_file = True
    elif len(sys.argv) >= 3 and sys.argv[2] in ['--file', '-f']:
        identifier = sys.argv[1]
        file_path = sys.argv[3]
        use_file = True
    else:
        message = sys.argv[2]
    
    # Get credentials
    app_id, app_secret, domain = get_feishu_credentials()
    if not app_id or not app_secret:
        print("Failed to get Feishu credentials", file=sys.stderr)
        sys.exit(1)
    
    # Get token
    token, base_url = get_tenant_access_token(app_id, app_secret, domain)
    if not token:
        print("Failed to get tenant_access_token", file=sys.stderr)
        sys.exit(1)
    
    # Get user IDs
    user_ids = get_user_ids_from_config(identifier)
    if not user_ids:
        if identifier.startswith('+') or identifier.isdigit():
            user_ids = get_user_id_by_phone(token, base_url, identifier)
            if not user_ids:
                print(f"Failed to get user for phone: {identifier}", file=sys.stderr)
                sys.exit(1)
        else:
            user_ids = {'open_id': identifier}
    else:
        print("Found user IDs in local config")
    
    # Send file
    if use_file:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        file_name = os.path.basename(file_path)
        print(f"Uploading file: {file_name}")
        
        # Upload file
        file_id = upload_file(token, base_url, file_path)
        if not file_id:
            sys.exit(1)
        
        # Send file message
        message_id, id_type = send_file_with_all_ids(token, base_url, user_ids, file_id, file_name)
        if message_id:
            print(f"[OK] File sent successfully!")
            print(f"   File: {file_name}")
            print(f"   Message ID: {message_id}")
            print(f"   ID Type: {id_type}")
            sys.exit(0)
        else:
            print("Failed to send file", file=sys.stderr)
            sys.exit(1)
    
    # Send text message
    if len(message) > 4000:
        print(f"Message is {len(message)} characters. Splitting...")
        success = send_long_content(token, base_url, user_ids, message)
        sys.exit(0 if success else 1)
    else:
        message_id, id_type = send_message_with_all_ids(token, base_url, user_ids, message)
        if message_id:
            print(f"Message sent! ID type: {id_type}, message_id: {message_id}")
            sys.exit(0)
        else:
            print("Failed to send message", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
