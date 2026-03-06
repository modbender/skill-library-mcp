#!/usr/bin/env python3
"""
SMB 字幕自动下载与上传工具
完整功能：
1. 扫描 SMB 共享中的视频文件
2. 使用 OpenSubtitles API 下载字幕
3. 将字幕上传到对应文件夹
"""

from smb.SMBConnection import SMBConnection
import os
import sys
import json
import re
import tempfile
import requests
from pathlib import Path
from io import BytesIO

# SMB 配置
SMB_CONFIG = {
    "username": "13917908083",
    "password": "Roger0808",
    "server_name": "Z4ProPlus-X6L8",
    "server_ip": "192.168.1.246",
    "share_name": "super8083",
    "remote_path": "qb/downloads"
}

# OpenSubtitles 配置
OPENSUBTITLES_API_KEY = "CBfNpndpF56j2TsGJuaicd8AAwx0rS2R"
OPENSUBTITLES_API = "https://api.opensubtitles.com/api/v1"
DEFAULT_LANGUAGES = ["zh-cn", "en"]

class SMBSubtitleManager:
    def __init__(self):
        self.conn = None
        self.video_files = []
        self.stats = {
            "total": 0,
            "skipped": 0,
            "downloaded": 0,
            "failed": 0
        }
        
    def connect(self):
        """连接 SMB 服务器"""
        self.conn = SMBConnection(
            SMB_CONFIG["username"],
            SMB_CONFIG["password"],
            "openclaw-client",
            SMB_CONFIG["server_name"],
            use_ntlm_v2=True
        )
        
        print(f"🔌 正在连接 SMB 服务器 {SMB_CONFIG['server_ip']}...")
        
        connected = self.conn.connect(SMB_CONFIG["server_ip"], 445, timeout=10)
        
        if connected:
            print("✅ SMB 连接成功!\\n")
            return True
        else:
            print("❌ SMB 连接失败")
            return False
    
    def parse_video_info(self, filename):
        """解析视频文件名提取剧集信息"""
        # TV Show 模式: ShowName.S01E02.xxx
        tv_match = re.search(r'([^.]+)\.S(\d+)E(\d+)', filename, re.IGNORECASE)
        
        # 电影模式: Movie.Name.2023.xxx
        movie_match = re.search(r'^(.+?)\s*(\d{4})', filename)
        
        if tv_match:
            show_name = tv_match.group(1).replace('.', ' ')
            season = int(tv_match.group(2))
            episode = int(tv_match.group(3))
            return {
                'type': 'tv',
                'title': show_name,
                'season': season,
                'episode': episode,
                'query': f"{show_name} S{season:02d}E{episode:02d}"
            }
        elif movie_match:
            movie_name = movie_match.group(1).replace('.', ' ').strip()
            year = movie_match.group(2)
            return {
                'type': 'movie',
                'title': movie_name,
                'year': year,
                'query': f"{movie_name} {year}"
            }
        else:
            # 默认使用文件名
            title = os.path.splitext(filename)[0].replace('.', ' ')
            return {
                'type': 'unknown',
                'title': title,
                'query': title
            }
    
    def scan_videos(self, subdir=""):
        """递归扫描视频文件"""
        path = f"{SMB_CONFIG['remote_path']}/{subdir}".strip("/")
        
        try:
            files = self.conn.listPath(SMB_CONFIG["share_name"], path)
            
            for f in files:
                if f.filename in ['.', '..', '.DS_Store']:
                    continue
                
                relative_path = f"{subdir}/{f.filename}".strip("/") if subdir else f.filename
                full_remote_path = f"{path}/{f.filename}".strip("/")
                
                if f.isDirectory:
                    # 递归扫描子目录
                    self.scan_videos(relative_path)
                else:
                    # 检查是否是视频文件
                    video_exts = ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
                    if any(f.filename.lower().endswith(ext) for ext in video_exts):
                        video_info = self.parse_video_info(f.filename)
                        video_info.update({
                            'filename': f.filename,
                            'remote_path': full_remote_path,
                            'relative_dir': subdir,
                            'size': f.file_size
                        })
                        self.video_files.append(video_info)
                        
        except Exception as e:
            print(f"⚠️  扫描目录失败 {path}: {e}")
    
    def check_existing_subtitles(self, video_info):
        """检查是否已存在字幕文件"""
        base_name = os.path.splitext(video_info['filename'])[0]
        subtitle_extensions = ['.srt', '.ass', '.vtt', '.sub']
        existing = []
        
        for ext in subtitle_extensions:
            for lang in ['zh-cn', 'zh', 'en']:
                sub_name = f"{base_name}.{lang}{ext}"
                sub_path = f"{video_info['relative_dir']}/{sub_name}".strip("/")
                full_path = f"{SMB_CONFIG['remote_path']}/{sub_path}".strip("/")
                
                try:
                    self.conn.getAttributes(SMB_CONFIG["share_name"], full_path)
                    existing.append(sub_name)
                except:
                    pass
        
        return existing
    
    def search_opensubtitles(self, video_info):
        """搜索 OpenSubtitles 字幕"""
        params = {
            'query': video_info['query']
        }
        
        if video_info.get('season'):
            params['season_number'] = video_info['season']
        if video_info.get('episode'):
            params['episode_number'] = video_info['episode']
        
        # 搜索所有语言
        params['languages'] = ','.join(DEFAULT_LANGUAGES)
        
        try:
            response = requests.get(
                f"{OPENSUBTITLES_API}/subtitles",
                params=params,
                headers={
                    'Api-Key': OPENSUBTITLES_API_KEY,
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   ⚠️  API 错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ⚠️  搜索失败: {e}")
            return None
    
    def download_subtitle_file(self, file_id):
        """从 OpenSubtitles 下载字幕文件"""
        try:
            response = requests.post(
                f"{OPENSUBTITLES_API}/download",
                headers={
                    'Api-Key': OPENSUBTITLES_API_KEY,
                    'Content-Type': 'application/json'
                },
                json={'file_id': file_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                download_link = data.get('link')
                
                if download_link:
                    # 下载实际文件
                    file_response = requests.get(download_link, timeout=60)
                    if file_response.status_code == 200:
                        return file_response.content
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  下载失败: {e}")
            return None
    
    def upload_subtitle_to_smb(self, subtitle_content, video_info, lang, file_ext):
        """上传字幕到 SMB"""
        base_name = os.path.splitext(video_info['filename'])[0]
        sub_filename = f"{base_name}.{lang}.{file_ext}"
        
        remote_path = f"{SMB_CONFIG['remote_path']}/{video_info['relative_dir']}/{sub_filename}".strip("/")
        
        try:
            # 使用 BytesIO 上传
            file_obj = BytesIO(subtitle_content)
            self.conn.storeFile(SMB_CONFIG["share_name"], remote_path, file_obj)
            return True
            
        except Exception as e:
            print(f"   ⚠️  上传失败: {e}")
            return False
    
    def process_video(self, video_info):
        """处理单个视频文件"""
        print(f"\\n🎬 {video_info['filename']}")
        print(f"   📺 识别: {video_info['query']}")
        
        # 检查现有字幕
        existing = self.check_existing_subtitles(video_info)
        if existing:
            print(f"   ⏭️  已存在字幕: {', '.join(existing)}")
            self.stats["skipped"] += 1
            return True
        
        # 搜索字幕
        print(f"   🔍 搜索字幕...")
        search_result = self.search_opensubtitles(video_info)
        
        if not search_result or 'data' not in search_result:
            print(f"   ❌ 搜索失败或无结果")
            self.stats["failed"] += 1
            return False
        
        subtitles = search_result['data']
        if not subtitles:
            print(f"   ❌ 未找到字幕")
            self.stats["failed"] += 1
            return False
        
        print(f"   ✅ 找到 {len(subtitles)} 个字幕")
        
        # 按语言下载最佳字幕
        downloaded = []
        for lang in DEFAULT_LANGUAGES:
            # 查找该语言的最佳字幕（按评分排序）
            lang_subs = [
                s for s in subtitles 
                if s.get('attributes', {}).get('language') == lang
            ]
            
            if not lang_subs:
                continue
            
            # 按评分排序
            lang_subs.sort(
                key=lambda x: float(x.get('attributes', {}).get('ratings', 0) or 0),
                reverse=True
            )
            
            best_sub = lang_subs[0]
            file_id = best_sub.get('attributes', {}).get('files', [{}])[0].get('file_id')
            
            if not file_id:
                continue
            
            print(f"   📥 下载 {lang} 字幕...")
            
            subtitle_content = self.download_subtitle_file(file_id)
            if subtitle_content:
                file_ext = best_sub.get('attributes', {}).get('format', 'srt')
                
                if self.upload_subtitle_to_smb(subtitle_content, video_info, lang, file_ext):
                    print(f"   ✅ {lang} 字幕上传成功")
                    downloaded.append(lang)
                else:
                    print(f"   ❌ {lang} 字幕上传失败")
        
        if downloaded:
            self.stats["downloaded"] += 1
            return True
        else:
            self.stats["failed"] += 1
            return False
    
    def process_all(self):
        """处理所有视频文件"""
        print("="*60)
        print("🎥 SMB 字幕自动下载工具")
        print("="*60)
        print(f"\\n📡 服务器: {SMB_CONFIG['server_ip']}")
        print(f"📁 共享: {SMB_CONFIG['share_name']}")
        print(f"📂 路径: {SMB_CONFIG['remote_path']}")
        print(f"🌐 字幕语言: {', '.join(DEFAULT_LANGUAGES)}")
        print()
        
        # 连接 SMB
        if not self.connect():
            return False
        
        # 扫描视频文件
        print("🔍 正在扫描视频文件...")
        self.scan_videos()
        
        self.stats["total"] = len(self.video_files)
        print(f"\\n📊 找到 {self.stats['total']} 个视频文件\\n")
        
        if not self.video_files:
            print("❌ 没有找到视频文件")
            self.conn.close()
            return False
        
        # 按剧集分组显示
        series_groups = {}
        for v in self.video_files:
            title = v.get('title', 'Unknown')
            if title not in series_groups:
                series_groups[title] = []
            series_groups[title].append(v)
        
        print("📋 发现的内容:")
        for title, videos in series_groups.items():
            if videos[0].get('type') == 'tv' and videos[0].get('season'):
                seasons = set(v.get('season') for v in videos if v.get('season'))
                print(f"   📺 {title} - {len(videos)} 集 (季: {', '.join(map(str, sorted(seasons)))})")
            else:
                print(f"   🎬 {title} - {len(videos)} 个文件")
        print()
        
        # 处理每个视频
        for i, video in enumerate(self.video_files, 1):
            print(f"\\n[{i}/{self.stats['total']}]", end="")
            self.process_video(video)
        
        # 显示统计
        print(f"\\n{'='*60}")
        print("📊 处理完成!")
        print(f"   总计: {self.stats['total']} 个视频")
        print(f"   ⏭️  跳过 (已有字幕): {self.stats['skipped']}")
        print(f"   ✅ 下载成功: {self.stats['downloaded']}")
        print(f"   ❌ 失败: {self.stats['failed']}")
        print(f"{'='*60}")
        
        self.conn.close()
        print("\\n🔌 SMB 连接已关闭")
        return True

def main():
    manager = SMBSubtitleManager()
    success = manager.process_all()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
