#!/usr/bin/env python3
"""
SMB 字幕下载与上传工具
功能：
1. 连接到 SMB 服务器浏览视频文件
2. 为每个视频下载字幕
3. 将字幕上传到 SMB 共享中对应的位置
"""

from smb.SMBConnection import SMBConnection
import os
import sys
import subprocess
import json
from pathlib import Path

# SMB 配置
SMB_CONFIG = {
    "username": "13917908083",
    "password": "Roger0808",
    "server_name": "Z4ProPlus-X6L8",
    "server_ip": "192.168.1.246",
    "share_name": "super8083",
    "remote_path": "qb/downloads"
}

# 字幕语言设置
SUBTITLE_LANGUAGES = "zh-cn,en"

class SMBSubtitleDownloader:
    def __init__(self):
        self.conn = None
        self.video_files = []
        self.downloaded_subtitles = []
        
    def connect(self):
        """连接 SMB 服务器"""
        self.conn = SMBConnection(
            SMB_CONFIG["username"],
            SMB_CONFIG["password"],
            "openclaw-client",
            SMB_CONFIG["server_name"],
            use_ntlm_v2=True
        )
        
        print(f"正在连接 SMB 服务器 {SMB_CONFIG['server_ip']}...")
        connected = self.conn.connect(SMB_CONFIG["server_ip"], 445, timeout=10)
        
        if connected:
            print("✓ SMB 连接成功!\\n")
            return True
        else:
            print("✗ SMB 连接失败")
            return False
    
    def scan_videos(self, subdir=""):
        """递归扫描视频文件"""
        path = f"{SMB_CONFIG['remote_path']}/{subdir}".strip("/")
        
        try:
            files = self.conn.listPath(SMB_CONFIG["share_name"], path)
            
            for f in files:
                if f.filename in ['.', '..', '.DS_Store']:
                    continue
                
                full_path = f"{path}/{f.filename}".strip("/")
                relative_path = f"{subdir}/{f.filename}".strip("/") if subdir else f.filename
                
                if f.isDirectory:
                    # 递归扫描子目录
                    self.scan_videos(relative_path)
                else:
                    # 检查是否是视频文件
                    video_exts = ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
                    if any(f.filename.lower().endswith(ext) for ext in video_exts):
                        self.video_files.append({
                            'filename': f.filename,
                            'remote_path': full_path,
                            'relative_dir': subdir,
                            'size': f.file_size
                        })
                        
        except Exception as e:
            print(f"扫描目录失败 {path}: {e}")
    
    def download_subtitle(self, video_info):
        """为单个视频下载字幕"""
        filename = video_info['filename']
        print(f"\\n处理: {filename}")
        
        # 创建本地临时目录
        temp_dir = "/tmp/smb_subtitles"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 检查是否已有字幕文件
        base_name = os.path.splitext(filename)[0]
        subtitle_extensions = ['.srt', '.ass', '.vtt', '.sub']
        
        existing_subtitles = []
        for ext in subtitle_extensions:
            for lang in ['zh-cn', 'en', 'zh']:
                sub_name = f"{base_name}.{lang}{ext}"
                try:
                    self.conn.getAttributes(SMB_CONFIG["share_name"], 
                                          f"{video_info['remote_path']}/{sub_name}")
                    existing_subtitles.append(sub_name)
                except:
                    pass
        
        if existing_subtitles:
            print(f"  ⏭️  已存在字幕: {', '.join(existing_subtitles)}")
            return True
        
        # 使用 OpenSubtitles 下载字幕
        print(f"  🔍 正在搜索字幕...")
        
        # 解析视频信息
        # 从文件名提取剧集信息
        import re
        
        # TV Show 模式: ShowName.S01E02...
        tv_match = re.search(r'([^.]+)\.S(\d+)E(\d+)', filename, re.IGNORECASE)
        # 电影模式
        movie_match = re.search(r'^(.+?)\s*(\d{4})', filename)
        
        if tv_match:
            show_name = tv_match.group(1).replace('.', ' ')
            season = int(tv_match.group(2))
            episode = int(tv_match.group(3))
            print(f"  📺 识别为: {show_name} S{season:02d}E{episode:02d}")
            query = f"{show_name} S{season:02d}E{episode:02d}"
        elif movie_match:
            movie_name = movie_match.group(1).replace('.', ' ').strip()
            year = movie_match.group(2)
            print(f"  🎬 识别为: {movie_name} ({year})")
            query = f"{movie_name} {year}"
        else:
            query = os.path.splitext(filename)[0].replace('.', ' ')
            print(f"  🎥 使用文件名搜索: {query}")
        
        # 这里可以调用 opensubtitles API 下载字幕
        # 由于需要 API 密钥，这里先创建一个占位符
        print(f"  ⚠️  字幕下载功能需要配置 OpenSubtitles API")
        print(f"     搜索关键词: {query}")
        
        return False
    
    def upload_subtitle(self, local_file, remote_dir, remote_filename):
        """上传字幕到 SMB"""
        try:
            remote_path = f"{SMB_CONFIG['remote_path']}/{remote_dir}/{remote_filename}".strip("/")
            
            with open(local_file, 'rb') as f:
                self.conn.storeFile(SMB_CONFIG["share_name"], remote_path, f)
            
            print(f"  ✓ 上传成功: {remote_filename}")
            return True
            
        except Exception as e:
            print(f"  ✗ 上传失败: {e}")
            return False
    
    def process_all(self):
        """处理所有视频文件"""
        print("="*60)
        print("SMB 字幕下载工具")
        print("="*60)
        print(f"\\n服务器: {SMB_CONFIG['server_ip']}")
        print(f"共享: {SMB_CONFIG['share_name']}")
        print(f"路径: {SMB_CONFIG['remote_path']}")
        print(f"字幕语言: {SUBTITLE_LANGUAGES}")
        print()
        
        # 连接 SMB
        if not self.connect():
            return False
        
        # 扫描视频文件
        print("正在扫描视频文件...")
        self.scan_videos()
        
        print(f"\\n找到 {len(self.video_files)} 个视频文件\\n")
        
        if not self.video_files:
            print("没有找到视频文件")
            self.conn.close()
            return False
        
        # 处理每个视频
        processed = 0
        skipped = 0
        failed = 0
        
        for video in self.video_files:
            result = self.download_subtitle(video)
            if result:
                processed += 1
            else:
                skipped += 1
        
        print(f"\\n{'='*60}")
        print("处理完成!")
        print(f"  总计: {len(self.video_files)} 个视频")
        print(f"  已有字幕: {skipped} 个")
        print(f"  待下载: {len(self.video_files) - processed - skipped} 个")
        print(f"{'='*60}")
        
        self.conn.close()
        return True

def main():
    downloader = SMBSubtitleDownloader()
    success = downloader.process_all()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
