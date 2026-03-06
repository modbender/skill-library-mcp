#!/usr/bin/env python3
"""
测试 Telegram Bot 模块 (Phase 3)
- 命令解析
- 命令处理
- Dashboard 格式化
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.telegram_bot import (
    TelegramCommand,
    CommandResult,
    TelegramCommandHandler,
    create_command_handler_from_config,
)
from lib.scheduler import ProjectInfo, ProjectLifecycle
from lib.state_manager import GlobalState, ProjectState


class TestTelegramCommand(unittest.TestCase):
    """测试 TelegramCommand 数据类"""
    
    def test_default_values(self):
        """测试默认值"""
        cmd = TelegramCommand(command="status")
        
        self.assertEqual(cmd.command, "status")
        self.assertIsNone(cmd.project_name)
        self.assertEqual(cmd.args, [])
        self.assertEqual(cmd.chat_id, "")
    
    def test_with_project(self):
        """测试带项目名"""
        cmd = TelegramCommand(
            command="pause",
            project_name="shike",
            chat_id="123"
        )
        
        self.assertEqual(cmd.command, "pause")
        self.assertEqual(cmd.project_name, "shike")


class TestCommandResult(unittest.TestCase):
    """测试 CommandResult 数据类"""
    
    def test_success(self):
        """测试成功结果"""
        result = CommandResult(success=True, message="OK")
        
        self.assertTrue(result.success)
        self.assertEqual(result.message, "OK")
    
    def test_failure(self):
        """测试失败结果"""
        result = CommandResult(success=False, message="Error")
        
        self.assertFalse(result.success)


class TestCommandParsing(unittest.TestCase):
    """测试命令解析"""
    
    def setUp(self):
        self.handler = TelegramCommandHandler("test_token")
    
    def test_parse_simple_command(self):
        """测试解析简单命令"""
        text = "/status"
        message = {"chat": {"id": 123}, "message_id": 1}
        
        cmd = self.handler._parse_command(text, message)
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command, "status")
        self.assertIsNone(cmd.project_name)
    
    def test_parse_command_with_project(self):
        """测试解析带项目名的命令"""
        text = "/pause @shike"
        message = {"chat": {"id": 123}, "message_id": 1}
        
        cmd = self.handler._parse_command(text, message)
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command, "pause")
        self.assertEqual(cmd.project_name, "shike")
    
    def test_parse_command_with_botname(self):
        """测试解析带 bot 名的命令"""
        text = "/status@mybot @shike"
        message = {"chat": {"id": 123}, "message_id": 1}
        
        cmd = self.handler._parse_command(text, message)
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command, "status")
        self.assertEqual(cmd.project_name, "shike")
    
    def test_parse_command_with_args(self):
        """测试解析带参数的命令"""
        text = "/log @shike 10"
        message = {"chat": {"id": 123}, "message_id": 1}
        
        cmd = self.handler._parse_command(text, message)
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.command, "log")
        self.assertEqual(cmd.project_name, "shike")
        self.assertEqual(cmd.args, ["10"])
    
    def test_parse_invalid_command(self):
        """测试解析无效命令"""
        text = "not a command"
        message = {"chat": {"id": 123}, "message_id": 1}
        
        cmd = self.handler._parse_command(text, message)
        
        self.assertIsNone(cmd)


class TestCommandHandlers(unittest.TestCase):
    """测试命令处理器"""
    
    def setUp(self):
        self.handler = TelegramCommandHandler("test_token")
        
        self.projects = [
            ProjectInfo(
                name="shike",
                dir="/shike",
                lifecycle=ProjectLifecycle.RUNNING,
            ),
            ProjectInfo(
                name="simcity",
                dir="/simcity",
                lifecycle=ProjectLifecycle.PAUSED,
            ),
        ]
        
        self.state = GlobalState()
        self.state.projects["/shike"] = ProjectState()
        self.state.projects["/simcity"] = ProjectState()
        
        self.sessions = {"/shike": MagicMock()}
    
    def test_handle_status_all(self):
        """测试处理 /status（全部项目）"""
        cmd = TelegramCommand(command="status")
        
        result = self.handler.handle_status(cmd, self.projects, self.state, self.sessions)
        
        self.assertTrue(result.success)
        self.assertIn("Dashboard", result.message)
    
    def test_handle_status_specific(self):
        """测试处理 /status @项目名"""
        cmd = TelegramCommand(command="status", project_name="shike")
        
        result = self.handler.handle_status(cmd, self.projects, self.state, self.sessions)
        
        self.assertTrue(result.success)
        self.assertIn("shike", result.message)
    
    def test_handle_status_not_found(self):
        """测试处理 /status 项目不存在"""
        cmd = TelegramCommand(command="status", project_name="nonexistent")
        
        result = self.handler.handle_status(cmd, self.projects, self.state, self.sessions)
        
        self.assertFalse(result.success)
        self.assertIn("未找到", result.message)
    
    def test_handle_pause_specific(self):
        """测试处理 /pause @项目名"""
        cmd = TelegramCommand(command="pause", project_name="shike")
        
        result = self.handler.handle_pause(cmd, self.projects, self.state)
        
        self.assertTrue(result.success)
        self.assertEqual(self.projects[0].lifecycle, ProjectLifecycle.PAUSED)
    
    def test_handle_pause_already_paused(self):
        """测试暂停已暂停的项目"""
        cmd = TelegramCommand(command="pause", project_name="simcity")
        
        result = self.handler.handle_pause(cmd, self.projects, self.state)
        
        self.assertFalse(result.success)
        self.assertIn("已经是暂停状态", result.message)
    
    def test_handle_resume_specific(self):
        """测试处理 /resume @项目名"""
        cmd = TelegramCommand(command="resume", project_name="simcity")
        
        result = self.handler.handle_resume(cmd, self.projects, self.state)
        
        self.assertTrue(result.success)
        self.assertEqual(self.projects[1].lifecycle, ProjectLifecycle.RUNNING)
    
    def test_handle_resume_not_paused(self):
        """测试恢复未暂停的项目"""
        cmd = TelegramCommand(command="resume", project_name="shike")
        
        result = self.handler.handle_resume(cmd, self.projects, self.state)
        
        self.assertFalse(result.success)
        self.assertIn("不是暂停状态", result.message)
    
    def test_handle_skip_no_project(self):
        """测试 /skip 未指定项目"""
        cmd = TelegramCommand(command="skip")
        
        result = self.handler.handle_skip(cmd, self.projects, self.state)
        
        self.assertFalse(result.success)
        self.assertIn("请指定项目", result.message)
    
    def test_handle_skip_no_task(self):
        """测试 /skip 无当前任务"""
        cmd = TelegramCommand(command="skip", project_name="shike")
        
        result = self.handler.handle_skip(cmd, self.projects, self.state)
        
        self.assertFalse(result.success)
        self.assertIn("没有正在进行的任务", result.message)
    
    def test_handle_approve_no_project(self):
        """测试 /approve 未指定项目"""
        cmd = TelegramCommand(command="approve")
        
        result = self.handler.handle_approve(cmd, self.projects, self.state)
        
        self.assertFalse(result.success)
        self.assertIn("请指定项目", result.message)
    
    def test_handle_log_all(self):
        """测试 /log 查看所有日志"""
        self.state.history = [
            {"timestamp": "2024-01-01T00:00:00", "action": "send", "project": "shike"},
            {"timestamp": "2024-01-01T00:01:00", "action": "send", "project": "simcity"},
        ]
        
        cmd = TelegramCommand(command="log")
        
        result = self.handler.handle_log(cmd, self.projects, self.state)
        
        self.assertTrue(result.success)
        self.assertIn("shike", result.message)
        self.assertIn("simcity", result.message)
    
    def test_handle_log_specific(self):
        """测试 /log @项目名"""
        self.state.history = [
            {"timestamp": "2024-01-01T00:00:00", "action": "send", "project": "shike"},
            {"timestamp": "2024-01-01T00:01:00", "action": "send", "project": "simcity"},
        ]
        
        cmd = TelegramCommand(command="log", project_name="shike")
        
        result = self.handler.handle_log(cmd, self.projects, self.state)
        
        self.assertTrue(result.success)
        self.assertIn("shike", result.message)
        self.assertNotIn("simcity", result.message)


class TestFormatDashboard(unittest.TestCase):
    """测试 Dashboard 格式化"""
    
    def setUp(self):
        self.handler = TelegramCommandHandler("test_token")
    
    def test_format_dashboard_basic(self):
        """测试基本 Dashboard 格式"""
        projects = [
            ProjectInfo(name="shike", dir="/shike", lifecycle=ProjectLifecycle.RUNNING),
        ]
        state = GlobalState()
        state.started_at = "2024-01-01T00:00:00"
        state.projects["/shike"] = ProjectState()
        sessions = {"/shike": MagicMock()}
        
        dashboard = self.handler.format_dashboard(projects, state, sessions)
        
        self.assertIn("Dashboard", dashboard)
        self.assertIn("shike", dashboard)
        self.assertIn("🟢", dashboard)  # 有 session 的运行中项目
    
    def test_format_dashboard_paused(self):
        """测试暂停项目的 Dashboard"""
        projects = [
            ProjectInfo(name="shike", dir="/shike", lifecycle=ProjectLifecycle.PAUSED),
        ]
        state = GlobalState()
        state.projects["/shike"] = ProjectState()
        sessions = {}
        
        dashboard = self.handler.format_dashboard(projects, state, sessions)
        
        self.assertIn("⏸", dashboard)
    
    def test_format_dashboard_with_tasks(self):
        """测试带任务的 Dashboard"""
        from lib.task_orchestrator import TasksConfig, Task
        
        tasks_config = TasksConfig(
            project_name="shike",
            tasks=[
                Task(id="t1", name="Task 1", prompt=""),
                Task(id="t2", name="Task 2", prompt=""),
            ]
        )
        
        projects = [
            ProjectInfo(
                name="shike",
                dir="/shike",
                lifecycle=ProjectLifecycle.RUNNING,
                tasks_config=tasks_config,
            ),
        ]
        
        state = GlobalState()
        state.projects["/shike"] = ProjectState()
        state.projects["/shike"].task_states = {
            "t1": MagicMock(status="COMPLETED"),
            "t2": MagicMock(status="RUNNING"),
        }
        
        sessions = {"/shike": MagicMock()}
        
        dashboard = self.handler.format_dashboard(projects, state, sessions)
        
        self.assertIn("1/2", dashboard)  # 任务进度


class TestPollCommands(unittest.TestCase):
    """测试轮询命令"""
    
    def setUp(self):
        self.handler = TelegramCommandHandler("test_token", ["123"])
    
    @patch('requests.get')
    def test_poll_commands_success(self, mock_get):
        """测试成功轮询"""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "ok": True,
                "result": [
                    {
                        "update_id": 1,
                        "message": {
                            "text": "/status",
                            "chat": {"id": 123},
                            "message_id": 1,
                            "from": {"username": "test"},
                            "date": 1234567890,
                        }
                    }
                ]
            }
        )
        
        commands = self.handler.poll_commands(timeout=0)
        
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].command, "status")
    
    @patch('requests.get')
    def test_poll_commands_unauthorized_chat(self, mock_get):
        """测试过滤未授权的 chat"""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "ok": True,
                "result": [
                    {
                        "update_id": 1,
                        "message": {
                            "text": "/status",
                            "chat": {"id": 456},  # 未授权的 chat
                            "message_id": 1,
                            "from": {},
                            "date": 1234567890,
                        }
                    }
                ]
            }
        )
        
        commands = self.handler.poll_commands(timeout=0)
        
        self.assertEqual(len(commands), 0)
    
    @patch('requests.get')
    def test_poll_commands_unsupported(self, mock_get):
        """测试过滤不支持的命令"""
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "ok": True,
                "result": [
                    {
                        "update_id": 1,
                        "message": {
                            "text": "/unsupported",
                            "chat": {"id": 123},
                            "message_id": 1,
                            "from": {},
                            "date": 1234567890,
                        }
                    }
                ]
            }
        )
        
        commands = self.handler.poll_commands(timeout=0)
        
        self.assertEqual(len(commands), 0)
    
    @patch('requests.get')
    def test_poll_commands_timeout(self, mock_get):
        """测试轮询超时"""
        import requests
        mock_get.side_effect = requests.Timeout()
        
        commands = self.handler.poll_commands(timeout=0)
        
        self.assertEqual(len(commands), 0)


class TestCreateCommandHandler(unittest.TestCase):
    """测试创建命令处理器"""
    
    def test_create_with_token(self):
        """测试有 token 时创建"""
        config = {
            "telegram": {
                "bot_token": "test_token",
                "chat_id": "123",
            }
        }
        
        handler = create_command_handler_from_config(config)
        
        self.assertIsNotNone(handler)
        self.assertEqual(handler.bot_token, "test_token")
    
    def test_create_without_token(self):
        """测试无 token 时返回 None"""
        config = {"telegram": {}}
        
        handler = create_command_handler_from_config(config)
        
        self.assertIsNone(handler)


if __name__ == '__main__':
    unittest.main()
