"""
小红书模块接口抽象层

定义各个组件的接口规范，遵循SOLID原则中的依赖倒置和接口隔离原则
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import XHSNote, XHSPublishResult


class IPublisher(ABC):
    """笔记发布接口"""
    
    @abstractmethod
    async def publish_note(self, note: XHSNote) -> XHSPublishResult:
        """发布笔记"""
        pass


class IFileUploader(ABC):
    """文件上传接口"""
    
    @abstractmethod
    async def upload_files(self, files: List[str], file_type: str) -> bool:
        """上传文件"""
        pass


class IContentFiller(ABC):
    """内容填写接口"""
    
    @abstractmethod
    async def fill_title(self, title: str) -> bool:
        """填写标题"""
        pass
    
    @abstractmethod
    async def fill_content(self, content: str) -> bool:
        """填写内容"""
        pass
    
    @abstractmethod
    async def fill_topics(self, topics: List[str]) -> bool:
        """填写话题"""
        pass


class IDataCollector(ABC):
    """数据采集接口"""
    
    @abstractmethod
    async def collect_dashboard_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """采集仪表板数据"""
        pass
    
    @abstractmethod
    async def collect_content_analysis_data(self, date: Optional[str] = None, 
                                           limit: int = 50) -> Dict[str, Any]:
        """采集内容分析数据"""
        pass
    
    @abstractmethod
    async def collect_fans_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """采集粉丝数据"""
        pass


class IBrowserManager(ABC):
    """浏览器管理接口"""
    
    @abstractmethod
    def create_driver(self):
        """创建浏览器驱动"""
        pass
    
    @abstractmethod
    def close_driver(self) -> None:
        """关闭浏览器驱动"""
        pass
    
    @abstractmethod
    def navigate_to(self, url: str) -> None:
        """导航到指定URL"""
        pass
    
    @abstractmethod
    def load_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """加载cookies"""
        pass


class IXHSClient(ABC):
    """小红书客户端主接口"""
    
    @abstractmethod
    async def publish_note(self, note: XHSNote) -> XHSPublishResult:
        """发布笔记"""
        pass
    
    @abstractmethod
    async def collect_creator_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """采集创作者数据"""
        pass 