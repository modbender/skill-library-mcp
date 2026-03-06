#!/usr/bin/env python3
"""
小红书笔记抓取 - 基于 XHS-Downloader 的解析逻辑
直接使用 requests 请求，避免 httpx 的代理问题

使用方法:
    python xhs_fetch.py "笔记URL或ID" --output /tmp/xhs_output --ocr
"""

import argparse
import json
import os
import re
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from lxml.etree import HTML
from yaml import safe_load


def load_cookies():
    """加载保存的 cookies"""
    cookie_file = Path.home() / '.xiaohongshu-scraper' / 'cookie_string.txt'
    if cookie_file.exists():
        return cookie_file.read_text().strip()
    
    # 尝试从 JSON 格式加载
    json_file = Path.home() / '.xiaohongshu-scraper' / 'cookies.json'
    if json_file.exists():
        cookies = json.loads(json_file.read_text())
        return '; '.join([f"{c['name']}={c['value']}" for c in cookies])
    
    return None


def extract_note_id(url_or_id):
    """从各种格式的链接中提取笔记 ID"""
    if re.match(r'^[a-f0-9]{24}$', url_or_id):
        return url_or_id
    
    patterns = [
        r'/explore/([a-f0-9]{24})',
        r'/discovery/item/([a-f0-9]{24})',
        r'/item/([a-f0-9]{24})',
        r'user/profile/[a-z0-9]+/([a-f0-9]{24})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return None


def resolve_short_link(short_url, headers):
    """解析短链接"""
    try:
        resp = requests.get(short_url, headers=headers, allow_redirects=False, timeout=10)
        if resp.status_code in [301, 302]:
            return resp.headers.get('Location', '')
    except:
        pass
    return short_url


def fetch_html(url, cookie):
    """获取页面 HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': cookie,
    }
    
    # 处理短链接
    if 'xhslink.com' in url:
        url = resolve_short_link(url, headers)
    
    resp = requests.get(url, headers=headers, timeout=30)
    return resp.text


def parse_initial_state(html):
    """从 HTML 中提取 __INITIAL_STATE__ 数据"""
    html_tree = HTML(html)
    scripts = html_tree.xpath("//script/text()")
    
    for script in reversed(scripts):
        if script.startswith("window.__INITIAL_STATE__"):
            data = safe_load(script.lstrip("window.__INITIAL_STATE__="))
            
            # PC 端数据结构
            if 'note' in data and 'noteDetailMap' in data['note']:
                note_map = data['note']['noteDetailMap']
                if note_map:
                    # 遍历所有 key（可能是 undefined 或实际 note_id）
                    for key, value in note_map.items():
                        if value and isinstance(value, dict) and 'note' in value:
                            note_data = value.get('note', {})
                            # 检查是否有有效数据
                            if note_data.get('noteId') or note_data.get('title') or note_data.get('desc'):
                                return note_data
            
            # 移动端数据结构
            if 'noteData' in data:
                return data['noteData'].get('data', {}).get('noteData', {})
    
    return None


def extract_note_data(data):
    """从解析的数据中提取笔记信息"""
    result = {
        'note_id': data.get('noteId', ''),
        'title': data.get('title', ''),
        'desc': data.get('desc', ''),
        'type': data.get('type', ''),  # video 或 normal
        'author': {
            'nickname': data.get('user', {}).get('nickname', ''),
            'user_id': data.get('user', {}).get('userId', ''),
        },
        'interact': {
            'liked_count': data.get('interactInfo', {}).get('likedCount', 0),
            'collected_count': data.get('interactInfo', {}).get('collectedCount', 0),
            'comment_count': data.get('interactInfo', {}).get('commentCount', 0),
            'share_count': data.get('interactInfo', {}).get('shareCount', 0),
        },
        'tags': [tag.get('name', '') for tag in data.get('tagList', [])],
        'time': data.get('time', 0),
        'images': [],
        'video': None,
    }
    
    # 提取图片
    image_list = data.get('imageList', [])
    for img in image_list:
        # 优先使用原图
        url = img.get('urlDefault') or img.get('url', '')
        if url:
            # 移除水印参数，获取高清图
            url = re.sub(r'\?.*$', '', url)
            result['images'].append({
                'url': url,
                'width': img.get('width', 0),
                'height': img.get('height', 0),
            })
        
        # 检查是否有动图
        if img.get('livePhoto'):
            result['images'][-1]['live_photo'] = img.get('stream', {}).get('h264', [{}])[0].get('masterUrl', '')
    
    # 提取视频
    if data.get('type') == 'video':
        video_info = data.get('video', {})
        media = video_info.get('media', {})
        stream = media.get('stream', {})
        
        # 获取最高清的视频
        for quality in ['h266', 'h265', 'h264', 'av1']:
            if quality in stream and stream[quality]:
                video_list = stream[quality]
                if video_list:
                    result['video'] = {
                        'url': video_list[0].get('masterUrl', ''),
                        'quality': quality,
                    }
                    break
    
    return result


def download_file(url, save_path):
    """下载文件"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.xiaohongshu.com/'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=60, stream=True)
        if resp.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"下载失败: {e}")
    return False


def ocr_image_vision(image_path):
    """使用 macOS Vision 框架进行 OCR"""
    swift_code = '''
import Vision
import AppKit

let imagePath = CommandLine.arguments[1]
guard let image = NSImage(contentsOfFile: imagePath),
      let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    exit(0)
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
    swift_file = '/tmp/ocr_vision.swift'
    with open(swift_file, 'w') as f:
        f.write(swift_code)
    
    try:
        result = subprocess.run(['swift', swift_file, image_path], capture_output=True, text=True, timeout=60)
        return result.stdout.strip() if result.returncode == 0 else None
    except:
        return None


def main():
    parser = argparse.ArgumentParser(description='小红书笔记抓取')
    parser.add_argument('url', help='笔记 URL 或 ID')
    parser.add_argument('--output', '-o', default='/tmp/xhs_note', help='输出目录')
    parser.add_argument('--ocr', action='store_true', help='对图片进行 OCR')
    parser.add_argument('--cookie', '-c', help='Cookie 字符串（可选，默认从文件读取）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("小红书笔记抓取")
    print("=" * 60)
    
    # 加载 cookie
    cookie = args.cookie or load_cookies()
    if not cookie:
        print("❌ 未找到 Cookie，请先登录小红书")
        return
    
    print("✓ Cookie 已加载")
    
    # 提取笔记 ID
    note_id = extract_note_id(args.url)
    if not note_id:
        # 可能是短链接，先解析
        print(f"尝试解析链接: {args.url}")
    
    # 构建 URL
    if note_id:
        url = f"https://www.xiaohongshu.com/explore/{note_id}"
    else:
        url = args.url
    
    print(f"目标 URL: {url}")
    
    # 获取页面
    print("\n正在获取页面...")
    try:
        html = fetch_html(url, cookie)
    except Exception as e:
        print(f"❌ 获取页面失败: {e}")
        return
    
    # 解析数据
    print("正在解析数据...")
    data = parse_initial_state(html)
    
    if not data:
        print("❌ 解析数据失败")
        # 保存 HTML 用于调试
        debug_file = Path(args.output) / 'debug.html'
        debug_file.parent.mkdir(parents=True, exist_ok=True)
        debug_file.write_text(html)
        print(f"已保存 HTML 到: {debug_file}")
        return
    
    # 提取笔记信息
    note = extract_note_data(data)
    
    print(f"\n📝 标题: {note['title']}")
    print(f"👤 作者: {note['author']['nickname']}")
    print(f"📄 描述: {note['desc'][:100]}..." if len(note['desc']) > 100 else f"📄 描述: {note['desc']}")
    print(f"❤️  点赞: {note['interact']['liked_count']} | 收藏: {note['interact']['collected_count']} | 评论: {note['interact']['comment_count']}")
    print(f"🏷️  标签: {', '.join(note['tags'])}")
    print(f"🖼️  图片: {len(note['images'])} 张")
    if note['video']:
        print(f"🎬 视频: {note['video']['quality']}")
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / 'images'
    images_dir.mkdir(exist_ok=True)
    
    # 下载图片
    local_images = []
    if note['images']:
        print(f"\n正在下载 {len(note['images'])} 张图片...")
        for i, img in enumerate(note['images']):
            url = img['url']
            ext = '.webp' if '.webp' in url else '.jpg'
            filename = f"image_{i+1:02d}{ext}"
            save_path = images_dir / filename
            
            if download_file(url, str(save_path)):
                local_images.append(str(save_path))
                print(f"  ✓ {filename}")
            else:
                print(f"  ✗ {filename}")
    
    # 下载视频
    local_video = None
    if note['video']:
        print("\n正在下载视频...")
        video_path = output_dir / 'video.mp4'
        if download_file(note['video']['url'], str(video_path)):
            local_video = str(video_path)
            print(f"  ✓ video.mp4")
    
    # OCR
    ocr_results = []
    if args.ocr and local_images:
        print("\n正在进行 OCR 识别...")
        for img_path in local_images:
            img_name = Path(img_path).name
            print(f"  处理: {img_name}")
            text = ocr_image_vision(img_path)
            if text:
                ocr_results.append({
                    'image': img_name,
                    'text': text
                })
                print(f"    识别到 {len(text)} 字符")
    
    # 保存结果
    result = {
        'note_id': note['note_id'],
        'fetch_time': datetime.now().isoformat(),
        'title': note['title'],
        'desc': note['desc'],
        'author': note['author'],
        'interact': note['interact'],
        'tags': note['tags'],
        'images': note['images'],
        'video': note['video'],
        'local_images': local_images,
        'local_video': local_video,
        'ocr_results': ocr_results,
    }
    
    with open(output_dir / 'note.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 生成 Markdown
    md = f"""# {note['title']}

**作者**: [{note['author']['nickname']}](https://www.xiaohongshu.com/user/profile/{note['author']['user_id']})  
**点赞**: {note['interact']['liked_count']} | **收藏**: {note['interact']['collected_count']} | **评论**: {note['interact']['comment_count']}  
**标签**: {', '.join(['#' + t for t in note['tags']])}  
**抓取时间**: {result['fetch_time']}

---

## 正文

{note['desc']}

---

## 图片

"""
    
    for i, img_path in enumerate(local_images):
        img_name = Path(img_path).name
        md += f"### 图片 {i+1}\n\n"
        md += f"![{img_name}](images/{img_name})\n\n"
        
        for ocr in ocr_results:
            if ocr['image'] == img_name:
                md += f"**OCR 识别文字:**\n\n```\n{ocr['text']}\n```\n\n"
                break
    
    if local_video:
        md += f"\n## 视频\n\n[video.mp4](video.mp4)\n"
    
    with open(output_dir / 'note.md', 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"\n" + "=" * 60)
    print("✅ 抓取完成!")
    print("=" * 60)
    print(f"\n输出目录: {output_dir}")
    print(f"  - note.json    (结构化数据)")
    print(f"  - note.md      (Markdown 文档)")
    print(f"  - images/      ({len(local_images)} 张图片)")
    if local_video:
        print(f"  - video.mp4    (视频)")
    if ocr_results:
        print(f"  - OCR 结果已包含在 JSON 和 MD 中")


if __name__ == '__main__':
    main()
