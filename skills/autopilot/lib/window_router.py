#!/usr/bin/env python3
"""
Layer 4: Window Router (窗口路由)
- Codex 窗口 ↔ 项目映射
- 窗口激活与验证
- 内置 30s TTL 缓存
"""

import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 缓存 TTL（秒）
CACHE_TTL = 30

# Codex Desktop 可能的进程名
CODEX_PROCESS_NAMES = ["Codex", "Codex Desktop"]

# ax_helper 二进制路径（优先 app bundle 内，回退到 lib/）
_AX_HELPER_PATHS = [
    os.path.expanduser("~/.autopilot/CodexAutopilot.app/Contents/MacOS/ax_helper"),
    os.path.expanduser("~/Applications/AXSender.app/Contents/MacOS/ax_helper"),
    os.path.expanduser("~/Applications/AutopilotRunner.app/Contents/MacOS/ax_helper"),
    os.path.expanduser("~/.local/bin/ax_helper"),
    os.path.join(os.path.dirname(__file__), "ax_helper"),
]

def _get_ax_helper() -> Optional[str]:
    """获取 ax_helper 二进制路径"""
    for p in _AX_HELPER_PATHS:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None


@dataclass
class WindowInfo:
    """窗口信息"""
    title: str
    window_id: int
    position: tuple = (0, 0)
    size: tuple = (0, 0)
    cached_at: float = 0.0
    
    @property
    def expired(self) -> bool:
        """检查缓存是否过期"""
        return time.time() - self.cached_at > CACHE_TTL


class WindowRouter:
    """
    Codex 窗口路由器
    
    管理 Codex 窗口与项目的映射关系，
    负责窗口激活和前台验证。
    """
    
    def __init__(self, cache_ttl: int = CACHE_TTL):
        """
        初始化窗口路由器
        
        Args:
            cache_ttl: 缓存过期时间（秒）
        """
        self._cache: Dict[str, WindowInfo] = {}  # project_name -> WindowInfo
        self._all_windows_cache: List[WindowInfo] = []
        self._all_windows_cached_at: float = 0.0
        self._cache_ttl = cache_ttl
    
    def get_window(self, project_name: str, project_dir: Optional[str] = None) -> Optional[WindowInfo]:
        """
        查找项目对应的 Codex 窗口
        
        匹配策略:
        1. 窗口标题包含项目名（不区分大小写）
        2. 窗口标题包含项目目录路径
        3. 如果只有一个 Codex 窗口，使用它（fallback）
        
        Args:
            project_name: 项目名称
            project_dir: 项目目录（可选，用于路径匹配）
        
        Returns:
            匹配的窗口信息，或 None
        """
        # 检查缓存
        cached = self._cache.get(project_name)
        if cached and not cached.expired:
            logger.debug(f"使用缓存的窗口: {project_name} -> {cached.title}")
            return cached
        
        # 获取所有 Codex 窗口
        windows = self._list_codex_windows()
        
        if not windows:
            logger.warning("没有找到任何 Codex 窗口")
            return None
        
        project_name_lower = project_name.lower()
        
        # 策略 1: 精确匹配项目名
        for window in windows:
            if project_name_lower in window.title.lower():
                self._cache[project_name] = window
                logger.debug(f"匹配窗口（项目名）: {project_name} -> {window.title}")
                return window
        
        # 策略 2: 匹配项目目录
        if project_dir:
            for window in windows:
                if project_dir in window.title:
                    self._cache[project_name] = window
                    logger.debug(f"匹配窗口（目录）: {project_name} -> {window.title}")
                    return window
        
        # 策略 3: Fallback - 如果只有一个窗口
        if len(windows) == 1:
            window = windows[0]
            self._cache[project_name] = window
            logger.debug(f"Fallback 到唯一窗口: {project_name} -> {window.title}")
            return window
        
        logger.warning(f"无法匹配项目 {project_name} 的窗口，有 {len(windows)} 个候选窗口")
        return None
    
    def activate(self, window: WindowInfo) -> bool:
        """
        将指定窗口提到前台
        
        优先使用 ax_helper（原生 AX API），回退到 osascript。
        
        Args:
            window: 窗口信息
        
        Returns:
            是否成功激活
        """
        # 方法 1: ax_helper（不依赖 osascript 权限）
        ax_helper = _get_ax_helper()
        if ax_helper and window.title:
            try:
                result = subprocess.run(
                    [ax_helper, 'activate', window.title],
                    capture_output=True, text=True, timeout=5
                )
                output = result.stdout.strip()
                if output.startswith("ACTIVATED|"):
                    logger.info(f"ax_helper 激活窗口成功: {window.title}")
                    time.sleep(0.5)
                    return True
                else:
                    logger.warning(f"ax_helper 激活失败: {output}")
            except Exception as e:
                logger.warning(f"ax_helper 激活异常: {e}")
        
        # 方法 2: 回退到 osascript
        for process_name in CODEX_PROCESS_NAMES:
            script = f'''
            tell application "System Events"
                if exists process "{process_name}" then
                    tell process "{process_name}"
                        repeat with w in windows
                            if name of w is "{self._escape_applescript(window.title)}" then
                                perform action "AXRaise" of w
                                set frontmost to true
                                return "success"
                            end if
                        end repeat
                    end tell
                end if
            end tell
            return "not_found"
            '''
            
            try:
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and "success" in result.stdout:
                    logger.info(f"osascript 激活窗口成功: {window.title}")
                    time.sleep(0.5)
                    return True
            except subprocess.TimeoutExpired:
                logger.warning(f"激活窗口超时: {window.title}")
            except Exception as e:
                logger.warning(f"激活窗口异常: {e}")
        
        logger.error(f"无法激活目标窗口: {window.title}")
        return False
    
    def verify_foreground(self, project_name: str) -> bool:
        """
        验证前台窗口是否是目标项目
        
        Args:
            project_name: 项目名称
        
        Returns:
            前台窗口是否匹配
        """
        # 方法 1: ax_helper
        ax_helper = _get_ax_helper()
        if ax_helper:
            try:
                result = subprocess.run(
                    [ax_helper, 'foreground'],
                    capture_output=True, text=True, timeout=5
                )
                output = result.stdout.strip()
                if output.startswith("FOREGROUND|"):
                    front_title = output.split("|", 1)[1]
                    if project_name.lower() in front_title.lower():
                        return True
                    else:
                        logger.debug(f"前台窗口 '{front_title}' 不匹配 '{project_name}'")
                        return False
                # NOT_FRONTMOST / NO_CODEX 等情况
                logger.debug(f"ax_helper foreground: {output}")
            except Exception as e:
                logger.debug(f"ax_helper foreground 异常: {e}")
        
        # 方法 2: 回退到 osascript
        for process_name in CODEX_PROCESS_NAMES:
            script = f'''
            tell application "System Events"
                if exists process "{process_name}" then
                    tell process "{process_name}"
                        if frontmost then
                            try
                                set frontWindow to first window
                                return name of frontWindow
                            on error
                                return ""
                            end try
                        end if
                    end tell
                end if
            end tell
            return ""
            '''
            try:
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    front_title = result.stdout.strip()
                    if front_title and project_name.lower() in front_title.lower():
                        return True
            except Exception as e:
                logger.debug(f"验证前台窗口异常: {e}")
        
        return False
    
    def _list_codex_windows(self) -> List[WindowInfo]:
        """
        枚举所有 Codex 窗口
        
        优先使用 ax_helper（原生 AX API），回退到 osascript。
        
        Returns:
            窗口信息列表
        """
        # 检查缓存
        if self._all_windows_cache and (time.time() - self._all_windows_cached_at) < self._cache_ttl:
            return self._all_windows_cache
        
        windows: List[WindowInfo] = []
        
        # 方法 1: ax_helper（推荐，不依赖 osascript 权限）
        ax_helper = _get_ax_helper()
        if ax_helper:
            try:
                result = subprocess.run(
                    [ax_helper, 'list'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if not line.startswith("WINDOW|"):
                            if line.startswith("AX_ERROR|"):
                                logger.warning(f"ax_helper AX 错误: {line}")
                            continue
                        parts = line.split('|')
                        # WINDOW|title|x,y|w,h
                        title = parts[1] if len(parts) > 1 else ""
                        
                        pos = (0, 0)
                        if len(parts) > 2:
                            try:
                                pp = parts[2].split(',')
                                pos = (int(pp[0]), int(pp[1]))
                            except (ValueError, IndexError):
                                pass
                        
                        size = (0, 0)
                        if len(parts) > 3:
                            try:
                                sp = parts[3].split(',')
                                size = (int(sp[0]), int(sp[1]))
                            except (ValueError, IndexError):
                                pass
                        
                        if title:
                            windows.append(WindowInfo(
                                title=title,
                                window_id=len(windows),
                                position=pos,
                                size=size,
                                cached_at=time.time(),
                            ))
                    
                    if windows:
                        logger.info(f"ax_helper 枚举到 {len(windows)} 个 Codex 窗口")
                        self._all_windows_cache = windows
                        self._all_windows_cached_at = time.time()
                        return windows
                        
            except subprocess.TimeoutExpired:
                logger.warning("ax_helper 枚举超时")
            except Exception as e:
                logger.warning(f"ax_helper 枚举异常: {e}")
        
        # 方法 2: 回退到 osascript
        for process_name in CODEX_PROCESS_NAMES:
            script = f'''
            set windowList to {{}}
            tell application "System Events"
                if exists process "{process_name}" then
                    tell process "{process_name}"
                        repeat with w in windows
                            try
                                set windowName to name of w
                                set windowPos to position of w
                                set windowSize to size of w
                                set end of windowList to windowName & "|" & (item 1 of windowPos) & "," & (item 2 of windowPos) & "|" & (item 1 of windowSize) & "," & (item 2 of windowSize)
                            end try
                        end repeat
                    end tell
                end if
            end tell
            set AppleScript's text item delimiters to "\\n"
            return windowList as text
            '''
            try:
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if not line.strip():
                            continue
                        try:
                            parts = line.split('|')
                            title = parts[0] if len(parts) > 0 else ""
                            pos = (0, 0)
                            if len(parts) > 1:
                                pos_parts = parts[1].split(',')
                                if len(pos_parts) == 2:
                                    pos = (int(pos_parts[0]), int(pos_parts[1]))
                            size = (0, 0)
                            if len(parts) > 2:
                                size_parts = parts[2].split(',')
                                if len(size_parts) == 2:
                                    size = (int(size_parts[0]), int(size_parts[1]))
                            if title:
                                windows.append(WindowInfo(
                                    title=title,
                                    window_id=len(windows),
                                    position=pos,
                                    size=size,
                                    cached_at=time.time(),
                                ))
                        except (ValueError, IndexError) as e:
                            logger.debug(f"解析窗口信息失败: {line}, 错误: {e}")
            except subprocess.TimeoutExpired:
                logger.warning(f"枚举窗口超时: {process_name}")
            except Exception as e:
                logger.warning(f"枚举窗口异常: {e}")
        
        # 更新缓存
        self._all_windows_cache = windows
        self._all_windows_cached_at = time.time()
        
        if windows:
            logger.info(f"osascript 枚举到 {len(windows)} 个 Codex 窗口")
        else:
            logger.debug("未枚举到任何 Codex 窗口")
        return windows
    
    def _escape_applescript(self, text: str) -> str:
        """转义 AppleScript 字符串中的特殊字符"""
        return text.replace('\\', '\\\\').replace('"', '\\"')
    
    def clear_cache(self) -> None:
        """清除所有缓存（用于测试）"""
        self._cache.clear()
        self._all_windows_cache.clear()
        self._all_windows_cached_at = 0.0
    
    def invalidate_project(self, project_name: str) -> None:
        """
        使特定项目的缓存失效
        
        Args:
            project_name: 项目名称
        """
        if project_name in self._cache:
            del self._cache[project_name]


# 全局单例
_window_router: Optional[WindowRouter] = None


def get_window_router() -> WindowRouter:
    """获取全局窗口路由器实例"""
    global _window_router
    if _window_router is None:
        _window_router = WindowRouter()
    return _window_router
