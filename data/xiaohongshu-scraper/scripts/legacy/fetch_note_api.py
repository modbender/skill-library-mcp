#!/usr/bin/env python3
"""
小红书笔记抓取 - API 方案
使用 cookies 直接调用 API 获取笔记数据

使用方法:
    python fetch_note_api.py "笔记URL或ID" --output /tmp/xhs_output
    python fetch_note_api.py "697d3a11000000002203a0c9" -o /tmp/xhs_output --ocr
"""

import argparse
import json
import os
import re
import requests
import hashlib
import time
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs


def load_cookies():
    """加载保存的 cookies"""
    cookie_file = Path.home() / '.xiaohongshu-scraper' / 'cookies.json'
    if not cookie_file.exists():
        print(f"❌ Cookie 文件不存在: {cookie_file}")
        print("请先运行登录脚本获取 cookies")
        return None
    
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
    
    # 转换为 cookie 字符串
    cookie_str = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    return cookie_str


def extract_note_id(url_or_id):
    """从各种格式的链接中提取笔记 ID"""
    # 如果已经是纯 ID
    if re.match(r'^[a-f0-9]{24}$', url_or_id):
        return url_or_id
    
    # 从 URL 中提取
    patterns = [
        r'/explore/([a-f0-9]{24})',
        r'/discovery/item/([a-f0-9]{24})',
        r'/item/([a-f0-9]{24})',
        r'note_id=([a-f0-9]{24})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    print(f"❌ 无法从链接中提取笔记 ID: {url_or_id}")
    return None


def get_xs_common():
    """生成 x-s 签名（简化版，可能需要更新）"""
    # 小红书的签名算法比较复杂，这里用简化方案
    # 实际可能需要逆向 JS 或使用 execjs
    return ""


def fetch_note_api(note_id, cookies):
    """通过 API 获取笔记数据"""
    
    url = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.xiaohongshu.com',
        'Referer': f'https://www.xiaohongshu.com/explore/{note_id}',
        'Cookie': cookies,
    }
    
    payload = {
        "source_note_id": note_id,
        "image_formats": ["jpg", "webp", "avif"],
        "extra": {"need_body_topic": "1"}
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success') or data.get('code') == 0:
                return data.get('data', {})
            else:
                print(f"API 返回错误: {data}")
                return None
        else:
            print(f"HTTP 错误: {resp.status_code}")
            print(resp.text[:500])
            return None
            
    except Exception as e:
        print(f"请求失败: {e}")
        return None


def fetch_note_web(note_id, cookies):
    """通过网页接口获取笔记数据（备用方案）"""
    
    url = f"https://www.xiaohongshu.com/explore/{note_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': cookies,
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        
        if resp.status_code == 200:
            # 从 HTML 中提取 JSON 数据
            # 小红书会在页面中嵌入 __INITIAL_STATE__ 或类似的数据
            
            # 方法1: 查找 window.__INITIAL_STATE__
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*</script>', resp.text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    return data
                except:
                    pass
            
            # 方法2: 查找 JSON-LD 数据
            match = re.search(r'<script type="application/ld\+json">(.+?)</script>', resp.text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    return {'ld_json': data}
                except:
                    pass
            
            # 方法3: 直接解析 HTML
            result = parse_html(resp.text)
            if result:
                return result
                
            return {'html': resp.text}
        else:
            print(f"HTTP 错误: {resp.status_code}")
            return None
            
    except Exception as e:
        print(f"请求失败: {e}")
        return None


def parse_html(html):
    """从 HTML 中解析笔记数据"""
    result = {}
    
    # 提取标题
    title_match = re.search(r'<title>([^<]+)</title>', html)
    if title_match:
        result['title'] = title_match.group(1).replace(' - 小红书', '').strip()
    
    # 提取 meta 描述
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)
    if desc_match:
        result['description'] = desc_match.group(1)
    
    # 提取 og:image
    images = re.findall(r'<meta property="og:image" content="([^"]+)"', html)
    if images:
        result['images'] = images
    
    # 提取所有图片 URL
    all_images = re.findall(r'https://[^"\']+\.(?:jpg|jpeg|png|webp|avif)[^"\']*', html)
    # 过滤并去重
    filtered_images = []
    for img in all_images:
        if 'sns-webpic' in img or 'ci.xiaohongshu.com' in img:
            # 清理 URL 参数
            clean_url = re.sub(r'\?.*$', '', img)
            if clean_url not in filtered_images:
                filtered_images.append(clean_url)
    
    if filtered_images:
        result['all_images'] = filtered_images
    
    return result if result else None


def download_image(url, save_path):
    """下载图片"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.xiaohongshu.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
    return False


def ocr_image_vision(image_path):
    """使用 macOS Vision 框架进行 OCR"""
    
    # 使用 Swift 脚本调用 Vision
    swift_code = '''
import Vision
import AppKit

let imagePath = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: imagePath),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("无法加载图片")
    exit(1)
}

let request = VNRecognizeTextRequest { request, error in
    guard let observations = request.results as? [VNRecognizedTextObservation] else { return }
    
    for observation in observations {
        if let topCandidate = observation.topCandidates(1).first {
            print(topCandidate.string)
        }
    }
}

request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "zh-Hant", "en"]

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
try? handler.perform([request])
'''
    
    # 写入临时 Swift 文件
    swift_file = '/tmp/ocr_vision.swift'
    with open(swift_file, 'w') as f:
        f.write(swift_code)
    
    try:
        result = subprocess.run(
            ['swift', swift_file, image_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"OCR 错误: {result.stderr}")
            return None
    except Exception as e:
        print(f"OCR 失败: {e}")
        return None


def ocr_image_tesseract(image_path):
    """使用 Tesseract 进行 OCR（备用）"""
    try:
        result = subprocess.run(
            ['tesseract', image_path, 'stdout', '-l', 'chi_sim+eng'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        print("Tesseract 未安装，跳过")
    except Exception as e:
        print(f"Tesseract OCR 失败: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description='小红书笔记抓取 - API 方案')
    parser.add_argument('url', help='笔记 URL 或 ID')
    parser.add_argument('--output', '-o', help='输出目录', default='/tmp/xhs_note')
    parser.add_argument('--ocr', action='store_true', help='对图片进行 OCR')
    parser.add_argument('--ocr-engine', choices=['vision', 'tesseract'], default='vision', help='OCR 引擎')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("小红书笔记抓取 - API 方案")
    print("=" * 60)
    
    # 加载 cookies
    cookies = load_cookies()
    if not cookies:
        return
    
    print(f"✓ Cookies 已加载")
    
    # 提取笔记 ID
    note_id = extract_note_id(args.url)
    if not note_id:
        return
    
    print(f"✓ 笔记 ID: {note_id}")
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / 'images'
    images_dir.mkdir(exist_ok=True)
    
    # 尝试 API 获取
    print("\n正在通过 API 获取笔记数据...")
    data = fetch_note_api(note_id, cookies)
    
    if not data:
        print("API 方式失败，尝试网页方式...")
        data = fetch_note_web(note_id, cookies)
    
    if not data:
        print("❌ 无法获取笔记数据")
        return
    
    # 保存原始数据
    raw_file = output_dir / 'raw_data.json'
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 原始数据已保存: {raw_file}")
    
    # 解析笔记数据
    result = {
        'note_id': note_id,
        'fetch_time': datetime.now().isoformat(),
        'title': '',
        'author': '',
        'content': '',
        'images': [],
        'local_images': [],
        'ocr_results': []
    }
    
    # 从不同数据结构中提取信息
    if 'items' in data and data['items']:
        note_data = data['items'][0].get('note_card', {})
        result['title'] = note_data.get('title', '')
        result['content'] = note_data.get('desc', '')
        result['author'] = note_data.get('user', {}).get('nickname', '')
        
        # 提取图片
        image_list = note_data.get('image_list', [])
        for img in image_list:
            # 优先使用高清图
            url = img.get('url_default') or img.get('url') or img.get('url_pre', '')
            if url and url not in result['images']:
                result['images'].append(url)
    
    elif 'title' in data:
        result['title'] = data.get('title', '')
        result['content'] = data.get('description', '')
        result['images'] = data.get('all_images', data.get('images', []))
    
    elif 'html' in data:
        # 需要进一步解析 HTML
        parsed = parse_html(data['html'])
        if parsed:
            result['title'] = parsed.get('title', '')
            result['content'] = parsed.get('description', '')
            result['images'] = parsed.get('all_images', [])
    
    print(f"\n📝 标题: {result['title']}")
    print(f"👤 作者: {result['author']}")
    print(f"📄 内容: {result['content'][:100]}..." if len(result['content']) > 100 else f"📄 内容: {result['content']}")
    print(f"🖼️  图片: {len(result['images'])} 张")
    
    # 下载图片
    if result['images']:
        print(f"\n正在下载 {len(result['images'])} 张图片...")
        for i, img_url in enumerate(result['images']):
            ext = '.jpg'
            if '.png' in img_url:
                ext = '.png'
            elif '.webp' in img_url:
                ext = '.webp'
            
            filename = f"image_{i+1:02d}{ext}"
            save_path = images_dir / filename
            
            if download_image(img_url, str(save_path)):
                result['local_images'].append(str(save_path))
                print(f"  ✓ {filename}")
            else:
                print(f"  ✗ {filename}")
    
    # OCR
    if args.ocr and result['local_images']:
        print(f"\n正在进行 OCR 识别 ({args.ocr_engine})...")
        
        for img_path in result['local_images']:
            print(f"  处理: {Path(img_path).name}")
            
            if args.ocr_engine == 'vision':
                text = ocr_image_vision(img_path)
            else:
                text = ocr_image_tesseract(img_path)
            
            if text:
                result['ocr_results'].append({
                    'image': img_path,
                    'text': text
                })
                print(f"    识别到 {len(text)} 字符")
            else:
                print(f"    未识别到文字")
    
    # 保存结果
    result_file = output_dir / 'note.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 生成 Markdown
    md_content = f"""# {result['title']}

**作者**: {result['author']}  
**抓取时间**: {result['fetch_time']}  
**笔记ID**: {result['note_id']}

## 正文内容

{result['content']}

## 图片

"""
    
    for i, img_path in enumerate(result['local_images']):
        md_content += f"### 图片 {i+1}\n\n"
        md_content += f"![image_{i+1}](images/{Path(img_path).name})\n\n"
        
        # 添加 OCR 结果
        for ocr in result['ocr_results']:
            if ocr['image'] == img_path:
                md_content += f"**OCR 识别文字:**\n\n```\n{ocr['text']}\n```\n\n"
                break
    
    md_file = output_dir / 'note.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n" + "=" * 60)
    print("✅ 抓取完成!")
    print("=" * 60)
    print(f"\n输出目录: {output_dir}")
    print(f"  - note.json    (结构化数据)")
    print(f"  - note.md      (Markdown 文档)")
    print(f"  - raw_data.json (原始 API 数据)")
    print(f"  - images/      ({len(result['local_images'])} 张图片)")
    if result['ocr_results']:
        print(f"  - OCR 结果已包含在 JSON 和 MD 中")


if __name__ == '__main__':
    main()
