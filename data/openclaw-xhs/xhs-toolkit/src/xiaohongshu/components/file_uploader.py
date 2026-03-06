"""
小红书文件上传器

专门负责文件上传处理，遵循单一职责原则
"""

import asyncio
import os
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..interfaces import IFileUploader, IBrowserManager
from ..constants import (XHSConfig, XHSSelectors, XHSMessages, 
                        get_file_upload_selectors, is_supported_image_format, 
                        is_supported_video_format)
from ...core.exceptions import PublishError, handle_exception
from ...utils.logger import get_logger

logger = get_logger(__name__)


class XHSFileUploader(IFileUploader):
    """小红书文件上传器"""
    
    def __init__(self, browser_manager: IBrowserManager):
        """
        初始化文件上传器
        
        Args:
            browser_manager: 浏览器管理器
        """
        self.browser_manager = browser_manager
    
    @handle_exception
    async def upload_files(self, files: List[str], file_type: str) -> bool:
        """
        上传文件
        
        Args:
            files: 文件路径列表
            file_type: 文件类型 ('image' 或 'video')
            
        Returns:
            上传是否成功
            
        Raises:
            PublishError: 当上传过程出错时
        """
        logger.info(f"📁 开始上传{len(files)}个{file_type}文件")
        
        try:
            # 验证文件
            self._validate_files(files, file_type)
            
            # 查找文件上传控件
            file_input = await self._find_file_input()
            if not file_input:
                raise PublishError("未找到文件上传控件", publish_step="文件上传")
            
            # 执行文件上传
            return await self._perform_upload(file_input, files, file_type)
            
        except Exception as e:
            if isinstance(e, PublishError):
                raise
            else:
                raise PublishError(f"文件上传失败: {str(e)}", publish_step="文件上传") from e
    
    def _validate_files(self, files: List[str], file_type: str) -> None:
        """
        验证文件有效性
        
        Args:
            files: 文件路径列表
            file_type: 文件类型
            
        Raises:
            PublishError: 当文件验证失败时
        """
        if not files:
            raise PublishError("文件列表为空", publish_step="文件验证")
        
        for file_path in files:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise PublishError(f"文件不存在: {file_path}", publish_step="文件验证")
            
            # 检查文件格式
            if file_type == "image":
                if not is_supported_image_format(file_path):
                    raise PublishError(f"不支持的图片格式: {file_path}", publish_step="文件验证")
                    
                # 检查图片数量限制
                if len(files) > XHSConfig.MAX_IMAGES:
                    raise PublishError(f"图片数量超限，最多{XHSConfig.MAX_IMAGES}张", 
                                     publish_step="文件验证")
                    
            elif file_type == "video":
                if not is_supported_video_format(file_path):
                    raise PublishError(f"不支持的视频格式: {file_path}", publish_step="文件验证")
                    
                # 检查视频数量限制
                if len(files) > XHSConfig.MAX_VIDEOS:
                    raise PublishError(f"视频数量超限，最多{XHSConfig.MAX_VIDEOS}个", 
                                     publish_step="文件验证")
            
            # 检查文件大小（可选）
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                logger.warning(f"⚠️ 文件较大({file_size / 1024 / 1024:.1f}MB): {file_path}")
        
        logger.info(f"✅ 文件验证通过，共{len(files)}个{file_type}文件")
    
    async def _find_file_input(self):
        """
        查找文件上传输入控件
        
        Returns:
            文件输入元素，如果未找到返回None
        """
        driver = self.browser_manager.driver
        wait = WebDriverWait(driver, XHSConfig.DEFAULT_WAIT_TIME)
        
        # 尝试多个选择器
        for selector in get_file_upload_selectors():
            try:
                logger.debug(f"🔍 尝试选择器: {selector}")
                file_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # 验证元素是否可用
                if file_input and file_input.is_enabled():
                    logger.info(f"✅ 找到文件上传控件: {selector}")
                    return file_input
                    
            except TimeoutException:
                logger.debug(f"⏰ 选择器超时: {selector}")
                continue
            except Exception as e:
                logger.debug(f"⚠️ 选择器错误: {selector}, {e}")
                continue
        
        logger.error("❌ 未找到可用的文件上传控件")
        return None
    
    async def _perform_upload(self, file_input, files: List[str], file_type: str) -> bool:
        """
        执行文件上传
        
        Args:
            file_input: 文件输入元素
            files: 文件路径列表
            file_type: 文件类型
            
        Returns:
            上传是否成功
        """
        try:
            # 将文件路径转换为绝对路径并合并
            absolute_files = [os.path.abspath(f) for f in files]
            files_string = '\n'.join(absolute_files)
            
            logger.info(f"📤 开始上传文件...")
            logger.debug(f"文件列表: {files_string}")
            
            # 发送文件路径到输入控件
            file_input.send_keys(files_string)
            
            # 等待上传完成
            success = await self._wait_for_upload_completion(file_type)
            
            if success:
                logger.info(f"✅ {file_type}文件上传成功")
            else:
                logger.error(f"❌ {file_type}文件上传失败")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 上传过程出错: {e}")
            return False
    
    async def _wait_for_upload_completion(self, file_type: str) -> bool:
        """
        等待上传完成
        
        Args:
            file_type: 文件类型
            
        Returns:
            上传是否成功完成
        """
        driver = self.browser_manager.driver
        
        # 根据文件类型设置不同的等待时间
        if file_type == "video":
            max_wait_time = XHSConfig.VIDEO_PROCESSING_TIME
            check_interval = 5
        else:
            max_wait_time = XHSConfig.FILE_UPLOAD_TIME
            check_interval = 2
        
        waited_time = 0
        
        while waited_time < max_wait_time:
            try:
                # 检查上传成功标识
                success_elements = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.UPLOAD_SUCCESS)
                if success_elements and any(elem.is_displayed() for elem in success_elements):
                    logger.info("✅ 检测到上传成功标识")
                    return True
                
                # 检查上传错误标识
                error_elements = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.UPLOAD_ERROR)
                if error_elements and any(elem.is_displayed() for elem in error_elements):
                    logger.error("❌ 检测到上传错误标识")
                    return False
                
                # 检查视频处理完成标识（仅视频文件）
                if file_type == "video":
                    complete_elements = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.VIDEO_COMPLETE)
                    if complete_elements and any(elem.is_displayed() for elem in complete_elements):
                        logger.info("✅ 视频处理完成")
                        return True
                    
                    # 检查视频处理中标识
                    processing_elements = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.VIDEO_PROCESSING)
                    if processing_elements and any(elem.is_displayed() for elem in processing_elements):
                        logger.info("🔄 视频处理中...")
                
                # 等待检查间隔
                await asyncio.sleep(check_interval)
                waited_time += check_interval
                
                # 每10秒打印一次进度
                if waited_time % 10 == 0:
                    logger.info(f"⏳ 上传进行中... 已等待{waited_time}秒")
                
            except Exception as e:
                logger.warning(f"⚠️ 检查上传状态时出错: {e}")
                await asyncio.sleep(check_interval)
                waited_time += check_interval
        
        # 超时后的最后检查
        logger.warning(f"⏰ 等待上传超时({max_wait_time}秒)，进行最后检查...")
        
        try:
            # 通过页面状态判断是否成功
            # 如果页面没有明显的错误提示，则认为上传成功
            error_elements = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.UPLOAD_ERROR)
            if not error_elements or not any(elem.is_displayed() for elem in error_elements):
                logger.info("✅ 未发现错误标识，认为上传成功")
                return True
        except Exception as e:
            logger.warning(f"⚠️ 最后检查时出错: {e}")
        
        logger.error("❌ 上传超时失败")
        return False
    
    def get_upload_progress(self) -> dict:
        """
        获取上传进度信息
        
        Returns:
            包含上传进度信息的字典
        """
        try:
            driver = self.browser_manager.driver
            
            # 查找进度条元素
            progress_elements = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.UPLOAD_PROGRESS)
            
            if progress_elements:
                progress_element = progress_elements[0]
                
                # 尝试获取进度值
                progress_value = progress_element.get_attribute("value") or "0"
                progress_text = progress_element.text or "上传中..."
                
                return {
                    "has_progress": True,
                    "value": progress_value,
                    "text": progress_text,
                    "visible": progress_element.is_displayed()
                }
            else:
                return {
                    "has_progress": False,
                    "message": "未找到进度信息"
                }
                
        except Exception as e:
            logger.warning(f"⚠️ 获取上传进度失败: {e}")
            return {
                "has_progress": False,
                "error": str(e)
            } 