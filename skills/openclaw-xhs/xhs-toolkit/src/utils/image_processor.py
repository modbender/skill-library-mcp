"""
图片处理模块

支持多种图片输入格式的处理：
- 本地文件路径
- 网络URL
"""

import os
import asyncio
import aiohttp
import tempfile
from pathlib import Path
from typing import List, Union, Optional
import uuid

from .logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """图片处理器，支持本地路径和URL下载"""
    
    def __init__(self, temp_dir: str = None):
        """
        初始化图片处理器
        
        Args:
            temp_dir: 临时文件目录路径
        """
        # 设置临时目录
        if temp_dir:
            self.temp_dir = Path(temp_dir)
        else:
            # 使用系统临时目录
            self.temp_dir = Path(tempfile.gettempdir()) / "xhs_images"
        
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"图片处理器初始化，临时目录: {self.temp_dir}")
    
    async def process_images(self, images_input: Union[str, List, None]) -> List[str]:
        """
        处理各种格式的图片输入，返回本地文件路径列表
        
        支持格式：
        - 本地路径: "/path/to/image.jpg"
        - 网络地址: "https://example.com/image.jpg"
        - 混合列表: ["path.jpg", "https://..."]
        
        Args:
            images_input: 图片输入（支持多种格式）
            
        Returns:
            List[str]: 本地文件路径列表
        """
        if not images_input:
            return []
        
        # 统一转换为列表格式
        images_list = self._normalize_to_list(images_input)
        
        # 处理每个图片
        local_paths = []
        for idx, img in enumerate(images_list):
            try:
                local_path = await self._process_single_image(img, idx)
                if local_path:
                    local_paths.append(local_path)
                    logger.info(f"✅ 处理图片成功 [{idx+1}/{len(images_list)}]: {local_path}")
            except Exception as e:
                logger.error(f"❌ 处理图片失败 [{idx+1}/{len(images_list)}]: {e}")
                continue
        
        logger.info(f"📸 图片处理完成，共处理 {len(local_paths)}/{len(images_list)} 张")
        return local_paths
    
    def _normalize_to_list(self, images_input: Union[str, List]) -> List:
        """将各种输入格式统一转换为列表"""
        if isinstance(images_input, str):
            # 单个字符串，可能是路径或逗号分隔的多个路径
            if ',' in images_input:
                # 逗号分隔的多个路径
                return [img.strip() for img in images_input.split(',') if img.strip()]
            else:
                return [images_input]
        elif isinstance(images_input, list):
            return images_input
        else:
            # 其他类型，返回空列表
            logger.warning(f"⚠️ 不支持的输入类型: {type(images_input)}")
            return []
    
    async def _process_single_image(self, img_input: str, index: int) -> Optional[str]:
        """
        处理单个图片输入
        
        Args:
            img_input: 图片输入（字符串）
            index: 图片索引
            
        Returns:
            Optional[str]: 本地文件路径，失败返回None
        """
        if not isinstance(img_input, str):
            logger.warning(f"⚠️ 无效的图片输入类型: {type(img_input)}")
            return None
            
        # 检查是否是网络地址
        if img_input.startswith(('http://', 'https://')):
            # 网络地址
            return await self._download_from_url(img_input, index)
        elif os.path.exists(img_input):
            # 本地文件
            return os.path.abspath(img_input)
        else:
            logger.warning(f"⚠️ 无效的图片路径: {img_input}")
            return None
    
    async def _download_from_url(self, url: str, index: int) -> Optional[str]:
        """
        下载网络图片到本地
        
        Args:
            url: 图片URL
            index: 图片索引
            
        Returns:
            Optional[str]: 本地文件路径，失败返回None
        """
        try:
            logger.info(f"⬇️ 开始下载图片: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"❌ 下载图片失败: {url}, 状态码: {response.status}")
                        return None
                    
                    # 获取文件扩展名
                    content_type = response.headers.get('content-type', '')
                    ext = self._get_extension_from_content_type(content_type)
                    if not ext:
                        # 从URL中尝试获取扩展名
                        url_path = Path(url.split('?')[0])
                        ext = url_path.suffix or '.jpg'
                    
                    # 生成唯一文件名
                    filename = f"download_{index}_{uuid.uuid4().hex[:8]}{ext}"
                    filepath = self.temp_dir / filename
                    
                    # 保存文件
                    content = await response.read()
                    filepath.write_bytes(content)
                    
                    logger.info(f"✅ 下载图片成功: {url} -> {filepath}")
                    return str(filepath)
                    
        except asyncio.TimeoutError:
            raise Exception(f"下载图片超时: {url}")
        except Exception as e:
            raise Exception(f"下载图片失败: {url}, 错误: {str(e)}")
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """根据content-type获取文件扩展名"""
        mapping = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp'
        }
        
        # 提取主要的内容类型（去除参数）
        main_type = content_type.split(';')[0].strip().lower()
        return mapping.get(main_type, '')
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        清理超过指定时间的临时文件
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
        """
        import time
        current_time = time.time()
        cleaned_count = 0
        
        try:
            for file in self.temp_dir.iterdir():
                if file.is_file():
                    file_age_hours = (current_time - file.stat().st_mtime) / 3600
                    if file_age_hours > max_age_hours:
                        try:
                            file.unlink()
                            cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"清理文件失败: {file}, 错误: {e}")
            
            if cleaned_count > 0:
                logger.info(f"🧹 清理了 {cleaned_count} 个临时文件")
                
        except Exception as e:
            logger.error(f"清理临时文件出错: {e}")