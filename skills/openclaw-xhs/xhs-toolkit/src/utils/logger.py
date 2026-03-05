"""
小红书工具包统一日志配置模块

提供统一的日志配置和管理功能
"""

import os
import sys
import logging
from typing import Optional, Any
from loguru import logger


class LoggerConfig:
    """日志配置管理器"""
    
    def __init__(self, log_level: str = "INFO", log_file: str = "xhs_toolkit.log"):
        """
        初始化日志配置
        
        Args:
            log_level: 日志级别
            log_file: 日志文件路径
        """
        self.log_level = log_level.upper()
        self.log_file = log_file
        self._setup_loguru()
        self._setup_third_party_loggers()
    
    def _setup_loguru(self) -> None:
        """配置loguru日志器"""
        # 移除默认的日志处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stderr,
            level=self.log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <level>{message}</level>",
            colorize=True
        )
        
        # 添加文件输出
        logger.add(
            self.log_file,
            rotation="10 MB",
            retention="7 days",
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}",
            encoding="utf-8"
        )
        
        # 如果是DEBUG级别，输出详细信息
        if self.log_level == "DEBUG":
            logger.debug("🔧 DEBUG模式已启用，将输出详细调试信息")
            logger.debug(f"🔧 日志级别: {self.log_level}")
            logger.debug(f"🔧 日志文件: {self.log_file}")
            logger.debug(f"🔧 当前工作目录: {os.getcwd()}")
            logger.debug(f"🔧 Python版本: {sys.version}")
    
    def _setup_third_party_loggers(self) -> None:
        """配置第三方库的日志器"""
        # 抑制selenium的部分警告
        selenium_logger = logging.getLogger('selenium')
        selenium_logger.setLevel(logging.WARNING)
        
        # 抑制urllib3的警告
        urllib3_logger = logging.getLogger('urllib3')
        urllib3_logger.setLevel(logging.WARNING)
        
        # 配置uvicorn和FastAPI的日志过滤器
        self._setup_asgi_filter()
    
    def _setup_asgi_filter(self) -> None:
        """设置ASGI相关的日志过滤器"""
        class ASGIErrorFilter(logging.Filter):
            def filter(self, record):
                # 过滤ASGI相关的错误信息
                asgi_error_keywords = [
                    "Expected ASGI message",
                    "RuntimeError",
                    "Exception in ASGI application",
                    "Cancel 0 running task(s)"
                ]
                return not any(keyword in record.getMessage() for keyword in asgi_error_keywords)
        
        # 应用过滤器到uvicorn日志
        uvicorn_logger = logging.getLogger("uvicorn.error")
        uvicorn_logger.addFilter(ASGIErrorFilter())
        
        uvicorn_access_logger = logging.getLogger("uvicorn.access")
        uvicorn_access_logger.addFilter(ASGIErrorFilter())
    
    def get_logger(self, name: str) -> Any:
        """
        获取带有模块名的日志器
        
        Args:
            name: 模块名称
            
        Returns:
            配置好的日志器
        """
        return logger.bind(name=name)


# 全局日志配置实例
_logger_config: Optional[LoggerConfig] = None


def setup_logger(log_level: str = None, log_file: str = None) -> None:
    """
    设置全局日志配置
    
    Args:
        log_level: 日志级别，默认从环境变量LOG_LEVEL获取
        log_file: 日志文件，默认为xhs_toolkit.log
    """
    global _logger_config
    
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    if log_file is None:
        log_file = "xhs_toolkit.log"
    
    _logger_config = LoggerConfig(log_level, log_file)


def get_logger(name: Optional[str] = None) -> Any:
    """
    获取日志器实例
    
    Args:
        name: 模块名称
        
    Returns:
        配置好的日志器
    """
    if name is None:
        name = __name__
        
    if _logger_config is None:
        setup_logger()
    
    return _logger_config.get_logger(name)


# 初始化默认日志配置
setup_logger() 