#!/usr/bin/env python3
"""
微信桌面自动化工具 - 支持Windows和macOS
功能：激活窗口、定位区域、获取好友列表、获取聊天记录、发送消息
"""

import os
import sys
import time
import json
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import threading
import random
import pyperclip
import requests

# 平台相关导入
import platform

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

if IS_WINDOWS:
    import win32gui
    import win32con
    import win32process
    import win32api
elif IS_MACOS:
    # macOS依赖需要单独安装
    try:
        from AppKit import NSWorkspace, NSApplication
        import Quartz
    except ImportError:
        print("macOS依赖未安装，请运行: pip install pyobjc-framework-Quartz")
        sys.exit(1)

import pyautogui
from PIL import ImageGrab
import cv2
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class WeChatRegion:
    """微信界面区域配置 - 根据精确布局定义"""
    window_rect: Tuple[int, int, int, int] = None  # (x, y, width, height)

    # 主要区域
    sidebar: Tuple[int, int, int, int] = None  # 侧边栏区域
    contact_panel: Tuple[int, int, int, int] = None  # 中间联系人面板
    chat_panel: Tuple[int, int, int, int] = None  # 右侧聊天面板

    # 侧边栏子区域
    sidebar_avatar: Tuple[int, int, int, int] = None  # 头像区域
    sidebar_chat_icon: Tuple[int, int, int, int] = None  # 消息图标（第一个菜单）
    sidebar_contact_icon: Tuple[int, int, int, int] = None  # 通讯录图标

    # 联系人面板子区域
    contact_search_area: Tuple[int, int, int, int] = None  # 搜索区域
    contact_search_input: Tuple[int, int, int, int] = None  # 搜索输入框
    contact_list: Tuple[int, int, int, int] = None  # 好友列表区域

    # 聊天面板子区域
    chat_header: Tuple[int, int, int, int] = None  # 头部区域
    chat_messages: Tuple[int, int, int, int] = None  # 消息记录区域
    chat_input_area: Tuple[int, int, int, int] = None  # 聊天区域（工具栏+输入框+底部）
    chat_toolbar: Tuple[int, int, int, int] = None  # 聊天工具栏
    chat_input_box: Tuple[int, int, int, int] = None  # 聊天输入框
    chat_bottom_area: Tuple[int, int, int, int] = None  # 底部区域
    chat_send_button: Tuple[int, int, int, int] = None  # 发送按钮

    # 搜索结果第一个联系人位置（不需要整个浮窗区域）
    search_result_first: Tuple[int, int, int, int] = None  # 搜索结果第一个联系人

    # 固定参数 - 根据微信界面精确尺寸定义
    sidebar_width: int = 60  # 侧边栏宽度
    contact_panel_min_width: int = 200  # 中间区域最小宽度
    split_line_width: int = 1  # 分割线宽度

    # 侧边栏参数
    sidebar_avatar_height: int = 70  # 头像区域高度
    sidebar_icon_height: int = 50  # 菜单图标高度
    sidebar_icon_margin: int = 10  # 图标上下间距
    sidebar_icon_size: int = 40  # 图标大小

    # 联系人面板参数
    contact_search_height: int = 70  # 搜索区域高度
    contact_search_input_width: int = 115  # 搜索输入框宽度
    contact_search_input_height: int = 30  # 搜索输入框高度
    contact_search_input_left: int = 40  # 搜索输入框左边距
    contact_search_input_bottom: int = 15  # 搜索输入框距离底部
    contact_item_height: int = 70  # 每个好友高度（搜索联系人也是这个高度）

    # 聊天面板参数
    chat_header_height: int = 70  # 头部高度
    chat_input_min_height: int = 150  # 聊天区域最小高度
    chat_toolbar_height: int = 45  # 工具栏高度
    chat_bottom_height: int = 45  # 底部区域高度
    chat_send_width: int = 100  # 发送按钮宽度
    chat_send_height: int = 30  # 发送按钮高度
    chat_send_right: int = 20  # 发送按钮右边距
    chat_send_bottom: int = 15  # 发送按钮底边距

    # 头像边界距离（头像距离消息区域边缘的距离）
    chat_avatar_boundary: int = 55  # 新增：头像边界距离

    # 聊天右键菜单
    chat_right_click_menu_width: int = 105  # 菜单宽度
    chat_right_click_menu_height: int = 310  # 菜单高度
    chat_right_click_item_height: int = 30  # 每个菜单项的高度

class WeChatAutomation:
    """微信自动化主类"""

    def __init__(self, ocr_debug: bool = True):
        self.logger = logger
        self.region = WeChatRegion()
        self.currentWindowUser = None
        # 平台特定的微信配置
        if IS_WINDOWS:
            self._init_windows_config()
        elif IS_MACOS:
            self._init_macos_config()
        else:
            self.logger.error(f"不支持的操作系统: {platform.system()}")
            sys.exit(1)

        # 创建必要的目录
        self._init_directories()
        # 加载配置
        self._load_region_config()

    def _init_windows_config(self):
        """Windows配置初始化"""
        self.wechat_paths = [
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files\Tencent\Weixin\Weixin.exe",
            os.path.expanduser(r"~\AppData\Local\Tencent\WeChat\WeChat.exe"),
            os.path.expanduser(r"~\AppData\Local\Tencent\WeChat\update\WeChat.exe"),
            os.path.expanduser(r"~\AppData\Local\Tencent\Weixin\update\Weixin.exe"),
        ]
        self.wechat_process_names = ['WeChat.exe', 'WeChatApp.exe', 'WeChatAppEx.exe', 'Weixin.exe']
        self.wechat_window_titles = ['微信', 'WeChat', 'Weixin']

    def _init_macos_config(self):
        """macOS配置初始化"""
        self.wechat_paths = [
            "/Applications/WeChat.app",
            "/Applications/微信.app",
            os.path.expanduser("~/Applications/WeChat.app"),
            os.path.expanduser("~/Applications/微信.app"),
        ]
        self.wechat_process_names = ['WeChat', '微信']
        self.wechat_window_titles = ['WeChat', '微信']

    def _init_directories(self):
        """初始化必要的目录"""
        Path("config").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        Path("debug").mkdir(exist_ok=True)

    def is_wechat_running(self) -> bool:
        """检查微信是否在运行"""
        try:
            if IS_WINDOWS:
                import psutil
                for proc in psutil.process_iter(['name']):
                    try:
                        proc_name = proc.info['name']
                        if proc_name and proc_name.lower() in [name.lower() for name in self.wechat_process_names]:
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            elif IS_MACOS:
                # macOS检查进程
                workspace = NSWorkspace.sharedWorkspace()
                running_apps = workspace.runningApplications()
                for app in running_apps:
                    if app.localizedName() in self.wechat_process_names:
                        return True

            return False
        except Exception as e:
            self.logger.error(f"检查微信进程失败: {e}")
            return False

    def find_wechat_exe(self) -> Optional[str]:
        """查找微信可执行文件"""
        for path in self.wechat_paths:
            if os.path.exists(path):
                self.logger.info(f"找到微信: {path}")
                return path

        # 尝试在PATH中查找
        if IS_WINDOWS:
            try:
                result = subprocess.run(['where', 'WeChat.exe'],
                                        capture_output=True, text=True, encoding='gbk',
                                        creationflags=subprocess.CREATE_NO_WINDOW)
                if result.stdout:
                    paths = result.stdout.strip().split('\n')
                    for path in paths:
                        if os.path.exists(path):
                            self.logger.info(f"从PATH找到微信: {path}")
                            return path
            except:
                pass

        self.logger.error("未找到微信安装路径")
        return None

    def start_wechat(self) -> bool:
        """启动微信"""
        try:
            wechat_path = self.find_wechat_exe()
            if not wechat_path:
                self.logger.error("找不到微信安装路径")
                return False

            self.logger.info(f"启动微信: {wechat_path}")

            if IS_WINDOWS:
                # Windows启动
                try:
                    import subprocess
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags = 1
                    startupinfo.wShowWindow = 1
                    CREATE_NO_WINDOW = 0x08000000

                    process = subprocess.Popen(
                        [wechat_path],
                        startupinfo=startupinfo,
                        shell=True,
                        creationflags=CREATE_NO_WINDOW
                    )
                    self.logger.info(f"微信进程已启动，PID: {process.pid}")

                except Exception as e:
                    self.logger.warning(f"标准启动方法失败，使用备用方案: {e}")
                    try:
                        os.startfile(wechat_path)
                        self.logger.info("使用os.startfile启动微信成功")
                    except Exception as e2:
                        self.logger.error(f"所有启动方法都失败: {e2}")
                        return False

            elif IS_MACOS:
                # macOS启动
                self.logger.info("macOS启动微信")
                try:
                    subprocess.run(['open', '-a', 'WeChat'],
                                   capture_output=True, text=True, timeout=10)
                    self.logger.info("使用open命令启动微信")
                except Exception as e:
                    self.logger.warning(f"open命令失败，尝试其他方法: {e}")
                    try:
                        subprocess.run(['open', '-a', '微信'],
                                       capture_output=True, text=True, timeout=10)
                        self.logger.info("使用中文名启动微信")
                    except Exception as e2:
                        self.logger.error(f"所有macOS启动方法都失败: {e2}")
                        return False

            # 等待微信启动
            for i in range(30):
                time.sleep(1)
                if self.is_wechat_running():
                    self.logger.info(f"微信已启动 (等待{i + 1}秒)")
                    time.sleep(1)  # 额外等待3秒让窗口完全加载
                    return True

            self.logger.warning("微信启动超时")
            return False

        except Exception as e:
            self.logger.error(f"启动微信失败: {e}")
            return False

    def activate_wechat_window(self, window_title: str = None) -> bool:
        """激活微信窗口"""
        self.logger.info("先激活微信窗口...")

        # 1. 检查微信是否在运行
        if not self.is_wechat_running():
            self.logger.info("微信未运行，尝试启动...")
            self.start_wechat()
            return False

        # 2. 查找并激活微信窗口
        try:
            activated = False
            if IS_WINDOWS:
                activated = self._activate_windows_window(window_title)
            elif IS_MACOS:
                activated = self._activate_macos_window(window_title)
            ## 激活后 如果没有定位，先初始化定位
            if activated and not self.region.sidebar:
                self.locate_regions()
            return activated
        except Exception as e:
            self.logger.error(f"激活微信窗口失败: {e}")
            return False

    def _activate_windows_window(self, window_title: str = None) -> bool:
        """Windows窗口激活"""
        wechat_windows = []

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        # 检查是否微信窗口
                        is_wechat = any(wechat_title in title for wechat_title in self.wechat_window_titles)
                        if is_wechat:
                            # 检查进程
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                import psutil
                                proc = psutil.Process(pid)
                                proc_name = proc.name()
                                if proc_name.lower() in [name.lower() for name in self.wechat_process_names]:
                                    windows.append((hwnd, title, proc_name))
                            except:
                                windows.append((hwnd, title, "未知"))
                except:
                    pass
            return True

        win32gui.EnumWindows(enum_windows_callback, wechat_windows)

        if not wechat_windows:
            self.logger.error("未找到微信窗口")
            return False

        # 选择窗口
        target_window = None
        if window_title:
            for hwnd, title, proc_name in wechat_windows:
                if window_title in title:
                    target_window = (hwnd, title, proc_name)
                    break

        if not target_window:
            # 选择主窗口（通常包含"微信"）
            for hwnd, title, proc_name in wechat_windows:
                if '微信' in title or 'WeChat' in title:
                    target_window = (hwnd, title, proc_name)
                    break

        if not target_window:
            target_window = wechat_windows[0]

        hwnd, title, proc_name = target_window
        self.logger.info(f"找到微信窗口: {title} (进程: {proc_name})")

        # 激活窗口
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)

        # 尝试最大化窗口
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            time.sleep(0.5)
        except:
            self.logger.error("微信未登录，请先登录:")
            return False

        # 激活窗口并置顶
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)

        # 获取窗口位置
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            if left < 0:
                width = right + left
                left = 0
            else:
                width = right - left
            if top < 0:
                height = bottom + top
                top = 0
            else:
                height = bottom - top

            self.region.window_rect = (left, top, width, height)
            self.logger.info(f"微信窗口已激活: 位置({left}, {top}) 大小({width}x{height})")

            # 点击消息图标激活消息面板
            self._click_chat_icon(left, top, width, height)

            return True
        except Exception as e:
            self.logger.error(f"激活窗口失败: {e}")
            return False

    def _click_chat_icon(self, window_left, window_top, window_width, window_height):
        """点击侧边栏的消息图标"""
        try:
            # 计算消息图标位置（侧边栏第一个图标）
            icon_x = window_left + self.region.sidebar_width // 2
            icon_y = window_top + self.region.sidebar_avatar_height + self.region.sidebar_icon_margin + self.region.sidebar_icon_size // 2

            pyautogui.click(icon_x, icon_y)
            self.logger.info(f"已点击消息图标位置: ({icon_x}, {icon_y})")
            time.sleep(1)  # 等待界面响应
            return True
        except Exception as e:
            self.logger.warning(f"点击消息图标失败: {e}")
            return False

    def _activate_macos_window(self, window_title: str = None) -> bool:
        """macOS窗口激活"""
        try:
            from AppKit import NSWorkspace
            import Quartz

            workspace = NSWorkspace.sharedWorkspace()

            # 获取微信应用
            wechat_app = None
            for app in workspace.runningApplications():
                if app.localizedName() in self.wechat_process_names:
                    wechat_app = app
                    break

            if not wechat_app:
                self.logger.error("未找到微信应用")
                return False

            # 激活应用
            wechat_app.activateWithOptions_(NSWorkspace.ActivateIgnoringOtherApps)
            time.sleep(1)

            # 获取窗口列表
            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
                Quartz.kCGNullWindowID
            )

            wechat_window = None
            for window in window_list:
                owner_name = window.get('kCGWindowOwnerName', '')
                window_name = window.get('kCGWindowName', '')

                if owner_name in self.wechat_process_names:
                    if window_title:
                        if window_title in window_name:
                            wechat_window = window
                            break
                    else:
                        if window_name and ('微信' in window_name or 'WeChat' in window_name):
                            wechat_window = window
                            break

            if wechat_window:
                # 获取窗口bounds
                bounds = wechat_window.get('kCGWindowBounds', {})
                x = bounds.get('X', 0)
                y = bounds.get('Y', 0)
                width = bounds.get('Width', 1440)
                height = bounds.get('Height', 900)

                self.region.window_rect = (int(x), int(y), int(width), int(height))
                self.logger.info(f"微信窗口: 位置({x}, {y}) 大小({width}x{height})")

                # 点击消息图标
                self._click_chat_icon(x, y, width, height)
                return True
            else:
                self.logger.warning("未能获取窗口信息")
                return False

        except Exception as e:
            self.logger.error(f"macOS窗口激活失败: {e}")
            return False

    def locate_regions(self) -> bool:
        """
        根据精确布局定位微信窗口中的各个区域
        """
        if not self.region.window_rect:
            self.logger.error("请先激活微信窗口")
            return False

        window_left, window_top, window_width, window_height = self.region.window_rect
        self.logger.info("开始根据精确布局定位微信界面区域...")
        self.logger.info(f"窗口位置: 左上({window_left}, {window_top}) 大小({window_width}x{window_height})")

        # ==================== 主要区域划分 ====================

        # 1. 侧边栏区域 (固定宽度60)
        sidebar_left = window_left
        sidebar_right = sidebar_left + self.region.sidebar_width
        sidebar_top = window_top
        sidebar_bottom = window_top + window_height
        sidebar_rect = (sidebar_left, sidebar_top, sidebar_right, sidebar_bottom)
        self.region.sidebar = sidebar_rect

        # 2. 中间联系人面板 (固定最小宽度200)
        contact_left = sidebar_right
        contact_right = contact_left + self.region.contact_panel_min_width
        contact_top = window_top
        contact_bottom = window_top + window_height
        contact_rect = (contact_left, contact_top, contact_right, contact_bottom)
        self.region.contact_panel = contact_rect

        # 3. 右侧聊天面板 (剩余宽度)
        chat_left = contact_right + self.region.split_line_width
        chat_right = window_left + window_width
        chat_top = window_top
        chat_bottom = window_top + window_height
        chat_rect = (chat_left, chat_top, chat_right, chat_bottom)
        self.region.chat_panel = chat_rect

        # ==================== 侧边栏子区域 ====================

        # 4. 侧边栏头像区域 (高度70)
        avatar_left = sidebar_left
        avatar_right = sidebar_right
        avatar_top = sidebar_top
        avatar_bottom = avatar_top + self.region.sidebar_avatar_height
        avatar_rect = (avatar_left, avatar_top, avatar_right, avatar_bottom)
        self.region.sidebar_avatar = avatar_rect

        # 5. 消息图标 (第一个菜单图标)
        chat_icon_left = sidebar_left + (self.region.sidebar_width - self.region.sidebar_icon_size) // 2
        chat_icon_top = avatar_bottom + self.region.sidebar_icon_margin
        chat_icon_right = chat_icon_left + self.region.sidebar_icon_size
        chat_icon_bottom = chat_icon_top + self.region.sidebar_icon_size
        chat_icon_rect = (chat_icon_left, chat_icon_top, chat_icon_right, chat_icon_bottom)
        self.region.sidebar_chat_icon = chat_icon_rect

        # 6. 通讯录图标 (第二个菜单图标)
        contact_icon_top = chat_icon_bottom + self.region.sidebar_icon_margin
        contact_icon_bottom = contact_icon_top + self.region.sidebar_icon_size
        contact_icon_rect = (chat_icon_left, contact_icon_top, chat_icon_right, contact_icon_bottom)
        self.region.sidebar_contact_icon = contact_icon_rect

        # ==================== 联系人面子区域 ====================

        # 7. 联系人搜索区域 (高度70)
        search_area_left = contact_left
        search_area_right = contact_right
        search_area_top = contact_top
        search_area_bottom = search_area_top + self.region.contact_search_height
        search_area_rect = (search_area_left, search_area_top, search_area_right, search_area_bottom)
        self.region.contact_search_area = search_area_rect

        # 8. 搜索输入框 (宽度115，高度30，左边距40，距离底部15)
        search_input_left = search_area_left + self.region.contact_search_input_left
        search_input_right = search_input_left + self.region.contact_search_input_width
        search_input_bottom = search_area_bottom - self.region.contact_search_input_bottom
        search_input_top = search_input_bottom - self.region.contact_search_input_height
        search_input_rect = (search_input_left, search_input_top, search_input_right, search_input_bottom)
        self.region.contact_search_input = search_input_rect

        # 9. 好友列表区域 (搜索区域下方)
        contact_list_left = contact_left
        contact_list_right = contact_right
        contact_list_top = search_area_bottom
        contact_list_bottom = contact_bottom
        contact_list_rect = (contact_list_left, contact_list_top, contact_list_right, contact_list_bottom)
        self.region.contact_list = contact_list_rect

        # ==================== 聊天面板子区域 ====================

        # 10. 聊天头部区域 (高度70)
        chat_header_left = chat_left
        chat_header_right = chat_right
        chat_header_top = chat_top
        chat_header_bottom = chat_header_top + self.region.chat_header_height
        chat_header_rect = (chat_header_left, chat_header_top, chat_header_right, chat_header_bottom)
        self.region.chat_header = chat_header_rect

        # 11. 聊天区域 (最小高度150)
        chat_input_min_top = chat_bottom - self.region.chat_input_min_height
        chat_input_area_left = chat_left
        chat_input_area_right = chat_right
        chat_input_area_top = chat_input_min_top
        chat_input_area_bottom = chat_bottom
        chat_input_area_rect = (chat_input_area_left, chat_input_area_top, chat_input_area_right,
                                chat_input_area_bottom)
        self.region.chat_input_area = chat_input_area_rect

        # 12. 消息记录区域 (头部下方到聊天区域上方)
        chat_messages_left = chat_left
        chat_messages_right = chat_right
        chat_messages_top = chat_header_bottom
        chat_messages_bottom = chat_input_area_top
        chat_messages_rect = (chat_messages_left, chat_messages_top, chat_messages_right, chat_messages_bottom)
        self.region.chat_messages = chat_messages_rect

        # ==================== 聊天区域子区域 ====================

        # 13. 聊天工具栏 (高度45)
        chat_toolbar_left = chat_input_area_left
        chat_toolbar_right = chat_input_area_right
        chat_toolbar_top = chat_input_area_top
        chat_toolbar_bottom = chat_toolbar_top + self.region.chat_toolbar_height
        chat_toolbar_rect = (chat_toolbar_left, chat_toolbar_top, chat_toolbar_right, chat_toolbar_bottom)
        self.region.chat_toolbar = chat_toolbar_rect

        # 14. 聊天输入框 (工具栏下方到底部区域上方)
        chat_input_left = chat_input_area_left
        chat_input_right = chat_input_area_right
        chat_input_top = chat_toolbar_bottom
        chat_input_bottom = chat_input_area_bottom - self.region.chat_bottom_height
        chat_input_rect = (chat_input_left, chat_input_top, chat_input_right, chat_input_bottom)
        self.region.chat_input_box = chat_input_rect

        # 15. 底部区域 (高度45，在聊天区域内靠底)
        chat_bottom_left = chat_input_area_left
        chat_bottom_right = chat_input_area_right
        chat_bottom_bottom = chat_input_area_bottom
        chat_bottom_top = chat_bottom_bottom - self.region.chat_bottom_height
        chat_bottom_rect = (chat_bottom_left, chat_bottom_top, chat_bottom_right, chat_bottom_bottom)
        self.region.chat_bottom_area = chat_bottom_rect

        # 16. 发送按钮 (宽度100，高度30，右边距20，底边距15)
        send_left = chat_bottom_right - self.region.chat_send_right - self.region.chat_send_width
        send_right = send_left + self.region.chat_send_width
        send_bottom = chat_bottom_bottom - self.region.chat_send_bottom
        send_top = send_bottom - self.region.chat_send_height
        send_rect = (send_left, send_top, send_right, send_bottom)
        self.region.chat_send_button = send_rect

        # ==================== 搜索结果区域（关键修改）====================

        # 17. 搜索结果第一个联系人的位置（搜索输入框下方，紧挨着）
        # 搜索浮窗紧挨着搜索输入框，浮窗宽度320，与输入框左对齐
        search_popup_width = 320  # 浮窗宽度

        # 浮窗左边界与搜索输入框左对齐
        search_popup_left = search_input_left

        # 搜索结果第一个联系人：距离浮窗顶部30，高度使用联系人列表中的70
        search_result_first_left = search_popup_left
        search_result_first_right = search_result_first_left + search_popup_width
        search_result_first_top = search_input_bottom + 30  # 紧挨着搜索框下方 + 30像素
        search_result_first_bottom = search_result_first_top + self.region.contact_item_height  # 使用联系人的高度70

        search_result_first_rect = (search_result_first_left, search_result_first_top,
                                    search_result_first_right, search_result_first_bottom)
        self.region.search_result_first = search_result_first_rect

        # 保存区域配置
        self._save_region_config()

        self.logger.info("所有区域定位完成")
        return True

    def _save_region_config(self):
        """保存区域配置到文件"""
        try:
            config = {}
            for field_name in self.region.__dataclass_fields__:
                value = getattr(self.region, field_name)
                if isinstance(value, tuple):
                    config[field_name] = list(value)
                else:
                    config[field_name] = value

            config['timestamp'] = datetime.now().isoformat()
            config['platform'] = platform.system()

            with open("config/wechat_regions.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.logger.info("区域配置已保存到 config/wechat_regions.json")

        except Exception as e:
            self.logger.error(f"保存区域配置失败: {e}")

    def _load_region_config(self) -> bool:
        """从文件加载区域配置"""
        try:
            config_file = Path("config/wechat_regions.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                # 检查平台是否匹配
                if config.get('platform') != platform.system():
                    self.logger.warning(f"配置来自不同平台({config.get('platform')})，重新定位")
                    return False

                # 更新区域配置
                for key, value in config.items():
                    if hasattr(self.region, key):
                        if isinstance(value, list):
                            setattr(self.region, key, tuple(value))
                        else:
                            setattr(self.region, key, value)

                self.logger.info("区域配置已从文件加载")
                return True
            return False

        except Exception as e:
            self.logger.error(f"加载区域配置失败: {e}")
            return False

    def _safe_click(self, x: int, y: int, click_type: str = 'left',
                    move_duration: float = 0.5, random_offset: int = 5,
                    description: str = "") -> bool:
        """
        安全的鼠标点击，带有自然的移动轨迹
        """
        try:
            if description:
                self.logger.debug(f"安全点击: {description}")

            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()

            # 添加随机偏移
            target_x = x + random.randint(-random_offset, random_offset)
            target_y = y + random.randint(-random_offset, random_offset)

            # 确保在屏幕范围内
            screen_width, screen_height = pyautogui.size()
            target_x = max(10, min(target_x, screen_width - 10))
            target_y = max(10, min(target_y, screen_height - 10))

            # 创建贝塞尔曲线路径（模拟人类鼠标移动）
            points = self._create_bezier_path(current_x, current_y, target_x, target_y, 20)

            # 按路径移动鼠标
            for point_x, point_y in points:
                pyautogui.moveTo(point_x, point_y)
                time.sleep(move_duration / len(points))

            # 在目标位置附近小范围随机移动（模拟人类瞄准）
            for _ in range(random.randint(2, 4)):
                hover_x = target_x + random.randint(-2, 2)
                hover_y = target_y + random.randint(-2, 2)
                pyautogui.moveTo(hover_x, hover_y, duration=0.05)
                time.sleep(0.05)

            # 最后移动到精确位置
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(0.1)

            # 执行点击
            if click_type == 'left':
                pyautogui.click(x, y)
            elif click_type == 'double':
                pyautogui.doubleClick(x, y)
            elif click_type == 'right':
                pyautogui.rightClick(x, y)

            # 点击后随机停留
            time.sleep(random.uniform(0.1, 0.3))

            return True

        except Exception as e:
            self.logger.error(f"安全点击失败: {e}")
            # 失败时使用普通点击
            try:
                if click_type == 'left':
                    pyautogui.click(x, y)
                elif click_type == 'double':
                    pyautogui.doubleClick(x, y)
                return True
            except:
                return False

    def _create_bezier_path(self, start_x: int, start_y: int, end_x: int, end_y: int,
                            num_points: int = 20) -> List[Tuple[int, int]]:
        """
        创建贝塞尔曲线路径，模拟人类鼠标移动
        """
        import random

        # 生成控制点
        control1_x = start_x + (end_x - start_x) * random.uniform(0.2, 0.4)
        control1_y = start_y + (end_y - start_y) * random.uniform(0.2, 0.4)

        control2_x = start_x + (end_x - start_x) * random.uniform(0.6, 0.8)
        control2_y = start_y + (end_y - start_y) * random.uniform(0.6, 0.8)

        points = []
        for i in range(num_points):
            t = i / (num_points - 1)

            # 三次贝塞尔曲线公式
            x = (1 - t) ** 3 * start_x + \
                3 * (1 - t) ** 2 * t * control1_x + \
                3 * (1 - t) * t ** 2 * control2_x + \
                t ** 3 * end_x

            y = (1 - t) ** 3 * start_y + \
                3 * (1 - t) ** 2 * t * control1_y + \
                3 * (1 - t) * t ** 2 * control2_y + \
                t ** 3 * end_y

            # 添加轻微随机抖动
            x += random.randint(-1, 1)
            y += random.randint(-1, 1)

            points.append((int(x), int(y)))

        return points

    def _type_text_safely(self, text: str, delay: float = 0.05):
        """安全输入文本，确保字符能被正确接收"""
        try:
            # 方法1：先尝试直接typewrite
            pyautogui.typewrite(text, interval=delay)
            time.sleep(0.3)

            # 检查是否输入成功（可以通过截图检查）
            # 如果失败，尝试其他方法

            return True
        except Exception as e:
            self.logger.warning(f"直接输入失败: {e}")
            return False

    def _type_with_clipboard(self, text: str):
        """使用剪贴板复制粘贴"""
        try:
            # 保存当前剪贴板内容
            original_clipboard = pyperclip.paste()

            # 复制文本到剪贴板
            pyperclip.copy(text)
            time.sleep(0.3)

            # 粘贴文本
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)

            # 恢复剪贴板内容
            pyperclip.copy(original_clipboard)

            self.logger.info(f"使用剪贴板输入: {text}")
            return True
        except Exception as e:
            self.logger.error(f"剪贴板输入失败: {e}")
            # 如果pyperclip不可用，尝试备用方法
            try:
                # 备用：模拟Ctrl+V
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                time.sleep(0.2)

                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.3)
                return True
            except:
                return False

    def search_and_send_message(self, contact_name: str, message: str = "您好") -> bool:
        """
        搜索联系人并发送消息（整合功能）
        """
        # 检查窗口激活状态
        if not self.activate_wechat_window():
            self.logger.error("无法激活微信窗口，等待60秒后重试")

        self.logger.info(f"开始执行：搜索联系人 '{contact_name}' 并发送消息: '{message}'")

        # 使用公共方法搜索并打开联系人
        if not self._search_and_open_contact(contact_name):
            return False

        try:
            # ========== 输入消息 ==========
            if not self.region.chat_input_box:
                self.logger.error("聊天输入框区域未定位")
                return False

            input_x1, input_y1, input_x2, input_y2 = self.region.chat_input_box
            input_center_x = (input_x1 + input_x2) // 2
            input_center_y = (input_y1 + input_y2) // 2

            self.logger.info(f"1. 安全点击聊天输入框，位置: ({input_center_x}, {input_center_y})")

            # 安全点击输入框
            self._safe_click(input_center_x, input_center_y,
                             move_duration=random.uniform(0.3, 0.5),
                             description="点击聊天输入框")
            time.sleep(0.5)

            # 清空输入框
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)

            # 再次安全点击确保焦点
            self._safe_click(input_center_x + random.randint(-1, 1),
                             input_center_y + random.randint(-1, 1),
                             move_duration=random.uniform(0.05, 0.1),
                             description="微调焦点")
            time.sleep(0.3)

            # 输入固定消息 - 优先使用剪贴板
            self.logger.info(f"2. 输入消息: {message}")

            if self._type_with_clipboard(message):
                self.logger.info("使用剪贴板输入消息成功")
            else:
                # 备用：直接输入
                self.logger.info("尝试直接输入消息...")
                for char in message:
                    pyautogui.typewrite(char)
                    time.sleep(0.1)

            time.sleep(0.5)

            # ========== 点击发送按钮 ==========
            if not self.region.chat_send_button:
                self.logger.error("发送按钮区域未定位")
                return False

            send_x1, send_y1, send_x2, send_y2 = self.region.chat_send_button
            send_center_x = (send_x1 + send_x2) // 2
            send_center_y = (send_y1 + send_y2) // 2

            self.logger.info(f"3. 安全点击发送按钮，位置: ({send_center_x}, {send_center_y})")

            self._safe_click(send_center_x, send_center_y,
                             move_duration=random.uniform(0.2, 0.4),
                             description="点击发送按钮")

            time.sleep(1.0)
            self.logger.info(f"✅ 消息发送完成！联系人: {contact_name}, 消息: {message}")

            return True
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            return False

    def get_chat_history(self, contact_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取指定联系人的最新聊天记录（只获取对方消息）
        """
        # 检查窗口激活状态
        if not self.activate_wechat_window():
            self.logger.error("无法激活微信窗口，等待60秒后重试")

        # 先搜索并打开该联系人
        result = self._search_and_open_contact(contact_name)
        if not result:
            self.logger.error(f"无法找到联系人: {contact_name}")
            return []

        # 使用上面修改的方法
        chat_data = self.get_chat_messages_by_copy(contact_name, limit)

        # 返回消息列表格式
        return chat_data

    def get_status(self) -> Dict[str, Any]:
        """获取微信状态"""
        return {
            'wechat_running': self.is_wechat_running(),
            'window_rect': self.region.window_rect,
            'regions_loaded': self.region.sidebar is not None,
            'platform': platform.system(),
            'timestamp': datetime.now().isoformat()
        }

    def _search_and_open_contact(self, contact_name: str) -> bool:
        """
        搜索并打开指定联系人（公共方法）
        """
        try:
            if self.currentWindowUser == contact_name:
                return True

            search_x1, search_y1, search_x2, search_y2 = self.region.contact_search_input
            search_center_x = (search_x1 + search_x2) // 2
            search_center_y = (search_y1 + search_y2) // 2

            self.logger.info(f"搜索并打开联系人: {contact_name}")

            # 点击搜索框
            self._safe_click(search_center_x, search_center_y,
                             move_duration=random.uniform(0.3, 0.5),
                             description="点击搜索框")
            time.sleep(0.8)

            # 清空输入框
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)

            # 输入联系人名称
            if self._type_with_clipboard(contact_name):
                self.logger.info("使用剪贴板输入联系人成功")
            else:
                for char in contact_name:
                    pyautogui.typewrite(char)
                    time.sleep(0.1)

            time.sleep(0.5)  # 等待搜索结果

            # 点击第一个搜索结果
            if self.region.search_result_first:
                result_x1, result_y1, result_x2, result_y2 = self.region.search_result_first
                result_center_x = (result_x1 + result_x2) // 2 - 30
                result_center_y = (result_y1 + result_y2) // 2

                self._safe_click(result_center_x, result_center_y,
                                 move_duration=random.uniform(0.4, 0.6),
                                 description="点击搜索结果")
            else:
                result_center_x = search_center_x
                result_center_y = search_center_y + 70
                pyautogui.click(result_center_x, result_center_y)

            time.sleep(2)  # 等待聊天界面加载
            self.currentWindowUser = contact_name
            return True

        except Exception as e:
            self.logger.error(f"搜索并打开联系人失败: {e}")
            return False

    def _scroll_to_bottom(self):
        """滚动消息记录区域到底部"""
        try:
            if not self.region.chat_messages:
                return False

            msg_x1, msg_y1, msg_x2, msg_y2 = self.region.chat_messages
            scroll_x = (msg_x1 + msg_x2) // 2
            scroll_y = (msg_y1 + msg_y2) // 2

            self.logger.info("滚动到消息底部...")

            # 点击消息区域确保焦点
            pyautogui.click(scroll_x, scroll_y)
            time.sleep(0.3)

            # 再向下滚动一点确保在最新位置
            for i in range(2):
                pyautogui.scroll(500)
                time.sleep(0.1)

            time.sleep(0.5)
            return True

        except Exception as e:
            self.logger.error(f"滚动到底部失败: {e}")
            return False

    def get_chat_messages_by_copy(self, contact_name, limit: int = 10) -> List[Dict[str, Any]]:
        """
        通过右键复制获取聊天消息
        1. 先定位所有消息气泡的位置
        2. 从最新的（最底部）开始，依次右键复制
        """
        messages = []

        try:
            # 1. 确保聊天消息区域已定位
            if not self.region.chat_messages:
                self.logger.error("聊天消息区域未定位")
                return messages

            # 获取聊天区域坐标
            msg_x1, msg_y1, msg_x2, msg_y2 = self.region.chat_messages
            region_width = msg_x2 - msg_x1
            region_height = msg_y2 - msg_y1
            self.logger.info(
                f"聊天消息区域: 位置({msg_x1},{msg_y1})-({msg_x2},{msg_y2}) 大小({region_width}x{region_height})")

            # 2. 使用与draw_messages_overlay相同的方法定位消息气泡
            message_rects = self._locate_message_bubbles()

            if not message_rects:
                self.logger.warning("未检测到任何消息气泡")
                return messages

            self.logger.info(f"检测到 {len(message_rects)} 个消息气泡")

            # 3. 按垂直位置排序（从底部到顶部，最新的先处理）
            message_rects.sort(key=lambda rect: rect[1], reverse=True)  # 按y坐标降序

            # 4. 限制处理数量，从最新的开始
            message_rects = message_rects[:limit]

            # 5. 对每个消息气泡执行右键复制
            for i, (x, y, w, h) in enumerate(message_rects):
                try:
                    # 计算消息气泡的中心点（相对坐标）
                    bubble_center_x = x + w // 2
                    bubble_center_y = y + h // 2

                    is_customer_message = (bubble_center_x < region_width * 0.4)
                    if is_customer_message:
                        copy_center_x = x + w - 20
                    else:
                        copy_center_x = x + 20
                    # 右键点击消息气泡中心（稍微偏移，避免点击在边缘）

                    # 转换为绝对屏幕坐标
                    absolute_x = msg_x1 + copy_center_x
                    absolute_y = msg_y1 + bubble_center_y

                    self.logger.info(f"处理消息 {i + 1}: 位置({absolute_x},{absolute_y}) 大小({w}x{h})")

                    click_x = absolute_x
                    click_y = absolute_y
                    pyautogui.click(click_x, click_y, button='right')
                    time.sleep(0.5)  # 等待右键菜单弹出，给足时间

                    # 获取复制菜单位置
                    copy_click_x, copy_click_y = self.get_copy_menu_position(click_x, click_y)

                    self.logger.debug(f"复制菜单位置: ({copy_click_x}, {copy_click_y})")

                    # 点击"复制"选项
                    pyautogui.click(copy_click_x, copy_click_y)
                    time.sleep(0.3)  # 等待复制完成

                    # 读取剪贴板内容
                    try:
                        clipboard_content = pyperclip.paste().strip()
                        if clipboard_content and len(clipboard_content) > 0:
                            # 判断消息方向（左侧是对方消息，右侧是自己消息）
                            is_right_side = bubble_center_x > (region_width // 2)

                            message = {
                                "content": clipboard_content,
                                "from": "me" if is_right_side else "you",
                                "position": (absolute_x, absolute_y),
                                "size": f"{w}x{h}",
                                "time": time.strftime("%H:%M:%S"),
                                "timestamp": time.time(),
                                "index": i + 1,
                                "contact": contact_name
                            }
                            messages.append(message)

                            self.logger.debug(f"复制到消息 {i + 1}: {clipboard_content[:50]}...")
                        else:
                            self.logger.debug(f"消息 {i + 1}: 剪贴板内容为空")
                    except Exception as clip_error:
                        self.logger.debug(f"读取剪贴板失败: {clip_error}")

                    # 点击其他位置关闭右键菜单（点击原始消息位置左上方）
                    close_x = max(click_x - 50, 10)
                    close_y = max(click_y - 50, 10)
                    pyautogui.click(close_x, close_y)
                    time.sleep(0.2)

                except Exception as e:
                    self.logger.error(f"处理消息 {i + 1} 失败: {e}")
                    # 如果失败，尝试ESC键关闭菜单
                    try:
                        pyautogui.press('esc')
                        time.sleep(0.2)
                    except:
                        pass
                    continue

            self.logger.info(f"成功获取 {len(messages)} 条消息")
            return messages

        except Exception as e:
            self.logger.error(f"通过复制获取消息失败: {e}")
            return messages

    def get_copy_menu_position(self, click_x: int, click_y: int) -> tuple[int, int]:
        """
        计算右键菜单中"复制"选项的点击位置
        """
        window_left, window_top, window_width, window_height = self.region.window_rect

        # 右键菜单的基本属性
        menu_width = self.region.chat_right_click_menu_width  # 菜单宽度
        menu_height = self.region.chat_right_click_menu_height  # 菜单高度
        item_height = self.region.chat_right_click_item_height  # 每个菜单项的高度

        # 复制按钮通常是第一个菜单项
        copy_item_offset_y = item_height // 2  # 点击第一个菜单项的中心位置

        # 初始菜单位置（菜单在鼠标右下方显示）
        # 注意：右键菜单的左上角位于鼠标点击位置的右下边缘
        menu_x = click_x
        menu_y = click_y

        # 检查是否需要调整菜单位置（避免超出屏幕边界）
        # 如果菜单会超出屏幕右边界，则左移菜单
        if menu_x + menu_width > window_width:
            menu_x = window_width - menu_width

        # 如果菜单会超出屏幕下边界，则上移菜单
        if menu_y + menu_height > window_height:
            menu_y = window_height - menu_height

        # 计算复制按钮的点击位置（第一个菜单项的中心）
        copy_click_x = menu_x + menu_width // 2  # 菜单水平中心
        copy_click_y = menu_y + copy_item_offset_y  # 第一个菜单项垂直中心

        return copy_click_x, copy_click_y

    def _locate_message_bubbles(self) -> List[Dict[str, Any]]:
        """
        定位聊天消息气泡（复用draw_messages_overlay中的逻辑）
        返回: [(x, y, w, h), ...] 相对于聊天区域的坐标
        """
        message_rects = []
        try:

            # 1. 检查聊天消息区域是否已定位
            if not self.region.chat_messages:
                return message_rects

            # 2. 获取聊天区域坐标
            msg_x1, msg_y1, msg_x2, msg_y2 = self.region.chat_messages
            width = msg_x2 - msg_x1
            height = msg_y2 - msg_y1

            logger.info(f"聊天消息区域: 位置({msg_x1},{msg_y1})-({msg_x2},{msg_y2}) 大小({width}x{height})")

            # 3. 截取聊天区域
            logger.info("截取聊天区域...")
            time.sleep(0.5)

            screenshot = ImageGrab.grab(bbox=(msg_x1, msg_y1, msg_x2, msg_y2))
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # 转换为numpy数组用于识别
            covered_array = np.array(screenshot.convert('RGB'))  # 转回RGB处理

            # 4. 获取背景色（采样左上角区域）
            logger.info("采样背景色...")
            # 采样左上角5x5区域
            sample_region = covered_array[0:5, 0:5]

            # 计算平均颜色
            background_color = np.mean(sample_region, axis=(0, 1)).astype(int)
            logger.info(f"检测到的背景色: R={background_color[0]}, G={background_color[1]}, B={background_color[2]}")

            # 5. 创建背景掩码（找到背景色区域）
            logger.info("创建背景掩码...")
            # 定义颜色容差
            tolerance = 20  # 颜色容差范围
            # 计算每个像素与背景色的差异
            diff = np.abs(covered_array - background_color)
            # 创建掩码：如果三个通道都在容差范围内，则为背景
            background_mask = np.all(diff <= tolerance, axis=2)
            # 6. 去除背景色：将背景变为黑色
            logger.info("去除背景色...")
            # 创建去除背景的图像
            background_removed = covered_array.copy()
            # 将背景区域设为黑色
            background_removed[background_mask] = [0, 0, 0]

            # 5. 第二步：使用原有的识别方法在覆盖后的图片上识别
            logger.info("在颜色覆盖的图像上识别气泡和头像...")

            # 检测头像和消息（在覆盖后的图片上）
            gray = cv2.cvtColor(background_removed, cv2.COLOR_RGB2GRAY)
            # 对非背景区域进行对比度增强
            # 使用CLAHE（限制对比度自适应直方图均衡化）
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # 使用自适应阈值 - 调整参数以更好地检测覆盖后的图像
            adaptive_thresh = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                15,  # 增加块大小以捕获更大区域
                5  # 调整常数
            )

            # 查找轮廓
            contours, hierarchy = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            logger.info(f"找到 {len(contours)} 个轮廓")
            # 方法1：使用层级关系过滤
            contours = self._filter_contours_by_hierarchy(contours, hierarchy, width)

            logger.info(f"过滤之后还有 {len(contours)} 个轮廓")

            # 分析轮廓
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                message_rects.append((x, y, w, h))

            logger.info(f"检测到{len(message_rects)} 条消息")
            return message_rects
        except Exception as e:
            logger.error(f"检测消息失败: {e}")
            return []

    def _filter_contours_by_hierarchy(self, contours, hierarchy, width):
        """
        使用头像边界过滤轮廓
        """
        if hierarchy is None:
            return []

        hierarchy = hierarchy[0]
        filtered_contours = []
        avatar_boundary = self.region.chat_avatar_boundary

        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)

            # 要求1：过滤掉高度小于30的
            if h < 30 or w<30:
                continue

            # 要求2：使用头像边界过滤 - 不在头像区域内
            aspect_ratio = w / h if h > 0 else 0
            # 左侧头像区域：x < 头像边界
            is_in_left_avatar_area = (x < avatar_boundary) and (0.8 <= aspect_ratio <= 1.2)
            # 右侧头像区域：x + w > width - 头像边界
            is_in_right_avatar_area =  (x + w > width - avatar_boundary) and (0.8 <= aspect_ratio <= 1.2)

            if is_in_left_avatar_area or is_in_right_avatar_area:
                logger.debug(f"过滤头像区域内的轮廓: 位置({x},{y}) 大小({w}x{h})")
                continue

            # 要求3：保留所有不在头像区域内的轮廓（不再检查宽高比）
            filtered_contours.append(contour)

        return filtered_contours

    def _click_and_valid_contact_by_index(self, index: int,contact_list:List[str]) -> bool:
        """
        点击联系人列表中指定索引位置的联系人

        Args:
            index: 联系人索引（从0开始）
        Returns:
            bool: 是否成功点击
        """
        try:
            if not self.region.contact_list:
                self.logger.error("联系人列表区域未定位")
                return False
            # if contact_list.__contains__(_get_current_contact()) :
            #     self.logger.warning("当前联系人不在指定范围内")
            #     return False
            # 获取联系人列表区域

            contact_x1, contact_y1, contact_x2, contact_y2 = self.region.contact_list

            # 每个联系人的高度
            item_height = self.region.contact_item_height

            # 计算点击位置
            # 第一个联系人的点击位置（中心偏下一点，避免点击到边界）
            base_y = contact_y1 + item_height // 2

            # 计算当前索引的点击位置
            click_x = (contact_x1 + contact_x2) // 2
            click_y = base_y + (index * item_height)

            # 确保点击位置在联系人列表区域内
            if click_y > contact_y2 - 10:
                self.logger.warning(f"索引 {index} 超出联系人列表范围")
                # 如果超出范围，点击最后一个可见位置
                return False
            self.logger.info(f"点击联系人列表第 {index + 1} 个位置: ({click_x}, {click_y})")

            # 安全点击
            self._safe_click(click_x, click_y,
                             move_duration=random.uniform(0.3, 0.5),
                             description=f"点击列表第{index + 1}个联系人")

            time.sleep(1)  # 等待聊天界面加载

            return True

        except Exception as e:
            self.logger.error(f"点击列表联系人失败: {e}")
            return False

    def auto_process_contacts(self, contact_list: List[str], max_polling_times: int = 5,
                              api_url: str = "http://localhost:8000/api/chat/message",
                              api_key: str = "") -> None:
        """
        自动处理联系人，轮询检查新消息并自动回复

        Args:
            max_polling_times: 最大轮询次数（点击联系人的次数）
            api_url: AI聊天接口URL
        """
        # 确保微信窗口已激活
        if not self.activate_wechat_window():
            self.logger.error("无法激活微信窗口，等待60秒后重试")
            return

        # 记录处理轮次
        round_count = 0
        while True:
            round_count += 1
            self.logger.info(f"=== 开始第 {round_count} 轮处理 ===")

            try:
                # 从索引0开始循环点击联系人
                for i in range(max_polling_times):
                    try:
                        self.logger.info(f"处理第 {i + 1}/{max_polling_times} 个联系人")

                        # 点击指定索引的联系人
                        if i!=0 and not self._click_and_valid_contact_by_index(i, contact_list):
                            continue
                        time.sleep(1)  # 等待聊天界面加载

                        # 检查是否有新消息
                        # 定位消息气泡
                        message_rects = self._locate_message_bubbles()

                        has_new_message = self._check_new_message(message_rects)

                        if has_new_message:
                            self.logger.info(f"检测到新消息，处理当前联系人")

                            # 获取最新消息
                            latest_messages = self._get_latest_messages(message_rects)

                            if latest_messages:
                                # 调用AI接口获取回复
                                ai_replies = self._call_ai_api(latest_messages, api_url, api_key)

                                if ai_replies:
                                    self.logger.info(f"收到 {len(ai_replies)} 条AI回复")

                                    # 发送多条回复
                                    for reply_msg in ai_replies:
                                        content = reply_msg.get('content', '').strip()
                                        pause_ms = reply_msg.get('pause_ms', 500)  # 默认500ms

                                        if content:
                                            self.logger.info(f"发送回复: {content[:50]}... (间隔: {pause_ms}ms)")

                                            # 发送消息
                                            success = self._send_message_directly(content)
                                            if success:
                                                self.logger.info(f"回复发送成功，等待 {pause_ms}ms")
                                                # 根据API返回的间隔时间等待
                                                time.sleep(pause_ms / 1000.0)
                                            else:
                                                self.logger.error("回复发送失败")
                                                time.sleep(1)  # 失败后等待1秒
                                        else:
                                            self.logger.warning("跳过空内容回复")
                                else:
                                    self.logger.warning("AI接口返回空回复")
                            else:
                                self.logger.info("未获取到客户消息")
                        else:
                            self.logger.info(f"无新消息，跳过当前联系人")

                        # 短暂等待，准备处理下一个
                        time.sleep(1)

                    except Exception as contact_error:
                        self.logger.error(f"处理联系人时出错: {contact_error}")
                        time.sleep(3)
                        continue

                # 完成一轮处理，等待5分钟
                self.logger.info(f"=== 第 {round_count} 轮处理完成，等待5分钟后继续 ===")
                time.sleep(300)  # 5分钟

            except Exception as e:
                self.logger.error(f"自动处理异常: {e}")
                time.sleep(60)  # 等待1分钟后重试

    def _check_new_message(self, message_rects) -> bool:
        """
        检查当前聊天窗口是否有最新消息（对方发来的）
        """
        try:
            if not self.region.chat_messages:
                self.logger.warning("聊天消息区域未定位")
                return False

            # 获取聊天区域坐标
            msg_x1, msg_y1, msg_x2, msg_y2 = self.region.chat_messages
            width = msg_x2 - msg_x1
            height = msg_y2 - msg_y1

            if not message_rects:
                self.logger.debug("未检测到任何消息气泡")
                return False

            # 找到Y坐标最大的消息（最底部）
            message_rects.sort(key=lambda rect: rect[1], reverse=True)
            x, y, w, h = message_rects[0]  # 最底部的一条消息

            # 计算消息气泡的中心点
            bubble_center_x = x + w // 2

            # 使用头像边界作为判断标准
            # 如果消息在左侧头像边界右侧，且在整个聊天区域左侧1/3范围内，认为是客户消息
            # 这比简单的中心线判断更准确
            avatar_boundary = self.region.chat_avatar_boundary
            is_customer_message = (bubble_center_x < width * 0.4)

            self.logger.debug(
                f"最新消息位置: x={x}, 中心x={bubble_center_x}, 头像边界={avatar_boundary}, 是否客户消息={is_customer_message}")

            return is_customer_message

        except Exception as e:
            self.logger.error(f"检查新消息失败: {e}")
            return False

    def _send_message_directly(self, message: str) -> bool:
        """
        参数:
            message: 要发送的消息内容
        """
        try:
            if not self.region.chat_input_box:
                self.logger.error("聊天输入框区域未定位")
                return False

            # 获取输入框坐标
            input_x1, input_y1, input_x2, input_y2 = self.region.chat_input_box
            input_center_x = (input_x1 + input_x2) // 2
            input_center_y = (input_y1 + input_y2) // 2

            self.logger.info(f"准备发送消息: {message[:50]}...")

            # 点击输入框获取焦点
            self._safe_click(input_center_x, input_center_y,
                             move_duration=random.uniform(0.3, 0.5),
                             description="点击聊天输入框")
            time.sleep(0.5)

            # 清空输入框
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            time.sleep(0.1)

            # 输入消息 - 优先使用剪贴板
            self.logger.info("输入消息内容...")
            if self._type_with_clipboard(message):
                self.logger.info("使用剪贴板输入消息成功")
            else:
                # 备用：直接输入
                for char in message:
                    pyautogui.typewrite(char)
                    time.sleep(random.uniform(0.05, 0.1))  # 随机间隔，更自然

            time.sleep(0.3)  # 等待输入完成

            # 点击发送按钮
            if not self.region.chat_send_button:
                self.logger.error("发送按钮区域未定位")
                return False

            send_x1, send_y1, send_x2, send_y2 = self.region.chat_send_button
            send_center_x = (send_x1 + send_x2) // 2
            send_center_y = (send_y1 + send_y2) // 2

            self.logger.info("点击发送按钮...")
            self._safe_click(send_center_x, send_center_y,
                             move_duration=random.uniform(0.2, 0.4),
                             description="点击发送按钮")

            time.sleep(0.5)  # 等待发送完成
            self.logger.info("消息发送完成")
            return True

        except Exception as e:
            self.logger.error(f"直接发送消息失败: {e}")
            return False

    def _get_latest_messages(self, message_rects) -> List[Dict[str, Any]]:
        """
        获取客户最新的连续消息（直到遇到自己发送的消息为止）

        逻辑：从最新的消息开始，连续获取客户（左侧）消息，直到遇到自己发送的消息
        例如：AABAA -> 取AA（A是客户，B是自己）

        Args:
            max_count: 最大检查的消息数量
        Returns:
            List[Dict]: 客户最新的连续消息列表
        """
        try:
            if not self.region.chat_messages:
                self.logger.error("聊天消息区域未定位")
                return []

            if not message_rects:
                self.logger.warning("未检测到任何消息气泡")
                return []
            # 获取聊天区域坐标
            msg_x1, msg_y1, msg_x2, msg_y2 = self.region.chat_messages
            width = msg_x2 - msg_x1

            # 按垂直位置排序（从底部到顶部，最新的先处理）
            message_rects.sort(key=lambda rect: rect[1], reverse=True)
            customer_messages = []

            for i, (x, y, w, h) in enumerate(message_rects):
                try:
                    # 计算消息气泡的中心点（相对坐标）
                    bubble_center_x = x + w // 2


                    # 使用头像边界和相对位置判断消息方向
                    is_customer_message =  (bubble_center_x < width * 0.4)
                    if is_customer_message:
                        copy_center_x = x + w -20
                    else:
                        copy_center_x = x + 20
                    # 如果是自己的消息，停止收集
                    if not is_customer_message:
                        self.logger.debug(f"遇到自己发送的消息，停止收集")
                        break

                    # 转换为绝对屏幕坐标
                    absolute_x = msg_x1 + copy_center_x
                    absolute_y = msg_y1 + (y + h // 2)

                    # 右键点击消息气泡中心
                    click_x = absolute_x
                    click_y = absolute_y
                    pyautogui.click(click_x, click_y, button='right')
                    time.sleep(0.5)
                    ## 先情况剪切板
                    pyperclip.copy("")
                    time.sleep(0.1)
                    if IS_WINDOWS:
                        try:
                            import win32clipboard
                            win32clipboard.OpenClipboard()
                            win32clipboard.EmptyClipboard()
                            win32clipboard.CloseClipboard()
                            time.sleep(0.1)
                        except:
                            pass
                    # 获取复制菜单位置并点击
                    copy_click_x, copy_click_y = self.get_copy_menu_position(click_x, click_y)
                    pyautogui.click(copy_click_x, copy_click_y)
                    time.sleep(0.3)
                    clipboard_content = pyperclip.paste().strip()
                    # 读取剪贴板内容
                    if clipboard_content and len(clipboard_content) > 0:
                        customer_messages.append(clipboard_content)

                except Exception as e:
                    self.logger.error(f"处理消息 {i + 1} 失败: {e}")
                    continue

            # 反转列表，使消息按时间顺序排列（从旧到新）
            customer_messages.reverse()

            self.logger.info(f"成功获取 {len(customer_messages)} 条客户连续消息")
            return customer_messages

        except Exception as e:
            self.logger.error(f"获取客户最新消息失败: {e}")
            return []

    def _call_ai_api(self, customer_messages: List[str], api_url: str, api_key: str) -> List[Dict[str, Any]]:
        """
        调用AI聊天接口（新版API格式）

        Args:
            customer_messages: 客户消息列表
            api_url: API地址
            api_key: API密钥
        Returns:
            List[Dict]: AI回复消息列表，包含content和pause_ms
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # 将客户消息列表合并为单个字符串
            combined_message = "\n".join(customer_messages)

            data = {
                "user_id": "7",  # 预设user_id为7
                "message": combined_message,
                "username": ""  # 空字符串
            }

            self.logger.info(f"调用AI接口: {api_url}")
            self.logger.info(f"请求消息: {len(customer_messages)}条，合并为: {combined_message[:50]}...")

            response = requests.post(
                api_url,
                json=data,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"API响应: {result}")

                if result.get("success"):
                    messages = result.get("data", {}).get("messages", [])
                    self.logger.info(f"收到AI回复: {len(messages)}条消息")
                    return messages
                else:
                    self.logger.error(f"API返回失败: {result.get('message', '未知错误')}")
                    return []
            else:
                self.logger.error(f"AI接口调用失败: {response.status_code} - {response.text}")
                return []

        except requests.exceptions.Timeout:
            self.logger.error("AI接口调用超时")
            return []
        except requests.exceptions.ConnectionError:
            self.logger.error("无法连接到AI接口")
            return []
        except Exception as api_error:
            self.logger.error(f"调用AI接口失败: {api_error}")
            import traceback
            traceback.print_exc()
            return []

def main():
    parser = argparse.ArgumentParser(description='微信桌面自动化工具')
    parser.add_argument('action', choices=[
        'start', 'activate', 'search_and_send', 'get_history', 'auto_process', 'help'
    ], help='要执行的操作')

    parser.add_argument('--contact', help='联系人名称（用于search_and_send和get_history操作）')
    parser.add_argument('--message', help='消息内容（用于search_and_send操作）')
    parser.add_argument('--limit', type=int, default=10, help='获取历史记录的数量限制（用于get_history操作）')
    parser.add_argument('--polling_times', type=int, default=5, help='轮询次数（用于auto_process操作）')
    parser.add_argument('--api_url', help='AI接口URL（用于auto_process操作）')
    parser.add_argument('--api_key', required='auto_process' in sys.argv, help='API密钥（auto_process操作必需）')
    parser.add_argument('--title', help='窗口标题（用于activate操作）')

    args = parser.parse_args()

    # 创建实例
    wechat = WeChatAutomation()

    try:
        if args.action == 'start':
            result = wechat.start_wechat()
            if result:
                print("✅ 微信启动成功")
                print(json.dumps({'success': True, 'message': '微信启动成功'}, ensure_ascii=False))
            else:
                print("❌ 微信启动失败")
                print(json.dumps({'success': False, 'message': '微信启动失败'}, ensure_ascii=False))

        elif args.action == 'activate':
            result = wechat.activate_wechat_window(args.title)
            if result:
                print("✅ 微信窗口激活成功")
                print(json.dumps({'success': True, 'message': '微信窗口激活成功'}, ensure_ascii=False))
            else:
                print("❌ 微信窗口激活失败")
                print(json.dumps({'success': False, 'message': '微信窗口激活失败'}, ensure_ascii=False))

        elif args.action == 'search_and_send':
            if not args.contact:
                print("错误：需要指定联系人名称 (--contact)")
                sys.exit(1)

            message = args.message if args.message else "您好"
            print(f"准备发送消息给: {args.contact}")
            print(f"消息内容: {message}")

            result = wechat.search_and_send_message(args.contact, message)

            if result:
                print("✅ 消息发送成功")
                print(json.dumps({
                    'success': True,
                    'contact': args.contact,
                    'message': message,
                    'result': '消息发送成功'
                }, ensure_ascii=False))
            else:
                print("❌ 消息发送失败")
                print(json.dumps({
                    'success': False,
                    'contact': args.contact,
                    'message': message,
                    'result': '消息发送失败'
                }, ensure_ascii=False))

        elif args.action == 'get_history':
            if not args.contact:
                print("错误：需要指定联系人名称 (--contact)")
                sys.exit(1)

            print(f"准备获取聊天记录: {args.contact}")
            print(f"限制数量: {args.limit}")

            messages = wechat.get_chat_history(args.contact, args.limit)

            print(f"✅ 成功获取 {len(messages)} 条聊天记录")
            print(json.dumps({
                'success': True,
                'contact': args.contact,
                'message_count': len(messages),
                'messages': messages
            }, ensure_ascii=False, indent=2))

        elif args.action == 'auto_process':
            # 直接使用预设的联系人列表
            contact_list = ["张三", "李四", "王五", "赵六"]

            print(f"开始自动处理联系人列表")
            print(f"联系人: {', '.join(contact_list)}")
            print(f"轮询次数: {args.polling_times}")
            print(f"AI接口: {args.api_url or 'http://localhost:8000/api/chat/message'}")
            print(f"API密钥: {args.api_key[:8]}...")
            print("程序将无限循环运行，按 Ctrl+C 停止")
            print("=" * 50)

            # 开始自动处理
            wechat.auto_process_contacts(
                contact_list=contact_list,
                max_polling_times=args.polling_times,
                api_url=args.api_url or "http://localhost:8000/api/chat/message",
                api_key=args.api_key
            )

        elif args.action == 'help':
            print("微信桌面自动化工具命令说明：")
            print("  start          - 启动微信")
            print("  activate       - 激活微信窗口")
            print("  search_and_send - 搜索联系人并发送消息")
            print("  get_history    - 获取聊天记录")
            print("  auto_process   - 自动处理联系人消息（预设联系人：张三、李四、王五、赵六）")
            print("\n参数说明：")
            print("  --contact      - 联系人名称（用于search_and_send、get_history）")
            print("  --message      - 消息内容（可选，默认：您好）")
            print("  --limit        - 获取历史记录数量（可选，默认：10）")
            print("  --polling_times - 轮询次数（可选，默认：5）")
            print("  --api_url      - AI接口URL（可选，默认：http://localhost:8000/api/chat/message）")
            print("  --api_key      - API密钥（auto_process操作必需）")
            print("  --title        - 窗口标题（可选）")
            print("\n使用示例：")
            print("  python wechat_auto.py start")
            print("  python wechat_auto.py activate")
            print("  python wechat_auto.py search_and_send --contact 张三 --message 你好")
            print("  python wechat_auto.py get_history --contact 李四 --limit 5")
            print("  python wechat_auto.py auto_process --polling_times 10")
            print("  python wechat_auto.py auto_process --polling_times 20 --api_url http://127.0.0.1:8000/api/chat/message")

        else:
            print(f"未知操作: {args.action}")
            print("使用 'python wechat_auto.py help' 查看帮助")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ 自动处理已停止")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {str(e)}")
        print(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()