#!/usr/bin/env python3
"""
图片/视频下载和 URL 替换模块
"""

import re
import os
from pathlib import Path
from typing import List, Tuple, Optional
import requests
from urllib.parse import urlparse


class MediaDownloader:
    """媒体下载器"""
    
    def __init__(self, md_filepath: Path, images_dir: Path, logger=None):
        self.md_filepath = md_filepath
        self.images_dir = images_dir
        self.logger = logger
        self.downloaded_urls = {}
        
    def extract_media_urls(self, content: str) -> List[str]:
        """从 Markdown 内容中提取所有媒体 URL"""
        urls = []
        
        # 提取 Markdown 图片格式: ![alt](url)
        markdown_img_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
        matches = re.findall(markdown_img_pattern, content, re.IGNORECASE)
        urls.extend(matches)
        
        # 提取直接媒体链接 (pbs.twimg.com, video.twimg.com)
        media_domains = [
            r'(https?://pbs\.twimg\.com/[^\s\)\]]*)',
            r'(https?://video\.twimg\.com/[^\s\)\]]*)',
        ]
        for pattern in media_domains:
            matches = re.findall(pattern, content, re.IGNORECASE)
            urls.extend(matches)
        
        return list(set(urls))  # 去重
    
    def download_media(self, url: str) -> Tuple[Optional[str], str]:
        """下载媒体文件并返回 (本地路径, 原始 URL)"""
        try:
            # 清理 URL（移除 name=orig 等参数）
            clean_url = re.sub(r'[?\&]name=[^&\s\)\]]*', '', url)
            
            # 解析 URL 获取文件名
            parsed = urlparse(clean_url)
            path = parsed.path
            filename = path.split('/')[-1]
            
            # 添加扩展名（如果没有）
            ext = os.path.splitext(filename)[1]
            if not ext:
                ext = '.jpg'  # 默认扩展名
                filename = filename + ext
            
            # 生成唯一的文件名（避免重复）
            base_name = os.path.splitext(filename)[0] or 'image'
            counter = 1
            while os.path.exists(self.images_dir / filename):
                filename = f"{base_name}_{counter}{ext}"
                counter += 1
            
            filepath = self.images_dir / filename
            
            # 下载文件
            response = requests.get(clean_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 返回相对路径
            rel_path = str(filepath.relative_to(self.md_filepath.parent))
            if self.logger:
                self.logger.debug(f"✓ Downloaded: {clean_url} -> {rel_path}")
            
            return rel_path, url
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"✗ Failed to download {url}: {str(e)}")
            return None, url
    
    def process_markdown(self) -> int:
        """处理 Markdown 文件：下载媒体并替换 URL
        
        返回: 下载成功的媒体数量
        """
        # 创建 images 目录
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取 Markdown 文件
        with open(self.md_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取所有媒体 URL
        urls = self.extract_media_urls(content)
        
        if not urls:
            if self.logger:
                self.logger.info("No media URLs found in Markdown file")
            return 0
        
        if self.logger:
            self.logger.info(f"Found {len(urls)} media URLs, downloading...")
        
        # 下载所有媒体并替换 URL
        downloaded_count = 0
        for url in urls:
            local_path, original_url = self.download_media(url)
            if local_path:
                # 替换 URL 为本地路径
                content = content.replace(original_url, local_path)
                downloaded_count += 1
        
        # 写回 Markdown 文件
        with open(self.md_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if self.logger:
            self.logger.info(f"✓ Media download completed: {downloaded_count}/{len(urls)} files")
            self.logger.info(f"  Images saved to: {self.images_dir}")
            self.logger.info(f"  Updated Markdown: {self.md_filepath.name}")
        
        return downloaded_count
