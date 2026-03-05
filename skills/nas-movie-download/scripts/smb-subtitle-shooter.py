#!/usr/bin/env python3
"""
SMB 字幕自动下载与上传工具 (使用伪射手 API)
伪射手 API: https://www.shooter.cn/api/ 的第三方镜像
"""

from smb.SMBConnection import SMBConnection
import os
import sys
import re
import time
import json
import hashlib
import tempfile
import requests
from io import BytesIO
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

# 伪射手 API 配置
SHOOTER_API = "https://www.shooter.cn/api/subapi.php"

def calculate_file_hash(filepath):
    """计算射手网的文件哈希"""
    # 射手网哈希算法：文件前 4KB、中间 4KB、最后 4KB 的 MD5
    if not os.path.exists(filepath):
        return None
    
    size = os.path.getsize(filepath)
    if size < 8192:
        # 小文件：整个文件 MD5
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    hashes = []
    with open(filepath, 'rb') as f:
        # 前 4KB
        hashes.append(hashlib.md5(f.read(4096)).hexdigest())
        
        # 中间 4KB
        f.seek(size // 2)
        hashes.append(hashlib.md5(f.read(4096)).hexdigest())
        
        # 最后 4KB
        f.seek(-4096, 2)
        hashes.append(hashlib.md5(f.read(4096)).hexdigest())
    
    return ';'.join(hashes)

class ShooterSubtitleDownloader:
    """射手网字幕下载器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_by_filename(self, filename, language='Chn'):
        """使用文件名搜索字幕"""
        try:
            # 射手网 API 参数
            params = {
                'filehash': '',
                'pathinfo': filename,
                'format': 'json',
                'lang': language
            }
            
            print(f"   🔍 搜索射手网: {filename[:50]}...")
            
            response = self.session.post(SHOOTER_API, data=params, timeout=30)
            
            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []
            
            try:
                data = response.json()
            except:
                # 可能没有字幕，返回空
                return []
            
            if not data or not isinstance(data, list):
                return []
            
            subtitles = []
            for item in data:
                if 'Files' in item:
                    for file_info in item['Files']:
                        subtitles.append({
                            'ext': file_info.get('Ext', 'srt'),
                            'link': file_info.get('Link', ''),
                            'delay': file_info.get('Delay', 0)
                        })
            
            return subtitles
            
        except Exception as e:
            print(f"   ⚠️  搜索失败: {e}")
            return []
    
    def download_subtitle(self, link):
        """下载字幕文件"""
        try:
            response = self.session.get(link, timeout=30)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"   ⚠️  下载失败: {e}")
            return None

class SMBSubtitleManager:
    def __init__(self):
        self.conn = None
        self.video_files = []
        self.temp_dir = tempfile.mkdtemp(prefix="smb_subtitles_")
        self.stats = {"total": 0, "skipped": 0, "downloaded": 0, "failed": 0}
        self.subtitle_downloader = ShooterSubtitleDownloader()
        
    def connect(self):
        self.conn = SMBConnection(
            SMB_CONFIG["username"], SMB_CONFIG["password"],
            "openclaw-client", SMB_CONFIG["server_name"], use_ntlm_v2=True
        )
        print("🔌 连接 SMB...", end=" ")
        connected = self.conn.connect(SMB_CONFIG["server_ip"], 445, timeout=10)
        if connected:
            print("✅")
            return True
        else:
            print("❌")
            return False
    
    def parse_video_info(self, filename):
        """解析视频文件名"""
        tv_match = re.search(r'([^.]+)\.S(\d+)E(\d+)', filename, re.IGNORECASE)
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
            title = os.path.splitext(filename)[0].replace('.', ' ')
            return {'type': 'unknown', 'title': title, 'query': title}
    
    def scan_videos(self, subdir=""):
        path = f"{SMB_CONFIG['remote_path']}/{subdir}".strip("/")
        try:
            files = self.conn.listPath(SMB_CONFIG["share_name"], path)
            for f in files:
                if f.filename in ['.', '..', '.DS_Store']:
                    continue
                relative_path = f"{subdir}/{f.filename}".strip("/") if subdir else f.filename
                full_remote_path = f"{path}/{f.filename}".strip("/")
                
                if f.isDirectory:
                    self.scan_videos(relative_path)
                else:
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
            print(f"⚠️ 扫描失败 {path}: {e}")
    
    def check_existing_subtitles(self, video_info):
        base_name = os.path.splitext(video_info['filename'])[0]
        for ext in ['.srt', '.ass', '.vtt', '.ssa']:
            for suffix in ['.zh', '.zh-cn', '.en', '.chs', '']:
                sub_name = f"{base_name}{suffix}{ext}" if suffix else f"{base_name}{ext}"
                sub_path = f"{video_info['relative_dir']}/{sub_name}".strip("/")
                full_path = f"{SMB_CONFIG['remote_path']}/{sub_path}".strip("/")
                try:
                    self.conn.getAttributes(SMB_CONFIG["share_name"], full_path)
                    return True
                except:
                    pass
        return False
    
    def download_subtitles(self, video_info):
        """下载字幕"""
        filename = video_info['filename']
        
        # 尝试用文件名搜索
        subtitles = self.subtitle_downloader.search_by_filename(filename, 'Chn')
        
        if not subtitles:
            # 尝试用查询词搜索
            query = video_info['query']
            subtitles = self.subtitle_downloader.search_by_filename(query, 'Chn')
        
        if not subtitles:
            return []
        
        print(f"   ✅ 找到 {len(subtitles)} 个字幕")
        
        downloaded_files = []
        for i, sub in enumerate(subtitles):
            link = sub.get('link', '')
            ext = sub.get('ext', 'srt')
            
            if not link:
                continue
            
            print(f"   📥 下载字幕 {i+1}/{len(subtitles)}...")
            data = self.subtitle_downloader.download_subtitle(link)
            
            if data:
                # 保存到临时文件
                local_path = os.path.join(self.temp_dir, f"subtitle_{i}.{ext}")
                with open(local_path, 'wb') as f:
                    f.write(data)
                downloaded_files.append(local_path)
        
        return downloaded_files
    
    def upload_subtitle(self, local_sub_path, video_info, index=0):
        """上传字幕到 SMB"""
        sub_filename = os.path.basename(local_sub_path)
        video_base = os.path.splitext(video_info['filename'])[0]
        sub_ext = os.path.splitext(sub_filename)[1]
        
        if index == 0:
            final_name = f"{video_base}.zh{sub_ext}"
        else:
            final_name = f"{video_base}.zh.{index}{sub_ext}"
        
        remote_path = f"{SMB_CONFIG['remote_path']}/{video_info['relative_dir']}/{final_name}".strip("/")
        
        try:
            with open(local_sub_path, 'rb') as f:
                self.conn.storeFile(SMB_CONFIG["share_name"], remote_path, f)
            return final_name
        except Exception as e:
            print(f"   ⚠️ 上传失败: {e}")
            return None
    
    def process_video(self, video_info):
        self.stats["total"] += 1
        print(f"\\n🎬 [{self.stats['total']}/{len(self.video_files)}] {video_info['filename']}")
        print(f"   📺 识别: {video_info['query']}")
        
        if self.check_existing_subtitles(video_info):
            print("   ⏭️ 已有字幕，跳过")
            self.stats["skipped"] += 1
            return True
        
        subtitle_files = self.download_subtitles(video_info)
        
        if not subtitle_files:
            print("   ❌ 未找到字幕")
            self.stats["failed"] += 1
            return False
        
        uploaded = 0
        for i, sub_file in enumerate(subtitle_files):
            result = self.upload_subtitle(sub_file, video_info, i)
            if result:
                print(f"   📤 上传: {result}")
                uploaded += 1
            os.remove(sub_file)
        
        if uploaded > 0:
            print("   ✅ 完成")
            self.stats["downloaded"] += 1
            return True
        else:
            print("   ❌ 上传失败")
            self.stats["failed"] += 1
            return False
    
    def process_batch(self, start_idx=0, batch_size=10):
        end_idx = min(start_idx + batch_size, len(self.video_files))
        batch = self.video_files[start_idx:end_idx]
        
        print(f"\\n📦 处理第 {start_idx+1}-{end_idx} 个视频\\n")
        
        for video in batch:
            self.process_video(video)
            time.sleep(1)  # 避免请求过快
        
        return end_idx < len(self.video_files)
    
    def run(self, start_idx=0, batch_size=10):
        print("="*60)
        print("🎥 SMB 字幕下载工具 (射手网 API)")
        print("="*60)
        
        if not self.connect():
            return False
        
        print("🔍 扫描视频文件...")
        self.scan_videos()
        print(f"✅ 找到 {len(self.video_files)} 个视频\\n")
        
        if not self.video_files:
            print("❌ 没有找到视频")
            self.conn.close()
            return False
        
        # 显示内容
        series_groups = {}
        for v in self.video_files:
            title = v.get('title', 'Unknown')
            if title not in series_groups:
                series_groups[title] = []
            series_groups[title].append(v)
        
        print("📋 发现的内容:")
        for title, videos in series_groups.items():
            if videos[0].get('type') == 'tv':
                print(f"   📺 {title} - {len(videos)} 集")
            else:
                print(f"   🎬 {title}")
        print()
        
        # 处理批次
        has_more = self.process_batch(start_idx, batch_size)
        
        print(f"\\n{'='*60}")
        print("📊 统计:")
        print(f"   已处理: {self.stats['total']}")
        print(f"   跳过: {self.stats['skipped']}")
        print(f"   成功: {self.stats['downloaded']}")
        print(f"   失败: {self.stats['failed']}")
        if has_more:
            print(f"\\n📦 还有 {len(self.video_files) - self.stats['total']} 个视频")
            print(f"   继续: python3 {sys.argv[0]} {self.stats['total']}")
        print(f"{'='*60}")
        
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        self.conn.close()
        print("\\n🔌 SMB 连接已关闭")
        return True

def main():
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    manager = SMBSubtitleManager()
    return 0 if manager.run(start_idx, batch_size) else 1

if __name__ == "__main__":
    sys.exit(main())
