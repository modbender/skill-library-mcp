"""
小红书Cookie管理模块

负责Cookie的获取、保存、加载和验证功能
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..core.config import XHSConfig
from ..core.browser import ChromeDriverManager
from ..core.exceptions import AuthenticationError, handle_exception
from ..xiaohongshu.models import CRITICAL_CREATOR_COOKIES
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CookieManager:
    """Cookie管理器"""
    
    def __init__(self, config: XHSConfig):
        """
        初始化Cookie管理器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.browser_manager = ChromeDriverManager(config)
    
    @handle_exception
    def save_cookies_interactive(self) -> bool:
        """
        交互式保存cookies - 支持创作者中心（命令行使用）
        
        Returns:
            是否成功保存cookies
            
        Raises:
            AuthenticationError: 当保存过程出错时
        """
        logger.info("🌺 开始获取小红书创作者中心Cookies...")
        logger.info("📝 注意：将直接跳转到创作者登录页面，确保获取完整的创作者权限cookies")
        
        try:
            # 创建浏览器驱动
            driver = self.browser_manager.create_driver()
            
            # 导航到创作者中心
            self.browser_manager.navigate_to_creator_center()
            
            logger.info("\n📋 请按照以下步骤操作:")
            logger.info("1. 在浏览器中手动登录小红书创作者中心")
            logger.info("2. 登录成功后，确保能正常访问创作者中心功能")
            logger.info("3. 建议点击进入【发布笔记】页面，确认权限完整")
            logger.info("4. 完成后，在此终端中按 Enter 键继续...")
            
            input()  # 等待用户输入
            
            logger.info("🍪 开始获取cookies...")
            cookies = driver.get_cookies()
            
            if not cookies:
                raise AuthenticationError("未获取到cookies，请确保已正确登录", auth_type="cookie_save")
            
            # 验证关键创作者cookies
            validation_result = self._validate_critical_cookies(cookies)
            
            # 保存cookies
            save_result = self._save_cookies_to_file(cookies, validation_result)
            
            if save_result:
                logger.info("\n🎉 Cookies获取成功！")
                logger.info("💡 现在可以正常访问创作者中心功能了")
                return True
            else:
                raise AuthenticationError("Cookies保存失败", auth_type="cookie_save")
            
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            else:
                raise AuthenticationError(f"获取cookies过程出错: {str(e)}", auth_type="cookie_save") from e
        finally:
            # 确保浏览器被关闭
            self.browser_manager.close_driver()
    
    def save_cookies_auto(self, timeout_seconds: int = 300) -> bool:
        """
        自动保存cookies（无需用户交互）
        
        Args:
            timeout_seconds: 等待登录完成的超时时间（秒）
            
        Returns:
            是否保存成功
            
        Raises:
            AuthenticationError: 当登录或保存失败时
        """
        logger.info("🚀 开始MCP自动登录流程...")
        logger.info(f"⏰ 超时时间: {timeout_seconds}秒")
        
        try:
            # 创建浏览器实例
            logger.info("🌐 正在启动浏览器...")
            driver = self.browser_manager.create_driver()
            logger.info("✅ 浏览器启动成功")
            
            # 导航到登录页面
            login_url = "https://creator.xiaohongshu.com/login"
            logger.info(f"🔗 正在访问登录页面: {login_url}")
            driver.get(login_url)
            logger.info("✅ 登录页面加载完成")
            
            # 等待用户登录完成
            logger.info("⏳ 等待用户完成登录...")
            logger.info("💡 请在浏览器中完成登录，程序将自动检测登录完成状态")
            
            success = self._wait_for_login_completion(driver, timeout_seconds)
            logger.info(f"🔍 登录检测结果: {'成功' if success else '失败'}")
            
            if not success:
                logger.error("❌ 登录检测失败或超时")
                raise AuthenticationError(f"登录超时（{timeout_seconds}秒），请重试", auth_type="cookie_save")
            
            logger.info("🍪 登录检测成功，开始获取cookies...")
            
            # 获取cookies
            try:
                cookies = driver.get_cookies()
                logger.info(f"📊 第一次获取到 {len(cookies)} 个cookies")
                
                if not cookies:
                    logger.warning("⚠️ 第一次未获取到cookies，尝试刷新页面...")
                    driver.refresh()
                    time.sleep(3)
                    cookies = driver.get_cookies()
                    logger.info(f"📊 刷新后获取到 {len(cookies)} 个cookies")
                
                if not cookies:
                    logger.error("❌ 仍然无法获取到cookies")
                    raise AuthenticationError("无法获取cookies，可能是页面未完全加载", auth_type="cookie_save")
                
            except Exception as e:
                logger.error(f"❌ 获取cookies时出错: {e}")
                raise AuthenticationError(f"获取cookies失败: {str(e)}", auth_type="cookie_save") from e
            
            # 验证cookies
            logger.info("🔍 开始验证cookies...")
            try:
                # 简化验证：只要有cookies就保存
                critical_cookies = [cookie['name'] for cookie in cookies if cookie.get('name') in CRITICAL_CREATOR_COOKIES]
                validation_result = {
                    "found_critical": critical_cookies,
                    "missing_critical": [],
                    "total_cookies": len(cookies)
                }
                
                logger.info(f"🔑 关键cookies数量: {len(critical_cookies)}")
                logger.info(f"🔑 关键cookies列表: {critical_cookies}")
                
            except Exception as e:
                logger.error(f"❌ 验证cookies时出错: {e}")
                # 即使验证出错，也尝试保存
                validation_result = {
                    "found_critical": [],
                    "missing_critical": [],
                    "total_cookies": len(cookies)
                }
            
            # 保存cookies
            logger.info("💾 开始保存cookies到文件...")
            try:
                save_result = self._save_cookies_to_file(cookies, validation_result)
                logger.info(f"💾 保存结果: {'成功' if save_result else '失败'}")
                
                if save_result:
                    logger.info("🎉 MCP自动登录完成！Cookies已成功保存")
                    
                    # 额外验证：检查文件是否真的被创建
                    cookies_file = Path(self.config.cookies_file)
                    if cookies_file.exists():
                        file_size = cookies_file.stat().st_size
                        logger.info(f"✅ 验证：cookies文件已创建，大小: {file_size} 字节")
                        return True
                    else:
                        logger.error("❌ 验证失败：cookies文件未创建")
                        raise AuthenticationError("Cookies文件创建失败", auth_type="cookie_save")
                else:
                    logger.error("❌ 保存cookies到文件失败")
                    raise AuthenticationError("Cookies保存失败", auth_type="cookie_save")
                    
            except Exception as e:
                logger.error(f"❌ 保存cookies过程出错: {e}")
                raise AuthenticationError(f"保存cookies失败: {str(e)}", auth_type="cookie_save") from e
            
        except Exception as e:
            logger.error(f"❌ MCP自动登录过程出错: {e}")
            if isinstance(e, AuthenticationError):
                raise
            else:
                raise AuthenticationError(f"MCP自动登录过程出错: {str(e)}", auth_type="cookie_save") from e
        finally:
            # 确保浏览器被关闭
            logger.info("🔒 正在关闭浏览器...")
            try:
                self.browser_manager.close_driver()
                logger.info("✅ 浏览器已关闭")
            except Exception as e:
                logger.warning(f"⚠️ 关闭浏览器时出错: {e}")
    
    def _wait_for_login_completion(self, driver, timeout_seconds: int) -> bool:
        """
        等待用户登录完成（改进的自动检测逻辑）
        
        Args:
            driver: WebDriver实例
            timeout_seconds: 超时时间
            
        Returns:
            是否检测到登录完成
        """
        import time
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        start_time = time.time()
        check_interval = 3  # 每3秒检查一次，提高响应速度
        
        logger.info(f"⏰ 开始智能检测登录状态，超时时间: {timeout_seconds}秒")
        logger.info("💡 请在浏览器中完成登录，包括：输入验证码 → 点击登录 → 进入创作者中心")
        
        # 记录初始URL，用于检测页面跳转
        initial_url = driver.current_url
        logger.debug(f"📍 初始页面URL: {initial_url}")
        
        last_url = initial_url
        login_attempts_detected = False
        
        while time.time() - start_time < timeout_seconds:
            try:
                current_url = driver.current_url
                elapsed = int(time.time() - start_time)
                
                # 检测URL变化，表明用户在进行操作
                if current_url != last_url:
                    logger.info(f"🔄 检测到页面跳转: {current_url}")
                    last_url = current_url
                
                # 1. 检查是否还在登录页面（包含登录相关关键词）
                try:
                    is_still_login = self._is_still_on_login_page(driver, current_url)
                    logger.info(f"🔍 登录页面检查结果: {is_still_login}")
                    if is_still_login:
                        logger.info(f"⏳ 仍在登录流程中... ({elapsed}/{timeout_seconds}秒)")
                        time.sleep(check_interval)
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ 登录页面检查出错: {e}")
                
                # 2. 检查是否成功进入创作者中心
                try:
                    logger.info(f"🔍 开始检查是否进入创作者中心: {current_url}")
                    creator_check_result = self._is_on_creator_center(driver, current_url)
                    logger.info(f"🔍 创作者中心检查结果: {creator_check_result}")
                    
                    if creator_check_result:
                        logger.info(f"🎯 已进入创作者中心页面: {current_url}")
                        logger.info("✅ 检测到页面跳转到创作者中心，立即认为登录成功！")
                        
                        # 等待3秒让页面完全加载
                        logger.info("⏳ 等待3秒让页面完全加载...")
                        time.sleep(3)
                        
                        # 再次确认页面状态
                        final_url = driver.current_url
                        logger.info(f"🔍 最终页面URL: {final_url}")
                        
                        # 快速检查cookies是否可获取
                        try:
                            test_cookies = driver.get_cookies()
                            logger.info(f"🍪 预检测到 {len(test_cookies)} 个cookies")
                        except Exception as e:
                            logger.warning(f"⚠️ 预检测cookies时出错: {e}")
                        
                        logger.info("✅ 登录检测完成，返回成功状态")
                        return True  # 简化逻辑：页面跳转即成功
                    else:
                        logger.info("❌ 尚未进入创作者中心，继续等待...")
                        
                except Exception as e:
                    logger.error(f"❌ 创作者中心检查出错: {e}")
                    logger.error(f"❌ 错误类型: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ 错误详情: {traceback.format_exc()}")
                    # 创作者中心检查出错时，不继续循环，直接返回失败
                    logger.error("❌ 由于检查出错，终止登录检测")
                    return False
                
                # 3. 检查是否出现错误页面
                try:
                    if self._is_error_page(driver):
                        logger.warning("❌ 检测到错误页面，登录可能失败")
                        return False
                except Exception as e:
                    logger.warning(f"⚠️ 错误页面检查出错: {e}")
                
                # 等待继续检查
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ 检测过程中出现严重错误: {e}")
                logger.error(f"❌ 错误类型: {type(e).__name__}")
                import traceback
                logger.error(f"❌ 错误详情: {traceback.format_exc()}")
                logger.error("❌ 由于严重错误，终止登录检测")
                return False
        
        logger.warning("⏰ 登录检测超时，可能是登录过程太长或网络问题")
        return False
    
    def _is_still_on_login_page(self, driver, current_url: str) -> bool:
        """检查是否还在登录页面"""
        try:
            logger.info(f"🔍 检查是否仍在登录页面: {current_url}")
            
            # 首先检查URL是否包含登录关键词（优先级最高）
            login_url_keywords = ['login', 'signin', 'auth', 'passport']
            if any(keyword in current_url.lower() for keyword in login_url_keywords):
                logger.info(f"❌ URL包含登录关键词，确认仍在登录页面")
                return True
            
            # 检查URL是否明确是创作者中心（且不是登录页面）
            creator_paths = ['/home', '/publish', '/studio', '/dashboard', '/content']
            if any(path in current_url.lower() for path in creator_paths):
                logger.info(f"✅ URL包含创作者中心路径，确定不在登录页面")
                return False
            
            # 如果URL不明确，检查页面元素（但要排除可能的误判）
            login_elements = [
                "//input[@type='password']",  # 密码输入框
                "//input[@placeholder*='验证码']",  # 验证码输入框
                "//input[@placeholder*='手机号']",  # 手机号输入框
                "//button[contains(text(), '登录') and not(contains(text(), '退出') or contains(text(), '注销'))]",  # 登录按钮（排除退出登录）
                "//button[contains(text(), '获取验证码')]",  # 获取验证码按钮
            ]
            
            found_login_elements = 0
            for xpath in login_elements:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        found_login_elements += 1
                        logger.debug(f"发现登录元素: {xpath}")
                except Exception as e:
                    logger.debug(f"检查登录元素出错 {xpath}: {e}")
            
            # 需要找到至少2个登录元素才认为是登录页面（避免误判）
            is_login_page = found_login_elements >= 2
            logger.info(f"登录元素数量: {found_login_elements}, 判定结果: {'登录页面' if is_login_page else '非登录页面'}")
            
            return is_login_page
            
        except Exception as e:
            logger.warning(f"检查登录页面时出错: {e}")
            return True  # 出错时保守认为还在登录页面
    
    def _is_on_creator_center(self, driver, current_url: str) -> bool:
        """检查是否进入创作者中心"""
        try:
            logger.info(f"🔍 检查是否进入创作者中心，当前URL: {current_url}")
            
            # 首先排除登录页面（即使包含creator关键词）
            login_url_keywords = ['login', 'signin', 'auth', 'passport']
            if any(keyword in current_url.lower() for keyword in login_url_keywords):
                logger.info(f"❌ URL包含登录关键词，确认仍在登录页面，非创作者中心")
                return False
            
            # URL包含创作者中心特定路径
            creator_paths = ['/home', '/publish', '/studio', '/dashboard', '/content', '/new']
            for path in creator_paths:
                if path in current_url.lower():
                    logger.info(f"✅ URL包含创作者中心路径'{path}'，确认已进入创作者中心: {current_url}")
                    return True
            
            logger.info("🔍 URL不包含关键词，检查页面元素...")
            
            # 页面包含创作者中心特征元素
            creator_elements = [
                "//div[contains(text(), '创作者中心')]",
                "//div[contains(text(), '发布笔记')]",
                "//button[contains(text(), '发布笔记')]",
                "//div[contains(text(), '数据概览')]",
                "//div[contains(text(), '内容管理')]"
            ]
            
            for xpath in creator_elements:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        logger.info(f"✅ 检测到创作者中心页面元素: {xpath}")
                        return True
                except Exception as e:
                    logger.debug(f"检查元素时出错 {xpath}: {e}")
            
            logger.info("❌ 未检测到创作者中心特征，仍在其他页面")
            return False
            
        except Exception as e:
            logger.warning(f"检查创作者中心时出错: {e}")
            return False
    
    def _is_error_page(self, driver) -> bool:
        """检查是否是错误页面"""
        try:
            error_elements = [
                "//div[contains(text(), '登录失败')]",
                "//div[contains(text(), '验证码错误')]",
                "//div[contains(text(), '账号或密码错误')]",
                "//div[contains(text(), '网络错误')]",
                "//div[contains(text(), '404')]",
                "//div[contains(text(), '500')]"
            ]
            
            for xpath in error_elements:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _verify_successful_login(self, driver) -> bool:
        """验证登录是否真正成功（优化后的宽松验证）"""
        try:
            # 1. 检查关键cookies
            cookies = driver.get_cookies()
            critical_cookies = [cookie['name'] for cookie in cookies if cookie['name'] in CRITICAL_CREATOR_COOKIES]
            
            logger.info(f"🔍 检查cookies: 总数({len(cookies)}) 关键({len(critical_cookies)}/9)")
            logger.debug(f"关键cookies: {critical_cookies}")
            
            # 2. 检查用户身份信息（多种可能的选择器）
            user_info_elements = [
                "//img[contains(@class, 'avatar')]",     # 用户头像
                "//div[contains(@class, 'user')]",       # 用户信息区域
                "//span[contains(@class, 'username')]",  # 用户名
                "//img[contains(@alt, '头像')]",          # 中文头像
                "//div[@class*='header']//img",          # 头部区域的图片
                "//div[contains(@class, 'profile')]"     # 用户资料区域
            ]
            
            user_info_found = False
            found_elements = []
            for xpath in user_info_elements:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        user_info_found = True
                        found_elements.append(xpath.split('//')[1][:20])  # 记录找到的元素类型
                except:
                    continue
            
            logger.debug(f"用户信息元素: {found_elements if found_elements else '未找到'}")
            
            # 3. 宽松的验证逻辑（降低门槛）
            if len(critical_cookies) >= 3:
                if len(critical_cookies) >= 4 or user_info_found:
                    logger.info(f"🎉 登录验证通过：关键cookies({len(critical_cookies)}/9)" + 
                               (f" + 用户信息({len(found_elements)}个)" if user_info_found else ""))
                    return True
                else:
                    logger.info(f"⚠️ 验证条件不足，但尝试保存cookies：cookies({len(critical_cookies)}/9)")
                    # 宽松处理：如果有3个以上关键cookies，就认为可能登录成功
                    return True
            else:
                logger.warning(f"❌ 关键cookies不足: {len(critical_cookies)}/9 < 3")
                return False
            
        except Exception as e:
            logger.warning(f"验证登录时出错，但继续尝试: {e}")
            # 出错时宽松处理，尝试检查基础cookies
            try:
                cookies = driver.get_cookies()
                if len(cookies) >= 5:  # 如果有足够多的cookies，就尝试保存
                    logger.info("⚠️ 验证出错但发现足够cookies，尝试保存")
                    return True
            except:
                pass
            return False
    
    def _validate_critical_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证关键创作者cookies（宽松模式）
        
        Args:
            cookies: Cookie列表
            
        Returns:
            验证结果字典
        """
        logger.info("🔍 验证创作者cookies（宽松模式）...")
        
        found_critical = []
        for cookie in cookies:
            if cookie.get('name') in CRITICAL_CREATOR_COOKIES:
                found_critical.append(cookie.get('name'))
        
        logger.info(f"✅ 找到关键创作者cookies: {found_critical}")
        
        # 宽松处理：不再严格要求特定cookies
        if found_critical:
            logger.info(f"🎉 发现 {len(found_critical)} 个关键cookies，验证通过")
        else:
            logger.info("💡 未发现预定义的关键cookies，但仍保存所有cookies")
        
        return {
            "found_critical": found_critical,
            "missing_critical": [],  # 宽松模式：不报告缺失
            "total_cookies": len(cookies)
        }
    
    def _save_cookies_to_file(self, cookies: List[Dict[str, Any]], validation_result: Dict[str, Any]) -> bool:
        """
        保存cookies到文件
        
        Args:
            cookies: Cookie列表
            validation_result: 验证结果
            
        Returns:
            是否保存成功
        """
        try:
            logger.info("📁 开始准备保存cookies...")
            
            # 创建cookies目录
            cookies_dir = Path(self.config.cookies_dir)
            logger.info(f"📁 cookies目录: {cookies_dir}")
            cookies_dir.mkdir(parents=True, exist_ok=True)
            logger.info("✅ cookies目录创建成功")
            
            # 构建新格式的cookies数据
            logger.info("📦 构建cookies数据结构...")
            cookies_data = {
                'cookies': cookies,
                'saved_at': datetime.now().isoformat(),
                'domain': 'creator.xiaohongshu.com',  # 标记为创作者中心cookies
                'critical_cookies_found': validation_result["found_critical"],
                'version': '2.0'  # 版本标记
            }
            logger.info(f"📦 数据结构构建完成，包含 {len(cookies)} 个cookies")
            
            # 保存cookies
            cookies_file = Path(self.config.cookies_file)
            logger.info(f"💾 准备写入文件: {cookies_file}")
            
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, ensure_ascii=False, indent=2)
            
            # 验证文件是否成功写入
            if cookies_file.exists():
                file_size = cookies_file.stat().st_size
                logger.info(f"✅ 文件写入成功: {cookies_file}")
                logger.info(f"📊 文件大小: {file_size} 字节")
                logger.info(f"📊 共保存了 {len(cookies)} 个cookies")
                logger.info(f"🔑 关键创作者cookies: {len(validation_result['found_critical'])}/{len(CRITICAL_CREATOR_COOKIES)}")
                
                # 显示关键cookies列表
                if validation_result['found_critical']:
                    logger.info(f"🔑 关键cookies列表: {validation_result['found_critical']}")
                
                return True
            else:
                logger.error("❌ 文件写入失败：文件不存在")
                return False
            
        except PermissionError as e:
            logger.error(f"❌ 权限错误，无法写入cookies文件: {e}")
            return False
        except json.JSONEncodeError as e:
            logger.error(f"❌ JSON编码错误: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 保存cookies失败: {e}")
            logger.error(f"❌ 错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"❌ 错误详情: {traceback.format_exc()}")
            return False
    
    @handle_exception
    def load_cookies(self) -> List[Dict[str, Any]]:
        """
        加载cookies - 支持新旧格式兼容
        
        Returns:
            Cookie列表
            
        Raises:
            AuthenticationError: 当加载失败时
        """
        cookies_file = Path(self.config.cookies_file)
        
        if not cookies_file.exists():
            logger.debug(f"Cookies文件不存在: {cookies_file}")
            return []
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 兼容新旧格式
            if isinstance(cookies_data, list):
                # 旧格式：直接是cookies列表
                cookies = cookies_data
                logger.debug("检测到旧版本cookies格式")
            else:
                # 新格式：包含元数据
                cookies = cookies_data.get('cookies', [])
                version = cookies_data.get('version', '1.0')
                domain = cookies_data.get('domain', 'unknown')
                logger.debug(f"检测到新版本cookies格式，版本: {version}, 域名: {domain}")
            
            logger.debug(f"成功加载 {len(cookies)} 个cookies")
            return cookies
            
        except Exception as e:
            raise AuthenticationError(f"加载cookies失败: {str(e)}", auth_type="cookie_load") from e
    
    def display_cookies_info(self) -> None:
        """显示当前cookies信息"""
        cookies_file = Path(self.config.cookies_file)
        
        if not cookies_file.exists():
            logger.warning("❌ Cookies文件不存在")
            return
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 兼容新旧格式
            if isinstance(cookies_data, list):
                # 旧格式：直接是cookies列表
                cookies = cookies_data
                saved_at = "未知"
                domain = "未知"
                version = "1.0"
            else:
                # 新格式：包含元数据
                cookies = cookies_data.get('cookies', [])
                saved_at = cookies_data.get('saved_at', '未知')
                domain = cookies_data.get('domain', '未知')
                version = cookies_data.get('version', '1.0')
            
            print(f"🍪 Cookies信息 ({cookies_file})")
            print("=" * 60)
            print(f"📊 总数量: {len(cookies)}")
            print(f"💾 保存时间: {saved_at}")
            print(f"🌐 域名: {domain}")
            print(f"📦 版本: {version}")
            
            # 显示关键创作者cookies状态
            if version != "1.0":
                print("\n🔑 关键创作者cookies状态:")
                found_critical = []
                for cookie in cookies:
                    if cookie.get('name') in CRITICAL_CREATOR_COOKIES:
                        found_critical.append(cookie.get('name'))
                        print(f"  ✅ {cookie.get('name')}")
                
                missing = set(CRITICAL_CREATOR_COOKIES) - set(found_critical)
                for missing_cookie in missing:
                    print(f"  ❌ {missing_cookie} (缺失)")
            
            print("\n📋 所有Cookies列表:")
            
            for i, cookie in enumerate(cookies, 1):
                name = cookie.get('name', 'N/A')
                domain = cookie.get('domain', 'N/A')
                expires = cookie.get('expiry', 'N/A')
                
                if expires != 'N/A':
                    try:
                        exp_date = datetime.fromtimestamp(expires)
                        expires = exp_date.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                # 标记关键cookies
                critical_mark = "🔑" if name in CRITICAL_CREATOR_COOKIES else "  "
                print(f"{critical_mark}{i:2d}. {name:35s} | {domain:25s} | 过期: {expires}")
            
        except Exception as e:
            logger.error(f"❌ 读取cookies失败: {e}")
    
    @handle_exception
    def validate_cookies(self) -> bool:
        """
        验证cookies是否有效
        
        Returns:
            cookies是否有效
            
        Raises:
            AuthenticationError: 当验证过程出错时
        """
        cookies_file = Path(self.config.cookies_file)
        
        if not cookies_file.exists():
            logger.warning("❌ Cookies文件不存在")
            return False
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 兼容新旧格式
            if isinstance(cookies_data, list):
                cookies = cookies_data
                logger.warning("⚠️ 检测到旧版本cookies，建议重新获取")
            else:
                cookies = cookies_data.get('cookies', [])
                version = cookies_data.get('version', '1.0')
                logger.info(f"📦 Cookies版本: {version}")
            
            logger.info("🔍 验证cookies...")
            
            # 检查关键创作者cookies
            found_cookies = []
            for cookie in cookies:
                if cookie.get('name') in CRITICAL_CREATOR_COOKIES:
                    found_cookies.append(cookie.get('name'))
            
            logger.info(f"✅ 找到关键创作者cookies: {found_cookies}")
            
            # 定义真正关键的cookies（必须存在的）
            must_have_cookies = ['a1', 'webId', 'galaxy_creator_session_id', 
                               'galaxy.creator.beaker.session.id', 'gid']
            missing = set(must_have_cookies) - set(found_cookies)  # 检查必须的cookies
            if missing:
                logger.warning(f"⚠️ 缺少重要cookies: {list(missing)}")
                logger.warning("💡 这可能导致创作者中心访问失败")
            
            # 检查过期时间
            current_time = time.time()
            expired_cookies = []
            expired_critical_cookies = []
            
            for cookie in cookies:
                expiry = cookie.get('expiry')
                cookie_name = cookie.get('name')
                if expiry and expiry < current_time:
                    expired_cookies.append(cookie_name)
                    # 检查是否是关键cookie过期
                    if cookie_name in CRITICAL_CREATOR_COOKIES:
                        expired_critical_cookies.append(cookie_name)
            
            if expired_cookies:
                logger.warning(f"⚠️ 已过期的cookies: {expired_cookies}")
                if expired_critical_cookies:
                    logger.warning(f"❌ 关键cookies已过期: {expired_critical_cookies}")
            else:
                logger.info("✅ 所有cookies都未过期")
            
            # 综合评估 - 更宽松的验证逻辑
            # 只要没有关键cookies过期，且缺少的关键cookies不超过2个就认为有效
            is_valid = len(expired_critical_cookies) == 0 and len(missing) <= 2
            
            if is_valid:
                logger.info("✅ Cookies验证通过，应该可以正常访问创作者中心")
            else:
                logger.warning("❌ Cookies验证失败，建议重新获取")
                logger.info("💡 运行命令: python xhs_toolkit.py cookie save")
            
            return is_valid
            
        except Exception as e:
            raise AuthenticationError(f"验证cookies失败: {str(e)}", auth_type="cookie_validate") from e
    
    @handle_exception
    def test_chromedriver_config(self) -> bool:
        """
        测试ChromeDriver配置是否正确
        
        Returns:
            测试是否通过
            
        Raises:
            AuthenticationError: 当测试失败时
        """
        logger.info("🔧 开始测试ChromeDriver配置...")
        
        try:
            driver = self.browser_manager.create_driver()
            logger.info("🌐 正在访问测试页面...")
            
            driver.get("https://www.google.com")
            title = driver.title
            logger.info(f"📄 页面标题: {title}")
            
            if "Google" in title:
                logger.info("✅ ChromeDriver配置测试成功！")
                result = True
            else:
                logger.warning("⚠️ 页面加载异常，请检查网络连接")
                result = False
                
            return result
            
        except Exception as e:
            raise AuthenticationError(f"ChromeDriver配置测试失败: {str(e)}", auth_type="chromedriver_test") from e
        finally:
            # 确保浏览器被关闭
            self.browser_manager.close_driver()


# 便捷函数
def create_cookie_manager(config: XHSConfig) -> CookieManager:
    """
    创建Cookie管理器的便捷函数
    
    Args:
        config: 配置管理器实例
        
    Returns:
        Cookie管理器实例
    """
    return CookieManager(config) 