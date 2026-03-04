#!/usr/bin/env python3
"""
测试状态机和状态管理
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.state_manager import (
    GlobalState,
    ProjectState,
    check_cooldown,
    check_daily_limit,
    get_project_state,
    get_total_daily_sends,
    increment_send_count,
    load_state,
    record_history,
    reset_daily_sends_if_needed,
    save_state,
)


class TestProjectState(unittest.TestCase):
    """测试项目状态"""
    
    def test_initial_state(self):
        """测试初始状态"""
        state = ProjectState()
        self.assertEqual(state.daily_sends, 0)
        self.assertEqual(state.daily_sends_date, "")
        self.assertIsNone(state.last_send_at)
        self.assertEqual(state.consecutive_failures, 0)
        self.assertEqual(state.loop_count, 0)
    
    def test_increment_send_count(self):
        """测试发送计数"""
        state = ProjectState()
        increment_send_count(state)
        self.assertEqual(state.daily_sends, 1)
        self.assertEqual(state.daily_sends_date, datetime.now().strftime('%Y-%m-%d'))
        self.assertIsNotNone(state.last_send_at)
        
        increment_send_count(state)
        self.assertEqual(state.daily_sends, 2)
    
    def test_reset_daily_sends_on_new_day(self):
        """测试新的一天重置计数"""
        state = ProjectState()
        state.daily_sends = 10
        state.daily_sends_date = "2020-01-01"  # 过去的日期
        
        reset_daily_sends_if_needed(state)
        self.assertEqual(state.daily_sends, 0)
        self.assertEqual(state.daily_sends_date, datetime.now().strftime('%Y-%m-%d'))
    
    def test_no_reset_same_day(self):
        """测试同一天不重置"""
        today = datetime.now().strftime('%Y-%m-%d')
        state = ProjectState()
        state.daily_sends = 10
        state.daily_sends_date = today
        
        reset_daily_sends_if_needed(state)
        self.assertEqual(state.daily_sends, 10)


class TestCooldown(unittest.TestCase):
    """测试冷却期检查"""
    
    def test_no_cooldown_on_first_send(self):
        """测试首次发送无冷却"""
        state = ProjectState()
        self.assertFalse(check_cooldown(state, 120))
    
    def test_in_cooldown(self):
        """测试在冷却期内"""
        state = ProjectState()
        state.last_send_at = datetime.now().isoformat()
        self.assertTrue(check_cooldown(state, 120))
    
    def test_cooldown_expired(self):
        """测试冷却期已过"""
        state = ProjectState()
        past = datetime.now() - timedelta(seconds=130)
        state.last_send_at = past.isoformat()
        self.assertFalse(check_cooldown(state, 120))
    
    def test_cooldown_boundary(self):
        """测试冷却期边界"""
        state = ProjectState()
        # 刚好 119 秒前
        past = datetime.now() - timedelta(seconds=119)
        state.last_send_at = past.isoformat()
        self.assertTrue(check_cooldown(state, 120))
        
        # 刚好 121 秒前
        past = datetime.now() - timedelta(seconds=121)
        state.last_send_at = past.isoformat()
        self.assertFalse(check_cooldown(state, 120))


class TestDailyLimit(unittest.TestCase):
    """测试每日限制检查"""
    
    def test_under_limit(self):
        """测试未达限制"""
        state = ProjectState()
        state.daily_sends = 10
        state.daily_sends_date = datetime.now().strftime('%Y-%m-%d')
        self.assertFalse(check_daily_limit(state, 50))
    
    def test_at_limit(self):
        """测试达到限制"""
        state = ProjectState()
        state.daily_sends = 50
        state.daily_sends_date = datetime.now().strftime('%Y-%m-%d')
        self.assertTrue(check_daily_limit(state, 50))
    
    def test_over_limit(self):
        """测试超过限制"""
        state = ProjectState()
        state.daily_sends = 60
        state.daily_sends_date = datetime.now().strftime('%Y-%m-%d')
        self.assertTrue(check_daily_limit(state, 50))
    
    def test_new_day_resets_limit(self):
        """测试新的一天重置限制"""
        state = ProjectState()
        state.daily_sends = 100
        state.daily_sends_date = "2020-01-01"  # 过去的日期
        self.assertFalse(check_daily_limit(state, 50))
        self.assertEqual(state.daily_sends, 0)  # 已被重置


class TestGlobalState(unittest.TestCase):
    """测试全局状态"""
    
    def test_get_project_state_creates_new(self):
        """测试获取不存在的项目会创建新状态"""
        state = GlobalState()
        proj = get_project_state(state, "/test/project")
        self.assertIsNotNone(proj)
        self.assertEqual(proj.daily_sends, 0)
    
    def test_get_project_state_returns_existing(self):
        """测试获取已存在的项目状态"""
        state = GlobalState()
        state.projects["/test/project"] = ProjectState(daily_sends=10)
        proj = get_project_state(state, "/test/project")
        self.assertEqual(proj.daily_sends, 10)
    
    def test_get_total_daily_sends(self):
        """测试计算总发送次数"""
        today = datetime.now().strftime('%Y-%m-%d')
        state = GlobalState()
        state.projects = {
            "/proj1": ProjectState(daily_sends=10, daily_sends_date=today),
            "/proj2": ProjectState(daily_sends=20, daily_sends_date=today),
            "/proj3": ProjectState(daily_sends=5, daily_sends_date="2020-01-01"),  # 过去的
        }
        total = get_total_daily_sends(state)
        self.assertEqual(total, 30)  # 10 + 20，不包括过去的
    
    def test_record_history(self):
        """测试记录历史"""
        state = GlobalState()
        record_history(state, "send", project="test", intent="error", reply="fix it")
        self.assertEqual(len(state.history), 1)
        self.assertEqual(state.history[0]['action'], "send")
        self.assertEqual(state.history[0]['project'], "test")


class TestStatePersistence(unittest.TestCase):
    """测试状态持久化"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.orig_state_path = None
        
        # 临时修改 STATE_PATH
        import lib.state_manager as sm
        self.orig_state_path = sm.STATE_PATH
        sm.STATE_PATH = os.path.join(self.temp_dir, "state.json")
        sm.AUTOPILOT_DIR = self.temp_dir
    
    def tearDown(self):
        """恢复原始路径"""
        import lib.state_manager as sm
        if self.orig_state_path:
            sm.STATE_PATH = self.orig_state_path
        
        # 清理临时文件
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_state(self):
        """测试保存和加载状态"""
        state = GlobalState()
        state.started_at = "2026-02-06T12:00:00"
        state.projects["/test"] = ProjectState(daily_sends=5)
        record_history(state, "test_action")
        
        self.assertTrue(save_state(state))
        
        loaded = load_state()
        self.assertEqual(loaded.started_at, "2026-02-06T12:00:00")
        self.assertIn("/test", loaded.projects)
        self.assertEqual(loaded.projects["/test"].daily_sends, 5)
        self.assertEqual(len(loaded.history), 1)
    
    def test_load_nonexistent_state(self):
        """测试加载不存在的状态文件"""
        import lib.state_manager as sm
        sm.STATE_PATH = os.path.join(self.temp_dir, "nonexistent.json")
        
        state = load_state()
        self.assertIsNotNone(state)
        self.assertIsNotNone(state.started_at)
    
    def test_history_truncation(self):
        """测试历史记录截断（只保留 100 条）"""
        state = GlobalState()
        for i in range(150):
            record_history(state, f"action_{i}")
        
        save_state(state)
        loaded = load_state()
        self.assertEqual(len(loaded.history), 100)


if __name__ == '__main__':
    unittest.main()
