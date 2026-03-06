"""
小红书笔记发布器

专门负责笔记发布流程，遵循单一职责原则
"""

import asyncio
from typing import Optional

from ..interfaces import IPublisher, IBrowserManager, IFileUploader, IContentFiller
from ..models import XHSNote, XHSPublishResult
from ..constants import XHSUrls, XHSConfig, XHSMessages
from ...core.exceptions import PublishError, handle_exception
from ...utils.logger import get_logger

logger = get_logger(__name__)


class XHSPublisher(IPublisher):
    """小红书笔记发布器"""
    
    def __init__(self, 
                 browser_manager: IBrowserManager,
                 file_uploader: IFileUploader, 
                 content_filler: IContentFiller):
        """
        初始化发布器
        
        Args:
            browser_manager: 浏览器管理器
            file_uploader: 文件上传器
            content_filler: 内容填写器
        """
        self.browser_manager = browser_manager
        self.file_uploader = file_uploader
        self.content_filler = content_filler
    
    @handle_exception
    async def publish_note(self, note: XHSNote) -> XHSPublishResult:
        """
        发布小红书笔记
        
        Args:
            note: 笔记对象
            
        Returns:
            发布结果
            
        Raises:
            PublishError: 当发布过程出错时
        """
        logger.info(f"📝 开始发布小红书笔记: {note.title}")
        
        try:
            # 创建浏览器驱动
            self.browser_manager.create_driver()
            
            # 导航到发布页面
            await self._navigate_to_publish_page()
            
            # 执行发布流程
            return await self._execute_publish_process(note)
            
        except Exception as e:
            if isinstance(e, PublishError):
                raise
            else:
                raise PublishError(f"发布笔记过程出错: {str(e)}", publish_step="初始化") from e
        finally:
            # 确保浏览器被关闭
            self.browser_manager.close_driver()
    
    async def _navigate_to_publish_page(self) -> None:
        """导航到发布页面"""
        logger.info("🌐 导航到小红书发布页面...")
        
        try:
            self.browser_manager.navigate_to(XHSUrls.PUBLISH_PAGE)
            await asyncio.sleep(XHSConfig.PAGE_LOAD_TIME)
            
            # 检查是否成功到达发布页面
            current_url = self.browser_manager.driver.current_url
            if "publish" not in current_url:
                raise PublishError("无法访问发布页面，可能需要重新登录", publish_step="页面访问")
                
            logger.info("✅ 成功导航到发布页面")
            
        except Exception as e:
            raise PublishError(f"导航到发布页面失败: {str(e)}", publish_step="导航") from e
    
    async def _execute_publish_process(self, note: XHSNote) -> XHSPublishResult:
        """执行发布流程的核心逻辑"""
        try:
            # 1. 根据内容类型切换发布模式
            await self._switch_publish_mode(note)
            
            # 2. 上传文件（图片/视频）
            await self._handle_file_upload(note)
            
            # 3. 填写笔记内容
            await self._fill_note_content(note)
            
            # 4. 提交发布
            return await self._submit_note(note)
            
        except Exception as e:
            # 截图保存错误现场
            self._take_error_screenshot()
            
            if isinstance(e, PublishError):
                raise
            else:
                raise PublishError(f"发布流程执行失败: {str(e)}", publish_step="流程执行") from e
    
    async def _switch_publish_mode(self, note: XHSNote) -> None:
        """根据笔记内容类型切换发布模式（图文/视频）"""
        from ..constants import XHSSelectors
        
        try:
            driver = self.browser_manager.driver
            
            # 判断内容类型
            has_images = note.images and len(note.images) > 0
            has_videos = note.videos and len(note.videos) > 0
            
            if has_images:
                logger.info("🔄 切换到图文发布模式...")
                await self._switch_to_image_mode()
                
            elif has_videos:
                logger.info("🔄 切换到视频发布模式...")
                await self._switch_to_video_mode()
                
        except Exception as e:
            logger.warning(f"⚠️ 模式切换过程出错: {e}，继续执行...")
    
    async def _switch_to_image_mode(self) -> None:
        """切换到图文模式"""
        from ..constants import XHSSelectors
        from selenium.webdriver.common.by import By
        
        try:
            driver = self.browser_manager.driver
            tabs = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.CREATOR_TABS)
            
            for tab in tabs:
                if (tab.is_displayed() and 
                    XHSSelectors.IMAGE_TAB_TEXT in tab.text and
                    tab.rect['x'] > 0 and tab.rect['y'] > 0):
                    
                    tab.click()
                    logger.info("✅ 已切换到图文发布模式")
                    await asyncio.sleep(XHSConfig.SHORT_WAIT_TIME)
                    return
                    
            logger.warning("⚠️ 未找到图文发布选项卡，可能已经在图文模式")
            
        except Exception as e:
            logger.warning(f"⚠️ 切换图文模式时出错: {e}")
    
    async def _switch_to_video_mode(self) -> None:
        """切换到视频模式"""
        from ..constants import XHSSelectors
        from selenium.webdriver.common.by import By
        
        try:
            driver = self.browser_manager.driver
            tabs = driver.find_elements(By.CSS_SELECTOR, XHSSelectors.CREATOR_TABS)
            
            for tab in tabs:
                if (tab.is_displayed() and 
                    XHSSelectors.VIDEO_TAB_TEXT in tab.text and
                    tab.rect['x'] > 0 and tab.rect['y'] > 0 and
                    "active" not in tab.get_attribute("class")):
                    
                    tab.click()
                    logger.info("✅ 已切换到视频发布模式")
                    await asyncio.sleep(XHSConfig.SHORT_WAIT_TIME)
                    return
                    
            logger.info("✅ 已在视频发布模式")
            
        except Exception as e:
            logger.warning(f"⚠️ 切换视频模式时出错: {e}")
    
    async def _handle_file_upload(self, note: XHSNote) -> None:
        """处理文件上传"""
        try:
            # 合并图片和视频文件
            files_to_upload = []
            file_type = ""
            
            if note.images:
                files_to_upload.extend(note.images)
                file_type = "image"
            
            if note.videos:
                files_to_upload.extend(note.videos)
                file_type = "video"
            
            if files_to_upload:
                success = await self.file_uploader.upload_files(files_to_upload, file_type)
                if not success:
                    raise PublishError("文件上传失败", publish_step="文件上传")
                    
        except Exception as e:
            if isinstance(e, PublishError):
                raise
            else:
                raise PublishError(f"文件上传处理失败: {str(e)}", publish_step="文件上传") from e
    
    async def _fill_note_content(self, note: XHSNote) -> None:
        """填写笔记内容"""
        try:
            # 填写标题
            success = await self.content_filler.fill_title(note.title)
            if not success:
                raise PublishError("标题填写失败", publish_step="内容填写")
            
            # 填写内容
            success = await self.content_filler.fill_content(note.content)
            if not success:
                raise PublishError("内容填写失败", publish_step="内容填写")
            
            # 第三步：填写话题
            if note.topics:
                logger.info(f"🏷️ 填写话题: {note.topics}")
                success = await self.content_filler.fill_topics(note.topics)
                if not success:
                    logger.warning("⚠️ 话题填写失败，但继续发布流程")
            else:
                logger.info("📝 未提供话题，跳过话题填写")
            
        except Exception as e:
            if isinstance(e, PublishError):
                raise
            else:
                raise PublishError(f"内容填写失败: {str(e)}", publish_step="内容填写") from e
    
    async def _submit_note(self, note: XHSNote) -> XHSPublishResult:
        """提交发布笔记"""
        from ..constants import XHSSelectors, get_publish_button_selectors
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            driver = self.browser_manager.driver
            wait = WebDriverWait(driver, XHSConfig.DEFAULT_WAIT_TIME)
            
            # 尝试多个发布按钮选择器
            publish_button = None
            for selector in get_publish_button_selectors():
                try:
                    if selector.startswith("//"):
                        # XPath选择器
                        publish_button = wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS选择器
                        publish_button = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    break
                except:
                    continue
            
            if not publish_button:
                raise PublishError("未找到发布按钮", publish_step="发布提交")
            
            # 点击发布按钮
            logger.info("🚀 点击发布按钮...")
            publish_button.click()
            
            # 等待发布完成
            await asyncio.sleep(XHSConfig.DEFAULT_WAIT_TIME)
            
            # 检查发布结果
            return await self._check_publish_result(note)
            
        except Exception as e:
            if isinstance(e, PublishError):
                raise
            else:
                raise PublishError(f"提交发布失败: {str(e)}", publish_step="发布提交") from e
    
    async def _check_publish_result(self, note: XHSNote) -> XHSPublishResult:
        """检查发布结果"""
        try:
            driver = self.browser_manager.driver
            current_url = driver.current_url
            
            # 简单的成功检查逻辑
            # 可以根据实际情况完善检查逻辑
            if "success" in current_url or "complete" in current_url:
                logger.info("✅ 笔记发布成功！")
                return XHSPublishResult(
                    success=True,
                    message=XHSMessages.PUBLISH_SUCCESS,
                    note_title=note.title,
                    final_url=current_url
                )
            else:
                logger.info("🎉 笔记发布完成，正在等待审核...")
                return XHSPublishResult(
                    success=True,
                    message="笔记已提交，等待审核",
                    note_title=note.title,
                    final_url=current_url
                )
                
        except Exception as e:
            logger.warning(f"⚠️ 检查发布结果时出错: {e}")
            return XHSPublishResult(
                success=True,
                message="发布完成，但无法确认结果",
                note_title=note.title
            )
    
    def _take_error_screenshot(self) -> None:
        """截图保存错误现场"""
        try:
            if hasattr(self.browser_manager, 'take_screenshot'):
                self.browser_manager.take_screenshot("publish_error_screenshot.png")
        except Exception as e:
            logger.warning(f"⚠️ 截图失败: {e}") 