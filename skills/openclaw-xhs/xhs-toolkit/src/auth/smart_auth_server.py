"""
小红书智能认证服务器

提供智能登录、cookie检测和自动提醒功能
支持MCP协议，可以被AI直接调用
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..core.config import XHSConfig
from .cookie_manager import CookieManager
from ..core.exceptions import AuthenticationError, handle_exception
from ..utils.logger import get_logger

logger = get_logger(__name__)


class LoginStatus(Enum):
    """登录状态枚举"""
    VALID = "valid"              # 有效登录状态
    EXPIRED = "expired"          # Cookie已过期
    MISSING = "missing"          # Cookie不存在
    INVALID = "invalid"          # Cookie无效
    NEEDS_LOGIN = "needs_login"  # 需要登录


@dataclass
class AuthStatus:
    """认证状态数据类"""
    status: LoginStatus
    message: str
    details: Dict[str, Any]
    suggestions: List[str]
    auto_action_available: bool = False


class SmartAuthServer:
    """智能认证服务器"""
    
    def __init__(self, config: Optional[XHSConfig] = None):
        """
        初始化智能认证服务器
        
        Args:
            config: 配置管理器实例，为空则自动创建
        """
        self.config = config or XHSConfig()
        self.cookie_manager = CookieManager(self.config)
        self._last_check_time = None
        self._cached_status = None
        self._cache_duration = timedelta(minutes=5)  # 缓存5分钟
    
    @handle_exception
    async def check_auth_status(self, force_check: bool = False) -> AuthStatus:
        """
        检查认证状态
        
        Args:
            force_check: 是否强制检查，忽略缓存
            
        Returns:
            认证状态对象
        """
        logger.info("🔍 检查小红书认证状态...")
        
        # 检查缓存
        if not force_check and self._is_cache_valid():
            logger.debug("📋 使用缓存的认证状态")
            return self._cached_status
        
        try:
            # 检查cookies文件是否存在
            cookies_file = Path(self.config.cookies_file)
            if not cookies_file.exists():
                return self._create_auth_status(
                    LoginStatus.MISSING,
                    "❌ 未找到小红书登录cookies",
                    {"cookies_file": str(cookies_file)},
                    ["请先登录小红书获取cookies", "运行登录命令: '登录小红书'"]
                )
            
            # 加载并验证cookies
            cookies = self.cookie_manager.load_cookies()
            if not cookies:
                return self._create_auth_status(
                    LoginStatus.MISSING,
                    "❌ Cookies文件为空或格式错误",
                    {"cookies_count": 0},
                    ["请重新登录小红书", "运行登录命令: '登录小红书'"]
                )
            
            # 详细验证cookies
            validation_result = await self._validate_cookies_detailed(cookies)
            
            # 更新缓存
            self._last_check_time = datetime.now()
            self._cached_status = validation_result
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ 检查认证状态失败: {e}")
            return self._create_auth_status(
                LoginStatus.INVALID,
                f"❌ 认证状态检查失败: {str(e)}",
                {"error": str(e)},
                ["请检查网络连接", "尝试重新登录: '登录小红书'"]
            )
    
    async def _validate_cookies_detailed(self, cookies: List[Dict[str, Any]]) -> AuthStatus:
        """
        详细验证cookies
        
        Args:
            cookies: Cookie列表
            
        Returns:
            认证状态对象
        """
        from ..xiaohongshu.models import CRITICAL_CREATOR_COOKIES
        
        logger.debug("🔍 详细验证cookies...")
        
        # 检查关键cookies
        found_critical = []
        expired_cookies = []
        current_time = time.time()
        
        for cookie in cookies:
            name = cookie.get('name', '')
            if name in CRITICAL_CREATOR_COOKIES:
                found_critical.append(name)
                
                # 检查过期时间
                expiry = cookie.get('expiry')
                if expiry and expiry < current_time:
                    expired_cookies.append(name)
        
        missing_critical = set(CRITICAL_CREATOR_COOKIES[:4]) - set(found_critical)
        
        # 构建验证详情
        details = {
            "total_cookies": len(cookies),
            "found_critical": found_critical,
            "missing_critical": list(missing_critical),
            "expired_cookies": expired_cookies,
            "critical_coverage": f"{len(found_critical)}/{len(CRITICAL_CREATOR_COOKIES)}"
        }
        
        # 判断状态
        if expired_cookies:
            return self._create_auth_status(
                LoginStatus.EXPIRED,
                f"⚠️ 发现过期cookies: {expired_cookies}",
                details,
                ["Cookies已过期，需要重新登录", "运行登录命令: '登录小红书'"],
                auto_action_available=True
            )
        
        if len(missing_critical) > 2:  # 缺少超过2个关键cookie
            return self._create_auth_status(
                LoginStatus.INVALID,
                f"❌ 缺少重要cookies: {list(missing_critical)}",
                details,
                ["关键cookies缺失，可能无法正常使用创作者功能", "建议重新登录: '登录小红书'"],
                auto_action_available=True
            )
        
        if len(missing_critical) > 0:
            return self._create_auth_status(
                LoginStatus.VALID,
                f"✅ 登录状态基本有效（缺少次要cookies: {list(missing_critical)}）",
                details,
                ["基本功能可用，如遇问题可重新登录"],
                auto_action_available=False
            )
        
        # 完全有效
        return self._create_auth_status(
            LoginStatus.VALID,
            "✅ 小红书登录状态完全有效",
            details,
            ["所有关键cookies都存在且有效"],
            auto_action_available=False
        )
    
    @handle_exception
    async def smart_login(self, interactive: bool = True, mcp_mode: bool = False) -> Dict[str, Any]:
        """
        智能登录功能
        
        Args:
            interactive: 是否使用交互式登录（命令行模式）
            mcp_mode: 是否为MCP模式（自动化登录）
            
        Returns:
            登录结果字典
        """
        mode_desc = "MCP自动化" if mcp_mode else "交互式"
        logger.info(f"🔐 开始{mode_desc}登录流程...")
        
        try:
            # 先检查当前状态
            auth_status = await self.check_auth_status(force_check=True)
            
            # MCP模式下不询问，直接登录
            if mcp_mode:
                logger.info("🤖 MCP模式：自动执行登录流程")
                try:
                    logger.info("🔄 开始调用save_cookies_auto...")
                    login_success = self.cookie_manager.save_cookies_auto(timeout_seconds=120)  # 减少到2分钟避免MCP超时
                    logger.info(f"🔄 save_cookies_auto调用完成，结果: {login_success}")
                except Exception as e:
                    logger.error(f"❌ save_cookies_auto调用出错: {e}")
                    logger.error(f"❌ 错误类型: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ 错误详情: {traceback.format_exc()}")
                    login_success = False
            else:
                # 命令行模式：如果已经有效，询问是否需要重新登录
                if auth_status.status == LoginStatus.VALID and interactive:
                    logger.info("✅ 当前登录状态有效")
                    logger.info("💡 如果遇到访问问题，可以选择重新登录")
                    
                    choice = input("是否需要重新登录？ (y/N): ").strip().lower()
                    if choice not in ['y', 'yes', '是']:
                        return {
                            "success": True,
                            "action": "skipped",
                            "message": "用户选择跳过重新登录",
                            "status": auth_status.status.value
                        }
                
                # 执行交互式登录流程
                if interactive:
                    logger.info("🌐 启动交互式登录...")
                    login_success = self.cookie_manager.save_cookies_interactive()
                else:
                    logger.warning("⚠️ 非交互模式暂不支持，切换到交互模式")
                    login_success = self.cookie_manager.save_cookies_interactive()
            
            if login_success:
                # 清除缓存，强制重新检查
                self._cached_status = None
                
                # MCP模式下不需要重新检查状态，直接返回成功
                if mcp_mode:
                    return {
                        "success": True,
                        "action": "mcp_auto_login",
                        "message": "✅ MCP自动登录成功！",
                        "status": "completed"
                    }
                else:
                    # 命令行模式：验证登录结果
                    new_status = await self.check_auth_status(force_check=True)
                    
                    return {
                        "success": True,
                        "action": "logged_in",
                        "message": "✅ 登录成功！",
                        "status": new_status.status.value,
                        "details": new_status.details
                    }
            else:
                return {
                    "success": False,
                    "action": "login_failed",
                    "message": "❌ 登录失败",
                    "status": "failed"
                }
                
        except Exception as e:
            logger.error(f"❌ {mode_desc}登录失败: {e}")
            return {
                "success": False,
                "action": "error",
                "message": f"登录过程出错: {str(e)}",
                "error": str(e)
            }
    
    @handle_exception
    async def auto_check_and_prompt(self) -> Dict[str, Any]:
        """
        自动检查并在需要时提示登录
        
        Returns:
            检查结果和建议
        """
        logger.debug("🤖 执行自动认证检查...")
        
        auth_status = await self.check_auth_status()
        
        result = {
            "status": auth_status.status.value,
            "message": auth_status.message,
            "needs_action": auth_status.auto_action_available,
            "suggestions": auth_status.suggestions,
            "details": auth_status.details,
            "timestamp": datetime.now().isoformat()
        }
        
        # 如果需要行动，添加自动提示
        if auth_status.auto_action_available:
            result["action_prompt"] = "需要重新登录小红书，请告知AI：'登录小红书'"
            logger.warning("⚠️ 检测到需要重新登录")
        
        return result
    
    def _create_auth_status(self, status: LoginStatus, message: str, 
                          details: Dict[str, Any], suggestions: List[str],
                          auto_action_available: bool = False) -> AuthStatus:
        """创建认证状态对象"""
        return AuthStatus(
            status=status,
            message=message,
            details=details,
            suggestions=suggestions,
            auto_action_available=auto_action_available
        )
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._last_check_time or not self._cached_status:
            return False
        
        return datetime.now() - self._last_check_time < self._cache_duration
    
    @handle_exception
    async def get_auth_info(self) -> Dict[str, Any]:
        """
        获取详细的认证信息
        
        Returns:
            认证信息字典
        """
        logger.info("📊 获取认证信息...")
        
        try:
            cookies_file = Path(self.config.cookies_file)
            
            if not cookies_file.exists():
                return {
                    "cookies_file_exists": False,
                    "cookies_file_path": str(cookies_file),
                    "message": "Cookies文件不存在"
                }
            
            # 读取cookies文件信息
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 兼容新旧格式
            if isinstance(cookies_data, list):
                cookies = cookies_data
                saved_at = "未知"
                version = "1.0"
                domain = "未知"
            else:
                cookies = cookies_data.get('cookies', [])
                saved_at = cookies_data.get('saved_at', '未知')
                version = cookies_data.get('version', '1.0')
                domain = cookies_data.get('domain', '未知')
            
            # 获取当前状态
            auth_status = await self.check_auth_status()
            
            return {
                "cookies_file_exists": True,
                "cookies_file_path": str(cookies_file),
                "cookies_count": len(cookies),
                "saved_at": saved_at,
                "version": version,
                "domain": domain,
                "current_status": auth_status.status.value,
                "status_message": auth_status.message,
                "details": auth_status.details,
                "suggestions": auth_status.suggestions
            }
            
        except Exception as e:
            logger.error(f"❌ 获取认证信息失败: {e}")
            return {
                "error": str(e),
                "message": "获取认证信息时出错"
            }


# 便捷函数
def create_smart_auth_server(config: Optional[XHSConfig] = None) -> SmartAuthServer:
    """
    创建智能认证服务器的便捷函数
    
    Args:
        config: 配置管理器实例
        
    Returns:
        智能认证服务器实例
    """
    return SmartAuthServer(config)


# MCP函数封装
async def mcp_check_login_status() -> Dict[str, Any]:
    """MCP函数：检查登录状态"""
    auth_server = create_smart_auth_server()
    auth_status = await auth_server.check_auth_status()
    
    return {
        "function": "check_login_status",
        "status": auth_status.status.value,
        "message": auth_status.message,
        "details": auth_status.details,
        "suggestions": auth_status.suggestions,
        "needs_login": auth_status.auto_action_available
    }


async def mcp_smart_login() -> Dict[str, Any]:
    """MCP函数：智能登录（MCP专用自动化模式）"""
    auth_server = create_smart_auth_server()
    result = await auth_server.smart_login(interactive=False, mcp_mode=True)
    
    return {
        "function": "mcp_smart_login",
        **result
    }


async def mcp_auto_check() -> Dict[str, Any]:
    """MCP函数：自动检查并提示"""
    auth_server = create_smart_auth_server()
    result = await auth_server.auto_check_and_prompt()
    
    return {
        "function": "auto_check",
        **result
    }


async def mcp_get_auth_info() -> Dict[str, Any]:
    """MCP函数：获取认证信息"""
    auth_server = create_smart_auth_server()
    result = await auth_server.get_auth_info()
    
    return {
        "function": "get_auth_info",
        **result
    }
