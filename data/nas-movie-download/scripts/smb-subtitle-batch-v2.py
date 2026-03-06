#!/usr/bin/env python3
"""
SMB 字幕自动下载与上传工具 (分批处理版)
使用射手网 API (assrt.net) 下载字幕
"""

from smb.SMBConnection import SMBConnection
import os
import sys
import re
import time
import json
import tempfile
import requests
import zipfile
import io
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

# 字幕源配置
SUBTITLE_APIS = {
    "assrt": {
        "name": "射手网",
        "token": "",  # 可选：如果有 token 可以用
        "base_url": "https://api.assrt.net/v1"
    }
}

class AssrtSubtitleDownloader:
    """射手网字幕下载器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_subtitles(self, query, limit=5):
        """搜索字幕"""
        try:
            # 射手网搜索
            search_url = "https://assrt.net/sub/"
            params = {'searchword': query}
            
            print(f"   🔍 射手网搜索: {query}")
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []
            
            # 解析搜索结果
            results = []
            import re
            
            # 查找字幕详情链接
            pattern = r'href="(/sub/\d+/[^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, response.text)
            
            for link, title in matches[:limit]:
                results.append({
                    'title': title.strip(),
                    'url': f"https://assrt.net{link}",
                    'link': link
                })
            
            return results
            
        except Exception as e:
            print(f"   ⚠️  搜索失败: {e}")
            return []
    
    def download_subtitle(self, detail_url):
        """下载字幕"""
        try:
            # 获取详情页
            response = self.session.get(detail_url, timeout=10)
            if response.status_code != 200:
                return None
            
            import re
            # 查找下载链接
            pattern = r'href="(/download/[^"]+)"'
            match = re.search(pattern, response.text)
            
            if not match:
                return None
            
            download_url = f"https://assrt.net{match.group(1)}"
            print(f"   📥 下载: {download_url[:50]}...")
            
            # 下载字幕
            dl_response = self.session.get(download_url, timeout=30)
            if dl_response.status_code == 200:
                return dl_response.content
            
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
        self.downloader = AssrtSubtitleDownloader()
        
    def connect(self):
        self.conn = SMBConnection(
            SMB_CONFIG["username"], SMB_CONFIG["password"],
            "openclaw-client", SMB_CONFIG["server_name"], use_ntlm_v2=True
        )
        sys.stdout.write("🔌 连接 SMB...")
        sys.stdout.flush()
        connected = self.conn.connect(SMB_CONFIG["server_ip"], 445, timeout=10)
        if connected:
            print(" ✅")
            return True
        else:
            print(" ❌")
            return False
    
    def parse_video_info(self, filename):
        """解析视频文件名"""
        tv_match = re.search(r'([^.]+)\.S(\d+)E(\d+)', filename, re.IGNORECASE)
        movie_match = re.search(r'^(.+?)\s*(\d{4})', filename)
        
        # 中文译名映射
        chinese_names = {
            'young sheldon': '小谢尔顿',
            'sheldon': '小谢尔顿',
        }
        
        if tv_match:
            show_name = tv_match.group(1).replace('.', ' ')
            season = int(tv_match.group(2))
            episode = int(tv_match.group(3))
            
            # 生成多个搜索关键词
            queries = [f"{show_name} S{season:02d}E{episode:02d}"]
            
            # 添加中文译名
            show_lower = show_name.lower()
            if show_lower in chinese_names:
                cn_name = chinese_names[show_lower]
                queries.append(f"{cn_name} S{season:02d}E{episode:02d}")
                queries.append(f"{cn_name} 第{season}季 第{episode}集")
            
            return {
                'type': 'tv',
                'title': show_name,
                'season': season,
                'episode': episode,
                'query': queries[0],
                'queries': queries
            }
        elif movie_match:
            movie_name = movie_match.group(1).replace('.', ' ').strip()
            year = movie_match.group(2)
            return {
                'type': 'movie',
                'title': movie_name,
                'year': year,
                'query': f"{movie_name} {year}",
                'queries': [f"{movie_name} {year}"]
            }
        else:
            title = os.path.splitext(filename)[0].replace('.', ' ')
            return {'type': 'unknown', 'title': title, 'query': title, 'queries': [title]}
    
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
    
    def process_subtitle_data(self, data):
        """处理下载的字幕数据（解压等）"""
        files = []
        
        try:
            # 尝试解压 ZIP
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                for name in zf.namelist():
                    if name.endswith(('.srt', '.ass', '.ssa', '.vtt')):
                        local_path = os.path.join(self.temp_dir, os.path.basename(name))
                        with open(local_path, 'wb') as f:
                            f.write(zf.read(name))
                        files.append(local_path)
        except zipfile.BadZipFile:
            # 不是 ZIP，直接保存
            # 猜测文件类型
            if b'[Script Info]' in data[:200]:
                ext = '.ass'
            else:
                ext = '.srt'
            local_path = os.path.join(self.temp_dir, f"subtitle{ext}")
            with open(local_path, 'wb') as f:
                f.write(data)
            files.append(local_path)
        
        return files
    
    def download_subtitles(self, video_info):
        """下载字幕"""
        queries = video_info.get('queries', [video_info['query']])
        
        for query in queries:
            print(f"   🔍 搜索: {query}")
            
            results = self.downloader.search_subtitles(query)
            
            if results:
                print(f"   ✅ 找到 {len(results)} 个结果")
                
                # 尝试下载前3个结果
                all_files = []
                for result in results[:3]:
                    print(f"   📥 尝试下载: {result['title'][:40]}...")
                    data = self.downloader.download_subtitle(result['url'])
                    
                    if data:
                        files = self.process_subtitle_data(data)
                        all_files.extend(files)
                        break  # 成功后跳出
                    
                    time.sleep(0.5)
                
                if all_files:
                    return all_files
            
            time.sleep(1)
        
        return []
    
    def upload_subtitle(self, local_sub_path, video_info, index=0):
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
        current = self.stats["total"]
        total = len(self.video_files)
        
        print(f"\n🎬 [{current}/{total}] {video_info['filename']}")
        print(f"   📺 识别: {video_info['query']}")
        
        if self.check_existing_subtitles(video_info):
            print("   ⏭️  已有字幕，跳过")
            self.stats["skipped"] += 1
            return True
        
        subtitle_files = self.download_subtitles(video_info)
        
        if not subtitle_files:
            print("   ❌ 未找到字幕")
            self.stats["failed"] += 1
            return False
        
        print(f"   ✅ 下载了 {len(subtitle_files)} 个字幕文件")
        
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
        
        print(f"\n📦 处理第 {start_idx+1}-{end_idx} 个视频 (共 {len(self.video_files)} 个)\n")
        
        for video in batch:
            self.process_video(video)
            time.sleep(1)  # 避免请求过快
        
        return end_idx < len(self.video_files)
    
    def run(self, start_idx=0, batch_size=10):
        print("="*60)
        print("🎥 SMB 字幕下载工具 (分批处理)")
        print("="*60)
        
        if not self.connect():
            return False
        
        print("🔍 扫描视频文件...")
        self.scan_videos()
        print(f"✅ 找到 {len(self.video_files)} 个视频\n")
        
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
                seasons = set(v.get('season') for v in videos if v.get('season'))
                print(f"   📺 {title} - {len(videos)} 集")
            else:
                print(f"   🎬 {title}")
        print()
        
        # 确认处理
        print(f"将处理第 {start_idx+1}-{min(start_idx+batch_size, len(self.video_files))} 个视频")
        print("开始处理...\n")
        
        # 处理批次
        has_more = self.process_batch(start_idx, batch_size)
        
        print(f"\n{'='*60}")
        print("📊 当前统计:")
        print(f"   已处理: {self.stats['total']}")
        print(f"   跳过: {self.stats['skipped']}")
        print(f"   成功: {self.stats['downloaded']}")
        print(f"   失败: {self.stats['failed']}")
        if has_more:
            remaining = len(self.video_files) - self.stats['total']
            print(f"\n📦 还有 {remaining} 个视频待处理")
            print(f"   下次运行: python3 {sys.argv[0]} {self.stats['total']} {batch_size}")
        print(f"{'='*60}")
        
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        self.conn.close()
        print("\n🔌 SMB 连接已关闭")
        return True

def main():
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5  # 默认每次5个
    
    manager = SMBSubtitleManager()
    return 0 if manager.run(start_idx, batch_size) else 1

if __name__ == "__main__":
    sys.exit(main())
