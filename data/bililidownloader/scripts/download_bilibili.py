#!/usr/bin/env python3
"""
Bilibili视频下载器
支持单个视频和系列视频的下载，提供格式和清晰度选择
"""

import subprocess
import argparse
import json
import sys
from typing import Dict, List, Optional


def get_video_info(url: str) -> Dict:
    """
    获取视频信息
    """
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"获取视频信息失败: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"解析视频信息失败: {e}")
        return {}


def get_playlist_info(url: str) -> Dict:
    """
    获取播放列表信息
    """
    try:
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--dump-json",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # 解析每一行JSON
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line:
                videos.append(json.loads(line))
        
        return {
            "entries": videos,
            "count": len(videos)
        }
    except subprocess.CalledProcessError as e:
        print(f"获取播放列表信息失败: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"解析播放列表信息失败: {e}")
        return {}


def list_formats(url: str) -> List[Dict]:
    """
    列出可用的视频格式
    """
    try:
        cmd = [
            "yt-dlp",
            "--list-formats",
            "--dump-json",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        formats = []
        if 'formats' in data:
            formats = data['formats']
        elif 'entries' in data and len(data['entries']) > 0:
            formats = data['entries'][0].get('formats', [])
            
        return formats
    except subprocess.CalledProcessError as e:
        print(f"获取格式信息失败: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"解析格式信息失败: {e}")
        return []


def display_formats(formats: List[Dict]):
    """
    显示可用格式
    """
    print("\n可用视频格式:")
    print("-" * 80)
    print(f"{'ID':<10} {'分辨率':<15} {'格式':<10} {'大小':<15} {'备注'}")
    print("-" * 80)
    
    for fmt in formats:
        format_id = fmt.get('format_id', 'N/A')
        resolution = f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}"
        ext = fmt.get('ext', 'N/A')
        filesize = fmt.get('filesize', fmt.get('filesize_approx', 'N/A'))
        
        if filesize != 'N/A':
            if filesize > 1024*1024*1024:  # 大于1GB
                filesize_str = f"{filesize/(1024*1024*1024):.1f}GB"
            elif filesize > 1024*1024:  # 大于1MB
                filesize_str = f"{filesize/(1024*1024):.1f}MB"
            elif filesize > 1024:  # 大于1KB
                filesize_str = f"{filesize/1024:.1f}KB"
            else:
                filesize_str = f"{filesize}B"
        else:
            filesize_str = 'N/A'
            
        note = []
        if fmt.get('vcodec') != 'none':
            note.append(fmt.get('vcodec', ''))
        if fmt.get('acodec') != 'none':
            note.append(fmt.get('acodec', ''))
        if fmt.get('fps'):
            note.append(f"{fmt.get('fps')}fps")
            
        note_str = ', '.join(note)
        
        print(f"{format_id:<10} {resolution:<15} {ext:<10} {filesize_str:<15} {note_str}")


def download_video(url: str, format_choice: Optional[str] = None, output_dir: str = "./"):
    """
    下载单个视频
    """
    try:
        cmd = ["yt-dlp"]
        
        if format_choice:
            cmd.extend(["-f", format_choice])
        
        # 设置输出格式
        cmd.extend([
            "-o", f"{output_dir}/%(title)s-[%(id)s].%(ext)s",
            "--progress",
            url
        ])
        
        print(f"开始下载视频: {url}")
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("视频下载成功!")
            return True
        else:
            print("视频下载失败!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        return False


def download_playlist(url: str, format_choice: Optional[str] = None, output_dir: str = "./"):
    """
    下载播放列表中的所有视频
    """
    try:
        cmd = ["yt-dlp"]
        
        if format_choice:
            cmd.extend(["-f", format_choice])
        
        # 设置输出格式
        cmd.extend([
            "-o", f"{output_dir}/%(playlist_title)s/%%(playlist_index)d. %%(title)s-[%%(id)s].%%(ext)s",
            "--progress",
            url
        ])
        
        print(f"开始下载播放列表: {url}")
        result = subprocess.run(cmd, check=True)
        
        if result.returncode == 0:
            print("播放列表下载成功!")
            return True
        else:
            print("播放列表下载失败!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Bilibili Video Downloader")
    parser.add_argument("url", help="Bilibili video URL")
    parser.add_argument("--format", "-f", dest="format_choice", help="Video format ID")
    parser.add_argument("--batch", action="store_true", help="Download entire series/playlist if detected")
    parser.add_argument("--no-batch", action="store_true", help="Only download single video even if playlist detected")
    parser.add_argument("--interactive", "-i", action="store_true", help="Enable interactive prompts")

    args = parser.parse_args()
    
    url = args.url
    format_choice = args.format_choice
    
    print("正在分析视频信息...")
    
    # 获取视频信息
    info = get_video_info(url)
    
    if not info:
        print("无法获取视频信息，请检查链接是否正确")
        sys.exit(1)
    
    # 检查是否为播放列表
    is_playlist = 'entries' in info and len(info['entries']) > 1
    
    if is_playlist:
        print(f"\n检测到系列视频: {info.get('title', '未知标题')}")
        print(f"视频总数: {len(info['entries'])}")
        
        # 获取播放列表详细信息
        playlist_info = get_playlist_info(url)
        if playlist_info:
            print(f"实际视频数量: {playlist_info.get('count', '未知')}")
        
        # 询问是否批量下载
        batch_download = False
        if args.batch:
            batch_download = True
        elif args.no_batch:
            batch_download = False
        elif args.interactive:
            while True:
                choice = input("\n是否批量下载整个系列? (y/n): ").lower()
                if choice in ['y', 'yes']:
                    batch_download = True
                    break
                elif choice in ['n', 'no']:
                    batch_download = False
                    break
                else:
                    print("请输入 y 或 n")
        else:
            # Default to no batch in non-interactive mode unless specified
            print("检测到播放列表，但未指定 --batch，默认仅下载当前视频。")
            batch_download = False
        
        if batch_download:
            # 获取格式信息
            formats = list_formats(url)
            if formats:
                display_formats(formats)
                
                if not format_choice:
                    if args.interactive:
                        format_choice = input("\n请选择格式ID (直接回车使用最佳格式): ").strip()
                        if not format_choice:
                            format_choice = None
                    else:
                        print("\n未指定格式，使用最佳格式。")
                        format_choice = None
                
                # 执行批量下载
                success = download_playlist(url, format_choice)
                
                if success:
                    print("\n所有视频下载完成!")
                else:
                    print("\n下载过程中出现错误!")
            else:
                print("无法获取格式信息，使用默认设置下载")
                success = download_playlist(url, format_choice)
                
                if success:
                    print("\n所有视频下载完成!")
                else:
                    print("\n下载过程中出现错误!")
        else:
            print("仅下载当前视频")
            # 获取当前视频的格式信息
            formats = list_formats(url)
            if formats:
                display_formats(formats)
                
                if not format_choice:
                    if args.interactive:
                        format_choice = input("\n请选择格式ID (直接回车使用最佳格式): ").strip()
                        if not format_choice:
                            format_choice = None
                    else:
                        print("\n未指定格式，使用最佳格式。")
                        format_choice = None
                
                # 执行下载
                success = download_video(url, format_choice)
                
                if success:
                    print("\n视频下载完成!")
                else:
                    print("\n下载过程中出现错误!")
            else:
                print("无法获取格式信息，使用默认设置下载")
                success = download_video(url, format_choice)
                
                if success:
                    print("\n视频下载完成!")
                else:
                    print("\n下载过程中出现错误!")
    else:
        # 单个视频
        print(f"\n检测到单个视频: {info.get('title', '未知标题')}")
        
        # 获取格式信息
        formats = list_formats(url)
        if formats:
            display_formats(formats)
            
            if not format_choice:
                if args.interactive:
                    format_choice = input("\n请选择格式ID (直接回车使用最佳格式): ").strip()
                    if not format_choice:
                        format_choice = None
                else:
                    print("\n未指定格式，使用最佳格式。")
                    format_choice = None
            
            # 执行下载
            success = download_video(url, format_choice)
            
            if success:
                print("\n视频下载完成!")
            else:
                print("\n下载过程中出现错误!")
        else:
            print("无法获取格式信息，使用默认设置下载")
            success = download_video(url, format_choice)
            
            if success:
                print("\n视频下载完成!")
            else:
                print("\n下载过程中出现错误!")


if __name__ == "__main__":
    main()