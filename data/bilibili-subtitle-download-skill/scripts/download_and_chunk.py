import os
import sys
import json
import re
import asyncio
import requests
from bilibili_api import login_v2, Credential

# Configuration
COOKIE_FILE = os.path.expanduser('~/.openclaw/workspace/bilibili_cookie.txt')
CHARS_PER_CHUNK = 100000 
QR_IMAGE_PATH = os.path.expanduser('~/.openclaw/workspace/bilibili_login_qr.png')

def clean_filename(title):
    return re.sub(r'[\\/:*?"<>|]', '_', title)

def get_saved_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r') as f:
            return f.read().strip()
    return ""

async def login_with_qr():
    qr = login_v2.QrCodeLogin(platform=login_v2.QrCodeLoginChannel.WEB)
    await qr.generate_qrcode()
    
    # Save QR code image for user to scan
    pic = qr.get_qrcode_picture()
    pic.to_file(QR_IMAGE_PATH)
    
    print(f"QR_CODE_READY:{QR_IMAGE_PATH}", flush=True)
    print("老大，请扫描这个二维码登录喵！🐾", flush=True)
    
    # Wait for login
    while not qr.has_done():
        state = await qr.check_state()
        if state == login_v2.QrCodeLoginEvents.DONE: # Success
            break
        await asyncio.sleep(2)
    
    credential = qr.get_credential()
    cookies = credential.get_cookies()
    
    # Save cookies to file in string format for general HTTP requests
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    with open(COOKIE_FILE, 'w') as f:
        f.write(cookie_str)
    
    if os.path.exists(QR_IMAGE_PATH):
        os.remove(QR_IMAGE_PATH)
        
    return cookie_str

def get_video_info(bv_id, cookie):
    url = "https://api.bilibili.com/x/web-interface/view"
    params = {'bvid': bv_id}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com/',
        'Cookie': cookie
    }
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    if data['code'] != 0:
        # If cookie invalid, code might be -101
        return None, data['message']
    return data['data'], None

def fetch_subtitle_content(bv_id, cid, cookie):
    # Logic adapted from gpt-bilibili-to-notion
    subtitle_api = 'https://api.bilibili.com/x/player/v2'
    headers = {
        'authority': 'api.bilibili.com',
        'accept': 'application/json, text/plain, */*',
        'origin': 'https://www.bilibili.com',
        'referer': 'https://www.bilibili.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Cookie': cookie
    }
    params = {'bvid': bv_id, 'cid': cid}
    resp = requests.get(subtitle_api, headers=headers, params=params)
    data = resp.json()
    
    if data.get('code') != 0:
        return None
    
    subtitles = data.get('data', {}).get('subtitle', {}).get('subtitles', [])
    if not subtitles:
        return None

    # Prefer Chinese (zh-Hans or zh-CN)
    target_url = ""
    for s in subtitles:
        if 'zh' in s.get('lan', ''):
            target_url = s['subtitle_url']
            break
    
    # If no Chinese subtitle found, but subtitles list is not empty
    if not target_url and subtitles:
        target_url = subtitles[0].get('subtitle_url', "")

    if not target_url:
        return None

    if target_url.startswith('//'):
        target_url = 'https:' + target_url
    
    resp = requests.get(target_url)
    body = resp.json().get('body', [])
    full_text = "\n".join([b.get('content', '') for b in body])
    return full_text

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_and_chunk.py <BV_ID> [P_NUM]")
        sys.exit(1)
    
    bv_id = sys.argv[1]
    p_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print(f"[*] Processing {bv_id} (P{p_num})...🐾", flush=True)
    
    try:
        cookie = get_saved_cookie()
        info = None
        
        if cookie:
            info, err = get_video_info(bv_id, cookie)
        
        # If no cookie or cookie expired/invalid
        if not info:
            cookie = await login_with_qr()
            info, err = get_video_info(bv_id, cookie)
            if not info:
                raise Exception(f"Failed to get video info even after login: {err}")

        # Get CID for the requested Part
        pages = info.get('pages', [])
        if p_num >= len(pages):
            raise Exception(f"Invalid P_NUM: video only has {len(pages)} parts.")
        cid = pages[p_num]['cid']
        
        # Try fetching subtitle using the logic from gpt-bilibili-to-notion
        full_text = fetch_subtitle_content(bv_id, cid, cookie)
        
        if not full_text:
            print("ERROR: 没找到字幕喵...😿 请确认视频是否有 CC 字幕喵。")
            sys.exit(1)

        title = info.get('title', bv_id)
        total_chars = len(full_text)
        
        # Create output dir in workspace using BV_ID
        output_dir = os.path.join(os.getcwd(), 'bili_temp', bv_id)
        os.makedirs(output_dir, exist_ok=True)
        
        chunks = []
        for i in range(0, total_chars, CHARS_PER_CHUNK):
            chunk_content = full_text[i : i + CHARS_PER_CHUNK]
            chunk_index = i // CHARS_PER_CHUNK
            chunk_file = os.path.join(output_dir, f"{bv_id}_chunk_{chunk_index}.txt")
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk_content)
            chunks.append(chunk_file)
            
        print(f"[*] Success. Total chunks: {len(chunks)}")
        print("RESULT_JSON:" + json.dumps({
            "bv_id": bv_id,
            "title": title,
            "total_chars": total_chars,
            "chunks": chunks
        }))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
