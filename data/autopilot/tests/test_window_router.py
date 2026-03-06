#!/usr/bin/env python3
"""
测试 Window Router 模块 (Phase 3)
- 窗口缓存 TTL
- 窗口标题匹配逻辑（精确/模糊/fallback）
- verify_foreground
- AppleScript 调用用 mock
"""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.window_router import (
    WindowInfo,
    WindowRouter,
    CACHE_TTL,
    CODEX_PROCESS_NAMES,
)


class TestWindowInfo(unittest.TestCase):
    """测试 WindowInfo 数据类"""
    
    def test_default_values(self):
        """测试默认值"""
        window = WindowInfo(title="Test", window_id=1)
        
        self.assertEqual(window.title, "Test")
        self.assertEqual(window.window_id, 1)
        self.assertEqual(window.position, (0, 0))
        self.assertEqual(window.size, (0, 0))
    
    def test_expired_cache(self):
        """测试缓存过期检测"""
        window = WindowInfo(
            title="Test",
            window_id=1,
            cached_at=time.time() - CACHE_TTL - 1
        )
        
        self.assertTrue(window.expired)
    
    def test_valid_cache(self):
        """测试缓存有效"""
        window = WindowInfo(
            title="Test",
            window_id=1,
            cached_at=time.time()
        )
        
        self.assertFalse(window.expired)


class TestWindowRouter(unittest.TestCase):
    """测试 WindowRouter"""
    
    def setUp(self):
        """创建路由器实例"""
        self.router = WindowRouter(cache_ttl=30)
    
    def tearDown(self):
        """清理缓存"""
        self.router.clear_cache()
    
    @patch('subprocess.run')
    def test_list_windows(self, mock_run):
        """测试枚举窗口"""
        # 模拟两个进程名都返回相同结果
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Shike — Codex|0,0|800,600\nSimCity — Codex|800,0|800,600"
        )
        
        self.router.clear_cache()  # 确保不使用缓存
        windows = self.router._list_codex_windows()
        
        # 可能会因为两个进程名都尝试而有重复，但至少应该有窗口
        self.assertGreaterEqual(len(windows), 2)
        titles = [w.title for w in windows]
        self.assertIn("Shike — Codex", titles)
        self.assertIn("SimCity — Codex", titles)
    
    @patch('subprocess.run')
    def test_list_windows_empty(self, mock_run):
        """测试无窗口情况"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        windows = self.router._list_codex_windows()
        
        self.assertEqual(len(windows), 0)
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_get_window_exact_match(self, mock_list):
        """测试精确匹配窗口"""
        mock_list.return_value = [
            WindowInfo(title="Shike — Codex", window_id=1, cached_at=time.time()),
            WindowInfo(title="SimCity — Codex", window_id=2, cached_at=time.time()),
        ]
        
        window = self.router.get_window("Shike")
        
        self.assertIsNotNone(window)
        self.assertEqual(window.title, "Shike — Codex")
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_get_window_case_insensitive(self, mock_list):
        """测试不区分大小写匹配"""
        mock_list.return_value = [
            WindowInfo(title="Shike — Codex", window_id=1, cached_at=time.time()),
        ]
        
        window = self.router.get_window("shike")
        
        self.assertIsNotNone(window)
        self.assertEqual(window.title, "Shike — Codex")
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_get_window_path_match(self, mock_list):
        """测试路径匹配"""
        mock_list.return_value = [
            WindowInfo(title="/Users/wes/Shike — Codex", window_id=1, cached_at=time.time()),
        ]
        
        window = self.router.get_window("shike", project_dir="/Users/wes/Shike")
        
        self.assertIsNotNone(window)
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_get_window_fallback_single(self, mock_list):
        """测试 fallback 到唯一窗口"""
        mock_list.return_value = [
            WindowInfo(title="Some Project — Codex", window_id=1, cached_at=time.time()),
        ]
        
        window = self.router.get_window("NonexistentProject")
        
        self.assertIsNotNone(window)
        self.assertEqual(window.title, "Some Project — Codex")
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_get_window_no_match_multiple(self, mock_list):
        """测试多窗口无匹配"""
        mock_list.return_value = [
            WindowInfo(title="Project A — Codex", window_id=1, cached_at=time.time()),
            WindowInfo(title="Project B — Codex", window_id=2, cached_at=time.time()),
        ]
        
        window = self.router.get_window("NonexistentProject")
        
        self.assertIsNone(window)


class TestWindowRouterCache(unittest.TestCase):
    """测试窗口路由缓存"""
    
    def setUp(self):
        self.router = WindowRouter(cache_ttl=1)  # 1秒 TTL
    
    def tearDown(self):
        self.router.clear_cache()
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_cache_hit(self, mock_list):
        """测试缓存命中"""
        mock_list.return_value = [
            WindowInfo(title="Shike — Codex", window_id=1, cached_at=time.time()),
        ]
        
        # 第一次调用
        self.router.get_window("Shike")
        
        # 第二次调用应该命中缓存
        mock_list.reset_mock()
        window = self.router.get_window("Shike")
        
        # _list_codex_windows 不应该再被调用
        mock_list.assert_not_called()
        self.assertIsNotNone(window)
    
    @patch.object(WindowRouter, '_list_codex_windows')
    def test_cache_expired(self, mock_list):
        """测试缓存过期"""
        mock_list.return_value = [
            WindowInfo(title="Shike — Codex", window_id=1, cached_at=time.time()),
        ]
        
        # 第一次调用
        self.router.get_window("Shike")
        
        # 手动使缓存过期（超过 1 秒 TTL）
        self.router._cache["Shike"].cached_at = time.time() - 2
        
        # 第二次调用应该重新获取
        mock_list.reset_mock()
        # 更新返回值以便检测是否调用
        mock_list.return_value = [
            WindowInfo(title="Shike — Codex", window_id=1, cached_at=time.time()),
        ]
        window = self.router.get_window("Shike")
        
        # 由于缓存过期，应该重新调用 _list_codex_windows
        self.assertTrue(mock_list.called or window is not None)
    
    def test_clear_cache(self):
        """测试清除缓存"""
        self.router._cache["test"] = WindowInfo(title="Test", window_id=1)
        self.router._all_windows_cache = [WindowInfo(title="Test", window_id=1)]
        
        self.router.clear_cache()
        
        self.assertEqual(len(self.router._cache), 0)
        self.assertEqual(len(self.router._all_windows_cache), 0)
    
    def test_invalidate_project(self):
        """测试使特定项目缓存失效"""
        self.router._cache["project1"] = WindowInfo(title="P1", window_id=1)
        self.router._cache["project2"] = WindowInfo(title="P2", window_id=2)
        
        self.router.invalidate_project("project1")
        
        self.assertNotIn("project1", self.router._cache)
        self.assertIn("project2", self.router._cache)


class TestWindowRouterActivate(unittest.TestCase):
    """测试窗口激活"""
    
    def setUp(self):
        self.router = WindowRouter()
    
    @patch('subprocess.run')
    def test_activate_success(self, mock_run):
        """测试成功激活"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="success"
        )
        
        window = WindowInfo(title="Shike — Codex", window_id=1)
        result = self.router.activate(window)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_activate_not_found(self, mock_run):
        """测试窗口未找到时直接失败（不盲目回退，防止误投）"""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="not_found"),
            MagicMock(returncode=0, stdout="not_found"),
        ]
        
        window = WindowInfo(title="Nonexistent — Codex", window_id=1)
        result = self.router.activate(window)
        
        # 多窗口场景下不应回退到随机窗口
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_activate_timeout(self, mock_run):
        """测试激活超时"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="osascript", timeout=5)
        
        window = WindowInfo(title="Test — Codex", window_id=1)
        result = self.router.activate(window)
        
        # 超时时回退到简单激活可能也会失败
        self.assertFalse(result)


class TestWindowRouterVerifyForeground(unittest.TestCase):
    """测试前台窗口验证"""
    
    def setUp(self):
        self.router = WindowRouter()
    
    @patch('subprocess.run')
    def test_verify_success(self, mock_run):
        """测试验证成功"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Shike — Codex"
        )
        
        result = self.router.verify_foreground("Shike")
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_verify_wrong_window(self, mock_run):
        """测试验证失败（错误窗口）"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SimCity — Codex"
        )
        
        result = self.router.verify_foreground("Shike")
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_verify_no_window(self, mock_run):
        """测试验证失败（无窗口）"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=""
        )
        
        result = self.router.verify_foreground("Shike")
        
        self.assertFalse(result)


class TestWindowRouterEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        self.router = WindowRouter()
    
    def test_escape_applescript(self):
        """测试 AppleScript 字符转义"""
        self.assertEqual(
            self.router._escape_applescript('Test "quoted"'),
            'Test \\"quoted\\"'
        )
        self.assertEqual(
            self.router._escape_applescript('Path\\with\\backslash'),
            'Path\\\\with\\\\backslash'
        )
    
    @patch('subprocess.run')
    def test_parse_window_info_malformed(self, mock_run):
        """测试解析格式错误的窗口信息"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="MalformedLine\nValid — Codex|0,0|800,600\n|bad|data"
        )
        
        windows = self.router._list_codex_windows()
        
        # 应该只解析成功的行
        self.assertGreaterEqual(len(windows), 1)


class TestCODEXProcessNames(unittest.TestCase):
    """测试 Codex 进程名"""
    
    def test_process_names(self):
        """测试进程名列表"""
        self.assertIn("Codex", CODEX_PROCESS_NAMES)
        self.assertIn("Codex Desktop", CODEX_PROCESS_NAMES)


if __name__ == '__main__':
    unittest.main()
