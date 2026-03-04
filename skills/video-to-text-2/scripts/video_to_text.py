#!/usr/bin/env python3
"""
视频转文字工具
支持：
1. B站视频 - 使用 bilibili-api 下载
2. 其他视频 - 使用 yt-dlp 下载
3. 本地文件 - 直接转写
最后使用 faster-whisper 转写为文字
"""

import argparse
import os
import subprocess
import sys
import tempfile
import asyncio
import requests
from faster_whisper import WhisperModel


# B站认证信息（需要用户自行配置）
BILIBILI_CREDENTIALS = {
    "sessdata": "",
    "bili_jct": "",
    "buvid3": ""
}


def is_bilibili_url(url: str) -> bool:
    """检查是否为B站链接"""
    return "bilibili.com" in url or "b23.tv" in url


def extract_bvid(url: str) -> str:
    """从URL提取BV号"""
    import re
    # 匹配 BV 号
    match = re.search(r'BV[a-zA-Z0-9]{10}', url)
    if match:
        return match.group(0)
    # 短链 b23.tv
    if "b23.tv" in url:
        # 需要先解析短链
        return url
    return url


async def download_bilibili(url: str, output_path: str = None) -> str:
    """使用 bilibili-api 下载B站视频"""
    from bilibili_api import video, Credential
    
    if output_path is None:
        output_path = tempfile.mkdtemp()
    
    print(f"📥 正在下载B站视频: {url}")
    
    # 检查认证信息
    if not all(BILIBILI_CREDENTIALS.values()):
        print("❌ 请配置B站认证信息 (SESSDATA, bili_jct, buvid3)")
        sys.exit(1)
    
    # 创建认证对象
    credential = Credential(
        sessdata=BILIBILI_CREDENTIALS["sessdata"],
        bili_jct=BILIBILI_CREDENTIALS["bili_jct"],
        buvid3=BILIBILI_CREDENTIALS["buvid3"]
    )
    
    # 提取BV号
    bvid = extract_bvid(url)
    
    # 获取视频信息
    v = video.Video(bvid=bvid, credential=credential)
    info = await v.get_info()
    print(f"  标题: {info['title']}")
    print(f"  UP主: {info['owner']['name']}")
    
    # 获取下载链接
    print("  获取下载链接...")
    download_url = await v.get_download_url(page_index=0)
    
    # 获取音频URL
    dash = download_url['dash']
    if 'audio' in dash and dash['audio']:
        audio_url = dash['audio'][0]['baseUrl']
        
        # 下载音频
        print("  下载音频中...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        resp = requests.get(audio_url, headers=headers)
        
        # 保存文件
        safe_title = "".join(c for c in info['title'] if c.isalnum() or c in ' -_').strip()[:50]
        output_file = os.path.join(output_path, f"{safe_title}.m4a")
        with open(output_file, 'wb') as f:
            f.write(resp.content)
        
        print(f"✅ 下载完成: {output_file}")
        return output_file
    else:
        print("❌ 未找到音频流")
        sys.exit(1)


def download_with_ytdlp(url: str, output_path: str = None) -> str:
    """使用 yt-dlp 下载视频"""
    if output_path is None:
        output_path = tempfile.mkdtemp()
    
    print(f"📥 正在下载视频: {url}")
    
    # 使用 yt-dlp 下载最佳质量音频
    cmd = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "wav",
        "-o", os.path.join(output_path, "%(title)s.%(ext)s"),
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 下载失败: {result.stderr}")
        sys.exit(1)
    
    # 找到下载的文件
    files = [f for f in os.listdir(output_path) if f.endswith('.wav')]
    if not files:
        files = [f for f in os.listdir(output_path) if f.endswith(('.mp4', 'webm', 'mkv', 'm4a'))]
    
    if not files:
        print("❌ 未找到下载的文件")
        sys.exit(1)
    
    filepath = os.path.join(output_path, files[0])
    print(f"✅ 下载完成: {filepath}")
    return filepath


def transcribe_audio(audio_path: str, model_size: str = "base", language: str = None) -> str:
    """使用 Whisper 转写音频"""
    print(f"🔄 正在加载 Whisper {model_size} 模型...")
    
    compute_type = "int8"
    model = WhisperModel(model_size, compute_type=compute_type)
    
    print("📝 正在转写...")
    
    params = {
        "beam_size": 5,
        "vad_filter": True,
    }
    if language:
        params["language"] = language
    
    segments, info = model.transcribe(audio_path, **params)
    
    print(f"检测到语言: {info.language} (概率: {info.language_probability:.2f})")
    print("-" * 50)
    
    full_text = []
    for segment in segments:
        text = segment.text.strip()
        full_text.append(text)
        print(f"[{segment.start:.1f}s - {segment.end:.1f}s] {text}")
    
    return "\n".join(full_text)


def main():
    parser = argparse.ArgumentParser(description="视频转文字工具")
    parser.add_argument("url", help="视频URL (B站/YouTube等) 或本地文件路径")
    parser.add_argument("-m", "--model", default="base", 
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper模型大小 (默认: base)")
    parser.add_argument("-l", "--language", default=None,
                        help="指定语言 (如 zh, en)")
    parser.add_argument("-o", "--output", default=None,
                        help="输出文件路径 (默认: 打印到终端)")
    parser.add_argument("--keep-files", action="store_true",
                        help="保留下载的音视频文件")
    
    # B站认证参数
    parser.add_argument("--sessdata", default=None, help="B站 SESSDATA")
    parser.add_argument("--bili-jct", default=None, help="B站 bili_jct")
    parser.add_argument("--buvid3", default=None, help="B站 buvid3")
    
    args = parser.parse_args()
    
    # 更新认证信息（命令行参数优先）
    global BILIBILI_CREDENTIALS
    if args.sessdata:
        BILIBILI_CREDENTIALS["sessdata"] = args.sessdata
    if args.bili_jct:
        BILIBILI_CREDENTIALS["bili_jct"] = args.bili_jct
    if args.buvid3:
        BILIBILI_CREDENTIALS["buvid3"] = args.buvid3
    
    with tempfile.TemporaryDirectory() as temp_dir:
        url_or_path = args.url
        
        # 判断下载方式
        if is_bilibili_url(url_or_path):
            # B站视频
            audio_path = asyncio.run(download_bilibili(url_or_path, temp_dir))
        elif os.path.isfile(url_or_path):
            # 本地文件
            audio_path = url_or_path
            print(f"📁 使用本地文件: {audio_path}")
        else:
            # 其他视频网站
            audio_path = download_with_ytdlp(url_or_path, temp_dir)
        
        # 转写
        text = transcribe_audio(audio_path, args.model, args.language)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n✅ 结果已保存到: {args.output}")
        else:
            print(f"\n{'='*50}")
            print("转写结果:")
            print("="*50)
            print(text)
        
        if args.keep_files:
            print(f"\n📁 保留的文件在: {temp_dir}")


if __name__ == "__main__":
    main()
