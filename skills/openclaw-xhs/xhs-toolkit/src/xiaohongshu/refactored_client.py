"""
重构后的小红书客户端

展示SOLID原则应用，使用组合模式和依赖注入
"""

from typing import Optional, Dict, Any

from .interfaces import IXHSClient, IBrowserManager, IDataCollector
from .models import XHSNote, XHSPublishResult
from .components.publisher import XHSPublisher
from .components.file_uploader import XHSFileUploader
from .components.content_filler import XHSContentFiller
from .components.data_collector import XHSDataCollector
from ..core.exceptions import handle_exception
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RefactoredXHSClient(IXHSClient):
    """
    重构后的小红书客户端
    
    遵循SOLID原则:
    - 单一职责: 每个组件专注一个功能
    - 开闭原则: 通过接口扩展，不修改现有代码
    - 里氏替换: 所有组件都可以替换实现
    - 接口隔离: 细粒度的接口定义
    - 依赖倒置: 依赖接口而非具体实现
    """
    
    def __init__(self, browser_manager: IBrowserManager):
        """
        初始化重构后的客户端
        
        使用依赖注入模式，所有依赖通过构造函数注入
        
        Args:
            browser_manager: 浏览器管理器
        """
        self.browser_manager = browser_manager
        
        # 组合模式：使用组合而非继承
        self.file_uploader = XHSFileUploader(browser_manager)
        self.content_filler = XHSContentFiller(browser_manager)
        self.publisher = XHSPublisher(
            browser_manager=browser_manager,
            file_uploader=self.file_uploader,
            content_filler=self.content_filler
        )
        self.data_collector = XHSDataCollector(browser_manager)
        
        logger.info("✅ 重构后的小红书客户端初始化完成")
    
    @handle_exception
    async def publish_note(self, note: XHSNote) -> XHSPublishResult:
        """
        发布笔记 - 委托给专门的发布器
        
        遵循单一职责原则：客户端只负责协调，发布逻辑由Publisher处理
        
        Args:
            note: 笔记对象
            
        Returns:
            发布结果
        """
        logger.info(f"🚀 使用重构后客户端发布笔记: {note.title}")
        
        # 委托给专门的发布器
        return await self.publisher.publish_note(note)
    
    @handle_exception
    async def collect_creator_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        采集创作者数据 - 委托给专门的数据采集器
        
        Args:
            date: 日期筛选
            
        Returns:
            采集的数据
        """
        logger.info("📊 使用重构后客户端采集创作者数据")
        
        # 委托给专门的数据采集器
        return await self.data_collector.collect_dashboard_data(date)
    
    def get_file_uploader(self) -> XHSFileUploader:
        """获取文件上传器 - 暴露组件供独立使用"""
        return self.file_uploader
    
    def get_content_filler(self) -> XHSContentFiller:
        """获取内容填写器 - 暴露组件供独立使用"""
        return self.content_filler
    
    def get_publisher(self) -> XHSPublisher:
        """获取发布器 - 暴露组件供独立使用"""
        return self.publisher
    
    def get_data_collector(self) -> XHSDataCollector:
        """获取数据采集器 - 暴露组件供独立使用"""
        return self.data_collector
    
    async def upload_files_only(self, files: list, file_type: str) -> bool:
        """
        仅上传文件，不发布笔记
        
        展示组件的独立使用能力
        
        Args:
            files: 文件路径列表
            file_type: 文件类型
            
        Returns:
            上传是否成功
        """
        logger.info(f"📁 独立上传{len(files)}个{file_type}文件")
        
        return await self.file_uploader.upload_files(files, file_type)
    
    async def fill_content_only(self, title: str, content: str, topics: list = None) -> Dict[str, bool]:
        """
        仅填写内容，不发布笔记
        
        展示组件的独立使用能力
        
        Args:
            title: 笔记标题
            content: 笔记内容
            topics: 话题列表
            
        Returns:
            各项填写结果
        """
        logger.info("📝 开始填写内容（仅内容填写模式）")
        
        results = {}
        
        # 填写标题
        results["title"] = await self.content_filler.fill_title(title)
        results["content"] = await self.content_filler.fill_content(content)
        
        # 填写话题（如果提供）
        if topics:
            results["topics"] = await self.content_filler.fill_topics(topics)
        
        logger.info(f"📊 内容填写完成: {results}")
        
        return {
            "results": results,
            "content_info": self.content_filler.get_current_content(),
        }
    
    def get_current_page_info(self) -> Dict[str, Any]:
        """
        获取当前页面信息
        
        整合多个组件的信息
        
        Returns:
            页面信息汇总
        """
        info = {
            "browser_url": getattr(self.browser_manager.driver, "current_url", "unknown"),
            "content_info": self.content_filler.get_current_content(),
            "upload_progress": self.file_uploader.get_upload_progress()
        }
        
        return info
    
    def __enter__(self):
        """上下文管理器入口"""
        self.browser_manager.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.browser_manager.close_driver()


# 工厂函数：依赖注入的实现
def create_refactored_client(browser_manager: IBrowserManager) -> RefactoredXHSClient:
    """
    创建重构后的客户端实例
    
    工厂模式 + 依赖注入模式
    
    Args:
        browser_manager: 浏览器管理器
        
    Returns:
        重构后的客户端实例
    """
    return RefactoredXHSClient(browser_manager)


# 适配器模式：提供与原客户端兼容的接口
class CompatibilityAdapter:
    """
    兼容性适配器
    
    为了保持向后兼容，提供与原XHSClient相同的接口
    """
    
    def __init__(self, browser_manager: IBrowserManager):
        self.refactored_client = RefactoredXHSClient(browser_manager)
    
    async def publish_note(self, note: XHSNote) -> XHSPublishResult:
        """兼容原publish_note接口"""
        return await self.refactored_client.publish_note(note)
    
    async def collect_creator_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """兼容原collect_creator_data接口"""
        return await self.refactored_client.collect_creator_data(date)
    
    # 添加其他需要兼容的方法... 