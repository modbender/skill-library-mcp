"""
小红书数据采集器组件

专门负责数据采集相关功能，遵循单一职责原则
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..interfaces import IBrowserManager
from ..data_collector import (
    collect_dashboard_data,
    collect_content_analysis_data,
    collect_fans_data
)
from ...core.exceptions import handle_exception
from ...utils.logger import get_logger

logger = get_logger(__name__)


class XHSDataCollector:
    """小红书数据采集器"""
    
    def __init__(self, browser_manager: IBrowserManager):
        """
        初始化数据采集器
        
        Args:
            browser_manager: 浏览器管理器
        """
        self.browser_manager = browser_manager
    
    @handle_exception
    async def collect_dashboard_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        采集账号概览数据
        
        Args:
            date: 指定日期 (YYYY-MM-DD)，默认为当前日期
            
        Returns:
            包含账号概览数据的字典
        """
        logger.info(f"🔍 开始采集账号概览数据: {date or '当前日期'}")
        
        try:
            data = await collect_dashboard_data(
                driver=self.browser_manager.driver,
                date=date
            )
            
            logger.info("✅ 账号概览数据采集完成")
            return data
            
        except Exception as e:
            logger.error(f"❌ 账号概览数据采集失败: {e}")
            raise
    
    @handle_exception
    async def collect_content_analysis_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        采集内容分析数据
        
        Args:
            date: 指定日期 (YYYY-MM-DD)，默认为当前日期
            
        Returns:
            包含内容分析数据的字典
        """
        logger.info(f"📊 开始采集内容分析数据: {date or '当前日期'}")
        
        try:
            data = await collect_content_analysis_data(
                driver=self.browser_manager.driver,
                date=date
            )
            
            logger.info("✅ 内容分析数据采集完成")
            return data
            
        except Exception as e:
            logger.error(f"❌ 内容分析数据采集失败: {e}")
            raise
    
    @handle_exception
    async def collect_fans_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        采集粉丝数据
        
        Args:
            date: 指定日期 (YYYY-MM-DD)，默认为当前日期
            
        Returns:
            包含粉丝数据的字典
        """
        logger.info(f"👥 开始采集粉丝数据: {date or '当前日期'}")
        
        try:
            data = await collect_fans_data(
                driver=self.browser_manager.driver,
                date=date
            )
            
            logger.info("✅ 粉丝数据采集完成")
            return data
            
        except Exception as e:
            logger.error(f"❌ 粉丝数据采集失败: {e}")
            raise
    
    @handle_exception
    async def collect_all_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        采集所有类型数据
        
        Args:
            date: 指定日期 (YYYY-MM-DD)，默认为当前日期
            
        Returns:
            包含所有数据的字典
        """
        logger.info(f"🎯 开始采集所有数据: {date or '当前日期'}")
        
        try:
            results = {}
            
            # 并行采集所有数据
            tasks = [
                self.collect_dashboard_data(date),
                self.collect_content_analysis_data(date),
                self.collect_fans_data(date)
            ]
            
            dashboard_data, content_data, fans_data = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            # 处理结果
            if not isinstance(dashboard_data, Exception):
                results['dashboard'] = dashboard_data
            else:
                logger.warning(f"⚠️ 账号概览数据采集失败: {dashboard_data}")
            
            if not isinstance(content_data, Exception):
                results['content_analysis'] = content_data
            else:
                logger.warning(f"⚠️ 内容分析数据采集失败: {content_data}")
            
            if not isinstance(fans_data, Exception):
                results['fans'] = fans_data
            else:
                logger.warning(f"⚠️ 粉丝数据采集失败: {fans_data}")
            
            logger.info(f"✅ 数据采集完成，成功采集 {len(results)} 类数据")
            return results
            
        except Exception as e:
            logger.error(f"❌ 批量数据采集失败: {e}")
            raise
    
    def get_supported_data_types(self) -> list:
        """
        获取支持的数据类型列表
        
        Returns:
            支持的数据类型列表
        """
        return [
            'dashboard',      # 账号概览
            'content_analysis', # 内容分析
            'fans'           # 粉丝数据
        ]
    
    def validate_date_format(self, date: str) -> bool:
        """
        验证日期格式是否正确
        
        Args:
            date: 日期字符串
            
        Returns:
            是否为有效格式
        """
        try:
            datetime.strptime(date, '%Y-%m-%d')
            return True
        except ValueError:
            return False 