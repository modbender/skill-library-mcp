"""
小红书工具包配置管理模块

负责环境变量加载、配置验证和跨平台路径检测
"""

import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from .exceptions import ConfigurationError, handle_exception
from ..utils.logger import get_logger

logger = get_logger(__name__)


class XHSConfig:
    """小红书工具包配置管理类"""
    
    def __init__(self, env_file_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            env_file_path: 环境变量文件路径，默认为当前目录下的.env
        """
        self.env_file_path = env_file_path or ".env"
        self._load_environment_variables()
        self._init_config_values()
    
    def _load_environment_variables(self) -> None:
        """加载环境变量配置"""
        try:
            # 检查.env文件是否存在
            if not os.path.exists(self.env_file_path):
                print(f"⚠️ 未找到配置文件: {self.env_file_path}")
                print("💡 程序将使用默认配置运行，建议创建配置文件以实现自定义设置")
                print()
            
            # 加载.env文件
            load_dotenv(self.env_file_path)
        except Exception as e:
            raise ConfigurationError(
                f"加载环境变量文件失败: {str(e)}",
                config_item="env_file"
            ) from e
    
    def _init_config_values(self) -> None:
        """初始化配置值"""
        # Chrome相关配置
        self.chrome_path = self._get_chrome_path()
        self.chromedriver_path = self._get_chromedriver_path()
        
        # 服务器配置
        self.server_host = os.getenv("SERVER_HOST", "0.0.0.0")
        self.server_port = int(os.getenv("SERVER_PORT", "8000"))
        
        # 文件路径配置
        self.cookies_file = os.getenv("COOKIES_FILE", "xhs_cookies.json")
        self.cookies_dir = os.path.dirname(self.cookies_file) or "."
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("LOG_FILE", "xhs_toolkit.log")
        
        # 浏览器选项
        self.disable_images = os.getenv("DISABLE_IMAGES", "false").lower() == "true"
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.headless = os.getenv("HEADLESS", "false").lower() == "true"  # 无头浏览器模式
        
        # 远程浏览器连接配置
        self.enable_remote_browser = os.getenv("ENABLE_REMOTE_BROWSER", "false").lower() == "true"
        self.remote_browser_host = os.getenv("REMOTE_BROWSER_HOST", "localhost")
        self.remote_browser_port = int(os.getenv("REMOTE_BROWSER_PORT", "9222"))
        
        # 其他配置
        self.timeout = int(os.getenv("TIMEOUT", "30"))
    
    def _get_chrome_path(self) -> str:
        """获取Chrome浏览器路径"""
        # 优先使用环境变量
        env_chrome_path = os.getenv("CHROME_PATH")
        if env_chrome_path and os.path.exists(env_chrome_path):
            return env_chrome_path
        
        # 自动检测系统默认Chrome路径
        return self._detect_default_chrome_path()
    
    def _detect_default_chrome_path(self) -> str:
        """自动检测系统默认Chrome路径"""
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
            ]
        elif system == "windows":  # Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
        else:  # Linux
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        
        # 检查每个路径是否存在
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        
        # 如果都不存在，尝试使用which/where命令
        try:
            if system == "windows":
                import subprocess
                result = subprocess.run(["where", "chrome"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            else:
                chrome_which = shutil.which("google-chrome") or shutil.which("chromium-browser")
                if chrome_which:
                    return chrome_which
        except:
            pass
        
        # 返回默认值，让用户自己配置
        return ""
    
    def _get_chromedriver_path(self) -> str:
        """获取ChromeDriver路径"""
        # 优先使用环境变量
        env_driver_path = os.getenv("WEBDRIVER_CHROME_DRIVER")
        if env_driver_path and os.path.exists(env_driver_path):
            return env_driver_path
        
        # 尝试在PATH中查找
        chromedriver_path = shutil.which("chromedriver")
        if chromedriver_path:
            return chromedriver_path
        
        # 返回空字符串，让selenium自己处理
        return ""
    
    @handle_exception
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置完整性
        
        Returns:
            验证结果字典
            
        Raises:
            ConfigurationError: 当验证过程出错时
        """
        issues = []
        
        # 检查Chrome路径
        if not self.chrome_path:
            issues.append("Chrome浏览器路径未设置或不存在")
        elif not os.path.exists(self.chrome_path):
            issues.append(f"Chrome浏览器路径不存在: {self.chrome_path}")
        
        # 检查ChromeDriver（可选，因为可以使用系统PATH）
        if self.chromedriver_path and not os.path.exists(self.chromedriver_path):
            issues.append(f"ChromeDriver路径不存在: {self.chromedriver_path}")
        
        # 检查端口范围
        if not (1024 <= self.server_port <= 65535):
            issues.append(f"服务器端口范围无效: {self.server_port}")
        
        # 检查日志级别
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            issues.append(f"无效的日志级别: {self.log_level}")
        
        # 检查Cookies目录是否可写
        cookies_dir = Path(self.cookies_dir)
        try:
            cookies_dir.mkdir(parents=True, exist_ok=True)
            # 测试写权限
            test_file = cookies_dir / ".test_write"
            test_file.touch()
            test_file.unlink()
        except Exception:
            issues.append(f"Cookies目录不可写: {self.cookies_dir}")
        
        # 远程浏览器配置验证（仅在启用时验证）
        if self.enable_remote_browser:
            if not (1024 <= self.remote_browser_port <= 65535):
                issues.append(f"远程浏览器端口范围无效: {self.remote_browser_port}")
            if not self.remote_browser_host.strip():
                issues.append("远程浏览器主机地址不能为空")
            logger.debug(f"远程浏览器配置验证: {self.remote_browser_host}:{self.remote_browser_port}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def get_env_example_content(self) -> str:
        """
        生成环境变量示例内容
        
        Returns:
            环境变量示例字符串
        """
        content = f"""# 小红书MCP工具包环境变量配置

# Chrome浏览器路径
CHROME_PATH={self.chrome_path or "自动检测"}

# ChromeDriver路径（可选，为空则使用系统PATH）
WEBDRIVER_CHROME_DRIVER={self.chromedriver_path or "自动检测"}

# MCP服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Cookies文件路径
COOKIES_FILE=xhs_cookies.json

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=xhs_toolkit.log

# 浏览器选项
DISABLE_IMAGES=false
DEBUG_MODE=false
# 无头浏览器模式（true=启用无头模式，false=显示浏览器界面）
HEADLESS=false

# 远程浏览器连接配置
# 是否启用远程浏览器连接（true=连接远程浏览器，false=启动本地浏览器）
ENABLE_REMOTE_BROWSER=false
# 远程浏览器主机地址（通常为localhost或远程服务器IP）
REMOTE_BROWSER_HOST=localhost
# 远程浏览器调试端口（Chrome启动时的--remote-debugging-port参数）
REMOTE_BROWSER_PORT=9222

# 超时设置（秒）
TIMEOUT=30
"""
        return content
    
    def save_env_example(self, file_path: str = "env_example") -> None:
        """
        保存环境变量示例文件
        
        Args:
            file_path: 示例文件路径
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.get_env_example_content())
        except Exception as e:
            raise ConfigurationError(f"保存环境变量示例失败: {str(e)}") from e
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典格式
        
        Returns:
            配置字典
        """
        return {
            "chrome_path": self.chrome_path,
            "chromedriver_path": self.chromedriver_path,
            "server_host": self.server_host,
            "server_port": self.server_port,
            "cookies_file": self.cookies_file,
            "cookies_dir": self.cookies_dir,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "disable_images": self.disable_images,
            "debug_mode": self.debug_mode,
            "headless": self.headless,
            "enable_remote_browser": self.enable_remote_browser,
            "remote_browser_host": self.remote_browser_host,
            "remote_browser_port": self.remote_browser_port,
            "timeout": self.timeout,
            "platform": platform.system(),
            "python_version": platform.python_version()
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        config_dict = self.to_dict()
        return "\n".join([f"{k}: {v}" for k, v in config_dict.items()])


# 便捷函数
def create_config(env_file_path: Optional[str] = None) -> XHSConfig:
    """
    创建配置管理器的便捷函数
    
    Args:
        env_file_path: 环境变量文件路径
        
    Returns:
        配置管理器实例
    """
    return XHSConfig(env_file_path)


def get_default_config() -> XHSConfig:
    """
    获取默认配置
    
    Returns:
        默认配置实例
    """
    return XHSConfig() 
